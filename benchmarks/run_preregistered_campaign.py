"""Preregistered record campaign executor (P166).

The campaign is entirely driven by `experiments/p166-campaign-manifest.json`:
targets, search-space parameters, sizes, budget, seeds and algorithms are read
from the manifest, never hardcoded here. That is what makes the pre-registration
verifiable: the frozen file fixes the goal and the win criterion before any run.

Every trial:
- runs the selected algorithm under a strict wall-clock budget,
- submits the best candidate to the independent verifier of `evobyte.target_catalogue`,
- aborts the campaign if the local search and the independent verifier disagree,
- aborts the campaign if a trial overshoots the budget beyond the frozen factor.

The output is `summary.json` with every raw trial, the per-target verdicts and a
SHA-256 chain of custody (manifest, catalogue, each certified candidate, and the
summary payload itself).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
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
    verify_schur_partition,
    verify_vanderwaerden_coloring,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


class CampaignIntegrityError(RuntimeError):
    """Raised when the campaign violates the frozen integrity rule."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def sha256_json(payload: Any) -> str:
    return sha256_bytes(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8"))


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


def build_space(params: dict[str, Any], size: int) -> dict[str, Any]:
    """Build the sampling / neighbourhood / evaluation interface for one target size."""
    kind = params["kind"]
    if kind == "vanderwaerden":
        colors = int(params["colors"])
        terms = int(params["terms"])

        def sample(rng: np.random.Generator) -> np.ndarray:
            return rng.integers(1, colors + 1, size=size)

        def neighbor(current: np.ndarray, rng: np.random.Generator) -> np.ndarray:
            out = current.copy()
            idx = int(rng.integers(0, size))
            choices = [c for c in range(1, colors + 1) if c != int(current[idx])]
            out[idx] = int(rng.choice(choices))
            return out

        def neighbors(
            current: np.ndarray, rng: np.random.Generator, k_sample: int
        ) -> list[tuple[np.ndarray, str]]:
            out = []
            for _ in range(k_sample):
                idx = int(rng.integers(0, size))
                choices = [c for c in range(1, colors + 1) if c != int(current[idx])]
                new_c = int(rng.choice(choices))
                cand = current.copy()
                cand[idx] = new_c
                out.append((cand, f"{idx}:{new_c}"))
            return out

        def evaluate(candidate: np.ndarray) -> tuple[float, bool]:
            bad = count_mono_progression_aps(candidate, terms)
            return -float(bad), bad == 0

        def certify(candidate: np.ndarray) -> tuple[bool, str]:
            return verify_vanderwaerden_coloring(candidate, colors, terms)

        return {
            "sample": sample,
            "neighbor": neighbor,
            "neighbors": neighbors,
            "evaluate": evaluate,
            "certify": certify,
        }

    if kind == "schur":
        classes = int(params["classes"])

        def sample(rng: np.random.Generator) -> np.ndarray:
            return rng.integers(1, classes + 1, size=size)

        def neighbor(current: np.ndarray, rng: np.random.Generator) -> np.ndarray:
            out = current.copy()
            idx = int(rng.integers(0, size))
            choices = [c for c in range(1, classes + 1) if c != int(current[idx])]
            out[idx] = int(rng.choice(choices))
            return out

        def neighbors(
            current: np.ndarray, rng: np.random.Generator, k_sample: int
        ) -> list[tuple[np.ndarray, str]]:
            out = []
            for _ in range(k_sample):
                idx = int(rng.integers(0, size))
                choices = [c for c in range(1, classes + 1) if c != int(current[idx])]
                new_c = int(rng.choice(choices))
                cand = current.copy()
                cand[idx] = new_c
                out.append((cand, f"{idx}:{new_c}"))
            return out

        def evaluate(candidate: np.ndarray) -> tuple[float, bool]:
            bad = count_sum_free_violations(candidate, classes)
            return -float(bad), bad == 0

        def certify(candidate: np.ndarray) -> tuple[bool, str]:
            return verify_schur_partition(candidate, classes)

        return {
            "sample": sample,
            "neighbor": neighbor,
            "neighbors": neighbors,
            "evaluate": evaluate,
            "certify": certify,
        }

    raise ValueError(f"unknown target kind {kind!r}")


def run_algorithm(
    algorithm: str, space: dict[str, Any], target_id: str, seconds: float, seed: int
) -> Any:
    if algorithm == "SimulatedAnnealing":
        return run_simulated_annealing(
            target_id,
            space["sample"],
            space["neighbor"],
            space["evaluate"],
            seconds,
            seed=seed,
        )
    if algorithm == "TabuSearch":
        return run_tabu_search(
            target_id,
            space["sample"],
            space["neighbors"],
            space["evaluate"],
            seconds,
            seed=seed,
        )
    if algorithm == "RandomSearch":
        return run_random_search(target_id, space["sample"], space["evaluate"], seconds, seed=seed)
    raise ValueError(f"unknown algorithm {algorithm!r}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args(argv[1:])

    manifest_path = Path(args.manifest)
    manifest_raw = manifest_path.read_bytes()
    manifest = json.loads(manifest_raw.decode("utf-8"))
    manifest_sha = sha256_bytes(manifest_raw)

    catalogue_path = REPO_ROOT / manifest["integrity_rule"]["catalogue_path"]
    catalogue_sha = sha256_file(catalogue_path)
    if catalogue_sha != manifest["integrity_rule"]["catalogue_sha256"]:
        raise CampaignIntegrityError(
            "catalogue hash mismatch: manifest freezes "
            f"{manifest['integrity_rule']['catalogue_sha256']} but the file is {catalogue_sha}"
        )

    max_overshoot = float(manifest["integrity_rule"]["max_overshoot_factor"])
    budget = float(manifest["budget_sec_per_seed"])
    seeds = [int(s) for s in manifest["seeds"]]
    algorithms = list(manifest["algorithms"])
    targets = list(manifest["targets"])

    started_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    campaign_started = time.perf_counter()
    trials: list[dict[str, Any]] = []

    for target_id in targets:
        params = manifest["target_parameters"][target_id]
        published_bound = float(params["published_bound"])
        sizes = {"tie": int(published_bound), "beat": int(published_bound) + 1}
        for size_kind, size in sizes.items():
            space = build_space(params, size)
            for algorithm in algorithms:
                for seed in seeds:
                    result = run_algorithm(algorithm, space, target_id, budget, seed)
                    candidate = np.asarray(result.best_candidate, dtype=int)
                    certified, message = space["certify"](candidate)
                    local_solved = candidate.size > 0 and space["evaluate"](candidate)[1]
                    if local_solved != certified:
                        raise CampaignIntegrityError(
                            f"local search and independent verifier disagree on {target_id} "
                            f"({size_kind}, {algorithm}, seed {seed})"
                        )
                    elapsed = float(result.elapsed_sec)
                    if elapsed > max_overshoot * budget:
                        raise CampaignIntegrityError(
                            f"trial overshoot: {target_id} {size_kind} {algorithm} seed {seed} "
                            f"took {elapsed:.3f}s against a {budget}s budget"
                        )
                    trials.append(
                        {
                            "target_id": target_id,
                            "size_kind": size_kind,
                            "size": size,
                            "published_bound": published_bound,
                            "algorithm": algorithm,
                            "seed": seed,
                            "budget_sec": budget,
                            "evaluations": int(result.evaluations),
                            "elapsed_sec": elapsed,
                            "best_score": float(result.best_score),
                            "violations": int(-result.best_score),
                            "is_solution": bool(result.is_solution),
                            "oracle_certified": bool(certified),
                            "oracle_message": message,
                            "candidate_sha256": sha256_json(candidate.tolist()),
                        }
                    )

    verdicts: dict[str, Any] = {}
    for target_id in targets:
        rows = [t for t in trials if t["target_id"] == target_id]
        beats = [t for t in rows if t["size_kind"] == "beat" and t["oracle_certified"]]
        ties = [t for t in rows if t["size_kind"] == "tie" and t["oracle_certified"]]
        if beats:
            verdict = "DISCOVERY_BEATEN"
            best = min(beats, key=lambda t: t["elapsed_sec"])
        elif ties:
            verdict = "DISCOVERY_TIED"
            best = min(ties, key=lambda t: t["elapsed_sec"])
        else:
            verdict = "NULL_RESULT"
            best = None
        published_bound = float(manifest["target_parameters"][target_id]["published_bound"])
        verdicts[target_id] = {
            "verdict": verdict,
            "published_bound": published_bound,
            "published_reference": manifest["target_parameters"][target_id]["reference"],
            "trials": len(rows),
            "beat_trials": sum(1 for t in rows if t["size_kind"] == "beat"),
            "tie_trials": sum(1 for t in rows if t["size_kind"] == "tie"),
            "certified_beat_trials": len(beats),
            "certified_tie_trials": len(ties),
            "best_violations_beat": min(
                (t["violations"] for t in rows if t["size_kind"] == "beat"), default=None
            ),
            "best_violations_tie": min(
                (t["violations"] for t in rows if t["size_kind"] == "tie"), default=None
            ),
            "total_evaluations": sum(t["evaluations"] for t in rows),
            "total_elapsed_sec": sum(t["elapsed_sec"] for t in rows),
            "witness": best,
        }

    total_evaluations = sum(t["evaluations"] for t in trials)
    total_elapsed = sum(t["elapsed_sec"] for t in trials)
    payload: dict[str, Any] = {
        "phase": "P166",
        "campaign_id": manifest["campaign_id"],
        "manifest_version": manifest["manifest_version"],
        "manifest_sha256": manifest_sha,
        "catalogue_sha256": catalogue_sha,
        "started_at": started_at,
        "finished_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "wall_clock_sec": time.perf_counter() - campaign_started,
        "budget_sec_per_seed": budget,
        "seeds": seeds,
        "algorithms": algorithms,
        "targets": targets,
        "excluded_targets": manifest["excluded_targets"],
        "verdict_rule": manifest["verdict_rule"],
        "hardware": {
            "cpu": platform.machine(),
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
        "totals": {
            "trials": len(trials),
            "total_evaluations": total_evaluations,
            "total_elapsed_sec": total_elapsed,
            "max_elapsed_sec": max((t["elapsed_sec"] for t in trials), default=0.0),
        },
        "verdicts": verdicts,
        "trials": trials,
    }
    payload["summary_sha256"] = sha256_json(payload)

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "summary.json"
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"wrote {out_path} ({len(trials)} trials, {total_evaluations} evaluations)")
    for target_id, entry in verdicts.items():
        print(
            f"  {target_id}: {entry['verdict']} "
            f"(beat certified {entry['certified_beat_trials']}/{entry['beat_trials']}, "
            f"tie certified {entry['certified_tie_trials']}/{entry['tie_trials']}, "
            f"best violations beat={entry['best_violations_beat']} tie={entry['best_violations_tie']})"
        )
    print(f"  summary_sha256={payload['summary_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
