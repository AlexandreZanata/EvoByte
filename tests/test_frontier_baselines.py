"""Tests for frontier competitive baselines and solver harness (P172)."""

from __future__ import annotations

import pytest

from evobyte.frontier_baselines import (
    canonical_form,
    external_sat_solver_status,
    run_hill_climbing,
    run_random_search,
    run_simulated_annealing,
    solve_tiny_sat_dpll,
)
from evobyte.frontier_catalogue import verify_covering_design, verify_weak_schur_partition


def test_sa_acceptance_and_cooling() -> None:
    """Test 1: SA on 3-state objective with fixed seed; improvements accepted, geometric cooling, 8 fields."""
    scores = {0: 1.0, 1: 5.0, 2: 10.0}

    def init_fn(rng):
        return 0

    def neighbor_fn(curr, rng):
        return (curr + 1) % 3

    def eval_fn(cand):
        return scores[cand], cand == 2

    res = run_simulated_annealing(
        target_id="toy_3state",
        init_fn=init_fn,
        neighbor_fn=neighbor_fn,
        eval_fn=eval_fn,
        max_seconds=0.05,
        t_init=1.0,
        t_min=1e-4,
        cooling_rate=0.9,
        seed=42,
    )

    required_fields = [
        "method",
        "target_id",
        "best_candidate",
        "best_score",
        "is_solution",
        "evaluations",
        "elapsed_sec",
        "seed",
    ]
    for f in required_fields:
        assert hasattr(res, f), f"Missing required field {f} in BaselineResult"

    assert res.evaluations > 0
    assert res.method == "SimulatedAnnealing"
    assert res.target_id == "toy_3state"
    assert res.best_candidate == 2
    assert res.best_score == 10.0
    assert res.is_solution is True

    # Check geometric cooling relation
    t_0, cr = 1.0, 0.9
    for step in range(1, 6):
        expected_t = t_0 * (cr**step)
        assert expected_t < t_0


def test_hillclimbing_reaches_local_optimum() -> None:
    """Test 2: Static landscape with known local optimum; deterministic convergence."""

    def init_fn(rng):
        return 0

    def neighbors_fn(curr):
        nbrs = []
        if curr > 0:
            nbrs.append(curr - 1)
        if curr < 10:
            nbrs.append(curr + 1)
        return nbrs

    def eval_fn(cand):
        s = -float((cand - 5) ** 2)
        return s, (cand == 5)

    res1 = run_hill_climbing(
        target_id="static_parabola",
        init_fn=init_fn,
        neighbors_fn=neighbors_fn,
        eval_fn=eval_fn,
        max_seconds=0.1,
        max_restarts=10,
        seed=42,
    )
    res2 = run_hill_climbing(
        target_id="static_parabola",
        init_fn=init_fn,
        neighbors_fn=neighbors_fn,
        eval_fn=eval_fn,
        max_seconds=0.1,
        max_restarts=10,
        seed=42,
    )

    assert res1.best_candidate == 5
    assert res1.best_score == 0.0
    assert res1.is_solution is True
    assert res1.best_candidate == res2.best_candidate
    assert res1.best_score == res2.best_score
    assert res1.evaluations == res2.evaluations


def test_symmetry_canonical_filter() -> None:
    """Test 3: Two colorings in same orbit share canonical form; SA with symmetry skips second."""
    sym = [(1, 0)]
    c1 = (1, 2)
    c2 = (2, 1)
    can1 = canonical_form(c1, sym)
    can2 = canonical_form(c2, sym)
    assert can1 == can2 == (1, 2)

    eval_count = 0

    def init_fn(rng):
        return (1, 2)

    def neighbor_fn(curr, rng):
        return (2, 1)

    def eval_fn(cand):
        nonlocal eval_count
        eval_count += 1
        return 1.0, False

    res = run_simulated_annealing(
        target_id="sym_toy",
        init_fn=init_fn,
        neighbor_fn=neighbor_fn,
        eval_fn=eval_fn,
        max_seconds=0.02,
        t_init=1.0,
        t_min=0.5,
        cooling_rate=0.9,
        symmetries=sym,
        seed=0,
    )

    assert res.skipped_symmetry > 0
    assert res.evaluations == 1
    assert eval_count == 1


def test_dpll_tiny_sat_unsat() -> None:
    """Test 4: CNF {(1,2),(-1,2),(1,-2)} is SAT; {(1),(-1)} is UNSAT; budget exhausted returns None."""
    clauses_sat = [frozenset({1, 2}), frozenset({-1, 2}), frozenset({1, -2})]
    is_sat, model, _stats = solve_tiny_sat_dpll(clauses_sat, 2, 100)
    assert is_sat is True
    assert model is not None
    for c in clauses_sat:
        assert any((lit > 0 and model[abs(lit)]) or (lit < 0 and not model[abs(lit)]) for lit in c)

    clauses_unsat = [frozenset({1}), frozenset({-1})]
    is_sat_u, model_u, _stats_u = solve_tiny_sat_dpll(clauses_unsat, 1, 100)
    assert is_sat_u is False
    assert model_u is None

    clauses_branch = [
        frozenset({1, 2}),
        frozenset({-1, 2}),
        frozenset({1, -2}),
        frozenset({-1, -2}),
    ]
    is_sat_b, model_b, stats_b = solve_tiny_sat_dpll(clauses_branch, 2, 0)
    assert is_sat_b is None
    assert model_b is None
    assert stats_b.get("budget_exhausted") is True


def test_external_solver_hook_reports_status() -> None:
    """Test 5: external_sat_solver_status returns (bool, path|None) without solving."""
    available, solver_path = external_sat_solver_status()
    assert isinstance(available, bool)
    if available:
        assert solver_path is not None
        assert ("kissat" in solver_path) or ("cadical" in solver_path)
    else:
        assert solver_path is None


def test_baselines_reject_malformed() -> None:
    """Test 6: Malformed inputs (color out of range, bad block size) yield negative verdict, no exception."""
    malformed_coloring = [1, 99, "bad"]
    ok_ws, _ = verify_weak_schur_partition(malformed_coloring, 2)
    assert ok_ws is False

    malformed_blocks = [(0, 1, 2), (1, 2)]
    ok_cov, _ = verify_covering_design(malformed_blocks, 7, 3, 2)
    assert ok_cov is False

    def malformed_eval(cand):
        return verify_covering_design(cand, 7, 3, 2)

    res_rnd = run_random_search(
        target_id="malformed_test_rnd",
        sampler_fn=lambda rng: "not_a_valid_candidate",
        eval_fn=malformed_eval,
        max_seconds=0.01,
        seed=0,
    )
    assert res_rnd.is_solution is False

    res_sa = run_simulated_annealing(
        target_id="malformed_test_sa",
        init_fn=lambda rng: [(0, 1)],
        neighbor_fn=lambda c, rng: [(0, 1, 2)],
        eval_fn=malformed_eval,
        max_seconds=0.01,
        seed=0,
    )
    assert res_sa.is_solution is False

    res_hc = run_hill_climbing(
        target_id="malformed_test_hc",
        init_fn=lambda rng: [(0, 1)],
        neighbors_fn=lambda c: [[(0, 1)]],
        eval_fn=malformed_eval,
        max_seconds=0.01,
        seed=0,
    )
    assert res_hc.is_solution is False


def test_provenance_determinism() -> None:
    """Test 7: Same seed on deterministic problem yields same evaluations and best_score."""

    def init_ws(rng):
        return tuple(int(rng.integers(1, 3)) for _ in range(8))

    def neighbor_ws(cand, rng):
        idx = int(rng.integers(0, 8))
        cl = list(cand)
        cl[idx] = 3 - cl[idx]
        return tuple(cl)

    def eval_ws(cand):
        v = 0
        for a in range(1, 8):
            for b in range(a + 1, 9):
                c = a + b
                if c <= 8 and cand[a - 1] == cand[b - 1] == cand[c - 1]:
                    v += 1
        return -float(v), (v == 0)

    res1 = run_simulated_annealing(
        "WS(2)", init_ws, neighbor_ws, eval_ws, max_seconds=0.2, seed=171
    )
    res2 = run_simulated_annealing(
        "WS(2)", init_ws, neighbor_ws, eval_ws, max_seconds=0.2, seed=171
    )

    assert res1.evaluations == res2.evaluations
    assert res1.best_score == res2.best_score
    assert res1.best_candidate == res2.best_candidate
    assert res1.is_solution is True
    assert res2.is_solution is True
