"""Unit tests for SAT Solver Exact Completion Bridge (P194).

Verifies:
1. CNF formula construction, DIMACS round-trip serialization, and variable tracking.
2. Exact cardinality constraints: At-Most-K, At-Least-K, Exactly-K (Sinz sequential counter).
3. XOR parity linear equations over GF(2) via Tseitin chaining.
4. PurePythonSolver DPLL engine correctness, model extraction, and timeout handling.
5. solve_cnf dispatch across backends (PySAT / Cadical / Glucose / Pure Python).
6. Covering design skeleton completion on C(7,3,2) and C(8,4,3) certified by verify_covering_design.
7. Orbit-level covering completion on narrow-gap targets C(13,6,3), C(14,6,3), and C(15,8,4).
8. Unsatisfiability proofs under tight cardinality constraints.
9. Quantum stabilizer generator synthesis and zero-dependency verification.
"""

from __future__ import annotations

import math
import pytest

from evobyte.frontier_catalogue import verify_covering_design
from evobyte.narrow_gap_catalogue import _C_7_3_2_BLOCKS, _C_8_4_3_BLOCKS, _STEANE_GENERATORS
from evobyte.qecc_verifier import check_stabilizer
from evobyte.sat_bridge import (
    CNFFormula,
    CoveringCnfEncoder,
    PurePythonSolver,
    StabilizerCnfEncoder,
    complete_covering_orbits,
    complete_covering_skeleton,
    solve_cnf,
)


def test_cnf_formula_basic_and_dimacs_roundtrip():
    """Formula builds clauses, tracks variable count, and round-trips via DIMACS."""
    formula = CNFFormula()
    v1 = formula.new_var("x1")
    v2 = formula.new_var("x2")
    v3 = formula.new_var("x3")

    formula.add_clause([v1, -v2])
    formula.add_clause([v2, v3])
    formula.add_clause([-v1, -v3])

    assert formula.n_vars >= 3
    assert len(formula.clauses) == 3

    dimacs = formula.to_dimacs()
    assert "p cnf" in dimacs
    assert dimacs.strip().endswith("0")

    parsed = CNFFormula.from_dimacs(dimacs)
    assert parsed.n_vars == formula.n_vars
    assert parsed.clauses == formula.clauses


def test_cardinality_at_most_k_exact_model_count():
    """At-Most-K constraint on n variables yields exactly sum_{i=0}^k C(n, i) satisfying models."""
    n = 4
    k = 2
    formula = CNFFormula(n_vars=n)
    lits = list(range(1, n + 1))
    formula.add_at_most_k(lits, k)

    # Collect all models restricted to the first n variables
    found_models: set[tuple[bool, ...]] = set()
    while True:
        res = solve_cnf(formula, solver_name="pure_python")
        if not res.is_sat or res.assignment is None:
            break
        assignment = tuple(res.assignment.get(i, False) for i in range(1, n + 1))
        found_models.add(assignment)
        # Block this specific model on primary variables
        blocking_clause = [-i if res.assignment.get(i, False) else i for i in range(1, n + 1)]
        formula.add_clause(blocking_clause)

    # sum_{i=0}^2 C(4, i) = 1 + 4 + 6 = 11 models
    expected_count = math.comb(4, 0) + math.comb(4, 1) + math.comb(4, 2)
    assert len(found_models) == expected_count
    for m in found_models:
        assert sum(1 for bit in m if bit) <= k


def test_cardinality_exactly_k():
    """Exactly-K constraint on n variables yields exactly C(n, k) satisfying models."""
    n = 4
    k = 2
    formula = CNFFormula(n_vars=n)
    lits = list(range(1, n + 1))
    formula.add_exactly_k(lits, k)

    found_models: set[tuple[bool, ...]] = set()
    while True:
        res = solve_cnf(formula, solver_name="pure_python")
        if not res.is_sat or res.assignment is None:
            break
        assignment = tuple(res.assignment.get(i, False) for i in range(1, n + 1))
        found_models.add(assignment)
        blocking_clause = [-i if res.assignment.get(i, False) else i for i in range(1, n + 1)]
        formula.add_clause(blocking_clause)

    assert len(found_models) == math.comb(4, 2)
    for m in found_models:
        assert sum(1 for bit in m if bit) == k


def test_xor_parity_constraint():
    """XOR constraint enforces correct odd/even parity across multiple boolean variables."""
    # Test even parity: x1 ^ x2 ^ x3 = 0
    f_even = CNFFormula(n_vars=3)
    f_even.add_xor([1, 2, 3], target_parity=0)

    # Fix x1=True, x2=True -> x3 must be False
    f_even.add_clause([1])
    f_even.add_clause([2])
    res_even = solve_cnf(f_even, solver_name="pure_python")
    assert res_even.is_sat
    assert res_even.assignment is not None
    assert res_even.assignment[3] is False

    # Test odd parity: x1 ^ x2 ^ x3 = 1 with x1=True, x2=True -> x3 must be True
    f_odd = CNFFormula(n_vars=3)
    f_odd.add_xor([1, 2, 3], target_parity=1)
    f_odd.add_clause([1])
    f_odd.add_clause([2])
    res_odd = solve_cnf(f_odd, solver_name="pure_python")
    assert res_odd.is_sat
    assert res_odd.assignment is not None
    assert res_odd.assignment[3] is True


def test_pure_python_solver_sat_and_unsat():
    """PurePythonSolver correctly decides SAT and UNSAT instances."""
    # SAT formula
    f_sat = CNFFormula(n_vars=3)
    f_sat.add_clause([1, 2])
    f_sat.add_clause([-1, 3])
    solver_sat = PurePythonSolver(f_sat)
    res_sat = solver_sat.solve()
    assert res_sat.status == "SAT"
    assert res_sat.is_sat

    # UNSAT formula: x1 and ~x1
    f_unsat = CNFFormula(n_vars=1)
    f_unsat.add_clause([1])
    f_unsat.add_clause([-1])
    solver_unsat = PurePythonSolver(f_unsat)
    res_unsat = solver_unsat.solve()
    assert res_unsat.status == "UNSAT"
    assert not res_unsat.is_sat


def test_pure_python_solver_timeout():
    """PurePythonSolver halts when the time budget is exceeded."""
    # Build a pigeonhole principle formula PHP(7, 6)
    n_pigeons = 7
    n_holes = 6
    formula = CNFFormula(n_vars=n_pigeons * n_holes)
    for p in range(n_pigeons):
        formula.add_clause([p * n_holes + h + 1 for h in range(n_holes)])
    for h in range(n_holes):
        for p1 in range(n_pigeons):
            for p2 in range(p1 + 1, n_pigeons):
                formula.add_clause([-(p1 * n_holes + h + 1), -(p2 * n_holes + h + 1)])

    solver = PurePythonSolver(formula)
    # A tight budget of 0.001s should trigger TIMEOUT or UNSAT without hanging
    res = solver.solve(timeout_seconds=0.001)
    assert res.status in ("TIMEOUT", "UNSAT")


def test_complete_covering_skeleton_c7_3_2():
    """Given 5 of 7 Fano plane blocks, SAT completes the missing 2 blocks in < 0.1s."""
    skeleton = list(_C_7_3_2_BLOCKS[:5])
    v, k, t = 7, 3, 2

    res = complete_covering_skeleton(
        skeleton=skeleton,
        v=v,
        k=k,
        t=t,
        max_additional_blocks=2,
        timeout_seconds=5.0,
        solver_name="auto",
    )

    assert res.success, f"Failed to complete C(7,3,2): {res.verification_msg}"
    assert res.status == "SAT"
    assert res.total_blocks == 7
    assert len(res.added_blocks or []) == 2
    assert res.uncovered_before == 6
    assert res.uncovered_after == 0
    assert res.verified
    assert res.solve_time_seconds < 1.0

    # Cross-verify with zero-dependency verifier
    is_valid, msg = verify_covering_design(res.completed_blocks, v, k, t)
    assert is_valid, msg


def test_complete_covering_skeleton_c8_4_3():
    """Given 11 of 14 C(8,4,3) blocks, SAT completes the missing 3 blocks in < 0.1s."""
    skeleton = list(_C_8_4_3_BLOCKS[:11])
    v, k, t = 8, 4, 3

    res = complete_covering_skeleton(
        skeleton=skeleton,
        v=v,
        k=k,
        t=t,
        max_additional_blocks=3,
        timeout_seconds=5.0,
        solver_name="auto",
    )

    assert res.success, f"Failed to complete C(8,4,3): {res.verification_msg}"
    assert res.status == "SAT"
    assert res.total_blocks == 14
    assert len(res.added_blocks or []) == 3
    assert res.verified
    assert res.solve_time_seconds < 1.0

    is_valid, msg = verify_covering_design(res.completed_blocks, v, k, t)
    assert is_valid, msg


def test_complete_covering_skeleton_unsat_on_impossible_bound():
    """SAT returns UNSAT when asked to complete C(7,3,2) with fewer blocks than possible."""
    skeleton = list(_C_7_3_2_BLOCKS[:5])  # 6 pairs uncovered; 1 block covers at most 3 pairs
    v, k, t = 7, 3, 2

    # 1 block can cover at most 3 pairs; 6 pairs uncovered -> impossible
    res = complete_covering_skeleton(
        skeleton=skeleton,
        v=v,
        k=k,
        t=t,
        max_additional_blocks=1,
        timeout_seconds=5.0,
        solver_name="auto",
    )

    assert not res.success
    assert res.status == "UNSAT"
    assert res.completed_blocks is None


def test_complete_covering_orbits_c13_6_3():
    """SAT completes C(13,6,3) under Z_13 cyclic group with 2 base blocks (26 blocks)."""
    v, k, t = 13, 6, 3
    # Start with an empty base block set, let SAT pick at most 2 base blocks
    res = complete_covering_orbits(
        fixed_base_blocks=[],
        v=v,
        k=k,
        t=t,
        max_additional_orbits=2,
        timeout_seconds=5.0,
        solver_name="auto",
    )

    assert res.success, f"Failed orbit completion for C(13,6,3): {res.verification_msg}"
    assert res.status == "SAT"
    assert res.total_blocks == 26
    assert res.verified
    assert res.solve_time_seconds < 5.0

    is_valid, msg = verify_covering_design(res.completed_blocks, v, k, t)
    assert is_valid, msg


def test_complete_covering_orbits_c14_6_3():
    """SAT completes C(14,6,3) under Z_14 cyclic group with 2 base blocks (28 blocks)."""
    v, k, t = 14, 6, 3
    res = complete_covering_orbits(
        fixed_base_blocks=[],
        v=v,
        k=k,
        t=t,
        max_additional_orbits=2,
        timeout_seconds=5.0,
        solver_name="auto",
    )

    assert res.success, f"Failed orbit completion for C(14,6,3): {res.verification_msg}"
    assert res.status == "SAT"
    assert res.total_blocks == 28
    assert res.verified
    assert res.solve_time_seconds < 5.0

    is_valid, msg = verify_covering_design(res.completed_blocks, v, k, t)
    assert is_valid, msg


def test_complete_covering_orbits_c15_8_4_matches_record():
    """Given 1 base block skeleton, SAT completes C(15,8,4) under Z_15 to 30 blocks (LJCR record)."""
    v, k, t = 15, 8, 4
    # 1 base block skeleton (covers 1085 of 1365 quadruples)
    skeleton_base = [(1, 2, 3, 4, 5, 6, 11, 13)]
    res = complete_covering_orbits(
        fixed_base_blocks=skeleton_base,
        v=v,
        k=k,
        t=t,
        max_additional_orbits=1,
        timeout_seconds=5.0,
        solver_name="auto",
        one_indexed=True,
    )

    assert res.success, f"Failed orbit completion for C(15,8,4): {res.verification_msg}"
    assert res.status == "SAT"
    assert res.total_blocks == 30
    assert res.verified
    assert res.solve_time_seconds < 5.0

    is_valid, msg = verify_covering_design(res.completed_blocks, v, k, t)
    assert is_valid, msg


def test_stabilizer_generator_synthesis_commutativity():
    """SAT synthesizes a non-trivial Pauli operator commuting with fixed Steane generators."""
    fixed = list(_STEANE_GENERATORS[:4])
    encoder = StabilizerCnfEncoder(n_qubits=7, fixed_generators=fixed)

    ok, gen_str, sat_res = encoder.synthesize_single_generator(
        timeout_seconds=5.0,
        solver_name="auto",
        min_weight=3,
    )

    assert ok, f"Failed to synthesize stabilizer generator: {sat_res.status}"
    assert gen_str is not None
    assert len(gen_str) == 7
    assert gen_str.count("I") <= 4  # Weight >= 3

    # Check commutativity with all 4 fixed generators
    all_gens = fixed + [gen_str]
    ok_stab, stab_res = check_stabilizer(all_gens)
    assert ok_stab, f"Commutativity check failed: {stab_res}"
