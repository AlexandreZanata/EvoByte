"""CVPS (Candidates Verified Per Second) benchmark harness with provenance header (P05 scope)."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import torch

from evobyte.evolution import sample_structured
from evobyte.vm_torch import execute_population_torch, get_default_device
from hw_probe import probe


def get_git_commit() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=5
        )
        if out.returncode == 0:
            return out.stdout.strip()[:12]
    except Exception:
        pass
    return "unknown"


def print_provenance_header(device: torch.device, seed: int, data_hash: str) -> None:
    hw = probe()
    commit = get_git_commit()
    print("=" * 85)
    print("PROVENANCE & HARDWARE TELEMETRY")
    print("=" * 85)
    print(f"  Git Commit      : {commit}")
    print(f"  CPU             : {hw.get('cpu', 'unknown')}")
    print(f"  OS              : {hw.get('os', 'unknown')}")
    print(f"  Python          : {hw.get('python', sys.version.split()[0])}")
    print(f"  PyTorch         : {getattr(torch, '__version__', 'unknown')}")
    print(f"  CUDA Available  : {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"  GPU             : {torch.cuda.get_device_name(0)}")
        print(
            f"  Device Memory   : {torch.cuda.get_device_properties(0).total_memory // (1024 * 1024)} MB"
        )
    else:
        print(f"  GPU             : {hw.get('gpu', 'None (CPU execution)')}")
    print(f"  Active Device   : {device}")
    print(f"  Seed            : {seed}")
    print(f"  Dataset SHA256  : {data_hash}")
    print("=" * 85)


def run_cvps_grid(device: torch.device, seed: int) -> list[dict]:
    rng = np.random.default_rng(seed)
    grid_p = [100, 500, 1000, 2000]
    grid_b = [32, 256, 1024]

    results = []
    print("\nCVPS Grid Benchmark: Candidates Verified Per Second")
    print("-" * 85)
    print(
        f"{'Candidates (P)':<15} | {'Batch (B)':<10} | {'Latency (ms)':<14} | {'CVPS (progs/s)':<18} | {'Evals/sec'}"
    )
    print("-" * 85)

    for b in grid_b:
        xs = torch.linspace(-10.0, 10.0, b, dtype=torch.float32, device=device)
        for p in grid_p:
            progs = np.stack([sample_structured(rng) for _ in range(p)])

            # Warmup
            execute_population_torch(progs, xs, device=device)
            if device.type == "cuda":
                torch.cuda.synchronize()

            repeats = 5
            t0 = time.perf_counter()
            for _ in range(repeats):
                execute_population_torch(progs, xs, device=device)
                if device.type == "cuda":
                    torch.cuda.synchronize()
            elapsed = (time.perf_counter() - t0) / repeats

            latency_ms = elapsed * 1000.0
            cvps = p / elapsed if elapsed > 0 else float("inf")
            evals_per_sec = (p * b) / elapsed if elapsed > 0 else float("inf")

            results.append(
                {
                    "P": p,
                    "B": b,
                    "latency_ms": latency_ms,
                    "cvps": cvps,
                    "evals_sec": evals_per_sec,
                }
            )
            print(
                f"{p:<15} | {b:<10} | {latency_ms:>10.2f} ms | {cvps:>16.1f} | {evals_per_sec:>14.1f}"
            )

    print("-" * 85)
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description="CVPS Benchmark Harness")
    ap.add_argument("--grid", action="store_true", help="Run full (P x B) grid")
    ap.add_argument("--provenance", action="store_true", help="Print provenance telemetry")
    ap.add_argument("--seed", type=int, default=42, help="RNG seed")
    ap.add_argument("--device", type=str, default=None, help="Target device (cpu/cuda)")
    args = ap.parse_args()

    dev = torch.device(args.device) if args.device else get_default_device()

    xs_dummy = np.linspace(-10.0, 10.0, 256, dtype=np.float32)
    ys_dummy = xs_dummy**2 + 3 * xs_dummy + 7
    data_hash = hashlib.sha256(xs_dummy.tobytes() + ys_dummy.tobytes()).hexdigest()[:16]

    if args.provenance or args.grid:
        print_provenance_header(dev, args.seed, data_hash)

    if args.grid:
        run_cvps_grid(dev, args.seed)
    else:
        # Quick smoke run
        rng = np.random.default_rng(args.seed)
        progs = np.stack([sample_structured(rng) for _ in range(100)])
        xs = torch.linspace(-10.0, 10.0, 32, dtype=torch.float32, device=dev)
        t0 = time.perf_counter()
        execute_population_torch(progs, xs, device=dev)
        dt = time.perf_counter() - t0
        print(f"Smoke CVPS: {100 / dt:.1f} progs/sec (P=100, B=32, device={dev})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
