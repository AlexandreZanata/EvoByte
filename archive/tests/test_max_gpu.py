"""Max-GPU stress tests for RTX 4060 Laptop (8GB): parallelism + threads, no crash (P21)."""

from __future__ import annotations

import concurrent.futures
import time
from pathlib import Path

import numpy as np
import pytest
import torch

from evobyte.batching import compute_chunk_size, execute_chunked
from evobyte.bytecode import decode_human
from evobyte.evolution import EvolutionConfig, sample_structured
from evobyte.provenance import resolve_device, seed_all, synchronize
from evobyte.resident import GPUResidentEvolution

VRAM_BUDGET_MB = 7000.0  # 8188 total - ~1188 reserve for driver/desktop/context
MAX_CHUNK_CAP = 20000  # kernel-launch sanity cap on top of byte model
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
needs_cuda = pytest.mark.skipif(not torch.cuda.is_available(), reason="requires CUDA 4060")


def _safe_chunk(n_points: int) -> int:
    return min(MAX_CHUNK_CAP, compute_chunk_size(n_points, VRAM_BUDGET_MB))


def _peak_mb(device: torch.device) -> tuple[float, float]:
    if device.type != "cuda":
        return 0.0, 0.0
    return (
        torch.cuda.max_memory_allocated(device) / (1024 * 1024),
        torch.cuda.max_memory_reserved(device) / (1024 * 1024),
    )


def _reset_peak(device: torch.device) -> None:
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)
        torch.cuda.empty_cache()


def test_max_chunk_grid_no_crash() -> None:
    """P x B grid at max safe chunk: chunked exec, peak VRAM bounded, spot conformance."""
    seed_all(42)
    torch.set_num_threads(8)
    dev = resolve_device(None)
    _reset_peak(dev)
    grid_p = [2000, 8000, 20000]
    grid_b = [32, 256, 1024]
    rng = np.random.default_rng(42)
    for b in grid_b:
        xs = torch.linspace(-5.0, 5.0, b, dtype=torch.float32, device=dev)
        chunk = _safe_chunk(b)
        assert chunk >= 1
        for p in grid_p:
            progs = np.stack([sample_structured(rng) for _ in range(p)])
            preds, flags = execute_chunked(
                progs, xs, chunk_size=chunk, vram_budget_mb=VRAM_BUDGET_MB, device=dev
            )
            synchronize(preds.device)
            assert preds.shape == (p, b)
            assert flags.shape == (p, b)
            peak_a, _peak_r = _peak_mb(dev)
            assert peak_a < VRAM_BUDGET_MB, f"OOM risk: peak {peak_a:.1f}MB at P={p} B={b}"
    # Spot conformance: GPU vs CPU on 64 programs must match exactly.
    progs = np.stack([sample_structured(rng) for _ in range(64)])
    xs64 = torch.linspace(-5.0, 5.0, 64, dtype=torch.float32, device=dev)
    pg, _ = execute_chunked(progs, xs64, chunk_size=_safe_chunk(64), device=dev)
    synchronize(pg.device)
    pc, _ = execute_chunked(progs, xs64.cpu(), chunk_size=512, device=torch.device("cpu"))
    assert torch.allclose(pg.cpu(), pc, atol=1e-5, rtol=1e-5)


@needs_cuda
def test_parallel_streams_and_threads() -> None:
    """2 CUDA streams + 8 CPU workers in parallel: same results as serial, no crash."""
    seed_all(7)
    torch.set_num_threads(8)
    torch.set_num_interop_threads(8)
    dev = torch.device("cuda")
    _reset_peak(dev)
    rng = np.random.default_rng(7)
    progs = np.stack([sample_structured(rng) for _ in range(4000)])
    xs = torch.linspace(-5.0, 5.0, 256, dtype=torch.float32, device=dev)
    chunk = _safe_chunk(256)
    halves = [progs[:2000], progs[2000:]]
    streams = [torch.cuda.Stream(device=dev), torch.cuda.Stream(device=dev)]
    outs: list = [None, None]

    def _run_on_stream(i: int) -> int:
        with torch.cuda.stream(streams[i]):
            p, f = execute_chunked(halves[i], xs, chunk_size=chunk, device=dev)
            torch.cuda.current_stream(dev).synchronize()
            outs[i] = (p.cpu(), f.cpu())
        return i

    # GPU halves on 2 streams in parallel + CPU decode/hash on 8 threads concurrently.
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        fut_gpu = [pool.submit(_run_on_stream, i) for i in (0, 1)]
        fut_cpu = [pool.submit(decode_human, progs[k]) for k in range(0, 4000, 500)]
        for f in concurrent.futures.as_completed(fut_gpu):
            f.result()
        decoded = [f.result() for f in fut_cpu]
    torch.cuda.synchronize(dev)
    assert all(isinstance(d, str) and len(d) > 0 for d in decoded)
    # Serial reference must match parallel streams exactly.
    pref, _ = execute_chunked(progs, xs, chunk_size=chunk, device=dev)
    synchronize(pref.device)
    cat = torch.cat([outs[0][0], outs[1][0]], dim=0)
    assert torch.allclose(cat, pref.cpu(), atol=1e-5, rtol=1e-5)
    peak_a, _ = _peak_mb(dev)
    assert peak_a < VRAM_BUDGET_MB


@needs_cuda
def test_sustained_max_10s() -> None:
    """10s resident evolution at P=2000 B=256: bounded VRAM, generations advance, telemetry sane."""
    seed_all(123)
    torch.set_num_threads(8)
    dev = torch.device("cuda")
    _reset_peak(dev)
    xs = np.linspace(-5.0, 5.0, 256, dtype=np.float32)
    ys = xs**2 + 3.0 * xs + 7.0
    cfg = EvolutionConfig(pop_size=2000, max_generations=1000000)
    evo = GPUResidentEvolution(xs, ys, config=cfg, device=dev)
    t0 = time.monotonic()
    res = evo.run(time_budget_sec=10.0)
    dt = time.monotonic() - t0
    assert res["generations"] >= 1
    # Early convergence (best_mse <= 1e-5) may stop before 10s: accept it as success.
    assert dt <= 16.0
    assert dt >= 9.0 or (res.get("converged") and res["best_mse"] <= 1e-5)
    peak_a, _ = _peak_mb(dev)
    assert peak_a < VRAM_BUDGET_MB
    assert np.isfinite(res["best_mse"])


def test_oom_safe_fallback() -> None:
    """Oversized chunk request falls back by halving instead of crashing."""
    seed_all(99)
    dev = resolve_device(None)
    _reset_peak(dev)
    rng = np.random.default_rng(99)
    progs = np.stack([sample_structured(rng) for _ in range(4000)])
    xs = torch.linspace(-5.0, 5.0, 1024, dtype=torch.float32, device=dev)
    # Absurd chunk (100k) must be clamped by execute_chunked/OOM retry, never crash.
    preds, _flags = execute_chunked(
        progs, xs, chunk_size=100000, vram_budget_mb=VRAM_BUDGET_MB, device=dev
    )
    synchronize(preds.device)
    assert preds.shape == (4000, 1024)
    peak_a, _ = _peak_mb(dev)
    assert peak_a < VRAM_BUDGET_MB
    _reset_peak(dev)


def test_p21_reproduction_gate_uses_manifest() -> None:
    """P21 exit-gate wiring: manifest reproduces without search (fast fixture)."""
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "benchmarks"))
    from full_matrix import run_reproduce_manifest

    repo = Path(__file__).resolve().parents[1]
    manifest = repo / "experiments" / "p13-manifest.json"
    if not manifest.exists():
        pytest.skip("p13-manifest.json not present")
    out = Path("/tmp/p21-maxgpu-check.json")
    report = run_reproduce_manifest(manifest, out)
    assert report["status"] == "PASS"
    assert len(report["raw_artifacts_verified"]) >= 1
    assert out.exists()
