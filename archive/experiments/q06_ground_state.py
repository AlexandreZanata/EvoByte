"""Experiment script for Q06: Ground-state candidate search across seeds.

Evolves compact variational ansatze scored strictly by Rayleigh quotient <ψ|H|ψ>,
evaluating E_cand - E_exact and fidelity post-hoc with TTS and TTE reporting.
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

from evobyte.quantum.ground import decode_ansatz, evolve_ground_state, to_statevector
from evobyte.quantum.hamiltonians import hamiltonian_hash, heisenberg, ising
from evobyte.quantum.oracle import exact, ground_state_fidelity
from hw_probe import probe


def get_git_commit() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=5)
        if out.returncode == 0:
            return out.stdout.strip()[:12]
    except Exception:
        pass
    return "unknown"


def run_q06_ground_state_experiment(
    seeds: list[int],
    n_qubits: int = 2,
    model: str = "heisenberg",
    pop_size: int = 40,
    generations: int = 40,
    n_terms: int = 4,
    target_tol: float = 1e-3,
) -> dict[str, Any]:
    """Execute ground-state candidate search over seeds reporting TTS and TTE."""
    # 1. Target Hamiltonian
    if model == "heisenberg":
        h_terms = heisenberg(n_qubits, j=1.0)
    elif model == "ising":
        h_terms = ising(n_qubits, j=1.0, h=1.0)
    else:
        raise ValueError(f"unknown model: {model}")

    h_hash = hamiltonian_hash(h_terms)
    oracle_truth = exact(h_terms, n_qubits)
    e_exact = float(oracle_truth["E_exact"])

    # Compute ground subspace degeneracy
    evals = oracle_truth["energies"]
    gs_deg = int(np.sum(np.abs(evals - e_exact) < 1e-6))

    records: list[dict[str, Any]] = []
    successes = 0

    print("=" * 110)
    print(f"Q06 GROUND-STATE CANDIDATE SEARCH — {model.upper()} (N={n_qubits} Qubits)")
    print("=" * 110)
    print(f"  Target Hamiltonian : {model} (N={n_qubits}) hash={h_hash}")
    print(f"  Oracle Provenance  : E_exact={e_exact:.8f}, Degeneracy={gs_deg}, Terms={len(h_terms)}")
    print(f"  Selection Score    : Rayleigh quotient <ψ|H|ψ> ONLY (zero oracle leakage)")
    print(f"  Target Tolerance   : |E_cand - E_exact| <= {target_tol:.1e}")
    print(f"  Search Population  : {pop_size}, Max Generations: {generations}, Max Terms: {n_terms}")
    print("-" * 110)
    print(
        f"{'Seed':<5} | {'Gen':<4} | {'Eval':<6} | {'Time (s)':<8} | {'QVPS':<8} | "
        f"{'E_cand':<11} | {'E_exact':<11} | {'Delta E':<10} | {'Fidelity':<8} | {'TTS (s)':<8} | {'TTE':<5} | {'Result'}"
    )
    print("-" * 110)

    for seed in seeds:
        res = evolve_ground_state(
            h_terms,
            n_qubits=n_qubits,
            pop_size=pop_size,
            generations=generations,
            n_terms=n_terms,
            seed=seed,
            target_energy=e_exact,
            target_energy_tol=target_tol,
            oracle_truth=oracle_truth,
        )

        e_cand = res["energy_candidate"]
        delta_e = res["energy_error"]
        fid = res["fidelity"]
        tts = res["tts_s"]
        tte = res["tte_evals"]
        is_succ = res["success"] and (fid is not None and fid > 0.95)

        if is_succ:
            successes += 1

        tts_str = f"{tts:.5f}" if tts is not None else "N/A"
        tte_str = str(tte) if tte is not None else "N/A"
        fid_str = f"{fid:.4f}" if fid is not None else "N/A"
        verdict = "PASS" if is_succ else "FAIL"

        print(
            f"{seed:<5} | {res['generations_run']:<4} | {res['evaluations']:<6} | {res['elapsed_s']:<8.4f} | {res['qvps']:<8.0f} | "
            f"{e_cand:<11.6f} | {e_exact:<11.6f} | {delta_e:<10.2e} | {fid_str:<8} | {tts_str:<8} | {tte_str:<5} | {verdict}"
        )

        records.append({
            "seed": seed,
            "generations_run": res["generations_run"],
            "best_generation": res["best_generation"],
            "evaluations": res["evaluations"],
            "elapsed_s": res["elapsed_s"],
            "qvps": res["qvps"],
            "e_cand": e_cand,
            "e_exact": e_exact,
            "delta_e": delta_e,
            "fidelity": fid,
            "tts_s": tts,
            "tte_evals": tte,
            "success": is_succ,
        })

    success_rate = successes / len(seeds)
    valid_tts = [r["tts_s"] for r in records if r["tts_s"] is not None]
    valid_tte = [r["tte_evals"] for r in records if r["tte_evals"] is not None]
    valid_fid = [r["fidelity"] for r in records if r["fidelity"] is not None]

    mean_tts = float(np.mean(valid_tts)) if valid_tts else 0.0
    mean_tte = float(np.mean(valid_tte)) if valid_tte else 0.0
    mean_fid = float(np.mean(valid_fid)) if valid_fid else 0.0

    print("-" * 110)
    print(
        f"SUMMARY: {successes}/{len(seeds)} successes ({success_rate * 100:.1f}%) | "
        f"Mean TTS: {mean_tts:.5f}s | Mean TTE: {mean_tte:.1f} evals | Mean Fidelity: {mean_fid:.4f}"
    )
    gate_passed = successes >= int(np.ceil(0.6 * len(seeds)))
    status_str = "PASS" if gate_passed else "FAIL"
    print(f"EXIT GATE VERDICT: {status_str}")
    print("=" * 110)

    return {
        "model": model,
        "n_qubits": n_qubits,
        "seeds": seeds,
        "h_hash": h_hash,
        "e_exact": e_exact,
        "gs_deg": gs_deg,
        "target_tol": target_tol,
        "successes": successes,
        "total_seeds": len(seeds),
        "success_rate": success_rate,
        "mean_tts_s": mean_tts,
        "mean_tte_evals": mean_tte,
        "mean_fidelity": mean_fid,
        "gate_passed": gate_passed,
        "records": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Q06 Ground State Search Experiment")
    parser.add_argument("--seeds", type=int, default=5, help="Number of seeds (default: 5)")
    parser.add_argument("--qubits", type=int, default=2, help="Number of qubits (default: 2)")
    parser.add_argument("--model", type=str, default="heisenberg", choices=["heisenberg", "ising"])
    parser.add_argument("--pop_size", type=int, default=40, help="Population size (default: 40)")
    parser.add_argument("--generations", type=int, default=40, help="Max generations (default: 40)")
    parser.add_argument("--terms", type=int, default=4, help="Candidate terms (default: 4)")
    parser.add_argument("--tol", type=float, default=1e-3, help="Energy error tolerance (default: 1e-3)")
    parser.add_argument("--all", action="store_true", help="Run across benchmark matrix (N=2,3 Heisenberg & Ising)")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    args = parser.parse_args()

    seeds = list(range(args.seeds))

    if args.all:
        benchmarks = [
            ("heisenberg", 2),
            ("ising", 2),
            ("heisenberg", 3),
            ("ising", 3),
        ]
        all_passed = True
        all_results = []
        for mod, nq in benchmarks:
            res = run_q06_ground_state_experiment(
                seeds=seeds,
                n_qubits=nq,
                model=mod,
                pop_size=args.pop_size,
                n_terms=(1 << nq) if mod == "ising" else min(1 << nq, max(args.terms, 1 << (nq - 1))),
                target_tol=args.tol,
            )
            all_results.append(res)
            if not res["gate_passed"]:
                all_passed = False

        if args.json:
            print(json.dumps(all_results, indent=2))
        return 0 if all_passed else 1

    res = run_q06_ground_state_experiment(
        seeds=seeds,
        n_qubits=args.qubits,
        model=args.model,
        pop_size=args.pop_size,
        generations=args.generations,
        n_terms=args.terms,
        target_tol=args.tol,
    )

    if args.json:
        print(json.dumps(res, indent=2))

    return 0 if res["gate_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
