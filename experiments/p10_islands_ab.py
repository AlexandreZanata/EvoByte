"""Experiment script for P10: A/B Benchmark Single-Population Control vs 4-Island Ring Migration."""

from __future__ import annotations

import argparse
import sys
import time
from typing import Any

import numpy as np

from evobyte.evolution import EvolutionConfig, run_evolution
from evobyte.islands import IslandRunnerConfig, run_evolution_islands
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


def run_islands_ab_benchmark(
    seeds: list[int],
    budget_sec: float = 600.0,
    total_pop_size: int = 1000,
    max_generations: int = 100,
    migration_interval: int = 5,
    migration_k: int = 4,
) -> tuple[bool, dict[str, Any]]:
    splits = generate_target_splits()
    xs_train, ys_train = splits["train"]
    xs_val, ys_val = splits["val"]
    xs_hidden, ys_hidden = splits["hidden"]
    xs_extrap, ys_extrap = splits["extrapolation"]

    print("================================================================================")
    print(f"P10 A/B Benchmark: Single-Pop Control vs 4-Island Ring Migration")
    print(f"Target: y = x^2 + 3x + 7 | Total Pop: {total_pop_size} | Seeds: {len(seeds)} | Budget: {budget_sec:.0f}s")
    print("================================================================================\n")

    single_results = []
    islands_results = []

    # 1. Condition A: Single-Population Control (N = 1000)
    print("--- Running Condition A: Single-Population Control (N = 1000) ---")
    for i, s in enumerate(seeds, 1):
        rng = np.random.default_rng(s)
        cfg_single = EvolutionConfig(
            pop_size=total_pop_size,
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
        res = run_evolution(xs_train, ys_train, cfg_single, rng)
        elapsed = time.perf_counter() - t0

        best_p = res["best_program"]
        ev_hid = evaluate(best_p, xs_hidden, ys_hidden)
        ev_ext = evaluate(best_p, xs_extrap, ys_extrap)
        success = (ev_hid["mse"] <= 1e-3) and (ev_ext["mse"] <= 1e-3)

        record = {
            "seed": s,
            "success": success,
            "generations": res["generations"],
            "time_sec": elapsed,
            "cvps": res["cvps"],
            "hidden_mse": ev_hid["mse"],
            "extrap_mse": ev_ext["mse"],
            "expression": res["best_expression"],
        }
        single_results.append(record)
        print(
            f"[Single {i}/{len(seeds)}] Seed {s:4d} | Success: {str(success):5s} | "
            f"Gen: {res['generations']:3d} | Time: {elapsed:5.1f}s | CVPS: {res['cvps']:6.1f} | "
            f"Hidden MSE: {ev_hid['mse']:.2e}"
        )

    # 2. Condition B: 4-Island Ring Migration (4 x 250 = 1000)
    print("\n--- Running Condition B: 4-Island Ring Migration (4 x 250 = 1000) ---")
    for i, s in enumerate(seeds, 1):
        rng = np.random.default_rng(s)
        cfg_islands = IslandRunnerConfig(
            n_islands=4,
            total_pop_size=total_pop_size,
            migration_interval=migration_interval,
            migration_k=migration_k,
            max_generations=max_generations,
            early_stop_fitness=1e-5,
        )
        t0 = time.perf_counter()
        res = run_evolution_islands(xs_train, ys_train, cfg_islands, rng)
        elapsed = time.perf_counter() - t0

        best_p = res["best_program"]
        ev_hid = evaluate(best_p, xs_hidden, ys_hidden)
        ev_ext = evaluate(best_p, xs_extrap, ys_extrap)
        success = (ev_hid["mse"] <= 1e-3) and (ev_ext["mse"] <= 1e-3)

        record = {
            "seed": s,
            "success": success,
            "generations": res["generations"],
            "time_sec": elapsed,
            "cvps": res["cvps"],
            "hidden_mse": ev_hid["mse"],
            "extrap_mse": ev_ext["mse"],
            "expression": res["best_expression"],
        }
        islands_results.append(record)
        print(
            f"[Islands {i}/{len(seeds)}] Seed {s:4d} | Success: {str(success):5s} | "
            f"Gen: {res['generations']:3d} | Time: {elapsed:5.1f}s | CVPS: {res['cvps']:6.1f} | "
            f"Hidden MSE: {ev_hid['mse']:.2e}"
        )

    # Aggregate comparisons
    single_succ = sum(r["success"] for r in single_results) / len(seeds)
    islands_succ = sum(r["success"] for r in islands_results) / len(seeds)

    single_time = np.mean([r["time_sec"] for r in single_results])
    islands_time = np.mean([r["time_sec"] for r in islands_results])

    single_cvps = np.mean([r["cvps"] for r in single_results])
    islands_cvps = np.mean([r["cvps"] for r in islands_results])

    print("\n### A/B Comparison Table: Single-Population vs 4-Island Ring Migration\n")
    print("| Condition | Success Rate | Mean Time (s) | Mean CVPS | Notes |")
    print("|---|---|---|---|---|")
    print(f"| **Single-Population (Control)** | {single_succ*100:.1f}% ({sum(r['success'] for r in single_results)}/{len(seeds)}) | {single_time:.1f}s | {single_cvps:.1f} | Unified selection pool |")
    print(f"| **4-Island Ring Migration** | **{islands_succ*100:.1f}%** ({sum(r['success'] for r in islands_results)}/{len(seeds)}) | {islands_time:.1f}s | {islands_cvps:.1f} | Heterogeneous pressures + ring transfer |")

    gate_passed = islands_succ >= 0.60
    print("\n--------------------------------------------------------------------------------")
    print(f"Islands Success Rate: {islands_succ*100:.1f}% (Threshold >= 60%): {'PASS' if gate_passed else 'FAIL'}")
    print(f"P10 Exit Gate: {'PASS' if gate_passed else 'FAIL'}")
    print("--------------------------------------------------------------------------------\n")

    return gate_passed, {"single": single_results, "islands": islands_results}


def main() -> int:
    parser = argparse.ArgumentParser(description="P10 Islands A/B Benchmark")
    parser.add_argument("--budget", type=str, default="10min", help="Time budget (default: 10min)")
    parser.add_argument("--seeds", type=int, default=5, help="Number of seeds (default: 5)")
    parser.add_argument("--pop-size", type=int, default=1000, help="Total population size (default: 1000)")
    parser.add_argument("--max-generations", type=int, default=100, help="Max generations (default: 100)")
    args = parser.parse_args()

    default_seed_list = [42, 101, 202, 303, 404]
    if args.seeds == 5:
        seeds = default_seed_list
    else:
        seeds = [100 + i for i in range(args.seeds)]

    budget_sec = parse_budget(args.budget)
    passed, _ = run_islands_ab_benchmark(
        seeds=seeds,
        budget_sec=budget_sec,
        total_pop_size=args.pop_size,
        max_generations=args.max_generations,
    )
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
