"""Interface de linha de comando do EvoByte.

Comandos disponíveis: ``verify``, ``run`` e ``campaign``. ``analyze`` é
reconhecido, mas só será ligado em F05-T01. ``run`` sempre passa pelo supervisor
e pelo ledger da campanha; métodos ainda não implementados falham de forma
explícita antes de reservar orçamento.
"""

from __future__ import annotations

import argparse
from contextlib import redirect_stdout
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Sequence

from .budget import Budget
from .campaign import (
    CampaignError,
    CampaignManifest,
    open_campaign,
)
from .candidate import canonical_json_bytes, create_candidate
from .certificates import CERTIFIED, certify
from .records import RecordsError, RunConfig, initialize_run
from .supervisor import COMPLETED, SupervisorError, run_supervised
from .validation.reference import validate as validate_reference

COMMANDS = frozenset({"verify", "run", "campaign", "analyze"})
IMPLEMENTED_METHODS: frozenset[str] = frozenset()
EPSILON = 1e-9


class CLIError(Exception):
    """Erro de interface com código estável e código de saída explícito."""

    def __init__(self, code: str, message: str, exit_code: int = 2) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.exit_code = exit_code


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise CLIError("INVALID_ARGUMENTS", message, 2)


def build_parser() -> argparse.ArgumentParser:
    parser = _Parser(
        prog="evobyte",
        description="Laboratório computacional EvoByte",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    verify = subparsers.add_parser(
        "verify",
        help="valida um candidato exportado",
        description="Valida um candidato com o verificador de referência.",
    )
    verify.add_argument("candidate", help="arquivo JSON do candidato ou envelope")
    verify.add_argument(
        "--expected-n",
        type=int,
        required=True,
        help="ordem externa esperada do grafo",
    )
    verify.add_argument(
        "--reference",
        action="store_true",
        help="usa o verificador de referência (padrão)",
    )

    run = subparsers.add_parser(
        "run",
        help="executa uma execução supervisionada",
        description="Valida a configuração e executa sob supervisor e ledger.",
    )
    run.add_argument("--config", required=True, help="arquivo JSON da RunConfig")
    run.add_argument("--manifest", required=True, help="arquivo JSON do manifesto")
    run.add_argument("--ledger", help="caminho do ledger da campanha")
    run.add_argument("--runs-dir", help="diretório raiz das execuções")

    campaign = subparsers.add_parser(
        "campaign",
        help="consulta o ledger agregado da campanha",
        description="Valida o manifesto e mostra o estado do ledger.",
    )
    campaign.add_argument("--manifest", required=True, help="arquivo JSON do manifesto")
    campaign.add_argument("--ledger", help="caminho do ledger da campanha")

    analyze = subparsers.add_parser(
        "analyze",
        help="análise (ainda não implementada)",
        description="Análise estatística será ligada em F05-T01.",
    )
    analyze.add_argument("--manifest", required=True, help="arquivo JSON do manifesto")
    analyze.add_argument("--output", required=True, help="diretório de saída")

    return parser


def _emit(stream, payload: dict[str, Any]) -> None:
    text = json.dumps(
        payload,
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
        default=str,
    )
    stream.write(text + "\n")
    stream.flush()


def _error_payload(
    command: str | None,
    code: str,
    message: str,
    exit_code: int,
) -> dict[str, Any]:
    return {
        "command": command,
        "ok": False,
        "exit_code": exit_code,
        "summary": message,
        "error": {"code": code, "message": message},
    }


def _read_json(path_value: str, label: str) -> Any:
    path = Path(path_value)
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise CLIError(
            "FILE_NOT_FOUND",
            f"não foi possível ler {label} '{path}': {exc}",
            2,
        ) from exc
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise CLIError(
            "INVALID_JSON",
            f"{label} '{path}' contém JSON inválido: {exc}",
            2,
        ) from exc


def _safe_component(value: Any, code: str, label: str) -> str:
    if (
        not isinstance(value, str)
        or not value.strip()
        or value in {".", ".."}
        or "/" in value
        or "\\" in value
        or "\x00" in value
    ):
        raise CLIError(code, f"{label} não é utilizável como diretório: {value!r}", 2)
    return value


def _candidate_payload(raw: Any) -> tuple[Any, str | None]:
    if not isinstance(raw, dict):
        return raw, None
    if "is_example" in raw:
        raise CLIError(
            "EXAMPLE_NOT_ALLOWED",
            "candidato de exemplo não pode ser verificado como execução real",
            2,
        )
    if "payload" in raw:
        declared_hash = raw.get("content_sha256")
        if declared_hash is not None and (
            not isinstance(declared_hash, str) or len(declared_hash) != 64
        ):
            raise CLIError(
                "INVALID_CANDIDATE_HASH",
                "content_sha256 do envelope deve ser SHA-256 hexadecimal",
                2,
            )
        return raw["payload"], declared_hash
    return raw, None


def _observe_git_state() -> tuple[str, bool]:
    try:
        commit_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CLIError(
            "GIT_UNAVAILABLE",
            f"não foi possível observar o estado do git: {exc}",
            2,
        ) from exc

    if commit_result.returncode != 0 or status_result.returncode != 0:
        raise CLIError(
            "GIT_UNAVAILABLE",
            "git rev-parse/status falhou",
            2,
        )

    commit = commit_result.stdout.strip()
    if not commit:
        raise CLIError("GIT_UNAVAILABLE", "commit observado vazio", 2)
    return commit, status_result.stdout.strip() == ""


def _worker_command_for_method(config: RunConfig) -> list[str]:
    raise CLIError(
        "METHOD_NOT_IMPLEMENTED",
        f"método '{config.payload['method']}' ainda não implementado",
        2,
    )


def _command_verify(args, output) -> int:
    raw = _read_json(args.candidate, "candidato")
    payload, declared_hash = _candidate_payload(raw)

    if declared_hash is not None:
        try:
            actual_hash = hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
        except (TypeError, ValueError) as exc:
            raise CLIError(
                "INVALID_CANDIDATE",
                f"payload do candidato não é canonizável: {exc}",
                2,
            ) from exc
        if actual_hash != declared_hash:
            raise CLIError(
                "CANDIDATE_HASH_MISMATCH",
                "content_sha256 do envelope diverge do payload",
                2,
            )

    try:
        result = validate_reference(payload, args.expected_n)
    except Exception as exc:
        raise CLIError(
            "REFERENCE_VALIDATION_FAILED",
            f"verificador de referência falhou: {exc}",
            3,
        ) from exc

    if result.valid:
        summary = f"válido: m={result.computed_m}"
    else:
        codes = sorted({violation.code for violation in result.violations})
        summary = "inválido: " + ", ".join(codes)

    payload_out = {
        "command": "verify",
        "ok": True,
        "exit_code": 0,
        "summary": summary,
        "result": {
            "candidate_path": str(Path(args.candidate)),
            "expected_n": args.expected_n,
            "requested_validator": "reference",
            **asdict(result),
        },
    }
    _emit(output, payload_out)
    return 0


def _run_exit_code(status: str) -> int:
    return 0 if status == COMPLETED else 3


def _command_run(args, output) -> int:
    config_raw = _read_json(args.config, "configuração")
    manifest_raw = _read_json(args.manifest, "manifesto")

    try:
        config = RunConfig.from_mapping(config_raw)
    except RecordsError as exc:
        raise CLIError(exc.code, exc.message, 2) from exc
    try:
        manifest = CampaignManifest.from_mapping(manifest_raw)
    except CampaignError as exc:
        raise CLIError(exc.code, exc.message, 2) from exc

    if config.payload["campaign_id"] != manifest.campaign_id:
        raise CLIError(
            "CAMPAIGN_MISMATCH",
            "campaign_id da configuração diverge do manifesto",
            2,
        )

    run_id = config.payload["run_id"]
    entry = manifest.schedule.get(run_id)
    if entry is None:
        raise CLIError(
            "RUN_NOT_IN_MANIFEST",
            f"run_id '{run_id}' não está na agenda do manifesto",
            2,
        )

    config_wall_limit = float(config.payload["budget"]["wall_limit_s"])
    if abs(config_wall_limit - entry.wall_limit_s) > EPSILON:
        raise CLIError(
            "RUN_LIMIT_MISMATCH",
            "wall_limit_s da configuração diverge do manifesto",
            2,
        )

    method = config.payload["method"]
    if method not in IMPLEMENTED_METHODS:
        raise CLIError(
            "METHOD_NOT_IMPLEMENTED",
            f"método '{method}' ainda não implementado",
            2,
        )
    worker_command = _worker_command_for_method(config)

    observed_commit, worktree_clean = _observe_git_state()
    if not worktree_clean:
        raise CLIError(
            "DIRTY_WORKTREE",
            "árvore de trabalho suja impede execução real",
            2,
        )
    if observed_commit != config.payload["code_commit"]:
        raise CLIError(
            "CODE_COMMIT_MISMATCH",
            "commit observado diverge do code_commit da configuração",
            2,
        )

    manifest_path = Path(args.manifest)
    ledger_path = (
        Path(args.ledger)
        if args.ledger
        else manifest_path.with_name(manifest_path.stem + ".ledger.json")
    )
    runs_dir = (
        Path(args.runs_dir)
        if args.runs_dir
        else manifest_path.parent / "runs"
    )
    campaign_component = _safe_component(
        manifest.campaign_id,
        "INVALID_CAMPAIGN_ID",
        "campaign_id",
    )
    run_component = _safe_component(run_id, "INVALID_RUN_ID", "run_id")
    run_dir = runs_dir / campaign_component / run_component

    try:
        controller = open_campaign(manifest, ledger_path)
    except CampaignError as exc:
        raise CLIError(exc.code, exc.message, 2) from exc

    try:
        try:
            reservation = controller.reserve(run_id)
        except CampaignError as exc:
            raise CLIError(exc.code, exc.message, 2) from exc

        try:
            recorder = initialize_run(
                config_raw,
                run_dir,
                observed_commit=observed_commit,
                worktree_clean=worktree_clean,
            )
        except RecordsError as exc:
            try:
                controller.reconcile(reservation.reservation_id, 0.0, "crashed")
            except CampaignError:
                pass
            raise CLIError(exc.code, exc.message, 2) from exc

        empty_dir = run_dir / "empty-certificate"
        empty_certificate: dict[str, Any] = {}

        def preflight() -> None:
            certificate = certify(
                create_candidate(n=config.payload["n"], edges=[]),
                run_id,
                config.payload["n"],
                config.payload["code_commit"],
                empty_dir,
            )
            empty_certificate["status"] = certificate.status
            empty_certificate["path"] = str(empty_dir / "certificate.json")
            if certificate.status != CERTIFIED:
                raise RuntimeError(
                    f"certificado vazio não foi certificado: {certificate.status}"
                )

        budget = Budget(
            time.monotonic(),
            float(config.payload["budget"]["wall_limit_s"]),
        )
        checkpoint_path = run_dir / "checkpoint.json"

        try:
            result = run_supervised(
                worker_command,
                budget,
                checkpoint_path,
                preflight=preflight,
            )
        except SupervisorError as exc:
            try:
                controller.reconcile(
                    reservation.reservation_id,
                    budget.elapsed_seconds(),
                    "crashed",
                )
            except CampaignError:
                pass
            raise CLIError(exc.code, exc.message, 3) from exc
        except Exception as exc:
            try:
                controller.reconcile(
                    reservation.reservation_id,
                    budget.elapsed_seconds(),
                    "crashed",
                )
            except CampaignError:
                pass
            raise CLIError(
                "SUPERVISOR_FAILED",
                f"supervisor falhou: {exc}",
                3,
            ) from exc

        try:
            reconciliation = controller.reconcile(
                reservation.reservation_id,
                result.wall_seconds,
                result.status,
            )
        except CampaignError as exc:
            raise CLIError(exc.code, exc.message, 3) from exc

        try:
            recorder.append_event(
                "supervisor",
                status=result.status,
                exit_code=result.exit_code,
                wall_seconds=result.wall_seconds,
                cpu_seconds=result.cpu_seconds,
                max_rss_bytes=result.max_rss_bytes,
                overrun_seconds=result.overrun_seconds,
            )
            recorder.append_event(
                "ledger",
                reservation_id=reconciliation.reservation_id,
                status=reconciliation.status,
                actual_seconds=reconciliation.actual_seconds,
                consumed_seconds_total=reconciliation.consumed_seconds_total,
                reserved_seconds_total=reconciliation.reserved_seconds_total,
            )
            recorder.write_inventory()
        except (RecordsError, OSError) as exc:
            raise CLIError(
                "RECORDS_FAILED",
                f"falha ao registrar evidência: {exc}",
                3,
            ) from exc

        exit_code = _run_exit_code(result.status)
        summary = (
            "execução concluída"
            if exit_code == 0
            else f"falha experimental: {result.status}"
        )
        snapshot = controller.snapshot()
        output_payload = {
            "command": "run",
            "ok": exit_code == 0,
            "exit_code": exit_code,
            "summary": summary,
            "config_sha256": config.sha256,
            "manifest_sha256": manifest.sha256,
            "run_directory": str(run_dir),
            "checkpoint_path": str(checkpoint_path),
            "ledger_path": str(ledger_path),
            "empty_certificate": empty_certificate or None,
            "result": result.to_dict(),
            "reconciliation": asdict(reconciliation),
            "ledger": snapshot,
        }
        _emit(output, output_payload)
        return exit_code
    finally:
        controller.close()


def _command_campaign(args, output) -> int:
    manifest_raw = _read_json(args.manifest, "manifesto")
    try:
        manifest = CampaignManifest.from_mapping(manifest_raw)
    except CampaignError as exc:
        raise CLIError(exc.code, exc.message, 2) from exc

    manifest_path = Path(args.manifest)
    ledger_path = (
        Path(args.ledger)
        if args.ledger
        else manifest_path.with_name(manifest_path.stem + ".ledger.json")
    )
    try:
        with open_campaign(manifest, ledger_path) as controller:
            snapshot = controller.snapshot()
    except CampaignError as exc:
        raise CLIError(exc.code, exc.message, 2) from exc

    output_payload = {
        "command": "campaign",
        "ok": True,
        "exit_code": 0,
        "summary": (
            f"campanha {manifest.campaign_id}: "
            f"{manifest.planned_max_experimental_launches} lançamentos planejados"
        ),
        "campaign_id": manifest.campaign_id,
        "manifest_sha256": manifest.sha256,
        "ledger_path": str(ledger_path),
        "ledger": snapshot,
    }
    _emit(output, output_payload)
    return 0


def _command_analyze(args, output) -> int:
    raise CLIError(
        "COMMAND_NOT_IMPLEMENTED",
        "analyze será ligado somente em F05-T01",
        2,
    )


def main(
    argv: Sequence[str] | None = None,
    *,
    stdout=None,
) -> int:
    output = sys.stdout if stdout is None else stdout
    argv_list = list(sys.argv[1:] if argv is None else argv)
    command = argv_list[0] if argv_list and argv_list[0] in COMMANDS else None
    parser = build_parser()

    try:
        with redirect_stdout(output):
            args = parser.parse_args(argv_list)
    except CLIError as exc:
        _emit(output, _error_payload(command, exc.code, exc.message, exc.exit_code))
        return exc.exit_code
    except SystemExit as exc:
        return int(exc.code or 0)

    try:
        if args.command == "verify":
            return _command_verify(args, output)
        if args.command == "run":
            return _command_run(args, output)
        if args.command == "campaign":
            return _command_campaign(args, output)
        if args.command == "analyze":
            return _command_analyze(args, output)
        raise CLIError("INVALID_ARGUMENTS", "comando ausente", 2)
    except CLIError as exc:
        _emit(
            output,
            _error_payload(args.command, exc.code, exc.message, exc.exit_code),
        )
        return exc.exit_code
    except (RecordsError, CampaignError, SupervisorError) as exc:
        _emit(output, _error_payload(args.command, exc.code, exc.message, 2))
        return 2
    except Exception as exc:
        _emit(
            output,
            _error_payload(
                args.command,
                "INTERNAL_ERROR",
                f"falha interna: {exc}",
                3,
            ),
        )
        return 3
