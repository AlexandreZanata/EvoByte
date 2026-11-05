"""Experiment script for Q10: Schrödinger residual search and staged evaluation.

Evaluates wavefunctions scored by stationary Schrödinger residual
||Hψ - Eψ|| + normalization_error + boundary_error + complexity_penalty
under a staged FAST -> DENSE -> HIGH_PRECISION -> STRICT doctrine.
Produces residual tables per strictness stage and analytic sanity logs.
"""

from __future__ import annotations

import argparse
import datetime
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "benchmarks"))

import numpy as np

from evobyte.quantum.residual import (
    StrictnessStage,
    box_analytic_ground_state,
    box_potential,
    build_box_ground_program,
    build_qho_ground_program,
    compute_residual,
    evaluate_program_staged,
    qho_analytic_ground_state,
    qho_potential,
    search_wavefunction_residual,
)
from hw_probe import probe


def get_git_commit() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=5)
        if out.returncode == 0:
            return out.stdout.strip()[:12]
    except Exception:
        pass
    return "unknown"


def run_analytic_sanity_log() -> list[dict[str, Any]]:
    """Evaluate analytic solutions and golden programs across all 4 strictness stages."""
    print("=" * 110)
    print("Q10 ANALYTIC SANITY ORACLE LOG (SOLVABLE SYSTEMS ACROSS ALL STAGES)")
    print("=" * 110)
    print(
        f"{'System':<8} | {'Stage':<15} | {'Grid':<5} | {'Residual Norm':<14} | "
        f"{'Energy':<10} | {'Norm Err':<10} | {'BC Err':<10} | {'Fidelity':<10} | {'Total Loss':<10}"
    )
    print("-" * 110)

    stages_info = [
        (StrictnessStage.FAST, 32),
        (StrictnessStage.DENSE, 128),
        (StrictnessStage.HIGH_PRECISION, 256),
        (StrictnessStage.STRICT, 256),
    ]

    records: list[dict[str, Any]] = []

    # 1. Quantum Harmonic Oscillator
    qho_prog = build_qho_ground_program()
    for stage, n_pts in stages_info:
        res = evaluate_program_staged(qho_prog, "qho", target_energy=0.5, max_stage=stage)
        fid_str = f"{res.analytical_fidelity:.6f}" if res.analytical_fidelity is not None else "N/A"
        print(
            f"{'QHO':<8} | {stage.name:<15} | {n_pts:<5} | {res.residual_norm:<14.4e} | "
            f"{res.rayleigh_energy:<10.6f} | {res.norm_error:<10.2e} | {res.boundary_error:<10.2e} | "
            f"{fid_str:<10} | {res.total_loss:<10.4e}"
        )
        records.append({
            "system": "qho",
            "stage": stage.name,
            "grid_points": n_pts,
            "residual_norm": res.residual_norm,
            "energy": res.rayleigh_energy,
            "norm_error": res.norm_error,
            "boundary_error": res.boundary_error,
            "fidelity": res.analytical_fidelity,
            "total_loss": res.total_loss,
        })

    print("-" * 110)

    # 2. Particle in a Box
    box_prog = build_box_ground_program()
    for stage, n_pts in stages_info:
        res = evaluate_program_staged(box_prog, "box", target_energy=0.5, max_stage=stage)
        fid_str = f"{res.analytical_fidelity:.6f}" if res.analytical_fidelity is not None else "N/A"
        print(
            f"{'Box':<8} | {stage.name:<15} | {n_pts:<5} | {res.residual_norm:<14.4e} | "
            f"{res.rayleigh_energy:<10.6f} | {res.norm_error:<10.2e} | {res.boundary_error:<10.2e} | "
            f"{fid_str:<10} | {res.total_loss:<10.4e}"
        )
        records.append({
            "system": "box",
            "stage": stage.name,
            "grid_points": n_pts,
            "residual_norm": res.residual_norm,
            "energy": res.rayleigh_energy,
            "norm_error": res.norm_error,
            "boundary_error": res.boundary_error,
            "fidelity": res.analytical_fidelity,
            "total_loss": res.total_loss,
        })

    print("=" * 110)
    print()
    return records


def run_q10_rediscovery(
    seeds: list[int],
    pop_size: int = 300,
    generations: int = 30,
    residual_tolerance: float = 0.05,
    fidelity_tolerance: float = 0.99,
) -> dict[str, Any]:
    """Execute staged rediscovery runs across solvable systems and seeds."""
    systems = [
        ("box", 0.5, None),
        ("qho", 0.5, None),
    ]

    all_records: list[dict[str, Any]] = []
    total_runs = len(systems) * len(seeds)
    successes = 0

    print("=" * 125)
    print(f"Q10 STAGED WAVEFUNCTION RESIDUAL REDISCOVERY ({len(seeds)} Seeds per System)")
    print("=" * 125)
    print(f"  Population Size      : {pop_size}")
    print(f"  Max Generations      : {generations}")
    print(f"  Residual Threshold   : ||Hψ - Eψ|| <= {residual_tolerance:.2e}")
    print(f"  Fidelity Threshold   : Fidelity >= {fidelity_tolerance:.4f}")
    print("-" * 125)
    print(
        f"{'System':<6} | {'Seed':<5} | {'Gen':<4} | {'Evals':<6} | {'Time (s)':<8} | "
        f"{'Residual Norm':<14} | {'Energy':<10} | {'Fidelity':<10} | {'Result':<6} | {'Discovered Expression'}"
    )
    print("-" * 125)

    for sys_name, target_e, seed_tmpls in systems:
        for seed in seeds:
            res = search_wavefunction_residual(
                system_name=sys_name,
                target_energy=target_e,
                pop_size=pop_size,
                generations=generations,
                seed=seed,
                early_stop_residual=residual_tolerance,
                seed_templates=seed_tmpls,
            )

            fid = res["fidelity"] if res["fidelity"] is not None else 0.0
            res_norm = res["residual_norm"]
            is_succ = (res_norm <= residual_tolerance) and (fid >= fidelity_tolerance)

            if is_succ:
                successes += 1

            verdict = "PASS" if is_succ else "FAIL"
            print(
                f"{sys_name.upper():<6} | {seed:<5} | {res['generations_run']:<4} | {res['evaluations']:<6} | {res['elapsed_s']:<8.3f} | "
                f"{res_norm:<14.4e} | {res['energy']:<10.6f} | {fid:<10.6f} | {verdict:<6} | {res['best_expression']}"
            )

            all_records.append({
                "system": sys_name,
                "seed": seed,
                "generations": res["generations_run"],
                "evaluations": res["evaluations"],
                "elapsed_s": res["elapsed_s"],
                "residual_norm": res_norm,
                "energy": res["energy"],
                "fidelity": fid,
                "expression": res["best_expression"],
                "success": is_succ,
            })

    print("-" * 125)
    success_rate = successes / total_runs
    mean_res = float(np.mean([r["residual_norm"] for r in all_records]))
    mean_fid = float(np.mean([r["fidelity"] for r in all_records]))
    print(
        f"SUMMARY: {successes}/{total_runs} successes ({success_rate * 100:.1f}%) | "
        f"Mean Residual Norm: {mean_res:.2e} | Mean Fidelity: {mean_fid:.6f}"
    )
    gate_passed = successes == total_runs
    status_str = "PASS" if gate_passed else "FAIL"
    print(f"EXIT GATE VERDICT: {status_str}")
    print("=" * 125)

    return {
        "seeds": seeds,
        "total_runs": total_runs,
        "successes": successes,
        "success_rate": success_rate,
        "mean_residual_norm": mean_res,
        "mean_fidelity": mean_fid,
        "gate_passed": gate_passed,
        "records": all_records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Q10 Schrödinger Residual Search Experiment")
    parser.add_argument("--seeds", type=int, default=3, help="Number of seeds (default: 3)")
    parser.add_argument("--pop_size", type=int, default=300, help="Population size (default: 300)")
    parser.add_argument("--generations", type=int, default=30, help="Max generations (default: 30)")
    parser.add_argument("--json", action="store_true", help="Output JSON results")
    args = parser.parse_args()

    # 1. Run analytic sanity check across all stages
    sanity_records = run_analytic_sanity_log()

    # 2. Run staged rediscovery experiment
    seeds = list(range(args.seeds))
    res = run_q10_rediscovery(
        seeds=seeds,
        pop_size=args.pop_size,
        generations=args.generations,
    )

    combined_output = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "git_commit": get_git_commit(),
        "hardware": probe(),
        "analytic_sanity_log": sanity_records,
        "rediscovery_experiment": res,
    }

    if args.json:
        print(json.dumps(combined_output, indent=2))

    return 0 if res["gate_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
