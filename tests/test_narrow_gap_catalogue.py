"""Tests for Narrow Gap Frontier Target Catalogue (P191).

Validates:
1. Exactly 5 record targets frozen with gap <= 2.
2. No proven optimal targets in record set.
3. Candidate cyclic/circulant symmetry groups defined for all targets.
4. Snapshot SHA-256 integrity against disk files.
5. Verification of calibration objects.
6. Execution time under 10 seconds per target (< 0.2s per test).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import time

from evobyte.narrow_gap_catalogue import (
    CALIBRATION_TARGETS,
    NARROW_GAP_TARGETS,
    get_calibration_by_id,
    get_calibration_catalogue,
    get_narrow_gap_catalogue,
    get_target_by_id,
    verify_target_candidate,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGETS_DIR = REPO_ROOT / "docs" / "research" / "targets"
JSON_CATALOGUE_PATH = TARGETS_DIR / "narrow_gap_targets_v1.json"


def test_catalogue_target_count() -> None:
    """Gate 1: Exactly 5 narrow-gap record targets must be frozen."""
    targets = get_narrow_gap_catalogue()
    assert len(targets) == 5, f"Expected exactly 5 targets, got {len(targets)}"
    assert len(NARROW_GAP_TARGETS) == 5

    # Target families breakdown: 3 covering designs and 2 QECC stabilizer codes
    covering = [t for t in targets if t.family == "covering_design"]
    qecc = [t for t in targets if t.family == "qecc_stabilizer"]
    assert len(covering) == 3, f"Expected 3 covering designs, got {len(covering)}"
    assert len(qecc) == 2, f"Expected 2 QECC targets, got {len(qecc)}"


def test_narrow_gap_condition() -> None:
    """Gate 2: Every record target must satisfy gap <= 2 and gap >= 1."""
    targets = get_narrow_gap_catalogue()
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
    targets = get_narrow_gap_catalogue()
    for t in targets:
        assert t.proven_optimal is False, f"Record target {t.target_id} marked proven_optimal"
        assert t.role == "record"
        assert t.best_known_value != t.theoretical_bound


def test_candidate_symmetry_groups() -> None:
    """Algebraic attractiveness: Each target must define a symmetry group with order >= 4."""
    targets = get_narrow_gap_catalogue()
    for t in targets:
        assert len(t.candidate_symmetry_group) > 0
        assert t.symmetry_order >= 4, f"Target {t.target_id} symmetry order {t.symmetry_order} < 4"


def test_snapshot_sha256_integrity() -> None:
    """Provenience audit: Snapshot SHA-256 must be 64-character lowercase hex."""
    targets = get_narrow_gap_catalogue()
    for t in targets:
        assert len(t.snapshot_sha256) == 64
        assert re.fullmatch(r"[0-9a-f]{64}", t.snapshot_sha256)

    # Reconfirm against raw disk files if present in workspace
    coverdata_file = REPO_ROOT / "data" / "raw" / "frontier" / "coverdata.json"
    if coverdata_file.exists():
        h = hashlib.sha256(coverdata_file.read_bytes()).hexdigest()
        for t in targets:
            if t.family == "covering_design":
                assert t.snapshot_sha256 == h, f"SHA mismatch for {t.target_id}"

    qecc_14_3_file = REPO_ROOT / "data" / "raw" / "quantum" / "codetables_qecc_14_3.html"
    if qecc_14_3_file.exists():
        h = hashlib.sha256(qecc_14_3_file.read_bytes()).hexdigest()
        target = get_target_by_id("qecc_14_3_open")
        assert target.snapshot_sha256 == h

    qecc_16_5_file = REPO_ROOT / "data" / "raw" / "quantum" / "codetables_qecc_16_5.html"
    if qecc_16_5_file.exists():
        h = hashlib.sha256(qecc_16_5_file.read_bytes()).hexdigest()
        target = get_target_by_id("qecc_16_5_open")
        assert target.snapshot_sha256 == h


def test_calibration_targets_verify() -> None:
    """Calibration verification: All calibration targets must pass with expected values."""
    calibrations = get_calibration_catalogue()
    assert len(calibrations) >= 5

    for c in calibrations:
        assert c.proven_optimal is True
        assert c.role == "calibration"
        t0 = time.perf_counter()
        if c.family == "covering_design":
            from evobyte.frontier_catalogue import verify_covering_design

            ok, msg = verify_covering_design(
                c.certificate_object,
                c.params["v"],
                c.params["k"],
                c.params["t"],
            )
            assert ok is True, f"Calibration {c.target_id} failed: {msg}"
            assert len(c.certificate_object) == c.expected_value
        elif c.family == "qecc_stabilizer":
            from evobyte.qecc_verifier import code_distance

            ok, res = code_distance(c.certificate_object)
            assert ok is True, f"QECC calibration {c.target_id} failed: {res}"
            assert res["d"] == c.expected_value
        dt = time.perf_counter() - t0
        assert dt < 0.2, f"Calibration {c.target_id} took {dt:.3f}s >= 0.2s"


def test_reference_qecc_objects_verification_speed() -> None:
    """Published reference QECC stabilizers must compute distance in < 0.1s."""
    target_14_3 = get_target_by_id("qecc_14_3_open")
    target_16_5 = get_target_by_id("qecc_16_5_open")

    assert target_14_3.reference_object is not None
    assert target_16_5.reference_object is not None

    t0 = time.perf_counter()
    ok_14, res_14 = verify_target_candidate("qecc_14_3_open", target_14_3.reference_object)
    dt_14 = time.perf_counter() - t0
    assert ok_14 is True
    assert res_14["d"] == 4
    assert dt_14 < 0.1

    t1 = time.perf_counter()
    ok_16, res_16 = verify_target_candidate("qecc_16_5_open", target_16_5.reference_object)
    dt_16 = time.perf_counter() - t1
    assert ok_16 is True
    assert res_16["d"] == 4
    assert dt_16 < 0.1


def test_verifier_rejection_rules() -> None:
    """Robustness: Verifier functions reject invalid or corrupted candidates."""
    # 1. Covering design rejection: incomplete blocks
    incomplete_blocks = [(1, 2, 3), (4, 5, 6)]
    ok, msg = verify_target_candidate("covering_C_13_6_3", incomplete_blocks)
    assert ok is False
    assert "only" in msg or "size !=" in msg

    # 2. Unknown target ID
    ok_bad, msg_bad = verify_target_candidate("unknown_id_xyz", [])
    assert ok_bad is False
    assert "Unknown target_id" in msg_bad

    # 3. QECC non-commuting stabilizer
    bad_stab = ["X" * 14, "Z" + "I" * 13]  # X vs Z on first qubit -> non-commuting
    ok_stab, msg_stab = verify_target_candidate("qecc_14_3_open", bad_stab)
    assert ok_stab is False


def test_target_lookup_helpers() -> None:
    """Helper coverage: get_target_by_id and get_calibration_by_id."""
    t = get_target_by_id("covering_C_13_6_3")
    assert t.name == "C(13,6,3)"

    import pytest

    with pytest.raises(KeyError):
        get_target_by_id("non_existent_target")

    c = get_calibration_by_id("covering_C_7_3_2")
    assert c.expected_value == 7

    with pytest.raises(KeyError):
        get_calibration_by_id("non_existent_calibration")


def test_exported_json_integrity() -> None:
    """JSON artefact matches Python catalogue exactly."""
    assert JSON_CATALOGUE_PATH.exists()
    with JSON_CATALOGUE_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["num_record_targets"] == 5
    assert len(data["targets"]) == 5
    assert len(data["calibrations"]) >= 5

    target_ids_json = [t["target_id"] for t in data["targets"]]
    target_ids_py = [t.target_id for t in NARROW_GAP_TARGETS]
    assert target_ids_json == target_ids_py
