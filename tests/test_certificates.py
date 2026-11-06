"""Testes de exportação e certificado independente (F01-T06)."""

from __future__ import annotations

from dataclasses import asdict, replace
from datetime import datetime
import json
import subprocess

import pytest

from evobyte import certificates as certificates_module
from evobyte.candidate import (
    Candidate,
    canonical_json_bytes,
    compute_content_sha256,
    create_candidate,
)
from evobyte.certificates import (
    CANDIDATE_FILENAME,
    CERTIFICATE_FILENAME,
    CERTIFIED,
    ENVELOPE_FILENAME,
    INVALID,
    UNCERTIFIED,
    certify,
    certify_exported,
    export_candidate,
    load_certificate,
)
from evobyte.validation.reference import validate as validate_reference
from evobyte.validation.runtime import validate as validate_runtime


def c5_candidate():
    return create_candidate(
        n=5,
        edges=[[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]],
    )


def forged_candidate(payload):
    canonical = canonical_json_bytes(payload)
    return Candidate(
        payload=payload,
        canonical_bytes=canonical,
        content_sha256=compute_content_sha256(canonical),
    )


def fake_reference_run(result):
    data = asdict(result)

    def run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout=json.dumps(data),
            stderr="",
        )

    return run


def test_export_writes_canonical_payload_and_envelope(tmp_path):
    candidate = c5_candidate()
    exported = export_candidate(candidate, tmp_path, "run-export-1")

    assert exported.directory == tmp_path
    assert exported.candidate_path == tmp_path / CANDIDATE_FILENAME
    assert exported.envelope_path == tmp_path / ENVELOPE_FILENAME
    assert exported.certificate_path == tmp_path / CERTIFICATE_FILENAME
    assert exported.content_sha256 == candidate.content_sha256

    assert exported.candidate_path.read_bytes() == candidate.canonical_bytes

    envelope = json.loads(exported.envelope_path.read_bytes())
    assert envelope["run_id"] == "run-export-1"
    assert envelope["payload"] == candidate.payload
    assert envelope["content_sha256"] == candidate.content_sha256
    assert envelope["certificate"] == CERTIFICATE_FILENAME
    assert "certificate_sha256" not in envelope


def test_certify_c5_is_certified(tmp_path):
    candidate = c5_candidate()
    certificate = certify(candidate, "run-1", 5, "abc123", tmp_path)

    assert certificate.status == CERTIFIED
    assert certificate.reasons == ()
    assert certificate.candidate_sha256 == candidate.content_sha256
    assert certificate.run_id == "run-1"
    assert certificate.rules_id == "girth-ge-5-v1"
    assert certificate.expected_n == 5
    assert certificate.verifier_commit == "abc123"
    assert certificate.reference_result is not None
    assert certificate.runtime_result is not None
    assert certificate.reference_result.valid is True
    assert certificate.runtime_result.valid is True
    assert certificate.reference_result.validator_id == "evobyte-reference"
    assert certificate.runtime_result.validator_id == "evobyte-runtime"
    assert certificate.reference_result.code_commit == "abc123"
    assert certificate.runtime_result.code_commit == "abc123"
    assert certificate.reference_result.payload_sha256 == candidate.content_sha256
    assert certificate.runtime_result.payload_sha256 == candidate.content_sha256
    assert certificate.reference_result.computed_m == 5
    assert certificate.runtime_result.computed_m == 5

    parsed_timestamp = datetime.fromisoformat(certificate.timestamp_utc)
    assert parsed_timestamp.tzinfo is not None

    certificate_path = tmp_path / CERTIFICATE_FILENAME
    assert certificate_path.exists()
    data = json.loads(certificate_path.read_bytes())
    assert data["status"] == CERTIFIED
    assert data["reference_result"]["valid"] is True
    assert data["runtime_result"]["valid"] is True
    assert "is_example" not in data


def test_certificate_round_trip(tmp_path):
    certificate = certify(c5_candidate(), "run-2", 5, "abc123", tmp_path)
    loaded = load_certificate(tmp_path)

    assert loaded == certificate
    assert loaded.status == CERTIFIED


def test_certify_empty_graph_is_certified(tmp_path):
    candidate = create_candidate(n=8, edges=[])
    certificate = certify(candidate, "empty", 8, "commit", tmp_path)

    assert certificate.status == CERTIFIED
    assert certificate.reference_result.computed_m == 0
    assert certificate.runtime_result.computed_m == 0


@pytest.mark.parametrize(
    "edges",
    [
        [[0, 1], [1, 2], [2, 0]],
        [[0, 1], [1, 2], [2, 3], [3, 0]],
    ],
    ids=["c3", "c4"],
)
def test_cycle_candidate_is_invalid(tmp_path, edges):
    candidate = create_candidate(n=5, edges=edges)
    certificate = certify(candidate, "invalid", 5, "commit", tmp_path)

    assert certificate.status == INVALID
    assert "INVALID_CANDIDATE" in certificate.reasons
    assert certificate.reference_result.valid is False
    assert certificate.runtime_result.valid is False
    assert (tmp_path / CERTIFICATE_FILENAME).exists()


def test_expected_n_mismatch_is_invalid(tmp_path):
    certificate = certify(c5_candidate(), "n-mismatch", 6, "commit", tmp_path)

    assert certificate.status == INVALID
    assert "INVALID_CANDIDATE" in certificate.reasons
    assert certificate.reference_result.valid is False
    assert certificate.runtime_result.valid is False


def test_wrong_claimed_m_is_invalid(tmp_path):
    payload = {
        "schema_version": 1,
        "rules_id": "girth-ge-5-v1",
        "n": 5,
        "edges": [[0, 1]],
        "claimed_m": 2,
    }
    candidate = forged_candidate(payload)

    certificate = certify(candidate, "forged", 5, "commit", tmp_path)

    assert certificate.status == INVALID
    reference_codes = {
        violation.code for violation in certificate.reference_result.violations
    }
    runtime_codes = {
        violation.code for violation in certificate.runtime_result.violations
    }
    assert "CLAIMED_M_MISMATCH" in reference_codes
    assert "CLAIMED_M_MISMATCH" in runtime_codes


def test_altered_candidate_file_is_uncertified(tmp_path):
    candidate = c5_candidate()
    exported = export_candidate(candidate, tmp_path, "altered")

    with exported.candidate_path.open("ab") as handle:
        handle.write(b" ")

    certificate = certify_exported(exported, candidate, 5, "commit")

    assert certificate.status == UNCERTIFIED
    assert "CANDIDATE_HASH_MISMATCH" in certificate.reasons
    assert certificate.reference_result.valid is True
    assert certificate.runtime_result.valid is True
    assert exported.certificate_path.exists()


def test_truncated_candidate_file_is_uncertified(tmp_path):
    candidate = c5_candidate()
    exported = export_candidate(candidate, tmp_path, "truncated")
    exported.candidate_path.write_bytes(candidate.canonical_bytes[:-10])

    certificate = certify_exported(exported, candidate, 5, "commit")

    assert certificate.status == UNCERTIFIED
    assert "CANDIDATE_HASH_MISMATCH" in certificate.reasons
    assert "CANDIDATE_FILE_UNREADABLE" in certificate.reasons
    assert certificate.reference_result is None
    assert exported.certificate_path.exists()


def test_missing_candidate_file_is_uncertified(tmp_path):
    candidate = c5_candidate()
    exported = export_candidate(candidate, tmp_path, "missing")
    exported.candidate_path.unlink()

    certificate = certify_exported(exported, candidate, 5, "commit")

    assert certificate.status == UNCERTIFIED
    assert "CANDIDATE_FILE_UNREADABLE" in certificate.reasons
    assert certificate.reference_result is None


def test_envelope_mismatch_is_uncertified(tmp_path):
    candidate = c5_candidate()
    exported = export_candidate(candidate, tmp_path, "envelope")

    envelope = json.loads(exported.envelope_path.read_bytes())
    envelope["run_id"] = "outro-run"
    exported.envelope_path.write_text(json.dumps(envelope), encoding="utf-8")

    certificate = certify_exported(exported, candidate, 5, "commit")

    assert certificate.status == UNCERTIFIED
    assert "ENVELOPE_MISMATCH" in certificate.reasons


def test_missing_envelope_is_uncertified(tmp_path):
    candidate = c5_candidate()
    exported = export_candidate(candidate, tmp_path, "envelope-missing")
    exported.envelope_path.unlink()

    certificate = certify_exported(exported, candidate, 5, "commit")

    assert certificate.status == UNCERTIFIED
    assert "ENVELOPE_UNREADABLE" in certificate.reasons


def test_is_example_in_envelope_is_rejected(tmp_path):
    candidate = c5_candidate()
    exported = export_candidate(candidate, tmp_path, "example")

    envelope = json.loads(exported.envelope_path.read_bytes())
    envelope["is_example"] = True
    exported.envelope_path.write_text(json.dumps(envelope), encoding="utf-8")

    certificate = certify_exported(exported, candidate, 5, "commit")

    assert certificate.status == UNCERTIFIED
    assert "EXAMPLE_NOT_ALLOWED" in certificate.reasons
    assert certificate.reference_result.valid is True
    assert certificate.runtime_result.valid is True


def test_reference_process_timeout_is_uncertified(tmp_path, monkeypatch):
    candidate = c5_candidate()
    exported = export_candidate(candidate, tmp_path, "timeout")

    def fail(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="python", timeout=1)

    monkeypatch.setattr("evobyte.certificates.subprocess.run", fail)

    certificate = certify_exported(exported, candidate, 5, "commit")

    assert certificate.status == UNCERTIFIED
    assert "REFERENCE_PROCESS_FAILED" in certificate.reasons
    assert certificate.reference_result is None
    assert certificate.runtime_result is not None


def test_reference_process_nonzero_exit_is_uncertified(tmp_path, monkeypatch):
    candidate = c5_candidate()
    exported = export_candidate(candidate, tmp_path, "exit")

    def fail(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=1,
            stdout="",
            stderr="falha",
        )

    monkeypatch.setattr("evobyte.certificates.subprocess.run", fail)

    certificate = certify_exported(exported, candidate, 5, "commit")

    assert certificate.status == UNCERTIFIED
    assert "REFERENCE_PROCESS_FAILED" in certificate.reasons
    assert certificate.reference_result is None


def test_reference_output_invalid_is_uncertified(tmp_path, monkeypatch):
    candidate = c5_candidate()
    exported = export_candidate(candidate, tmp_path, "bad-output")

    def fail(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout="nao-e-json",
            stderr="",
        )

    monkeypatch.setattr("evobyte.certificates.subprocess.run", fail)

    certificate = certify_exported(exported, candidate, 5, "commit")

    assert certificate.status == UNCERTIFIED
    assert "REFERENCE_OUTPUT_INVALID" in certificate.reasons
    assert certificate.reference_result is None


def test_payload_hash_divergence_is_uncertified(tmp_path, monkeypatch):
    candidate = c5_candidate()
    exported = export_candidate(candidate, tmp_path, "hash-divergence")
    result = validate_reference(candidate.payload, 5)
    data = asdict(result)
    data["payload_sha256"] = "0" * 64

    def run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout=json.dumps(data),
            stderr="",
        )

    monkeypatch.setattr("evobyte.certificates.subprocess.run", run)

    certificate = certify_exported(exported, candidate, 5, "commit")

    assert certificate.status == UNCERTIFIED
    assert "PAYLOAD_HASH_MISMATCH" in certificate.reasons
    assert exported.certificate_path.exists()


def test_verifier_commit_mismatch_is_uncertified(tmp_path, monkeypatch):
    candidate = c5_candidate()
    exported = export_candidate(candidate, tmp_path, "commit-mismatch")
    result = validate_reference(candidate.payload, 5)
    data = asdict(result)
    data["code_commit"] = "outro-commit"

    def run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout=json.dumps(data),
            stderr="",
        )

    monkeypatch.setattr("evobyte.certificates.subprocess.run", run)

    certificate = certify_exported(exported, candidate, 5, "commit")

    assert certificate.status == UNCERTIFIED
    assert "VERIFIER_COMMIT_MISMATCH" in certificate.reasons


def test_divergent_runtime_verdict_is_uncertified(tmp_path, monkeypatch):
    candidate = c5_candidate()
    exported = export_candidate(candidate, tmp_path, "divergence")

    def broken_runtime(payload, expected_n):
        return replace(
            validate_runtime(payload, expected_n),
            valid=False,
        )

    monkeypatch.setattr("evobyte.certificates.validate_runtime", broken_runtime)

    certificate = certify_exported(exported, candidate, 5, "commit")

    assert certificate.status == UNCERTIFIED
    assert "VERDICT_DIVERGENCE" in certificate.reasons
    assert certificate.reference_result.valid is True
    assert certificate.runtime_result.valid is False
    assert exported.certificate_path.exists()


def test_export_identity_mismatch_is_uncertified(tmp_path):
    candidate = c5_candidate()
    exported = export_candidate(candidate, tmp_path, "export-identity")
    forged_export = replace(exported, content_sha256="0" * 64)

    certificate = certify_exported(forged_export, candidate, 5, "commit")

    assert certificate.status == UNCERTIFIED
    assert "EXPORT_IDENTITY_MISMATCH" in certificate.reasons


def test_reference_subprocess_script_is_independent():
    script = certificates_module._REFERENCE_SCRIPT
    assert "from evobyte.validation.reference import validate" in script
    for forbidden in (
        "evobyte.validation.runtime",
        "evobyte.candidate",
        "evobyte.search",
        "numpy",
        "torch",
    ):
        assert forbidden not in script


def test_export_rejects_inconsistent_candidate(tmp_path):
    candidate = c5_candidate()
    broken = replace(candidate, content_sha256="0" * 64)

    with pytest.raises(ValueError):
        export_candidate(broken, tmp_path, "broken")


def test_invalid_arguments_are_rejected(tmp_path):
    candidate = c5_candidate()

    with pytest.raises(ValueError):
        certify(candidate, "", 5, "commit", tmp_path)

    with pytest.raises(ValueError):
        certify(candidate, "run", 0, "commit", tmp_path)

    with pytest.raises(ValueError):
        certify(candidate, "run", True, "commit", tmp_path)

    with pytest.raises(ValueError):
        certify(candidate, "run", 5, "", tmp_path)

    with pytest.raises(ValueError):
        certify(candidate, "run", 5, "commit", tmp_path, timeout_seconds=0)


def test_load_certificate_raises_when_absent(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_certificate(tmp_path)
