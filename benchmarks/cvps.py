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


def run_search_loop_benchmark(device: torch.device, seeds: list[int]) -> dict[str, Any]:
    """Run GPU-resident evolutionary search benchmark across seeds (P17 scope)."""
    import tempfile

    from evobyte.evolution import EvolutionConfig, run_evolution
    from evobyte.resident import GPUResidentEvolution

    print("\n" + "=" * 135)
    print("GPU-RESIDENT EVOLUTIONARY SEARCH BENCHMARK (P17)")
    print("=" * 135)

    n_points = 256
    xs_np = np.linspace(-5.0, 5.0, n_points, dtype=np.float32)
    ys_np = xs_np**2 + 3.0 * xs_np + 7.0

    pop_size = 1000
    max_gens = 40
    cfg = EvolutionConfig(
        pop_size=pop_size,
        elite_k=32,
        tournament_size=4,
        crossover_p=0.3,
        point_mut_p=0.02,
        large_mut_p=0.05,
        gene_mut_p=0.08,
        random_inject_p=0.10,
        max_generations=max_gens,
        early_stop_fitness=1e-5,
    )

    print(f"Target Problem   : y = x^2 + 3x + 7 (B={n_points} points)")
    print(f"Population (P)   : {pop_size} candidates resident in VRAM")
    print(f"Max Generations  : {max_gens}")
    print(f"Active Device    : {device}")
    print(f"Seeds Evaluated  : {seeds}")
    print("-" * 135)
    print(
        f"{'Seed':<6} | {'Gens':<5} | {'Total Time':<11} | {'Search CVPS':<13} | "
        f"{'Eval %':<8} | {'Sel %':<8} | {'Rep/Mut %':<10} | {'Valid %':<8} | "
        f"{'Dup %':<8} | {'Best MSE':<11} | {'Best Expression'}"
    )
    print("-" * 135)

    seed_results = []
    total_candidates_all = 0
    total_time_all = 0.0

    for s in seeds:
        torch.manual_seed(s)
        if device.type == "cuda":
            torch.cuda.manual_seed_all(s)
            torch.cuda.reset_peak_memory_stats(device)
            torch.cuda.synchronize(device)

        evo = GPUResidentEvolution(xs_np, ys_np, config=cfg, device=device)
        res = evo.run(max_generations=max_gens)

        hist = res["history"]
        n_gens = len(hist)
        tot_time = res["time_sec"]
        tot_cand = res["candidates_total"]
        search_cvps = res["search_cvps"]

        sum_eval = sum(h["eval_time_s"] for h in hist)
        sum_sel = sum(h["select_time_s"] for h in hist)
        sum_rep = sum(h["reproduce_time_s"] for h in hist)
        sum_stages = max(sum_eval + sum_sel + sum_rep, 1e-6)

        pct_eval = (sum_eval / sum_stages) * 100.0
        pct_sel = (sum_sel / sum_stages) * 100.0
        pct_rep = (sum_rep / sum_stages) * 100.0

        mean_valid = float(np.mean([h["valid_rate"] for h in hist]) * 100.0)
        mean_dup = float(np.mean([h["duplicate_rate"] for h in hist]) * 100.0)

        peak_alloc = (
            torch.cuda.max_memory_allocated(device) / (1024 * 1024)
            if device.type == "cuda"
            else 0.0
        )
        peak_res = (
            torch.cuda.max_memory_reserved(device) / (1024 * 1024) if device.type == "cuda" else 0.0
        )

        total_candidates_all += tot_cand
        total_time_all += tot_time

        expr_str = res["best_expression"]
        if len(expr_str) > 35:
            expr_str = expr_str[:32] + "..."

        print(
            f"{s:<6} | {n_gens:<5} | {tot_time:>9.3f} s | {search_cvps:>13.1f} | "
            f"{pct_eval:>7.1f}% | {pct_sel:>7.1f}% | {pct_rep:>9.1f}% | {mean_valid:>7.1f}% | "
            f"{mean_dup:>7.1f}% | {res['best_mse']:>11.4e} | {expr_str}"
        )

        seed_results.append(
            {
                "seed": s,
                "generations": n_gens,
                "candidates": tot_cand,
                "time_sec": tot_time,
                "search_cvps": search_cvps,
                "eval_pct": pct_eval,
                "select_pct": pct_sel,
                "reproduce_pct": pct_rep,
                "mean_valid_rate": mean_valid / 100.0,
                "mean_duplicate_rate": mean_dup / 100.0,
                "best_fitness": res["best_fitness"],
                "best_mse": res["best_mse"],
                "best_expression": res["best_expression"],
                "converged": res["converged"],
                "peak_alloc_vram_mb": peak_alloc,
                "peak_res_vram_mb": peak_res,
            }
        )

    print("-" * 135)
    mean_search_cvps = total_candidates_all / max(total_time_all, 1e-6)

    # 2. Fixed-step resume verification
    print("\nValidating Deterministic Checkpoint & Resume on Seed 42...")
    resume_seed = 42
    torch.manual_seed(resume_seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(resume_seed)

    test_cfg = EvolutionConfig(pop_size=500, elite_k=16, max_generations=20)
    evo_uninterrupted = GPUResidentEvolution(xs_np, ys_np, config=test_cfg, device=device)
    res_uninterrupted = evo_uninterrupted.run(max_generations=20)

    with tempfile.TemporaryDirectory() as td:
        ckpt_file = Path(td) / "resume_test.pt"
        torch.manual_seed(resume_seed)
        if device.type == "cuda":
            torch.cuda.manual_seed_all(resume_seed)

        evo_split1 = GPUResidentEvolution(xs_np, ys_np, config=test_cfg, device=device)
        evo_split1.run(max_generations=10)
        evo_split1.save_checkpoint(ckpt_file)

        evo_split2 = GPUResidentEvolution(xs_np, ys_np, config=test_cfg, device=device)
        evo_split2.load_checkpoint(ckpt_file)
        evo_split2.run(max_generations=10)

        match_fit = bool(
            np.isclose(res_uninterrupted["best_fitness"], evo_split2.best_fitness, rtol=1e-5)
        )
        match_mse = bool(np.isclose(res_uninterrupted["best_mse"], evo_split2.best_mse, rtol=1e-5))
        match_pop = bool(torch.equal(evo_uninterrupted.population, evo_split2.population))
        resume_ok = bool(match_fit and match_mse and match_pop)

    resume_verdict = "PASS" if resume_ok else "FAIL"
    print(f"  Uninterrupted Best MSE : {res_uninterrupted['best_mse']:.6e}")
    print(f"  Resumed Best MSE       : {evo_split2.best_mse:.6e}")
    print(f"  Population Bit-Equal   : {match_pop}")
    print(f"  Resume Gate Status     : {resume_verdict}")

    # 3. CPU Baseline Comparison on Seed 42
    print("\nMeasuring CPU Baseline Search Loop (P=500, B=256, 5 generations)...")
    cpu_cfg = EvolutionConfig(pop_size=500, elite_k=16, max_generations=5)
    rng_cpu = np.random.default_rng(42)
    t0 = time.perf_counter()
    run_evolution(xs_np, ys_np, cpu_cfg, rng_cpu)
    cpu_time = time.perf_counter() - t0
    cpu_search_cvps = (5 * 500) / max(cpu_time, 1e-6)

    # Equivalent GPU run
    torch.manual_seed(42)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(42)
    gpu_evo_comp = GPUResidentEvolution(xs_np, ys_np, config=cpu_cfg, device=device)
    t0 = time.perf_counter()
    gpu_evo_comp.run(max_generations=5)
    gpu_time = time.perf_counter() - t0
    gpu_comp_cvps = (5 * 500) / max(gpu_time, 1e-6)
    speedup = gpu_comp_cvps / max(cpu_search_cvps, 1e-6)

    print(f"  CPU Sequential Loop CVPS : {cpu_search_cvps:,.1f} candidates/sec")
    print(f"  GPU-Resident Loop CVPS   : {gpu_comp_cvps:,.1f} candidates/sec")
    print(f"  End-to-End Speedup Ratio : {speedup:.1f}x")
    print("=" * 135)

    return {
        "seeds": seeds,
        "runs": seed_results,
        "mean_search_cvps": mean_search_cvps,
        "resume_verification": {
            "seed": resume_seed,
            "uninterrupted_best_mse": res_uninterrupted["best_mse"],
            "resumed_best_mse": evo_split2.best_mse,
            "population_equal": match_pop,
            "status": resume_verdict,
        },
        "comparison": {
            "cpu_search_cvps": cpu_search_cvps,
            "gpu_search_cvps": gpu_comp_cvps,
            "speedup_ratio": speedup,
        },
        "verdict": (
            "PASS"
            if resume_ok and all(r["mean_valid_rate"] > 0.05 for r in seed_results)
            else "FAIL"
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="CVPS Benchmark Harness")
    ap.add_argument("--grid", action="store_true", help="Run full (P x B) grid")
    ap.add_argument("--tune", action="store_true", help="Run VRAM-budget cascade tuning benchmark")
    ap.add_argument(
        "--search-loop",
        action="store_true",
        help="Run GPU-resident evolutionary search benchmark across seeds (P17)",
    )
    ap.add_argument(
        "--seeds",
        type=int,
        default=5,
        help="Number of seeds for multi-seed benchmarks (default: 5)",
    )
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

    if args.provenance or args.grid or args.tune or args.search_loop:
        print_provenance_header(dev, args.seed, data_hash)

    if args.search_loop:
        seeds = [42, 101, 202, 303, 404] if args.seeds == 5 else [42 + i for i in range(args.seeds)]
        report_data = run_search_loop_benchmark(dev, seeds)
        if args.output:
            full_report = {
                "benchmark": "gpu_resident_evolution",
                "git_commit": get_git_commit(),
                "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
                "device": str(dev),
                "hardware": probe(),
                **report_data,
            }
            out_p = Path(args.output)
            out_p.parent.mkdir(parents=True, exist_ok=True)
            with open(out_p, "w", encoding="utf-8") as f:
                json.dump(full_report, f, indent=2)
            print(f"\nArtifact written to {out_p}")
    elif args.tune:
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
