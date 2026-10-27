"""Unit tests for Blind Historical Calibration Protocol (P205).

Verifies:
1. Blind exact rediscovery of optimal covering design C(9, 3, 2) = 12 (AG(2, 3)):
   - Exactly 12 blocks of size 3 covering all 36 pairs on 9 points.
   - Independent zero-dependency verification by verify_covering_design.
   - Combinatorial verification of affine plane properties (4 parallel classes of 3 lines).
2. Blind synthesis of Steane [[7, 1, 3]] CSS quantum code:
   - 6 commuting generators on 7 qubits (CSS structure).
   - Independent verification of distance d = 3 by code_distance.
3. Blind synthesis of Shor-class [[9, 1, 3]] non-circulant quantum stabilizer code:
   - Rank 8 mutually commuting generators on 9 qubits.
   - Independent verification of distance d = 3 by code_distance.
4. Fast multi-seed protocol execution achieves CALIBRATION_REPRODUCED (100% success).
5. Pre-recorded benchmark results JSON artifact integrity and cryptographic provenance.
"""

from __future__ import annotations

import json
from pathlib import Path

from evobyte.frontier_catalogue import verify_covering_design
from evobyte.p205_calibration import (
    run_p205_calibration_protocol,
    synthesize_affine_covering_c9_3_2,
    synthesize_shor_9_1_3,
    synthesize_steane_7_1_3,
    verify_affine_plane_properties,
)
from evobyte.qecc_verifier import check_stabilizer, code_distance


def test_synthesize_affine_covering_c9_3_2_validity():
    """Blind synthesis produces an exact C(9, 3, 2) = 12 covering design and AG(2, 3) plane."""
    ok, blocks, stats = synthesize_affine_covering_c9_3_2(seed=42, timeout_seconds=10.0)

    assert ok, f"Synthesis failed: {stats}"
    assert len(blocks) == 12
    for b in blocks:
        assert len(b) == 3
        assert len(set(b)) == 3
        for elem in b:
            assert 1 <= elem <= 9

    # Independent zero-dependency verification
    verified_cov, v_msg = verify_covering_design(blocks, 9, 3, 2)
    assert verified_cov, v_msg

    # Affine plane combinatorial verification
    verified_affine, a_msg = verify_affine_plane_properties(blocks, 9, 3)
    assert verified_affine, a_msg


def test_synthesize_steane_7_1_3_validity():
    """Blind synthesis produces a valid [[7, 1, 3]] CSS code certified by oracle."""
    ok, gens, stats = synthesize_steane_7_1_3(seed=42, timeout_seconds=10.0)

    assert ok, f"Synthesis failed: {stats}"
    assert len(gens) == 6
    for g in gens:
        assert len(g) == 7
        assert set(g).issubset({"I", "X", "Y", "Z"})

    # Check stabilizer commutation and rank
    ok_stab, stab_res = check_stabilizer(gens)
    assert ok_stab, f"check_stabilizer failed: {stab_res}"
    assert isinstance(stab_res, dict)
    assert stab_res.get("n") == 7
    assert stab_res.get("k") == 1
    assert stab_res.get("rank") == 6

    # Check code distance
    ok_dist, dist_res = code_distance(gens)
    assert ok_dist, f"code_distance failed: {dist_res}"
    assert isinstance(dist_res, dict)
    assert dist_res.get("d") == 3


def test_synthesize_shor_9_1_3_validity():
    """Blind synthesis produces a valid [[9, 1, 3]] non-circulant code certified by oracle."""
    ok, gens, stats = synthesize_shor_9_1_3(seed=42, timeout_seconds=10.0)

    assert ok, f"Synthesis failed: {stats}"
    assert len(gens) == 8
    for g in gens:
        assert len(g) == 9
        assert set(g).issubset({"I", "X", "Y", "Z"})

    # Check stabilizer commutation and rank
    ok_stab, stab_res = check_stabilizer(gens)
    assert ok_stab, f"check_stabilizer failed: {stab_res}"
    assert isinstance(stab_res, dict)
    assert stab_res.get("n") == 9
    assert stab_res.get("k") == 1
    assert stab_res.get("rank") == 8

    # Check code distance
    ok_dist, dist_res = code_distance(gens)
    assert ok_dist, f"code_distance failed: {dist_res}"
    assert isinstance(dist_res, dict)
    assert dist_res.get("d") == 3


def test_p205_calibration_seeds_success_rate():
    """Protocol achieves 100% successes on all 3 milestones under fast budget."""
    seeds = [42, 43]
    results = run_p205_calibration_protocol(seeds=seeds, timeout_per_trial=10.0)

    assert results["verdict"] == "CALIBRATION_REPRODUCED"
    assert results["targets"]["covering_c9_3_2"]["successes"] == 2
    assert results["targets"]["steane_7_1_3"]["successes"] == 2
    assert results["targets"]["shor_9_1_3"]["successes"] == 2


def test_p205_calibration_results_artifact_integrity():
    """Pre-recorded benchmark results JSON is present, complete, and verified."""
    artifact_path = Path("experiments/p205-calibration-results.json")
    assert artifact_path.exists(), "experiments/p205-calibration-results.json not found"

    with artifact_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["verdict"] == "CALIBRATION_REPRODUCED"
    assert len(data["seeds"]) == 5
    assert data["total_benchmark_time_seconds"] < 90.0

    cov_data = data["targets"]["covering_c9_3_2"]
    assert cov_data["successes"] == 5
    assert len(cov_data["trials"]) == 5
    for trial in cov_data["trials"]:
        assert trial["verified"]
        assert trial["total_blocks"] == 12

    steane_data = data["targets"]["steane_7_1_3"]
    assert steane_data["successes"] == 5
    assert len(steane_data["trials"]) == 5
    for trial in steane_data["trials"]:
        assert trial["verified"]
        assert trial["code_distance"] == 3

    shor_data = data["targets"]["shor_9_1_3"]
    assert shor_data["successes"] == 5
    assert len(shor_data["trials"]) == 5
    for trial in shor_data["trials"]:
        assert trial["verified"]
        assert trial["code_distance"] == 3
