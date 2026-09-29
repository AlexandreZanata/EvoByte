"""Quality Diversity (MAP-Elites + Novelty Search) primitives (spec: docs/EVOLUTION.md, P09)."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import numpy as np
import torch

from evobyte.batching import execute_chunked
from evobyte.bytecode import N_INSTR, decode_human
from evobyte.evolution import (
    EvolutionConfig,
    crossover_single_point,
    mutate_candidate,
    sample_pure,
    sample_structured,
    select_tournament,
)


def classify_family(program: np.ndarray) -> str:
    """Classify program into mathematical family based on active opcodes."""
    active_ops = set((int(w) & 0xFF) for w in program if (int(w) & 0xFF) != 0)
    if active_ops & {0x05, 0x06}:  # SIN, COS
        return "trig"
    if active_ops & {0x07, 0x08}:  # EXP, LOG
        return "exp_log"
    if active_ops & {0x09, 0x0B}:  # POW, SQRT
        return "power_root"
    if active_ops & {0x0A, 0x0D, 0x0E}:  # ABS, MIN, MAX
        return "piecewise"
    if active_ops <= {0x01, 0x02, 0x03, 0x0C, 0x0F}:  # ADD, SUB, MUL, NEG, CSEL
        return "polynomial"
    return "other"


def compute_behavior_descriptor(preds: np.ndarray | torch.Tensor) -> np.ndarray:
    """Compute normalized behavior vector (Z-score normalized and clamped to [-3, 3])."""
    if isinstance(preds, torch.Tensor):
        arr = preds.detach().cpu().numpy()
    else:
        arr = np.asarray(preds, dtype=np.float32)

    # Handle single vector vs 2D batch
    if arr.ndim == 1:
        s = float(np.std(arr))
        if s < 1e-6 or not np.isfinite(s):
            return np.zeros_like(arr, dtype=np.float32)
        m = float(np.mean(arr))
        return np.clip((arr - m) / s, -3.0, 3.0).astype(np.float32)
    else:
        s = np.std(arr, axis=1, keepdims=True)
        m = np.mean(arr, axis=1, keepdims=True)
        safe_s = np.where((s < 1e-6) | (~np.isfinite(s)), 1.0, s)
        norm = (arr - m) / safe_s
        norm = np.where((s < 1e-6) | (~np.isfinite(s)), 0.0, norm)
        return np.clip(norm, -3.0, 3.0).astype(np.float32)


def compute_trend_feature(xs: np.ndarray, preds: np.ndarray) -> float:
    """Compute normalized Pearson correlation between xs and preds in [-1.0, 1.0]."""
    if not np.all(np.isfinite(preds)):
        return 0.0
    sx = float(np.std(xs))
    sy = float(np.std(preds))
    if sx < 1e-6 or sy < 1e-6:
        return 0.0
    cov = float(np.mean((xs - np.mean(xs)) * (preds - np.mean(preds))))
    r = cov / (sx * sy + 1e-7)
    return float(np.clip(r, -1.0, 1.0))


class NoveltyArchive:
    """Archive of historical behavior descriptors with vectorized k-NN novelty computation."""

    def __init__(self, max_size: int = 2000) -> None:
        self.max_size = max_size
        self.descriptors: list[np.ndarray] = []

    def add(self, descriptor: np.ndarray) -> None:
        if len(self.descriptors) >= self.max_size:
            # Drop oldest entry FIFO
            self.descriptors.pop(0)
        self.descriptors.append(np.asarray(descriptor, dtype=np.float32).copy())

    def compute_novelty_scores(self, population_descriptors: np.ndarray, k: int = 15) -> np.ndarray:
        """Compute average Euclidean distance to k nearest neighbors in archive + population."""
        pop_t = torch.from_numpy(population_descriptors).float()
        n_pop = pop_t.shape[0]

        if len(self.descriptors) > 0:
            arch_t = torch.from_numpy(np.stack(self.descriptors)).float()
            all_t = torch.cat([pop_t, arch_t], dim=0)
        else:
            all_t = pop_t

        n_neighbors = min(k + 1, all_t.shape[0])
        if n_neighbors <= 1:
            return np.zeros((n_pop,), dtype=np.float32)

        dists = torch.cdist(pop_t, all_t)
        topk_vals, _ = torch.topk(dists, k=n_neighbors, largest=False, dim=1)
        # Exclude self distance at index 0
        novelty = topk_vals[:, 1:].mean(dim=1)
        return novelty.cpu().numpy()


class MapElitesGrid:
    """2D Quality-Diversity grid binned by (Program Size, Behavioral Trend)."""

    def __init__(self, size_bins: int = 16, behavior_bins: int = 10) -> None:
        self.size_bins = size_bins
        self.behavior_bins = behavior_bins
        self.cells: dict[tuple[int, int], dict[str, Any]] = {}

    def add(
        self,
        program: np.ndarray,
        fitness: float,
        descriptor: np.ndarray,
        xs: np.ndarray,
        preds: np.ndarray,
    ) -> bool:
        """Add candidate to grid. Returns True if new cell filled or existing cell improved."""
        size = int(sum((int(w) & 0xFF) != 0 for w in program))
        size_idx = min(self.size_bins - 1, max(0, size - 1))

        trend = compute_trend_feature(xs, preds)
        behav_idx = min(self.behavior_bins - 1, max(0, int((trend + 1.0) / 2.0 * self.behavior_bins)))

        cell_key = (size_idx, behav_idx)
        if cell_key not in self.cells or fitness < self.cells[cell_key]["fitness"]:
            self.cells[cell_key] = {
                "program": program.copy(),
                "fitness": float(fitness),
                "size": size,
                "trend": trend,
                "descriptor": descriptor.copy(),
                "family": classify_family(program),
                "expression": decode_human(program),
            }
            return True
        return False

    def coverage(self) -> float:
        """Fraction of grid cells occupied."""
        total_cells = self.size_bins * self.behavior_bins
        return len(self.cells) / total_cells if total_cells > 0 else 0.0

    def occupied_count(self) -> int:
        return len(self.cells)

    def get_elites(self) -> list[dict[str, Any]]:
        return list(self.cells.values())

    def get_unique_families(self) -> set[str]:
        return {c["family"] for c in self.cells.values()}


@dataclass
class QDConfig(EvolutionConfig):
    """Quality-Diversity configuration extending standard EvolutionConfig."""

    novelty_weight: float = 0.05
    novelty_k: int = 15
    map_elites_size_bins: int = 16
    map_elites_behav_bins: int = 10
    qd_selection_ratio: float = 0.30


def run_evolution_qd(
    xs_train: np.ndarray,
    ys_train: np.ndarray,
    config: QDConfig,
    rng: np.random.Generator,
    xs_val: np.ndarray | None = None,
    ys_val: np.ndarray | None = None,
    archive: Any | None = None,
    on_generation: Callable[[dict[str, Any]], None] | None = None,
    initial_population: np.ndarray | None = None,
    start_generation: int = 1,
) -> dict[str, Any]:
    """Execute Quality-Diversity evolutionary loop with MAP-Elites grid and novelty bonus."""
    pop_size = config.pop_size
    if initial_population is not None:
        pop = initial_population.copy()
    else:
        pop = np.stack([sample_structured(rng) for _ in range(pop_size)])

    grid = MapElitesGrid(
        size_bins=config.map_elites_size_bins,
        behavior_bins=config.map_elites_behav_bins,
    )
    novelty_arch = NoveltyArchive()

    ys_t = torch.from_numpy(ys_train)
    t_start = time.perf_counter()
    best_overall_fit = float("inf")
    best_overall_prog = pop[0].copy()
    best_overall_mse = float("inf")
    converged = False
    last_gen = start_generation

    for gen in range(start_generation, start_generation + config.max_generations):
        last_gen = gen
        # 1. Batch evaluation
        preds, flags = execute_chunked(pop, xs_train)
        diff = preds - ys_t.unsqueeze(0).to(preds.device)
        raw_mse_t = (diff ** 2).mean(dim=1)
        raw_mse_t[flags.any(dim=1)] += 1e6
        raw_mse = raw_mse_t.cpu().numpy()

        preds_np = preds.cpu().numpy()
        descriptors = compute_behavior_descriptor(preds_np)

        # 2. Update MAP-Elites grid with current candidates
        for i in range(pop_size):
            if not flags[i].any().item():
                grid.add(
                    program=pop[i],
                    fitness=float(raw_mse[i]),
                    descriptor=descriptors[i],
                    xs=xs_train,
                    preds=preds_np[i],
                )

        # 3. Novelty bonus calculation
        if config.novelty_weight > 0.0:
            novelty_scores = novelty_arch.compute_novelty_scores(descriptors, k=config.novelty_k)
            # Normalize novelty scores into [0, 1]
            n_min = float(np.min(novelty_scores))
            n_max = float(np.max(novelty_scores))
            norm_novelty = (novelty_scores - n_min) / (n_max - n_min + 1e-6)
        else:
            norm_novelty = np.zeros(pop_size, dtype=np.float32)

        # 4. Selection fitness combines Quality (MSE + complexity) with Novelty bonus
        complexity = np.array(
            [sum((int(w) & 0xFF) != 0 for w in p) for p in pop], dtype=np.float32
        )
        combined_fitness = raw_mse + config.complexity_weight * complexity - config.novelty_weight * norm_novelty

        # Track absolute best quality candidate
        best_quality_idx = int(np.argmin(raw_mse))
        if float(raw_mse[best_quality_idx]) < best_overall_mse:
            best_overall_mse = float(raw_mse[best_quality_idx])
            best_overall_fit = float(combined_fitness[best_quality_idx])
            best_overall_prog = pop[best_quality_idx].copy()

        # Update novelty archive with high-novelty individuals
        if config.novelty_weight > 0.0:
            top_novel_idx = np.argsort(novelty_scores)[-max(1, pop_size // 50):]
            for idx in top_novel_idx:
                novelty_arch.add(descriptors[idx])

        # Archive hook
        if archive is not None:
            archive.add_elite(
                program=best_overall_prog,
                generation=gen,
                fitness=best_overall_mse,
                train_error=best_overall_mse,
                complexity=float(sum((int(w) & 0xFF) != 0 for w in best_overall_prog)),
                novelty_score=float(norm_novelty[best_quality_idx]),
            )

        # Callback hook
        if on_generation is not None:
            stats = {
                "generation": gen,
                "best_fitness": best_overall_fit,
                "best_mse": best_overall_mse,
                "best_expression": decode_human(best_overall_prog),
                "grid_coverage": grid.coverage(),
                "unique_families": grid.get_unique_families(),
                "elapsed_time": time.perf_counter() - t_start,
                "candidates_total": (gen - start_generation + 1) * pop_size,
            }
            on_generation(stats)

        # Early termination
        if best_overall_mse <= config.early_stop_fitness:
            converged = True
            break

        # 5. Next generation assembly (Quality-Diversity)
        order = np.argsort(combined_fitness)
        sorted_pop = pop[order]
        sorted_fit = combined_fitness[order]

        # Top elites from combined fitness
        k_direct = min(config.elite_k // 2, len(sorted_pop))
        direct_elites = sorted_pop[:k_direct].copy()

        # Elites drawn from MAP-Elites grid to preserve structural diversity
        grid_elites_list = grid.get_elites()
        if len(grid_elites_list) > 0:
            grid_sample_size = min(config.elite_k - k_direct, len(grid_elites_list))
            grid_sample_indices = rng.choice(len(grid_elites_list), size=grid_sample_size, replace=False)
            grid_elites = np.stack([grid_elites_list[idx]["program"] for idx in grid_sample_indices])
            elites = np.concatenate([direct_elites, grid_elites], axis=0)
        else:
            elites = direct_elites

        # Random injection floor (at least 10%)
        n_inject = max(
            int(np.ceil(config.random_inject_p * pop_size)),
            int(np.ceil(0.10 * pop_size)),
        )
        n_pure = n_inject // 2
        n_struct = n_inject - n_pure
        injected = np.stack(
            [sample_pure(rng) for _ in range(n_pure)]
            + [sample_structured(rng) for _ in range(n_struct)]
        )

        # Offspring generation
        n_offspring = pop_size - len(elites) - len(injected)
        offspring = []
        pool_size = max(4, min(len(sorted_pop), max(20, int(0.25 * len(sorted_pop)))))

        while len(offspring) < n_offspring:
            # QD parent selection: 30% from MAP-Elites grid, 70% from tournament
            if len(grid_elites_list) > 0 and rng.random() < config.qd_selection_ratio:
                g_idx = rng.integers(0, len(grid_elites_list))
                p1 = grid_elites_list[g_idx]["program"]
            else:
                idx1 = select_tournament(sorted_fit, config.tournament_size, rng, sample_pool_size=pool_size)
                p1 = sorted_pop[idx1]

            if len(grid_elites_list) > 0 and rng.random() < config.qd_selection_ratio:
                g_idx = rng.integers(0, len(grid_elites_list))
                p2 = grid_elites_list[g_idx]["program"]
            else:
                idx2 = select_tournament(sorted_fit, config.tournament_size, rng, sample_pool_size=pool_size)
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
        pop = np.concatenate(parts, axis=0)[:pop_size]

    total_time = time.perf_counter() - t_start
    total_candidates = (last_gen - start_generation + 1) * pop_size

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
        "grid_coverage": grid.coverage(),
        "unique_families": grid.get_unique_families(),
        "grid_elites_count": grid.occupied_count(),
        "grid": grid,
    }
