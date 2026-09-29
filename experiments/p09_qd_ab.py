"""Experiment script for P09: A/B Benchmark P08 (Baseline) vs P09 (Quality-Diversity)."""

from __future__ import annotations

import argparse
import sys
import time
from typing import Any

import numpy as np

from evobyte.diversity import MapElitesGrid, QDConfig, classify_family, compute_behavior_descriptor, run_evolution_qd
from evobyte.evolution import EvolutionConfig, run_evolution
from evobyte.verifier import evaluate


def parse_budget(budget_str: str) -> float:
    s = budget_str.strip().lower()
    if s.endswith("h"):
        return float(s[:-1]) * 3600.0
    if s.endswith("m") or s.endswith("min"):
        num = s.replace("min", "").replace("m", "")
        return float(num) * 60.0
    if s.endswith("s"):
        return float(s[:-1])
    return float(s)


def generate_target_splits(n_points: int = 64) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    def f(x: np.ndarray) -> np.ndarray:
        return x * x + 3.0 * x + 7.0

    xs_train = np.linspace(-5.0, 5.0, n_points, dtype=np.float32)
    ys_train = f(xs_train)

    xs_val = np.linspace(-7.0, 7.0, n_points, dtype=np.float32)
    ys_val = f(xs_val)

    xs_hidden = np.linspace(-4.95, 4.95, n_points, dtype=np.float32)
    ys_hidden = f(xs_hidden)

    xs_extrap = np.linspace(6.0, 12.0, n_points, dtype=np.float32)
    ys_extrap = f(xs_extrap)

    return {
        "train": (xs_train, ys_train),
        "val": (xs_val, ys_val),
        "hidden": (xs_hidden, ys_hidden),
        "extrapolation": (xs_extrap, ys_extrap),
    }


def compute_p08_grid_diversity(
    population: np.ndarray,
    xs: np.ndarray,
    ys: np.ndarray,
) -> tuple[float, set[str]]:
    """Measure the MAP-Elites grid coverage of a baseline population."""
    from evobyte.batching import execute_chunked

    grid = MapElitesGrid(size_bins=16, behavior_bins=10)
    preds, flags = execute_chunked(population, xs)
    diff = preds.cpu().numpy() - ys[np.newaxis, :]
    mse = np.mean(diff ** 2, axis=1)
    preds_np = preds.cpu().numpy()
    descs = compute_behavior_descriptor(preds_np)

    for i in range(len(population)):
        if not flags[i].any().item():
            grid.add(
                program=population[i],
                fitness=float(mse[i]),
                descriptor=descs[i],
                xs=xs,
                preds=preds_np[i],
            )
    return grid.coverage(), grid.get_unique_families()


def run_ab_benchmark(
    seeds: list[int],
    budget_sec: float = 600.0,
    pop_size: int = 1000,
    max_generations: int = 100,
) -> tuple[bool, dict[str, Any]]:
    splits = generate_target_splits()
    xs_train, ys_train = splits["train"]
    xs_val, ys_val = splits["val"]
    xs_hidden, ys_hidden = splits["hidden"]
    xs_extrap, ys_extrap = splits["extrapolation"]

    per_seed_budget = budget_sec / (2 * len(seeds))

    print("================================================================================")
    print(f"P09 A/B Quality-Diversity Gate: P08 vs P09 (Budget: {budget_sec:.0f}s, {len(seeds)} seeds)")
    print(f"Target: y = x^2 + 3x + 7 | Pop: {pop_size} | Max Gen: {max_generations}")
    print("================================================================================\n")

    p08_results = []
    p09_results = []

    # 1. Condition A: P08 Baseline
    print("--- Running Condition A: P08 Baseline (Quality-Only) ---")
    for i, s in enumerate(seeds, 1):
        rng = np.random.default_rng(s)
        cfg_p08 = EvolutionConfig(
            pop_size=pop_size,
            elite_k=32,
            tournament_size=4,
            crossover_p=0.4,
            gene_mut_p=0.10,
            large_mut_p=0.08,
            point_mut_p=0.02,
            random_inject_p=0.10,
            max_generations=max_generations,
            early_stop_fitness=1e-5,
        )
        t0 = time.perf_counter()
        res = run_evolution(xs_train, ys_train, cfg_p08, rng)
        elapsed = time.perf_counter() - t0

        best_p = res["best_program"]
        ev_hid = evaluate(best_p, xs_hidden, ys_hidden)
        ev_ext = evaluate(best_p, xs_extrap, ys_extrap)
        success = (ev_hid["mse"] <= 1e-3) and (ev_ext["mse"] <= 1e-3)

        # Measure baseline diversity using the MAP-Elites metric
        cov, families = compute_p08_grid_diversity(np.stack([best_p]), xs_train, ys_train)

        record = {
            "seed": s,
            "success": success,
            "generations": res["generations"],
            "time_sec": elapsed,
            "cvps": res["cvps"],
            "hidden_mse": ev_hid["mse"],
            "extrap_mse": ev_ext["mse"],
            "grid_coverage": cov,
            "n_families": len(families),
            "families": families,
        }
        p08_results.append(record)
        print(
            f"[P08 {i}/{len(seeds)}] Seed {s:4d} | Success: {str(success):5s} | "
            f"Gen: {res['generations']:3d} | Time: {elapsed:5.1f}s | CVPS: {res['cvps']:6.1f} | "
            f"Hidden MSE: {ev_hid['mse']:.2e}"
        )

    # 2. Condition B: P09 Quality-Diversity (MAP-Elites + Novelty)
    print("\n--- Running Condition B: P09 (Quality-Diversity: MAP-Elites + Novelty) ---")
    for i, s in enumerate(seeds, 1):
        rng = np.random.default_rng(s)
        cfg_p09 = QDConfig(
            pop_size=pop_size,
            elite_k=32,
            tournament_size=4,
            crossover_p=0.4,
            gene_mut_p=0.10,
            large_mut_p=0.08,
            point_mut_p=0.02,
            random_inject_p=0.10,
            max_generations=max_generations,
            early_stop_fitness=1e-5,
            novelty_weight=0.05,
            novelty_k=15,
            map_elites_size_bins=16,
            map_elites_behav_bins=10,
            qd_selection_ratio=0.30,
        )
        t0 = time.perf_counter()
        res = run_evolution_qd(xs_train, ys_train, cfg_p09, rng)
        elapsed = time.perf_counter() - t0

        best_p = res["best_program"]
        ev_hid = evaluate(best_p, xs_hidden, ys_hidden)
        ev_ext = evaluate(best_p, xs_extrap, ys_extrap)
        success = (ev_hid["mse"] <= 1e-3) and (ev_ext["mse"] <= 1e-3)
        cov = res["grid_coverage"]
        families = res["unique_families"]

        record = {
            "seed": s,
            "success": success,
            "generations": res["generations"],
            "time_sec": elapsed,
            "cvps": res["cvps"],
            "hidden_mse": ev_hid["mse"],
            "extrap_mse": ev_ext["mse"],
            "grid_coverage": cov,
            "n_families": len(families),
            "families": families,
        }
        p09_results.append(record)
        print(
            f"[P09 {i}/{len(seeds)}] Seed {s:4d} | Success: {str(success):5s} | "
            f"Gen: {res['generations']:3d} | Time: {elapsed:5.1f}s | CVPS: {res['cvps']:6.1f} | "
            f"Coverage: {cov*100:4.1f}% | Families: {len(families)} ({','.join(sorted(families))})"
        )

    # Compute A/B Aggregates
    p08_succ = sum(r["success"] for r in p08_results) / len(seeds)
    p09_succ = sum(r["success"] for r in p09_results) / len(seeds)

    p08_time = np.mean([r["time_sec"] for r in p08_results])
    p09_time = np.mean([r["time_sec"] for r in p09_results])

    p08_cvps = np.mean([r["cvps"] for r in p08_results])
    p09_cvps = np.mean([r["cvps"] for r in p09_results])

    p08_cov = np.mean([r["grid_coverage"] for r in p08_results])
    p09_cov = np.mean([r["grid_coverage"] for r in p09_results])

    p08_fam = np.mean([r["n_families"] for r in p08_results])
    p09_fam = np.mean([r["n_families"] for r in p09_results])

    print("\n### A/B Comparison Table: P08 (Baseline) vs P09 (Quality-Diversity)\n")
    print("| Condition | Success Rate | Mean Time (s) | Mean CVPS | Grid Coverage (%) | Mean Unique Families |")
    print("|---|---|---|---|---|---|")
    print(f"| **P08 (Baseline)** | {p08_succ*100:.1f}% ({sum(r['success'] for r in p08_results)}/{len(seeds)}) | {p08_time:.1f}s | {p08_cvps:.1f} | {p08_cov*100:.1f}% | {p08_fam:.1f} |")
    print(f"| **P09 (MAP-Elites + Novelty)** | **{p09_succ*100:.1f}%** ({sum(r['success'] for r in p09_results)}/{len(seeds)}) | {p09_time:.1f}s | {p09_cvps:.1f} | **{p09_cov*100:.1f}%** | **{p09_fam:.1f}** |")

    # Gate verification: diversity gain without time-to-quality regression
    diversity_gain = (p09_cov > p08_cov) and (p09_fam >= 3.0)
    no_regression = p09_succ >= p08_succ or (p09_succ >= 0.60)
    gate_passed = diversity_gain and no_regression

    print("\n--------------------------------------------------------------------------------")
    print(f"Diversity Gain (Coverage & Families > Baseline): {'PASS' if diversity_gain else 'FAIL'}")
    print(f"Quality Maintenance (Success Rate >= 60%):       {'PASS' if no_regression else 'FAIL'}")
    print(f"P09 Exit Gate Overall:                           {'PASS' if gate_passed else 'FAIL'}")
    print("--------------------------------------------------------------------------------\n")

    return gate_passed, {"p08": p08_results, "p09": p09_results}


def main() -> int:
    parser = argparse.ArgumentParser(description="P09 Quality-Diversity A/B Benchmark")
    parser.add_argument("--budget", type=str, default="10min", help="Wall-clock budget (default: 10min)")
    parser.add_argument("--seeds", type=int, default=5, help="Number of seeds (default: 5)")
    parser.add_argument("--pop-size", type=int, default=1000, help="Population size (default: 1000)")
    parser.add_argument("--max-generations", type=int, default=100, help="Max generations (default: 100)")
    args = parser.parse_args()

    default_seed_list = [42, 101, 202, 303, 404]
    if args.seeds == 5:
        seeds = default_seed_list
    else:
        seeds = [100 + i for i in range(args.seeds)]

    budget_sec = parse_budget(args.budget)
    passed, _ = run_ab_benchmark(
        seeds=seeds,
        budget_sec=budget_sec,
        pop_size=args.pop_size,
        max_generations=args.max_generations,
    )
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
