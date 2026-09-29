"""Pauli algebra throughput benchmark with provenance tracking (Q01 scope).

Measures operations per second for symplectic commutation and multiplication
across millions of random mask pairs on CPU, validating parity-rate sanity.
"""

from __future__ import annotations

import argparse
import datetime
import json
import subprocess
import sys
import time
from pathlib import Path

# Add project root and benchmarks directory to import path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np

from evobyte.quantum.pauli import Pauli, commutes_with, multiply
from hw_probe import probe


def get_git_info() -> dict[str, str]:
    """Capture current git provenance."""
    info = {"commit": "unknown", "branch": "unknown", "clean": "unknown"}
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=5
        )
        if out.returncode == 0:
            info["commit"] = out.stdout.strip()[:12]
        out_branch = subprocess.run(
            ["git", "branch", "--show-current"], capture_output=True, text=True, timeout=5
        )
        if out_branch.returncode == 0:
            info["branch"] = out_branch.stdout.strip()
        out_status = subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True, timeout=5
        )
        if out_status.returncode == 0:
            info["clean"] = "true" if not out_status.stdout.strip() else "false"
    except Exception:
        pass
    return info


def generate_pauli_pairs(
    n: int, n_qubits: int = 64, seed: int = 0
) -> tuple[list[Pauli], list[Pauli], list[int], list[int], list[int], list[int]]:
    """Generate n pairs of random Pauli operators and raw int masks."""
    rng = np.random.default_rng(seed)
    if n_qubits == 64:
        x1_raw = rng.integers(0, 2**64, size=n, dtype=np.uint64)
        z1_raw = rng.integers(0, 2**64, size=n, dtype=np.uint64)
        x2_raw = rng.integers(0, 2**64, size=n, dtype=np.uint64)
        z2_raw = rng.integers(0, 2**64, size=n, dtype=np.uint64)
    else:
        x1_raw = rng.integers(0, 1 << n_qubits, size=n, dtype=np.uint64)
        z1_raw = rng.integers(0, 1 << n_qubits, size=n, dtype=np.uint64)
        x2_raw = rng.integers(0, 1 << n_qubits, size=n, dtype=np.uint64)
        z2_raw = rng.integers(0, 1 << n_qubits, size=n, dtype=np.uint64)

    p1_phases = rng.integers(0, 4, size=n, dtype=np.int32)
    p2_phases = rng.integers(0, 4, size=n, dtype=np.int32)

    x1_list = [int(v) for v in x1_raw]
    z1_list = [int(v) for v in z1_raw]
    x2_list = [int(v) for v in x2_raw]
    z2_list = [int(v) for v in z2_raw]

    p1_list = [Pauli(x1_list[i], z1_list[i], int(p1_phases[i]), n_qubits) for i in range(n)]
    p2_list = [Pauli(x2_list[i], z2_list[i], int(p2_phases[i]), n_qubits) for i in range(n)]
    return p1_list, p2_list, x1_list, z1_list, x2_list, z2_list


def benchmark_pauli_algebra(n: int = 1_000_000, n_qubits: int = 64, seed: int = 0) -> dict:
    """Run full benchmark suite over n random Pauli pairs."""
    t0_gen = time.perf_counter()
    p1s, p2s, x1s, z1s, x2s, z2s = generate_pauli_pairs(n, n_qubits=n_qubits, seed=seed)
    gen_time = time.perf_counter() - t0_gen

    # 1. High-level commutes_with (Pauli object)
    t0 = time.perf_counter()
    c_obj = 0
    for i in range(n):
        if commutes_with(p1s[i], p2s[i]):
            c_obj += 1
    t1 = time.perf_counter()
    time_comm_obj = t1 - t0
    ops_comm_obj = n / time_comm_obj if time_comm_obj > 0 else 0.0
    rate_comm_obj = c_obj / n

    # 2. High-level multiply (Pauli object)
    t0 = time.perf_counter()
    for i in range(n):
        multiply(p1s[i], p2s[i])
    t1 = time.perf_counter()
    time_mul_obj = t1 - t0
    ops_mul_obj = n / time_mul_obj if time_mul_obj > 0 else 0.0

    # 3. Raw int bit-op commutation (XOR/AND/POPCOUNT)
    t0 = time.perf_counter()
    c_raw = 0
    for i in range(n):
        if (((x1s[i] & z2s[i]).bit_count() + (z1s[i] & x2s[i]).bit_count()) & 1) == 0:
            c_raw += 1
    t1 = time.perf_counter()
    time_comm_raw = t1 - t0
    ops_comm_raw = n / time_comm_raw if time_comm_raw > 0 else 0.0
    rate_comm_raw = c_raw / n

    # 4. Raw int bit-op multiply (XOR/AND/POPCOUNT/Z4).
    # Keep the computations even though only their elapsed time is reported.
    t0 = time.perf_counter()
    for i in range(n):
        _rx = x1s[i] ^ x2s[i]
        _rz = z1s[i] ^ z2s[i]
        _rphase = (2 * ((z1s[i] & x2s[i]).bit_count() & 1)) & 3
    t1 = time.perf_counter()
    time_mul_raw = t1 - t0
    ops_mul_raw = n / time_mul_raw if time_mul_raw > 0 else 0.0

    # Parity sanity: for n_qubits >= 8, theoretical is 0.500000
    expected_rate = 0.5 + 0.5 * (4.0 ** (-n_qubits))
    rate_diff = abs(rate_comm_obj - expected_rate)
    parity_sanity_pass = rate_diff < 0.01

    return {
        "n": n,
        "n_qubits": n_qubits,
        "seed": seed,
        "generation_time_s": gen_time,
        "commutes_with_obj": {
            "elapsed_s": time_comm_obj,
            "ops_per_sec": ops_comm_obj,
            "commute_count": c_obj,
            "commute_rate": rate_comm_obj,
        },
        "multiply_obj": {
            "elapsed_s": time_mul_obj,
            "ops_per_sec": ops_mul_obj,
        },
        "commutes_with_raw": {
            "elapsed_s": time_comm_raw,
            "ops_per_sec": ops_comm_raw,
            "commute_count": c_raw,
            "commute_rate": rate_comm_raw,
        },
        "multiply_raw": {
            "elapsed_s": time_mul_raw,
            "ops_per_sec": ops_mul_raw,
        },
        "parity_sanity": {
            "expected_rate": expected_rate,
            "empirical_rate": rate_comm_obj,
            "delta": rate_diff,
            "passed": parity_sanity_pass,
        },
    }


def print_provenance_header(hw: dict, git: dict, n: int, n_qubits: int, seed: int) -> None:
    print("=" * 85)
    print("Q-FORGE PAULI ALGEBRA BENCHMARK — PROVENANCE & TELEMETRY")
    print("=" * 85)
    print(
        f"  Git Commit          : {git.get('commit', 'unknown')} (branch: {git.get('branch', 'unknown')}, clean: {git.get('clean', 'unknown')})"
    )
    print(f"  Timestamp           : {datetime.datetime.now(datetime.timezone.utc).isoformat()}")
    print(f"  CPU                 : {hw.get('cpu', 'unknown')}")
    print(f"  OS                  : {hw.get('os', 'unknown')}")
    print(f"  Python              : {hw.get('python', sys.version.split()[0])}")
    print(f"  NumPy               : {hw.get('numpy', np.__version__)}")
    print(f"  Pairs Tested (N)    : {n:,}")
    print(f"  Qubits (Width)      : {n_qubits}")
    print(f"  Random Seed         : {seed}")
    print("=" * 85)


def print_results(res: dict) -> None:
    comm_obj = res["commutes_with_obj"]
    mul_obj = res["multiply_obj"]
    comm_raw = res["commutes_with_raw"]
    mul_raw = res["multiply_raw"]
    sanity = res["parity_sanity"]

    print("\nBENCHMARK RESULTS (CPU Baseline):")
    print("-" * 85)
    print(
        f"{'Operation / Layer':<35} | {'Count':>10} | {'Time (s)':>10} | {'Throughput (ops/s)':>20}"
    )
    print("-" * 85)
    print(
        f"{'commutes_with (Pauli object)':<35} | {res['n']:>10,} | {comm_obj['elapsed_s']:>10.3f} | {comm_obj['ops_per_sec']:>20,.0f}"
    )
    print(
        f"{'multiply (Pauli object)':<35} | {res['n']:>10,} | {mul_obj['elapsed_s']:>10.3f} | {mul_obj['ops_per_sec']:>20,.0f}"
    )
    print(
        f"{'raw_commute (XOR/AND/POPCNT)':<35} | {res['n']:>10,} | {comm_raw['elapsed_s']:>10.3f} | {comm_raw['ops_per_sec']:>20,.0f}"
    )
    print(
        f"{'raw_multiply (XOR/AND/POPCNT/Z4)':<35} | {res['n']:>10,} | {mul_raw['elapsed_s']:>10.3f} | {mul_raw['ops_per_sec']:>20,.0f}"
    )
    print("-" * 85)

    print("\nPARITY-RATE SANITY CHECK:")
    print("-" * 85)
    print(
        f"  Empirical Commutation Rate : {sanity['empirical_rate']:.6f} ({comm_obj['commute_count']:,} / {res['n']:,})"
    )
    print(f"  Theoretical Expected Rate  : {sanity['expected_rate']:.6f}")
    print(f"  Deviation (|Emp - Exp|)    : {sanity['delta']:.6f} (tolerance: < 0.010000)")
    status_str = (
        "PASS (rate within binomial bounds)"
        if sanity["passed"]
        else "FAIL (rate deviates unexpectedly)"
    )
    print(f"  Sanity Verdict             : {status_str}")
    print("=" * 85)


def main() -> int:
    parser = argparse.ArgumentParser(description="Q-Forge Pauli Algebra Throughput Benchmark")
    parser.add_argument(
        "--n", type=int, default=1_000_000, help="Number of random Pauli pairs (default: 1000000)"
    )
    parser.add_argument("--seed", type=int, default=0, help="Random seed (default: 0)")
    parser.add_argument(
        "--qubits", type=int, default=64, help="Number of qubits per operator (default: 64)"
    )
    parser.add_argument("--json", action="store_true", help="Output JSON results")
    args = parser.parse_args()

    hw = probe()
    git = get_git_info()

    if not args.json:
        print_provenance_header(hw, git, args.n, args.qubits, args.seed)

    res = benchmark_pauli_algebra(n=args.n, n_qubits=args.qubits, seed=args.seed)
    res["telemetry"] = {
        "hardware": hw,
        "git": git,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }

    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print_results(res)

    if not res["parity_sanity"]["passed"]:
        print("\nERROR: Parity sanity check failed!", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
