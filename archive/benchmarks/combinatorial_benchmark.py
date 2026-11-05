"""Honest combinatorial baseline benchmark (P164).

Runs the fully-implemented baselines of `evobyte.combinatorial_baselines` against
a pre-registered target of the P163 catalogue, under strict paired wall-clock
budgets, and certifies the best candidate with the independent P163 verifier.

No execution is simulated: every method evaluates real candidates under
`time.perf_counter()`.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from evobyte.combinatorial_baselines import (
    run_random_search,
    run_simulated_annealing,
    run_tabu_search,
)
from evobyte.target_catalogue import (
    load_catalogue,
    verify_schur_partition,
    verify_vanderwaerden_coloring,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CATALOGUE_PATH = REPO_ROOT / "docs" / "research" / "targets" / "open_targets.json"


@dataclass(frozen=True)
class CombinatorialTarget:
    """Search space derived from a pre-registered catalogue target."""

    target_id: str
    kind: str  # "vanderwaerden" | "schur"
    size: int  # number of positions (N)
    classes: int  # colors r or partition classes k
    terms: int  # length k of the arithmetic progression (van der Waerden only)

    def sample(self, rng: np.random.Generator) -> np.ndarray:
        return rng.integers(1, self.classes + 1, size=self.size)

    def neighbor(self, current: np.ndarray, rng: np.random.Generator) -> np.ndarray:
        candidate = current.copy()
        pos = int(rng.integers(0, self.size))
        candidate[pos] = int(rng.integers(1, self.classes + 1))
        return candidate

    def neighbors(
        self, current: np.ndarray, rng: np.random.Generator, k: int
    ) -> list[tuple[np.ndarray, str]]:
        out: list[tuple[np.ndarray, str]] = []
        for _ in range(k):
            pos = int(rng.integers(0, self.size))
            new_color = int(rng.integers(1, self.classes + 1))
            candidate = current.copy()
            candidate[pos] = new_color
            out.append((candidate, f"pos={pos}:{int(current[pos])}->{new_color}"))
        return out

    def violations(self, candidate: np.ndarray) -> int:
        if self.kind == "vanderwaerden":
            return count_mono_progression_aps(candidate, self.terms)
        return count_sum_free_violations(candidate, self.classes)

    def evaluate(self, candidate: np.ndarray) -> tuple[float, bool]:
        bad = self.violations(candidate)
        return -float(bad), bad == 0

    def certify(self, candidate: np.ndarray) -> tuple[bool, str]:
        if self.kind == "vanderwaerden":
            return verify_vanderwaerden_coloring(candidate, self.classes, self.terms)
        return verify_schur_partition(candidate, self.classes)


def count_mono_progression_aps(coloring: np.ndarray, terms: int) -> int:
    """Count monochromatic arithmetic progressions of length `terms` (vectorized)."""
    col = np.asarray(coloring, dtype=int)
    n = len(col)
    if terms < 2 or n < terms:
        return 0
    total = 0
    max_d = (n - 1) // (terms - 1)
    for d in range(1, max_d + 1):
        span = n - (terms - 1) * d
        if span <= 0:
            continue
        window = np.ones(span, dtype=bool)
        for i in range(1, terms):
            window &= col[i * d : i * d + span] == col[:span]
        total += int(np.count_nonzero(window))
    return total


def count_sum_free_violations(coloring: np.ndarray, classes: int) -> int:
    """Count monochromatic Schur triples x + y = z inside each class."""
    col = np.asarray(coloring, dtype=int)
    total = 0
    for c in range(1, classes + 1):
        elements = np.flatnonzero(col == c) + 1
        if elements.size < 2:
            continue
        sums = elements[:, None] + elements[None, :]
        total += int(np.count_nonzero(np.isin(sums, elements)))
    return total


def build_target(target_id: str) -> CombinatorialTarget:
    """Map a catalogue target id to its concrete search space."""
    specs = {spec.target_id: spec for spec in load_catalogue(CATALOGUE_PATH)}
    if target_id not in specs:
        raise ValueError(f"unknown target {target_id!r}; catalogue has {sorted(specs)}")
    spec = specs[target_id]
    size = int(spec.published_bound) + 1
    if target_id.startswith("vanderwaerden"):
        terms = 3 if target_id.endswith("w3_3") else 6
        classes = 3 if target_id.endswith("w3_3") else 2
        return CombinatorialTarget(target_id, "vanderwaerden", size, classes, terms)
    if target_id.startswith("schur"):
        return CombinatorialTarget(target_id, "schur", size, 5, 0)
    raise ValueError(f"target {target_id!r} has no combinatorial search space in this benchmark")


def run_target(
    target: CombinatorialTarget, seconds: float, seeds: list[int]
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for seed in seeds:
        random_result = run_random_search(
            target_id=target.target_id,
            sampler_fn=target.sample,
            eval_fn=target.evaluate,
            max_seconds=seconds,
            seed=seed,
        )
        sa_result = run_simulated_annealing(
            target_id=target.target_id,
            init_fn=target.sample,
            neighbor_fn=target.neighbor,
            eval_fn=target.evaluate,
            max_seconds=seconds,
            seed=seed,
        )
        tabu_result = run_tabu_search(
            target_id=target.target_id,
            init_fn=target.sample,
            neighbors_fn=target.neighbors,
            eval_fn=target.evaluate,
            max_seconds=seconds,
            seed=seed,
        )
        for result in (random_result, sa_result, tabu_result):
            candidate = np.asarray(result.best_candidate, dtype=int)
            certified, message = target.certify(candidate)
            rows.append(
                {
                    "method": result.method,
                    "target_id": result.target_id,
                    "seed": result.seed,
                    "evaluations": result.evaluations,
                    "elapsed_sec": result.elapsed_sec,
                    "best_score": result.best_score,
                    "violations": target.violations(candidate),
                    "is_solution": result.is_solution,
                    "oracle_certified": certified,
                    "oracle_message": message,
                    "best_candidate": candidate.tolist(),
                }
            )
    return rows


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for row in rows:
        entry = summary.setdefault(
            row["method"],
            {
                "runs": 0,
                "total_evaluations": 0,
                "mean_elapsed_sec": 0.0,
                "max_elapsed_sec": 0.0,
                "solved_runs": 0,
                "certified_runs": 0,
                "best_violations": None,
            },
        )
        entry["runs"] += 1
        entry["total_evaluations"] += row["evaluations"]
        entry["mean_elapsed_sec"] += row["elapsed_sec"]
        entry["max_elapsed_sec"] = max(entry["max_elapsed_sec"], row["elapsed_sec"])
        entry["solved_runs"] += int(row["is_solution"])
        entry["certified_runs"] += int(row["oracle_certified"])
        if entry["best_violations"] is None or row["violations"] < entry["best_violations"]:
            entry["best_violations"] = row["violations"]
    for entry in summary.values():
        entry["mean_elapsed_sec"] = entry["mean_elapsed_sec"] / max(1, entry["runs"])
    return summary


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-id", required=True)
    parser.add_argument("--seconds", type=float, default=0.5)
    parser.add_argument("--seeds", required=True, help="comma-separated seed list")
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv[1:])

    seeds = [int(s) for s in args.seeds.split(",") if s.strip()]
    if not seeds:
        raise ValueError("--seeds must list at least one seed")

    target = build_target(args.target_id)
    started = time.perf_counter()
    rows = run_target(target, args.seconds, seeds)
    elapsed = time.perf_counter() - started

    payload = {
        "phase": "P164",
        "suite": "honest-combinatorial-baselines",
        "target_id": target.target_id,
        "search_space": {
            "kind": target.kind,
            "size": target.size,
            "classes": target.classes,
            "terms": target.terms,
        },
        "seconds_per_run": args.seconds,
        "seeds": seeds,
        "methods": ["RandomSearch", "SimulatedAnnealing", "TabuSearch"],
        "timer": "time.perf_counter()",
        "elapsed_sec": elapsed,
        "hardware": {
            "cpu": platform.machine(),
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
        "results": rows,
        "summary": summarize(rows),
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {out_path} ({len(rows)} runs)")
    for method, entry in payload["summary"].items():
        print(
            f"  {method}: evaluations={entry['total_evaluations']} "
            f"max_elapsed={entry['max_elapsed_sec']:.3f}s best_violations={entry['best_violations']} "
            f"certified={entry['certified_runs']}/{entry['runs']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
