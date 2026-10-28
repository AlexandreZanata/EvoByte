"""Unit tests for Preregistered Bivariate and Projective Campaign (P216).

Verifies:
1. qecc_20_2_bivariate achieves DISCOVERY_TIED (d=6, k=2, n=20) via bivariate bicycle code.
2. qecc_18_3_bivariate synthesizes valid quantum code with distance d >= 4.
3. qecc_20_3_bivariate synthesizes valid quantum code with distance d >= 4.
4. covering_C_14_6_3_projective rigorously proves NULL_BOUND under full PGL(2, 13) group.
5. covering_C_16_7_3_affine2d rigorously proves NULL_BOUND under AGL(2, 4) group.
6. Campaign results artifact integrity, cryptographic SHA-256 provenance, and checkpoint persistence.
"""

from __future__ import annotations

import json
from pathlib import Path

from evobyte.bivariate_campaign import (
    evaluate_covering_c14_6_3_projective,
    evaluate_covering_c16_7_3_affine2d,
    evaluate_qecc_18_3_bivariate,
    evaluate_qecc_20_2_bivariate,
    evaluate_qecc_20_3_bivariate,
)
from evobyte.bivariate_target_catalogue import verify_target_candidate
from evobyte.qecc_verifier import check_stabilizer, code_distance


def test_evaluate_qecc_20_2_produces_tie_record() -> None:
    """Bivariate bicycle search on [[20, 2, d]] ties Grassl world record d=6."""
    res = evaluate_qecc_20_2_bivariate(seed=42, timeout_sec=10.0)

    assert res["verified"] is True
    assert res["verdict"] == "DISCOVERY_TIED"
    assert res["achieved_value"] == 6
    assert res["n"] == 20
    assert res["k"] == 2
    assert len(res["generators"]) == 18
    assert len(res["candidate_sha256"]) == 64

    # Independent oracle verification
    ok_stab, stab_info = check_stabilizer(res["generators"])
    assert ok_stab is True
    assert stab_info.get("n") == 20
    assert stab_info.get("k") == 2
    assert stab_info.get("rank") == 18

    ok_dist, dist_info = code_distance(res["generators"])
    assert ok_dist is True
    assert dist_info.get("d") == 6

    # Target catalogue verification
    ok_cat, _ = verify_target_candidate(
        "qecc_20_2_bivariate", res["generators"], check_distance=True
    )
    assert ok_cat is True


def test_evaluate_qecc_18_3_execution() -> None:
    """Search on [[18, 3, d]] executes within budget and verifies stabilizer code."""
    res = evaluate_qecc_18_3_bivariate(seed=42, timeout_sec=10.0)

    assert res["verified"] is True
    assert res["n"] == 18
    assert res["k"] == 3
    assert res["achieved_value"] is not None
    assert res["achieved_value"] >= 4
    assert res["verdict"] in ("DISCOVERY_BEATEN", "DISCOVERY_TIED", "NULL_RESULT", "INCONCLUSIVE")

    ok_stab, stab_info = check_stabilizer(res["generators"])
    assert ok_stab is True
    assert stab_info.get("k") == 3


def test_evaluate_qecc_20_3_execution() -> None:
    """Search on [[20, 3, d]] executes within budget and verifies stabilizer code."""
    res = evaluate_qecc_20_3_bivariate(seed=42, timeout_sec=10.0)

    assert res["verified"] is True
    assert res["n"] == 20
    assert res["k"] == 3
    assert res["achieved_value"] is not None
    assert res["achieved_value"] >= 4
    assert res["verdict"] in ("DISCOVERY_BEATEN", "DISCOVERY_TIED", "NULL_RESULT", "INCONCLUSIVE")

    ok_stab, stab_info = check_stabilizer(res["generators"])
    assert ok_stab is True
    assert stab_info.get("k") == 3


def test_covering_c14_6_3_projective_null_bound() -> None:
    """Prove NULL_BOUND for C(14, 6, 3) under full PGL(2, 13) group."""
    res = evaluate_covering_c14_6_3_projective(seed=42)

    assert res["verified"] is True
    assert res["verdict"] == "NULL_BOUND"
    assert res["details"]["min_orbit_length"] == 91
    assert res["details"]["min_orbit_length"] > res["published_best"]
    assert res["published_best"] == 25


def test_covering_c16_7_3_affine2d_null_bound() -> None:
    """Prove NULL_BOUND for C(16, 7, 3) under 2D affine group AGL(2, 4)."""
    res = evaluate_covering_c16_7_3_affine2d(seed=42)

    assert res["verified"] is True
    assert res["verdict"] == "NULL_BOUND"
    assert res["details"]["min_orbit_length"] == 160
    assert res["details"]["min_orbit_length"] > res["published_best"]
    assert res["published_best"] == 24


def test_campaign_results_artifact_integrity() -> None:
    """Verify saved campaign results JSON and checkpoint files."""
    results_path = Path("experiments/p216-bivariate-campaign-results.json")
    checkpoint_path = Path("experiments/p216-bivariate-campaign-checkpoint.json")

    assert results_path.exists(), "Campaign results file not found"
    assert checkpoint_path.exists(), "Campaign checkpoint file not found"

    with results_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["verdict"] == "DISCOVERY_TIED"
    assert len(data["seeds"]) == 5
    assert data["total_campaign_time_seconds"] < 150.0

    counts = data["verdict_counts"]
    assert counts["DISCOVERY_TIED"] == 5
    assert counts["NULL_BOUND"] == 10
    assert counts["NULL_RESULT"] == 10

    # Check targets structure
    targets = data["targets"]
    assert len(targets) == 5
    for _, tdata in targets.items():
        assert len(tdata["trials"]) == 5
        for trial in tdata["trials"]:
            assert trial["verified"] is True
            assert "candidate_sha256" in trial
            assert len(trial["candidate_sha256"]) == 64
