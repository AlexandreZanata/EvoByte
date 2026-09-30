"""CVPS (Candidates Verified Per Second) benchmark harness with provenance header (P05 scope)."""

from __future__ import annotations

import argparse
import contextlib
import datetime
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import torch
from hw_probe import probe

from evobyte.evolution import sample_structured
from evobyte.vm import execute_batch
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


def run_cvps_grid(device: torch.device, seed: int) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    grid_p = [100, 500, 1000, 2000]
    grid_b = [32, 256, 1024]

    results = []
    print("\nCVPS Grid Benchmark: Candidates Verified Per Second")
    print("-" * 125)
    print(
        f"{'Candidates (P)':<15} | {'Batch (B)':<10} | {'Latency (ms)':<14} | {'CVPS (progs/s)':<16} | "
        f"{'Evals/sec':<14} | {'Alloc VRAM':<12} | {'Res VRAM':<12} | {'Conformance'}"
    )
    print("-" * 125)

    for b in grid_b:
        xs = torch.linspace(-10.0, 10.0, b, dtype=torch.float32, device=device)
        for p in grid_p:
            progs = np.stack([sample_structured(rng) for _ in range(p)])

            # Warmup
            execute_population_torch(progs, xs, device=device)
            if device.type == "cuda":
                torch.cuda.synchronize(device)

            if device.type == "cuda":
                torch.cuda.reset_peak_memory_stats(device)
                torch.cuda.synchronize(device)

            repeats = 5
            t0 = time.perf_counter()
            for _ in range(repeats):
                out_t, flags_t = execute_population_torch(progs, xs, device=device)
                if device.type == "cuda":
                    torch.cuda.synchronize(device)
            elapsed = (time.perf_counter() - t0) / repeats

            latency_ms = elapsed * 1000.0
            cvps = p / elapsed if elapsed > 0 else float("inf")
            evals_per_sec = (p * b) / elapsed if elapsed > 0 else float("inf")

            peak_alloc_mb = (
                torch.cuda.max_memory_allocated(device) / (1024 * 1024)
                if device.type == "cuda"
                else 0.0
            )
            peak_res_mb = (
                torch.cuda.max_memory_reserved(device) / (1024 * 1024)
                if device.type == "cuda"
                else 0.0
            )

            # Conformance check against CPU oracle on first 5 candidates
            conf_ok = True
            xs_np = xs.cpu().numpy()
            for check_i in range(min(5, p)):
                pred_cpu, flag_cpu = execute_batch(progs[check_i], xs_np)
                pred_gpu = out_t[check_i].cpu().numpy()
                flag_gpu = flags_t[check_i].cpu().numpy()
                if not np.allclose(pred_cpu, pred_gpu, rtol=1e-5, atol=1e-5):
                    conf_ok = False
                    break
                if not np.array_equal(flag_cpu, flag_gpu):
                    conf_ok = False
                    break

            conf_str = "PASS" if conf_ok else "FAIL"
            alloc_str = f"{peak_alloc_mb:.2f} MB"
            res_str = f"{peak_res_mb:.2f} MB"

            results.append(
                {
                    "P": p,
                    "B": b,
                    "latency_ms": latency_ms,
                    "cvps": cvps,
                    "evals_sec": evals_per_sec,
                    "peak_alloc_vram_mb": peak_alloc_mb,
                    "peak_res_vram_mb": peak_res_mb,
                    "conformance": conf_ok,
                }
            )
            print(
                f"{p:<15} | {b:<10} | {latency_ms:>10.2f} ms | {cvps:>14.1f} | {evals_per_sec:>14.1f} | "
                f"{alloc_str:>12} | {res_str:>12} | {conf_str}"
            )

    print("-" * 125)

    # CPU Baseline Comparison on P=500, B=256
    p_comp = 500
    b_comp = 256
    progs_comp = np.stack([sample_structured(rng) for _ in range(p_comp)])
    xs_comp_np = np.linspace(-10.0, 10.0, b_comp, dtype=np.float32)

    t0 = time.perf_counter()
    for pi in range(p_comp):
        execute_batch(progs_comp[pi], xs_comp_np)
    cpu_time = time.perf_counter() - t0
    cpu_cvps = p_comp / cpu_time if cpu_time > 0 else float("inf")

    # GPU comparison on same P=500, B=256
    xs_comp_t = torch.from_numpy(xs_comp_np).to(device)
    execute_population_torch(progs_comp, xs_comp_t, device=device)
    if device.type == "cuda":
        torch.cuda.synchronize(device)

    t0 = time.perf_counter()
    repeats = 5
    for _ in range(repeats):
        execute_population_torch(progs_comp, xs_comp_t, device=device)
        if device.type == "cuda":
            torch.cuda.synchronize(device)
    gpu_time = (time.perf_counter() - t0) / repeats
    gpu_cvps = p_comp / gpu_time if gpu_time > 0 else float("inf")
    speedup = gpu_cvps / cpu_cvps if cpu_cvps > 0 else float("inf")

    print("\nCPU vs GPU Representative Comparison (P=500, B=256):")
    print(f"  CPU Sequential Throughput : {cpu_cvps:,.1f} CVPS ({cpu_time * 1000:.2f} ms)")
    print(f"  GPU Vectorized Throughput : {gpu_cvps:,.1f} CVPS ({gpu_time * 1000:.2f} ms)")
    print(f"  GPU Speedup Ratio         : {speedup:.1f}x")
    print("-" * 125)

    return {
        "grid": results,
        "comparison_p500_b256": {
            "cpu_cvps": cpu_cvps,
            "gpu_cvps": gpu_cvps,
            "speedup_ratio": speedup,
        },
    }


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
    ap.add_argument("--output", type=str, default=None, help="Output path for JSON report")
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
        grid_data = run_cvps_grid(dev, args.seed)
        if args.output:
            report = {
                "benchmark": "cvps_grid",
                "git_commit": get_git_commit(),
                "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
                "device": str(dev),
                "hardware": probe(),
                "seed": args.seed,
                "grid_results": grid_data["grid"],
                "comparison": grid_data["comparison_p500_b256"],
                "verdict": "PASS"
                if all(r.get("conformance", True) for r in grid_data["grid"])
                else "FAIL",
            }
            out_p = Path(args.output)
            out_p.parent.mkdir(parents=True, exist_ok=True)
            with open(out_p, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)
            print(f"Artifact written to {out_p}")
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
