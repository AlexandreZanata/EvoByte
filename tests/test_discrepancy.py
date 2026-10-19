"""Tests for combinatorial discrepancy theory and covering systems formal baseline (P137)."""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from evobyte.discrepancy import (
    arithmetic_progression_discrepancy,
    audit_discrepancy_covering_baseline,
    discrepancy_covering_benchmarks,
    generate_discrepancy_covering_signatures_lean_code,
    hypergraph_discrepancy,
    is_completely_multiplicative,
    is_primitive_set,
    liouville_sequence,
    primitive_set_reciprocal_log_sum,
    roth_ap_bound,
    sign_value,
    spencer_bound,
    subset_discrepancy,
    verify_covering_system,
    verify_discrepancy_covering_baseline_soundness,
)


def test_sign_value() -> None:
    """Test mapping of booleans to {-1, +1} signs."""
    assert sign_value(True) == 1
    assert sign_value(False) == -1


def test_subset_discrepancy() -> None:
    """Test absolute sum of signs on subset indices."""
    signs = [1, -1, 1, 1, -1]
    assert subset_discrepancy([0, 1], signs) == 0  # 1 + (-1) = 0
    assert subset_discrepancy([0, 2, 3], signs) == 3  # 1 + 1 + 1 = 3
    assert subset_discrepancy([1, 4], signs) == 2  # |-1 + -1| = 2
    assert subset_discrepancy([], signs) == 0


def test_hypergraph_discrepancy() -> None:
    """Test combinatorial discrepancy over hypergraph incidence matrix."""
    # 3 sets over 3 elements
    matrix = [
        [1, 1, 0],
        [0, 1, 1],
        [1, 0, 1],
    ]
    signs = [1, -1, 1]
    # Set 1: 1 + (-1) = 0
    # Set 2: -1 + 1 = 0
    # Set 3: 1 + 1 = 2
    # max disc = 2
    assert hypergraph_discrepancy(matrix, signs) == 2
    assert hypergraph_discrepancy([], signs) == 0


def test_arithmetic_progression_discrepancy() -> None:
    """Test AP discrepancy computation for constant and alternating sequences."""
    # All +1 sequence: max discrepancy on length n is n
    ones = [1] * 20
    res = arithmetic_progression_discrepancy(ones)
    assert res["max_discrepancy"] == 20
    assert res["best_step"] == 1
    assert res["best_length"] == 20

    # Alternating sequence: [1, -1, 1, -1, ...]
    alt = [1 if i % 2 == 0 else -1 for i in range(20)]
    res_alt = arithmetic_progression_discrepancy(alt)
    # Step 1 has max disc 1, but step 2: indices 0, 2, 4... all have sign +1!
    # for d = 2: k*2 <= 20 gives 10 terms of +1, discrepancy 10!
    assert res_alt["max_discrepancy"] == 10
    assert res_alt["best_step"] == 2
    assert res_alt["best_length"] == 10


def test_is_completely_multiplicative() -> None:
    """Test detection of completely multiplicative functions."""
    # Constant 1 function is completely multiplicative
    f_one = {i: 1 for i in range(1, 51)}
    assert is_completely_multiplicative(f_one) is True

    # Liouville function is completely multiplicative
    lio = liouville_sequence(50)
    f_lio = {i: lio[i - 1] for i in range(1, 51)}
    assert is_completely_multiplicative(f_lio) is True

    # Bad function where f(1) != 1
    bad_f = {1: -1, 2: 1}
    assert is_completely_multiplicative(bad_f) is False

    # Non-multiplicative function
    non_mult = {1: 1, 2: 1, 3: 1, 6: -1}  # f(2*3) = -1 != 1*1
    assert is_completely_multiplicative(non_mult) is False


def test_liouville_sequence() -> None:
    """Test generation of Liouville sequence lambda(n)."""
    lio = liouville_sequence(10)
    # lambda(1) = 1 (0 prime factors)
    assert lio[0] == 1
    # lambda(2) = -1 (1 prime factor: 2)
    assert lio[1] == -1
    # lambda(3) = -1 (1 prime factor: 3)
    assert lio[2] == -1
    # lambda(4) = 1 (2 prime factors: 2^2)
    assert lio[3] == 1
    # lambda(5) = -1 (1 prime factor: 5)
    assert lio[4] == -1
    # lambda(6) = 1 (2 prime factors: 2*3)
    assert lio[5] == 1
    # lambda(7) = -1 (7)
    assert lio[6] == -1
    # lambda(8) = -1 (2^3 -> 3 factors -> odd -> -1)
    assert lio[7] == -1
    # lambda(9) = 1 (3^2 -> 2 factors -> even -> 1)
    assert lio[8] == 1
    # lambda(10) = 1 (2*5 -> 2 factors -> even -> 1)
    assert lio[9] == 1


def test_spencer_and_roth_bounds() -> None:
    """Test evaluation of Spencer's 6*sqrt(n) and Roth's c*n^(1/4) discrepancy bounds."""
    assert spencer_bound(0) == 0.0
    assert spencer_bound(1) == 6.0
    assert spencer_bound(4) == 12.0
    assert spencer_bound(100) == 60.0

    assert roth_ap_bound(16, c=1.0) == 2.0  # 16^(1/4) = 2
    assert roth_ap_bound(81, c=1.0) == 3.0  # 81^(1/4) = 3


def test_verify_covering_system() -> None:
    """Test covering system verification for Erdős 1950 and incomplete systems."""
    # Classic Erdős 1950: (0, 2), (0, 3), (1, 4), (5, 6), (7, 12)
    erdos_sys = [(0, 2), (0, 3), (1, 4), (5, 6), (7, 12)]
    res = verify_covering_system(erdos_sys)
    assert res["is_covering"] is True
    assert res["distinct_moduli"] is True
    assert res["min_modulus"] == 2
    assert res["max_modulus"] == 12
    assert res["lcm"] == 12
    assert res["reciprocal_sum"] > 1.0

    # Incomplete system: evens only (0, 2)
    inc = [(0, 2)]
    res_inc = verify_covering_system(inc)
    assert res_inc["is_covering"] is False
    assert res_inc["uncovered_witness"] == 1


def test_primitive_sets() -> None:
    """Test detection of primitive sets (antichains in divisibility poset)."""
    # Prime numbers are always primitive
    primes = [2, 3, 5, 7, 11, 13]
    assert is_primitive_set(primes) is True

    # Set with divisibility is not primitive
    not_prim = [2, 3, 4]  # 2 divides 4
    assert is_primitive_set(not_prim) is False

    # Reciprocal log sum
    r_sum = primitive_set_reciprocal_log_sum([2, 3])
    expected = 1.0 / (2 * math.log(2)) + 1.0 / (3 * math.log(3))
    assert math.isclose(r_sum, expected, rel_tol=1e-5)


def test_discrepancy_covering_benchmarks() -> None:
    """Test all deterministic benchmarks pass."""
    benchmarks = discrepancy_covering_benchmarks()
    assert len(benchmarks) == 4
    for b in benchmarks:
        assert b["passed"] is True


def test_generate_discrepancy_covering_signatures_lean_code() -> None:
    """Test generated Lean code contains expected theorems and zero sorry."""
    code = generate_discrepancy_covering_signatures_lean_code()
    assert "namespace EvoByte.DiscrepancyCovering" in code
    assert "theorem sign_val_sq" in code
    assert "theorem edp_multiplicative_step_2" in code
    assert "theorem spencer_bound_sq" in code
    assert "theorem erdos_1950_covering_reciprocal_cleared" in code
    assert "sorry" not in code
    thms = [line for line in code.splitlines() if line.startswith("theorem ") or line.startswith("lemma ")]
    assert len(thms) >= 80


def test_audit_discrepancy_covering_baseline() -> None:
    """Test P137 baseline audit against Lean 4 kernel."""
    audit = audit_discrepancy_covering_baseline(verify_lake=True)
    assert audit["module"] == "DiscrepancyCoveringSignatures"
    assert audit["has_sorry"] is False
    assert audit["lake_passed"] is True
    assert audit["total_theorems"] >= 75
    assert len(audit["benchmarks"]) == 4

    sound, findings = verify_discrepancy_covering_baseline_soundness(audit, min_theorems=75)
    assert sound is True
    assert findings == []


def test_verify_discrepancy_covering_soundness_rejections() -> None:
    """Test that soundness validator properly catches defects."""
    bad_audit = {
        "has_sorry": True,
        "lake_passed": True,
        "total_theorems": 100,
        "benchmarks": [{"passed": True}],
    }
    sound, findings = verify_discrepancy_covering_baseline_soundness(bad_audit)
    assert sound is False
    assert any("SORRY_DETECTED" in f for f in findings)

    bad_lake = {
        "has_sorry": False,
        "lake_passed": False,
        "lake_reasons": ["error"],
        "total_theorems": 100,
        "benchmarks": [{"passed": True}],
    }
    sound2, findings2 = verify_discrepancy_covering_baseline_soundness(bad_lake)
    assert sound2 is False
    assert any("LAKE_BUILD_FAILED" in f for f in findings2)


def test_p137_acceptance_rejects_wrong_phase(tmp_path: Path) -> None:
    """Test that P137 audit rejects invalid configuration phase."""
    import sys

    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root / "benchmarks") not in sys.path:
        sys.path.insert(0, str(repo_root / "benchmarks"))
    from science_matrix import run_p137_discrepancy_covering_baseline_audit

    cfg_p = tmp_path / "bad-p137.json"
    cfg_p.write_text(json.dumps({"phase": "INVALID"}), encoding="utf-8")
    with pytest.raises(ValueError, match="not a P137 configuration"):
        run_p137_discrepancy_covering_baseline_audit(cfg_p, tmp_path / "out.json")


def test_p137_audit_smoke(tmp_path: Path) -> None:
    """Test smoke run of P137 audit on valid config."""
    import sys

    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root / "benchmarks") not in sys.path:
        sys.path.insert(0, str(repo_root / "benchmarks"))
    from science_matrix import run_p137_discrepancy_covering_baseline_audit

    cfg_file = repo_root / "experiments/p137-config.json"
    with open(cfg_file, encoding="utf-8") as f:
        cfg_data = json.load(f)
    cfg_data["verify_lake"] = False
    cfg_data["allow_dirty"] = True

    tmp_cfg = tmp_path / "p137-smoke-config.json"
    tmp_cfg.write_text(json.dumps(cfg_data), encoding="utf-8")
    out_file = tmp_path / "p137-smoke-out.json"

    report = run_p137_discrepancy_covering_baseline_audit(tmp_cfg, out_file)
    assert report["phase"] == "P137"
    assert report["total_theorems"] >= 75
    assert report["has_sorry"] is False
    assert out_file.exists()
