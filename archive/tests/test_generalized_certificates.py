"""Unit tests for Autonomous Generalized Certificate Verifier (P207).

Verifies:
1. All canonical v3.0.0 and v2.0.0 certificates in experiments/certificates/ validate successfully.
2. Adversarial corruption detection (single-bit flip, mutated generator, dropped block,
   tampered checksum, non-commuting operator) is rejected 100% of the time.
3. Extractor roundtrip and deterministic SHA-256 payload checksums.
4. Standalone CLI execution via pure Python standard library (`python3 -S`).
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest

from evobyte.generalized_certificate_extractor import (
    extract_affine_covering_certificate,
    extract_null_bound_certificate,
    extract_qecc_certificate,
)
from scripts.verify_generalized_certificate import (
    compute_payload_checksum,
    verify_certificate_document,
)


def test_all_extracted_certificates_validate():
    """Verify all certificates in experiments/certificates/*.json pass validation."""
    cert_dir = Path("experiments/certificates")
    cert_files = sorted(list(cert_dir.glob("*.json")))

    assert len(cert_files) >= 7, f"Expected at least 7 certificates, found {len(cert_files)}"

    for cf in cert_files:
        with cf.open("r", encoding="utf-8") as f:
            doc = json.load(f)

        valid, msg = verify_certificate_document(doc, check_sha=True)
        assert valid, f"Certificate {cf.name} failed verification: {msg}"


def test_adversarial_checksum_tampering_rejected():
    """Corrupting any field without recomputing sha256_checksum is immediately rejected."""
    cert_path = Path("experiments/certificates/qecc_14_3_tied_record.json")
    with cert_path.open("r", encoding="utf-8") as f:
        doc = json.load(f)

    # Mutate a parameter
    tampered_doc = copy.deepcopy(doc)
    tampered_doc["parameters"]["claimed_d"] = 5

    valid, msg = verify_certificate_document(tampered_doc, check_sha=True)
    assert not valid
    assert "checksum mismatch" in msg.lower()


def test_adversarial_stabilizer_noncommutation_rejected():
    """Mutating a Pauli generator breaks symplectic commutativity and is rejected."""
    cert_path = Path("experiments/certificates/qecc_14_3_tied_record.json")
    with cert_path.open("r", encoding="utf-8") as f:
        doc = json.load(f)

    tampered_doc = copy.deepcopy(doc)
    # Flip first character of generator 0
    g0 = tampered_doc["candidate"]["generators"][0]
    flipped_char = "Z" if g0[0] != "Z" else "X"
    tampered_doc["candidate"]["generators"][0] = flipped_char + g0[1:]
    # Recompute checksum so checksum check passes, forcing mathematical failure
    tampered_doc["sha256_checksum"] = compute_payload_checksum(tampered_doc)

    valid, msg = verify_certificate_document(tampered_doc, check_sha=True)
    assert not valid
    assert (
        "not commute" in msg.lower()
        or "linearly dependent" in msg.lower()
        or "undetected" in msg.lower()
    )


def test_adversarial_covering_dropped_block_rejected():
    """Removing a block from a minimal covering design is immediately rejected."""
    cert_path = Path("experiments/certificates/calib_covering_C_9_3_2.json")
    with cert_path.open("r", encoding="utf-8") as f:
        doc = json.load(f)

    tampered_doc = copy.deepcopy(doc)
    # Drop the first block
    tampered_doc["candidate"]["blocks"].pop(0)
    tampered_doc["parameters"]["claimed_blocks"] = len(tampered_doc["candidate"]["blocks"])
    tampered_doc["sha256_checksum"] = compute_payload_checksum(tampered_doc)

    valid, msg = verify_certificate_document(tampered_doc, check_sha=True)
    assert not valid
    assert "uncovered" in msg.lower() or "violation" in msg.lower()


def test_adversarial_null_bound_falsification_rejected():
    """Claiming a NULL_BOUND where min_orbit_length <= published_best is rejected."""
    cert_path = Path("experiments/certificates/covering_C_13_5_3_null_bound.json")
    with cert_path.open("r", encoding="utf-8") as f:
        doc = json.load(f)

    tampered_doc = copy.deepcopy(doc)
    # Claim min_orbit_length is smaller than published_best
    tampered_doc["candidate"]["min_orbit_length"] = 30
    tampered_doc["sha256_checksum"] = compute_payload_checksum(tampered_doc)

    valid, msg = verify_certificate_document(tampered_doc, check_sha=True)
    assert not valid
    assert "obstruction condition failed" in msg.lower()


def test_extractor_roundtrip():
    """Test extractor functions create valid, self-consistent certificates."""
    # Covering
    cert_cov = extract_affine_covering_certificate(
        target_id="test_cov",
        v=9,
        k=3,
        t=2,
        blocks=[
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9],
            [1, 4, 7],
            [2, 5, 8],
            [3, 6, 9],
            [1, 5, 9],
            [2, 6, 7],
            [3, 4, 8],
            [1, 6, 8],
            [2, 4, 9],
            [3, 5, 7],
        ],
        affine_plane=True,
    )
    doc_cov = cert_cov.to_dict()
    valid_cov, msg_cov = verify_certificate_document(doc_cov)
    assert valid_cov, msg_cov

    # QECC
    cert_qecc = extract_qecc_certificate(
        target_id="test_steane",
        n=7,
        k=1,
        claimed_d=3,
        generators=["IIIXXXX", "IXXIIXX", "XIXIXIX", "IIIZZZZ", "IZZIIZZ", "ZIZIZIZ"],
    )
    doc_qecc = cert_qecc.to_dict()
    valid_qecc, msg_qecc = verify_certificate_document(doc_qecc)
    assert valid_qecc, msg_qecc


def test_standalone_cli_execution():
    """Test executing scripts/verify_generalized_certificate.py via python3 -S."""
    cmd = [
        sys.executable,
        "-S",
        "scripts/verify_generalized_certificate.py",
        "experiments/certificates/calib_covering_C_9_3_2.json",
        "experiments/certificates/calib_steane_7_1_3.json",
        "experiments/certificates/calib_shor_9_1_3.json",
        "experiments/certificates/qecc_14_3_tied_record.json",
        "experiments/certificates/qecc_16_5_tied_record.json",
        "experiments/certificates/covering_C_13_5_3_null_bound.json",
        "experiments/certificates/covering_C_15_10_4_null_bound.json",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"CLI verification failed: {res.stderr}\n{res.stdout}"
    assert "ALL PASSED" in res.stdout
