"""Blind rediscovery protocol for literature benchmark targets (P165).

Calibrates search algorithms on known combinatorial milestones:
- vdw_3_3_26: van der Waerden coloring of length 26 with 3 colors (optimum known).
- vdw_2_4_34: van der Waerden coloring of length 34 with 2 colors.
- schur_3_13: sum-free partition of 1..13 into 3 classes.
- spectral_counter_sample: small connected graph refuting naive spectral heuristics.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable

import numpy as np

from evobyte.combinatorial_baselines import (
    BaselineResult,
    run_random_search,
    run_simulated_annealing,
    run_tabu_search,
)
from evobyte.target_catalogue import (
    verify_schur_partition,
    verify_vanderwaerden_coloring,
)


@dataclass
class RediscoveryTrial:
    instance_id: str
    method: str
    seed: int
    success: bool
    time_to_hit_sec: float | None
    total_evals: int
    elapsed_sec: float


def make_vdw_evaluator(
    n: int, r: int, k: int
) -> tuple[
    Callable[[np.random.Generator], np.ndarray],
    Callable[[np.ndarray, np.random.Generator], np.ndarray],
    Callable[[np.ndarray, np.random.Generator, int], list[tuple[np.ndarray, str]]],
    Callable[[np.ndarray], tuple[float, bool]],
]:
    """Return (init_fn, neighbor_fn, neighbors_fn, eval_fn) for VdW coloring."""

    def init_fn(rng: np.random.Generator) -> np.ndarray:
        return rng.integers(1, r + 1, size=n)

    def neighbor_fn(cand: np.ndarray, rng: np.random.Generator) -> np.ndarray:
        out = cand.copy()
        idx = rng.integers(0, n)
        cur = out[idx]
        choices = [c for c in range(1, r + 1) if c != cur]
        out[idx] = rng.choice(choices)
        return out

    def neighbors_fn(
        cand: np.ndarray, rng: np.random.Generator, k_sample: int
    ) -> list[tuple[np.ndarray, str]]:
        res = []
        for _ in range(k_sample):
            idx = rng.integers(0, n)
            cur = cand[idx]
            choices = [c for c in range(1, r + 1) if c != cur]
            new_c = int(rng.choice(choices))
            out = cand.copy()
            out[idx] = new_c
            res.append((out, f"{idx}:{new_c}"))
        return res

    def eval_fn(cand: np.ndarray) -> tuple[float, bool]:
        # Count violations (fewer violations = higher score)
        valid, _ = verify_vanderwaerden_coloring(cand, r=r, k=k)
        if valid:
            return 0.0, True

        violations = 0
        max_d = (n - 1) // (k - 1)
        for d in range(1, max_d + 1):
            for a in range(n - (k - 1) * d):
                idxs = [a + i * d for i in range(k)]
                if all(cand[i] == cand[idxs[0]] for i in idxs):
                    violations += 1
        return -float(violations), False

    return init_fn, neighbor_fn, neighbors_fn, eval_fn


def run_single_calibration_trial(
    instance_id: str,
    method: str,
    max_seconds: float,
    seed: int,
) -> RediscoveryTrial:
    """Execute one calibration trial with exact wall-clock budget."""
    if instance_id == "vdw_3_3_26":
        init_fn, neighbor_fn, neighbors_fn, eval_fn = make_vdw_evaluator(n=26, r=3, k=3)
    elif instance_id == "vdw_2_4_34":
        init_fn, neighbor_fn, neighbors_fn, eval_fn = make_vdw_evaluator(n=34, r=2, k=4)
    else:
        raise ValueError(f"unsupported calibration instance {instance_id}")

    if method == "RandomSearch":
        res = run_random_search(instance_id, init_fn, eval_fn, max_seconds, seed)
    elif method == "SimulatedAnnealing":
        res = run_simulated_annealing(
            instance_id, init_fn, neighbor_fn, eval_fn, max_seconds, seed=seed
        )
    elif method == "TabuSearch":
        res = run_tabu_search(instance_id, init_fn, neighbors_fn, eval_fn, max_seconds, seed=seed)
    else:
        raise ValueError(f"unknown method {method}")

    return RediscoveryTrial(
        instance_id=instance_id,
        method=method,
        seed=seed,
        success=res.is_solution,
        time_to_hit_sec=res.elapsed_sec if res.is_solution else None,
        total_evals=res.evaluations,
        elapsed_sec=res.elapsed_sec,
    )
