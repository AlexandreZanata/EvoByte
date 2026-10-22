"""Blind rediscovery campaign harness (P165).

Runs the P165 calibration trials over the known literature milestones, under
paired wall-clock budgets, and records per-method statistics.

The harness also performs an independent exhaustive check that each calibration
instance sits exactly at the published optimum (a valid coloring of length n
exists, none of length n+1), so a "rediscovery" is provably the known optimum
and not a weaker or impossible target.
"""

from __future__ import annotations

import argparse
import json
import platform
import statistics
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from evobyte.rediscovery import run_single_calibration_trial
from evobyte.target_catalogue import verify_vanderwaerden_coloring

METHODS = ["RandomSearch", "SimulatedAnnealing", "TabuSearch"]

# (instance_id, n, r, k, published_optimum)
INSTANCES: dict[str, tuple[int, int, int, int]] = {
    "vdw_3_3_26": (26, 3, 3, 27),
    "vdw_2_4_34": (34, 2, 4, 35),
}


def exhaustive_feasible(n: int, r: int, k: int) -> tuple[bool, list[int] | None, int]:
    """Backtracking search for a valid r-coloring of [1..n] with no monochromatic k-AP.

    Returns (satisfiable, certificate, explored_nodes).
    """
    colors = [0] * (n + 1)

    def dfs(p: int) -> bool:
        if p > n:
            return True
        for c in range(1, r + 1):
            ok = True
            for d in range(1, (p - 1) // (k - 1) + 1):
                if p - (k - 1) * d >= 1 and all(
                    colors[p - (k - 1) * d + j * d] == c for j in range(k - 1)
                ):
                    ok = False
                    break
            if ok:
                colors[p] = c
                if dfs(p + 1):
                    return True
                colors[p] = 0
        return False

    found = dfs(1)
    return found, (colors[1:] if found else None), 0


def check_instance_optimum(instance_id: str) -> dict[str, Any]:
    """Independently confirm the instance size is the published optimum."""
    n, r, k, published = INSTANCES[instance_id]
    t0 = time.perf_counter()
    sat, certificate, _ = exhaustive_feasible(n, r, k)
    sat_time = time.perf_counter() - t0
    certified = False
    oracle_message = ""
    if certificate is not None:
        certified, oracle_message = verify_vanderwaerden_coloring(
            np.asarray(certificate, dtype=int), r, k
        )
    t1 = time.perf_counter()
    sat_next, _, _ = exhaustive_feasible(n + 1, r, k)
    next_time = time.perf_counter() - t1
    return {
        "instance_id": instance_id,
        "n": n,
        "colors": r,
        "terms": k,
        "published_optimum": published,
        "feasible_at_n": sat,
        "feasible_at_n_plus_1": sat_next,
        "certificate": certificate,
        "certificate_verified_by_oracle": certified,
        "oracle_message": oracle_message,
        "feasible_search_sec": sat_time,
        "infeasible_search_sec": next_time,
        "matches_published_optimum": bool(sat and not sat_next and published == n + 1),
    }


def run_campaign(
    instances: list[str], budgets: list[float], seeds: list[int]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    trials: list[dict[str, Any]] = []
    for seconds in budgets:
        for instance_id in instances:
            for method in METHODS:
                for seed in seeds:
                    trial = run_single_calibration_trial(instance_id, method, seconds, seed)
                    trials.append(
                        {
                            "budget_sec": seconds,
                            "instance_id": trial.instance_id,
                            "method": trial.method,
                            "seed": trial.seed,
                            "success": trial.success,
                            "time_to_hit_sec": trial.time_to_hit_sec,
                            "total_evals": trial.total_evals,
                            "elapsed_sec": trial.elapsed_sec,
                            "evals_per_sec": trial.total_evals / max(trial.elapsed_sec, 1e-9),
                        }
                    )
    return trials, summarize(trials)


def summarize(trials: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for trial in trials:
        key = f"{trial['budget_sec']}s|{trial['instance_id']}|{trial['method']}"
        entry = summary.setdefault(
            key,
            {
                "budget_sec": trial["budget_sec"],
                "instance_id": trial["instance_id"],
                "method": trial["method"],
                "runs": 0,
                "hits": 0,
                "success_rate": 0.0,
                "mean_time_to_hit_sec": None,
                "median_time_to_hit_sec": None,
                "mean_total_evals": 0.0,
                "mean_elapsed_sec": 0.0,
                "mean_evals_per_sec": 0.0,
            },
        )
        entry["runs"] += 1
        entry["hits"] += int(trial["success"])
        entry["mean_total_evals"] += trial["total_evals"]
        entry["mean_elapsed_sec"] += trial["elapsed_sec"]
        entry["mean_evals_per_sec"] += trial["evals_per_sec"]
        if trial["success"] and trial["time_to_hit_sec"] is not None:
            entry.setdefault("_hits", []).append(trial["time_to_hit_sec"])
    for entry in summary.values():
        entry["success_rate"] = entry["hits"] / max(1, entry["runs"])
        entry["mean_total_evals"] /= max(1, entry["runs"])
        entry["mean_elapsed_sec"] /= max(1, entry["runs"])
        entry["mean_evals_per_sec"] /= max(1, entry["runs"])
        hits = entry.pop("_hits", [])
        if hits:
            entry["mean_time_to_hit_sec"] = statistics.fmean(hits)
            entry["median_time_to_hit_sec"] = statistics.median(hits)
    return summary


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instances", required=True)
    parser.add_argument("--seconds", required=True, help="comma-separated wall-clock budgets")
    parser.add_argument("--seeds", required=True, help="comma-separated seed list")
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv[1:])

    instances = [s.strip() for s in args.instances.split(",") if s.strip()]
    budgets = [float(s) for s in args.seconds.split(",") if s.strip()]
    seeds = [int(s) for s in args.seeds.split(",") if s.strip()]
    unknown = [i for i in instances if i not in INSTANCES]
    if unknown:
        raise ValueError(f"unknown instances {unknown}; known: {sorted(INSTANCES)}")
    if not budgets or not seeds:
        raise ValueError("--seconds and --seeds must not be empty")

    started = time.perf_counter()
    optima = [check_instance_optimum(i) for i in instances]
    trials, summary = run_campaign(instances, budgets, seeds)
    elapsed = time.perf_counter() - started

    payload = {
        "phase": "P165",
        "suite": "blind-rediscovery-calibration",
        "instances": instances,
        "budgets_sec": budgets,
        "seeds": seeds,
        "methods": METHODS,
        "timer": "time.perf_counter()",
        "elapsed_sec": elapsed,
        "hardware": {
            "cpu": platform.machine(),
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
        "instance_optimum_checks": optima,
        "trials": trials,
        "summary": summary,
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {out_path} ({len(trials)} trials)")
    for key, entry in summary.items():
        print(
            f"  {key}: hits={entry['hits']}/{entry['runs']} "
            f"mean_t_hit={entry['mean_time_to_hit_sec']} "
            f"mean_evals={entry['mean_total_evals']:.0f} "
            f"evals/s={entry['mean_evals_per_sec']:.0f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
