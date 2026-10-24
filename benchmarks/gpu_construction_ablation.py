"""CPU vs GPU ablation for priority scoring (P175)."""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np
import torch

from evobyte.bytecode import encode_instr, is_valid, nop_program
from evobyte.constructive_torch import (
    GPU_CPU_TOLERANCE,
    peak_vram_mb,
    score_batch_torch,
    within_tolerance,
)


def gen_triples(n: int, seed: int):
    rng = np.random.default_rng(seed)
    ops = [
        0x01,
        0x02,
        0x03,
        0x04,
        0x05,
        0x06,
        0x07,
        0x08,
        0x09,
        0x0A,
        0x0B,
        0x0C,
        0x0D,
        0x0E,
        0x0F,
        0x10,
        0x11,
    ]
    progs, feats, ctxs = [], [], []
    attempts = 0
    while len(progs) < n and attempts < n * 50:
        attempts += 1
        p = nop_program()
        for s in range(8):
            op = int(rng.choice(ops))
            dst, a = int(rng.integers(0, 8)), int(rng.integers(0, 8))
            b = int(rng.integers(0, 16)) if op in (0x0F, 0x10, 0x11) else int(rng.integers(0, 8))
            p[s] = encode_instr(op, dst, a, b)
        if not is_valid(p):
            continue
        progs.append(p.copy())
        feats.append([float(rng.normal(0, 2)) for _ in range(7)])
        ctxs.append([float(rng.normal(0, 2)) for _ in range(5)])
    assert len(progs) == n, f"only {len(progs)}/{n} valid programs sampled"
    return progs, feats, ctxs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--device", default=None)
    parser.add_argument("--seed", type=int, default=175)
    parser.add_argument("--n", type=int, default=2000)
    args = parser.parse_args()

    n, seed = int(args.n), int(args.seed)
    progs, feats, ctxs = gen_triples(n, seed)

    t0 = time.perf_counter()
    cpu_scores = score_batch_torch(progs, feats, ctxs, device="cpu")
    cpu_sec = time.perf_counter() - t0

    gpu_available = torch.cuda.is_available() and (args.device != "cpu")
    out: dict = {
        "n": n,
        "seed": seed,
        "cpu_sec": float(cpu_sec),
        "tolerance": float(GPU_CPU_TOLERANCE),
        "torch_version": str(torch.__version__),
        "cuda_version": str(torch.version.cuda) if torch.cuda.is_available() else None,
    }
    if not gpu_available:
        out.update(
            {
                "gpu_available": False,
                "gpu_sec": None,
                "speedup": None,
                "peak_vram_mb": None,
                "max_abs_diff": None,
            }
        )
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(json.dumps(out, indent=2), encoding="utf-8")
        print(f"no CUDA; cpu_sec={cpu_sec:.3f}s n={n}")
        return

    dev = torch.device(args.device) if args.device else None
    # Steady-state warmup (CUDA init + allocator outside the timed region).
    score_batch_torch(progs[:64], feats[:64], ctxs[:64], device=args.device)
    try:
        torch.cuda.reset_peak_memory_stats(dev)
    except Exception:
        pass
    t0 = time.perf_counter()
    gpu_scores = score_batch_torch(progs, feats, ctxs, device=args.device)
    gpu_sec = time.perf_counter() - t0
    peak = peak_vram_mb(args.device)
    try:
        dev_name = torch.cuda.get_device_name(dev)
    except Exception:
        dev_name = None

    diffs = []
    rel_diffs = []
    in_tol = 0
    for a, b in zip(cpu_scores, gpu_scores):
        if a == b == float("-inf"):
            diffs.append(0.0)
            rel_diffs.append(0.0)
            in_tol += 1
        elif not (math.isfinite(a) and math.isfinite(b)):
            diffs.append(float("inf"))
            rel_diffs.append(float("inf"))
        else:
            diffs.append(abs(a - b))
            rel_diffs.append(abs(a - b) / max(1.0, abs(b)))
            if within_tolerance(b, a):
                in_tol += 1
    max_diff = max(diffs) if diffs else 0.0
    max_rel = max(rel_diffs) if rel_diffs else 0.0
    speedup = float(cpu_sec / gpu_sec) if gpu_sec > 0 else None
    out.update(
        {
            "gpu_available": True,
            "gpu_sec": float(gpu_sec),
            "speedup": speedup,
            "peak_vram_mb": peak,
            "max_abs_diff": float(max_diff),
            "max_rel_diff": float(max_rel),
            "in_tolerance": int(in_tol),
            "tolerance_note": "allclose rtol=atol=1e-5 (repo convention); abs diff is magnitude-dependent in float32",
            "device": str(dev) if dev is not None else "cuda",
            "device_name": dev_name,
        }
    )
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(
        f"cpu={cpu_sec:.3f}s gpu={gpu_sec:.3f}s speedup={speedup:.2f}x peak={peak}MB maxdiff={max_diff:.2e}"
    )


if __name__ == "__main__":
    main()
