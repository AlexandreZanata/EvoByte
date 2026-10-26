#!/usr/bin/env python3
"""Benchmark runner for Hard Historical Records Calibration (P195).

Executes blind calibration protocol on two difficult literature milestones:
1. Gottesman [[8, 3, 3]] stabilizer code.
2. Covering design C(10, 4, 3) = 30 (Mills 1979 / SQS(10)).

Both targets are evaluated across 5 seeds under strict 300-second per-trial budget.
Writes output to experiments/p195-hard-calibration-results.json.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import subprocess
import time
from typing import Any

from evobyte.hard_calibration import run_hard_calibration_protocol

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
    parser = argparse.ArgumentParser(description="Run P195 Hard Historical Records Calibration")
    parser.add_argument(
        "--output",
        type=str,
        default="experiments/p195-hard-calibration-results.json",
        help="Path to output results file",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=300.0,
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

    print("=" * 70)
    print("P195 HARD HISTORICAL RECORDS CALIBRATION BENCHMARK")
    print(f"Commit: {commit_sha} | Python: {platform.python_version()} | PySAT: {_PYSAT_VER}")
    print(f"Seeds: {seeds} | Budget per trial: {args.timeout}s")
    print("=" * 70)

    t_start = time.perf_counter()
    calib_results = run_hard_calibration_protocol(
        seeds=seeds,
        timeout_per_trial=args.timeout,
        solver_name=args.solver,
    )
    total_time = time.perf_counter() - t_start

    calib_results["git_commit"] = commit_sha
    calib_results["hardware"] = {
        "platform": platform.platform(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "pysat_version": _PYSAT_VER,
    }
    calib_results["total_benchmark_time_seconds"] = total_time

    # Print summary
    print("\n" + "=" * 70)
    print("TARGET 1: GOTTESMAN [[8, 3, 3]] QUANTUM STABILIZER CODE")
    print("-" * 70)
    qecc_trials = calib_results["targets"]["qecc_8_3_3"]["trials"]
    for t_res in qecc_trials:
        s = t_res["seed"]
        el = t_res["wall_clock_seconds"]
        v = t_res["verified"]
        d = t_res.get("code_distance", 0)
        h = t_res.get("sha256", "none")[:16]
        print(f"Seed {s:2d}: verified={v} (d={d}) in {el:.3f}s | SHA: {h}...")
    succ_qecc = calib_results["targets"]["qecc_8_3_3"]["successes"]
    print(f"QECC Successes: {succ_qecc}/{len(seeds)}")

    print("\n" + "=" * 70)
    print("TARGET 2: COVERING DESIGN C(10, 4, 3) = 30 (SQS(10))")
    print("-" * 70)
    cov_trials = calib_results["targets"]["covering_c10_4_3"]["trials"]
    for t_res in cov_trials:
        s = t_res["seed"]
        el = t_res["wall_clock_seconds"]
        v = t_res["verified"]
        b = t_res.get("total_blocks", 0)
        h = t_res.get("sha256", "none")[:16]
        print(f"Seed {s:2d}: verified={v} (blocks={b}) in {el * 1000:6.2f} ms | SHA: {h}...")
    succ_cov = calib_results["targets"]["covering_c10_4_3"]["successes"]
    print(f"Covering Design Successes: {succ_cov}/{len(seeds)}")

    verdict = calib_results["verdict"]
    print("\n" + "=" * 70)
    print(f"OVERALL CALIBRATION VERDICT: {verdict}")
    print(f"Total benchmark wall-clock time: {total_time:.3f} seconds")
    print("=" * 70)

    out_p = Path(args.output)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with out_p.open("w", encoding="utf-8") as f:
        json.dump(calib_results, f, indent=2, sort_keys=True)
    print(f"\nSaved structured results to {out_p}")


if __name__ == "__main__":
    main()
