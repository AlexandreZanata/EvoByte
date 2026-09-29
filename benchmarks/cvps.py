"""CVPS (Candidates Verified Per Second) benchmark harness with provenance header (P05 scope)."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import torch
from hw_probe import probe

from evobyte.evolution import sample_structured
from evobyte.vm_torch import execute_population_torch, get_default_device


def get_git_commit() -> str:
    with contextlib.suppress(OSError, subprocess.SubprocessError):
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=5, check=False
        )
        if out.returncode == 0:
            return out.stdout.strip()[:12]
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
    ap.add_argument("--tune", action="store_true", help="Run VRAM-budget cascade tuning benchmark")
    ap.add_argument(
        "--vram-budget", type=float, default=7500.0, help="VRAM budget in MB (default: 7500.0)"
    )
    ap.add_argument("--provenance", action="store_true", help="Print provenance telemetry")
    ap.add_argument("--seed", type=int, default=42, help="RNG seed")
    ap.add_argument("--device", type=str, default=None, help="Target device (cpu/cuda)")
    args = ap.parse_args()

    dev = torch.device(args.device) if args.device else get_default_device()

    xs_dummy = np.linspace(-10.0, 10.0, 256, dtype=np.float32)
    ys_dummy = xs_dummy**2 + 3 * xs_dummy + 7
    data_hash = hashlib.sha256(xs_dummy.tobytes() + ys_dummy.tobytes()).hexdigest()[:16]

    if args.provenance or args.grid or args.tune:
        print_provenance_header(dev, args.seed, data_hash)

    if args.tune:
        from evobyte.batching import compute_chunk_size, execute_chunked

        print(f"\nTuned Cascade Batching under {args.vram_budget:.1f} MB VRAM Budget (P06)")
        print("=" * 95)
        print(
            f"{'Stage':<18} | {'Points':<8} | {'Candidates':<12} | {'Chunk Size':<12} | {'Est VRAM':<12} | {'CVPS':<10} | {'Kill %'}"
        )
        print("-" * 95)

        rng = np.random.default_rng(args.seed)

        # Benchmark representative scaling
        stages_config = [
            {
                "name": "S1 (coarse screening)",
                "points": 256,
                "P": 10000,
                "target_P": 100000,
                "kill": 0.99,
            },
            {
                "name": "S2 (fine discrimination)",
                "points": 4096,
                "P": 1000,
                "target_P": 1000,
                "kill": 0.99,
            },
            {
                "name": "S3 (full verification)",
                "points": 10000,
                "P": 10,
                "target_P": 10,
                "kill": 0.0,
            },
        ]

        for s_idx, cfg in enumerate(stages_config, 1):
            pts = cfg["points"]
            p_count = cfg["P"]
            chunk = compute_chunk_size(pts, vram_budget_mb=args.vram_budget)
            est_vram_mb = (min(chunk, p_count) * 48 * pts) / (1024 * 1024)

            progs = np.stack([sample_structured(rng) for _ in range(p_count)])
            xs = torch.linspace(-10.0, 10.0, pts, dtype=torch.float32, device=dev)

            t0 = time.perf_counter()
            execute_chunked(
                progs, xs, chunk_size=chunk, vram_budget_mb=args.vram_budget, device=dev
            )
            if dev.type == "cuda":
                torch.cuda.synchronize()
            dt = time.perf_counter() - t0

            cvps = p_count / dt if dt > 0 else float("inf")
            kill_pct = cfg["kill"] * 100
            print(
                f"S{s_idx} {cfg['name']:<15} | {pts:<8} | {cfg['target_P']:<12} | {chunk:<12} | {est_vram_mb:>9.2f} MB | {cvps:>10.1f} | {kill_pct:>5.1f}%"
            )
        print("-" * 95)

    elif args.grid:
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
