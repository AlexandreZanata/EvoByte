"""Island model with ring migration and heterogeneous evolutionary pressures (spec: docs/EVOLUTION.md, P10)."""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch

from evobyte.batching import execute_chunked
from evobyte.bytecode import decode_human
from evobyte.diversity import NoveltyArchive, compute_behavior_descriptor
from evobyte.evolution import EvolutionConfig, sample_structured, step_generation


@dataclass
class IslandConfig:
    """Specialized configuration and pressure for a single island."""

    name: str
    pop_size: int = 250
    elite_k: int = 16
    tournament_size: int = 4
    crossover_p: float = 0.4
    point_mut_p: float = 0.02
    large_mut_p: float = 0.05
    gene_mut_p: float = 0.08
    random_inject_p: float = 0.10
    complexity_weight: float = 0.001
    novelty_weight: float = 0.0


def get_default_island_configs(pop_per_island: int = 250) -> list[IslandConfig]:
    """Return standard 4 islands per docs/EVOLUTION.md with heterogeneous pressures."""
    return [
        IslandConfig(
            name="small-size",
            pop_size=pop_per_island,
            elite_k=16,
            tournament_size=4,
            crossover_p=0.4,
            point_mut_p=0.02,
            large_mut_p=0.05,
            gene_mut_p=0.08,
            random_inject_p=0.10,
            complexity_weight=0.010,  # 10x parsimony pressure
            novelty_weight=0.0,
        ),
        IslandConfig(
            name="high-mutation",
            pop_size=pop_per_island,
            elite_k=16,
            tournament_size=4,
            crossover_p=0.35,
            point_mut_p=0.05,  # High exploratory mutation
            large_mut_p=0.12,
            gene_mut_p=0.15,
            random_inject_p=0.20,  # 20% random injection
            complexity_weight=0.001,
            novelty_weight=0.0,
        ),
        IslandConfig(
            name="low-mutation",
            pop_size=pop_per_island,
            elite_k=16,
            tournament_size=4,
            crossover_p=0.50,  # High recombination, low mutation for exploitation
            point_mut_p=0.01,
            large_mut_p=0.02,
            gene_mut_p=0.04,
            random_inject_p=0.10,
            complexity_weight=0.001,
            novelty_weight=0.0,
        ),
        IslandConfig(
            name="high-novelty",
            pop_size=pop_per_island,
            elite_k=16,
            tournament_size=4,
            crossover_p=0.4,
            point_mut_p=0.02,
            large_mut_p=0.05,
            gene_mut_p=0.08,
            random_inject_p=0.10,
            complexity_weight=0.001,
            novelty_weight=0.10,  # High behavioral diversity pressure
        ),
    ]


@dataclass
class IslandRunnerConfig:
    """Hyperparameters and operational controls for multi-island evolution."""

    n_islands: int = 4
    total_pop_size: int = 1000
    migration_interval: int = 5
    migration_k: int = 4
    max_generations: int = 100
    early_stop_fitness: float = 1e-5
    checkpoint_interval: int = 0
    checkpoint_path: str | Path | None = None
    island_configs: list[IslandConfig] | None = None

    def __post_init__(self) -> None:
        if self.total_pop_size % self.n_islands != 0:
            raise ValueError(
                f"total_pop_size ({self.total_pop_size}) must be divisible by n_islands ({self.n_islands})"
            )
        if self.island_configs is None:
            pop_per_island = self.total_pop_size // self.n_islands
            self.island_configs = get_default_island_configs(pop_per_island)


class IslandModel:
    """Heterogeneous island model with synchronous ring migration."""

    def __init__(
        self,
        config: IslandRunnerConfig,
        rng: np.random.Generator,
        initial_populations: list[np.ndarray] | None = None,
    ) -> None:
        self.config = config
        self.rng = rng
        self.n_islands = config.n_islands
        self.pop_per_island = config.total_pop_size // config.n_islands

        if initial_populations is not None:
            self.populations = [p.copy() for p in initial_populations]
        else:
            self.populations = [
                np.stack([sample_structured(self.rng) for _ in range(self.pop_per_island)])
                for _ in range(self.n_islands)
            ]

        self.novelty_archives = [NoveltyArchive(max_size=500) for _ in range(self.n_islands)]
        self.migration_history: list[dict[str, Any]] = []

    def migrate_ring(self, k: int = 4) -> list[tuple[int, int, int]]:
        """Migrate top-k elites from island i to island (i+1)%n_islands."""
        migrations = []
        # Extract top-k elites from each island (assumes populations are sorted by fitness)
        elites = [self.populations[i][:k].copy() for i in range(self.n_islands)]

        for i in range(self.n_islands):
            dest = (i + 1) % self.n_islands
            # Immigrants replace the worst k individuals in the destination island
            self.populations[dest][-k:] = elites[i].copy()
            migrations.append((i, dest, k))

        return migrations

    def step(
        self,
        xs_train: np.ndarray,
        ys_train: np.ndarray,
        gen: int,
    ) -> dict[str, Any]:
        """Perform one generational step across all islands with tensorized batch evaluation."""
        all_pops = np.concatenate(self.populations, axis=0)
        ys_t = torch.from_numpy(ys_train)

        # Vectorized batch evaluation across all islands simultaneously
        preds, flags = execute_chunked(all_pops, xs_train)
        diff = preds - ys_t.unsqueeze(0).to(preds.device)
        raw_mse = (diff**2).mean(dim=1)
        raw_mse[flags.any(dim=1)] += 1e6
        raw_mse_np = raw_mse.cpu().numpy()

        preds_np = preds.cpu().numpy()
        descriptors = compute_behavior_descriptor(preds_np)

        # Slice results per island
        mse_slices = np.split(raw_mse_np, self.n_islands)
        desc_slices = np.split(descriptors, self.n_islands)

        new_populations = []
        island_stats = []

        for i in range(self.n_islands):
            isl_cfg = self.config.island_configs[i]
            pop_i = self.populations[i]
            mse_i = mse_slices[i]
            desc_i = desc_slices[i]

            complexity = np.array(
                [sum((int(w) & 0xFF) != 0 for w in p) for p in pop_i], dtype=np.float32
            )

            # Novelty pressure calculation for high-novelty island
            if isl_cfg.novelty_weight > 0.0:
                novelty_scores = self.novelty_archives[i].compute_novelty_scores(desc_i, k=10)
                n_min = float(np.min(novelty_scores))
                n_max = float(np.max(novelty_scores))
                norm_novelty = (novelty_scores - n_min) / (n_max - n_min + 1e-6)
                for d in desc_i[np.argsort(novelty_scores)[-2:]]:
                    self.novelty_archives[i].add(d)
            else:
                norm_novelty = np.zeros(self.pop_per_island, dtype=np.float32)

            # Island-specific fitness
            fit_i = (
                mse_i
                + isl_cfg.complexity_weight * complexity
                - isl_cfg.novelty_weight * norm_novelty
            )

            # Sort population by fitness
            order_i = np.argsort(fit_i)
            sorted_pop_i = pop_i[order_i]
            sorted_mse_i = mse_i[order_i]

            island_best_mse = float(sorted_mse_i[0])
            island_best_fit = float(fit_i[order_i[0]])
            island_stats.append(
                {
                    "island": i,
                    "name": isl_cfg.name,
                    "best_mse": island_best_mse,
                    "best_fitness": island_best_fit,
                    "best_expression": decode_human(sorted_pop_i[0]),
                }
            )

            # Evolve population for this island
            ev_cfg = EvolutionConfig(
                pop_size=isl_cfg.pop_size,
                elite_k=isl_cfg.elite_k,
                tournament_size=isl_cfg.tournament_size,
                crossover_p=isl_cfg.crossover_p,
                point_mut_p=isl_cfg.point_mut_p,
                large_mut_p=isl_cfg.large_mut_p,
                gene_mut_p=isl_cfg.gene_mut_p,
                random_inject_p=isl_cfg.random_inject_p,
                complexity_weight=isl_cfg.complexity_weight,
            )
            next_pop_i = step_generation(sorted_pop_i, fit_i[order_i], ev_cfg, self.rng)
            new_populations.append(next_pop_i)

        self.populations = new_populations

        # Check for ring migration trigger
        migration_occurred = False
        if gen % self.config.migration_interval == 0:
            self.migrate_ring(k=self.config.migration_k)
            migration_occurred = True
            self.migration_history.append({"generation": gen, "k": self.config.migration_k})

        # Overall best across all islands
        best_overall_idx = int(np.argmin(raw_mse_np))
        best_overall_prog = all_pops[best_overall_idx].copy()
        best_overall_mse = float(raw_mse_np[best_overall_idx])

        return {
            "best_program": best_overall_prog,
            "best_mse": best_overall_mse,
            "best_expression": decode_human(best_overall_prog),
            "island_stats": island_stats,
            "migration_occurred": migration_occurred,
        }


def run_evolution_islands(
    xs_train: np.ndarray,
    ys_train: np.ndarray,
    config: IslandRunnerConfig,
    rng: np.random.Generator,
    xs_val: np.ndarray | None = None,
    ys_val: np.ndarray | None = None,
    archive: Any | None = None,
    on_generation: Callable[[dict[str, Any]], None] | None = None,
    initial_populations: list[np.ndarray] | None = None,
    start_generation: int = 1,
) -> dict[str, Any]:
    """Execute the closed-loop island evolution with ring migration."""
    from evobyte.archive import save_checkpoint

    model = IslandModel(config, rng, initial_populations=initial_populations)
    t_start = time.perf_counter()
    best_overall_mse = float("inf")
    best_overall_prog = model.populations[0][0].copy()
    converged = False
    last_gen = start_generation

    for gen in range(start_generation, start_generation + config.max_generations):
        last_gen = gen
        step_result = model.step(xs_train, ys_train, gen)

        if step_result["best_mse"] < best_overall_mse:
            best_overall_mse = step_result["best_mse"]
            best_overall_prog = step_result["best_program"].copy()

        # Archive hook
        if archive is not None:
            archive.add_elite(
                program=best_overall_prog,
                generation=gen,
                fitness=best_overall_mse,
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
                "populations": [p.copy() for p in model.populations],
            }
            save_checkpoint(config.checkpoint_path, state)

        # Callback hook
        if on_generation is not None:
            stats = {
                "generation": gen,
                "best_mse": best_overall_mse,
                "best_expression": decode_human(best_overall_prog),
                "island_stats": step_result["island_stats"],
                "migration_occurred": step_result["migration_occurred"],
                "elapsed_time": time.perf_counter() - t_start,
                "candidates_total": (gen - start_generation + 1) * config.total_pop_size,
            }
            on_generation(stats)

        # Early termination
        if best_overall_mse <= config.early_stop_fitness:
            converged = True
            break

    total_time = time.perf_counter() - t_start
    total_candidates = (last_gen - start_generation + 1) * config.total_pop_size

    return {
        "best_program": best_overall_prog,
        "best_mse": best_overall_mse,
        "best_expression": decode_human(best_overall_prog),
        "generations": last_gen - start_generation + 1,
        "candidates_total": total_candidates,
        "time_sec": total_time,
        "cvps": total_candidates / max(total_time, 1e-6),
        "converged": converged,
        "model": model,
    }
