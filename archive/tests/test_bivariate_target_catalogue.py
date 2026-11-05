"""Tests for Bivariate Target Catalogue (P211).

Validates:
1. Exactly 5 record targets frozen with gap <= 2.
2. Breakdown: 3 QECC stabilizer codes and 2 covering designs.
3. Anti-wall rule: No record target has proven_optimal=True.
4. Candidate bivariate/projective symmetry groups defined with symmetry_order >= 30.
5. Snapshot SHA-256 integrity against raw disk files.
6. Verification of all 3 calibration objects (Bravyi [[72,12,6]], Steane [[7,1,3]], C(9,3,2)).
7. Verifier execution time under 50 ms per verification.
8. JSON catalogue export round-trip integrity.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import time

from evobyte.bivariate_target_catalogue import (
    BIVARIATE_CALIBRATION_TARGETS,
    BIVARIATE_TARGETS,
    export_catalogue_to_json,
    get_bivariate_calibration_catalogue,
    get_bivariate_target_catalogue,
    get_calibration_by_id,
    get_target_by_id,
    verify_calibration_candidate,
    verify_target_candidate,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGETS_DIR = REPO_ROOT / "docs" / "research" / "targets"
JSON_CATALOGUE_PATH = TARGETS_DIR / "bivariate_targets_v1.json"


def test_catalogue_target_count() -> None:
    """Gate 1: Exactly 5 bivariate/projective record targets must be frozen."""
    targets = get_bivariate_target_catalogue()
    assert len(targets) == 5, f"Expected exactly 5 targets, got {len(targets)}"
    assert len(BIVARIATE_TARGETS) == 5

    qecc = [t for t in targets if t.family == "qecc_stabilizer"]
    covering = [t for t in targets if t.family == "covering_design"]
    assert len(qecc) == 3, f"Expected 3 QECC targets, got {len(qecc)}"
    assert len(covering) == 2, f"Expected 2 covering designs, got {len(covering)}"


def test_narrow_gap_condition() -> None:
    """Gate 2: Every record target must satisfy 1 <= gap <= 2."""
    targets = get_bivariate_target_catalogue()
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
    targets = get_bivariate_target_catalogue()
    for t in targets:
        assert t.proven_optimal is False, f"Record target {t.target_id} marked proven_optimal"
        assert t.role == "record"
        assert t.best_known_value != t.theoretical_bound


def test_candidate_bivariate_symmetry_groups() -> None:
    """Each target must define a bivariate or projective symmetry group with order >= 30."""
    targets = get_bivariate_target_catalogue()
    for t in targets:
        assert len(t.candidate_symmetry_group) > 0
        assert t.symmetry_order >= 30, (
            f"Target {t.target_id} symmetry order {t.symmetry_order} < 30"
        )


def test_snapshot_sha256_integrity() -> None:
    """Snapshot SHA-256 must be 64-character lowercase hex and match disk snapshots."""
    targets = get_bivariate_target_catalogue()
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

    raw_qecc_18_3 = REPO_ROOT / "data" / "raw" / "quantum" / "codetables_qecc_18_3.html"
    if raw_qecc_18_3.exists():
        h = hashlib.sha256(raw_qecc_18_3.read_bytes()).hexdigest()
        assert get_target_by_id("qecc_18_3_bivariate").snapshot_sha256 == h

    raw_qecc_20_3 = REPO_ROOT / "data" / "raw" / "quantum" / "codetables_qecc_20_3.html"
    if raw_qecc_20_3.exists():
        h = hashlib.sha256(raw_qecc_20_3.read_bytes()).hexdigest()
        assert get_target_by_id("qecc_20_3_bivariate").snapshot_sha256 == h

    raw_qecc_20_2 = REPO_ROOT / "data" / "raw" / "quantum" / "codetables_qecc_20_2.html"
    if raw_qecc_20_2.exists():
        h = hashlib.sha256(raw_qecc_20_2.read_bytes()).hexdigest()
        assert get_target_by_id("qecc_20_2_bivariate").snapshot_sha256 == h


def test_calibration_targets_verification() -> None:
    """Gate 3: All 3 calibration objects must verify successfully."""
    calibs = get_bivariate_calibration_catalogue()
    assert len(calibs) == 3, f"Expected 3 calibration targets, got {len(calibs)}"
    assert len(BIVARIATE_CALIBRATION_TARGETS) == 3

    # 1. Bravyi 72-12-6 bivariate bicycle code
    c_bravyi = get_calibration_by_id("calib_bravyi_72_12_6")
    ok, payload = verify_calibration_candidate(c_bravyi.target_id, c_bravyi.certificate_object)
    assert ok is True, f"Bravyi [[72,12,6]] verification failed: {payload}"
    assert payload["k"] == 12
    assert payload["n"] == 72
    assert payload["d"] == 6

    # 2. Steane 7-qubit CSS code
    c_steane = get_calibration_by_id("calib_steane_7_1_3")
    ok, payload = verify_calibration_candidate(c_steane.target_id, c_steane.certificate_object)
    assert ok is True, f"Steane verification failed: {payload}"
    assert payload["distance"]["k"] == 1
    assert payload["distance"]["d"] == 3

    # 3. AG(2, 3) covering design
    c_cov = get_calibration_by_id("calib_covering_C_9_3_2")
    ok, msg = verify_calibration_candidate(c_cov.target_id, c_cov.certificate_object)
    assert ok is True, f"C(9,3,2) verification failed: {msg}"
    assert len(c_cov.certificate_object) == 12


def test_verifier_timing_under_50ms() -> None:
    """Gate 4: Verifier execution time must be under 50 ms per verification."""
    targets = get_bivariate_target_catalogue()
    for t in targets:
        if t.family == "qecc_stabilizer":
            t0 = time.perf_counter()
            ok, payload = verify_target_candidate(
                t.target_id, t.reference_object, check_distance=False
            )
            dt_ms = (time.perf_counter() - t0) * 1000.0
            assert ok is True, f"Target {t.target_id} reference verification failed: {payload}"
            assert dt_ms < 50.0, f"Target {t.target_id} took {dt_ms:.2f} ms (> 50 ms)"

    # Also check calibration targets timing under 50 ms
    calibs = get_bivariate_calibration_catalogue()
    for c in calibs:
        t0 = time.perf_counter()
        ok, payload = verify_calibration_candidate(c.target_id, c.certificate_object)
        dt_ms = (time.perf_counter() - t0) * 1000.0
        assert ok is True, f"Calibration target {c.target_id} failed: {payload}"
        assert dt_ms < 50.0, f"Calibration target {c.target_id} took {dt_ms:.2f} ms (> 50 ms)"


def test_json_catalogue_roundtrip(tmp_path: Path) -> None:
    """Gate 5: Catalogue JSON dump and reload roundtrip."""
    test_json = tmp_path / "bivariate_test.json"
    export_catalogue_to_json(test_json)

    assert test_json.exists()
    content = json.loads(test_json.read_text(encoding="utf-8"))
    assert content["target_count"] == 5
    assert content["calibration_count"] == 3
    assert len(content["targets"]) == 5
    assert len(content["calibrations"]) == 3

    # Ensure frozen committed catalogue matches
    if JSON_CATALOGUE_PATH.exists():
        committed_content = json.loads(JSON_CATALOGUE_PATH.read_text(encoding="utf-8"))
        assert committed_content["target_count"] == 5
        assert committed_content["calibration_count"] == 3
