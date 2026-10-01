"""Experiment script for Q09: Formula discovery from simulated quantum observables across 5 seeds.

Generates quantum observable datasets (ground energy, gap, magnetization, entropy)
over parameter grids, hides the generating relation, and discovers compact formulas
using the symbolic-regression pipeline with hidden and extrapolation error reporting.
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

from evobyte.evolution import EvolutionConfig, run_evolution
from evobyte.quantum.observables import generate_observable_dataset
from evobyte.verifier import evaluate
from hw_probe import probe


def get_git_commit() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=5)
        if out.returncode == 0:
            return out.stdout.strip()[:12]
    except Exception:
        pass
    return "unknown"


def generate_experiment_splits(
    model: str = "heisenberg",
    n_qubits: int = 2,
    n_points: int = 64,
) -> tuple[str, dict[str, tuple[np.ndarray, np.ndarray]]]:
    """Generate train, val, hidden in-domain, and extrapolation out-of-domain splits."""
    if model == "heisenberg":
        # Ground energy scaling: E_0(J) = -3 J (N=2) or -4 J (N=3)
        # 1. Training grid in [0.5, 4.0]
        train_grid = {"J": np.linspace(0.5, 4.0, n_points)}
        ds_train = generate_observable_dataset("heisenberg", n_qubits, train_grid, observables=["energy"])
        xs_train, ys_train = ds_train.to_arrays("energy")

        # 2. Validation grid in [0.5, 4.0]
        val_grid = {"J": np.linspace(0.55, 3.95, n_points)}
        ds_val = generate_observable_dataset("heisenberg", n_qubits, val_grid, observables=["energy"])
        xs_val, ys_val = ds_val.to_arrays("energy")

        # 3. Hidden in-domain test grid (interleaved)
        hidden_grid = {"J": np.linspace(0.52, 3.98, n_points)}
        ds_hidden = generate_observable_dataset("heisenberg", n_qubits, hidden_grid, observables=["energy"])
        xs_hidden, ys_hidden = ds_hidden.to_arrays("energy")

        # 4. Out-of-domain extrapolation grid in [5.0, 10.0]
        extrap_grid = {"J": np.linspace(5.0, 10.0, n_points)}
        ds_extrap = generate_observable_dataset("heisenberg", n_qubits, extrap_grid, observables=["energy"])
        xs_extrap, ys_extrap = ds_extrap.to_arrays("energy")

    elif model == "ising":
        # Pure transverse field limit: E_0(h) = -N * h (J=0)
        # Training in [0.5, 4.0]
        train_grid = {"J": [0.0], "h": np.linspace(0.5, 4.0, n_points)}
        ds_train = generate_observable_dataset("ising", n_qubits, train_grid, observables=["energy"])
        xs_train, ys_train = ds_train.to_arrays("energy")

        val_grid = {"J": [0.0], "h": np.linspace(0.55, 3.95, n_points)}
        ds_val = generate_observable_dataset("ising", n_qubits, val_grid, observables=["energy"])
        xs_val, ys_val = ds_val.to_arrays("energy")

        hidden_grid = {"J": [0.0], "h": np.linspace(0.52, 3.98, n_points)}
        ds_hidden = generate_observable_dataset("ising", n_qubits, hidden_grid, observables=["energy"])
        xs_hidden, ys_hidden = ds_hidden.to_arrays("energy")

        extrap_grid = {"J": [0.0], "h": np.linspace(5.0, 10.0, n_points)}
        ds_extrap = generate_observable_dataset("ising", n_qubits, extrap_grid, observables=["energy"])
        xs_extrap, ys_extrap = ds_extrap.to_arrays("energy")
    else:
        raise ValueError(f"unknown model: {model}")

    splits = {
        "train": (xs_train[:, 0].ravel().astype(np.float32), ys_train.astype(np.float32)),
        "val": (xs_val[:, 0].ravel().astype(np.float32), ys_val.astype(np.float32)),
        "hidden": (xs_hidden[:, 0].ravel().astype(np.float32), ys_hidden.astype(np.float32)),
        "extrapolation": (xs_extrap[:, 0].ravel().astype(np.float32), ys_extrap.astype(np.float32)),
    }
    return ds_train.sha256_hash, splits


def run_q09_experiment(
    seeds: list[int],
    model: str = "heisenberg",
    n_qubits: int = 2,
    pop_size: int = 1000,
    max_generations: int = 80,
    tolerance: float = 1e-3,
) -> dict[str, Any]:
    """Execute blind symbolic rediscovery over seeds with hidden and extrapolation testing."""
    ds_hash, splits = generate_experiment_splits(model=model, n_qubits=n_qubits)
    xs_train, ys_train = splits["train"]
    xs_val, ys_val = splits["val"]
    xs_hidden, ys_hidden = splits["hidden"]
    xs_extrap, ys_extrap = splits["extrapolation"]

    records: list[dict[str, Any]] = []
    successes = 0

    print("=" * 115)
    print(f"Q09 QUANTUM FORMULA REDISCOVERY — {model.upper()} (N={n_qubits} Qubits)")
    print("=" * 115)
    print(f"  Dataset SHA-256 Hash : {ds_hash}")
    print(f"  Train Domain         : [{xs_train.min():.2f}, {xs_train.max():.2f}] ({len(xs_train)} points)")
    print(f"  Hidden Test Domain   : [{xs_hidden.min():.2f}, {xs_hidden.max():.2f}] ({len(xs_hidden)} points)")
    print(f"  Extrapolation Domain : [{xs_extrap.min():.2f}, {xs_extrap.max():.2f}] ({len(xs_extrap)} points)")
    print(f"  Population Size      : {pop_size}, Max Generations: {max_generations}")
    print(f"  Success Tolerance    : Hidden MSE <= {tolerance:.1e}")
    print("-" * 115)
    print(
        f"{'Seed':<5} | {'Gen':<4} | {'Eval':<6} | {'Time (s)':<8} | {'CVPS':<8} | "
        f"{'Train MSE':<11} | {'Hidden MSE':<11} | {'Extrap MSE':<11} | {'Result':<6} | {'Discovered Expression'}"
    )
    print("-" * 115)

    for seed in seeds:
        rng = np.random.default_rng(seed)
        config = EvolutionConfig(
            pop_size=pop_size,
            elite_k=32,
            tournament_size=4,
            crossover_p=0.5,
            gene_mut_p=0.15,
            large_mut_p=0.10,
            point_mut_p=0.03,
            random_inject_p=0.15,
            max_generations=max_generations,
            early_stop_fitness=1e-5,
            complexity_weight=0.0001,
        )

        res = run_evolution(
            xs_train=xs_train,
            ys_train=ys_train,
            config=config,
            rng=rng,
            xs_val=xs_val,
            ys_val=ys_val,
        )

        best_prog = res["best_program"]
        train_mse = res["best_mse"]

        # Evaluate on hidden and extrapolation test splits
        hidden_eval = evaluate(best_prog, xs_hidden, ys_hidden)
        hidden_mse = float(hidden_eval["mse"])

        extrap_eval = evaluate(best_prog, xs_extrap, ys_extrap)
        extrap_mse = float(extrap_eval["mse"])

        is_succ = (hidden_mse <= tolerance) and (extrap_mse <= tolerance * 10)
        if is_succ:
            successes += 1

        expr_str = res["best_expression"]
        verdict = "PASS" if is_succ else "FAIL"

        print(
            f"{seed:<5} | {res['generations']:<4} | {res['candidates_total']:<6} | {res['time_sec']:<8.3f} | {res['cvps']:<8.0f} | "
            f"{train_mse:<11.2e} | {hidden_mse:<11.2e} | {extrap_mse:<11.2e} | {verdict:<6} | {expr_str}"
        )

        records.append({
            "seed": seed,
            "generations": res["generations"],
            "candidates_total": res["candidates_total"],
            "time_sec": res["time_sec"],
            "cvps": res["cvps"],
            "train_mse": train_mse,
            "hidden_mse": hidden_mse,
            "extrapolation_mse": extrap_mse,
            "expression": expr_str,
            "success": is_succ,
        })

    success_rate = successes / len(seeds)
    mean_hidden = float(np.mean([r["hidden_mse"] for r in records]))
    mean_extrap = float(np.mean([r["extrapolation_mse"] for r in records]))

    print("-" * 115)
    print(
        f"SUMMARY: {successes}/{len(seeds)} successes ({success_rate * 100:.1f}%) | "
        f"Mean Hidden MSE: {mean_hidden:.2e} | Mean Extrapolation MSE: {mean_extrap:.2e}"
    )
    gate_passed = successes >= int(np.ceil(0.6 * len(seeds)))
    status_str = "PASS" if gate_passed else "FAIL"
    print(f"EXIT GATE VERDICT: {status_str}")
    print("=" * 115)

    return {
        "model": model,
        "n_qubits": n_qubits,
        "dataset_hash": ds_hash,
        "seeds": seeds,
        "successes": successes,
        "total_seeds": len(seeds),
        "success_rate": success_rate,
        "mean_hidden_mse": mean_hidden,
        "mean_extrapolation_mse": mean_extrap,
        "gate_passed": gate_passed,
        "records": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Q09 Quantum Formula Discovery Experiment")
    parser.add_argument("--seeds", type=int, default=5, help="Number of seeds (default: 5)")
    parser.add_argument("--model", type=str, default="heisenberg", choices=["heisenberg", "ising"])
    parser.add_argument("--qubits", type=int, default=2, help="Number of qubits (default: 2)")
    parser.add_argument("--pop_size", type=int, default=1000, help="Population size (default: 1000)")
    parser.add_argument("--generations", type=int, default=80, help="Max generations (default: 80)")
    parser.add_argument("--tol", type=float, default=1e-3, help="MSE tolerance (default: 1e-3)")
    parser.add_argument("--json", action="store_true", help="Output JSON results")
    args = parser.parse_args()

    seeds = list(range(args.seeds))
    res = run_q09_experiment(
        seeds=seeds,
        model=args.model,
        n_qubits=args.qubits,
        pop_size=args.pop_size,
        max_generations=args.generations,
        tolerance=args.tol,
    )

    if args.json:
        print(json.dumps(res, indent=2))

    return 0 if res["gate_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
