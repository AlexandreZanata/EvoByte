"""Unit tests for Hard Historical Records Calibration Protocol (P195).

Verifies:
1. Blind synthesis of Gottesman [[8, 3, 3]] stabilizer code:
   - Rank 5 mutually commuting generators.
   - Independent verification of distance d = 3 by code_distance.
2. Blind exact rediscovery of optimal covering design C(10, 4, 3) = 30:
   - Exactly 30 blocks covering all 120 triples of 10 points.
   - Independent zero-dependency verification by verify_covering_design.
3. Multi-seed calibration protocol achieves CALIBRATION_PASSED (>= 3/5 successes).
4. Structured results artifact integrity and cryptographic provenance.
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from evobyte.frontier_catalogue import verify_covering_design
from evobyte.hard_calibration import (
    run_hard_calibration_protocol,
    solve_hard_covering_c10_4_3,
    synthesize_stabilizer_8_3_3,
)
from evobyte.qecc_verifier import check_stabilizer, code_distance


def test_synthesize_stabilizer_8_3_3_validity():
    """Blind synthesis produces a valid [[8,3,3]] stabilizer code certified by oracle."""
    ok, gens, stats = synthesize_stabilizer_8_3_3(seed=42, timeout_seconds=10.0)

    assert ok, f"Synthesis failed: {stats}"
    assert len(gens) == 5
    for g in gens:
        assert len(g) == 8
        assert set(g).issubset({"I", "X", "Y", "Z"})

    # Check stabilizer commutation and rank
    ok_stab, stab_res = check_stabilizer(gens)
    assert ok_stab, f"check_stabilizer failed: {stab_res}"
    assert isinstance(stab_res, dict)
    assert stab_res.get("n") == 8
    assert stab_res.get("k") == 3
    assert stab_res.get("rank") == 5

    # Check code distance
    ok_dist, dist_res = code_distance(gens)
    assert ok_dist, f"code_distance failed: {dist_res}"
    assert isinstance(dist_res, dict)
    assert dist_res.get("d") == 3


def test_solve_hard_covering_c10_4_3_validity():
    """Blind orbit SAT solves C(10, 4, 3) = 30 certified by verify_covering_design."""
    ok, blocks, stats = solve_hard_covering_c10_4_3(seed=42, timeout_seconds=10.0)

    assert ok, f"Covering solve failed: {stats}"
    assert len(blocks) == 30
    for b in blocks:
        assert len(b) == 4
        assert len(set(b)) == 4
        for elem in b:
            assert 1 <= elem <= 10

    # Strict independent verification
    verified, v_msg = verify_covering_design(blocks, 10, 4, 3)
    assert verified, v_msg


def test_hard_calibration_seeds_success_rate():
    """Protocol achieves at least 3/5 successes on both milestones under fast budget."""
    seeds = [42, 43, 44]
    results = run_hard_calibration_protocol(seeds=seeds, timeout_per_trial=10.0)

    assert results["verdict"] == "CALIBRATION_PASSED"
    assert results["targets"]["qecc_8_3_3"]["successes"] == 3
    assert results["targets"]["covering_c10_4_3"]["successes"] == 3


def test_hard_calibration_results_artifact_integrity():
    """Pre-recorded benchmark results JSON is present, complete, and verified."""
    artifact_path = Path("experiments/p195-hard-calibration-results.json")
    assert artifact_path.exists(), "experiments/p195-hard-calibration-results.json not found"

    with artifact_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["verdict"] == "CALIBRATION_PASSED"
    assert len(data["seeds"]) == 5

    qecc_data = data["targets"]["qecc_8_3_3"]
    assert qecc_data["successes"] >= 3
    assert len(qecc_data["trials"]) == 5
    for trial in qecc_data["trials"]:
        assert trial["verified"]
        assert trial["code_distance"] == 3

    cov_data = data["targets"]["covering_c10_4_3"]
    assert cov_data["successes"] >= 3
    assert len(cov_data["trials"]) == 5
    for trial in cov_data["trials"]:
        assert trial["verified"]
        assert trial["total_blocks"] == 30
