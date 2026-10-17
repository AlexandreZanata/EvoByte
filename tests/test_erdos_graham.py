"""Unit and integration tests for P109 Erdős–Graham unit fraction formalization."""

from __future__ import annotations

import pytest

from evobyte.algebraic import (
    compute_denominators_lcm,
    find_erdos_graham_unit_fractions,
    verify_unit_fraction_sum,
)
from evobyte.formal_bridge import (
    audit_erdos_graham_unit_fractions,
    generate_erdos_graham_theorems_lean_code,
    verify_erdos_graham_soundness,
)


def test_find_erdos_graham_unit_fractions():
    sols = find_erdos_graham_unit_fractions(max_len=5, limit=50)
    assert len(sols) >= 50
    for s in sols:
        assert len(s) >= 3
        assert len(s) == len(set(s))
        assert all(d >= 2 for d in s)
        assert verify_unit_fraction_sum(s) is True


def test_verify_unit_fraction_sum():
    # True solutions
    assert verify_unit_fraction_sum([2, 3, 6]) is True
    assert verify_unit_fraction_sum([2, 4, 6, 12]) is True
    assert verify_unit_fraction_sum([2, 3, 7, 42]) is True

    # Duplicate denominators
    assert verify_unit_fraction_sum([2, 2]) is False

    # Sum != 1
    assert verify_unit_fraction_sum([2, 3, 5]) is False
    assert verify_unit_fraction_sum([]) is False


def test_compute_denominators_lcm():
    assert compute_denominators_lcm([2, 3, 6]) == 6
    assert compute_denominators_lcm([2, 4, 6, 12]) == 12
    assert compute_denominators_lcm([2, 3, 7, 42]) == 42


def test_generate_erdos_graham_theorems_lean_code():
    code = generate_erdos_graham_theorems_lean_code([[2, 3, 6], [2, 4, 6, 12]])
    assert "sorry" not in code
    assert "import Mathlib.Tactic" in code
    assert "theorem unit_fraction_split" in code
    assert "theorem erdos_graham_rat_0_2_3_6" in code
    assert "theorem erdos_graham_lcm_0" in code


def test_audit_erdos_graham_unit_fractions():
    audit_res = audit_erdos_graham_unit_fractions(limit=75, verify_lake=False)
    assert audit_res["solutions_found"] >= 50
    assert audit_res["all_verified"] is True
    assert audit_res["theorem_count"] >= 70
    assert audit_res["has_sorry"] is False

    sound, findings = verify_erdos_graham_soundness(
        audit_res,
        min_solutions=50,
        min_theorems=70,
    )
    assert sound is True
    assert len(findings) == 0
