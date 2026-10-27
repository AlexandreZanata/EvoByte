"""Tests for Generalized Target Catalogue (P201).

Validates:
1. Exactly 5 record targets frozen with gap <= 2.
2. Breakdown: 3 QECC stabilizer codes and 2 covering designs.
3. Anti-wall rule: No record target has proven_optimal=True.
4. Candidate generalized symmetry groups defined with symmetry_order >= 4.
5. Snapshot SHA-256 integrity against raw disk files.
6. Verification of all 3 calibration objects (Shor, Steane, C(9,3,2)).
7. Verifier execution time under 50 ms per verification.
8. JSON catalogue export round-trip integrity.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import time

from evobyte.generalized_target_catalogue import (
    CALIBRATION_TARGETS,
    GENERALIZED_TARGETS,
    export_catalogue_to_json,
    get_calibration_by_id,
    get_generalized_calibration_catalogue,
    get_generalized_target_catalogue,
    get_target_by_id,
    verify_calibration_candidate,
    verify_target_candidate,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGETS_DIR = REPO_ROOT / "docs" / "research" / "targets"
JSON_CATALOGUE_PATH = TARGETS_DIR / "generalized_targets_v1.json"


def test_catalogue_target_count() -> None:
    """Gate 1: Exactly 5 generalized record targets must be frozen."""
    targets = get_generalized_target_catalogue()
    assert len(targets) == 5, f"Expected exactly 5 targets, got {len(targets)}"
    assert len(GENERALIZED_TARGETS) == 5

    qecc = [t for t in targets if t.family == "qecc_stabilizer"]
    covering = [t for t in targets if t.family == "covering_design"]
    assert len(qecc) == 3, f"Expected 3 QECC targets, got {len(qecc)}"
    assert len(covering) == 2, f"Expected 2 covering designs, got {len(covering)}"


def test_narrow_gap_condition() -> None:
    """Gate 2: Every record target must satisfy 1 <= gap <= 2."""
    targets = get_generalized_target_catalogue()
    for t in targets:
        assert 1 <= t.gap <= 2, f"Target {t.target_id} has gap {t.gap} not in [1, 2]"
        if t.family == "covering_design":
            expected_gap = t.best_known_value - t.theoretical_bound
            assert t.gap == expected_gap
        elif t.family == "qecc_stabilizer":
            expected_gap = t.theoretical_bound - t.best_known_value
            assert t.gap == expected_gap


def test_no_proven_optimal_targets() -> None:
    """Anti-wall rule: No record target has proven_optimal=True or zero gap."""
    targets = get_generalized_target_catalogue()
    for t in targets:
        assert t.proven_optimal is False, f"Record target {t.target_id} marked proven_optimal"
        assert t.role == "record"
        assert t.best_known_value != t.theoretical_bound


def test_candidate_generalized_symmetry_groups() -> None:
    """Each target must define a generalized symmetry group with order >= 4."""
    targets = get_generalized_target_catalogue()
    for t in targets:
        assert len(t.candidate_symmetry_group) > 0
        assert t.symmetry_order >= 4, f"Target {t.target_id} symmetry order {t.symmetry_order} < 4"


def test_snapshot_sha256_integrity() -> None:
    """Snapshot SHA-256 must be 64-character lowercase hex and match disk snapshots."""
    targets = get_generalized_target_catalogue()
    for t in targets:
        assert len(t.snapshot_sha256) == 64
        assert re.fullmatch(r"[0-9a-f]{64}", t.snapshot_sha256)

    # Check against raw disk files
    coverdata_file = REPO_ROOT / "data" / "raw" / "frontier" / "coverdata.json"
    if coverdata_file.exists():
        h = hashlib.sha256(coverdata_file.read_bytes()).hexdigest()
        for t in targets:
            if t.family == "covering_design":
                assert t.snapshot_sha256 == h

    raw_qecc_14_3 = REPO_ROOT / "data" / "raw" / "quantum" / "codetables_qecc_14_3.html"
    if raw_qecc_14_3.exists():
        h = hashlib.sha256(raw_qecc_14_3.read_bytes()).hexdigest()
        assert get_target_by_id("qecc_14_3_noncirculant").snapshot_sha256 == h

    raw_qecc_16_5 = REPO_ROOT / "data" / "raw" / "quantum" / "codetables_qecc_16_5.html"
    if raw_qecc_16_5.exists():
        h = hashlib.sha256(raw_qecc_16_5.read_bytes()).hexdigest()
        assert get_target_by_id("qecc_16_5_noncirculant").snapshot_sha256 == h

    raw_qecc_18_3 = REPO_ROOT / "data" / "raw" / "quantum" / "codetables_qecc_18_3.html"
    if raw_qecc_18_3.exists():
        h = hashlib.sha256(raw_qecc_18_3.read_bytes()).hexdigest()
        assert get_target_by_id("qecc_18_3_noncirculant").snapshot_sha256 == h


def test_calibration_targets_verification() -> None:
    """Gate 3: All 3 calibration targets must verify correctly and fast."""
    calibs = get_generalized_calibration_catalogue()
    assert len(calibs) == 3

    # Shor [[9,1,3]]
    t0 = time.perf_counter()
    ok_shor, payload_shor = verify_calibration_candidate("calib_shor_9_1_3", get_calibration_by_id("calib_shor_9_1_3").certificate_object)
    dt_shor = time.perf_counter() - t0
    assert ok_shor is True
    assert payload_shor["check"]["n"] == 9
    assert payload_shor["check"]["k"] == 1
    assert payload_shor["distance"]["d"] == 3
    assert dt_shor < 0.05, f"Shor verification took {dt_shor:.4f}s >= 0.05s"

    # Steane [[7,1,3]]
    t0 = time.perf_counter()
    ok_steane, payload_steane = verify_calibration_candidate("calib_steane_7_1_3", get_calibration_by_id("calib_steane_7_1_3").certificate_object)
    dt_steane = time.perf_counter() - t0
    assert ok_steane is True
    assert payload_steane["check"]["n"] == 7
    assert payload_steane["check"]["k"] == 1
    assert payload_steane["distance"]["d"] == 3
    assert dt_steane < 0.05, f"Steane verification took {dt_steane:.4f}s >= 0.05s"

    # C(9,3,2) = 12
    t0 = time.perf_counter()
    ok_cov, payload_cov = verify_calibration_candidate("calib_covering_C_9_3_2", get_calibration_by_id("calib_covering_C_9_3_2").certificate_object)
    dt_cov = time.perf_counter() - t0
    assert ok_cov is True
    assert "covered" in str(payload_cov)
    assert dt_cov < 0.05, f"C(9,3,2) verification took {dt_cov:.4f}s >= 0.05s"


def test_qecc_reference_verification() -> None:
    """Verification of stored Grassl reference stabilizer generators."""
    # Check 14-3
    t14 = get_target_by_id("qecc_14_3_noncirculant")
    ok14, p14 = verify_target_candidate(t14.target_id, t14.reference_object)
    assert ok14 is True
    assert p14["check"]["n"] == 14
    assert p14["check"]["k"] == 3

    # Check 16-5
    t16 = get_target_by_id("qecc_16_5_noncirculant")
    ok16, p16 = verify_target_candidate(t16.target_id, t16.reference_object)
    assert ok16 is True
    assert p16["check"]["n"] == 16
    assert p16["check"]["k"] == 5


def test_json_catalogue_round_trip(tmp_path: Path) -> None:
    """Exported JSON file matches the python dataclass definitions."""
    tmp_json = tmp_path / "test_catalogue.json"
    export_catalogue_to_json(tmp_json)
    assert tmp_json.exists()

    with open(tmp_json, encoding="utf-8") as f:
        data = json.load(f)

    assert data["target_count"] == 5
    assert data["calibration_count"] == 3
    assert len(data["targets"]) == 5
    assert len(data["calibrations"]) == 3

    # Check committed file matches schema
    assert JSON_CATALOGUE_PATH.exists()
    with open(JSON_CATALOGUE_PATH, encoding="utf-8") as f:
        comm_data = json.load(f)
    assert comm_data["target_count"] == 5
    assert comm_data["calibration_count"] == 3
