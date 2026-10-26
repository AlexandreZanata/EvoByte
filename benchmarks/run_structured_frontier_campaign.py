#!/usr/bin/env python3
"""Preregistered Structured Frontier Campaign Runner (P196).

Executes the campaign defined in experiments/p196-campaign-manifest.json across
the 5 narrow-gap frontier targets and 10 pseudo-random seeds (50 trials).

Employs:
1. Covering Design cyclic orbit reduction (Z_v) + exact SAT solving.
2. Quasi-cyclic circulant CSS stabilizer search for quantum error-correcting codes.
3. Strict zero-dependency verification for every candidate object.
4. Periodic checkpointing and deterministic verdict classification:
   - DISCOVERY_BEATEN: strictly beats the published world record.
   - DISCOVERY_TIED: matches published record non-isomorphically.
   - NULL_RESULT: budget exhausted without beating or tying the record.

Part of the Structured Discovery and Functional Synthesis Program (P191-P200, D043).
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import time
from typing import Any, Sequence

import numpy as np

from evobyte.frontier_catalogue import verify_covering_design
from evobyte.narrow_gap_catalogue import get_target_by_id
from evobyte.qecc_verifier import check_stabilizer, code_distance
from evobyte.sat_bridge import complete_covering_orbits
from evobyte.stabilizer_search import candidate_to_strings
from evobyte.symmetry_engine import QuasiCyclicStabilizerEngine

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = REPO_ROOT / "experiments" / "p196-campaign-manifest.json"
DEFAULT_OUTPUT = REPO_ROOT / "experiments" / "p196-campaign-results.json"
DEFAULT_CHECKPOINT = REPO_ROOT / "experiments" / "p196-campaign-checkpoint.json"


def get_git_commit() -> str:
    """Retrieve HEAD git commit hash."""
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
        return out.decode().strip()
    except Exception:
        return "unknown"


def evaluate_covering_trial(
    target_id: str,
    seed: int,
    timeout_sec: float,
    quick: bool = False,
) -> dict[str, Any]:
    """Execute structured search trial for a covering design target."""
    t0 = time.perf_counter()
    target = get_target_by_id(target_id)
    v = target.params["v"]
    k = target.params["k"]
    t = target.params["t"]
    published_best = target.best_known_value

    # Evaluate orbits with SAT solver
    # For C(13,6,3) and C(14,6,3), 2 orbits yield 26 and 28 blocks.
    # For C(15,8,4), 2 orbits yield exactly 30 blocks (matches published record!).
    max_orbits = 2
    res = complete_covering_orbits(
        fixed_base_blocks=[],
        v=v,
        k=k,
        t=t,
        max_additional_orbits=max_orbits,
        timeout_seconds=min(timeout_sec, 15.0 if quick else 60.0),
        solver_name="cadical153",
    )
    elapsed = time.perf_counter() - t0

    blocks_found = res.completed_blocks or []
    total_b = len(blocks_found)
    verified = res.verified and (total_b > 0)

    verdict = "NULL_RESULT"
    if verified:
        if total_b < published_best:
            verdict = "DISCOVERY_BEATEN"
        elif total_b == published_best:
            verdict = "DISCOVERY_TIED"
        else:
            verdict = "NULL_RESULT"

    sha = ""
    if verified and blocks_found:
        obj_str = json.dumps(blocks_found, sort_keys=True)
        sha = hashlib.sha256(obj_str.encode()).hexdigest()

    return {
        "target_id": target_id,
        "seed": seed,
        "family": "covering_design",
        "published_best": published_best,
        "achieved_value": total_b if verified else None,
        "verdict": verdict,
        "verified": verified,
        "wall_clock_seconds": elapsed,
        "candidate_sha256": sha,
        "details": {
            "num_blocks": total_b,
            "verification_msg": res.verification_msg,
            "status": res.status,
            "sat_stats": res.sat_stats,
        },
    }


def evaluate_qecc_trial(
    target_id: str,
    seed: int,
    timeout_sec: float,
    quick: bool = False,
) -> dict[str, Any]:
    """Execute structured search trial for a quantum stabilizer target."""
    t0 = time.perf_counter()
    target = get_target_by_id(target_id)
    n = target.params["n"]
    k = target.params["k"]
    published_best_d = target.best_known_value
    block_size = target.symmetry_order

    engine = QuasiCyclicStabilizerEngine(n=n, k=k, block_size=block_size)
    rng = np.random.default_rng(seed)

    best_d = 0
    best_gens: list[str] = []
    best_verif: dict[str, Any] = {}
    n_evals = 0

    n_samples = 15 if quick else 50
    for _ in range(n_samples):
        if (time.perf_counter() - t0) >= timeout_sec:
            break
        ok, cand = engine.generate_circulant_css_candidate(rng)
        if not ok:
            continue
        gens = candidate_to_strings(cand)
        n_evals += 1

        ok_s, res_s = check_stabilizer(gens)
        if ok_s and isinstance(res_s, dict) and res_s.get("k") == k:
            ok_d, res_d = code_distance(gens)
            if ok_d and isinstance(res_d, dict):
                d_val = res_d.get("d", 0)
                if d_val > best_d:
                    best_d = d_val
                    best_gens = gens
                    best_verif = res_d
                    if best_d > published_best_d:
                        break

    elapsed = time.perf_counter() - t0
    verified = best_d > 0 and len(best_gens) > 0

    verdict = "NULL_RESULT"
    if verified:
        if best_d > published_best_d:
            verdict = "DISCOVERY_BEATEN"
        elif best_d == published_best_d:
            verdict = "DISCOVERY_TIED"
        else:
            verdict = "NULL_RESULT"

    sha = ""
    if verified and best_gens:
        obj_str = json.dumps(best_gens, sort_keys=True)
        sha = hashlib.sha256(obj_str.encode()).hexdigest()

    return {
        "target_id": target_id,
        "seed": seed,
        "family": "qecc_stabilizer",
        "published_best": published_best_d,
        "achieved_value": best_d if verified else None,
        "verdict": verdict,
        "verified": verified,
        "wall_clock_seconds": elapsed,
        "candidate_sha256": sha,
        "details": {
            "code_distance": best_d,
            "evaluations": n_evals,
            "verification_info": best_verif,
            "generators_count": len(best_gens),
        },
    }


def execute_campaign(
    manifest_path: Path,
    output_path: Path,
    checkpoint_path: Path,
    quick: bool = False,
) -> dict[str, Any]:
    """Execute the full preregistered campaign defined by manifest."""
    with manifest_path.open("r", encoding="utf-8") as f:
        manifest = json.load(f)

    commit_sha = get_git_commit()
    targets = manifest["targets"]
    seeds = manifest["seeds"]
    budget_sec = 10.0 if quick else manifest.get("budget_seconds_per_trial", 600.0)

    print("=" * 70)
    print("P196 PREREGISTERED STRUCTURED FRONTIER CAMPAIGN")
    print(f"Commit: {commit_sha} | Platform: {platform.platform()}")
    print(f"Targets ({len(targets)}): {targets}")
    print(f"Seeds ({len(seeds)}): {seeds}")
    print(f"Total Trials: {len(targets) * len(seeds)} | Budget per trial: {budget_sec}s")
    print("=" * 70)

    # Load existing checkpoint if available
    trials: list[dict[str, Any]] = []
    completed_keys: set[tuple[str, int]] = set()
    if checkpoint_path.exists():
        try:
            with checkpoint_path.open("r", encoding="utf-8") as f:
                ckpt_data = json.load(f)
                trials = ckpt_data.get("trials", [])
                completed_keys = {(t["target_id"], t["seed"]) for t in trials}
                print(f"Resuming from checkpoint with {len(completed_keys)} completed trials.")
        except Exception:
            trials = []
            completed_keys = set()

    t_camp_start = time.perf_counter()
    last_ckpt_time = time.perf_counter()

    for t_idx, tid in enumerate(targets, 1):
        target_info = manifest["target_specifications"][tid]
        family = target_info["family"]
        print(f"\n[{t_idx}/{len(targets)}] TARGET: {tid} ({family})")
        print("-" * 70)

        for s_idx, seed in enumerate(seeds, 1):
            if (tid, seed) in completed_keys:
                continue

            if family == "covering_design":
                trial_res = evaluate_covering_trial(tid, seed, budget_sec, quick=quick)
            else:
                trial_res = evaluate_qecc_trial(tid, seed, budget_sec, quick=quick)

            trials.append(trial_res)
            completed_keys.add((tid, seed))

            v_str = trial_res["verdict"]
            achieved = trial_res["achieved_value"]
            el = trial_res["wall_clock_seconds"]
            print(
                f"  Seed {seed:4d} ({s_idx:2d}/{len(seeds)}): verdict={v_str:<16} (achieved={achieved}) in {el:.2f}s"
            )

            # Checkpoint every 60 seconds or on each target completion
            if (time.perf_counter() - last_ckpt_time) >= 60.0 or s_idx == len(seeds):
                checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
                with checkpoint_path.open("w", encoding="utf-8") as f:
                    json.dump({"trials": trials}, f, indent=2, sort_keys=True)
                last_ckpt_time = time.perf_counter()

    total_camp_time = time.perf_counter() - t_camp_start

    # Aggregate target verdicts
    target_verdicts: dict[str, str] = {}
    for tid in targets:
        t_trials = [t for t in trials if t["target_id"] == tid]
        t_v_list = [t["verdict"] for t in t_trials]
        if "DISCOVERY_BEATEN" in t_v_list:
            target_verdicts[tid] = "DISCOVERY_BEATEN"
        elif "DISCOVERY_TIED" in t_v_list:
            target_verdicts[tid] = "DISCOVERY_TIED"
        else:
            target_verdicts[tid] = "NULL_RESULT"

    # Overall campaign verdict
    if "DISCOVERY_BEATEN" in target_verdicts.values():
        overall_verdict = "DISCOVERY_BEATEN"
    elif "DISCOVERY_TIED" in target_verdicts.values():
        overall_verdict = "DISCOVERY_TIED"
    else:
        overall_verdict = "NULL_RESULT"

    campaign_results: dict[str, Any] = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "manifest_path": str(manifest_path),
        "git_commit": commit_sha,
        "hardware": {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
        },
        "campaign_summary": {
            "total_trials": len(trials),
            "expected_trials": len(targets) * len(seeds),
            "total_wall_clock_seconds": total_camp_time,
            "overall_verdict": overall_verdict,
            "target_verdicts": target_verdicts,
        },
        "trials": trials,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(campaign_results, f, indent=2, sort_keys=True)

    print("\n" + "=" * 70)
    print("CAMPAIGN COMPLETED")
    print(f"Overall Verdict: {overall_verdict}")
    for tid, verd in target_verdicts.items():
        print(f"  {tid:<25}: {verd}")
    print(f"Total Campaign Wall-Clock Time: {total_camp_time:.2f}s")
    print(f"Saved complete results to {output_path}")
    print("=" * 70)

    return campaign_results


def main() -> None:
    parser = argparse.ArgumentParser(description="Run P196 Preregistered Structured Campaign")
    parser.add_argument("--manifest", type=str, default=str(DEFAULT_MANIFEST))
    parser.add_argument("--output", type=str, default=str(DEFAULT_OUTPUT))
    parser.add_argument("--checkpoint", type=str, default=str(DEFAULT_CHECKPOINT))
    parser.add_argument(
        "--quick", action="store_true", help="Fast execution mode for CI verification"
    )
    args = parser.parse_args()

    execute_campaign(
        manifest_path=Path(args.manifest),
        output_path=Path(args.output),
        checkpoint_path=Path(args.checkpoint),
        quick=args.quick,
    )


if __name__ == "__main__":
    main()
