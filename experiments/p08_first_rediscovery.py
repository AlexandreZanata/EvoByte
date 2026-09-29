"""Experiment script for P08: First blind rediscovery of y = x^2 + 3x + 7 across 5 seeds."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

from evobyte.archive import write_hall_of_fame_entry
from evobyte.bytecode import decode_human
from evobyte.evolution import EvolutionConfig, run_evolution
from evobyte.verifier import evaluate


def parse_budget(budget_str: str) -> float:
    """Parse budget string into seconds (e.g. '1h' -> 3600.0, '600s' -> 600.0)."""
    s = budget_str.strip().lower()
    if s.endswith("h"):
        return float(s[:-1]) * 3600.0
    if s.endswith("m"):
        return float(s[:-1]) * 60.0
    if s.endswith("s"):
        return float(s[:-1])
    return float(s)


def generate_target_splits(n_points: int = 64) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """Generate train, val, hidden, and extrapolation splits for y = x^2 + 3x + 7."""
    # Target 1: y = x^2 + 3x + 7
    def f(x: np.ndarray) -> np.ndarray:
        return x * x + 3.0 * x + 7.0

    xs_train = np.linspace(-5.0, 5.0, n_points, dtype=np.float32)
    ys_train = f(xs_train)

    xs_val = np.linspace(-7.0, 7.0, n_points, dtype=np.float32)
    ys_val = f(xs_val)

    # Hidden in-domain evaluation points (disjoint grid)
    xs_hidden = np.linspace(-4.95, 4.95, n_points, dtype=np.float32)
    ys_hidden = f(xs_hidden)

    # Extrapolation out-of-domain evaluation points
    xs_extrap = np.linspace(6.0, 12.0, n_points, dtype=np.float32)
    ys_extrap = f(xs_extrap)

    return {
        "train": (xs_train, ys_train),
        "val": (xs_val, ys_val),
        "hidden": (xs_hidden, ys_hidden),
        "extrapolation": (xs_extrap, ys_extrap),
    }


def run_rediscovery_benchmark(
    seeds: list[int],
    budget_sec: float = 3600.0,
    pop_size: int = 1000,
    max_generations: int = 100,
    tolerance: float = 1e-3,
    fame_path: str | Path | None = "hall_of_fame/fame.jsonl",
) -> tuple[bool, list[dict[str, Any]]]:
    splits = generate_target_splits()
    xs_train, ys_train = splits["train"]
    xs_val, ys_val = splits["val"]
    xs_hidden, ys_hidden = splits["hidden"]
    xs_extrap, ys_extrap = splits["extrapolation"]

    results = []
    successes = 0
    t_start_total = time.perf_counter()

    print("================================================================================")
    print(f"P08 MVP Rediscovery Gate: y = x^2 + 3x + 7 ({len(seeds)} seeds, pop={pop_size}, budget={budget_sec:.0f}s)")
    print("================================================================================")

    for i, s in enumerate(seeds, 1):
        if time.perf_counter() - t_start_total >= budget_sec:
            print(f"Budget of {budget_sec:.0f}s exhausted before seed {s}.")
            break

        rng = np.random.default_rng(s)
        config = EvolutionConfig(
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
            complexity_weight=0.001,
        )

        res = run_evolution(xs_train, ys_train, config, rng, xs_val=xs_val, ys_val=ys_val)
        best_p = res["best_program"]

        ev_train = evaluate(best_p, xs_train, ys_train)
        ev_val = evaluate(best_p, xs_val, ys_val)
        ev_hidden = evaluate(best_p, xs_hidden, ys_hidden)
        ev_extrap = evaluate(best_p, xs_extrap, ys_extrap)

        is_success = (ev_hidden["mse"] <= tolerance) and (ev_extrap["mse"] <= tolerance)
        if is_success:
            successes += 1

        active_instructions = sum((int(w) & 0xFF) != 0 for w in best_p)
        expr_str = decode_human(best_p)

        record = {
            "seed": s,
            "success": is_success,
            "generations": res["generations"],
            "time_sec": res["time_sec"],
            "candidates": res["candidates_total"],
            "cvps": res["cvps"],
            "train_mse": ev_train["mse"],
            "val_mse": ev_val["mse"],
            "hidden_mse": ev_hidden["mse"],
            "extrap_mse": ev_extrap["mse"],
            "size": active_instructions,
            "expression": expr_str,
            "program": best_p,
        }
        results.append(record)

        status_str = "SUCCESS" if is_success else "FAIL"
        print(
            f"[{i}/{len(seeds)}] Seed {s:4d} -> {status_str:7s} | Gen: {res['generations']:3d} | "
            f"Time: {res['time_sec']:5.1f}s | CVPS: {res['cvps']:6.1f} | "
            f"Hidden MSE: {ev_hidden['mse']:.2e} | Extrap MSE: {ev_extrap['mse']:.2e}"
        )

        # Write top discovery to Hall of Fame if non-memorizer
        if is_success and fame_path is not None:
            fame_entry = {
                "rank": 1,
                "fitness": float(res["best_fitness"]),
                "expression": expr_str,
                "generation": res["generations"],
                "discovered_after_N_candidates": res["candidates_total"],
                "train_error": float(ev_train["mse"]),
                "validation_error": float(ev_val["mse"]),
                "val_gap": float(max(0.0, ev_val["mse"] - ev_train["mse"])),
                "extrapolation_error": float(ev_extrap["mse"]),
                "complexity": float(active_instructions),
                "parents": ["seed_" + str(s)],
                "hash": str(hash(expr_str) & 0xFFFFFFFFFFFFFFFF),
                "reproduction_cmd": f"python3 experiments/p08_first_rediscovery.py --seeds {s}",
            }
            write_hall_of_fame_entry(fame_path, fame_entry)

    # Print markdown table
    print("\n### Rediscovery Results Table\n")
    print("| Seed | Status | Gen | Time (s) | Candidates | CVPS | Train MSE | Hidden MSE | Extrap MSE | Size | Expression |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in results:
        stat = "**SUCCESS**" if r["success"] else "FAIL"
        expr_short = (r["expression"][:40] + "...") if len(r["expression"]) > 40 else r["expression"]
        print(
            f"| {r['seed']} | {stat} | {r['generations']} | {r['time_sec']:.1f} | "
            f"{r['candidates']} | {r['cvps']:.1f} | {r['train_mse']:.2e} | "
            f"{r['hidden_mse']:.2e} | {r['extrap_mse']:.2e} | {r['size']} | `{expr_short}` |"
        )

    success_rate = successes / len(seeds) if seeds else 0.0
    passed_gate = successes >= 3 and len(seeds) >= 5
    print("\n--------------------------------------------------------------------------------")
    print(f"Total Successes: {successes}/{len(seeds)} ({success_rate * 100:.1f}%)")
    print(f"MVP Gate Threshold: >= 3/5 within budget -> {'PASS' if passed_gate else 'FAIL'}")
    print("--------------------------------------------------------------------------------\n")

    return passed_gate, results


def main() -> int:
    parser = argparse.ArgumentParser(description="P08 First Blind Rediscovery Experiment")
    parser.add_argument("--seeds", type=int, default=5, help="Number of seeds to run (default: 5)")
    parser.add_argument("--budget", type=str, default="1h", help="Time budget (default: 1h)")
    parser.add_argument("--pop-size", type=int, default=1000, help="Population size (default: 1000)")
    parser.add_argument("--max-generations", type=int, default=100, help="Max generations (default: 100)")
    args = parser.parse_args()

    default_seed_list = [42, 101, 202, 303, 404]
    if args.seeds == 5:
        seeds = default_seed_list
    else:
        seeds = [100 + i for i in range(args.seeds)]

    budget_sec = parse_budget(args.budget)
    passed, _ = run_rediscovery_benchmark(
        seeds=seeds,
        budget_sec=budget_sec,
        pop_size=args.pop_size,
        max_generations=args.max_generations,
    )
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
