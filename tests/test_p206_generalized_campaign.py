"""Unit tests for Preregistered Generalized Symmetry Campaign (P206).

Verifies:
1. qecc_14_3_noncirculant achieves DISCOVERY_TIED (d=4, k=3, n=14) breaking circulant obstruction.
2. qecc_16_5_noncirculant achieves DISCOVERY_TIED (d=4, k=5, n=16) breaking circulant obstruction.
3. qecc_18_3_noncirculant synthesizes valid quantum code with distance d >= 4.
4. covering_C_13_5_3_affine rigorously proves NULL_BOUND under full AGL(1, 13) group.
5. covering_C_15_10_4_affine rigorously proves NULL_BOUND under dihedral group D_15.
6. Campaign results artifact integrity, cryptographic SHA-256 provenance, and checkpoint persistence.
"""

from __future__ import annotations

import json
from pathlib import Path

from evobyte.generalized_campaign import (
    evaluate_covering_c13_5_3_affine,
    evaluate_covering_c15_10_4_affine,
    evaluate_qecc_14_3,
    evaluate_qecc_16_5,
    evaluate_qecc_18_3,
)
from evobyte.qecc_verifier import check_stabilizer, code_distance


def test_evaluate_qecc_14_3_produces_tie_record():
    """Blind search on [[14, 3, d]] ties Grassl world record d=4 via non-circulant CSS."""
    res = evaluate_qecc_14_3(seed=42, timeout_sec=10.0)

    assert res["verified"] is True
    assert res["verdict"] == "DISCOVERY_TIED"
    assert res["achieved_value"] == 4
    assert res["n"] == 14
    assert res["k"] == 3
    assert len(res["generators"]) == 11
    assert len(res["candidate_sha256"]) == 64

    # Independent oracle verification
    ok_stab, stab_info = check_stabilizer(res["generators"])
    assert ok_stab is True
    assert stab_info.get("n") == 14
    assert stab_info.get("k") == 3
    assert stab_info.get("rank") == 11

    ok_dist, dist_info = code_distance(res["generators"])
    assert ok_dist is True
    assert dist_info.get("d") == 4


def test_evaluate_qecc_16_5_produces_tie_record():
    """Blind search on [[16, 5, d]] ties Grassl world record d=4 via non-circulant CSS."""
    res = evaluate_qecc_16_5(seed=42, timeout_sec=10.0)

    assert res["verified"] is True
    assert res["verdict"] == "DISCOVERY_TIED"
    assert res["achieved_value"] == 4
    assert res["n"] == 16
    assert res["k"] == 5
    assert len(res["generators"]) == 11
    assert len(res["candidate_sha256"]) == 64

    # Independent oracle verification
    ok_stab, stab_info = check_stabilizer(res["generators"])
    assert ok_stab is True
    assert stab_info.get("n") == 16
    assert stab_info.get("k") == 5
    assert stab_info.get("rank") == 11

    ok_dist, dist_info = code_distance(res["generators"])
    assert ok_dist is True
    assert dist_info.get("d") == 4


def test_evaluate_qecc_18_3_execution():
    """Search on [[18, 3, d]] executes within budget and verifies stabilizer code."""
    res = evaluate_qecc_18_3(seed=42, timeout_sec=10.0)

    assert res["verified"] is True
    assert res["n"] == 18
    assert res["k"] == 3
    assert res["achieved_value"] >= 4
    assert res["verdict"] in ("DISCOVERY_BEATEN", "DISCOVERY_TIED", "NULL_RESULT")

    ok_stab, stab_info = check_stabilizer(res["generators"])
    assert ok_stab is True
    assert stab_info.get("k") == 3


def test_covering_c13_5_3_affine_null_bound():
    """Prove NULL_BOUND for C(13, 5, 3) under full AGL(1, 13) group."""
    res = evaluate_covering_c13_5_3_affine(seed=42)

    assert res["verified"] is True
    assert res["verdict"] == "NULL_BOUND"
    assert res["details"]["min_orbit_length"] == 39
    assert res["details"]["min_orbit_length"] > res["published_best"]
    assert res["published_best"] == 34


def test_covering_c15_10_4_affine_null_bound():
    """Prove NULL_BOUND for C(15, 10, 4) under dihedral group D_15."""
    res = evaluate_covering_c15_10_4_affine(seed=42)

    assert res["verified"] is True
    assert res["verdict"] == "NULL_BOUND"
    assert res["details"]["min_non_trivial_orbit_length"] == 15
    assert res["details"]["min_non_trivial_orbit_length"] > res["published_best"]
    assert res["published_best"] == 14


def test_campaign_results_artifact_integrity():
    """Verify saved campaign results JSON and checkpoint files."""
    results_path = Path("experiments/p206-generalized-campaign-results.json")
    checkpoint_path = Path("experiments/p206-generalized-campaign-checkpoint.json")

    assert results_path.exists(), "Campaign results file not found"
    assert checkpoint_path.exists(), "Campaign checkpoint file not found"

    with results_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["verdict"] == "DISCOVERY_TIED"
    assert len(data["seeds"]) == 5
    assert data["total_campaign_time_seconds"] < 150.0  # well below budget

    counts = data["verdict_counts"]
    assert counts["DISCOVERY_TIED"] == 10
    assert counts["NULL_BOUND"] == 10
    assert counts["NULL_RESULT"] == 5

    # Check targets structure
    targets = data["targets"]
    assert len(targets) == 5
    for tid, tdata in targets.items():
        assert len(tdata["trials"]) == 5
        for trial in tdata["trials"]:
            assert trial["verified"] is True
            assert "candidate_sha256" in trial
            assert len(trial["candidate_sha256"]) == 64
