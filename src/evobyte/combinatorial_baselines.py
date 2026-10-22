"""Honest combinatorial baselines for extremal search (P164).

Provides pure, fully-implemented baselines for discrete optimization:
- RandomSearch
- SimulatedAnnealing
- TabuSearch

All algorithms operate under strict wall-clock time budgets and return identical
result dictionaries with full provenance.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Any, Callable

import numpy as np


@dataclass
class BaselineResult:
    method: str
    target_id: str
    best_candidate: Any
    best_score: float
    is_solution: bool
    evaluations: int
    elapsed_sec: float
    seed: int


def run_random_search(
    target_id: str,
    sampler_fn: Callable[[np.random.Generator], Any],
    eval_fn: Callable[[Any], tuple[float, bool]],
    max_seconds: float,
    seed: int = 0,
) -> BaselineResult:
    """Evaluate randomly generated candidates until wall-clock deadline."""
    rng = np.random.default_rng(seed)
    start_time = time.perf_counter()
    evals = 0
    best_score = float("-inf")
    best_cand = None
    is_solved = False

    while (time.perf_counter() - start_time) < max_seconds:
        cand = sampler_fn(rng)
        evals += 1
        score, solved = eval_fn(cand)
        if score > best_score:
            best_score = score
            best_cand = cand
            if solved:
                is_solved = True
                break

    elapsed = time.perf_counter() - start_time
    return BaselineResult(
        method="RandomSearch",
        target_id=target_id,
        best_candidate=best_cand,
        best_score=best_score,
        is_solution=is_solved,
        evaluations=evals,
        elapsed_sec=elapsed,
        seed=seed,
    )


def run_simulated_annealing(
    target_id: str,
    init_fn: Callable[[np.random.Generator], Any],
    neighbor_fn: Callable[[Any, np.random.Generator], Any],
    eval_fn: Callable[[Any], tuple[float, bool]],
    max_seconds: float,
    t_init: float = 1.0,
    t_min: float = 1e-4,
    cooling_rate: float = 0.9995,
    seed: int = 0,
) -> BaselineResult:
    """Run Simulated Annealing with geometric temperature decay."""
    rng = np.random.default_rng(seed)
    start_time = time.perf_counter()
    evals = 0

    current_cand = init_fn(rng)
    current_score, is_solved = eval_fn(current_cand)
    evals += 1

    best_cand = current_cand
    best_score = current_score
    temp = t_init

    while (time.perf_counter() - start_time) < max_seconds and not is_solved:
        neighbor = neighbor_fn(current_cand, rng)
        n_score, n_solved = eval_fn(neighbor)
        evals += 1

        delta = n_score - current_score
        if delta > 0 or (temp > 1e-12 and rng.random() < math.exp(delta / max(temp, 1e-12))):
            current_cand = neighbor
            current_score = n_score
            if current_score > best_score:
                best_score = current_score
                best_cand = current_cand
                if n_solved:
                    is_solved = True
                    break

        temp = max(temp * cooling_rate, t_min)

    elapsed = time.perf_counter() - start_time
    return BaselineResult(
        method="SimulatedAnnealing",
        target_id=target_id,
        best_candidate=best_cand,
        best_score=best_score,
        is_solution=is_solved,
        evaluations=evals,
        elapsed_sec=elapsed,
        seed=seed,
    )


def run_tabu_search(
    target_id: str,
    init_fn: Callable[[np.random.Generator], Any],
    neighbors_fn: Callable[[Any, np.random.Generator, int], list[tuple[Any, str]]],
    eval_fn: Callable[[Any], tuple[float, bool]],
    max_seconds: float,
    tabu_tenure: int = 20,
    sample_neighbors: int = 15,
    seed: int = 0,
) -> BaselineResult:
    """Run Tabu Search with short-term memory list."""
    rng = np.random.default_rng(seed)
    start_time = time.perf_counter()
    evals = 0

    current_cand = init_fn(rng)
    current_score, is_solved = eval_fn(current_cand)
    evals += 1

    best_cand = current_cand
    best_score = current_score
    tabu_list: list[str] = []

    while (time.perf_counter() - start_time) < max_seconds and not is_solved:
        neighbors = neighbors_fn(current_cand, rng, sample_neighbors)
        if not neighbors:
            break

        best_cand_step = None
        best_score_step = float("-inf")
        best_move_step = None

        for cand, move_repr in neighbors:
            score, solved = eval_fn(cand)
            evals += 1
            # Aspiration criterion: accept move if it beats global best even if tabu
            if (move_repr not in tabu_list) or (score > best_score):
                if score > best_score_step:
                    best_score_step = score
                    best_cand_step = cand
                    best_move_step = move_repr
                    if solved:
                        is_solved = True
                        break

        if best_cand_step is not None:
            current_cand = best_cand_step
            current_score = best_score_step
            if best_move_step:
                tabu_list.append(best_move_step)
                if len(tabu_list) > tabu_tenure:
                    tabu_list.pop(0)

            if current_score > best_score:
                best_score = current_score
                best_cand = current_cand

    elapsed = time.perf_counter() - start_time
    return BaselineResult(
        method="TabuSearch",
        target_id=target_id,
        best_candidate=best_cand,
        best_score=best_score,
        is_solution=is_solved,
        evaluations=evals,
        elapsed_sec=elapsed,
        seed=seed,
    )
