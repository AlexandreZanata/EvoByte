#!/usr/bin/env python3
"""Stabilizer search benchmark protocol using Q-Forge evolution (P181).

Runs evolutionary search on target QECC stabilizer codes under fixed dual budgets
(time and evaluations) per seed, validating every candidate strictly with P179.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
from typing import Any

import numpy as np

from evobyte.qecc_verifier import check_stabilizer, code_distance
from evobyte.quantum.evolution_q import tournament_select
from evobyte.stabilizer_search import (
    candidate_to_strings,
    crossover_stabilizer_sets,
    fitness_stabilizer_set,
    mutate_stabilizer_set,
    random_stabilizer_set,
    repair_commutation,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
CAT_PATH = REPO_ROOT / "docs" / "research" / "targets" / "qecc_frontier_v1.json"


def load_target(target_id: str) -> dict[str, Any]:
    """Load target specification from QECC Frontier Catalogue."""
    if not CAT_PATH.exists():
        raise FileNotFoundError(f"Catalogue not found at {CAT_PATH}")
    with CAT_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    for t in data.get("targets", []):
        if t["target_id"] == target_id:
            return t
    raise ValueError(f"Target '{target_id}' not found in {CAT_PATH}")


def run_single_seed_search(
    n: int,
    k: int,
    best_known: int,
    seed: int,
    seconds_limit: float,
    evals_limit: int = 500,
    pop_size: int = 20,
) -> dict[str, Any]:
    """Execute evolutionary search on one seed under dual budget."""
    t0 = time.perf_counter()
    rng = np.random.default_rng(seed)

    # Initialize population
    population: list[np.ndarray] = [random_stabilizer_set(n, k, rng) for _ in range(pop_size)]
    fitness_cache: list[float] = [0.0] * pop_size

    eval_count = 0
    best_d = 0
    best_cand: np.ndarray | None = None
    records_found: list[dict[str, Any]] = []

    # Initial evaluation
    for i in range(pop_size):
        if eval_count >= evals_limit or (time.perf_counter() - t0) >= seconds_limit:
            break
        score, is_rec = fitness_stabilizer_set(population[i], n, k, best_known)
        eval_count += 1
        fitness_cache[i] = score
        d_val = int(score)
        if d_val > best_d:
            best_d = d_val
            best_cand = population[i].copy()
        if is_rec:
            # Revalidate with P179 immediately
            gens = candidate_to_strings(population[i])
            ok_s, _ = check_stabilizer(gens)
            ok_d, d_info = code_distance(gens)
            if ok_s and ok_d and isinstance(d_info, dict) and d_info.get("d", 0) > best_known:
                obj_str = json.dumps(gens, sort_keys=True)
                sha = hashlib.sha256(obj_str.encode()).hexdigest()
                records_found.append(
                    {
                        "d": d_info["d"],
                        "generators": gens,
                        "sha256": sha,
                        "eval_idx": eval_count,
                        "elapsed_s": time.perf_counter() - t0,
                    }
                )

    generation = 0
    while eval_count < evals_limit and (time.perf_counter() - t0) < seconds_limit:
        generation += 1
        new_pop: list[np.ndarray] = []
        new_scores: list[float] = []

        # Elitism: retain top 2
        elite_indices = np.argsort(fitness_cache)[::-1][:2]
        for e_idx in elite_indices:
            new_pop.append(population[e_idx].copy())
            new_scores.append(fitness_cache[e_idx])

        # Fill rest through selection, crossover and mutation
        while len(new_pop) < pop_size:
            if eval_count >= evals_limit or (time.perf_counter() - t0) >= seconds_limit:
                break
            # Tournament selection (minimize negative fitness)
            neg_fitness = [-sc for sc in fitness_cache]
            parent_a = population[int(rng.integers(0, pop_size))]
            parent_b = population[int(rng.integers(0, pop_size))]
            if len(population) >= 3:
                # tournament select
                c1, c2 = rng.choice(pop_size, size=2, replace=False)
                parent_a = (
                    population[c1] if fitness_cache[c1] >= fitness_cache[c2] else population[c2]
                )
                c3, c4 = rng.choice(pop_size, size=2, replace=False)
                parent_b = (
                    population[c3] if fitness_cache[c3] >= fitness_cache[c4] else population[c4]
                )

            # Crossover
            if rng.random() < 0.7:
                child_a, child_b = crossover_stabilizer_sets(parent_a, parent_b, rng)
            else:
                child_a, child_b = parent_a.copy(), parent_b.copy()

            # Mutation
            child_a = mutate_stabilizer_set(child_a, rng)
            child_b = mutate_stabilizer_set(child_b, rng)

            for child in (child_a, child_b):
                if len(new_pop) >= pop_size:
                    break
                ok_rep, fixed = repair_commutation(child)
                candidate_to_eval = fixed if ok_rep else child
                sc, is_rec = fitness_stabilizer_set(candidate_to_eval, n, k, best_known)
                eval_count += 1
                new_pop.append(candidate_to_eval)
                new_scores.append(sc)

                d_val = int(sc)
                if d_val > best_d:
                    best_d = d_val
                    best_cand = candidate_to_eval.copy()
                if is_rec:
                    gens = candidate_to_strings(candidate_to_eval)
                    ok_s, _ = check_stabilizer(gens)
                    ok_d, d_info = code_distance(gens)
                    if (
                        ok_s
                        and ok_d
                        and isinstance(d_info, dict)
                        and d_info.get("d", 0) > best_known
                    ):
                        obj_str = json.dumps(gens, sort_keys=True)
                        sha = hashlib.sha256(obj_str.encode()).hexdigest()
                        records_found.append(
                            {
                                "d": d_info["d"],
                                "generators": gens,
                                "sha256": sha,
                                "eval_idx": eval_count,
                                "elapsed_s": time.perf_counter() - t0,
                            }
                        )

        population = new_pop
        fitness_cache = new_scores

    elapsed = time.perf_counter() - t0
    best_gens = candidate_to_strings(best_cand) if best_cand is not None else []
    return {
        "seed": seed,
        "elapsed_seconds": elapsed,
        "evaluations": eval_count,
        "generations": generation,
        "best_d": best_d,
        "best_candidate_generators": best_gens,
        "records_count": len(records_found),
        "records": records_found,
    }


def run_campaign(
    target_id: str,
    seconds: float,
    seeds: list[int],
    output_path: Path,
    checkpoint_path: Path | None = None,
    evals: int = 500,
) -> dict[str, Any]:
    target = load_target(target_id)
    n = target["n"]
    k = target["k"]
    best_known = target["best_known_value"]

    results: list[dict[str, Any]] = []
    t_start = time.perf_counter()

    for idx, seed in enumerate(seeds):
        res = run_single_seed_search(
            n=n,
            k=k,
            best_known=best_known,
            seed=seed,
            seconds_limit=seconds,
            evals_limit=evals,
        )
        results.append(res)

        if checkpoint_path is not None:
            partial_data = {
                "target_id": target_id,
                "n": n,
                "k": k,
                "best_known": best_known,
                "seeds_completed": idx + 1,
                "total_seeds": len(seeds),
                "partial_results": results,
            }
            checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
            checkpoint_path.write_text(json.dumps(partial_data, indent=2), encoding="utf-8")

    total_records = sum(r["records_count"] for r in results)
    best_overall_d = max((r["best_d"] for r in results), default=0)

    summary = {
        "target_id": target_id,
        "n": n,
        "k": k,
        "best_known": best_known,
        "target_role": target.get("role", "unknown"),
        "total_seeds": len(seeds),
        "total_elapsed_s": time.perf_counter() - t_start,
        "best_d_found": best_overall_d,
        "beat_best_known": bool(best_overall_d > best_known),
        "total_record_witnesses": total_records,
        "runs": results,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="P181 Stabilizer Search Benchmark")
    parser.add_argument(
        "--target", type=str, default="five_qubit_5_1_3", help="Target ID from catalogue"
    )
    parser.add_argument("--seconds", type=float, default=2.0, help="Per-seed time limit in seconds")
    parser.add_argument(
        "--seeds", type=str, default="42,43,44", help="Comma-separated random seeds"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="experiments/p181-stabilizer-results.json",
        help="Output JSON path",
    )
    parser.add_argument(
        "--checkpoint", type=str, default=None, help="Optional checkpoint JSON path"
    )
    parser.add_argument("--evals", type=int, default=300, help="Per-seed evaluation budget")
    parser.add_argument("--smoke", action="store_true", help="Quick smoke run")
    args = parser.parse_args()

    if args.smoke:
        seeds = [42]
        seconds = 0.5
        evals = 20
    else:
        seeds = [int(s.strip()) for s in args.seeds.split(",") if s.strip()]
        seconds = args.seconds
        evals = args.evals

    out_p = Path(args.output)
    ckpt_p = Path(args.checkpoint) if args.checkpoint else None

    summary = run_campaign(
        target_id=args.target,
        seconds=seconds,
        seeds=seeds,
        output_path=out_p,
        checkpoint_path=ckpt_p,
        evals=evals,
    )
    print(
        f"Search completed: target={summary['target_id']} best_d={summary['best_d_found']} "
        f"(best_known={summary['best_known']}) records={summary['total_record_witnesses']} -> {out_p}"
    )


if __name__ == "__main__":
    main()
