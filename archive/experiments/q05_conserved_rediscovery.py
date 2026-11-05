"""Experiment script for Q05: Blind rediscovery of conserved operators across 5 seeds.

Evolves Pauli operator candidates against small laboratory Hamiltonians without
symmetry hints, evaluated against hidden parameter splits for generalization.
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

from evobyte.quantum.evolution_q import evolve_conserved_operator
from evobyte.quantum.hamiltonians import (
    PauliTerm,
    commutator_norm,
    decode_hamiltonian,
    hamiltonian_hash,
    heisenberg,
    ising,
)
from evobyte.quantum.oracle import exact
from hw_probe import probe


def get_git_commit() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=5)
        if out.returncode == 0:
            return out.stdout.strip()[:12]
    except Exception:
        pass
    return "unknown"


def run_q05_rediscovery(
    seeds: list[int],
    n_qubits: int = 3,
    model: str = "heisenberg",
    pop_size: int = 60,
    generations: int = 50,
    n_terms: int = 4,
    early_stop_tol: float = 1e-7,
) -> dict[str, Any]:
    """Execute blind evolutionary rediscovery over seeds with hidden generalization scoring."""
    # 1. Target training Hamiltonian
    if model == "heisenberg":
        h_train = heisenberg(n_qubits, j=1.0)
        # Hidden parameter split: perturbed coupling J=1.37
        h_hidden = heisenberg(n_qubits, j=1.37)
    elif model == "ising":
        h_train = ising(n_qubits, j=1.0, h=1.0)
        # Hidden parameter split: perturbed J=1.42, h=0.85
        h_hidden = ising(n_qubits, j=1.42, h=0.85)
    else:
        raise ValueError(f"unknown model: {model}")

    train_hash = hamiltonian_hash(h_train)
    hidden_hash = hamiltonian_hash(h_hidden)
    oracle_owe = exact(h_train, n_qubits)

    records: list[dict[str, Any]] = []
    successes = 0

    print("=" * 95)
    print(f"Q05 CONSERVED-OPERATOR BLIND REDISCOVERY — {model.upper()} (N={n_qubits} Qubits)")
    print("=" * 95)
    print(f"  Training Hamiltonian : {model} (N={n_qubits}) hash={train_hash} E_exact={oracle_owe['E_exact']:.6f}")
    print(f"  Hidden Test Split    : {model} perturbed hash={hidden_hash}")
    print(f"  Seeds Tested         : {seeds}")
    print(f"  Search Population    : {pop_size}, Max Generations: {generations}, Terms: {n_terms}")
    print(f"  Success Threshold    : commutator error < {early_stop_tol:.1e}")
    print("-" * 95)
    print(f"{'Seed':<5} | {'Gen':<5} | {'QVPS':<8} | {'Time (s)':<8} | {'Train Norm':<12} | {'Hidden Norm':<12} | {'Result':<8} | {'Candidate Operator'}")
    print("-" * 95)

    for seed in seeds:
        res = evolve_conserved_operator(
            h_train,
            n_qubits=n_qubits,
            pop_size=pop_size,
            generations=generations,
            n_terms=n_terms,
            seed=seed,
            early_stop_tol=early_stop_tol,
        )

        cand = res["best_candidate"]
        train_norm = res["commutator_error"]
        hidden_norm = commutator_norm(h_hidden, cand, n_qubits)
        is_success = (train_norm < early_stop_tol) and (hidden_norm < early_stop_tol * 2)

        if is_success:
            successes += 1

        cand_str = decode_hamiltonian(cand, n_qubits)
        verdict = "SUCCESS" if is_success else "FAIL"

        print(
            f"{seed:<5} | {res['generations_run']:<5} | {res['qvps']:<8.0f} | {res['elapsed_s']:<8.3f} | "
            f"{train_norm:<12.2e} | {hidden_norm:<12.2e} | {verdict:<8} | {cand_str}"
        )

        records.append({
            "seed": seed,
            "generations_run": res["generations_run"],
            "evaluations": res["evaluations"],
            "elapsed_s": res["elapsed_s"],
            "qvps": res["qvps"],
            "train_norm": train_norm,
            "hidden_norm": hidden_norm,
            "success": is_success,
            "candidate_decoded": cand_str,
        })

    success_rate = successes / len(seeds)
    print("-" * 95)
    print(f"REDISCOVERY SUMMARY: {successes}/{len(seeds)} successes (Rate: {success_rate * 100:.1f}%)")
    gate_status = "PASS (rate >= 3/5)" if successes >= 3 else "FAIL (rate < 3/5)"
    print(f"EXIT GATE VERDICT  : {gate_status}")
    print("=" * 95)

    return {
        "model": model,
        "n_qubits": n_qubits,
        "seeds": seeds,
        "train_hash": train_hash,
        "hidden_hash": hidden_hash,
        "successes": successes,
        "total_seeds": len(seeds),
        "success_rate": success_rate,
        "gate_passed": successes >= 3,
        "records": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Q05 Conserved Operator Rediscovery Experiment")
    parser.add_argument("--seeds", type=int, default=5, help="Number of seeds to run (default: 5)")
    parser.add_argument("--qubits", type=int, default=3, help="Number of qubits (default: 3)")
    parser.add_argument("--model", type=str, default="heisenberg", choices=["heisenberg", "ising"])
    parser.add_argument("--pop_size", type=int, default=60, help="Population size (default: 60)")
    parser.add_argument("--generations", type=int, default=50, help="Generations (default: 50)")
    parser.add_argument("--terms", type=int, default=4, help="Candidate terms (default: 4)")
    parser.add_argument("--json", action="store_true", help="Output JSON results")
    args = parser.parse_args()

    seeds = list(range(args.seeds))
    res = run_q05_rediscovery(
        seeds=seeds,
        n_qubits=args.qubits,
        model=args.model,
        pop_size=args.pop_size,
        generations=args.generations,
        n_terms=args.terms,
    )

    if args.json:
        print(json.dumps(res, indent=2))

    return 0 if res["gate_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
