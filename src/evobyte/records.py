"""Registros de configuração, ambiente e eventos de uma execução.

O diretório de saída é exclusivo. Configuração e ambiente são gravados com
serialização canônica e escrita atômica; eventos são append-only; o inventário
guarda hashes dos arquivos de evidência. Contrato em
docs/03-architecture-and-contracts.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import tempfile
from typing import Any

from . import __version__
from .candidate import canonical_json_bytes

SCHEMA_VERSION = 1
RULES_ID = "girth-ge-5-v1"

ALLOWED_METHODS = frozenset(
    {
        "random",
        "greedy",
        "local_uniform",
        "local_manual",
        "local_linear",
        "local_untrained",
    }
)
ALLOWED_N = frozenset({8, 10, 12, 16, 18, 20, 24, 28, 32})
ALLOWED_COST_MODES = frozenset({"cold_start", "amortized"})

CONFIG_FILENAME = "config.json"
ENVIRONMENT_FILENAME = "environment.json"
EVENTS_FILENAME = "events.jsonl"
INVENTORY_FILENAME = "inventory.json"

BUDGET_FIELDS = (
    "wall_limit_s",
    "search_stop_s",
    "finalize_by_s",
    "terminate_at_s",
    "kill_at_s",
    "checkpoint_every_s",
    "training_limit_s",
)

REQUIRED_CONFIG_FIELDS = frozenset(
    {
        "schema_version",
        "protocol_version",
        "protocol_sha256",
        "campaign_id",
        "run_id",
        "code_commit",
        "rules_id",
        "n",
        "method",
        "cost_mode",
        "seed_block",
        "derived_seeds",
        "device",
        "compute_threads",
        "budget",
        "method_parameters",
    }
)

_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_COMMIT_PATTERN = re.compile(r"^[0-9a-f]{7,64}$")


class RecordsError(ValueError):
    """Erro estável de configuração, ambiente ou registro de eventos."""

    def __init__(self, message: str, code: str) -> None:
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message


def _is_strict_int(value: Any) -> bool:
    return type(value) is int


def _is_finite_number(value: Any) -> bool:
    return type(value) in (int, float) and math.isfinite(value)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _validate_non_empty_string(value: Any, code: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RecordsError(f"{field} deve ser string não vazia", code)
    return value


def _validate_budget(raw_budget: Any) -> dict[str, int | float]:
    if not isinstance(raw_budget, dict):
        raise RecordsError("budget deve ser um dicionário", "INVALID_BUDGET")

    missing = [field for field in BUDGET_FIELDS if field not in raw_budget]
    if missing:
        raise RecordsError(f"budget sem campos obrigatórios: {missing}", "INVALID_BUDGET")
    unknown = sorted(set(raw_budget) - set(BUDGET_FIELDS))
    if unknown:
        raise RecordsError(f"budget com campos desconhecidos: {unknown}", "INVALID_BUDGET")

    budget: dict[str, int | float] = {}
    for field in BUDGET_FIELDS:
        value = raw_budget[field]
        if not _is_finite_number(value):
            raise RecordsError(f"budget.{field} deve ser número finito", "INVALID_BUDGET")
        if field == "training_limit_s":
            if value < 0:
                raise RecordsError(
                    "budget.training_limit_s deve ser >= 0",
                    "INVALID_BUDGET",
                )
        elif value <= 0:
            raise RecordsError(
                f"budget.{field} deve ser positivo",
                "INVALID_BUDGET",
            )
        budget[field] = value

    if not (
        budget["search_stop_s"]
        < budget["finalize_by_s"]
        < budget["terminate_at_s"]
        < budget["kill_at_s"]
        <= budget["wall_limit_s"]
    ):
        raise RecordsError(
            "ordem temporal do budget inválida: "
            "search_stop_s < finalize_by_s < terminate_at_s < kill_at_s <= wall_limit_s",
            "INVALID_BUDGET",
        )
    if budget["training_limit_s"] > budget["wall_limit_s"]:
        raise RecordsError(
            "budget.training_limit_s não pode exceder wall_limit_s",
            "INVALID_BUDGET",
        )

    return budget


def _validate_derived_seeds(raw_seeds: Any) -> dict[str, int]:
    if not isinstance(raw_seeds, dict) or not raw_seeds:
        raise RecordsError(
            "derived_seeds deve ser um dicionário não vazio",
            "INVALID_DERIVED_SEEDS",
        )

    seeds: dict[str, int] = {}
    for name in sorted(raw_seeds):
        if not isinstance(name, str) or not name.strip():
            raise RecordsError(
                "nomes de derived_seeds devem ser strings não vazias",
                "INVALID_DERIVED_SEEDS",
            )
        seed = raw_seeds[name]
        if not _is_strict_int(seed) or seed < 0:
            raise RecordsError(
                f"derived_seeds.{name} deve ser inteiro estrito >= 0",
                "INVALID_DERIVED_SEEDS",
            )
        seeds[name] = seed
    return seeds


def _validate_config_payload(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise RecordsError("configuração deve ser um dicionário", "CONFIG_NOT_MAPPING")

    if "is_example" in raw:
        raise RecordsError(
            "configuração de exemplo não pode ser usada em execução real",
            "EXAMPLE_NOT_ALLOWED",
        )

    unknown = sorted(set(raw) - REQUIRED_CONFIG_FIELDS)
    if unknown:
        raise RecordsError(f"campos desconhecidos: {unknown}", "UNKNOWN_FIELD")

    missing = sorted(REQUIRED_CONFIG_FIELDS - set(raw))
    if missing:
        raise RecordsError(f"campos obrigatórios ausentes: {missing}", "MISSING_FIELD")

    if not _is_strict_int(raw["schema_version"]) or raw["schema_version"] != SCHEMA_VERSION:
        raise RecordsError(
            f"schema_version deve ser {SCHEMA_VERSION}",
            "INVALID_SCHEMA_VERSION",
        )

    protocol_version = _validate_non_empty_string(
        raw["protocol_version"], "INVALID_PROTOCOL_VERSION", "protocol_version"
    )

    protocol_sha256 = raw["protocol_sha256"]
    if not isinstance(protocol_sha256, str) or not _SHA256_PATTERN.fullmatch(
        protocol_sha256
    ):
        raise RecordsError(
            "protocol_sha256 deve ser SHA-256 hexadecimal minúsculo",
            "INVALID_PROTOCOL_SHA256",
        )

    campaign_id = _validate_non_empty_string(
        raw["campaign_id"], "INVALID_CAMPAIGN_ID", "campaign_id"
    )
    run_id = _validate_non_empty_string(raw["run_id"], "INVALID_RUN_ID", "run_id")

    code_commit = raw["code_commit"]
    if not isinstance(code_commit, str) or not _COMMIT_PATTERN.fullmatch(code_commit):
        raise RecordsError(
            "code_commit deve ser hexadecimal minúsculo de 7 a 64 caracteres",
            "INVALID_CODE_COMMIT",
        )

    if raw["rules_id"] != RULES_ID:
        raise RecordsError(
            f"rules_id deve ser '{RULES_ID}'",
            "UNEXPECTED_RULES_ID",
        )

    n = raw["n"]
    if not _is_strict_int(n) or n not in ALLOWED_N:
        raise RecordsError(
            f"n deve estar em {sorted(ALLOWED_N)}",
            "INVALID_N",
        )

    method = raw["method"]
    if not isinstance(method, str) or method not in ALLOWED_METHODS:
        raise RecordsError(
            f"method deve estar em {sorted(ALLOWED_METHODS)}",
            "INVALID_METHOD",
        )

    cost_mode = raw["cost_mode"]
    if not isinstance(cost_mode, str) or cost_mode not in ALLOWED_COST_MODES:
        raise RecordsError(
            f"cost_mode deve estar em {sorted(ALLOWED_COST_MODES)}",
            "INVALID_COST_MODE",
        )

    seed_block = raw["seed_block"]
    if not _is_strict_int(seed_block) or seed_block < 0:
        raise RecordsError(
            "seed_block deve ser inteiro estrito >= 0",
            "INVALID_SEED_BLOCK",
        )

    derived_seeds = _validate_derived_seeds(raw["derived_seeds"])

    device = _validate_non_empty_string(raw["device"], "INVALID_DEVICE", "device")

    compute_threads = raw["compute_threads"]
    if not _is_strict_int(compute_threads) or compute_threads < 1:
        raise RecordsError(
            "compute_threads deve ser inteiro estrito >= 1",
            "INVALID_COMPUTE_THREADS",
        )

    budget = _validate_budget(raw["budget"])

    method_parameters = raw["method_parameters"]
    if not isinstance(method_parameters, dict):
        raise RecordsError(
            "method_parameters deve ser um dicionário",
            "INVALID_METHOD_PARAMETERS",
        )

    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "protocol_version": protocol_version,
        "protocol_sha256": protocol_sha256,
        "campaign_id": campaign_id,
        "run_id": run_id,
        "code_commit": code_commit,
        "rules_id": RULES_ID,
        "n": n,
        "method": method,
        "cost_mode": cost_mode,
        "seed_block": seed_block,
        "derived_seeds": derived_seeds,
        "device": device,
        "compute_threads": compute_threads,
        "budget": budget,
        "method_parameters": copy.deepcopy(method_parameters),
    }

    try:
        canonical_json_bytes(payload)
    except (TypeError, ValueError) as exc:
        raise RecordsError(
            "configuração não é serializável de forma canônica",
            "INVALID_CONFIG_JSON",
        ) from exc

    return payload


@dataclass(frozen=True)
class RunConfig:
    """Configuração validada e seu hash canônico, sem campo autorreferente."""

    payload: dict[str, Any]
    sha256: str

    @classmethod
    def from_mapping(cls, raw: Any) -> "RunConfig":
        payload = _validate_config_payload(raw)
        digest = hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
        return cls(payload=payload, sha256=digest)


def _memory_bytes(unavailable: dict[str, str]) -> int | None:
    sysconf = getattr(os, "sysconf", None)
    if sysconf is None:
        unavailable["memory_bytes"] = "not_supported_by_platform"
        return None
    try:
        page_size = sysconf("SC_PAGE_SIZE")
        page_count = sysconf("SC_PHYS_PAGES")
    except (ValueError, OSError):
        unavailable["memory_bytes"] = "not_reported_by_os"
        return None
    if (
        not _is_strict_int(page_size)
        or not _is_strict_int(page_count)
        or page_size <= 0
        or page_count <= 0
    ):
        unavailable["memory_bytes"] = "not_reported_by_os"
        return None
    return page_size * page_count


def capture_environment() -> dict[str, Any]:
    """Coleta ambiente observado; campos indisponíveis ficam null com motivo."""
    unavailable: dict[str, str] = {}

    try:
        uname = platform.uname()
    except Exception:
        uname = None

    def platform_value(name: str) -> str | None:
        if uname is None:
            unavailable[f"platform.{name}"] = "not_reported_by_platform"
            return None
        value = getattr(uname, name, None)
        if not value:
            unavailable[f"platform.{name}"] = "not_reported_by_platform"
            return None
        return str(value)

    cpu_count = os.cpu_count()
    if cpu_count is None:
        unavailable["cpu_count"] = "not_reported_by_os"

    memory_bytes = _memory_bytes(unavailable)

    unavailable["gpu"] = "not_queried"
    unavailable["cuda"] = "not_queried"

    return {
        "captured_at_utc": _utc_now(),
        "python": {
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "compiler": platform.python_compiler(),
        },
        "platform": {
            "system": platform_value("system"),
            "release": platform_value("release"),
            "version": platform_value("version"),
            "machine": platform_value("machine"),
            "processor": platform_value("processor"),
        },
        "cpu_count": cpu_count,
        "memory_bytes": memory_bytes,
        "gpu": None,
        "cuda": None,
        "packages": {"evobyte": __version__},
        "unavailable": unavailable,
    }


def _atomic_write_bytes(path: Path, data: bytes) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=path.name + ".",
        suffix=".tmp",
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    except BaseException:
        try:
            temporary_path.unlink()
        except FileNotFoundError:
            pass
        raise


def _json_bytes(payload: Any) -> bytes:
    return canonical_json_bytes(payload)


def _append_event_line(path: Path, line: str) -> None:
    data = (line + "\n").encode("utf-8")
    try:
        descriptor = os.open(path, os.O_RDWR | os.O_CREAT | os.O_APPEND, 0o644)
        original_size = os.fstat(descriptor).st_size
        try:
            written = 0
            while written < len(data):
                count = os.write(descriptor, data[written:])
                if count <= 0:
                    raise OSError("escrita vazia no log de eventos")
                written += count
            os.fsync(descriptor)
        except OSError:
            try:
                os.ftruncate(descriptor, original_size)
            except OSError:
                pass
            raise
        finally:
            os.close(descriptor)
    except OSError as exc:
        raise RecordsError(
            f"falha ao anexar evento: {exc}",
            "EVENT_WRITE_FAILED",
        ) from exc


def read_events(directory: str | Path) -> tuple[dict[str, Any], ...]:
    """Lê e valida a sequência contínua do log append-only."""
    path = Path(directory) / EVENTS_FILENAME
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise RecordsError(
            f"log de eventos indisponível: {exc}",
            "EVENT_LOG_MISSING_OR_INVALID",
        ) from exc

    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()

    events: list[dict[str, Any]] = []
    for expected_sequence, line in enumerate(lines, start=1):
        if not line.strip():
            raise RecordsError(
                f"linha vazia no log de eventos: {expected_sequence}",
                "EVENT_LOG_INVALID",
            )
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise RecordsError(
                f"JSON inválido no evento {expected_sequence}",
                "EVENT_LOG_INVALID",
            ) from exc
        if not isinstance(event, dict):
            raise RecordsError(
                f"evento {expected_sequence} não é objeto JSON",
                "EVENT_LOG_INVALID",
            )
        if event.get("sequence") != expected_sequence:
            raise RecordsError(
                f"sequência fora de ordem no evento {expected_sequence}",
                "EVENT_LOG_INVALID",
            )
        if not isinstance(event.get("stage"), str) or not event["stage"].strip():
            raise RecordsError(
                f"evento {expected_sequence} sem stage válido",
                "EVENT_LOG_INVALID",
            )
        events.append(event)

    return tuple(events)


def _evidence_files(directory: Path) -> dict[str, Path]:
    files: dict[str, Path] = {}
    for path in sorted(directory.iterdir()):
        if not path.is_file():
            continue
        if path.name == INVENTORY_FILENAME or path.name.endswith(".tmp"):
            continue
        files[path.name] = path
    return files


def write_inventory(directory: str | Path) -> dict[str, Any]:
    """Grava ou atualiza o inventário de hashes dos arquivos de evidência."""
    path = Path(directory)
    files = {
        name: hashlib.sha256(file_path.read_bytes()).hexdigest()
        for name, file_path in _evidence_files(path).items()
    }
    inventory = {"algorithm": "sha256", "files": files}
    _atomic_write_bytes(path / INVENTORY_FILENAME, _json_bytes(inventory))
    return inventory


def verify_inventory(directory: str | Path) -> dict[str, Any]:
    """Confere hashes e a lista de arquivos; divergência preserva o erro."""
    path = Path(directory)
    inventory_path = path / INVENTORY_FILENAME
    try:
        inventory = json.loads(inventory_path.read_bytes())
    except (OSError, json.JSONDecodeError) as exc:
        raise RecordsError(
            f"inventário indisponível ou inválido: {exc}",
            "INVENTORY_MISSING_OR_INVALID",
        ) from exc

    if (
        not isinstance(inventory, dict)
        or inventory.get("algorithm") != "sha256"
        or not isinstance(inventory.get("files"), dict)
    ):
        raise RecordsError("inventário malformado", "INVENTORY_MISSING_OR_INVALID")

    expected_files = inventory["files"]
    actual_files = _evidence_files(path)
    if set(actual_files) != set(expected_files):
        raise RecordsError(
            "conjunto de arquivos diverge do inventário",
            "INVENTORY_MISMATCH",
        )

    for name, expected_hash in expected_files.items():
        if not isinstance(name, str) or not isinstance(expected_hash, str):
            raise RecordsError("inventário malformado", "INVENTORY_MISSING_OR_INVALID")
        actual_hash = hashlib.sha256(actual_files[name].read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            raise RecordsError(
                f"hash divergente para {name}",
                "INVENTORY_MISMATCH",
            )

    return inventory


def _prepare_output_directory(path: Path) -> Path:
    if path.exists():
        if not path.is_dir():
            raise RecordsError(
                f"diretório de saída não é diretório: {path}",
                "OUTPUT_NOT_DIRECTORY",
            )
        if any(path.iterdir()):
            raise RecordsError(
                f"diretório de saída não está vazio: {path}",
                "RUN_EXISTS",
            )
    else:
        path.mkdir(parents=True)
    return path


@dataclass
class RunRecorder:
    """Recorder de eventos de uma execução já inicializada."""

    directory: Path
    config: RunConfig
    next_sequence: int = 1

    @property
    def config_sha256(self) -> str:
        return self.config.sha256

    def append_event(self, stage: str, **fields: Any) -> dict[str, Any]:
        if not isinstance(stage, str) or not stage.strip():
            raise RecordsError("stage deve ser string não vazia", "INVALID_EVENT")
        if "sequence" in fields or "stage" in fields:
            raise RecordsError(
                "sequence e stage são campos reservados do evento",
                "INVALID_EVENT",
            )

        event = {"sequence": self.next_sequence, "stage": stage, **fields}
        try:
            line = json.dumps(
                event,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
                ensure_ascii=False,
            )
        except (TypeError, ValueError) as exc:
            raise RecordsError(
                "evento não é serializável de forma canônica",
                "INVALID_EVENT",
            ) from exc

        _append_event_line(self.directory / EVENTS_FILENAME, line)
        self.next_sequence += 1
        return event

    def write_inventory(self) -> dict[str, Any]:
        return write_inventory(self.directory)


def initialize_run(
    raw_config: Any,
    output_directory: str | Path,
    *,
    observed_commit: str,
    worktree_clean: bool,
    environment: dict[str, Any] | None = None,
) -> RunRecorder:
    """Valida e grava configuração, ambiente, log vazio e inventário."""
    config = RunConfig.from_mapping(raw_config)

    if worktree_clean is not True:
        raise RecordsError(
            "árvore de trabalho suja impede execução real",
            "DIRTY_WORKTREE",
        )
    if observed_commit != config.payload["code_commit"]:
        raise RecordsError(
            "commit observado diverge de code_commit da configuração",
            "CODE_COMMIT_MISMATCH",
        )

    if environment is None:
        environment_payload = capture_environment()
    else:
        if not isinstance(environment, dict):
            raise RecordsError(
                "environment deve ser um dicionário",
                "INVALID_ENVIRONMENT",
            )
        environment_payload = copy.deepcopy(environment)

    try:
        environment_bytes = _json_bytes(environment_payload)
    except (TypeError, ValueError) as exc:
        raise RecordsError(
            "ambiente não é serializável de forma canônica",
            "INVALID_ENVIRONMENT",
        ) from exc

    directory = _prepare_output_directory(Path(output_directory))

    _atomic_write_bytes(directory / CONFIG_FILENAME, config_bytes(config))
    _atomic_write_bytes(directory / ENVIRONMENT_FILENAME, environment_bytes)
    _atomic_write_bytes(directory / EVENTS_FILENAME, b"")
    write_inventory(directory)

    return RunRecorder(directory=directory, config=config)


def config_bytes(config: RunConfig) -> bytes:
    return canonical_json_bytes(config.payload)


def load_config(directory: str | Path) -> RunConfig:
    path = Path(directory) / CONFIG_FILENAME
    try:
        raw = json.loads(path.read_bytes())
    except (OSError, json.JSONDecodeError) as exc:
        raise RecordsError(
            f"configuração indisponível ou inválida: {exc}",
            "CONFIG_UNREADABLE",
        ) from exc
    return RunConfig.from_mapping(raw)


def resume_run(directory: str | Path) -> RunRecorder:
    """Reabre uma execução verificando inventário e sequência de eventos."""
    path = Path(directory)
    verify_inventory(path)
    config = load_config(path)
    events = read_events(path)
    return RunRecorder(
        directory=path,
        config=config,
        next_sequence=len(events) + 1,
    )
