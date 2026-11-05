#!/usr/bin/env python3
"""Run small bivariate bicycle code exhaustive census (P222).

CLI that enumerates all (A, B) pairs over F_2[Z_l x Z_m] with 2 <= l*m <= max_lm,
computes exact k and exact d (up to wmax), outputs deterministically sorted JSON,
performs independent pure-Python re-verification (P221 stdlib), and generates summary.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from evobyte.bb_census import run_census
from tests.test_p221_independent_recompute import build as stdlib_build, distance as stdlib_distance


def sha256_of_file(filepath: Path | str) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def reverify_example(
    ex: dict[str, Any], n: int, k_expected: int, d_expected: int | None, d_gt: int | None
) -> dict[str, Any]:
    """Reverify a code using pure-Python stdlib distance from test_p221_independent_recompute."""
    l = ex["l"]
    m = ex["m"]
    a_exp = [tuple(p) for p in ex["A"]]
    b_exp = [tuple(p) for p in ex["B"]]

    hx_mat, hz_mat = stdlib_build(l, m, a_exp, b_exp)
    n_qubits = 2 * l * m
    assert n_qubits == n, f"Qubit mismatch: {n_qubits} != {n}"

    t0 = time.time()
    rx, rz, d = stdlib_distance(hx_mat, hz_mat, n_qubits)
    elapsed = time.time() - t0
    k = n_qubits - rx - rz

    if k != k_expected:
        raise RuntimeError(
            f"Independent reverification FAILED for n={n}, k={k_expected}: "
            f"got k={k} (rx={rx}, rz={rz})"
        )

    if d_expected is not None and d != d_expected:
        raise RuntimeError(
            f"Independent reverification FAILED for n={n}, k={k_expected}: "
            f"expected d={d_expected}, got d={d}"
        )

    if d_gt is not None and d <= d_gt:
        raise RuntimeError(
            f"Independent reverification FAILED for n={n}, k={k_expected}: "
            f"expected d > {d_gt}, got d={d}"
        )

    return {
        "n": n,
        "k": k,
        "rx": rx,
        "rz": rz,
        "d": d,
        "reverified": True,
        "elapsed_s": round(elapsed, 4),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run P222 BB Code Exhaustive Census")
    parser.add_argument(
        "--max-lm", type=int, default=16, help="Maximum l*m group size (default: 16)"
    )
    parser.add_argument("--min-l", type=int, default=2, help="Minimum l (default: 2)")
    parser.add_argument(
        "--wmax", type=int, default=7, help="Maximum search weight for distance (default: 7)"
    )
    parser.add_argument("--workers", type=int, default=16, help="Worker processes (default: 16)")
    parser.add_argument(
        "--out",
        type=str,
        default="experiments/p222-bb-census.json",
        help="Output census JSON path (default: experiments/p222-bb-census.json)",
    )
    parser.add_argument(
        "--summary",
        type=str,
        default="experiments/p222-bb-census-summary.json",
        help="Output summary JSON path (default: experiments/p222-bb-census-summary.json)",
    )
    args = parser.parse_args()

    out_path = Path(args.out)
    summary_path = Path(args.summary)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.parent.mkdir(parents=True, exist_ok=True)

    print(
        f"=== EvoByte P222 BB Code Census (max_lm={args.max_lm}, wmax={args.wmax}, workers={args.workers}) ==="
    )
    records, summary = run_census(
        max_lm=args.max_lm,
        wmax=args.wmax,
        workers=args.workers,
        min_l=args.min_l,
        log_fn=print,
    )

    print(f"Writing {len(records)} records to {out_path}...")
    with open(out_path, "w", encoding="utf-8") as f:
        for r in records:
            n, k, l, m, A, B, d_exact, d_gt = r
            line_dict = {
                "l": l,
                "m": m,
                "A": [list(p) for p in A],
                "B": [list(p) for p in B],
                "n": n,
                "k": k,
                "d_exact": d_exact,
                "d_gt": d_gt,
            }
            f.write(json.dumps(line_dict, separators=(",", ":")) + "\n")

    file_size = out_path.stat().st_size
    sha256_out = sha256_of_file(out_path)
    print(f"Census written: {out_path} ({file_size / (1024 * 1024):.2f} MB, sha256: {sha256_out})")

    # If larger than 50 MB, also produce compressed .jsonl.gz per P222 spec
    gz_path = None
    sha256_gz = None
    if file_size > 50 * 1024 * 1024:
        gz_target = out_path.with_name("p222-bb-census.jsonl.gz")
        print(f"File exceeds 50 MB limit ({file_size} bytes). Compressing to {gz_target}...")
        with open(out_path, "rb") as f_in, gzip.open(gz_target, "wb", compresslevel=9) as f_out:
            while chunk := f_in.read(1024 * 1024):
                f_out.write(chunk)
        gz_size = gz_target.stat().st_size
        sha256_gz = sha256_of_file(gz_target)
        gz_path = str(gz_target)
        print(
            f"Compressed archive: {gz_target} ({gz_size / (1024 * 1024):.2f} MB, sha256: {sha256_gz})"
        )

    # Independent reverification of best candidates with d >= 4
    print("=== Running Independent Pure-Python Reverification (stdlib) ===")
    reverified: list[dict[str, Any]] = []
    for key, info in sorted(summary["best_d"].items(), key=lambda it: (it[1]["n"], it[1]["k"])):
        n = info["n"]
        k = info["k"]
        best_d = info["best_d"]
        ex = info["example"]
        d_exact = ex["d_exact"]
        d_gt = ex["d_gt"]

        if best_d >= 4 or d_gt is not None:
            print(f"Reverifying (n={n}, k={k}, target_d={best_d})...", end=" ", flush=True)
            res = reverify_example(ex, n=n, k_expected=k, d_expected=d_exact, d_gt=d_gt)
            reverified.append(res)
            print(f"PASS (rx={res['rx']}, rz={res['rz']}, d={res['d']} in {res['elapsed_s']}s)")

    summary["independent_reverification"] = reverified
    summary["output_file"] = str(out_path)
    summary["output_file_size_bytes"] = file_size
    summary["output_file_sha256"] = sha256_out
    if gz_path is not None:
        summary["compressed_file"] = gz_path
        summary["compressed_file_sha256"] = sha256_gz

    # Output Calibration Gate
    print("=== Checking Output Calibration Gate ===")
    best_16_2 = summary["best_d"].get("16_2")
    if best_16_2 is not None:
        if best_16_2["best_d"] != 4:
            raise RuntimeError(
                f"STOP: Output calibration failed for (n=16, k=2): "
                f"expected max d=4, got {best_16_2['best_d']}"
            )
        print("Calibration (n=16, k=2) -> max d=4: PASS")

    best_20_2 = summary["best_d"].get("20_2")
    if best_20_2 is not None:
        if best_20_2["best_d"] != 6:
            raise RuntimeError(
                f"STOP: Output calibration failed for (n=20, k=2): "
                f"expected max d=6, got {best_20_2['best_d']}"
            )
        print("Calibration (n=20, k=2) -> max d=6: PASS")

    # Write summary
    print(f"Writing summary to {summary_path}...")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Summary written: {summary_path}")

    # Print summary table
    print("\n=== Best Distance Table (n, k) ===")
    print(
        f"{'n':>4} | {'k':>4} | {'best_d':>6} | {'exact?':>6} | {'count':>8} | {'example group':>13}"
    )
    print("-" * 55)
    for key, info in sorted(summary["best_d"].items(), key=lambda it: (it[1]["n"], it[1]["k"])):
        ex = info["example"]
        grp = f"Z_{ex['l']} x Z_{ex['m']}"
        exact_str = "yes" if info["is_exact"] else "no"
        print(
            f"{info['n']:>4} | {info['k']:>4} | {info['best_d']:>6} | {exact_str:>6} | {info['count']:>8} | {grp:>13}"
        )

    print(f"\nCensus completed successfully in {summary['elapsed_seconds']}s.")


if __name__ == "__main__":
    main()
