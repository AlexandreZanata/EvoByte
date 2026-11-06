"""Exportação de candidato e certificado independente do EvoByte.

O payload canônico é exportado, relido do disco e verificado pelo verificador de
referência em um subprocesso que não importa o motor nem o verificador de
execução. O processo pai executa o verificador de execução e compara hashes,
identidades e verdictos. Contrato em docs/03-architecture-and-contracts.md.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

from .candidate import Candidate, canonical_json_bytes, compute_content_sha256
from .validation import ValidationResult, Violation
from .validation.runtime import validate as validate_runtime

CERTIFIED = "CERTIFIED"
INVALID = "INVALID"
UNCERTIFIED = "UNCERTIFIED"

REFERENCE_VALIDATOR_ID = "evobyte-reference"
RUNTIME_VALIDATOR_ID = "evobyte-runtime"

CANDIDATE_FILENAME = "candidate.json"
ENVELOPE_FILENAME = "envelope.json"
CERTIFICATE_FILENAME = "certificate.json"

DEFAULT_REFERENCE_TIMEOUT_SECONDS = 30.0

_REFERENCE_SCRIPT = """
import dataclasses
import json
import sys

from evobyte.validation.reference import validate

payload_path = sys.argv[1]
expected_n = json.loads(sys.argv[2])
with open(payload_path, "rb") as handle:
    raw_payload = json.load(handle)
result = validate(raw_payload, expected_n)
print(json.dumps(dataclasses.asdict(result)))
""".strip()


@dataclass(frozen=True)
class CandidateExport:
    """Caminhos e identidade da exportação de um candidato."""

    directory: Path
    candidate_path: Path
    envelope_path: Path
    certificate_path: Path
    run_id: str
    content_sha256: str


@dataclass(frozen=True)
class Certificate:
    """Certificado com os dois verdictos independentes e o status final."""

    candidate_sha256: str
    run_id: str
    rules_id: str
    expected_n: int
    verifier_commit: str
    reference_result: ValidationResult | None
    runtime_result: ValidationResult | None
    timestamp_utc: str
    status: str
    reasons: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_sha256": self.candidate_sha256,
            "run_id": self.run_id,
            "rules_id": self.rules_id,
            "expected_n": self.expected_n,
            "verifier_commit": self.verifier_commit,
            "reference_result": (
                asdict(self.reference_result)
                if self.reference_result is not None
                else None
            ),
            "runtime_result": (
                asdict(self.runtime_result)
                if self.runtime_result is not None
                else None
            ),
            "timestamp_utc": self.timestamp_utc,
            "status": self.status,
            "reasons": list(self.reasons),
        }


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _unique(values: list[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))


def _check_candidate_consistency(candidate: Candidate) -> None:
    if not isinstance(candidate, Candidate):
        raise TypeError("candidate deve ser uma instância de evobyte.candidate.Candidate")

    payload = candidate.payload
    if not isinstance(payload, dict):
        raise ValueError("payload do candidato deve ser um dicionário")

    required_fields = ("schema_version", "rules_id", "n", "edges", "claimed_m")
    missing = [field for field in required_fields if field not in payload]
    if missing:
        raise ValueError(f"payload do candidato sem campos obrigatórios: {missing}")
    if not isinstance(payload["rules_id"], str):
        raise ValueError("rules_id do candidato deve ser string")
    if type(payload["n"]) is not int:
        raise ValueError("n do candidato deve ser inteiro estrito")
    if not isinstance(payload["edges"], list):
        raise ValueError("edges do candidato deve ser lista")
    if type(payload["claimed_m"]) is not int:
        raise ValueError("claimed_m do candidato deve ser inteiro estrito")

    try:
        canonical = canonical_json_bytes(payload)
    except (TypeError, ValueError) as exc:
        raise ValueError("payload do candidato não é canonizável") from exc

    if canonical != candidate.canonical_bytes:
        raise ValueError("bytes canônicos do candidato não correspondem ao payload")
    if compute_content_sha256(canonical) != candidate.content_sha256:
        raise ValueError("hash de conteúdo do candidato não corresponde ao payload")


def _check_common_inputs(expected_n: Any, verifier_commit: Any) -> None:
    if type(expected_n) is not int or expected_n < 1:
        raise ValueError("expected_n deve ser inteiro estrito >= 1")
    if not isinstance(verifier_commit, str) or not verifier_commit.strip():
        raise ValueError("verifier_commit deve ser string não vazia")


def _check_run_id(run_id: Any) -> None:
    if not isinstance(run_id, str) or not run_id.strip():
        raise ValueError("run_id deve ser string não vazia")


def _check_timeout(timeout_seconds: Any) -> None:
    if not isinstance(timeout_seconds, (int, float)) or timeout_seconds <= 0:
        raise ValueError("timeout_seconds deve ser numérico e positivo")


@contextmanager
def _commit_environment(verifier_commit: str):
    previous = os.environ.get("EVOBYTE_CODE_COMMIT")
    os.environ["EVOBYTE_CODE_COMMIT"] = verifier_commit
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop("EVOBYTE_CODE_COMMIT", None)
        else:
            os.environ["EVOBYTE_CODE_COMMIT"] = previous


def _reference_environment(verifier_commit: str) -> dict[str, str]:
    environment = dict(os.environ)
    environment["EVOBYTE_CODE_COMMIT"] = verifier_commit
    source_root = Path(__file__).resolve().parents[1]
    existing = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = (
        str(source_root) + (os.pathsep + existing if existing else "")
    )
    return environment


def _result_from_mapping(data: Any) -> ValidationResult:
    if not isinstance(data, dict):
        raise ValueError("resultado do subprocesso deve ser um objeto JSON")

    raw_violations = data["violations"]
    if not isinstance(raw_violations, list):
        raise ValueError("violations deve ser lista")

    violations: list[Violation] = []
    for item in raw_violations:
        if not isinstance(item, dict) or not isinstance(item.get("code"), str):
            raise ValueError("violação malformada no resultado do subprocesso")
        witness = item.get("witness")
        violations.append(
            Violation(
                code=item["code"],
                witness=tuple(witness) if witness is not None else None,
            )
        )

    computed_m = data["computed_m"]
    if computed_m is not None and type(computed_m) is not int:
        raise ValueError("computed_m deve ser inteiro ou nulo")

    if not isinstance(data["valid"], bool):
        raise ValueError("valid deve ser booleano")
    if not isinstance(data["validator_id"], str):
        raise ValueError("validator_id deve ser string")
    if not isinstance(data["validator_version"], str):
        raise ValueError("validator_version deve ser string")

    code_commit = data.get("code_commit")
    if code_commit is not None and not isinstance(code_commit, str):
        raise ValueError("code_commit deve ser string ou nulo")

    payload_sha256 = data.get("payload_sha256")
    if payload_sha256 is not None and not isinstance(payload_sha256, str):
        raise ValueError("payload_sha256 deve ser string ou nulo")

    return ValidationResult(
        valid=data["valid"],
        computed_m=computed_m,
        violations=tuple(violations),
        validator_id=data["validator_id"],
        validator_version=data["validator_version"],
        code_commit=code_commit,
        payload_sha256=payload_sha256,
    )


def _run_reference_subprocess(
    candidate_path: Path,
    expected_n: int,
    verifier_commit: str,
    timeout_seconds: float,
) -> tuple[ValidationResult | None, str | None]:
    command = [
        sys.executable,
        "-c",
        _REFERENCE_SCRIPT,
        str(candidate_path),
        json.dumps(expected_n),
    ]
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            env=_reference_environment(verifier_commit),
            check=False,
        )
    except (subprocess.TimeoutExpired, OSError):
        return None, "REFERENCE_PROCESS_FAILED"

    if completed.returncode != 0:
        return None, "REFERENCE_PROCESS_FAILED"

    try:
        data = json.loads(completed.stdout.strip())
        return _result_from_mapping(data), None
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return None, "REFERENCE_OUTPUT_INVALID"


def _run_runtime(
    payload: Any,
    expected_n: int,
    verifier_commit: str,
) -> tuple[ValidationResult | None, str | None]:
    try:
        with _commit_environment(verifier_commit):
            return validate_runtime(payload, expected_n), None
    except Exception:
        return None, "RUNTIME_VALIDATION_FAILED"


def _decide_status(
    reference_result: ValidationResult | None,
    runtime_result: ValidationResult | None,
    reasons: list[str],
) -> str:
    if reference_result is None or runtime_result is None:
        if not reasons:
            reasons.append("VERIFICATION_INCOMPLETE")
        return UNCERTIFIED

    if reasons:
        return UNCERTIFIED

    if reference_result.valid and runtime_result.valid:
        return CERTIFIED

    if not reference_result.valid and not runtime_result.valid:
        reasons.append("INVALID_CANDIDATE")
        return INVALID

    reasons.append("VERDICT_DIVERGENCE")
    return UNCERTIFIED


def _identity_reasons(
    reference_result: ValidationResult,
    runtime_result: ValidationResult,
    candidate: Candidate,
    verifier_commit: str,
) -> list[str]:
    reasons: list[str] = []

    if (
        reference_result.validator_id != REFERENCE_VALIDATOR_ID
        or runtime_result.validator_id != RUNTIME_VALIDATOR_ID
    ):
        reasons.append("VALIDATOR_IDENTITY_MISMATCH")

    if (
        reference_result.code_commit != verifier_commit
        or runtime_result.code_commit != verifier_commit
    ):
        reasons.append("VERIFIER_COMMIT_MISMATCH")

    if (
        reference_result.payload_sha256 != candidate.content_sha256
        or runtime_result.payload_sha256 != candidate.content_sha256
    ):
        reasons.append("PAYLOAD_HASH_MISMATCH")

    if reference_result.computed_m != runtime_result.computed_m:
        reasons.append("VERDICT_DIVERGENCE")
    elif (
        reference_result.valid
        and runtime_result.valid
        and reference_result.computed_m != candidate.m
    ):
        reasons.append("COUNT_MISMATCH")

    return reasons


def export_candidate(
    candidate: Candidate,
    directory: str | Path,
    run_id: str,
) -> CandidateExport:
    """Exporta o payload canônico e o envelope sem hash autorreferente."""
    _check_candidate_consistency(candidate)
    _check_run_id(run_id)

    directory_path = Path(directory)
    directory_path.mkdir(parents=True, exist_ok=True)

    candidate_path = directory_path / CANDIDATE_FILENAME
    envelope_path = directory_path / ENVELOPE_FILENAME
    certificate_path = directory_path / CERTIFICATE_FILENAME

    candidate_path.write_bytes(candidate.canonical_bytes)

    envelope = {
        "run_id": run_id,
        "payload": candidate.payload,
        "content_sha256": candidate.content_sha256,
        "certificate": CERTIFICATE_FILENAME,
    }
    envelope_path.write_bytes(canonical_json_bytes(envelope))

    return CandidateExport(
        directory=directory_path,
        candidate_path=candidate_path,
        envelope_path=envelope_path,
        certificate_path=certificate_path,
        run_id=run_id,
        content_sha256=candidate.content_sha256,
    )


def certify_exported(
    exported: CandidateExport,
    candidate: Candidate,
    expected_n: int,
    verifier_commit: str,
    *,
    timeout_seconds: float = DEFAULT_REFERENCE_TIMEOUT_SECONDS,
) -> Certificate:
    """Relê a exportação, verifica os dois núcleos e grava o certificado."""
    _check_candidate_consistency(candidate)
    _check_common_inputs(expected_n, verifier_commit)
    _check_timeout(timeout_seconds)

    if not isinstance(exported, CandidateExport):
        raise TypeError("exported deve ser uma instância de CandidateExport")

    reasons: list[str] = []
    payload: Any = None
    runtime_result: ValidationResult | None = None
    reference_result: ValidationResult | None = None

    if exported.content_sha256 != candidate.content_sha256:
        reasons.append("EXPORT_IDENTITY_MISMATCH")

    try:
        raw_bytes = exported.candidate_path.read_bytes()
    except OSError:
        reasons.append("CANDIDATE_FILE_UNREADABLE")
    else:
        actual_hash = hashlib.sha256(raw_bytes).hexdigest()
        if actual_hash != candidate.content_sha256:
            reasons.append("CANDIDATE_HASH_MISMATCH")

        try:
            payload = json.loads(raw_bytes)
        except (json.JSONDecodeError, UnicodeDecodeError):
            reasons.append("CANDIDATE_FILE_UNREADABLE")

    if payload is not None:
        if isinstance(payload, dict) and "is_example" in payload:
            reasons.append("EXAMPLE_NOT_ALLOWED")

        runtime_result, runtime_error = _run_runtime(
            payload, expected_n, verifier_commit
        )
        if runtime_error is not None:
            reasons.append(runtime_error)

        reference_result, reference_error = _run_reference_subprocess(
            exported.candidate_path,
            expected_n,
            verifier_commit,
            timeout_seconds,
        )
        if reference_error is not None:
            reasons.append(reference_error)

    try:
        envelope = json.loads(exported.envelope_path.read_bytes())
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        reasons.append("ENVELOPE_UNREADABLE")
    else:
        if isinstance(envelope, dict) and "is_example" in envelope:
            reasons.append("EXAMPLE_NOT_ALLOWED")
        if (
            not isinstance(envelope, dict)
            or envelope.get("run_id") != exported.run_id
            or envelope.get("content_sha256") != candidate.content_sha256
            or envelope.get("certificate") != CERTIFICATE_FILENAME
            or envelope.get("payload") != payload
        ):
            reasons.append("ENVELOPE_MISMATCH")

    if reference_result is not None and runtime_result is not None:
        reasons.extend(
            _identity_reasons(
                reference_result,
                runtime_result,
                candidate,
                verifier_commit,
            )
        )

    status = _decide_status(reference_result, runtime_result, reasons)

    certificate = Certificate(
        candidate_sha256=candidate.content_sha256,
        run_id=exported.run_id,
        rules_id=candidate.rules_id,
        expected_n=expected_n,
        verifier_commit=verifier_commit,
        reference_result=reference_result,
        runtime_result=runtime_result,
        timestamp_utc=_utc_now(),
        status=status,
        reasons=_unique(reasons),
    )
    _write_certificate(exported.certificate_path, certificate)
    return certificate


def certify(
    candidate: Candidate,
    run_id: str,
    expected_n: int,
    verifier_commit: str,
    directory: str | Path,
    *,
    timeout_seconds: float = DEFAULT_REFERENCE_TIMEOUT_SECONDS,
) -> Certificate:
    """Exporta e certifica um candidato em um único passo."""
    exported = export_candidate(candidate, directory, run_id)
    return certify_exported(
        exported,
        candidate,
        expected_n,
        verifier_commit,
        timeout_seconds=timeout_seconds,
    )


def _write_certificate(path: Path, certificate: Certificate) -> None:
    serialized = json.dumps(
        certificate.to_dict(),
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
    )
    path.write_text(serialized + "\n", encoding="utf-8")


def _optional_result(data: Any) -> ValidationResult | None:
    if data is None:
        return None
    return _result_from_mapping(data)


def load_certificate(directory: str | Path) -> Certificate:
    """Carrega o certificado gravado; ausência ou conteúdo inválido são erros."""
    path = Path(directory) / CERTIFICATE_FILENAME
    data = json.loads(path.read_bytes())

    if not isinstance(data, dict):
        raise ValueError("certificado deve ser um objeto JSON")

    return Certificate(
        candidate_sha256=data["candidate_sha256"],
        run_id=data["run_id"],
        rules_id=data["rules_id"],
        expected_n=data["expected_n"],
        verifier_commit=data["verifier_commit"],
        reference_result=_optional_result(data.get("reference_result")),
        runtime_result=_optional_result(data.get("runtime_result")),
        timestamp_utc=data["timestamp_utc"],
        status=data["status"],
        reasons=tuple(data.get("reasons", ())),
    )
