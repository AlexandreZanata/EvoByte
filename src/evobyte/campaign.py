"""Manifesto e ledger do orçamento agregado de uma campanha.

O manifesto declara uma agenda finita e quotas por etapa. O controlador reserva
o limite inteiro da execução antes do lançamento, persiste consumo, reservas e
tentativas sob trava local e recusa qualquer lançamento que ultrapasse a agenda,
as quotas, o teto global ou o número de tentativas. Contrato em
docs/03-architecture-and-contracts.md e docs/05-experiment-budget.md.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile
from typing import Any

try:
    import fcntl
except ImportError:
    fcntl = None

from .candidate import canonical_json_bytes

SCHEMA_VERSION = 1
MAX_ABSOLUTE_WALL_CAP_S = 300000.0
MAX_EXPERIMENTAL_LAUNCHES = 516
MAX_RUN_WALL_S = 600.0
EPSILON = 1e-9

KNOWN_STAGES = frozenset(
    {
        "tests",
        "development",
        "tuning",
        "pilot",
        "confirmatory",
        "reproduction",
        "analysis_and_independent_verification",
        "external_failure_reserve",
    }
)

RECONCILABLE_STATUSES = frozenset(
    {
        "completed",
        "training_failed",
        "invalid",
        "timeout",
        "oom",
        "crashed",
        "external_failure",
    }
)

MANIFEST_REQUIRED_FIELDS = frozenset(
    {
        "schema_version",
        "campaign_id",
        "status",
        "protocol_version",
        "protocol_sha256",
        "absolute_wall_cap_s",
        "reserved_wall_s",
        "planned_max_experimental_launches",
        "quotas_s",
        "schedule",
        "frozen_manifest_sha256",
    }
)

LEDGER_REQUIRED_FIELDS = frozenset(
    {
        "schema_version",
        "campaign_id",
        "manifest_sha256",
        "consumed_seconds",
        "reserved_seconds",
        "launches",
        "overrun_seconds",
        "stages",
        "runs",
        "reservations",
        "history",
    }
)


class CampaignError(ValueError):
    """Erro estável de manifesto, ledger, trava ou reserva."""

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


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _positive_number(value: Any) -> bool:
    return _is_finite_number(value) and value > 0


def _nonnegative_number(value: Any) -> bool:
    return _is_finite_number(value) and value >= 0


def _canonical_manifest_hash(raw_manifest: dict[str, Any]) -> str:
    payload = {
        key: value
        for key, value in raw_manifest.items()
        if key != "frozen_manifest_sha256"
    }
    try:
        canonical = canonical_json_bytes(payload)
    except (TypeError, ValueError) as exc:
        raise CampaignError(
            "manifesto não é serializável de forma canônica",
            "INVALID_MANIFEST_JSON",
        ) from exc
    return hashlib.sha256(canonical).hexdigest()


@dataclass(frozen=True)
class ScheduleEntry:
    run_id: str
    stage: str
    wall_limit_s: float
    max_attempts: int


@dataclass(frozen=True)
class CampaignManifest:
    payload: dict[str, Any]
    sha256: str
    schedule: dict[str, ScheduleEntry]
    quotas: dict[str, float]

    @property
    def campaign_id(self) -> str:
        return self.payload["campaign_id"]

    @property
    def reserved_wall_s(self) -> float:
        return float(self.payload["reserved_wall_s"])

    @property
    def absolute_wall_cap_s(self) -> float:
        return float(self.payload["absolute_wall_cap_s"])

    @property
    def planned_max_experimental_launches(self) -> int:
        return int(self.payload["planned_max_experimental_launches"])

    @property
    def global_limit_seconds(self) -> float:
        return min(self.reserved_wall_s, self.absolute_wall_cap_s)

    @classmethod
    def from_mapping(cls, raw: Any) -> "CampaignManifest":
        if not isinstance(raw, dict):
            raise CampaignError(
                "manifesto deve ser um dicionário",
                "MANIFEST_NOT_MAPPING",
            )
        if "is_example" in raw:
            raise CampaignError(
                "manifesto de exemplo não pode ser executado",
                "EXAMPLE_NOT_ALLOWED",
            )

        missing = sorted(MANIFEST_REQUIRED_FIELDS - set(raw))
        if missing:
            raise CampaignError(
                f"campos obrigatórios ausentes: {missing}",
                "MISSING_FIELD",
            )

        if not _is_strict_int(raw["schema_version"]) or raw["schema_version"] != SCHEMA_VERSION:
            raise CampaignError(
                f"schema_version deve ser {SCHEMA_VERSION}",
                "INVALID_SCHEMA_VERSION",
            )

        campaign_id = raw["campaign_id"]
        if not _non_empty_string(campaign_id):
            raise CampaignError(
                "campaign_id deve ser string não vazia",
                "INVALID_CAMPAIGN_ID",
            )

        if raw["status"] != "FROZEN":
            raise CampaignError(
                "manifesto deve estar FROZEN antes de controlar a campanha",
                "MANIFEST_NOT_FROZEN",
            )

        protocol_version = raw["protocol_version"]
        if not _non_empty_string(protocol_version):
            raise CampaignError(
                "protocol_version deve ser string não vazia",
                "INVALID_PROTOCOL_VERSION",
            )

        protocol_sha256 = raw["protocol_sha256"]
        if (
            not isinstance(protocol_sha256, str)
            or len(protocol_sha256) != 64
            or any(character not in "0123456789abcdef" for character in protocol_sha256)
        ):
            raise CampaignError(
                "protocol_sha256 deve ser SHA-256 hexadecimal minúsculo",
                "INVALID_PROTOCOL_SHA256",
            )

        frozen_hash = raw["frozen_manifest_sha256"]
        computed_hash = _canonical_manifest_hash(raw)
        if not isinstance(frozen_hash, str) or frozen_hash != computed_hash:
            raise CampaignError(
                "frozen_manifest_sha256 diverge do conteúdo do manifesto",
                "MANIFEST_HASH_MISMATCH",
            )

        absolute_cap = raw["absolute_wall_cap_s"]
        if not _positive_number(absolute_cap):
            raise CampaignError(
                "absolute_wall_cap_s deve ser número finito > 0",
                "INVALID_CAP",
            )
        if absolute_cap > MAX_ABSOLUTE_WALL_CAP_S + EPSILON:
            raise CampaignError(
                f"absolute_wall_cap_s excede {MAX_ABSOLUTE_WALL_CAP_S}",
                "MANIFEST_CAP_EXCEEDED",
            )

        reserved_wall = raw["reserved_wall_s"]
        if not _positive_number(reserved_wall) or reserved_wall > absolute_cap + EPSILON:
            raise CampaignError(
                "reserved_wall_s deve ser positivo e <= absolute_wall_cap_s",
                "INVALID_RESERVED_TOTAL",
            )

        planned_launches = raw["planned_max_experimental_launches"]
        if (
            not _is_strict_int(planned_launches)
            or planned_launches < 1
            or planned_launches > MAX_EXPERIMENTAL_LAUNCHES
        ):
            raise CampaignError(
                f"planned_max_experimental_launches deve estar em [1, {MAX_EXPERIMENTAL_LAUNCHES}]",
                "INVALID_LAUNCH_CAP",
            )

        raw_quotas = raw["quotas_s"]
        if not isinstance(raw_quotas, dict) or not raw_quotas:
            raise CampaignError(
                "quotas_s deve ser um dicionário não vazio",
                "INVALID_QUOTAS",
            )
        quotas: dict[str, float] = {}
        for stage, quota in raw_quotas.items():
            if stage not in KNOWN_STAGES:
                raise CampaignError(
                    f"etapa desconhecida em quotas_s: {stage!r}",
                    "UNKNOWN_STAGE",
                )
            if not _positive_number(quota):
                raise CampaignError(
                    f"quota de {stage} deve ser número finito > 0",
                    "INVALID_QUOTAS",
                )
            quotas[stage] = float(quota)
        if sum(quotas.values()) > reserved_wall + EPSILON:
            raise CampaignError(
                "soma das quotas excede reserved_wall_s",
                "INVALID_QUOTAS",
            )

        raw_schedule = raw["schedule"]
        if not isinstance(raw_schedule, list) or not raw_schedule:
            raise CampaignError(
                "schedule deve ser uma lista não vazia",
                "INVALID_SCHEDULE",
            )

        schedule: dict[str, ScheduleEntry] = {}
        total_planned_seconds = 0.0
        total_possible_launches = 0
        for item in raw_schedule:
            if not isinstance(item, dict):
                raise CampaignError(
                    "cada item de schedule deve ser um dicionário",
                    "INVALID_SCHEDULE",
                )
            run_id = item.get("run_id")
            if not _non_empty_string(run_id):
                raise CampaignError(
                    "run_id do schedule deve ser string não vazia",
                    "INVALID_RUN_ID",
                )
            if run_id in schedule:
                raise CampaignError(
                    f"run_id repetido no schedule: {run_id}",
                    "DUPLICATE_RUN_ID",
                )
            stage = item.get("stage")
            if stage not in KNOWN_STAGES:
                raise CampaignError(
                    f"etapa desconhecida no schedule: {stage!r}",
                    "INVALID_RUN_STAGE",
                )
            if stage not in quotas:
                raise CampaignError(
                    f"schedule usa etapa sem quota: {stage}",
                    "UNKNOWN_STAGE_QUOTA",
                )
            wall_limit = item.get("wall_limit_s")
            if not _positive_number(wall_limit):
                raise CampaignError(
                    f"wall_limit_s inválido para {run_id}",
                    "INVALID_RUN_LIMIT",
                )
            if wall_limit > MAX_RUN_WALL_S + EPSILON:
                raise CampaignError(
                    f"wall_limit_s de {run_id} excede {MAX_RUN_WALL_S}",
                    "INVALID_RUN_LIMIT",
                )
            max_attempts = item.get("max_attempts", 1)
            if not _is_strict_int(max_attempts) or max_attempts < 1:
                raise CampaignError(
                    f"max_attempts inválido para {run_id}",
                    "INVALID_ATTEMPTS",
                )
            schedule[run_id] = ScheduleEntry(
                run_id=run_id,
                stage=stage,
                wall_limit_s=float(wall_limit),
                max_attempts=max_attempts,
            )
            total_planned_seconds += float(wall_limit) * max_attempts
            total_possible_launches += max_attempts

        if total_planned_seconds > reserved_wall + EPSILON:
            raise CampaignError(
                "custo máximo do schedule excede reserved_wall_s",
                "MANIFEST_OVERCOMMITTED",
            )
        if total_possible_launches > planned_launches:
            raise CampaignError(
                "tentativas possíveis do schedule excedem planned_max_experimental_launches",
                "MANIFEST_LAUNCH_OVERCOMMITTED",
            )

        return cls(
            payload=copy.deepcopy(raw),
            sha256=computed_hash,
            schedule=schedule,
            quotas=quotas,
        )


@dataclass(frozen=True)
class Reservation:
    reservation_id: str
    run_id: str
    stage: str
    wall_limit_s: float
    attempt: int
    created_at_utc: str


@dataclass(frozen=True)
class Reconciliation:
    reservation_id: str
    run_id: str
    stage: str
    reserved_seconds: float
    actual_seconds: float
    status: str
    overrun_seconds: float
    reason: str | None
    consumed_seconds_total: float
    reserved_seconds_total: float
    overrun_seconds_total: float


def _write_json_atomic(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
        ensure_ascii=False,
    ).encode("utf-8")
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


def _initial_ledger(manifest: CampaignManifest) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "campaign_id": manifest.campaign_id,
        "manifest_sha256": manifest.sha256,
        "consumed_seconds": 0.0,
        "reserved_seconds": 0.0,
        "launches": 0,
        "overrun_seconds": 0.0,
        "stages": {
            stage: {
                "consumed_seconds": 0.0,
                "reserved_seconds": 0.0,
                "launches": 0,
            }
            for stage in sorted(manifest.quotas)
        },
        "runs": {},
        "reservations": {},
        "history": [],
    }


def _close_to(first: float, second: float) -> bool:
    return abs(first - second) <= EPSILON


def _validate_ledger(ledger: Any, manifest: CampaignManifest) -> None:
    if not isinstance(ledger, dict):
        raise CampaignError("ledger deve ser um objeto JSON", "LEDGER_CORRUPTED")
    if not LEDGER_REQUIRED_FIELDS <= set(ledger):
        raise CampaignError("ledger sem campos obrigatórios", "LEDGER_CORRUPTED")
    if ledger.get("schema_version") != SCHEMA_VERSION:
        raise CampaignError("ledger com schema_version inválido", "LEDGER_CORRUPTED")
    if ledger.get("campaign_id") != manifest.campaign_id:
        raise CampaignError(
            "ledger pertence a outra campanha",
            "LEDGER_MISMATCH",
        )
    if ledger.get("manifest_sha256") != manifest.sha256:
        raise CampaignError(
            "ledger foi criado para outro manifesto",
            "LEDGER_MANIFEST_MISMATCH",
        )

    for field in ("consumed_seconds", "reserved_seconds", "overrun_seconds"):
        if not _nonnegative_number(ledger.get(field)):
            raise CampaignError(
                f"ledger.{field} inválido",
                "LEDGER_CORRUPTED",
            )
    if not _is_strict_int(ledger.get("launches")) or ledger["launches"] < 0:
        raise CampaignError("ledger.launches inválido", "LEDGER_CORRUPTED")

    stages = ledger.get("stages")
    if not isinstance(stages, dict) or set(stages) != set(manifest.quotas):
        raise CampaignError("ledger.stages inválido", "LEDGER_CORRUPTED")
    for stage, state in stages.items():
        if (
            not isinstance(state, dict)
            or not _nonnegative_number(state.get("consumed_seconds"))
            or not _nonnegative_number(state.get("reserved_seconds"))
            or not _is_strict_int(state.get("launches"))
            or state["launches"] < 0
        ):
            raise CampaignError(
                f"estado da etapa {stage} inválido",
                "LEDGER_CORRUPTED",
            )

    runs = ledger.get("runs")
    if not isinstance(runs, dict):
        raise CampaignError("ledger.runs inválido", "LEDGER_CORRUPTED")
    run_consumed = 0.0
    run_reserved = 0.0
    run_overrun = 0.0
    run_attempts = 0
    for run_id, state in runs.items():
        entry = manifest.schedule.get(run_id)
        if entry is None:
            raise CampaignError(
                f"ledger contém run fora do manifesto: {run_id}",
                "LEDGER_MANIFEST_MISMATCH",
            )
        if (
            not isinstance(state, dict)
            or state.get("stage") != entry.stage
            or not _is_strict_int(state.get("attempts"))
            or state["attempts"] < 0
            or state["attempts"] > entry.max_attempts
            or not _nonnegative_number(state.get("consumed_seconds"))
            or not _nonnegative_number(state.get("reserved_seconds"))
            or not _nonnegative_number(state.get("overrun_seconds"))
            or (
                state.get("last_status") is not None
                and state.get("last_status") not in RECONCILABLE_STATUSES
            )
        ):
            raise CampaignError(
                f"estado do run {run_id} inválido",
                "LEDGER_CORRUPTED",
            )
        run_consumed += float(state["consumed_seconds"])
        run_reserved += float(state["reserved_seconds"])
        run_overrun += float(state["overrun_seconds"])
        run_attempts += int(state["attempts"])

    reservations = ledger.get("reservations")
    if not isinstance(reservations, dict):
        raise CampaignError("ledger.reservations inválido", "LEDGER_CORRUPTED")
    reservation_total = 0.0
    reservation_by_stage: dict[str, float] = {}
    for reservation_id, item in reservations.items():
        if not isinstance(item, dict):
            raise CampaignError("reserva malformada", "LEDGER_CORRUPTED")
        run_id = item.get("run_id")
        entry = manifest.schedule.get(run_id)
        if entry is None:
            raise CampaignError(
                "reserva aponta para run fora do manifesto",
                "LEDGER_MANIFEST_MISMATCH",
            )
        attempt = item.get("attempt")
        if (
            item.get("stage") != entry.stage
            or not _is_strict_int(attempt)
            or attempt < 1
            or attempt > entry.max_attempts
            or not _positive_number(item.get("wall_limit_s"))
            or not _close_to(float(item["wall_limit_s"]), entry.wall_limit_s)
            or not isinstance(item.get("created_at_utc"), str)
            or reservation_id != f"{run_id}#{attempt}"
        ):
            raise CampaignError(
                f"reserva {reservation_id} inválida",
                "LEDGER_CORRUPTED",
            )
        run_state = runs.get(run_id)
        if run_state is None or int(run_state["attempts"]) < attempt:
            raise CampaignError(
                f"reserva {reservation_id} sem tentativa correspondente",
                "LEDGER_CORRUPTED",
            )
        seconds = float(item["wall_limit_s"])
        reservation_total += seconds
        reservation_by_stage[entry.stage] = (
            reservation_by_stage.get(entry.stage, 0.0) + seconds
        )

    history = ledger.get("history")
    if not isinstance(history, list) or not all(
        isinstance(item, dict) for item in history
    ):
        raise CampaignError("ledger.history inválido", "LEDGER_CORRUPTED")

    if not _close_to(reservation_total, float(ledger["reserved_seconds"])):
        raise CampaignError(
            "reserved_seconds diverge das reservas abertas",
            "LEDGER_CORRUPTED",
        )
    if not _close_to(run_reserved, float(ledger["reserved_seconds"])):
        raise CampaignError(
            "reservas dos runs divergem do total",
            "LEDGER_CORRUPTED",
        )
    if not _close_to(run_consumed, float(ledger["consumed_seconds"])):
        raise CampaignError(
            "consumo dos runs diverge do total",
            "LEDGER_CORRUPTED",
        )
    if not _close_to(run_overrun, float(ledger["overrun_seconds"])):
        raise CampaignError(
            "overrun dos runs diverge do total",
            "LEDGER_CORRUPTED",
        )
    if run_attempts != ledger["launches"]:
        raise CampaignError(
            "tentativas dos runs divergem do total de lançamentos",
            "LEDGER_CORRUPTED",
        )

    stage_consumed = sum(
        float(state["consumed_seconds"]) for state in stages.values()
    )
    stage_reserved = sum(
        float(state["reserved_seconds"]) for state in stages.values()
    )
    stage_launches = sum(int(state["launches"]) for state in stages.values())
    if not _close_to(stage_consumed, float(ledger["consumed_seconds"])):
        raise CampaignError(
            "consumo das etapas diverge do total",
            "LEDGER_CORRUPTED",
        )
    if not _close_to(stage_reserved, float(ledger["reserved_seconds"])):
        raise CampaignError(
            "reservas das etapas divergem do total",
            "LEDGER_CORRUPTED",
        )
    if stage_launches != ledger["launches"]:
        raise CampaignError(
            "lançamentos das etapas divergem do total",
            "LEDGER_CORRUPTED",
        )
    for stage, expected in reservation_by_stage.items():
        if not _close_to(float(stages[stage]["reserved_seconds"]), expected):
            raise CampaignError(
                f"reserva da etapa {stage} diverge das reservas abertas",
                "LEDGER_CORRUPTED",
            )


def _acquire_lock(lock_path: Path):
    if fcntl is None:
        raise CampaignError(
            "trava de campanha não suportada nesta plataforma",
            "LOCK_UNSUPPORTED",
        )
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o644)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        os.close(descriptor)
        raise CampaignError(
            "outro controlador já detém a campanha",
            "CAMPAIGN_LOCKED",
        ) from exc
    except OSError:
        os.close(descriptor)
        raise
    return descriptor


def _release_lock(descriptor) -> None:
    try:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
    finally:
        os.close(descriptor)


class CampaignController:
    """Controlador de reservas e consumo agregado de uma campanha."""

    def __init__(
        self,
        manifest: CampaignManifest,
        ledger_path: Path,
        lock_descriptor,
        ledger: dict[str, Any],
    ) -> None:
        self.manifest = manifest
        self.ledger_path = ledger_path
        self._lock_descriptor = lock_descriptor
        self._ledger = ledger
        self._closed = False

    def _ensure_open(self) -> None:
        if self._closed:
            raise CampaignError("controlador já encerrado", "CAMPAIGN_CLOSED")

    def _commit(self, new_ledger: dict[str, Any]) -> None:
        try:
            _write_json_atomic(self.ledger_path, new_ledger)
        except OSError as exc:
            raise CampaignError(
                f"falha ao persistir ledger: {exc}",
                "LEDGER_WRITE_FAILED",
            ) from exc
        self._ledger = new_ledger

    def reserve(self, run_id: str) -> Reservation:
        """Reserva o limite inteiro do run antes de qualquer spawn."""
        self._ensure_open()

        entry = self.manifest.schedule.get(run_id)
        if entry is None:
            raise CampaignError(
                f"run não declarado no manifesto: {run_id}",
                "RUN_NOT_IN_MANIFEST",
            )

        new_ledger = copy.deepcopy(self._ledger)
        run_state = new_ledger["runs"].get(run_id)
        if run_state is None:
            run_state = {
                "stage": entry.stage,
                "attempts": 0,
                "consumed_seconds": 0.0,
                "reserved_seconds": 0.0,
                "overrun_seconds": 0.0,
                "last_status": None,
            }
        elif run_state.get("stage") != entry.stage:
            raise CampaignError(
                f"etapa do run {run_id} diverge do manifesto",
                "LEDGER_MISMATCH",
            )

        if run_state["attempts"] >= entry.max_attempts:
            raise CampaignError(
                f"run {run_id} esgotou as tentativas",
                "MAX_ATTEMPTS_EXCEEDED",
            )
        if new_ledger["launches"] + 1 > self.manifest.planned_max_experimental_launches:
            raise CampaignError(
                "limite de lançamentos da campanha seria excedido",
                "LAUNCH_LIMIT_EXCEEDED",
            )

        stage_state = new_ledger["stages"].get(entry.stage)
        if stage_state is None:
            raise CampaignError(
                f"etapa sem estado no ledger: {entry.stage}",
                "LEDGER_CORRUPTED",
            )
        stage_available = (
            self.manifest.quotas[entry.stage]
            - float(stage_state["consumed_seconds"])
            - float(stage_state["reserved_seconds"])
        )
        if entry.wall_limit_s > stage_available + EPSILON:
            raise CampaignError(
                f"quota da etapa {entry.stage} seria excedida",
                "STAGE_QUOTA_EXCEEDED",
            )

        global_available = (
            self.manifest.global_limit_seconds
            - float(new_ledger["consumed_seconds"])
            - float(new_ledger["reserved_seconds"])
        )
        if entry.wall_limit_s > global_available + EPSILON:
            raise CampaignError(
                "teto global da campanha seria excedido",
                "GLOBAL_BUDGET_EXCEEDED",
            )

        attempt = int(run_state["attempts"]) + 1
        reservation_id = f"{run_id}#{attempt}"
        if reservation_id in new_ledger["reservations"]:
            raise CampaignError(
                f"reserva duplicada: {reservation_id}",
                "DUPLICATE_RESERVATION",
            )

        seconds = entry.wall_limit_s
        created_at = _utc_now()
        run_state["attempts"] = attempt
        run_state["reserved_seconds"] = (
            float(run_state["reserved_seconds"]) + seconds
        )
        new_ledger["runs"][run_id] = run_state
        new_ledger["launches"] += 1
        new_ledger["reserved_seconds"] = (
            float(new_ledger["reserved_seconds"]) + seconds
        )
        stage_state["launches"] += 1
        stage_state["reserved_seconds"] = (
            float(stage_state["reserved_seconds"]) + seconds
        )
        new_ledger["reservations"][reservation_id] = {
            "run_id": run_id,
            "stage": entry.stage,
            "wall_limit_s": seconds,
            "attempt": attempt,
            "created_at_utc": created_at,
        }

        self._commit(new_ledger)
        return Reservation(
            reservation_id=reservation_id,
            run_id=run_id,
            stage=entry.stage,
            wall_limit_s=seconds,
            attempt=attempt,
            created_at_utc=created_at,
        )

    def _reconcile(
        self,
        reservation_id: str,
        actual_seconds: float,
        status: str,
        reason: str | None,
    ) -> Reconciliation:
        self._ensure_open()
        reservation = self._ledger["reservations"].get(reservation_id)
        if reservation is None:
            raise CampaignError(
                f"reserva não encontrada ou já reconciliada: {reservation_id}",
                "RESERVATION_NOT_FOUND",
            )
        if not _nonnegative_number(actual_seconds):
            raise CampaignError(
                "actual_seconds deve ser número finito >= 0",
                "INVALID_ACTUAL_SECONDS",
            )
        if status not in RECONCILABLE_STATUSES:
            raise CampaignError(
                f"status inválido: {status!r}",
                "INVALID_STATUS",
            )

        reserved = float(reservation["wall_limit_s"])
        if status == "completed" and actual_seconds > reserved + EPSILON:
            raise CampaignError(
                "status completed não pode ser aceito com overrun",
                "INVALID_RECONCILIATION",
            )
        overrun = max(0.0, float(actual_seconds) - reserved)

        new_ledger = copy.deepcopy(self._ledger)
        run_id = reservation["run_id"]
        stage = reservation["stage"]
        run_state = new_ledger["runs"][run_id]
        stage_state = new_ledger["stages"][stage]

        new_ledger["reservations"].pop(reservation_id)
        new_ledger["reserved_seconds"] = max(
            0.0,
            float(new_ledger["reserved_seconds"]) - reserved,
        )
        new_ledger["consumed_seconds"] = (
            float(new_ledger["consumed_seconds"]) + float(actual_seconds)
        )
        new_ledger["overrun_seconds"] = (
            float(new_ledger["overrun_seconds"]) + overrun
        )

        run_state["reserved_seconds"] = max(
            0.0,
            float(run_state["reserved_seconds"]) - reserved,
        )
        run_state["consumed_seconds"] = (
            float(run_state["consumed_seconds"]) + float(actual_seconds)
        )
        run_state["overrun_seconds"] = (
            float(run_state["overrun_seconds"]) + overrun
        )
        run_state["last_status"] = status

        stage_state["reserved_seconds"] = max(
            0.0,
            float(stage_state["reserved_seconds"]) - reserved,
        )
        stage_state["consumed_seconds"] = (
            float(stage_state["consumed_seconds"]) + float(actual_seconds)
        )

        new_ledger["history"].append(
            {
                "reservation_id": reservation_id,
                "run_id": run_id,
                "stage": stage,
                "reserved_seconds": reserved,
                "actual_seconds": float(actual_seconds),
                "status": status,
                "overrun_seconds": overrun,
                "reason": reason,
                "reconciled_at_utc": _utc_now(),
            }
        )

        self._commit(new_ledger)
        return Reconciliation(
            reservation_id=reservation_id,
            run_id=run_id,
            stage=stage,
            reserved_seconds=reserved,
            actual_seconds=float(actual_seconds),
            status=status,
            overrun_seconds=overrun,
            reason=reason,
            consumed_seconds_total=float(new_ledger["consumed_seconds"]),
            reserved_seconds_total=float(new_ledger["reserved_seconds"]),
            overrun_seconds_total=float(new_ledger["overrun_seconds"]),
        )

    def reconcile(
        self,
        reservation_id: str,
        actual_seconds: float,
        status: str,
    ) -> Reconciliation:
        """Substitui a reserva pelo consumo real observado."""
        return self._reconcile(reservation_id, actual_seconds, status, None)

    def abandon(self, reservation_id: str) -> Reconciliation:
        """Encerra reserva órfã cobrando o limite reservado, sem zerar consumo."""
        reservation = self._ledger["reservations"].get(reservation_id)
        if reservation is None:
            raise CampaignError(
                f"reserva não encontrada ou já reconciliada: {reservation_id}",
                "RESERVATION_NOT_FOUND",
            )
        return self._reconcile(
            reservation_id,
            float(reservation["wall_limit_s"]),
            "crashed",
            "ABANDONED",
        )

    def open_reservations(self) -> tuple[Reservation, ...]:
        self._ensure_open()
        reservations = []
        for reservation_id, item in sorted(self._ledger["reservations"].items()):
            reservations.append(
                Reservation(
                    reservation_id=reservation_id,
                    run_id=item["run_id"],
                    stage=item["stage"],
                    wall_limit_s=float(item["wall_limit_s"]),
                    attempt=int(item["attempt"]),
                    created_at_utc=item["created_at_utc"],
                )
            )
        return tuple(reservations)

    def snapshot(self) -> dict[str, Any]:
        self._ensure_open()
        ledger = copy.deepcopy(self._ledger)
        global_limit = self.manifest.global_limit_seconds
        stages = {}
        for stage, state in sorted(ledger["stages"].items()):
            quota = self.manifest.quotas[stage]
            stages[stage] = {
                "quota_seconds": quota,
                "consumed_seconds": state["consumed_seconds"],
                "reserved_seconds": state["reserved_seconds"],
                "available_seconds": quota
                - float(state["consumed_seconds"])
                - float(state["reserved_seconds"]),
                "launches": state["launches"],
            }
        return {
            "campaign_id": ledger["campaign_id"],
            "manifest_sha256": ledger["manifest_sha256"],
            "global": {
                "limit_seconds": global_limit,
                "consumed_seconds": ledger["consumed_seconds"],
                "reserved_seconds": ledger["reserved_seconds"],
                "available_seconds": global_limit
                - float(ledger["consumed_seconds"])
                - float(ledger["reserved_seconds"]),
                "launches": ledger["launches"],
                "planned_max_launches": self.manifest.planned_max_experimental_launches,
                "overrun_seconds": ledger["overrun_seconds"],
            },
            "stages": stages,
            "runs": ledger["runs"],
            "open_reservations": [
                asdict(reservation) for reservation in self.open_reservations()
            ],
            "history": ledger["history"],
        }

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._lock_descriptor is not None:
            _release_lock(self._lock_descriptor)
            self._lock_descriptor = None

    def __enter__(self) -> "CampaignController":
        self._ensure_open()
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()


def open_campaign(
    manifest_data: Any,
    ledger_path: str | Path,
    lock_path: str | Path | None = None,
) -> CampaignController:
    """Abre ou cria a campanha sob trava, sem zerar contadores existentes."""
    manifest = (
        manifest_data
        if isinstance(manifest_data, CampaignManifest)
        else CampaignManifest.from_mapping(manifest_data)
    )
    ledger = Path(ledger_path)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    lock = Path(lock_path) if lock_path is not None else ledger.with_name(
        ledger.name + ".lock"
    )
    descriptor = _acquire_lock(lock)

    try:
        if ledger.exists():
            try:
                raw_ledger = json.loads(ledger.read_bytes())
            except (OSError, json.JSONDecodeError) as exc:
                raise CampaignError(
                    f"ledger corrompido ou ilegível: {exc}",
                    "LEDGER_CORRUPTED",
                ) from exc
            _validate_ledger(raw_ledger, manifest)
            current_ledger = raw_ledger
        else:
            current_ledger = _initial_ledger(manifest)
            try:
                _write_json_atomic(ledger, current_ledger)
            except OSError as exc:
                raise CampaignError(
                    f"falha ao criar ledger: {exc}",
                    "LEDGER_WRITE_FAILED",
                ) from exc
    except Exception:
        _release_lock(descriptor)
        raise

    return CampaignController(manifest, ledger, descriptor, current_ledger)
