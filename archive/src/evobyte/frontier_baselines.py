"""Honest competitive baselines for frontier combinatorial search (P172)."""

from __future__ import annotations

from dataclasses import dataclass
import math
import shutil
import time
from typing import Any, Callable

import numpy as np


@dataclass(frozen=True)
class BaselineResult:
    method: str  # "RandomSearch" | "SimulatedAnnealing" | "HillClimbing"
    target_id: str
    best_candidate: Any
    best_score: float  # maior = melhor
    is_solution: bool
    evaluations: int  # chamadas REAIS ao avaliador, nunca contador artificial
    elapsed_sec: float  # time.perf_counter()
    seed: int
    skipped_symmetry: int = 0


def _evaluate_candidate(eval_fn: Callable[[Any], Any], candidate: Any) -> tuple[float, bool]:
    """Safely evaluates a candidate without raising exceptions on malformed inputs."""
    try:
        res = eval_fn(candidate)
        if isinstance(res, tuple):
            if len(res) >= 2:
                # Case 1: (score: float, is_sol: bool)
                if isinstance(res[1], bool) and not isinstance(res[0], bool):
                    return float(res[0]), bool(res[1])
                # Case 2: (is_sol: bool, msg: str) as returned by verifiers
                elif isinstance(res[0], bool):
                    is_sol = bool(res[0])
                    if isinstance(res[1], (int, float)) and not isinstance(res[1], bool):
                        score = float(res[1])
                    else:
                        score = 1.0 if is_sol else 0.0
                    return score, is_sol
                else:
                    return float(res[0]), bool(res[1])
            elif len(res) == 1:
                return float(res[0]), bool(res[0] > 0)
        elif isinstance(res, bool):
            return (1.0 if res else 0.0), bool(res)
        elif isinstance(res, (int, float, np.number)):
            return float(res), False
        elif hasattr(res, "score") and hasattr(res, "is_solution"):
            return float(res.score), bool(res.is_solution)
        return float(res), False
    except Exception:
        return -float("inf"), False


def canonical_form(candidate: tuple, symmetries: list[tuple] | None = None) -> tuple:
    """Menor tupla na órbita do candidato sob o grupo de permutações dado."""
    if not isinstance(candidate, tuple):
        try:
            candidate = tuple(candidate)
        except Exception:
            return candidate
    if not symmetries:
        return candidate
    orbit = [candidate]
    n = len(candidate)
    for sym in symmetries:
        try:
            if len(sym) == n:
                permuted = tuple(candidate[sym[i]] for i in range(n))
                orbit.append(permuted)
        except Exception:
            continue
    return min(orbit)


def run_random_search(
    target_id: str,
    sampler_fn: Callable[[np.random.Generator], Any],
    eval_fn: Callable[[Any], Any],
    max_seconds: float,
    seed: int = 0,
) -> BaselineResult:
    """Pure Random Search baseline."""
    rng = np.random.default_rng(seed)
    t0 = time.perf_counter()

    evaluations = 0
    first_cand = sampler_fn(rng)
    best_score, best_is_sol = _evaluate_candidate(eval_fn, first_cand)
    best_candidate = first_cand
    evaluations += 1

    while (time.perf_counter() - t0 < max_seconds) and not best_is_sol:
        cand = sampler_fn(rng)
        score, is_sol = _evaluate_candidate(eval_fn, cand)
        evaluations += 1
        if score > best_score:
            best_score = score
            best_candidate = cand
            best_is_sol = is_sol
            if best_is_sol:
                break

    elapsed = time.perf_counter() - t0
    return BaselineResult(
        method="RandomSearch",
        target_id=target_id,
        best_candidate=best_candidate,
        best_score=best_score,
        is_solution=best_is_sol,
        evaluations=evaluations,
        elapsed_sec=elapsed,
        seed=seed,
    )


def run_simulated_annealing(
    target_id: str,
    init_fn: Callable[[np.random.Generator], Any],
    neighbor_fn: Callable[[Any, np.random.Generator], Any],
    eval_fn: Callable[[Any], Any],
    max_seconds: float,
    t_init: float = 1.0,
    t_min: float = 1e-4,
    cooling_rate: float = 0.9995,
    symmetries: list[tuple] | None = None,
    seed: int = 0,
) -> BaselineResult:
    """Simulated Annealing baseline with optional symmetry filtering."""
    rng = np.random.default_rng(seed)
    t0 = time.perf_counter()

    seen_canonical: set[tuple] = set()
    skipped_symmetry = 0
    evaluations = 0

    current_candidate = init_fn(rng)
    if symmetries:
        c_can = canonical_form(current_candidate, symmetries)
        seen_canonical.add(c_can)

    current_score, current_is_sol = _evaluate_candidate(eval_fn, current_candidate)
    evaluations += 1

    best_candidate = current_candidate
    best_score = current_score
    best_is_sol = current_is_sol

    temp = float(t_init)
    while (time.perf_counter() - t0 < max_seconds) and (temp > t_min) and not best_is_sol:
        try:
            neighbor = neighbor_fn(current_candidate, rng)
        except Exception:
            break

        if symmetries:
            n_can = canonical_form(neighbor, symmetries)
            if n_can in seen_canonical:
                skipped_symmetry += 1
                temp *= cooling_rate
                continue
            seen_canonical.add(n_can)

        nbr_score, nbr_is_sol = _evaluate_candidate(eval_fn, neighbor)
        evaluations += 1

        delta = nbr_score - current_score
        accept = False
        if delta >= 0.0:
            accept = True
        else:
            prob = math.exp(delta / max(temp, 1e-12))
            if rng.random() < prob:
                accept = True

        if accept:
            current_candidate = neighbor
            current_score = nbr_score
            current_is_sol = nbr_is_sol
            if current_score > best_score:
                best_score = current_score
                best_candidate = current_candidate
                best_is_sol = current_is_sol
                if best_is_sol:
                    break

        temp *= cooling_rate

    elapsed = time.perf_counter() - t0
    return BaselineResult(
        method="SimulatedAnnealing",
        target_id=target_id,
        best_candidate=best_candidate,
        best_score=best_score,
        is_solution=best_is_sol,
        evaluations=evaluations,
        elapsed_sec=elapsed,
        seed=seed,
        skipped_symmetry=skipped_symmetry,
    )


def run_hill_climbing(
    target_id: str,
    init_fn: Callable[[np.random.Generator], Any],
    neighbors_fn: Callable[[Any], list[Any]],
    eval_fn: Callable[[Any], Any],
    max_seconds: float,
    max_restarts: int = 50,
    symmetries: list[tuple] | None = None,
    seed: int = 0,
) -> BaselineResult:
    """Deterministic steepest ascent hill-climbing with random restarts."""
    rng = np.random.default_rng(seed)
    t0 = time.perf_counter()

    seen_canonical: set[tuple] = set()
    skipped_symmetry = 0
    evaluations = 0

    best_candidate = None
    best_score = -float("inf")
    best_is_sol = False

    for _restart in range(max_restarts + 1):
        if time.perf_counter() - t0 >= max_seconds or best_is_sol:
            break

        current_candidate = init_fn(rng)
        if symmetries:
            c_can = canonical_form(current_candidate, symmetries)
            seen_canonical.add(c_can)

        c_score, c_is_sol = _evaluate_candidate(eval_fn, current_candidate)
        evaluations += 1

        if c_score > best_score or best_candidate is None:
            best_score = c_score
            best_candidate = current_candidate
            best_is_sol = c_is_sol
            if best_is_sol:
                break

        while time.perf_counter() - t0 < max_seconds:
            try:
                neighbors = neighbors_fn(current_candidate)
            except Exception:
                break
            if not neighbors:
                break

            best_neighbor = None
            best_nbr_score = -float("inf")
            best_nbr_is_sol = False

            for nbr in neighbors:
                if symmetries:
                    n_can = canonical_form(nbr, symmetries)
                    if n_can in seen_canonical:
                        skipped_symmetry += 1
                        continue
                    seen_canonical.add(n_can)

                score, is_sol = _evaluate_candidate(eval_fn, nbr)
                evaluations += 1

                if score > best_nbr_score:
                    best_nbr_score = score
                    best_neighbor = nbr
                    best_nbr_is_sol = is_sol

            if best_neighbor is not None and best_nbr_score > c_score:
                current_candidate = best_neighbor
                c_score = best_nbr_score
                c_is_sol = best_nbr_is_sol
                if c_score > best_score:
                    best_score = c_score
                    best_candidate = current_candidate
                    best_is_sol = c_is_sol
                    if best_is_sol:
                        break
            else:
                break

    elapsed = time.perf_counter() - t0
    return BaselineResult(
        method="HillClimbing",
        target_id=target_id,
        best_candidate=best_candidate,
        best_score=best_score,
        is_solution=best_is_sol,
        evaluations=evaluations,
        elapsed_sec=elapsed,
        seed=seed,
        skipped_symmetry=skipped_symmetry,
    )


def solve_tiny_sat_dpll(
    clauses: list[frozenset[int]], n_vars: int, max_decisions: int
) -> tuple[bool | None, dict | None, dict]:
    """DPLL puro (unit propagation + literal puro + ordem fixa). Retorna
    (True, modelo, stats) | (False, None, stats) | (None, None, stats=orçamento esgotado).
    None significa 'não sei', nunca um palpite."""
    stats = {
        "decisions": 0,
        "unit_propagations": 0,
        "pure_literals": 0,
        "budget_exhausted": False,
    }

    def simplify(
        cls: list[frozenset[int]], assignment: dict[int, bool]
    ) -> tuple[str, list[frozenset[int]]]:
        new_cls = []
        for c in cls:
            sat = False
            unresolved = []
            for lit in c:
                var = abs(lit)
                if var in assignment:
                    val = assignment[var]
                    if (lit > 0 and val) or (lit < 0 and not val):
                        sat = True
                        break
                else:
                    unresolved.append(lit)
            if sat:
                continue
            if not unresolved:
                return "UNSAT", []
            new_cls.append(frozenset(unresolved))
        if not new_cls:
            return "SAT", []
        return "UNDECIDED", new_cls

    def dpll(
        cls: list[frozenset[int]], assignment: dict[int, bool]
    ) -> tuple[bool | None, dict[int, bool] | None]:
        cur_cls = cls
        while True:
            status, cur_cls = simplify(cur_cls, assignment)
            if status == "SAT":
                full_model = {v: assignment.get(v, True) for v in range(1, n_vars + 1)}
                return True, full_model
            if status == "UNSAT":
                return False, None

            unit_lit = None
            for c in cur_cls:
                if len(c) == 1:
                    unit_lit = next(iter(c))
                    break
            if unit_lit is not None:
                stats["unit_propagations"] += 1
                var = abs(unit_lit)
                assignment[var] = unit_lit > 0
                continue

            all_lits: set[int] = set()
            for c in cur_cls:
                all_lits.update(c)
            pure_found = False
            for lit in sorted(all_lits, key=abs):
                if -lit not in all_lits:
                    var = abs(lit)
                    if var not in assignment:
                        stats["pure_literals"] += 1
                        assignment[var] = lit > 0
                        pure_found = True
                        break
            if pure_found:
                continue
            break

        if stats["decisions"] >= max_decisions:
            stats["budget_exhausted"] = True
            return None, None

        chosen_var = None
        for v in range(1, n_vars + 1):
            if v not in assignment:
                chosen_var = v
                break
        if chosen_var is None:
            full_model = {v: assignment.get(v, True) for v in range(1, n_vars + 1)}
            return True, full_model

        stats["decisions"] += 1

        assign_true = dict(assignment)
        assign_true[chosen_var] = True
        sat, model = dpll(cur_cls, assign_true)
        if sat is True:
            return True, model
        if sat is None:
            return None, None

        assign_false = dict(assignment)
        assign_false[chosen_var] = False
        sat, model = dpll(cur_cls, assign_false)
        if sat is True:
            return True, model
        if sat is None:
            return None, None

        return False, None

    if not clauses:
        return True, {v: True for v in range(1, n_vars + 1)}, stats
    for c in clauses:
        if len(c) == 0:
            return False, None, stats

    res, model = dpll(clauses, {})
    return res, model, stats


def external_sat_solver_status() -> tuple[bool, str | None]:
    """Detecta `kissat`/`cadical` no PATH. Nunca executa solving aqui."""
    for binary in ["kissat", "cadical"]:
        path = shutil.which(binary)
        if path:
            return True, path
    return False, None
