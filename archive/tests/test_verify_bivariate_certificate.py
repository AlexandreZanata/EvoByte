"""Unit tests for Standalone Zero-Dependency Bivariate Certificate Verifier (P217).

Verifies:
1. All canonical v4.0.0 certificates in experiments/certificates/v4/ validate successfully.
2. Average verification latency across all certificates is strictly < 2.0 ms.
3. Adversarial corruption detection (tampered checksum, non-commuting Pauli generator,
   linearly dependent generator, falsified code distance, corrupted COO matrix,
   falsified NULL_BOUND, dropped covering block) is rejected 100% of the time (0 false positives).
4. Standalone CLI execution via pure Python standard library (`python3 -S`).
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys
import time

from scripts.verify_bivariate_certificate import (
    compute_payload_checksum,
    verify_certificate_document,
)


def test_all_v4_certificates_pass_verification() -> None:
    """Verify all 7 certificates in experiments/certificates/v4/*.json pass validation in < 2 ms avg."""
    cert_dir = Path("experiments/certificates/v4")
    cert_files = sorted(list(cert_dir.glob("*.json")))

    assert len(cert_files) == 7, f"Expected exactly 7 v4 certificates, found {len(cert_files)}"

    times_ms: list[float] = []
    for cf in cert_files:
        with cf.open("r", encoding="utf-8") as f:
            doc = json.load(f)

        t0 = time.perf_counter()
        valid, msg = verify_certificate_document(doc, check_sha=True)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        times_ms.append(elapsed_ms)

        assert valid, f"Certificate {cf.name} failed verification: {msg}"

    avg_ms = sum(times_ms) / len(times_ms)
    assert avg_ms < 2.0, f"Average verification time {avg_ms:.2f} ms exceeds 2.0 ms threshold"


def test_adversarial_checksum_tampering_rejected() -> None:
    """Corrupting any field without recomputing sha256_checksum is immediately rejected."""
    cert_path = Path("experiments/certificates/v4/qecc_20_2_tied_record.json")
    with cert_path.open("r", encoding="utf-8") as f:
        doc = json.load(f)

    tampered_doc = copy.deepcopy(doc)
    tampered_doc["parameters"]["claimed_d"] = 7

    valid, msg = verify_certificate_document(tampered_doc, check_sha=True)
    assert not valid
    assert "checksum mismatch" in msg.lower()


def test_adversarial_stabilizer_noncommutation_rejected() -> None:
    """Mutating a Pauli generator breaks symplectic commutativity and is rejected."""
    cert_path = Path("experiments/certificates/v4/qecc_20_2_tied_record.json")
    with cert_path.open("r", encoding="utf-8") as f:
        doc = json.load(f)

    tampered_doc = copy.deepcopy(doc)
    # Flip first character of generator 0 from X/I to Z
    g0 = tampered_doc["candidate"]["generators"][0]
    flipped_char = "Z" if g0[0] != "Z" else "X"
    tampered_doc["candidate"]["generators"][0] = flipped_char + g0[1:]
    tampered_doc["sha256_checksum"] = compute_payload_checksum(tampered_doc)

    valid, msg = verify_certificate_document(tampered_doc, check_sha=True)
    assert not valid
    assert (
        "not commute" in msg.lower()
        or "linearly dependent" in msg.lower()
        or "undetected" in msg.lower()
        or "coo matrix" in msg.lower()
    )


def test_adversarial_linear_dependence_rejected() -> None:
    """Duplicating a generator creates linear dependence (rank < m) and is rejected."""
    cert_path = Path("experiments/certificates/v4/qecc_20_2_tied_record.json")
    with cert_path.open("r", encoding="utf-8") as f:
        doc = json.load(f)

    tampered_doc = copy.deepcopy(doc)
    # Duplicate generator 0 into generator 1
    tampered_doc["candidate"]["generators"][1] = tampered_doc["candidate"]["generators"][0]
    tampered_doc["sha256_checksum"] = compute_payload_checksum(tampered_doc)

    valid, msg = verify_certificate_document(tampered_doc, check_sha=True)
    assert not valid
    assert "linearly dependent" in msg.lower() or "rank" in msg.lower()


def test_adversarial_falsified_code_distance_rejected() -> None:
    """Inflating claimed code distance (e.g. claiming d=7 on a d=6 code) is rejected."""
    cert_path = Path("experiments/certificates/v4/qecc_20_2_tied_record.json")
    with cert_path.open("r", encoding="utf-8") as f:
        doc = json.load(f)

    tampered_doc = copy.deepcopy(doc)
    tampered_doc["parameters"]["claimed_d"] = 7
    tampered_doc["sha256_checksum"] = compute_payload_checksum(tampered_doc)

    valid, msg = verify_certificate_document(tampered_doc, check_sha=True)
    assert not valid
    assert "undetected" in msg.lower() or "error" in msg.lower()


def test_adversarial_coo_matrix_tampering_rejected() -> None:
    """Modifying a coordinate in COO representation is rejected."""
    cert_path = Path("experiments/certificates/v4/qecc_20_2_tied_record.json")
    with cert_path.open("r", encoding="utf-8") as f:
        doc = json.load(f)

    tampered_doc = copy.deepcopy(doc)
    # Alter first coordinate entry
    tampered_doc["candidate"]["coo_matrices"]["HX"][0] = [0, 19]
    tampered_doc["sha256_checksum"] = compute_payload_checksum(tampered_doc)

    valid, msg = verify_certificate_document(tampered_doc, check_sha=True)
    assert not valid
    assert "coo matrix" in msg.lower()


def test_adversarial_bivariate_polynomial_noncommutation_rejected() -> None:
    """Tampering with polynomial terms in bivariate bicycle certificate is rejected."""
    cert_path = Path("experiments/certificates/v4/calib_bravyi_72_12_6.json")
    with cert_path.open("r", encoding="utf-8") as f:
        doc = json.load(f)

    tampered_doc = copy.deepcopy(doc)
    # Mutate polynomial terms of A
    tampered_doc["candidate"]["terms_a"] = [[1, 2], [3, 4]]
    tampered_doc["candidate"]["terms_b"] = [[0, 1], [2, 0]]
    tampered_doc["sha256_checksum"] = compute_payload_checksum(tampered_doc)

    valid, msg = verify_certificate_document(tampered_doc, check_sha=True)
    assert not valid
    assert (
        "do not commute" in msg.lower()
        or "ab != ba" in msg.lower()
        or "coo matrix" in msg.lower()
        or "polynomial terms" in msg.lower()
    )


def test_adversarial_null_bound_falsification_rejected() -> None:
    """Claiming a NULL_BOUND where min_orbit_length <= published_best is rejected."""
    cert_path = Path("experiments/certificates/v4/covering_C_14_6_3_null_bound.json")
    with cert_path.open("r", encoding="utf-8") as f:
        doc = json.load(f)

    tampered_doc = copy.deepcopy(doc)
    tampered_doc["candidate"]["min_orbit_length"] = 20
    tampered_doc["sha256_checksum"] = compute_payload_checksum(tampered_doc)

    valid, msg = verify_certificate_document(tampered_doc, check_sha=True)
    assert not valid
    assert "obstruction condition failed" in msg.lower()


def test_adversarial_covering_dropped_block_rejected() -> None:
    """Removing a block from a covering design is immediately rejected."""
    cert_path = Path("experiments/certificates/v4/calib_covering_C_9_3_2.json")
    with cert_path.open("r", encoding="utf-8") as f:
        doc = json.load(f)

    tampered_doc = copy.deepcopy(doc)
    tampered_doc["candidate"]["blocks"].pop(0)
    tampered_doc["parameters"]["claimed_blocks"] = len(tampered_doc["candidate"]["blocks"])
    tampered_doc["sha256_checksum"] = compute_payload_checksum(tampered_doc)

    valid, msg = verify_certificate_document(tampered_doc, check_sha=True)
    assert not valid
    assert "uncovered" in msg.lower() or "violation" in msg.lower()


def test_standalone_cli_execution() -> None:
    """Test executing scripts/verify_bivariate_certificate.py via python3 -S."""
    cmd = [
        sys.executable,
        "-S",
        "scripts/verify_bivariate_certificate.py",
        "experiments/certificates/v4/*.json",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"CLI verification failed: {res.stderr}\n{res.stdout}"
    assert "ALL PASSED" in res.stdout
