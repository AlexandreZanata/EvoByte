#!/usr/bin/env python3
"""Execute QECC blind rediscovery and preregistered campaign (P182).

Protocol:
1. Phase 1: Blind rediscovery calibration on known codes (Steane [[7,1,3]], Shor [[9,1,3]])
   from purely random initialization (no manual solution seeds).
2. Phase 2: Preregistered campaign on open Grassl targets under fixed dual budget.
3. Strict incremental checkpointing and independent P179 oracle validation.
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
from evobyte.stabilizer_search import (
    candidate_to_strings,
    crossover_stabilizer_sets,
    fitness_stabilizer_set,
    mutate_stabilizer_set,
    random_stabilizer_set,
    repair_commutation,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = REPO_ROOT / "experiments" / "p182-qecc-manifest.json"
DEFAULT_OUTPUT = REPO_ROOT / "experiments" / "p182-qecc-results.json"
DEFAULT_CHECKPOINT = REPO_ROOT / "experiments" / "p182-qecc-checkpoint.json"
CATALOGUE_PATH = REPO_ROOT / "docs" / "research" / "targets" / "qecc_frontier_v1.json"


def evaluate_trial_verdict(best_d: int, best_known: int, role: str) -> str:
    """Determine verdict for a single trial."""
    if role == "calibration":
        return "REDISCOVERY_OK" if best_d >= best_known else "NULL_RESULT"
    else:
        return "DISCOVERY_BEATEN" if best_d > best_known else "NULL_RESULT"


def evaluate_target_verdict(trial_verdicts: list[str]) -> str:
    """Aggregate trial verdicts for a single target."""
    if "DISCOVERY_BEATEN" in trial_verdicts:
        return "DISCOVERY_BEATEN"
    if "REDISCOVERY_OK" in trial_verdicts:
        return "REDISCOVERY_OK"
    return "NULL_RESULT"


def evaluate_campaign_verdict(target_verdicts: dict[str, str]) -> str:
    """Aggregate campaign verdict across all record targets."""
    for verdict in target_verdicts.values():
        if verdict == "DISCOVERY_BEATEN":
            return "DISCOVERY_BEATEN"
    return "NULL_RESULT"


def load_catalogue_targets(cat_path: Path) -> dict[str, dict[str, Any]]:
    """Load target dictionary keyed by target_id."""
    with cat_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return {t["target_id"]: t for t in data.get("targets", [])}


def run_trial(
    target_info: dict[str, Any],
    seed: int,
    seconds_limit: float,
    evals_limit: int = 50,
    pop_size: int = 20,
    early_stop_on_rediscovery: bool = True,
) -> dict[str, Any]:
    """Run single evolutionary search trial from purely random initialization."""
    target_id = target_info["target_id"]
    n = target_info["n"]
    k = target_info["k"]
    role = target_info.get("role", "record")
    best_known = target_info["best_known_value"]

    t0 = time.perf_counter()
    rng = np.random.default_rng(seed)

    # Strictly pseudo-random initialization (never seeded with solutions)
    population: list[np.ndarray] = [random_stabilizer_set(n, k, rng) for _ in range(pop_size)]
    fitness_cache: list[float] = [0.0] * pop_size

    eval_count = 0
    best_d = 0
    best_cand: np.ndarray | None = None
    records_found: list[dict[str, Any]] = []

    for i in range(pop_size):
        if eval_count >= evals_limit or (time.perf_counter() - t0) >= seconds_limit:
            break
        sc, is_rec = fitness_stabilizer_set(population[i], n, k, best_known)
        eval_count += 1
        fitness_cache[i] = sc
        d_val = int(sc)
        if d_val > best_d:
            best_d = d_val
            best_cand = population[i].copy()
        if is_rec:
            gens = candidate_to_strings(population[i])
            ok_s, _ = check_stabilizer(gens)
            ok_d, d_info = code_distance(gens)
            if ok_s and ok_d and isinstance(d_info, dict) and d_info.get("d", 0) > best_known:
                obj_str = json.dumps(gens, sort_keys=True)
                records_found.append(
                    {
                        "d": d_info["d"],
                        "generators": gens,
                        "sha256": hashlib.sha256(obj_str.encode()).hexdigest(),
                        "eval_idx": eval_count,
                        "elapsed_s": time.perf_counter() - t0,
                    }
                )

    generation = 0
    while eval_count < evals_limit and (time.perf_counter() - t0) < seconds_limit:
        if role == "calibration" and early_stop_on_rediscovery and best_d >= best_known:
            break
        generation += 1
        new_pop: list[np.ndarray] = []
        new_scores: list[float] = []

        # Elitism: retain top 2
        elite_indices = np.argsort(fitness_cache)[::-1][:2]
        for e_idx in elite_indices:
            new_pop.append(population[e_idx].copy())
            new_scores.append(fitness_cache[e_idx])

        while len(new_pop) < pop_size:
            if eval_count >= evals_limit or (time.perf_counter() - t0) >= seconds_limit:
                break
            parent_a = population[int(rng.integers(0, pop_size))]
            parent_b = population[int(rng.integers(0, pop_size))]
            if len(population) >= 3:
                c1, c2 = rng.choice(pop_size, size=2, replace=False)
                parent_a = (
                    population[c1] if fitness_cache[c1] >= fitness_cache[c2] else population[c2]
                )
                c3, c4 = rng.choice(pop_size, size=2, replace=False)
                parent_b = (
                    population[c3] if fitness_cache[c3] >= fitness_cache[c4] else population[c4]
                )

            if rng.random() < 0.7:
                child_a, child_b = crossover_stabilizer_sets(parent_a, parent_b, rng)
            else:
                child_a, child_b = parent_a.copy(), parent_b.copy()

            child_a = mutate_stabilizer_set(child_a, rng)
            child_b = mutate_stabilizer_set(child_b, rng)

            for child in (child_a, child_b):
                if len(new_pop) >= pop_size:
                    break
                ok_rep, fixed = repair_commutation(child)
                cand_eval = fixed if ok_rep else child
                sc, is_rec = fitness_stabilizer_set(cand_eval, n, k, best_known)
                eval_count += 1
                new_pop.append(cand_eval)
                new_scores.append(sc)

                d_val = int(sc)
                if d_val > best_d:
                    best_d = d_val
                    best_cand = cand_eval.copy()
                if is_rec:
                    gens = candidate_to_strings(cand_eval)
                    ok_s, _ = check_stabilizer(gens)
                    ok_d, d_info = code_distance(gens)
                    if (
                        ok_s
                        and ok_d
                        and isinstance(d_info, dict)
                        and d_info.get("d", 0) > best_known
                    ):
                        obj_str = json.dumps(gens, sort_keys=True)
                        records_found.append(
                            {
                                "d": d_info["d"],
                                "generators": gens,
                                "sha256": hashlib.sha256(obj_str.encode()).hexdigest(),
                                "eval_idx": eval_count,
                                "elapsed_s": time.perf_counter() - t0,
                            }
                        )

        population = new_pop
        fitness_cache = new_scores

    elapsed = time.perf_counter() - t0
    verdict = evaluate_trial_verdict(best_d, best_known, role)
    best_gens = candidate_to_strings(best_cand) if best_cand is not None else []

    return {
        "target_id": target_id,
        "role": role,
        "n": n,
        "k": k,
        "best_known": best_known,
        "seed": seed,
        "elapsed_seconds": elapsed,
        "evaluations": eval_count,
        "generations": generation,
        "best_d": best_d,
        "verdict": verdict,
        "best_candidate_generators": best_gens,
        "records_count": len(records_found),
        "records": records_found,
    }


def execute_campaign(
    manifest_path: Path,
    output_path: Path,
    checkpoint_path: Path,
    resume: bool = True,
    budget_scale: float = 1.0,
) -> dict[str, Any]:
    """Execute full P182 protocol according to frozen manifest."""
    manifest_bytes = manifest_path.read_bytes()
    manifest_sha = hashlib.sha256(manifest_bytes).hexdigest()
    manifest = json.loads(manifest_bytes.decode("utf-8"))

    cat_targets = load_catalogue_targets(CATALOGUE_PATH)

    # Initialize or load checkpoint
    state: dict[str, Any] = {
        "phase": "P182",
        "manifest_sha256": manifest_sha,
        "completed_trials": {},
        "calibration_runs": [],
        "campaign_runs": [],
    }

    if resume and checkpoint_path.exists():
        try:
            with checkpoint_path.open("r", encoding="utf-8") as f:
                loaded_state = json.load(f)
                if loaded_state.get("manifest_sha256") == manifest_sha:
                    state = loaded_state
        except Exception:
            pass

    t_global_start = time.perf_counter()

    # --- Phase 1: Blind Rediscovery Calibration ---
    cal_cfg = manifest["calibration"]
    cal_targets = cal_cfg["targets"]
    cal_seeds = cal_cfg["seeds"]
    cal_budget_sec = float(cal_cfg["budget_sec_per_seed"]) * budget_scale
    cal_max_evals = int(cal_cfg.get("max_evaluations_per_trial", 200))

    cal_passed = True
    for tid in cal_targets:
        if tid not in cat_targets:
            raise ValueError(f"Calibration target {tid} not in catalogue")
        target_info = cat_targets[tid]
        for seed in cal_seeds:
            trial_key = f"calib_{tid}_{seed}"
            if trial_key in state["completed_trials"]:
                trial_res = state["completed_trials"][trial_key]
            else:
                trial_res = run_trial(
                    target_info=target_info,
                    seed=seed,
                    seconds_limit=cal_budget_sec,
                    evals_limit=cal_max_evals,
                    pop_size=20,
                    early_stop_on_rediscovery=True,
                )
                state["completed_trials"][trial_key] = trial_res
                state["calibration_runs"].append(trial_res)
                # save checkpoint
                checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
                checkpoint_path.write_text(json.dumps(state, indent=2), encoding="utf-8")

            if trial_res["verdict"] != "REDISCOVERY_OK":
                cal_passed = False

    if not cal_passed:
        print("STOP RULE: Blind rediscovery calibration failed. Aborting campaign.")
        state["calibration_status"] = "CALIBRATION_FAILED"
        state["campaign_status"] = "ABORTED_ON_FAILED_CALIBRATION"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
        return state

    state["calibration_status"] = "ALL_CALIBRATIONS_PASSED"

    # --- Phase 2: Preregistered Campaign on Open Targets ---
    camp_cfg = manifest["campaign"]
    camp_targets = camp_cfg["targets"]
    camp_seeds = camp_cfg["seeds"]
    camp_budget_sec = float(camp_cfg["budget_sec_per_seed"]) * budget_scale
    camp_max_evals = int(camp_cfg.get("max_evaluations_per_trial", 50))

    target_trial_verdicts: dict[str, list[str]] = {tid: [] for tid in camp_targets}

    for tid in camp_targets:
        if tid not in cat_targets:
            raise ValueError(f"Campaign target {tid} not in catalogue")
        target_info = cat_targets[tid]
        for seed in camp_seeds:
            trial_key = f"camp_{tid}_{seed}"
            if trial_key in state["completed_trials"]:
                trial_res = state["completed_trials"][trial_key]
            else:
                trial_res = run_trial(
                    target_info=target_info,
                    seed=seed,
                    seconds_limit=camp_budget_sec,
                    evals_limit=camp_max_evals,
                    pop_size=20,
                    early_stop_on_rediscovery=False,
                )
                state["completed_trials"][trial_key] = trial_res
                state["campaign_runs"].append(trial_res)
                # save checkpoint
                checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
                checkpoint_path.write_text(json.dumps(state, indent=2), encoding="utf-8")

            target_trial_verdicts[tid].append(trial_res["verdict"])

    target_overall_verdicts = {
        tid: evaluate_target_verdict(v_list) for tid, v_list in target_trial_verdicts.items()
    }
    overall_campaign_verdict = evaluate_campaign_verdict(target_overall_verdicts)

    all_records = []
    for run in state["campaign_runs"]:
        all_records.extend(run.get("records", []))

    final_results = {
        "phase": "P182",
        "manifest_sha256": manifest_sha,
        "calibration_status": "ALL_CALIBRATIONS_PASSED",
        "calibration_runs": state["calibration_runs"],
        "campaign_status": overall_campaign_verdict,
        "target_verdicts": target_overall_verdicts,
        "campaign_runs": state["campaign_runs"],
        "total_elapsed_seconds": time.perf_counter() - t_global_start,
        "total_records_discovered": len(all_records),
        "records": all_records,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(final_results, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return final_results


def main() -> None:
    parser = argparse.ArgumentParser(description="P182 QECC campaign runner")
    parser.add_argument(
        "--manifest", type=str, default=str(DEFAULT_MANIFEST), help="Manifest JSON path"
    )
    parser.add_argument("--output", type=str, default=str(DEFAULT_OUTPUT), help="Output JSON path")
    parser.add_argument(
        "--checkpoint", type=str, default=str(DEFAULT_CHECKPOINT), help="Checkpoint JSON path"
    )
    parser.add_argument(
        "--no-resume", action="store_true", help="Do not resume from existing checkpoint"
    )
    parser.add_argument(
        "--budget-scale", type=float, default=1.0, help="Scale factor for time budget (default 1.0)"
    )
    args = parser.parse_args()

    results = execute_campaign(
        manifest_path=Path(args.manifest),
        output_path=Path(args.output),
        checkpoint_path=Path(args.checkpoint),
        resume=not args.no_resume,
        budget_scale=args.budget_scale,
    )
    print(
        f"P182 Campaign complete: calib={results['calibration_status']} "
        f"campaign_verdict={results['campaign_status']} records={results['total_records_discovered']} "
        f"-> {args.output}"
    )


if __name__ == "__main__":
    main()
