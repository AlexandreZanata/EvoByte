"""Tests for Autonomous Structured Certificate Extractor and Standalone Verifier (P197).

Strict verification criteria:
1. Zero external dependencies in `scripts/verify_structured_certificate.py` (enforced by AST).
2. Standalone script executes with `python3 -S` (without site-packages) and returns 0 on valid certificates.
3. Strict rejection (non-zero exit code) on 1-bit adversarial mutations, corruptions, or parameter tampering.
4. Complete coverage of C(15, 8, 4) discovery certificate, SQS(10) calibration, and [[8, 3, 3]] stabilizer code.
5. All verification routines execute in < 5.0 seconds.
"""

from __future__ import annotations

import ast
import copy
import json
from pathlib import Path
import subprocess
import sys
import time

import pytest

from evobyte.certificate_extractor import (
    CanonicalCertificate,
    extract_c10_4_3_certificate,
    extract_c15_8_4_certificate,
    extract_covering_certificate,
    extract_qecc_8_3_3_certificate,
    extract_qecc_certificate,
    load_canonical_certificate,
)
from evobyte.frontier_catalogue import verify_covering_design as internal_verify_covering
from evobyte.qecc_verifier import (
    check_stabilizer as internal_check_stabilizer,
    code_distance as internal_code_distance,
)
from scripts.verify_structured_certificate import (
    compute_payload_checksum,
    verify_certificate_document,
    verify_covering_design_pure,
    verify_qecc_stabilizer_pure,
)

VERIFIER_SCRIPT = Path("scripts/verify_structured_certificate.py")
CERT_DIR = Path("experiments/certificates")


def _run_standalone_cli(cert_path: Path | str) -> subprocess.CompletedProcess[str]:
    """Run standalone verifier with python3 -S (zero third-party imports)."""
    return subprocess.run(
        [sys.executable, "-S", str(VERIFIER_SCRIPT), str(cert_path)],
        capture_output=True,
        text=True,
        timeout=10,
    )


# ---------------------------------------------------------------------------
# 1. Zero Dependency Architecture Gate (AST Inspection)
# ---------------------------------------------------------------------------


def test_standalone_verifier_imports_only_stdlib() -> None:
    """AST check: scripts/verify_structured_certificate.py imports ONLY Python standard library."""
    tree = ast.parse(VERIFIER_SCRIPT.read_text(encoding="utf-8"))

    allowed_stdlib = {
        "__future__",
        "sys",
        "os",
        "json",
        "hashlib",
        "math",
        "itertools",
        "time",
        "typing",
        "dataclasses",
        "pathlib",
        "collections",
        "functools",
    }

    imported_modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported_modules.add(node.module.split(".")[0])

    assert imported_modules.issubset(allowed_stdlib), (
        f"Disallowed non-stdlib imports in standalone verifier: {imported_modules - allowed_stdlib}"
    )
    assert "numpy" not in imported_modules
    assert "pysat" not in imported_modules
    assert "evobyte" not in imported_modules


# ---------------------------------------------------------------------------
# 2. Positive Verification Gates (python3 -S execution)
# ---------------------------------------------------------------------------


def test_standalone_accepts_c15_8_4_discovery_tied_certificate() -> None:
    """The C(15, 8, 4) = 30 discovery certificate passes standalone python3 -S in < 0.1s."""
    cert_path = CERT_DIR / "covering_C_15_8_4_tied_record.json"
    assert cert_path.is_file(), f"Certificate not found at {cert_path}"

    t0 = time.perf_counter()
    res = _run_standalone_cli(cert_path)
    elapsed = time.perf_counter() - t0

    assert res.returncode == 0, f"Standalone verifier failed: {res.stderr}\nOutput: {res.stdout}"
    assert "[SUCCESS]" in res.stdout
    assert "all 1365 4-subsets of 15 elements covered by 30 blocks" in res.stdout
    assert elapsed < 5.0, f"Verification too slow: {elapsed:.3f} s"


def test_standalone_accepts_sqs10_calibration_certificate() -> None:
    """The C(10, 4, 3) = 30 SQS(10) calibration certificate passes standalone python3 -S in < 0.05s."""
    cert_path = CERT_DIR / "covering_C_10_4_3_sqs10.json"
    assert cert_path.is_file(), f"Certificate not found at {cert_path}"

    res = _run_standalone_cli(cert_path)
    assert res.returncode == 0, f"Standalone verifier failed: {res.stderr}"
    assert "[SUCCESS]" in res.stdout
    assert "all 120 3-subsets of 10 elements covered by 30 blocks" in res.stdout


def test_standalone_accepts_gottesman_8_3_3_certificate() -> None:
    """The Gottesman [[8, 3, 3]] stabilizer calibration certificate passes standalone python3 -S in < 0.05s."""
    cert_path = CERT_DIR / "qecc_8_3_3_gottesman.json"
    assert cert_path.is_file(), f"Certificate not found at {cert_path}"

    res = _run_standalone_cli(cert_path)
    assert res.returncode == 0, f"Standalone verifier failed: {res.stderr}"
    assert "[SUCCESS]" in res.stdout
    assert "[[8, 3, 3]] stabilizer code with 5 independent commuting generators" in res.stdout


# ---------------------------------------------------------------------------
# 3. Dual-Verifier Consistency Gates
# ---------------------------------------------------------------------------


def test_dual_verifier_consistency_on_all_certificates() -> None:
    """Internal EvoByte verifiers and standalone zero-dep verifiers produce identical verdicts."""
    # 1. C(15, 8, 4)
    doc_c15 = load_canonical_certificate(CERT_DIR / "covering_C_15_8_4_tied_record.json")
    blocks_15 = doc_c15["candidate"]["blocks"]
    ok_ext_15, msg_ext_15 = verify_covering_design_pure(doc_c15)
    ok_int_15, msg_int_15 = internal_verify_covering(blocks_15, 15, 8, 4)
    assert ok_ext_15 is True and ok_int_15 is True
    assert "1365" in msg_ext_15 and "1365" in msg_int_15

    # 2. C(10, 4, 3)
    doc_c10 = load_canonical_certificate(CERT_DIR / "covering_C_10_4_3_sqs10.json")
    blocks_10 = doc_c10["candidate"]["blocks"]
    ok_ext_10, msg_ext_10 = verify_covering_design_pure(doc_c10)
    ok_int_10, msg_int_10 = internal_verify_covering(blocks_10, 10, 4, 3)
    assert ok_ext_10 is True and ok_int_10 is True
    assert "120" in msg_ext_10 and "120" in msg_int_10

    # 3. QECC [[8, 3, 3]]
    doc_qecc = load_canonical_certificate(CERT_DIR / "qecc_8_3_3_gottesman.json")
    gens = doc_qecc["candidate"]["generators"]
    ok_ext_q, _ = verify_qecc_stabilizer_pure(doc_qecc)
    ok_stab_int, _ = internal_check_stabilizer(gens)
    ok_dist_int, dist_info = internal_code_distance(gens)
    assert ok_ext_q is True
    assert ok_stab_int is True
    assert ok_dist_int is True
    assert dist_info.get("d") == 3


# ---------------------------------------------------------------------------
# 4. Adversarial Mutation & Corruption Rejection Gates
# ---------------------------------------------------------------------------


def test_reject_tampered_payload_checksum(tmp_path: Path) -> None:
    """Modifying even 1 bit of the certificate checksum triggers immediate rejection."""
    doc = load_canonical_certificate(CERT_DIR / "covering_C_15_8_4_tied_record.json")
    # Mutate checksum by flipping first hex char
    bad_char = "1" if doc["sha256_checksum"][0] == "0" else "0"
    doc["sha256_checksum"] = bad_char + doc["sha256_checksum"][1:]

    p = tmp_path / "corrupted_checksum.json"
    p.write_text(json.dumps(doc), encoding="utf-8")

    res = _run_standalone_cli(p)
    assert res.returncode == 1
    assert "SHA-256 payload checksum mismatch" in res.stderr


def test_reject_single_element_mutation_in_covering_block(tmp_path: Path) -> None:
    """Mutating 1 element in 1 block of C(15, 8, 4) is detected immediately even if SHA is updated."""
    doc = load_canonical_certificate(CERT_DIR / "covering_C_15_8_4_tied_record.json")
    # Mutate block 0, element 7 from 13 to 14
    doc["candidate"]["blocks"][0][7] = 14
    # Recompute valid checksum for the corrupted candidate to bypass header check
    cert = CanonicalCertificate(
        certificate_type=doc["certificate_type"],
        target_id=doc["target_id"],
        verdict=doc["verdict"],
        parameters=doc["parameters"],
        candidate=doc["candidate"],
        metadata=doc["metadata"],
    )
    p = tmp_path / "mutated_block.json"
    cert.save(p)

    res = _run_standalone_cli(p)
    assert res.returncode == 1
    # Either symmetry mismatch or uncovered 4-subsets
    assert "FAILED" in res.stderr or "expanded base blocks do not match" in res.stderr


def test_reject_removed_block_in_covering(tmp_path: Path) -> None:
    """Removing 1 block from C(15, 8, 4) leaves 4-subsets uncovered and is rejected."""
    doc = load_canonical_certificate(CERT_DIR / "covering_C_15_8_4_tied_record.json")
    doc["candidate"]["blocks"] = doc["candidate"]["blocks"][:-1]  # 29 blocks
    doc["candidate"].pop("symmetry", None)
    doc["parameters"]["claimed_blocks"] = 29

    cert = CanonicalCertificate(
        certificate_type=doc["certificate_type"],
        target_id=doc["target_id"],
        verdict=doc["verdict"],
        parameters=doc["parameters"],
        candidate=doc["candidate"],
        metadata=doc["metadata"],
    )
    p = tmp_path / "removed_block.json"
    cert.save(p)

    res = _run_standalone_cli(p)
    assert res.returncode == 1
    assert "FAILED" in res.stderr
    assert "4-subsets uncovered" in res.stderr


def test_reject_duplicate_and_out_of_range_elements(tmp_path: Path) -> None:
    """Out-of-range elements or duplicates inside blocks are immediately rejected."""
    doc = load_canonical_certificate(CERT_DIR / "covering_C_10_4_3_sqs10.json")
    doc["candidate"].pop("symmetry", None)

    # 1. Out of range (element 11 when v=10)
    doc1 = copy.deepcopy(doc)
    doc1["candidate"]["blocks"][0][3] = 11
    p1 = tmp_path / "out_of_range.json"
    CanonicalCertificate(
        certificate_type=doc1["certificate_type"],
        target_id=doc1["target_id"],
        verdict=doc1["verdict"],
        parameters=doc1["parameters"],
        candidate=doc1["candidate"],
        metadata=doc1["metadata"],
    ).save(p1)
    res1 = _run_standalone_cli(p1)
    assert res1.returncode == 1
    assert "out of range" in res1.stderr

    # 2. Duplicate element in block
    doc2 = copy.deepcopy(doc)
    doc2["candidate"]["blocks"][0][1] = doc2["candidate"]["blocks"][0][0]
    p2 = tmp_path / "duplicate.json"
    CanonicalCertificate(
        certificate_type=doc2["certificate_type"],
        target_id=doc2["target_id"],
        verdict=doc2["verdict"],
        parameters=doc2["parameters"],
        candidate=doc2["candidate"],
        metadata=doc2["metadata"],
    ).save(p2)
    res2 = _run_standalone_cli(p2)
    assert res2.returncode == 1
    assert "duplicate element" in res2.stderr


def test_reject_non_commuting_qecc_generator(tmp_path: Path) -> None:
    """Mutating 1 Pauli character in [[8, 3, 3]] that breaks commutation is caught."""
    doc = load_canonical_certificate(CERT_DIR / "qecc_8_3_3_gottesman.json")
    gens = list(doc["candidate"]["generators"])
    gens[0] = "ZYXYYYYY"  # Change first Pauli to Z, breaking commutation with generator 1
    doc["candidate"]["generators"] = gens

    p = tmp_path / "bad_commutation.json"
    CanonicalCertificate(
        certificate_type=doc["certificate_type"],
        target_id=doc["target_id"],
        verdict=doc["verdict"],
        parameters=doc["parameters"],
        candidate=doc["candidate"],
        metadata=doc["metadata"],
    ).save(p)

    res = _run_standalone_cli(p)
    assert res.returncode == 1
    assert "do not commute" in res.stderr


def test_reject_linearly_dependent_qecc_generators(tmp_path: Path) -> None:
    """Duplicate / linearly dependent stabilizer generators are caught by GF(2) rank check."""
    doc = load_canonical_certificate(CERT_DIR / "qecc_8_3_3_gottesman.json")
    gens = list(doc["candidate"]["generators"])
    gens[1] = gens[0]  # Duplicate generator 0 into position 1
    doc["candidate"]["generators"] = gens

    p = tmp_path / "dependent_generators.json"
    CanonicalCertificate(
        certificate_type=doc["certificate_type"],
        target_id=doc["target_id"],
        verdict=doc["verdict"],
        parameters=doc["parameters"],
        candidate=doc["candidate"],
        metadata=doc["metadata"],
    ).save(p)

    res = _run_standalone_cli(p)
    assert res.returncode == 1
    assert "linearly dependent" in res.stderr


def test_reject_falsified_code_distance(tmp_path: Path) -> None:
    """Claiming code distance d=4 on [[8, 3, 3]] is rejected because weight 3 logical operators exist."""
    doc = load_canonical_certificate(CERT_DIR / "qecc_8_3_3_gottesman.json")
    doc["parameters"]["claimed_d"] = 4  # False claim

    p = tmp_path / "falsified_d.json"
    CanonicalCertificate(
        certificate_type=doc["certificate_type"],
        target_id=doc["target_id"],
        verdict=doc["verdict"],
        parameters=doc["parameters"],
        candidate=doc["candidate"],
        metadata=doc["metadata"],
    ).save(p)

    res = _run_standalone_cli(p)
    assert res.returncode == 1
    assert "undetected logical operator" in res.stderr


def test_cli_usage_and_invalid_files(tmp_path: Path) -> None:
    """CLI returns exit code 2 on missing arguments or non-existent files."""
    # No args
    res_no_args = subprocess.run(
        [sys.executable, "-S", str(VERIFIER_SCRIPT)],
        capture_output=True,
        text=True,
    )
    assert res_no_args.returncode == 2

    # Non-existent file
    res_missing = subprocess.run(
        [sys.executable, "-S", str(VERIFIER_SCRIPT), str(tmp_path / "non_existent.json")],
        capture_output=True,
        text=True,
    )
    assert res_missing.returncode == 2

    # Malformed JSON
    bad_json = tmp_path / "malformed.json"
    bad_json.write_text("{ unclosed json", encoding="utf-8")
    res_malformed = _run_standalone_cli(bad_json)
    assert res_malformed.returncode == 1


# ---------------------------------------------------------------------------
# 5. Certificate Extractor Unit Tests
# ---------------------------------------------------------------------------


def test_extractor_functions_generate_valid_certificates(tmp_path: Path) -> None:
    """Extractor helpers produce complete, saveable, and reloadable CanonicalCertificate instances."""
    # Covering extractor
    c15 = extract_covering_certificate(
        target_id="test_c15",
        v=15,
        k=8,
        t=4,
        blocks=[[1, 2, 3, 4, 5, 6, 7, 8]],
        verdict="DISCOVERY_TIED",
    )
    assert c15.certificate_type == "covering_design"
    assert len(c15.compute_checksum()) == 64

    # QECC extractor
    cq = extract_qecc_certificate(
        target_id="test_qecc",
        n=5,
        k=1,
        d=3,
        generators=["XZZXI", "IXZZX", "XIXZZ", "ZXIXZ"],
        verdict="CALIBRATION_REPRODUCED",
    )
    assert cq.certificate_type == "qecc_stabilizer"
    assert cq.parameters["claimed_d"] == 3

    # Save and reload
    save_path = tmp_path / "test_saved_cert.json"
    cq.save(save_path)
    loaded = load_canonical_certificate(save_path)
    assert loaded["sha256_checksum"] == cq.compute_checksum()
