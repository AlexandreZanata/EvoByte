#!/usr/bin/env python3
"""Benchmark runner for Blind Historical Calibration (P205).

Executes blind calibration protocol on three literature milestones:
1. Covering design C(9, 3, 2) = 12 (Affine plane AG(2, 3) over F_9).
2. Steane [[7, 1, 3]] CSS quantum code.
3. Shor [[9, 1, 3]] non-circulant quantum stabilizer code.

All targets evaluated across 5 seeds under 30.0s per-trial budget.
Total calibration time must be < 90 seconds.
Writes output to experiments/p205-calibration-results.json.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import subprocess
import time
from typing import Any

from evobyte.p205_calibration import run_p205_calibration_protocol

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
    parser = argparse.ArgumentParser(description="Run P205 Blind Historical Calibration")
    parser.add_argument(
        "--output",
        type=str,
        default="experiments/p205-calibration-results.json",
        help="Path to output results file",
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

    print("=" * 70)
    print("P205 BLIND HISTORICAL CALIBRATION BENCHMARK")
    print(f"Commit: {commit_sha} | Python: {platform.python_version()} | PySAT: {_PYSAT_VER}")
    print(f"Seeds: {seeds} | Budget per trial: {args.timeout}s")
    print("=" * 70)

    t_start = time.perf_counter()
    calib_results = run_p205_calibration_protocol(
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
    print("TARGET 1: AFFINE COVERING DESIGN C(9, 3, 2) = 12 (AG(2, 3))")
    print("-" * 70)
    cov_trials = calib_results["targets"]["covering_c9_3_2"]["trials"]
    for t_res in cov_trials:
        s = t_res["seed"]
        el = t_res["wall_clock_seconds"]
        v = t_res["verified"]
        b = t_res.get("total_blocks", 0)
        h = t_res.get("sha256", "none")[:16]
        print(f"Seed {s:2d}: verified={v} (b={b}) in {el:.3f}s | SHA: {h}...")

    print("\n" + "=" * 70)
    print("TARGET 2: STEANE [[7, 1, 3]] CSS QUANTUM CODE")
    print("-" * 70)
    steane_trials = calib_results["targets"]["steane_7_1_3"]["trials"]
    for t_res in steane_trials:
        s = t_res["seed"]
        el = t_res["wall_clock_seconds"]
        v = t_res["verified"]
        d = t_res.get("code_distance", 0)
        h = t_res.get("sha256", "none")[:16]
        print(f"Seed {s:2d}: verified={v} (d={d}) in {el:.3f}s | SHA: {h}...")

    print("\n" + "=" * 70)
    print("TARGET 3: SHOR [[9, 1, 3]] NON-CIRCULANT QUANTUM STABILIZER CODE")
    print("-" * 70)
    shor_trials = calib_results["targets"]["shor_9_1_3"]["trials"]
    for t_res in shor_trials:
        s = t_res["seed"]
        el = t_res["wall_clock_seconds"]
        v = t_res["verified"]
        d = t_res.get("code_distance", 0)
        h = t_res.get("sha256", "none")[:16]
        print(f"Seed {s:2d}: verified={v} (d={d}) in {el:.3f}s | SHA: {h}...")

    print("\n" + "=" * 70)
    print(f"CALIBRATION VERDICT: {calib_results['verdict']}")
    print(f"Total Wall Clock: {total_time:.3f}s (< 90.0s requirement)")
    print("=" * 70)

    # Save artifact
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(calib_results, f, indent=2, sort_keys=True)
    print(f"\nSaved calibration results manifest to: {out_path}")


if __name__ == "__main__":
    main()
