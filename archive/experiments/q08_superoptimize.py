"""Experiment script for Q08: Circuit superoptimization across seeds.

Demonstrates superoptimization of redundant quantum circuits:
finds certified equivalent circuits with strictly fewer gates, shallower depth,
and fewer two-qubit operations, returning exact equivalence certificates.
"""

from __future__ import annotations

import argparse
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

from evobyte.quantum.circuit import (
    OPCODE_CNOT,
    OPCODE_H,
    OPCODE_X,
    OPCODE_Z,
    CircuitInstruction,
    circuit_depth,
    decode_circuit_text,
    gate_count,
    two_qubit_count,
)
from evobyte.quantum.circuit_evo import check_circuit_equivalence, superoptimize_circuit
from hw_probe import probe


def get_git_commit() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=5)
        if out.returncode == 0:
            return out.stdout.strip()[:12]
    except Exception:
        pass
    return "unknown"


def build_benchmark_circuits() -> dict[str, dict[str, Any]]:
    """Build canonical redundant benchmark circuits for superoptimization."""
    # 1. Redundant Bell preparation circuit (6 gates -> 2 gates)
    c_bell_redundant = [
        CircuitInstruction(OPCODE_X, 0),
        CircuitInstruction(OPCODE_X, 0),
        CircuitInstruction(OPCODE_H, 0),
        CircuitInstruction(OPCODE_Z, 1),
        CircuitInstruction(OPCODE_Z, 1),
        CircuitInstruction(OPCODE_CNOT, 0, 1),
    ]

    # 2. Redundant GHZ 3-qubit circuit (7 gates -> 3 gates)
    c_ghz_redundant = [
        CircuitInstruction(OPCODE_H, 0),
        CircuitInstruction(OPCODE_CNOT, 0, 1),
        CircuitInstruction(OPCODE_X, 2),
        CircuitInstruction(OPCODE_X, 2),
        CircuitInstruction(OPCODE_CNOT, 1, 2),
        CircuitInstruction(OPCODE_Z, 0),
        CircuitInstruction(OPCODE_Z, 0),
    ]

    # 3. Redundant Identity cancellation (4 gates -> 0 gates)
    c_ident_redundant = [
        CircuitInstruction(OPCODE_H, 0),
        CircuitInstruction(OPCODE_CNOT, 0, 1),
        CircuitInstruction(OPCODE_CNOT, 0, 1),
        CircuitInstruction(OPCODE_H, 0),
    ]

    return {
        "bell_redundant": {
            "name": "Redundant Bell Circuit",
            "n_qubits": 2,
            "circuit": c_bell_redundant,
            "target_gate_reduction": 4,
        },
        "ghz_redundant": {
            "name": "Redundant GHZ Circuit",
            "n_qubits": 3,
            "circuit": c_ghz_redundant,
            "target_gate_reduction": 4,
        },
        "identity_cancellation": {
            "name": "Identity Involutions",
            "n_qubits": 2,
            "circuit": c_ident_redundant,
            "target_gate_reduction": 4,
        },
    }


def run_benchmark(
    bench_key: str,
    bench_data: dict[str, Any],
    seeds: list[int],
    pop_size: int = 50,
    generations: int = 40,
) -> dict[str, Any]:
    """Run superoptimization experiment over seeds for a benchmark circuit."""
    c_ref = bench_data["circuit"]
    n_qubits = bench_data["n_qubits"]
    name = bench_data["name"]

    g_ref = gate_count(c_ref)
    d_ref = circuit_depth(c_ref, n_qubits)
    q2_ref = two_qubit_count(c_ref)

    records: list[dict[str, Any]] = []
    successes = 0

    print("=" * 115)
    print(f"Q08 SUPEROPTIMIZATION BENCHMARK — {name.upper()} (N={n_qubits} Qubits)")
    print("=" * 115)
    print(f"  Reference Circuit : {decode_circuit_text(c_ref)}")
    print(f"  Reference Profile : Gates={g_ref}, Depth={d_ref}, 2-Qubit={q2_ref}")
    print(f"  Target Goal       : Reduce gates by >= {bench_data['target_gate_reduction']} with exact equivalence")
    print(f"  Search Population : {pop_size}, Max Generations: {generations}")
    print("-" * 115)
    print(
        f"{'Seed':<5} | {'Gen':<4} | {'Eval':<6} | {'Time (s)':<8} | {'QVPS':<8} | "
        f"{'Orig(G/D/2Q)':<13} | {'Opt(G/D/2Q)':<12} | {'Delta(G/D/2Q)':<14} | {'Fidelity':<8} | {'Equiv?':<6} | {'Result'}"
    )
    print("-" * 115)

    for seed in seeds:
        res = superoptimize_circuit(
            circuit_ref=c_ref,
            n_qubits=n_qubits,
            pop_size=pop_size,
            generations=generations,
            seed=seed,
            allowed_opcodes=[OPCODE_H, OPCODE_CNOT, OPCODE_X, OPCODE_Z],
        )

        cert = res["certificate"]
        opt_c = res["best_circuit"]
        is_succ = cert.is_equivalent and (cert.gate_reduction >= bench_data["target_gate_reduction"])

        if is_succ:
            successes += 1

        orig_str = f"{cert.orig_gates}/{cert.orig_depth}/{cert.orig_two_qubits}"
        opt_str = f"{cert.opt_gates}/{cert.opt_depth}/{cert.opt_two_qubits}"
        delta_str = f"-{cert.gate_reduction}/-{cert.depth_reduction}/-{cert.two_qubit_reduction}"
        equiv_str = "YES" if cert.is_equivalent else "NO"
        verdict = "PASS" if is_succ else "FAIL"

        print(
            f"{seed:<5} | {res['generations_run']:<4} | {res['evaluations']:<6} | {res['elapsed_s']:<8.4f} | {res['qvps']:<8.0f} | "
            f"{orig_str:<13} | {opt_str:<12} | {delta_str:<14} | {cert.process_fidelity:<8.4f} | {equiv_str:<6} | {verdict}"
        )

        records.append({
            "seed": seed,
            "generations_run": res["generations_run"],
            "evaluations": res["evaluations"],
            "elapsed_s": res["elapsed_s"],
            "qvps": res["qvps"],
            "opt_circuit_text": decode_circuit_text(opt_c),
            "orig_gates": cert.orig_gates,
            "orig_depth": cert.orig_depth,
            "orig_two_qubits": cert.orig_two_qubits,
            "opt_gates": cert.opt_gates,
            "opt_depth": cert.opt_depth,
            "opt_two_qubits": cert.opt_two_qubits,
            "gate_reduction": cert.gate_reduction,
            "depth_reduction": cert.depth_reduction,
            "two_qubit_reduction": cert.two_qubit_reduction,
            "process_fidelity": cert.process_fidelity,
            "global_phase_angle": cert.global_phase_angle,
            "frobenius_error": cert.frobenius_error,
            "is_equivalent": cert.is_equivalent,
            "success": is_succ,
        })

    success_rate = successes / len(seeds)
    mean_gate_red = float(np.mean([r["gate_reduction"] for r in records]))
    mean_depth_red = float(np.mean([r["depth_reduction"] for r in records]))
    mean_2q_red = float(np.mean([r["two_qubit_reduction"] for r in records]))

    print("-" * 115)
    print(
        f"BENCHMARK SUMMARY: {successes}/{len(seeds)} certified ({success_rate * 100:.1f}%) | "
        f"Mean Gate Reduction: -{mean_gate_red:.1f} | Mean Depth Reduction: -{mean_depth_red:.1f} | Mean 2Q Reduction: -{mean_2q_red:.1f}"
    )
    print("=" * 115)

    return {
        "benchmark": bench_key,
        "name": name,
        "n_qubits": n_qubits,
        "ref_gates": g_ref,
        "ref_depth": d_ref,
        "ref_two_qubits": q2_ref,
        "successes": successes,
        "total_seeds": len(seeds),
        "success_rate": success_rate,
        "mean_gate_reduction": mean_gate_red,
        "mean_depth_reduction": mean_depth_red,
        "mean_two_qubit_reduction": mean_2q_red,
        "gate_passed": successes >= len(seeds),
        "records": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Q08 Circuit Superoptimization Experiment")
    parser.add_argument("--seeds", type=int, default=3, help="Number of seeds (default: 3)")
    parser.add_argument("--pop_size", type=int, default=50, help="Population size (default: 50)")
    parser.add_argument("--generations", type=int, default=40, help="Max generations (default: 40)")
    parser.add_argument("--bench", type=str, default="all", choices=["all", "bell", "ghz", "identity"])
    parser.add_argument("--json", action="store_true", help="Output JSON results")
    args = parser.parse_args()

    benchmarks = build_benchmark_circuits()
    seeds = list(range(args.seeds))

    if args.bench == "all":
        to_run = list(benchmarks.items())
    elif args.bench == "bell":
        to_run = [("bell_redundant", benchmarks["bell_redundant"])]
    elif args.bench == "ghz":
        to_run = [("ghz_redundant", benchmarks["ghz_redundant"])]
    else:
        to_run = [("identity_cancellation", benchmarks["identity_cancellation"])]

    all_passed = True
    all_results = []

    for b_key, b_data in to_run:
        res = run_benchmark(
            bench_key=b_key,
            bench_data=b_data,
            seeds=seeds,
            pop_size=args.pop_size,
            generations=args.generations,
        )
        all_results.append(res)
        if not res["gate_passed"]:
            all_passed = False

    print("\n" + "=" * 80)
    status_str = "PASS (ALL BENCHMARKS CERTIFIED)" if all_passed else "FAIL"
    print(f"OVERALL EXIT GATE VERDICT: {status_str}")
    print("=" * 80 + "\n")

    if args.json:
        print(json.dumps(all_results, indent=2))

    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
