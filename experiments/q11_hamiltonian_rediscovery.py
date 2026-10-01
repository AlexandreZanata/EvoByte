"""Experiment script for Q11: Blind Hamiltonian rediscovery from quantum dynamics.

Generates observable dynamics from a target Hamiltonian, discovers sparse Pauli
terms and interaction coefficients via evolutionary search, and evaluates
structural term recovery (precision, recall, F1, coefficient error) across 5 seeds.
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

from evobyte.quantum.hamdisc import (
    DynamicsDataset,
    dynamics_matching_fitness,
    evaluate_structural_recovery,
    generate_dynamics_dataset,
    ising_transverse_benchmark,
    rediscover_hamiltonian_from_dynamics,
    xyz_field_benchmark,
)
from evobyte.quantum.hamiltonians import PauliTerm, decode_hamiltonian
from hw_probe import probe


def get_git_commit() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=5)
        if out.returncode == 0:
            return out.stdout.strip()[:12]
    except Exception:
        pass
    return "unknown"


def run_q11_experiment(
    seeds: list[int],
    model: str = "xyz",
    n_qubits: int = 2,
    pop_size: int = 100,
    generations: int = 35,
    mse_tolerance: float = 1e-4,
    prec_tolerance: float = 0.99,
    rec_tolerance: float = 0.99,
) -> dict[str, Any]:
    """Execute blind Hamiltonian rediscovery across multiple seeds."""
    if model == "xyz":
        target_terms = xyz_field_benchmark(n_qubits=n_qubits, jx=1.0, jy=0.5, jz=0.8, hz=0.4)
    elif model == "ising":
        target_terms = ising_transverse_benchmark(n_qubits=n_qubits, jz=1.0, hx=0.5)
    else:
        raise ValueError(f"unknown model: {model}")

    # Generate dynamics dataset
    dataset = generate_dynamics_dataset(target_terms, n_qubits=n_qubits, seed=0)
    target_str = decode_hamiltonian(target_terms, n_qubits)

    # Sanity check: evaluate true Hamiltonian on dataset
    sanity_mse, sanity_loss = dynamics_matching_fitness(target_terms, dataset, lambda_sparse=0.0, lambda_comp=0.0)

    print("=" * 125)
    print(f"Q11 HAMILTONIAN REDISCOVERY FROM DYNAMICS ({model.upper()}, N={n_qubits} Qubits)")
    print("=" * 125)
    print(f"  Target Hamiltonian   : {target_str}")
    print(f"  Dataset SHA-256 Hash : {dataset.sha256_hash}")
    print(f"  Trajectory Grid      : {len(dataset.initial_states)} initial states x {len(dataset.times)} times x {len(dataset.observable_terms)} observables")
    print(f"  Sanity Oracle MSE    : {sanity_mse:.4e} (true Hamiltonian)")
    print(f"  Population Size      : {pop_size}, Max Generations: {generations}")
    print(f"  Success Thresholds   : MSE <= {mse_tolerance:.1e}, Precision >= {prec_tolerance:.2f}, Recall >= {rec_tolerance:.2f}")
    print("-" * 125)
    print(
        f"{'Seed':<5} | {'Gen':<4} | {'Evals':<6} | {'Time (s)':<8} | {'MSE Dyn':<11} | "
        f"{'Precision':<9} | {'Recall':<7} | {'F1':<5} | {'MAE Coeff':<10} | {'Result':<6} | {'Discovered Hamiltonian'}"
    )
    print("-" * 125)

    records: list[dict[str, Any]] = []
    successes = 0

    for seed in seeds:
        res = rediscover_hamiltonian_from_dynamics(
            dataset=dataset,
            max_k=2,
            pop_size=pop_size,
            max_generations=generations,
            early_stop_mse=1e-6,
            seed=seed,
        )

        disc_terms = res["discovered_terms"]
        mse_dyn = res["dynamics_mse"]
        metrics = evaluate_structural_recovery(disc_terms, target_terms)

        prec = metrics["precision"]
        rec = metrics["recall"]
        f1 = metrics["f1"]
        mae = metrics["coeff_mae"]

        is_succ = (mse_dyn <= mse_tolerance) and (prec >= prec_tolerance) and (rec >= rec_tolerance)
        if is_succ:
            successes += 1

        verdict = "PASS" if is_succ else "FAIL"
        expr_str = res["expression"]

        print(
            f"{seed:<5} | {res['generations']:<4} | {res['evaluations']:<6} | {res['elapsed_s']:<8.3f} | {mse_dyn:<11.2e} | "
            f"{prec:<9.2f} | {rec:<7.2f} | {f1:<5.2f} | {mae:<10.4f} | {verdict:<6} | {expr_str}"
        )

        records.append({
            "seed": seed,
            "generations": res["generations"],
            "evaluations": res["evaluations"],
            "elapsed_s": res["elapsed_s"],
            "dynamics_mse": mse_dyn,
            "precision": prec,
            "recall": rec,
            "f1": f1,
            "coeff_mae": mae,
            "coeff_max_err": metrics["coeff_max_err"],
            "expression": expr_str,
            "success": is_succ,
        })

    print("-" * 125)
    success_rate = successes / len(seeds)
    mean_prec = float(np.mean([r["precision"] for r in records]))
    mean_rec = float(np.mean([r["recall"] for r in records]))
    mean_f1 = float(np.mean([r["f1"] for r in records]))
    mean_mae = float(np.mean([r["coeff_mae"] for r in records]))
    mean_mse = float(np.mean([r["dynamics_mse"] for r in records]))

    print(
        f"SUMMARY: {successes}/{len(seeds)} successes ({success_rate * 100:.1f}%) | "
        f"Mean Precision: {mean_prec:.2f} | Mean Recall: {mean_rec:.2f} | Mean F1: {mean_f1:.2f} | "
        f"Mean Coeff MAE: {mean_mae:.4f} | Mean MSE: {mean_mse:.2e}"
    )

    gate_passed = successes == len(seeds)
    status_str = "PASS" if gate_passed else "FAIL"
    print(f"EXIT GATE VERDICT: {status_str}")
    print("=" * 125)

    return {
        "model": model,
        "n_qubits": n_qubits,
        "target_hamiltonian": target_str,
        "dataset_hash": dataset.sha256_hash,
        "sanity_oracle_mse": sanity_mse,
        "seeds": seeds,
        "total_seeds": len(seeds),
        "successes": successes,
        "success_rate": success_rate,
        "mean_precision": mean_prec,
        "mean_recall": mean_rec,
        "mean_f1": mean_f1,
        "mean_coeff_mae": mean_mae,
        "mean_dynamics_mse": mean_mse,
        "gate_passed": gate_passed,
        "records": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Q11 Hamiltonian Rediscovery Experiment")
    parser.add_argument("--seeds", type=int, default=5, help="Number of seeds (default: 5)")
    parser.add_argument("--model", type=str, default="xyz", choices=["xyz", "ising"])
    parser.add_argument("--qubits", type=int, default=2, help="Number of qubits (default: 2)")
    parser.add_argument("--pop_size", type=int, default=80, help="Population size (default: 80)")
    parser.add_argument("--generations", type=int, default=25, help="Max generations (default: 25)")
    parser.add_argument("--json", action="store_true", help="Output JSON results")
    args = parser.parse_args()

    seeds = list(range(args.seeds))
    res = run_q11_experiment(
        seeds=seeds,
        model=args.model,
        n_qubits=args.qubits,
        pop_size=args.pop_size,
        generations=args.generations,
    )

    combined_output = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "git_commit": get_git_commit(),
        "hardware": probe(),
        "results": res,
    }

    if args.json:
        print(json.dumps(combined_output, indent=2))

    return 0 if res["gate_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
