"""Evolution of bytecode priority programs for constructive search (P174)."""

from __future__ import annotations

import time
from typing import Any, Callable

import numpy as np

from evobyte.bytecode import N_INSTR, N_REGS, encode_instr, is_valid
from evobyte.evolution import STRUCTURED_OP_RATIOS, STRUCTURED_OPS


def _sample_valid_program(rng: np.random.Generator) -> np.ndarray:
    """Rejection-sample one S0-valid v1 program (random, nothing hardcoded)."""
    for _ in range(200):
        prog = np.zeros((N_INSTR,), dtype=np.uint32)
        n_active = int(rng.integers(2, N_INSTR + 1))
        for i in range(n_active):
            if rng.random() < 0.35:
                continue
            op = int(rng.choice(STRUCTURED_OPS, p=STRUCTURED_OP_RATIOS))
            if op == 0x00:
                continue
            dst = int(rng.integers(0, N_REGS))
            a = int(rng.integers(0, N_REGS))
            if op in (0x0F, 0x10, 0x11):
                b = int(rng.integers(0, 16))
            else:
                b = int(rng.integers(0, N_REGS))
            prog[i] = encode_instr(op, dst, a, b)
        if not any((int(w) >> 8) & 0xFF == 7 and (int(w) & 0xFF) != 0 for w in prog):
            op = int(rng.choice([0x01, 0x02, 0x03, 0x0F]))
            b = int(rng.integers(0, 16)) if op == 0x0F else int(rng.integers(0, N_REGS))
            prog[n_active - 1] = encode_instr(op, 7, int(rng.integers(0, N_REGS)), b)
        if is_valid(prog):
            return prog
    # Fallback: deterministic golden ADD (still valid; sampler keeps determinism).
    from evobyte.bytecode import nop_program

    prog = nop_program()
    prog[0] = encode_instr(0x01, dst=7, a=0, b=1)
    return prog


def mutate_priority_program(prog: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Point mutation on one instruction slot; keeps parent if result invalid."""
    out = np.asarray(prog, dtype=np.uint32).copy()
    idx = int(rng.integers(0, N_INSTR))
    op = int(rng.choice(STRUCTURED_OPS, p=STRUCTURED_OP_RATIOS))
    if op == 0x00:
        return out
    dst = int(rng.integers(0, N_REGS))
    a = int(rng.integers(0, N_REGS))
    if op in (0x0F, 0x10, 0x11):
        b = int(rng.integers(0, 16))
    else:
        b = int(rng.integers(0, N_REGS))
    try:
        out[idx] = encode_instr(op, dst, a, b)
    except ValueError:
        return np.asarray(prog, dtype=np.uint32).copy()
    if is_valid(out):
        return out
    return np.asarray(prog, dtype=np.uint32).copy()


def crossover_priority_programs(
    p1: np.ndarray, p2: np.ndarray, rng: np.random.Generator
) -> np.ndarray:
    """Single-point crossover on the uint32 vector; keeps p1 if child invalid."""
    a = np.asarray(p1, dtype=np.uint32).copy()
    b = np.asarray(p2, dtype=np.uint32).copy()
    pt = int(rng.integers(1, N_INSTR))
    child = np.concatenate([a[:pt], b[pt:]]).astype(np.uint32)
    if is_valid(child):
        return child
    return a


def _score_objective(objective_fn: Callable[..., Any], prog: np.ndarray) -> float:
    """Call objective_fn once; accept float or (score, valid) tuple."""
    res = objective_fn(prog)
    if isinstance(res, (tuple, list)) and len(res) >= 1:
        try:
            return float(res[0])
        except Exception:
            return float("-inf")
    try:
        return float(res)  # type: ignore[arg-type]
    except Exception:
        return float("-inf")


def evolve_priorities(
    objective_fn: Callable[[np.ndarray], Any],
    budget_evals: int,
    pop_size: int = 32,
    seed: int = 0,
    max_seconds: float | None = None,
    elite_k: int = 4,
    p_mut: float = 0.3,
    tournament_size: int = 3,
) -> tuple[np.ndarray, float, int, float]:
    """Evolve v1 priority programs against objective_fn.

    Population of S0-valid v1 programs; fitness = objective_fn(program).
    Counts EVERY objective call (no cache between seeds). Deterministic
    given seed (rng only; wall-clock only stops early). No LLM, no network.
    Returns (best_program, best_score, n_evals, elapsed_sec).
    """
    t0 = time.perf_counter()
    rng = np.random.default_rng(int(seed))
    budget = max(1, int(budget_evals))
    pop_n = max(2, int(pop_size))
    elite = max(1, min(int(elite_k), pop_n))

    population = [_sample_valid_program(rng) for _ in range(pop_n)]
    scores = np.full((pop_n,), float("-inf"), dtype=np.float64)
    n_evals = 0
    for i, prog in enumerate(population):
        if n_evals >= budget:
            break
        if max_seconds is not None and (time.perf_counter() - t0) >= max_seconds:
            break
        scores[i] = _score_objective(objective_fn, prog)
        n_evals += 1

    order = np.argsort(-scores, kind="stable")
    population = [population[i] for i in order]
    scores = scores[order]
    best_prog = population[0].copy()
    best_score = float(scores[0])

    while n_evals < budget:
        if max_seconds is not None and (time.perf_counter() - t0) >= max_seconds:
            break
        offspring: list[np.ndarray] = []
        while len(offspring) < pop_n - elite:
            if n_evals + len(offspring) >= budget:
                break
            cand_idx = rng.choice(pop_n, size=int(tournament_size), replace=False)
            parent1 = population[int(cand_idx[np.argmax(scores[cand_idx])])]
            cand_idx2 = rng.choice(pop_n, size=int(tournament_size), replace=False)
            parent2 = population[int(cand_idx2[np.argmax(scores[cand_idx2])])]
            child = crossover_priority_programs(parent1, parent2, rng)
            if rng.random() < float(p_mut):
                child = mutate_priority_program(child, rng)
            offspring.append(child)
        new_scores = np.full((len(offspring),), float("-inf"), dtype=np.float64)
        for j, child in enumerate(offspring):
            if n_evals >= budget:
                break
            if max_seconds is not None and (time.perf_counter() - t0) >= max_seconds:
                break
            new_scores[j] = _score_objective(objective_fn, child)
            n_evals += 1
        # Elitist merge: keep top pop_n across parents + evaluated offspring.
        merged_progs = population + offspring[: len(new_scores)]
        merged_scores = np.concatenate([scores, new_scores[: len(offspring)]])
        # Offspring beyond time/budget keep -inf and sink to bottom.
        order = np.argsort(-merged_scores, kind="stable")[:pop_n]
        population = [merged_progs[i] for i in order]
        scores = merged_scores[order]
        if float(scores[0]) > best_score:
            best_score = float(scores[0])
            best_prog = population[0].copy()
        # If no offspring evaluated (budget/time exhausted), stop.
        if len(offspring) == 0 or np.all(new_scores == float("-inf")) and len(offspring) > 0 and n_evals >= budget:
            break
        if max_seconds is not None and (time.perf_counter() - t0) >= max_seconds:
            break

    elapsed = time.perf_counter() - t0
    return best_prog.copy(), float(best_score), int(n_evals), float(elapsed)
