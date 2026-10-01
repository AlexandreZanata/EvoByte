"""Evolution primitives: selection, mutation, crossover, elitism, and closed loop (P03 & P08 scope)."""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch

from evobyte.batching import execute_chunked
from evobyte.bytecode import N_INSTR, N_REGS, OPCODES, decode_human, encode_instr, is_valid

STRUCTURED_OP_RATIOS = np.array(
    [
        0.25,
        0.12,
        0.12,
        0.10,
        0.06,
        0.03,
        0.03,
        0.03,
        0.02,
        0.02,
        0.03,
        0.02,
        0.03,
        0.03,
        0.03,
        0.08,
    ],
    dtype=np.float64,
)
STRUCTURED_OP_RATIOS /= STRUCTURED_OP_RATIOS.sum()
STRUCTURED_OPS = np.array(sorted(OPCODES.keys()), dtype=np.int64)


def sample_pure(rng: np.random.Generator) -> np.ndarray:
    """Uniform random program (raw bytes, usually invalid)."""
    words = rng.integers(0, 2**32, size=(N_INSTR,), dtype=np.int64).astype(np.uint32)
    return words


def sample_structured(rng: np.random.Generator, p_nop: float = 0.35) -> np.ndarray:
    """Opcode-aware sampler: valid registers, NOP padding, output write guaranteed."""
    prog = np.zeros((N_INSTR,), dtype=np.uint32)
    n_active = int(rng.integers(2, N_INSTR + 1))
    for i in range(n_active):
        if rng.random() < p_nop:
            continue
        op = int(rng.choice(STRUCTURED_OPS, p=STRUCTURED_OP_RATIOS))
        if op == 0x00:
            continue
        dst = int(rng.integers(0, N_REGS))
        a = int(rng.integers(0, N_REGS))
        b = int(rng.integers(0, 16)) if op == 0x0F else int(rng.integers(0, N_REGS))
        prog[i] = encode_instr(op, dst, a, b)
    # Guarantee at least one write to r7 so S0 has a chance.
    if not any((int(w) >> 8) & 0xFF == 7 and (int(w) & 0xFF) != 0 for w in prog):
        op = int(rng.choice([0x01, 0x02, 0x03, 0x0F]))
        b = int(rng.integers(0, 16)) if op == 0x0F else int(rng.integers(0, N_REGS))
        prog[n_active - 1] = encode_instr(op, 7, int(rng.integers(0, N_REGS)), b)
    return prog


def sample_valid(
    rng: np.random.Generator, structured: bool = True, max_tries: int = 100
) -> np.ndarray:
    """Rejection-sample until S0-valid (bounded tries; raises on failure)."""
    sampler = sample_structured if structured else sample_pure
    for _ in range(max_tries):
        prog = sampler(rng)
        if is_valid(prog):
            return prog
    raise RuntimeError(f"no valid program in {max_tries} tries")


def mutate_point(program: np.ndarray, rng: np.random.Generator, p_byte: float = 0.02) -> np.ndarray:
    """Flip random bytes with probability p_byte per byte."""
    raw = program.view(np.uint8).copy()
    mask = rng.random(raw.shape) < p_byte
    raw[mask] = rng.integers(0, 256, size=int(mask.sum()), dtype=np.int64).astype(np.uint8)
    out = raw.view(np.uint32).copy()
    # Clamp opcodes into the known table so mutation stays in-schema.
    for i in range(N_INSTR):
        op = int(out[i]) & 0xFF
        if op not in OPCODES:
            out[i] = np.uint32((int(out[i]) & 0xFFFFFF00) | 0x00)
    return out


def crossover_single_point(
    a: np.ndarray, b: np.ndarray, rng: np.random.Generator
) -> tuple[np.ndarray, np.ndarray]:
    """Single-point crossover over 16 slots."""
    pt = int(rng.integers(1, N_INSTR))
    c1 = np.concatenate([a[:pt], b[pt:]]).astype(np.uint32)
    c2 = np.concatenate([b[:pt], a[pt:]]).astype(np.uint32)
    return c1, c2


def select_tournament(
    fitnesses: np.ndarray,
    tournament_size: int,
    rng: np.random.Generator,
    sample_pool_size: int | None = None,
) -> int:
    """Select candidate index via tournament selection among random competitors."""
    pool_len = len(fitnesses) if sample_pool_size is None else min(len(fitnesses), sample_pool_size)
    competitors = rng.integers(0, pool_len, size=tournament_size)
    best_comp = competitors[np.argmin(fitnesses[competitors])]
    return int(best_comp)


def select_topk(
    population: np.ndarray,
    fitnesses: np.ndarray,
    k: int,
) -> np.ndarray:
    """Select top-k candidates by lowest fitness."""
    order = np.argsort(fitnesses)[:k]
    return population[order].copy()


def mutate_block(
    program: np.ndarray,
    rng: np.random.Generator,
    p_block: float = 0.05,
    max_block_len: int = 3,
) -> np.ndarray:
    """Large (block) mutation: replaces a contiguous chunk of instructions with freshly sampled ones."""
    out = program.copy()
    if rng.random() < p_block:
        block_len = int(rng.integers(1, max_block_len + 1))
        start = int(rng.integers(0, N_INSTR - block_len + 1))
        for idx in range(start, start + block_len):
            op = int(rng.choice(STRUCTURED_OPS, p=STRUCTURED_OP_RATIOS))
            dst = int(rng.integers(0, N_REGS))
            a = int(rng.integers(0, N_REGS))
            b = int(rng.integers(0, 16)) if op == 0x0F else int(rng.integers(0, N_REGS))
            out[idx] = encode_instr(op, dst, a, b)
    return out


def mutate_candidate(
    program: np.ndarray,
    rng: np.random.Generator,
    p_gene: float = 0.08,
    p_block: float = 0.05,
    p_byte: float = 0.02,
) -> np.ndarray:
    """Comprehensive mutation combining block, instruction-level, and byte-level mutations."""
    out = program.copy()
    if p_block > 0.0 and rng.random() < p_block:
        out = mutate_block(out, rng, p_block=1.0)
    if p_gene > 0.0:
        for i in range(N_INSTR):
            if rng.random() < p_gene:
                op = int(rng.choice(STRUCTURED_OPS, p=STRUCTURED_OP_RATIOS))
                dst = int(rng.integers(0, N_REGS))
                a = int(rng.integers(0, N_REGS))
                b = int(rng.integers(0, 16)) if op == 0x0F else int(rng.integers(0, N_REGS))
                out[i] = encode_instr(op, dst, a, b)
    if p_byte > 0.0:
        out = mutate_point(out, rng, p_byte=p_byte)
    return out


@dataclass
class EvolutionConfig:
    """Evolution hyperparameters and operational controls."""

    pop_size: int = 500
    elite_k: int = 32
    tournament_size: int = 4
    crossover_p: float = 0.3
    point_mut_p: float = 0.02
    large_mut_p: float = 0.05
    gene_mut_p: float = 0.08
    random_inject_p: float = 0.10
    max_generations: int = 100
    early_stop_fitness: float = 1e-5
    complexity_weight: float = 0.001
    checkpoint_interval: int = 0
    checkpoint_path: str | Path | None = None

    def __post_init__(self) -> None:
        if self.random_inject_p < 0.10:
            raise ValueError(
                f"random_inject_p must be >= 0.10 per EVOLUTION.md rule (got {self.random_inject_p})"
            )
        if self.pop_size <= 0:
            raise ValueError(f"pop_size must be positive (got {self.pop_size})")
        if self.elite_k < 0:
            raise ValueError(f"elite_k must be non-negative (got {self.elite_k})")


def step_generation(
    population: np.ndarray,
    fitnesses: np.ndarray,
    config: EvolutionConfig,
    rng: np.random.Generator,
) -> np.ndarray:
    """Advance population by one generation: elitism, tournament selection, crossover, mutation, injection."""
    pop_size = config.pop_size
    order = np.argsort(fitnesses)
    sorted_pop = population[order]
    sorted_fit = fitnesses[order]

    # 1. Elitism: preserve top-K
    k = min(config.elite_k, len(sorted_pop))
    elites = sorted_pop[:k].copy()

    # 2. Random injection floor (at least 10% pure random, always)
    n_inject = max(
        int(np.ceil(config.random_inject_p * pop_size)),
        int(np.ceil(0.10 * pop_size)),
    )
    n_pure = n_inject // 2
    n_struct = n_inject - n_pure
    injected_list = [sample_pure(rng) for _ in range(n_pure)] + [
        sample_structured(rng) for _ in range(n_struct)
    ]
    injected = np.stack(injected_list)

    # 3. Offspring generation via tournament selection
    n_offspring = pop_size - len(elites) - len(injected)
    offspring = []
    pool_size = max(4, min(len(sorted_pop), max(20, int(0.25 * len(sorted_pop)))))

    while len(offspring) < n_offspring:
        idx1 = select_tournament(
            sorted_fit, config.tournament_size, rng, sample_pool_size=pool_size
        )
        idx2 = select_tournament(
            sorted_fit, config.tournament_size, rng, sample_pool_size=pool_size
        )
        p1 = sorted_pop[idx1]
        p2 = sorted_pop[idx2]

        if rng.random() < config.crossover_p:
            c1, c2 = crossover_single_point(p1, p2, rng)
        else:
            c1, c2 = p1.copy(), p2.copy()

        c1 = mutate_candidate(
            c1,
            rng,
            p_gene=config.gene_mut_p,
            p_block=config.large_mut_p,
            p_byte=config.point_mut_p,
        )
        offspring.append(c1)

        if len(offspring) < n_offspring:
            c2 = mutate_candidate(
                c2,
                rng,
                p_gene=config.gene_mut_p,
                p_block=config.large_mut_p,
                p_byte=config.point_mut_p,
            )
            offspring.append(c2)

    parts = [elites]
    if offspring:
        parts.append(np.stack(offspring))
    if len(injected) > 0:
        parts.append(injected)
    next_pop = np.concatenate(parts, axis=0)
    return next_pop[:pop_size]


def run_evolution(
    xs_train: np.ndarray,
    ys_train: np.ndarray,
    config: EvolutionConfig,
    rng: np.random.Generator,
    xs_val: np.ndarray | None = None,
    ys_val: np.ndarray | None = None,
    archive: Any | None = None,
    on_generation: Callable[[dict[str, Any]], None] | None = None,
    initial_population: np.ndarray | None = None,
    start_generation: int = 1,
) -> dict[str, Any]:
    """Execute the full closed evolutionary loop."""
    from evobyte.archive import save_checkpoint

    if initial_population is not None:
        pop = initial_population.copy()
    else:
        pop = np.stack([sample_structured(rng) for _ in range(config.pop_size)])

    ys_t = torch.from_numpy(ys_train)
    t_start = time.perf_counter()
    best_overall_fit = float("inf")
    best_overall_prog = pop[0].copy()
    best_overall_mse = float("inf")
    converged = False
    last_gen = start_generation

    for gen in range(start_generation, start_generation + config.max_generations):
        last_gen = gen
        # Evaluate batch with VRAM-budget-aware batching
        preds, flags = execute_chunked(pop, xs_train)
        diff = preds - ys_t.unsqueeze(0).to(preds.device)
        mse = (diff**2).mean(dim=1)
        # Heavy penalty for runtime invalidity (division by zero, overflow, NaN)
        mse[flags.any(dim=1)] += 1e6
        raw_mse = mse.cpu().numpy()

        # Complexity penalty: non-NOP instruction count
        complexity = np.array([sum((int(w) & 0xFF) != 0 for w in p) for p in pop], dtype=np.float32)
        fitnesses = raw_mse + config.complexity_weight * complexity

        best_idx = int(np.argmin(fitnesses))
        gen_best_fit = float(fitnesses[best_idx])
        gen_best_mse = float(raw_mse[best_idx])

        if gen_best_fit < best_overall_fit:
            best_overall_fit = gen_best_fit
            best_overall_mse = gen_best_mse
            best_overall_prog = pop[best_idx].copy()

        # Archive hook
        if archive is not None:
            archive.add_elite(
                program=best_overall_prog,
                generation=gen,
                fitness=best_overall_fit,
                train_error=best_overall_mse,
                complexity=float(sum((int(w) & 0xFF) != 0 for w in best_overall_prog)),
            )

        # Checkpoint hook
        if (
            config.checkpoint_interval > 0
            and config.checkpoint_path is not None
            and gen % config.checkpoint_interval == 0
        ):
            state = {
                "generation": gen,
                "rng_state": rng.bit_generator.state,
                "population": pop.copy(),
            }
            save_checkpoint(config.checkpoint_path, state)

        # Callback hook
        if on_generation is not None:
            stats = {
                "generation": gen,
                "best_fitness": best_overall_fit,
                "best_mse": best_overall_mse,
                "best_expression": decode_human(best_overall_prog),
                "elapsed_time": time.perf_counter() - t_start,
                "candidates_total": (gen - start_generation + 1) * config.pop_size,
            }
            on_generation(stats)

        # Early termination
        if best_overall_mse <= config.early_stop_fitness:
            converged = True
            break

        # Reproduce & advance population
        pop = step_generation(pop, fitnesses, config, rng)

    total_time = time.perf_counter() - t_start
    total_candidates = (last_gen - start_generation + 1) * config.pop_size

    return {
        "best_program": best_overall_prog,
        "best_fitness": best_overall_fit,
        "best_mse": best_overall_mse,
        "best_expression": decode_human(best_overall_prog),
        "generations": last_gen - start_generation + 1,
        "candidates_total": total_candidates,
        "time_sec": total_time,
        "cvps": total_candidates / max(total_time, 1e-6),
        "converged": converged,
    }
