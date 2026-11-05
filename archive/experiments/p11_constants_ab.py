"""Experiment script for P11: A/B Benchmark Bank-Only Control vs Fitted Constants (P11 scope)."""

from __future__ import annotations

import argparse
import sys
import time
from typing import Any, Callable

import numpy as np

from evobyte.constants import (
    TunableProgram,
    evaluate_tunable,
    tune_promoted_candidate,
)
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


def generate_target_splits(
    func: Callable[[np.ndarray], np.ndarray],
    n_points: int = 64,
) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    xs_train = np.linspace(-3.0, 3.0, n_points, dtype=np.float32)
    ys_train = func(xs_train)

    xs_val = np.linspace(-4.0, 4.0, n_points, dtype=np.float32)
    ys_val = func(xs_val)

    xs_hidden = np.linspace(-2.95, 2.95, n_points, dtype=np.float32)
    ys_hidden = func(xs_hidden)

    xs_extrap = np.linspace(3.5, 6.0, n_points, dtype=np.float32)
    ys_extrap = func(xs_extrap)

    return {
        "train": (xs_train, ys_train),
        "val": (xs_val, ys_val),
        "hidden": (xs_hidden, ys_hidden),
        "extrapolation": (xs_extrap, ys_extrap),
    }


TARGET_DEFINITIONS: dict[str, tuple[str, Callable[[np.ndarray], np.ndarray]]] = {
    "quad": (
        "y = 3.14159 x^2 + 0.173 x",
        lambda x: 3.14159265 * x**2 + 0.173 * x,
    ),
    "linear": (
        "y = 3.14159 x + 0.173",
        lambda x: 3.14159265 * x + 0.173,
    ),
}


def run_target_benchmark(
    target_key: str,
    target_name: str,
    func: Callable[[np.ndarray], np.ndarray],
    seeds: list[int],
    pop_size: int = 400,
    max_generations: int = 40,
) -> dict[str, Any]:
    splits = generate_target_splits(func)
    xs_train, ys_train = splits["train"]
    xs_val, ys_val = splits["val"]
    xs_hidden, ys_hidden = splits["hidden"]
    xs_extrap, ys_extrap = splits["extrapolation"]

    print(f"\n================================================================================")
    print(f"Target: {target_name} ({target_key}) | Pop: {pop_size} | Gens: {max_generations} | Seeds: {len(seeds)}")
    print(f"================================================================================")

    records_a = []
    records_b = []

    for s in seeds:
        rng = np.random.default_rng(s)
        cfg = EvolutionConfig(
            pop_size=pop_size,
            max_generations=max_generations,
            gene_mut_p=0.15,
            crossover_p=0.4,
            early_stop_fitness=1e-5,
        )

        # ---------------------------------------------------------
        # Condition A: Bank-only control (fixed CONST_BANK, 0 fit cost)
        # ---------------------------------------------------------
        t0_a = time.perf_counter()
        res_a = run_evolution(xs_train, ys_train, cfg, rng)
        time_a = time.perf_counter() - t0_a

        best_prog_a = res_a["best_program"]
        ev_a_tr = evaluate(best_prog_a, xs_train, ys_train)
        ev_a_val = evaluate(best_prog_a, xs_val, ys_val)
        ev_a_hid = evaluate(best_prog_a, xs_hidden, ys_hidden)
        ev_a_ext = evaluate(best_prog_a, xs_extrap, ys_extrap)

        rec_a = {
            "seed": s,
            "train_mse": ev_a_tr["mse"],
            "val_mse": ev_a_val["mse"],
            "hidden_mse": ev_a_hid["mse"],
            "extrap_mse": ev_a_ext["mse"],
            "time_sec": time_a,
            "fit_steps": 0,
            "fit_time_sec": 0.0,
            "total_time_sec": time_a,
            "optimizer": "none",
            "expression": res_a["best_expression"],
        }
        records_a.append(rec_a)

        # ---------------------------------------------------------
        # Condition B: Fitted (S3/L2 promotion hook: linear head + local search)
        # All fitting time and optimizer steps are billed explicitly!
        # ---------------------------------------------------------
        t0_fit = time.perf_counter()
        tuned = tune_promoted_candidate(best_prog_a, xs_train, ys_train, max_steps=80)
        time_fit = time.perf_counter() - t0_fit

        tunable_prog = tuned["tunable_program"]
        ev_b_tr = evaluate_tunable(tunable_prog, xs_train, ys_train)
        ev_b_val = evaluate_tunable(tunable_prog, xs_val, ys_val)
        ev_b_hid = evaluate_tunable(tunable_prog, xs_hidden, ys_hidden)
        ev_b_ext = evaluate_tunable(tunable_prog, xs_extrap, ys_extrap)

        total_time_b = time_a + time_fit

        rec_b = {
            "seed": s,
            "train_mse": ev_b_tr["mse"],
            "val_mse": ev_b_val["mse"],
            "hidden_mse": ev_b_hid["mse"],
            "extrap_mse": ev_b_ext["mse"],
            "evo_time_sec": time_a,
            "fit_steps": tuned["steps"],
            "fit_time_sec": time_fit,
            "total_time_sec": total_time_b,
            "optimizer": tuned["optimizer"],
            "expression": tuned["expression"],
        }
        records_b.append(rec_b)

        print(
            f"Seed {s:3d} | "
            f"Cond A MSE: {rec_a['train_mse']:.5f} ({rec_a['total_time_sec']:.2f}s) | "
            f"Cond B MSE: {rec_b['train_mse']:.5f} ({rec_b['total_time_sec']:.2f}s, +{time_fit*1000:.0f}ms fit) | "
            f"Opt: {rec_b['optimizer']}"
        )

    # Aggregate summaries
    mean_tr_a = float(np.mean([r["train_mse"] for r in records_a]))
    mean_tr_b = float(np.mean([r["train_mse"] for r in records_b]))

    mean_hid_a = float(np.mean([r["hidden_mse"] for r in records_a]))
    mean_hid_b = float(np.mean([r["hidden_mse"] for r in records_b]))

    mean_ext_a = float(np.mean([r["extrap_mse"] for r in records_a]))
    mean_ext_b = float(np.mean([r["extrap_mse"] for r in records_b]))

    mean_time_a = float(np.mean([r["total_time_sec"] for r in records_a]))
    mean_time_b = float(np.mean([r["total_time_sec"] for r in records_b]))

    mean_fit_time = float(np.mean([r["fit_time_sec"] for r in records_b]))
    mean_fit_steps = float(np.mean([r["fit_steps"] for r in records_b]))

    mse_ratio = mean_tr_a / max(mean_tr_b, 1e-12)

    return {
        "target_key": target_key,
        "target_name": target_name,
        "records_a": records_a,
        "records_b": records_b,
        "mean_tr_a": mean_tr_a,
        "mean_tr_b": mean_tr_b,
        "mean_hid_a": mean_hid_a,
        "mean_hid_b": mean_hid_b,
        "mean_ext_a": mean_ext_a,
        "mean_ext_b": mean_ext_b,
        "mean_time_a": mean_time_a,
        "mean_time_b": mean_time_b,
        "mean_fit_time": mean_fit_time,
        "mean_fit_steps": mean_fit_steps,
        "mse_ratio": mse_ratio,
        "b_wins": mean_tr_b < mean_tr_a,
    }


def run_constants_ab_benchmark(
    seeds: list[int],
    targets: list[str],
    pop_size: int = 400,
    max_generations: int = 40,
) -> tuple[bool, dict[str, Any]]:
    print("================================================================================")
    print("P11 A/B Benchmark: Bank-Only Control vs Fitted Constants Optimization")
    print(f"Targets: {', '.join(targets)} | Seeds: {seeds}")
    print("================================================================================")

    all_results = {}
    all_targets_pass = True

    for t_key in targets:
        t_name, t_func = TARGET_DEFINITIONS[t_key]
        res = run_target_benchmark(
            target_key=t_key,
            target_name=t_name,
            func=t_func,
            seeds=seeds,
            pop_size=pop_size,
            max_generations=max_generations,
        )
        all_results[t_key] = res
        if not res["b_wins"]:
            all_targets_pass = False

    # Print summary A/B table
    print("\n" + "=" * 80)
    print("P11 A/B Benchmark Summary Table")
    print("=" * 80)
    header = (
        f"{'Target':<26} | {'Cond A MSE':<12} | {'Cond B MSE':<12} | "
        f"{'MSE Gain':<10} | {'Time A':<8} | {'Time B (Billed)':<15} | {'Winner':<6}"
    )
    print(header)
    print("-" * len(header))

    for t_key, res in all_results.items():
        winner = "Cond B" if res["b_wins"] else "Cond A"
        gain_str = f"{res['mse_ratio']:.1f}x" if res["mse_ratio"] < 1e5 else ">10000x"
        row = (
            f"{res['target_name']:<26} | {res['mean_tr_a']:<12.5f} | {res['mean_tr_b']:<12.5f} | "
            f"{gain_str:<10} | {res['mean_time_a']:<8.2f}s | {res['mean_time_b']:<15.2f}s | {winner:<6}"
        )
        print(row)

    print("-" * len(header))

    # Detailed per-seed breakdown table
    print("\nDetailed Per-Seed Breakdown (Condition B vs Condition A):")
    print(f"{'Target':<8} | {'Seed':<5} | {'Cond A MSE':<11} | {'Cond B MSE':<11} | {'Fit Steps':<9} | {'Fit Time':<8} | {'Optimizer':<25}")
    print("-" * 88)
    for t_key, res in all_results.items():
        for ra, rb in zip(res["records_a"], res["records_b"]):
            print(
                f"{t_key:<8} | {ra['seed']:<5d} | {ra['train_mse']:<11.5f} | {rb['train_mse']:<11.5f} | "
                f"{rb['fit_steps']:<9d} | {rb['fit_time_sec']*1000:<6.1f}ms | {rb['optimizer']:<25}"
            )
    print("-" * 88)

    print("\n--------------------------------------------------------------------------------")
    print(f"Condition B (Fitted) beats Condition A (Bank-only): {'PASS' if all_targets_pass else 'FAIL'}")
    print(f"P11 Exit Gate: {'PASS' if all_targets_pass else 'FAIL'}")
    print("--------------------------------------------------------------------------------\n")

    return all_targets_pass, all_results


def main() -> int:
    parser = argparse.ArgumentParser(description="P11 Constant Optimization A/B Benchmark")
    parser.add_argument("--seeds", type=int, default=5, help="Number of seeds (default: 5)")
    parser.add_argument(
        "--target",
        type=str,
        default="all",
        choices=["all", "quad", "linear"],
        help="Target to benchmark (default: all)",
    )
    parser.add_argument("--pop-size", type=int, default=400, help="Population size (default: 400)")
    parser.add_argument("--max-generations", type=int, default=40, help="Max generations (default: 40)")
    parser.add_argument("--budget", type=str, default="10min", help="Time budget (default: 10min)")
    args = parser.parse_args()

    default_seeds = [42, 101, 202, 303, 404]
    if args.seeds == 5:
        seeds = default_seeds
    else:
        seeds = [100 + i for i in range(args.seeds)]

    targets = list(TARGET_DEFINITIONS.keys()) if args.target == "all" else [args.target]

    passed, _ = run_constants_ab_benchmark(
        seeds=seeds,
        targets=targets,
        pop_size=args.pop_size,
        max_generations=args.max_generations,
    )
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
