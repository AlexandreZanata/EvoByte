"""Unit and integration tests for P110 Pillai-Catalan exponential Diophantine formalization."""

from __future__ import annotations

from pathlib import Path

import pytest

from evobyte.algebraic import (
    PillaiSolution,
    compute_baker_effective_bound,
    find_pillai_solutions,
    sieve_pillai_fixed_bases,
    sieve_pillai_modular_obstruction,
    verify_pillai_solution,
)
from evobyte.formal_bridge import (
    audit_pillai_catalan_exponential_diophantine,
    generate_pillai_catalan_theorems_lean_code,
    verify_pillai_catalan_soundness,
)


def test_find_pillai_solutions():
    sols = find_pillai_solutions(max_base=30, max_exp=15, max_c=100, limit=100)
    assert len(sols) >= 80
    for s in sols:
        assert isinstance(s, PillaiSolution)
        assert s.x >= 2
        assert s.y >= 2
        assert s.p >= 2
        assert s.q >= 2
        assert 1 <= s.c <= 100
        assert verify_pillai_solution(s) is True


def test_verify_pillai_solution():
    # True Catalan / Pillai solutions
    assert verify_pillai_solution((3, 2, 2, 3, 1)) is True  # 9 - 8 = 1
    assert verify_pillai_solution((3, 3, 5, 2, 2)) is True  # 27 - 25 = 2
    assert verify_pillai_solution((2, 7, 5, 3, 3)) is True  # 128 - 125 = 3
    assert verify_pillai_solution((2, 5, 3, 3, 5)) is True  # 32 - 27 = 5

    # False solutions
    assert verify_pillai_solution((2, 3, 3, 2, 1)) is False  # 8 - 9 = -1 != 1
    assert verify_pillai_solution((1, 2, 2, 3, 1)) is False  # x < 2
    assert verify_pillai_solution((3, 1, 2, 3, 1)) is False  # p < 2


def test_compute_baker_effective_bound():
    bound_info = compute_baker_effective_bound(2, 3, 5)
    assert bound_info["x"] == 2
    assert bound_info["y"] == 3
    assert bound_info["c"] == 5
    assert bound_info["effective_exponent_bound"] >= 10

    with pytest.raises(ValueError):
        compute_baker_effective_bound(1, 3, 5)


def test_sieve_pillai_modular_obstruction():
    obs = sieve_pillai_modular_obstruction(2, 4, 4)
    assert 5 in obs
    assert 4 in obs or 8 in obs

    obs_c3 = sieve_pillai_modular_obstruction(3, 4, 4)
    assert 5 in obs_c3


def test_sieve_pillai_fixed_bases():
    # 3^p - 2^q = 1 -> (2, 3) since 9 - 8 = 1
    fixed = sieve_pillai_fixed_bases(3, 2, 1)
    assert (2, 3) in fixed

    # 2^p - 3^q = 5 -> (5, 3) since 32 - 27 = 5
    fixed_5 = sieve_pillai_fixed_bases(2, 3, 5)
    assert (5, 3) in fixed_5


def test_generate_pillai_catalan_theorems_lean_code():
    code = generate_pillai_catalan_theorems_lean_code(
        [PillaiSolution(3, 2, 2, 3, 1), PillaiSolution(3, 3, 5, 2, 2)]
    )
    assert "sorry" not in code
    assert "import Mathlib.Tactic" in code
    assert "theorem pillai_pow_pos" in code
    assert "theorem pillai_baker_cutoff_2_3" in code
    assert "theorem pillai_sol_0_1_3_2_2_3" in code
    assert "theorem pillai_nosol_0_2_3_3_2_1" in code


def test_audit_pillai_catalan_soundness(tmp_path: Path):
    audit_res = audit_pillai_catalan_exponential_diophantine(
        generated_path=tmp_path / "TestPillaiTheorems.lean",
        limit=100,
        verify_lake=False,
    )
    assert audit_res["solutions_found"] >= 80
    assert audit_res["all_verified"] is True
    assert audit_res["theorem_count"] >= 120
    assert audit_res["has_sorry"] is False

    sound, findings = verify_pillai_catalan_soundness(
        audit_res,
        min_solutions=80,
        min_theorems=120,
    )
    assert sound is True
    assert len(findings) == 0
