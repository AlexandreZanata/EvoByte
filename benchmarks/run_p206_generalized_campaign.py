#!/usr/bin/env python3
"""Benchmark runner for Preregistered Generalized Symmetry Campaign (P206).

Executes the campaign defined across the 5 narrow-gap frontier targets
frozen in P201:
1. qecc_14_3_noncirculant: [[14, 3, d]] non-circulant CSS quantum code.
2. qecc_16_5_noncirculant: [[16, 5, d]] non-circulant CSS quantum code.
3. qecc_18_3_noncirculant: [[18, 3, d]] non-circulant CSS quantum code.
4. covering_C_13_5_3_affine: C(13, 5, 3) under AGL(1, 13).
5. covering_C_15_10_4_affine: C(15, 10, 4) under D_15.

Evaluates 5 pseudo-random seeds per target (25 total trials).
Saves structured results to experiments/p206-generalized-campaign-results.json
and incremental checkpoints to experiments/p206-generalized-campaign-checkpoint.json.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import subprocess
import time
from typing import Any

from evobyte.generalized_campaign import run_generalized_campaign

try:
    import pysat

    _PYSAT_VER = pysat.__version__
except ImportError:
    _PYSAT_VER = None


def get_git_commit() -> str:
    """Retrieve current git commit HEAD hash."""
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
        return out.decode().strip()
    except Exception:
        return "unknown"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run P206 Preregistered Generalized Campaign")
    parser.add_argument(
        "--output",
        type=str,
        default="experiments/p206-generalized-campaign-results.json",
        help="Path to output results file",
    )
    parser.add_argument(
        "--checkpoint",
        type=str,
        default="experiments/p206-generalized-campaign-checkpoint.json",
        help="Path to checkpoint file",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Per-trial timeout limit in seconds",
    )
    parser.add_argument(
        "--solver",
        type=str,
        default="cadical153",
        help="Solver backend to use",
    )
    args = parser.parse_args()

    commit_sha = get_git_commit()
    seeds = [42, 43, 44, 45, 46]

    print("=" * 75)
    print("P206 PREREGISTERED GENERALIZED SYMMETRY CAMPAIGN BENCHMARK")
    print(f"Commit: {commit_sha} | Python: {platform.python_version()} | PySAT: {_PYSAT_VER}")
    print(f"Seeds: {seeds} | Budget per trial: {args.timeout}s")
    print("=" * 75)

    t_start = time.perf_counter()
    campaign_results = run_generalized_campaign(
        seeds=seeds,
        timeout_per_trial=args.timeout,
        solver_name=args.solver,
        checkpoint_path=args.checkpoint,
    )
    total_time = time.perf_counter() - t_start

    campaign_results["git_commit"] = commit_sha
    campaign_results["hardware"] = {
        "platform": platform.platform(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "pysat_version": _PYSAT_VER,
    }
    campaign_results["total_benchmark_time_seconds"] = total_time

    # Print summary tables
    for tid, target_data in campaign_results["targets"].items():
        print("\n" + "=" * 75)
        print(f"TARGET: {tid} ({target_data['name']})")
        print(f"Family: {target_data['family']} | Published Best: {target_data['published_best']}")
        print("-" * 75)
        for t_res in target_data["trials"]:
            s = t_res["seed"]
            verdict = t_res["verdict"]
            achieved = t_res.get("achieved_value")
            el = t_res["wall_clock_seconds"]
            sha = t_res.get("candidate_sha256", "none")[:16]
            print(
                f"Seed {s:2d}: verdict={verdict:<15} achieved={str(achieved):<5} in {el:.3f}s | SHA: {sha}..."
            )

    print("\n" + "=" * 75)
    print(f"CAMPAIGN OVERALL VERDICT: {campaign_results['verdict']}")
    print(f"Verdict Counts: {campaign_results['verdict_counts']}")
    print(f"Total Wall Clock: {total_time:.3f}s")
    print("=" * 75)

    # Save artifact
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(campaign_results, f, indent=2, sort_keys=True)
    print(f"\nSaved campaign results manifest to: {out_path}")


if __name__ == "__main__":
    main()
