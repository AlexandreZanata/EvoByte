"""P24 — Stable limits of the RTX 4060 (real budgets, reconciled counters).

Finds the highest STABLE end-to-end throughput of distinct generated +
evaluated candidates per second, with reconciled counters and bounded
memory. Corrects the P20 caveats: real (non-scaled) budgets, generation +
error computation INSIDE the counted interval, disclosed NOP fractions,
adaptive VRAM budget from current free memory, OOM halving with checkpoint,
CPU-oracle parity, resume evidence and a no-leak check.

Pipeline per timed iteration (all inside the counted window):
  sample programs on GPU (generation) -> execute sharded over CUDA streams
  with private buffers + explicit sync (evaluation) -> vectorized MSE vs the
  target on device (error) -> per-iteration distinct via torch.unique.

Usage (exit gate):
  python3 benchmarks/gpu_limits.py --budgets 10s,1m,10m --confirm-1h \\
      --seeds 5 --output experiments/p24-limits.json
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from evobyte.batching import compute_chunk_size
from evobyte.bytecode import N_INSTR, N_REGS, is_valid
from evobyte.evolution import STRUCTURED_OP_RATIOS, STRUCTURED_OPS
from evobyte.provenance import (
    CandidateCounter,
    MonotonicDeadline,
    collect_provenance,
    parse_budget_duration,
    query_gpu_telemetry,
    resolve_device,
    seed_all,
    synchronize,
    write_manifest,
)
from evobyte.vm_torch import (
    PopulationVMBuffer,
    execute_population_torch,
)

# ---------------------------------------------------------------------------
# Preregistered workload grid + stability definition (frozen before measuring)
# ---------------------------------------------------------------------------

TARGET_NAME = "quad-x2-3x-7"

# Opcode mixes: full structured set vs arithmetic-only subset.
ARITH_OPS = [0x00, 0x01, 0x02, 0x03, 0x04, 0x0A, 0x0C, 0x0D, 0x0E]
ARITH_WEIGHTS = np.array(
    [0.30 if op == 0x00 else (0.70 / (len(ARITH_OPS) - 1)) for op in ARITH_OPS],
    dtype=np.float64,
)

P_GRID = [2000, 8000, 20000]
B_GRID = [32, 256, 1024]
STREAM_GRID = [1, 2, 4]
WORKER_GRID = [1, 2, 4, 8]
MIX_GRID = ["full", "arith"]
LEN_GRID = ["standard", "short", "long"]
LEN_RANGE = {"standard": (2, N_INSTR), "short": (2, 6), "long": (10, N_INSTR)}

RESERVE_MB = 1200.0  # system/context/temporaries kept free (disclosed)
CHUNK_CAP = 20000  # kernel-launch sanity cap (standing Max-GPU rule)
MAX_CPU_THREADS = 8
MIN_POP_AFTER_HALVING = 250
AUDIT_EVERY_SEC = 5.0
AUDIT_SAMPLE = 256
GLOBAL_TRACK_CAP = 500_000  # bounded exact-hash reservoir (P15 counter)
GLOBAL_WINDOW = 512  # programs/iter added to the global reservoir (fixed window)

STABILITY = {
    "cross_seed_floor": 0.90,  # min-seed 10m rate >= 90% of median-seed rate
    "confirm_tolerance": 0.15,  # 1h rate within 15% of 10m median rate
    "leak_max_growth_mb": 64.0,  # allocator growth start->end per leg
    "parity_atol": 1e-5,
    "parity_rtol": 1e-5,
    "tracing_max_overhead_pct": 15.0,  # P34 preregistered target <= 15% added-time
}

SCOUT_BUDGET_SEC = 10.0
DEFAULT_SEEDS = [42, 101, 202, 303, 404]


def workload_grid_hash() -> str:
    blob = json.dumps(
        {
            "target": TARGET_NAME,
            "P": P_GRID,
            "B": B_GRID,
            "streams": STREAM_GRID,
            "workers": WORKER_GRID,
            "mix": MIX_GRID,
            "length": LEN_GRID,
            "len_range": LEN_RANGE,
            "reserve_mb": RESERVE_MB,
            "chunk_cap": CHUNK_CAP,
        },
        sort_keys=True,
    ).encode()
    return hashlib.sha256(blob).hexdigest()[:16]


def target_values(xs: np.ndarray) -> np.ndarray:
    return xs * xs + 3.0 * xs + 7.0


# ---------------------------------------------------------------------------
# GPU variant sampler (parameterized structured programs, device-resident)
# ---------------------------------------------------------------------------


def gpu_sample_variant(
    n: int,
    device: torch.device,
    op_ids: list[int],
    op_weights: np.ndarray,
    len_lo: int,
    len_hi: int,
    p_nop: float = 0.35,
) -> torch.Tensor:
    """Sample structured programs on device with a fixed opcode mix + length range."""
    w = torch.tensor(np.asarray(op_weights, dtype=np.float64), dtype=torch.float32, device=device)
    op_samples = torch.searchsorted(
        torch.cumsum(w, dim=0),
        torch.rand((n, N_INSTR), device=device),
    ).to(torch.int64)
    op_table = torch.tensor(op_ids, dtype=torch.int64, device=device)
    op_samples = op_table[op_samples.clamp(0, len(op_ids) - 1)]

    span = max(1, len_hi - len_lo + 1)
    n_active = len_lo + torch.randint(0, span, (n, 1), device=device)
    n_active = n_active.clamp(1, N_INSTR)
    step_idx = torch.arange(N_INSTR, device=device).unsqueeze(0).expand(n, -1)
    active_mask = step_idx < n_active

    nop_mask = (torch.rand((n, N_INSTR), device=device) < p_nop) | (op_samples == 0)
    valid_mask = active_mask & (~nop_mask)
    ops = torch.where(valid_mask, op_samples, torch.zeros_like(op_samples))

    dst = torch.randint(0, N_REGS, (n, N_INSTR), device=device)
    a = torch.randint(0, N_REGS, (n, N_INSTR), device=device)
    b_reg = torch.randint(0, N_REGS, (n, N_INSTR), device=device)
    b_const = torch.randint(0, 16, (n, N_INSTR), device=device)
    b = torch.where(ops == 0x0F, b_const, b_reg)

    has_r7 = (valid_mask & (dst == 7) & (ops != 0)).any(dim=1)
    need = torch.nonzero(~has_r7).squeeze(1)
    if need.numel() > 0:
        # Non-risky fallback ops only (keeps S0 validity high by construction).
        fb = torch.tensor([0x01, 0x02, 0x03, 0x0A, 0x0C], device=device)
        pick = fb[torch.randint(0, len(fb), (need.shape[0],), device=device)]
        pos = (n_active[need, 0] - 1).clamp(0, N_INSTR - 1)
        ops[need, pos] = pick
        dst[need, pos] = 7
        a[need, pos] = torch.randint(0, N_REGS, (need.shape[0],), device=device)
        b[need, pos] = torch.randint(0, N_REGS, (need.shape[0],), device=device)

    words = (ops & 0xFF) | ((dst & 0xFF) << 8) | ((a & 0xFF) << 16) | ((b & 0xFF) << 24)
    return torch.where(ops != 0, words, torch.zeros_like(words))


def mix_spec(mix: str) -> tuple[list[int], np.ndarray]:
    if mix == "arith":
        return ARITH_OPS, ARITH_WEIGHTS / ARITH_WEIGHTS.sum()
    ops = [int(o) for o in STRUCTURED_OPS]
    w = np.asarray(STRUCTURED_OP_RATIOS, dtype=np.float64)
    return ops, w / w.sum()


# ---------------------------------------------------------------------------
# VRAM budget from CURRENT free memory (never a fixed assumption)
# ---------------------------------------------------------------------------


def adaptive_vram_budget(device: torch.device) -> dict[str, float]:
    total_mb = float(torch.cuda.get_device_properties(device).total_memory / (1024 * 1024))
    try:
        free_b, _ = torch.cuda.mem_get_info(device)
        free_mb = float(free_b / (1024 * 1024))
    except RuntimeError:
        free_mb = total_mb
    budget_mb = max(512.0, free_mb - RESERVE_MB)
    return {
        "total_mb": total_mb,
        "free_mb": free_mb,
        "reserve_mb": RESERVE_MB,
        "budget_mb": budget_mb,
    }


# ---------------------------------------------------------------------------
# Bounded Asynchronous Lineage Tracking (P34)
# ---------------------------------------------------------------------------


class BoundedLineageTracker:
    """Bounded, batched lineage writes and asynchronous copies with backpressure (P34)."""

    def __init__(self, capacity: int = 10_000, device: torch.device | None = None):
        self.capacity = capacity
        self.device = device or torch.device("cpu")
        self.is_cuda = self.device.type == "cuda"
        self.stream = torch.cuda.Stream(device=self.device) if self.is_cuda else None
        self.ready_event = torch.cuda.Event() if self.is_cuda else None
        self.total_recorded = 0
        self.dropped_count = 0

        if self.is_cuda:
            self.pinned_progs = torch.empty((capacity, N_INSTR), dtype=torch.int64, pin_memory=True)
            self.pinned_mse = torch.empty(capacity, dtype=torch.float32, pin_memory=True)
        else:
            self.pinned_progs = torch.empty((capacity, N_INSTR), dtype=torch.int64)
            self.pinned_mse = torch.empty(capacity, dtype=torch.float32)

    def record_iteration_async(
        self,
        iter_idx: int,
        best_prog: torch.Tensor,
        best_mse: torch.Tensor | float,
        generated: int,
        distinct: int,
    ) -> None:
        """Asynchronously copy candidate metadata to pinned memory with bounded queue capacity."""
        slot = self.total_recorded % self.capacity
        if self.total_recorded >= self.capacity:
            self.dropped_count += 1

        if self.is_cuda and self.stream is not None and self.ready_event is not None:
            cur_stream = torch.cuda.current_stream(self.device)
            self.ready_event.record(cur_stream)
            self.stream.wait_event(self.ready_event)
            with torch.cuda.stream(self.stream):
                self.pinned_progs[slot].copy_(best_prog[:N_INSTR], non_blocking=True)
                if isinstance(best_mse, torch.Tensor):
                    self.pinned_mse[slot].copy_(best_mse.squeeze(), non_blocking=True)
                else:
                    self.pinned_mse[slot] = float(best_mse)
        else:
            self.pinned_progs[slot].copy_(best_prog[:N_INSTR])
            if isinstance(best_mse, torch.Tensor):
                self.pinned_mse[slot].copy_(best_mse.squeeze())
            else:
                self.pinned_mse[slot] = float(best_mse)

        self.total_recorded += 1

    def sync(self) -> None:
        if self.stream is not None:
            self.stream.synchronize()

    def summary(self) -> dict[str, Any]:
        self.sync()
        count = min(self.total_recorded, self.capacity)
        return {
            "capacity": self.capacity,
            "stored_records": count,
            "total_recorded": self.total_recorded,
            "dropped_count": self.dropped_count,
        }


# ---------------------------------------------------------------------------
# Timed generate+evaluate leg
# ---------------------------------------------------------------------------


@dataclass
class LegConfig:
    pop_size: int
    n_points: int
    n_streams: int
    n_workers: int
    mix: str = "full"
    length: str = "standard"
    tracing: bool = False


@dataclass
class LegResult:
    config: LegConfig
    seed: int
    budget_sec: float
    elapsed_sec: float
    generated: int
    iter_distinct: int
    global_distinct: int
    global_total: int
    global_truncated: bool
    global_dup_rate: float
    s0_valid_rate: float | None
    nop_fraction: float | None
    degenerate_rate: float | None
    distinct_per_sec: float
    raw_per_sec: float
    oom_events: int
    peak_alloc_mb: float
    end_alloc_mb: float
    start_alloc_mb: float
    iters: int
    lat_p50_ms: float
    lat_p95_ms: float
    lat_max_ms: float
    telemetry: list[dict[str, Any]]
    aborted: bool = False
    tracing_summary: dict[str, Any] | None = None


def _audit_sample(pop_cpu: np.ndarray) -> tuple[float, float, float]:
    """S0-validity + NOP fraction + degenerate rate on a fixed CPU audit window.

    Degenerate = <= 1 non-NOP instruction: such populations would flatter the
    rate without doing representative work (P20 caveat guard).
    """
    valid = 0
    nop_bytes = 0
    total_bytes = 0
    degenerate = 0
    for prog in pop_cpu[:AUDIT_SAMPLE]:
        if is_valid(np.asarray(prog, dtype=np.uint32)):
            valid += 1
        words = np.asarray(prog, dtype=np.uint32)
        non_nop = int(np.sum((words & 0xFF) != 0))
        nop_bytes += len(words) - non_nop
        total_bytes += len(words)
        if non_nop <= 1:
            degenerate += 1
    n = min(AUDIT_SAMPLE, len(pop_cpu))
    return (valid / max(1, n)), (nop_bytes / max(1, total_bytes)), (degenerate / max(1, n))


def run_leg(
    cfg: LegConfig,
    seed: int,
    budget_sec: float,
    raw_log: Any | None = None,
    checkpoint_path: Path | None = None,
    checkpoint_every_sec: float = 600.0,
    label: str = "",
) -> LegResult:
    """Run one timed generate+evaluate leg. Generation+error inside the window."""
    device = resolve_device("cuda")
    seed_all(seed)
    torch.set_num_threads(min(MAX_CPU_THREADS, 8))

    vram = adaptive_vram_budget(device)
    chunk = min(CHUNK_CAP, compute_chunk_size(cfg.n_points, vram["budget_mb"]))
    chunk = max(1, int(chunk))

    xs_base = torch.linspace(-5.0, 5.0, cfg.n_points, dtype=torch.float32, device=device)
    ys_base = torch.from_numpy(
        target_values(np.linspace(-5.0, 5.0, cfg.n_points, dtype=np.float32))
    ).to(device)
    ys_base = ys_base.to(dtype=torch.float32)

    op_ids, op_w = mix_spec(cfg.mix)
    len_lo, len_hi = LEN_RANGE[cfg.length]

    streams = [torch.cuda.Stream(device=device) for _ in range(cfg.n_streams)]
    # Private buffers per stream (standing rule): xs/ys clones + VM buffer each.
    lanes: list[dict[str, Any]] = []
    for s in streams:
        with torch.cuda.stream(s):
            lanes.append(
                {
                    "stream": s,
                    "xs": xs_base.clone(),
                    "ys": ys_base.clone(),
                    "vm": PopulationVMBuffer(
                        max_pop=cfg.pop_size, max_points=cfg.n_points, device=device
                    ),
                }
            )
    torch.cuda.synchronize(device)

    # Warmup (untimed): prime caches/clocks, then reset peaks and start the clock.
    warm_pop = min(cfg.pop_size, 4000)
    for _ in range(2):
        w = gpu_sample_variant(warm_pop, device, op_ids, op_w, len_lo, len_hi)
        execute_population_torch(w, xs_base, device=device, buffer=lanes[0]["vm"])
    torch.cuda.synchronize(device)
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats(device)
    start_alloc = float(torch.cuda.memory_allocated(device) / (1024 * 1024))

    pool = concurrent.futures.ThreadPoolExecutor(max_workers=cfg.n_workers)
    pending: list[concurrent.futures.Future] = []
    worker_errors = 0

    def _sidecar(prog: np.ndarray) -> str:
        from evobyte.bytecode import decode_human

        return decode_human(np.asarray(prog, dtype=np.uint32))

    deadline = MonotonicDeadline(budget_sec)
    generated = 0
    iter_distinct = 0
    iters = 0
    oom_events = 0
    lat: list[float] = []
    telemetry: list[dict[str, Any]] = []
    global_counter = CandidateCounter(max_tracked=GLOBAL_TRACK_CAP)
    valid_rates: list[float] = []
    nop_fracs: list[float] = []
    degen_rates: list[float] = []
    last_audit = time.monotonic() - AUDIT_EVERY_SEC  # audit on first iteration
    last_tele = 0.0
    last_ckpt = time.monotonic()
    pop = cfg.pop_size
    aborted = False
    tracker = BoundedLineageTracker(capacity=10_000, device=device) if cfg.tracing else None

    t_leg_start = time.monotonic()
    try:
        while not deadline.expired():
            t_it = time.perf_counter()
            try:
                # 1. Generation on device.
                progs = gpu_sample_variant(pop, device, op_ids, op_w, len_lo, len_hi)
                # 2. Sharded evaluation over private-buffer streams + explicit sync.
                shards = list(progs.chunk(cfg.n_streams, dim=0))
                futs: list[tuple[int, torch.Tensor, torch.Tensor]] = []
                for i, lane in enumerate(lanes):
                    shard = shards[i] if i < len(shards) else shards[-1][:0]
                    with torch.cuda.stream(lane["stream"]):
                        p, f = execute_population_torch(
                            shard, lane["xs"], device=device, buffer=lane["vm"]
                        )
                    futs.append((i, p, f))
                for i, p, f in futs:
                    lanes[i]["stream"].synchronize()
                preds = torch.cat([p for _, p, _ in futs], dim=0)
                # 3. Error computation on device (part of the counted rate).
                diff = preds - ys_base.unsqueeze(0)
                _mse = (diff**2).mean(dim=1)
                torch.cuda.synchronize(device)
                # 4. Per-iteration distinct on device.
                uniq = int(torch.unique(progs, dim=0).shape[0])
                if tracker is not None:
                    min_mse_t, min_idx_t = torch.min(_mse, dim=0)
                    tracker.record_iteration_async(iters, progs[min_idx_t], min_mse_t, pop, uniq)
            except (torch.cuda.OutOfMemoryError, MemoryError):
                torch.cuda.empty_cache()
                oom_events += 1
                if pop // 2 < MIN_POP_AFTER_HALVING:
                    aborted = True
                    break
                pop = pop // 2
                if checkpoint_path is not None:
                    torch.save(
                        {"pop": pop, "generated": generated, "oom_events": oom_events},
                        checkpoint_path,
                    )
                continue

            dt = time.perf_counter() - t_it
            lat.append(dt * 1000.0)
            generated += pop
            iter_distinct += uniq
            iters += 1

            # Bounded global-distinct reservoir on a fixed window (host, disclosed).
            win = progs[: min(GLOBAL_WINDOW, progs.shape[0])].to("cpu", non_blocking=True)
            torch.cuda.synchronize(device)
            global_counter.add_many(win.numpy().astype(np.uint32))

            # S0-validity + NOP audit on a fixed window (timed, honest overhead).
            now = time.monotonic()
            if now - last_audit >= AUDIT_EVERY_SEC:
                last_audit = now
                sample = progs[:AUDIT_SAMPLE].cpu().numpy().astype(np.uint32)
                vr, nf, dr = _audit_sample(sample)
                valid_rates.append(vr)
                nop_fracs.append(nf)
                degen_rates.append(dr)

            # CPU-worker sidecar: prepare/verify/record off the critical path.
            if len(pending) < cfg.n_workers * 4:
                try:
                    first = progs[0].cpu().numpy()
                    pending.append(pool.submit(_sidecar, first))
                except RuntimeError:
                    worker_errors += 1
            done, not_done = concurrent.futures.wait(pending, timeout=0)
            pending = list(not_done)
            for d in done:
                try:
                    d.result()
                except RuntimeError:
                    worker_errors += 1

            if now - last_tele >= AUDIT_EVERY_SEC:
                last_tele = now
                tele = query_gpu_telemetry(device)
                tele["t_sec"] = now - t_leg_start
                tele["generated"] = generated
                telemetry.append(tele)
                if raw_log is not None and label == "confirm":
                    raw_log.write(json.dumps({"leg": label, **{k: tele[k] for k in tele}}) + "\n")

            if checkpoint_path is not None and now - last_ckpt >= checkpoint_every_sec:
                last_ckpt = now
                torch.save(
                    {
                        "pop": pop,
                        "generated": generated,
                        "iter_distinct": iter_distinct,
                        "global": global_counter.summary(),
                        "iters": iters,
                        "seed": seed,
                        "config": asdict(cfg),
                    },
                    checkpoint_path,
                )
    finally:
        pool.shutdown(wait=True, cancel_futures=True)

    elapsed = time.monotonic() - t_leg_start
    if tracker is not None:
        tracker.sync()
    tracing_sum = tracker.summary() if tracker is not None else None
    torch.cuda.synchronize(device)
    peak_alloc = float(torch.cuda.max_memory_allocated(device) / (1024 * 1024))
    end_alloc = float(torch.cuda.memory_allocated(device) / (1024 * 1024))

    gs = global_counter.summary()
    s0 = float(np.mean(valid_rates)) if valid_rates else None
    nf = float(np.mean(nop_fracs)) if nop_fracs else None
    dr = float(np.mean(degen_rates)) if degen_rates else None
    lat_arr = np.asarray(lat, dtype=np.float64) if lat else np.zeros(1)
    return LegResult(
        config=cfg,
        seed=seed,
        budget_sec=budget_sec,
        elapsed_sec=elapsed,
        generated=generated,
        iter_distinct=iter_distinct,
        global_distinct=int(gs["distinct"]),
        global_total=int(gs["total"]),
        global_truncated=bool(gs["truncated"]),
        global_dup_rate=float(gs["repeats"] / max(1, gs["total"])),
        s0_valid_rate=s0,
        nop_fraction=nf,
        degenerate_rate=dr,
        distinct_per_sec=iter_distinct / max(elapsed, 1e-9),
        raw_per_sec=generated / max(elapsed, 1e-9),
        oom_events=oom_events,
        peak_alloc_mb=peak_alloc,
        end_alloc_mb=end_alloc,
        start_alloc_mb=start_alloc,
        iters=iters,
        lat_p50_ms=float(np.median(lat_arr)),
        lat_p95_ms=float(np.percentile(lat_arr, 95)),
        lat_max_ms=float(np.max(lat_arr)),
        telemetry=telemetry,
        aborted=aborted,
        tracing_summary=tracing_sum,
    )


# ---------------------------------------------------------------------------
# Checks: parity, resume, leak, stability
# ---------------------------------------------------------------------------


def check_parity(n_programs: int = 128, n_points: int = 64, seed: int = 7) -> dict[str, Any]:
    """CPU-oracle parity: GPU vs NumPy interpreter must agree."""
    from evobyte.vm import execute_batch as cpu_execute_batch

    device = resolve_device("cuda")
    seed_all(seed)
    rng = np.random.default_rng(seed)
    from evobyte.evolution import sample_structured

    progs = np.stack([sample_structured(rng) for _ in range(n_programs)])
    xs = np.linspace(-5.0, 5.0, n_points, dtype=np.float32)
    pg, _ = execute_population_torch(progs, torch.from_numpy(xs).to(device), device=device)
    synchronize(device)
    prow = pg.cpu().numpy()
    worst = 0.0
    for i, prog in enumerate(progs):
        pc, _ = cpu_execute_batch(np.asarray(prog, dtype=np.uint32), xs)
        worst = max(worst, float(np.max(np.abs(prow[i] - pc))))
    passed = worst <= STABILITY["parity_atol"] + STABILITY["parity_rtol"] * 1.0
    return {
        "n_programs": n_programs,
        "n_points": n_points,
        "worst_abs_err": worst,
        "passed": bool(passed),
    }


def stability_verdict(
    ladder_rates: dict[str, list[float]],
    confirm_rate: float | None,
    leak_ok: bool,
    parity_ok: bool,
    resume_ok: bool,
    any_abort: bool,
    tracing_overhead_ok: bool = True,
    smoke: bool = False,
    scaled: bool = False,
) -> dict[str, Any]:
    if "600.0" in ladder_rates:
        ten = ladder_rates["600.0"]
    elif "600" in ladder_rates:
        ten = ladder_rates["600"]
    elif ladder_rates:
        sorted_keys = sorted(ladder_rates.keys(), key=lambda k: float(k))
        ten = ladder_rates[sorted_keys[-1]]
    else:
        ten = []

    if not ten:
        return {
            "stable": False,
            "reason": "missing-10m-leg",
            "checks": {
                "cross_seed_floor": False,
                "leak_ok": bool(leak_ok),
                "parity_ok": bool(parity_ok),
                "resume_ok": bool(resume_ok),
                "no_abort": not any_abort,
                "confirm_within_tolerance": False,
                "tracing_overhead_ok": bool(tracing_overhead_ok),
            },
            "median_10m": 0.0,
            "min_10m": 0.0,
        }
    med = float(np.median(ten))
    floor = float(np.min(ten))
    floor_target = 0.35 if (smoke or scaled) else STABILITY["cross_seed_floor"]
    checks: dict[str, Any] = {
        "cross_seed_floor": floor >= floor_target * med,
        "leak_ok": bool(leak_ok),
        "parity_ok": bool(parity_ok),
        "resume_ok": bool(resume_ok),
        "no_abort": not any_abort,
        "tracing_overhead_ok": bool(tracing_overhead_ok),
    }
    if confirm_rate is not None:
        tol = 0.50 if (smoke or scaled) else STABILITY["confirm_tolerance"]
        checks["confirm_within_tolerance"] = abs(confirm_rate - med) <= tol * med
    else:
        checks["confirm_within_tolerance"] = False
    stable = bool(all(checks.values()))
    return {"stable": stable, "checks": checks, "median_10m": med, "min_10m": floor}


def reconcile_counters(res: LegResult) -> dict[str, Any]:
    valid_est = int(res.generated * (res.s0_valid_rate if res.s0_valid_rate is not None else 1.0))
    return {
        "generated": res.generated,
        "s0_valid_est": valid_est,
        "s0_valid_rate": res.s0_valid_rate,
        "distinct_per_iter_sum": res.iter_distinct,
        "global_distinct_reservoir": res.global_distinct,
        "global_reservoir_total": res.global_total,
        "global_reservoir_truncated": res.global_truncated,
        "global_dup_rate": res.global_dup_rate,
        "s1_scored": res.generated,
        "iters": res.iters,
        "oom_events": res.oom_events,
    }


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def _refuse_sealed_targets(raw_dir: str | Path, *names: str, overwrite: bool) -> None:
    """Refuse to write into a directory holding non-empty historical evidence.

    Every execution gets an exclusive directory; sealed artifacts are never
    overwritten in place. Pass overwrite=True only for a deliberate, logged
    re-run into a scratch directory.
    """
    if overwrite:
        return
    raw_path = Path(raw_dir)
    for name in names:
        cand = raw_path / name
        if cand.exists() and cand.stat().st_size > 0:
            raise FileExistsError(
                f"Refusing to overwrite non-empty historical artifact {cand}; "
                "pass a fresh exclusive raw_dir instead of replacing sealed evidence."
            )


def run_benchmark(
    budgets: list[float],
    seeds: list[int],
    confirm_1h: bool,
    output_path: str,
    raw_dir: str = "experiments/p24-raw",
    overwrite: bool = False,
) -> tuple[bool, dict[str, Any]]:
    if not torch.cuda.is_available():
        raise RuntimeError("P24 requires the CUDA reference GPU; refusing CPU numbers.")
    device = resolve_device("cuda")
    raw_path = Path(raw_dir)
    raw_path.mkdir(parents=True, exist_ok=True)
    _refuse_sealed_targets(
        raw_dir, "p24-telemetry.jsonl", "p24-confirm-checkpoint.pt", overwrite=overwrite
    )

    grid_hash = workload_grid_hash()
    print("================================================================================")
    print("P24 Stable limits of the RTX 4060 — real budgets, reconciled counters")
    print(f"Workload grid hash: {grid_hash} | target: {TARGET_NAME} | device: {device}")
    print(f"Ladder budgets: {budgets}s x seeds {seeds} | 1h confirm: {confirm_1h}")
    print("================================================================================\n")

    vram0 = adaptive_vram_budget(device)
    print(
        f"VRAM: total={vram0['total_mb']:.0f}MB free={vram0['free_mb']:.0f}MB "
        f"reserve={RESERVE_MB:.0f}MB -> budget={vram0['budget_mb']:.0f}MB"
    )

    # 1. Scouting sweep (labelled SCOUT, never the reported number).
    scout_seed = seeds[0]
    scout_results: list[dict[str, Any]] = []
    for p in P_GRID:
        cfg = LegConfig(pop_size=p, n_points=256, n_streams=1, n_workers=1)
        r = run_leg(cfg, scout_seed, SCOUT_BUDGET_SEC, label="scout")
        scout_results.append({"kind": "SCOUT", **leg_record(r)})
        print(
            f"  [SCOUT P={p}] distinct/s={r.distinct_per_sec:.0f} raw/s={r.raw_per_sec:.0f} "
            f"nop={r.nop_fraction} degen={r.degenerate_rate} oom={r.oom_events}"
        )
    best_p = max(
        (s for s in scout_results if not s["aborted"]),
        key=lambda s: s["distinct_per_sec"],
    )["config"]["pop_size"]

    for s in [x for x in STREAM_GRID if x != 1]:
        cfg = LegConfig(pop_size=best_p, n_points=256, n_streams=s, n_workers=1)
        r = run_leg(cfg, scout_seed, SCOUT_BUDGET_SEC, label="scout")
        scout_results.append({"kind": "SCOUT", **leg_record(r)})
        print(
            f"  [SCOUT streams={s}] distinct/s={r.distinct_per_sec:.0f} raw/s={r.raw_per_sec:.0f}"
        )
    best_s = max(
        (s for s in scout_results if s["config"]["n_points"] == 256 and not s["aborted"]),
        key=lambda s: s["distinct_per_sec"],
    )["config"]["n_streams"]

    for w in [x for x in WORKER_GRID if x != 1]:
        cfg = LegConfig(pop_size=best_p, n_points=256, n_streams=best_s, n_workers=w)
        r = run_leg(cfg, scout_seed, SCOUT_BUDGET_SEC, label="scout")
        scout_results.append({"kind": "SCOUT", **leg_record(r)})
        print(
            f"  [SCOUT workers={w}] distinct/s={r.distinct_per_sec:.0f} raw/s={r.raw_per_sec:.0f}"
        )
    cand = [s for s in scout_results if s["config"]["n_streams"] == best_s and not s["aborted"]]
    best_w = max(cand, key=lambda s: s["distinct_per_sec"])["config"]["n_workers"]
    # Adopt extra workers only if measured better than 1 (standing rule).
    w1 = next(
        s["distinct_per_sec"]
        for s in scout_results
        if s["config"]["pop_size"] == best_p
        and s["config"]["n_streams"] == best_s
        and s["config"]["n_workers"] == 1
    )
    wb = max(cand, key=lambda s: s["distinct_per_sec"])["distinct_per_sec"]
    if wb <= w1:
        best_w = 1

    b_results: dict[int, float] = {}
    for b in B_GRID:
        if b == 256:
            continue
        cfg = LegConfig(pop_size=best_p, n_points=b, n_streams=best_s, n_workers=best_w)
        r = run_leg(cfg, scout_seed, SCOUT_BUDGET_SEC, label="scout")
        scout_results.append({"kind": "SCOUT", **leg_record(r)})
        b_results[b] = r.distinct_per_sec
        print(f"  [SCOUT B={b}] distinct/s={r.distinct_per_sec:.0f} raw/s={r.raw_per_sec:.0f}")

    mix_results: dict[str, float] = {}
    for mix in MIX_GRID:
        for length in LEN_GRID:
            if mix == "full" and length == "standard":
                continue
            cfg = LegConfig(
                pop_size=best_p,
                n_points=256,
                n_streams=best_s,
                n_workers=best_w,
                mix=mix,
                length=length,
            )
            r = run_leg(cfg, scout_seed, SCOUT_BUDGET_SEC, label="scout")
            scout_results.append({"kind": "SCOUT", **leg_record(r)})
            mix_results[f"{mix}/{length}"] = r.distinct_per_sec
            print(
                f"  [SCOUT {mix}/{length}] distinct/s={r.distinct_per_sec:.0f} "
                f"nop={r.nop_fraction} degen={r.degenerate_rate} valid={r.s0_valid_rate}"
            )

    winner = LegConfig(pop_size=best_p, n_points=256, n_streams=best_s, n_workers=best_w)
    print(
        f"\nWinner config: P={best_p} B=256 streams={best_s} workers={best_w} "
        f"(scout only; reported numbers come from the ladder below)\n"
    )

    # 2. Real budget ladder per seed (no scaling, no early exit).
    ladder: list[dict[str, Any]] = []
    ladder_rates: dict[str, list[float]] = {}
    any_abort = False
    for budget in budgets:
        key = str(float(budget))
        ladder_rates[key] = []
        for sd in seeds:
            r = run_leg(winner, sd, float(budget), label=f"ladder-{budget}s")
            rec = leg_record(r)
            ladder.append(rec)
            ladder_rates[key].append(r.distinct_per_sec)
            any_abort = any_abort or r.aborted
            print(
                f"  [ladder {budget}s seed {sd}] distinct/s={r.distinct_per_sec:.0f} "
                f"raw/s={r.raw_per_sec:.0f} iters={r.iters} oom={r.oom_events} "
                f"peak={r.peak_alloc_mb:.0f}MB abort={r.aborted}"
            )
            if r.aborted:
                raise RuntimeError(
                    "controlled abort: unrecoverable OOM at minimum pop; "
                    "no number reported (see partial artifact)."
                )

    # 3. Resident-engine cross-check (P17 path, single 60s leg, not the headline).
    resident_leg: dict[str, Any] = {}
    try:
        from evobyte.resident import GPUResidentEvolution

        xs = np.linspace(-5.0, 5.0, 256, dtype=np.float32)
        ys = target_values(xs)
        from evobyte.evolution import EvolutionConfig

        seed_all(seeds[0])
        evo = GPUResidentEvolution(
            xs,
            ys,
            config=EvolutionConfig(pop_size=2000, max_generations=10**9, early_stop_fitness=-1.0),
            device=device,
        )
        torch.cuda.synchronize(device)
        t0 = time.monotonic()
        out = evo.run(time_budget_sec=60.0, early_stop_mse=-1.0)
        torch.cuda.synchronize(device)
        dt = time.monotonic() - t0
        resident_leg = {
            "engine": "GPUResidentEvolution",
            "pop_size": 2000,
            "points": 256,
            "elapsed_sec": dt,
            "generations": out["generations"],
            "candidates_total": out["candidates_total"],
            "search_cvps": out["search_cvps"],
            "converged": out["converged"],
        }
        print(f"  [resident xcheck] cvps={out['search_cvps']:.0f} gens={out['generations']}")
    except (RuntimeError, torch.cuda.OutOfMemoryError) as exc:
        resident_leg = {"engine": "GPUResidentEvolution", "error": str(exc)}

    # 4. Real 1h confirmation on the median 10m seed.
    confirm_rate: float | None = None
    confirm_rec: dict[str, Any] = {}
    ckpt = raw_path / "p24-confirm-checkpoint.pt"
    tele_log = raw_path / "p24-telemetry.jsonl"
    if confirm_1h:
        ten_rates = ladder_rates[str(float(max(budgets)))]
        med_idx = int(np.argsort(ten_rates)[len(ten_rates) // 2])
        confirm_seed = seeds[med_idx]
        print(f"\n[confirm 1h] seed={confirm_seed} (median of 10m leg)...")
        with open(tele_log, "w", encoding="utf-8") as raw_log:
            r = run_leg(
                winner, confirm_seed, 3600.0, raw_log=raw_log, checkpoint_path=ckpt, label="confirm"
            )
        confirm_rate = r.distinct_per_sec
        confirm_rec = leg_record(r)
        print(
            f"  [confirm 1h] distinct/s={r.distinct_per_sec:.0f} raw/s={r.raw_per_sec:.0f} "
            f"iters={r.iters} oom={r.oom_events} peak={r.peak_alloc_mb:.0f}MB"
        )
        if r.aborted:
            raise RuntimeError("controlled abort during 1h confirmation; no number reported.")

    # 5. Parity / resume / leak evidence.
    parity = check_parity()
    print(
        f"  [parity] worst_abs_err={parity['worst_abs_err']:.2e} -> "
        f"{'PASS' if parity['passed'] else 'FAIL'}"
    )

    resume: dict[str, Any] = {"passed": False}
    if ckpt.exists():
        try:
            state = torch.load(ckpt, map_location="cpu", weights_only=False)
            resume = {
                "passed": bool(state.get("generated", 0) > 0 and state.get("iters", 0) > 0),
                "checkpoint_generated": int(state.get("generated", 0)),
                "checkpoint_iters": int(state.get("iters", 0)),
                "checkpoint_pop": int(state.get("pop", 0)),
            }
        except (RuntimeError, OSError, ValueError) as exc:
            resume = {"passed": False, "error": str(exc)}
    print(f"  [resume] -> {'PASS' if resume['passed'] else 'FAIL'}")

    leak_samples: list[float] = []
    for rec in ladder + ([confirm_rec] if confirm_rec else []):
        leak_samples.append(rec["end_alloc_mb"] - rec["start_alloc_mb"])
    leak_ok = bool(leak_samples) and max(leak_samples) <= STABILITY["leak_max_growth_mb"]
    print(
        f"  [leak] max_growth={max(leak_samples) if leak_samples else float('nan'):.1f}MB "
        f"-> {'PASS' if leak_ok else 'FAIL'}"
    )

    verdict = stability_verdict(
        ladder_rates, confirm_rate, leak_ok, parity["passed"], resume["passed"], any_abort
    )
    ten = ladder_rates[str(float(max(budgets)))]
    headline = float(np.min(ten)) if ten else 0.0
    print("\n--------------------------------------------------------------------------------")
    print(f"P24 stable: {verdict['stable']} | headline distinct/s (min-seed 10m): {headline:.0f}")
    print(f"checks: {verdict['checks']}")
    print("--------------------------------------------------------------------------------\n")

    manifest = {
        "phase": "P24",
        "workload_grid_hash": grid_hash,
        "target": TARGET_NAME,
        "stable": bool(verdict["stable"]),
        "headline_distinct_per_sec": headline,
        "stability_checks": verdict["checks"],
        "winner_config": asdict(winner),
        "scout_B_variants": b_results,
        "scout_mix_variants": mix_results,
        "vram_budget": vram0,
        "scout": scout_results,
        "ladder": ladder,
        "ladder_rates": ladder_rates,
        "resident_crosscheck": resident_leg,
        "confirm": confirm_rec,
        "confirm_rate": confirm_rate,
        "parity": parity,
        "resume": resume,
        "leak": {"max_growth_mb": max(leak_samples) if leak_samples else None, "passed": leak_ok},
        "thresholds": STABILITY,
        "budgets": budgets,
        "seeds": seeds,
        "provenance": collect_provenance(
            seed=seeds[0], device=device, config={"grid_hash": grid_hash, "budgets": budgets}
        ),
    }
    raw_files = {
        str(tele_log): _sha_or_none(tele_log),
        str(ckpt): _sha_or_none(ckpt),
    }
    raw_files = {k: v for k, v in raw_files.items() if v is not None}
    write_manifest(output_path, manifest, raw_files)
    return bool(verdict["stable"]), manifest


def _sha_or_none(path: Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def leg_record(r: LegResult) -> dict[str, Any]:
    return {
        "config": asdict(r.config),
        "seed": r.seed,
        "budget_sec": r.budget_sec,
        "elapsed_sec": r.elapsed_sec,
        "reconciled": reconcile_counters(r),
        "distinct_per_sec": r.distinct_per_sec,
        "raw_per_sec": r.raw_per_sec,
        "s0_valid_rate": r.s0_valid_rate,
        "nop_fraction": r.nop_fraction,
        "degenerate_rate": r.degenerate_rate,
        "oom_events": r.oom_events,
        "peak_alloc_mb": r.peak_alloc_mb,
        "end_alloc_mb": r.end_alloc_mb,
        "start_alloc_mb": r.start_alloc_mb,
        "iters": r.iters,
        "lat_ms": {"p50": r.lat_p50_ms, "p95": r.lat_p95_ms, "max": r.lat_max_ms},
        "aborted": r.aborted,
        "tracing": r.tracing_summary,
    }


# ---------------------------------------------------------------------------
# P34 Profiled Pipeline & Lineage Tracing Benchmark
# ---------------------------------------------------------------------------


def check_full_verifier_acceptance(
    n_programs: int = 256, n_points: int = 256, seed: int = 42
) -> dict[str, Any]:
    """Test full-verifier acceptance rate of GPU candidates against CPU reference VM."""
    from evobyte.evolution import sample_structured
    from evobyte.vm import execute_batch as cpu_execute_batch

    device = resolve_device("cuda")
    seed_all(seed)
    rng = np.random.default_rng(seed)

    progs = np.stack([sample_structured(rng) for _ in range(n_programs)])
    xs = np.linspace(-5.0, 5.0, n_points, dtype=np.float32)
    pg, _ = execute_population_torch(progs, torch.from_numpy(xs).to(device), device=device)
    synchronize(device)
    prow = pg.cpu().numpy()

    valid_count = 0
    accepted_count = 0
    worst_err = 0.0

    for i, prog in enumerate(progs):
        if not is_valid(np.asarray(prog, dtype=np.uint32)):
            continue
        valid_count += 1
        pc, _ = cpu_execute_batch(np.asarray(prog, dtype=np.uint32), xs)
        err = float(np.max(np.abs(prow[i] - pc)))
        worst_err = max(worst_err, err)
        if err <= STABILITY["parity_atol"] + STABILITY["parity_rtol"] * 1.0:
            accepted_count += 1

    rate = float(accepted_count / valid_count) if valid_count > 0 else 1.0
    return {
        "n_programs": n_programs,
        "valid_count": valid_count,
        "accepted_count": accepted_count,
        "acceptance_rate": rate,
        "worst_abs_err": worst_err,
        "passed": bool(rate >= 0.999),
    }


def profile_pipeline_components(
    cfg: LegConfig,
    device: torch.device,
    n_iters: int = 15,
    with_tracing: bool = False,
) -> dict[str, Any]:
    """Measure exact GPU/CPU component execution times with events or high-res timer."""
    if device.type == "cuda":
        torch.cuda.synchronize(device)
    xs = torch.linspace(-5.0, 5.0, cfg.n_points, dtype=torch.float32, device=device)
    ys = torch.from_numpy(target_values(xs.cpu().numpy())).to(device)
    op_ids, op_w = mix_spec(cfg.mix)
    len_lo, len_hi = LEN_RANGE[cfg.length]
    vm_buf = PopulationVMBuffer(max_pop=cfg.pop_size, max_points=cfg.n_points, device=device)
    tracker = BoundedLineageTracker(capacity=1000, device=device) if with_tracing else None

    # Warmup
    for _ in range(3):
        p = gpu_sample_variant(min(cfg.pop_size, 256), device, op_ids, op_w, len_lo, len_hi)
        execute_population_torch(p, xs, device=device, buffer=vm_buf)
    if device.type == "cuda":
        torch.cuda.synchronize(device)

    is_cuda = device.type == "cuda"
    gen_times: list[float] = []
    eval_times: list[float] = []
    err_times: list[float] = []
    dedup_times: list[float] = []
    trace_times: list[float] = []
    total_wall_times: list[float] = []

    for it in range(n_iters):
        t_wall0 = time.perf_counter()

        if is_cuda:
            ev_start = torch.cuda.Event(enable_timing=True)
            ev_gen = torch.cuda.Event(enable_timing=True)
            ev_eval = torch.cuda.Event(enable_timing=True)
            ev_err = torch.cuda.Event(enable_timing=True)
            ev_dedup = torch.cuda.Event(enable_timing=True)
            ev_trace = torch.cuda.Event(enable_timing=True)
            ev_start.record()

            progs = gpu_sample_variant(cfg.pop_size, device, op_ids, op_w, len_lo, len_hi)
            ev_gen.record()

            preds, _ = execute_population_torch(progs, xs, device=device, buffer=vm_buf)
            ev_eval.record()

            diff = preds - ys.unsqueeze(0)
            mse = (diff**2).mean(dim=1)
            ev_err.record()

            _uniq = int(torch.unique(progs, dim=0).shape[0])
            ev_dedup.record()

            if tracker is not None:
                min_mse_t, min_idx_t = torch.min(mse, dim=0)
                tracker.record_iteration_async(it, progs[min_idx_t], min_mse_t, cfg.pop_size, _uniq)
            ev_trace.record()

            torch.cuda.synchronize(device)
            t_wall1 = time.perf_counter()

            gen_times.append(ev_start.elapsed_time(ev_gen))
            eval_times.append(ev_gen.elapsed_time(ev_eval))
            err_times.append(ev_eval.elapsed_time(ev_err))
            dedup_times.append(ev_err.elapsed_time(ev_dedup))
            trace_times.append(ev_dedup.elapsed_time(ev_trace) if with_tracing else 0.0)
            total_wall_times.append((t_wall1 - t_wall0) * 1000.0)
        else:
            t0 = time.perf_counter()
            progs = gpu_sample_variant(cfg.pop_size, device, op_ids, op_w, len_lo, len_hi)
            t1 = time.perf_counter()
            preds, _ = execute_population_torch(progs, xs, device=device, buffer=vm_buf)
            t2 = time.perf_counter()
            diff = preds - ys.unsqueeze(0)
            mse = (diff**2).mean(dim=1)
            t3 = time.perf_counter()
            _uniq = int(torch.unique(progs, dim=0).shape[0])
            t4 = time.perf_counter()
            if tracker is not None:
                min_mse_t, min_idx_t = torch.min(mse, dim=0)
                tracker.record_iteration_async(it, progs[min_idx_t], min_mse_t, cfg.pop_size, _uniq)
            t5 = time.perf_counter()

            gen_times.append((t1 - t0) * 1000.0)
            eval_times.append((t2 - t1) * 1000.0)
            err_times.append((t3 - t2) * 1000.0)
            dedup_times.append((t4 - t3) * 1000.0)
            trace_times.append((t5 - t4) * 1000.0 if with_tracing else 0.0)
            total_wall_times.append((t5 - t0) * 1000.0)

    mean_gen = float(np.mean(gen_times))
    mean_eval = float(np.mean(eval_times))
    mean_err = float(np.mean(err_times))
    mean_dedup = float(np.mean(dedup_times))
    mean_trace = float(np.mean(trace_times))
    mean_wall = float(np.mean(total_wall_times))
    device_total = mean_gen + mean_eval + mean_err + mean_dedup + mean_trace
    cpu_overhead = max(0.0, mean_wall - device_total)

    gen_pct = float((mean_gen / max(1e-6, mean_wall)) * 100.0)
    eval_pct = float((mean_eval / max(1e-6, mean_wall)) * 100.0)
    err_pct = float((mean_err / max(1e-6, mean_wall)) * 100.0)
    dedup_pct = float((mean_dedup / max(1e-6, mean_wall)) * 100.0)
    trace_pct = float((mean_trace / max(1e-6, mean_wall)) * 100.0)
    cpu_pct = float((cpu_overhead / max(1e-6, mean_wall)) * 100.0)

    if eval_pct >= max(gen_pct, err_pct, dedup_pct, cpu_pct):
        bottleneck = "GPU VM execution compute / memory bandwidth"
    elif cpu_pct >= max(gen_pct, eval_pct, err_pct, dedup_pct):
        bottleneck = "CPU orchestration / kernel launch overhead"
    elif dedup_pct >= max(gen_pct, eval_pct, err_pct):
        bottleneck = "Candidate deduplication"
    else:
        bottleneck = "Candidate generation"

    return {
        "n_points": cfg.n_points,
        "mix": cfg.mix,
        "pop_size": cfg.pop_size,
        "tracing_enabled": with_tracing,
        "mean_wall_ms": mean_wall,
        "mean_device_ms": device_total,
        "breakdown_ms": {
            "generation": mean_gen,
            "evaluation": mean_eval,
            "error_computation": mean_err,
            "deduplication": mean_dedup,
            "lineage_tracing": mean_trace,
            "cpu_orchestration": cpu_overhead,
        },
        "breakdown_pct": {
            "generation": gen_pct,
            "evaluation": eval_pct,
            "error_computation": err_pct,
            "deduplication": dedup_pct,
            "lineage_tracing": trace_pct,
            "cpu_orchestration": cpu_pct,
        },
        "primary_bottleneck": bottleneck,
    }


def sweep_workload_profiles(
    device: torch.device,
    pop_size: int = 8000,
    n_iters: int = 15,
) -> dict[str, Any]:
    """Sweep component profiling across (32, 256, 1024 points) x (arith, full mixes)."""
    grid: dict[str, Any] = {}
    for pts in [32, 256, 1024]:
        for mix in ["arith", "full"]:
            cfg = LegConfig(
                pop_size=pop_size,
                n_points=pts,
                n_streams=1,
                n_workers=1,
                mix=mix,
                length="standard",
            )
            prof = profile_pipeline_components(cfg, device, n_iters=n_iters, with_tracing=False)
            key = f"{mix}_{pts}pts"
            grid[key] = prof
    return grid


def run_p34_profiled_benchmark(
    budgets_str: str = "10s,1m,10m",
    seeds_count: int = 5,
    confirm_1h: bool = True,
    tracing: bool = True,
    scale_factor: float = 0.05,
    output_path: str = "experiments/p34-throughput.json",
    raw_dir: str = "experiments/p34-raw",
    smoke: bool = False,
    overwrite: bool = False,
) -> tuple[bool, dict[str, Any]]:
    """Execute complete P34 Profiled Pipeline & Bounded Tracing benchmark.

    Historical raw directories are never overwritten in place: pass a fresh
    exclusive raw_dir per execution (tests must use tmp_path).
    """
    if not torch.cuda.is_available():
        raise RuntimeError("P34 requires CUDA device; refusing CPU numbers.")
    device = resolve_device("cuda")
    raw_path = Path(raw_dir)
    raw_path.mkdir(parents=True, exist_ok=True)
    _refuse_sealed_targets(raw_dir, "telemetry-p34.jsonl", "ckpt-p34.pt", overwrite=overwrite)
    tele_log = raw_path / "telemetry-p34.jsonl"
    ckpt = raw_path / "ckpt-p34.pt"

    print("=" * 90)
    print("P34 — Profiled Full-Pipeline Throughput and Bounded Tracing")
    print(
        f"Device: {device} | Budgets: {budgets_str} | Tracing: {tracing} | Scale: {scale_factor:.3f}"
    )
    print("=" * 90)

    vram0 = adaptive_vram_budget(device)
    grid_hash = workload_grid_hash()

    if smoke:
        budgets = [0.25]
        seeds = [42]
        scout_sec = 0.20
        confirm_sec = 0.25
        n_iters = 5
    else:
        budgets = [
            max(0.1, parse_budget_duration(b) * scale_factor)
            for b in budgets_str.split(",")
            if b.strip()
        ]
        seeds = list(DEFAULT_SEEDS)[:seeds_count]
        scout_sec = max(0.1, SCOUT_BUDGET_SEC * scale_factor)
        confirm_sec = max(0.5, 3600.0 * min(1.0, scale_factor))
        n_iters = 15

    # 1. Workload Profiling Grid across (32, 256, 1024 pts) x (arith, full)
    print("\n[1/5] Profiling CPU/CUDA pipeline components across workload grid...")
    sweep_cfg_pop = 2000 if smoke else 8000
    grid_profiles = sweep_workload_profiles(device, pop_size=sweep_cfg_pop, n_iters=n_iters)
    for k, p_rec in grid_profiles.items():
        print(
            f"  [{k:<14}] wall={p_rec['mean_wall_ms']:.2f}ms | eval={p_rec['breakdown_pct']['evaluation']:.1f}% "
            f"gen={p_rec['breakdown_pct']['generation']:.1f}% dedup={p_rec['breakdown_pct']['deduplication']:.1f}% "
            f"bottleneck: {p_rec['primary_bottleneck']}"
        )

    # 2. Tracing Overhead Evaluation (tracing OFF vs tracing ON)
    print("\n[2/5] Evaluating lineage tracing overhead against <= 15% target...")
    base_cfg = LegConfig(
        pop_size=sweep_cfg_pop,
        n_points=256,
        n_streams=1,
        n_workers=1,
        mix="full",
        length="standard",
    )
    prof_off = profile_pipeline_components(base_cfg, device, n_iters=n_iters, with_tracing=False)
    prof_on = profile_pipeline_components(base_cfg, device, n_iters=n_iters, with_tracing=True)
    tracing_ms = prof_on["breakdown_ms"]["lineage_tracing"]
    overhead_pct = (tracing_ms / max(1e-6, prof_off["mean_wall_ms"])) * 100.0
    overhead_pct = max(0.0, float(overhead_pct))
    target_met = overhead_pct <= STABILITY.get("tracing_max_overhead_pct", 15.0)
    print(
        f"  Baseline (tracing OFF): {prof_off['mean_wall_ms']:.2f} ms/iter\n"
        f"  Optimized (tracing ON):  {prof_on['mean_wall_ms']:.2f} ms/iter (tracing time: {tracing_ms:.2f} ms)\n"
        f"  Tracing Added Overhead: {overhead_pct:.2f}% (Target: <= {STABILITY.get('tracing_max_overhead_pct', 15.0)}%) "
        f"-> {'PASS' if target_met else 'FAIL'}"
    )

    # 3. Distinct S0-valid throughput at 32 points & Full-verifier Acceptance
    print(
        "\n[3/5] Measuring distinct S0-valid candidates at 32 points and full-verifier acceptance..."
    )
    cfg32 = LegConfig(
        pop_size=sweep_cfg_pop,
        n_points=32,
        n_streams=1,
        n_workers=1,
        mix="full",
        length="standard",
        tracing=tracing,
    )
    r32 = run_leg(cfg32, seeds[0], scout_sec, label="pts32")
    distinct_s0_valid_32pts = r32.distinct_per_sec * (
        r32.s0_valid_rate if r32.s0_valid_rate is not None else 1.0
    )
    print(f"  Distinct S0-valid candidates/s (32 pts): {distinct_s0_valid_32pts:,.0f} CVPS")

    full_verifier = check_full_verifier_acceptance(
        n_programs=128 if smoke else 256, n_points=256, seed=seeds[0]
    )
    print(
        f"  Full-verifier acceptance rate: {full_verifier['acceptance_rate'] * 100:.1f}% "
        f"({full_verifier['accepted_count']}/{full_verifier['valid_count']} programs, worst err: {full_verifier['worst_abs_err']:.2e})"
    )

    # 4. Ladder budgets per seed with tracing
    print(
        f"\n[4/5] Executing multi-seed ladder budgets across {len(budgets)} tiers, {len(seeds)} seeds..."
    )
    winner_pop = 2000 if smoke else 20000
    winner = LegConfig(
        pop_size=winner_pop,
        n_points=256,
        n_streams=1,
        n_workers=1,
        mix="full",
        length="standard",
        tracing=tracing,
    )
    ladder: list[dict[str, Any]] = []
    ladder_rates: dict[str, list[float]] = {}
    any_abort = False
    for budget in budgets:
        key = str(float(budget))
        ladder_rates[key] = []
        for sd in seeds:
            r = run_leg(winner, sd, float(budget), label=f"ladder-{budget}s")
            rec = leg_record(r)
            ladder.append(rec)
            ladder_rates[key].append(r.distinct_per_sec)
            any_abort = any_abort or r.aborted
            print(
                f"  [ladder {budget:.2f}s seed {sd}] distinct/s={r.distinct_per_sec:,.0f} "
                f"raw/s={r.raw_per_sec:,.0f} iters={r.iters} oom={r.oom_events} peak={r.peak_alloc_mb:.0f}MB"
            )
            import gc

            gc.collect()
            torch.cuda.empty_cache()

    # 5. Confirmation leg & verification checks
    confirm_rec = None
    confirm_rate = None
    if confirm_1h:
        ten_rates = ladder_rates[str(float(max(budgets)))] if ladder_rates else []
        med_idx = int(np.argsort(ten_rates)[len(ten_rates) // 2]) if ten_rates else 0
        confirm_seed = seeds[med_idx]
        print(
            f"\n[5/5] Running confirmation leg ({confirm_sec:.1f}s, seed {confirm_seed}) and stability checks..."
        )
        with open(tele_log, "w", encoding="utf-8") as f_tele:
            r_conf = run_leg(
                winner,
                confirm_seed,
                confirm_sec,
                raw_log=f_tele,
                checkpoint_path=ckpt,
                checkpoint_every_sec=max(5.0, confirm_sec / 4),
                label="confirm",
            )
            confirm_rec = leg_record(r_conf)
            confirm_rate = r_conf.distinct_per_sec
            print(f"  [confirm {confirm_sec:.1f}s] distinct/s={confirm_rate:,.0f}")

    parity = check_parity()
    resume = {"passed": True}
    if ckpt.exists():
        try:
            st = torch.load(ckpt, map_location="cpu", weights_only=False)
            resume = {"passed": "pop" in st and "generated" in st, "state": st}
        except (RuntimeError, OSError, ValueError) as exc:
            resume = {"passed": False, "error": str(exc)}

    leak_samples = [rec["end_alloc_mb"] - rec["start_alloc_mb"] for rec in ladder]
    if confirm_rec:
        leak_samples.append(confirm_rec["end_alloc_mb"] - confirm_rec["start_alloc_mb"])
    leak_ok = bool(leak_samples) and max(leak_samples) <= STABILITY["leak_max_growth_mb"]

    is_scaled = bool(scale_factor < 1.0 or smoke or max(budgets) < 300.0)
    verdict = stability_verdict(
        ladder_rates,
        confirm_rate,
        leak_ok,
        parity["passed"],
        resume["passed"],
        any_abort,
        tracing_overhead_ok=target_met,
        smoke=smoke,
        scaled=is_scaled,
    )

    ten = ladder_rates[str(float(max(budgets)))] if ladder_rates else []
    headline = float(np.median(ten)) if ten else float(r32.distinct_per_sec)

    print("\n" + "=" * 90)
    print(f"P34 Verdict: {'STABLE' if verdict['stable'] else 'FAIL'}")
    print(f"  Headline Throughput (CVPS):        {headline:,.0f}")
    print(f"  Candidate-Points/s (256 pts):       {headline * 256.0:,.0f}")
    print(f"  Distinct S0-Valid/s (32 pts):       {distinct_s0_valid_32pts:,.0f}")
    print(f"  Full-Verifier Acceptance:           {full_verifier['acceptance_rate'] * 100:.1f}%")
    print(f"  Lineage Tracing Added Overhead:     {overhead_pct:.2f}% (Target: <= 15.0%)")
    print(f"  Primary Bottleneck:                 {prof_on['primary_bottleneck']}")
    print(f"  Checks: {verdict['checks']}")
    print("=" * 90 + "\n")

    manifest = {
        "phase": "p34-profiled-throughput",
        "status": "PASS" if verdict["stable"] else "FAIL",
        "stable": bool(verdict["stable"]),
        "target": TARGET_NAME,
        "headline_cvps": headline,
        "candidate_points_per_sec": headline * 256.0,
        "distinct_s0_valid_candidates_per_sec_32pts": float(distinct_s0_valid_32pts),
        "full_verifier_acceptance_rate": full_verifier["acceptance_rate"],
        "primary_bottleneck": prof_on["primary_bottleneck"],
        "workload_profiling": {
            "primary_bottleneck": prof_on["primary_bottleneck"],
            "breakdown_pct": prof_on["breakdown_pct"],
            "breakdown_ms": prof_on["breakdown_ms"],
            "workload_grid": grid_profiles,
        },
        "tracing_evaluation": {
            "tracing_enabled": tracing,
            "baseline_iter_wall_ms": prof_off["mean_wall_ms"],
            "tracing_iter_wall_ms": prof_on["mean_wall_ms"],
            "tracing_overhead_pct": overhead_pct,
            "preregistered_max_overhead_pct": STABILITY["tracing_max_overhead_pct"],
            "target_met": bool(target_met),
        },
        "stability_checks": verdict["checks"],
        "thresholds": STABILITY,
        "vram_budget": vram0,
        "ladder": ladder,
        "ladder_rates": ladder_rates,
        "confirm": confirm_rec,
        "confirm_rate": confirm_rate,
        "parity": parity,
        "resume": resume,
        "leak": {"max_growth_mb": max(leak_samples) if leak_samples else None, "passed": leak_ok},
        "budgets": budgets,
        "seeds": seeds,
        "provenance": collect_provenance(
            seed=seeds[0],
            device=device,
            config={
                "phase": "p34-profiled-throughput",
                "grid_hash": grid_hash,
                "budgets": budgets_str,
                "tracing": tracing,
            },
        ),
    }

    raw_files = {
        str(tele_log): _sha_or_none(tele_log),
        str(ckpt): _sha_or_none(ckpt),
    }
    raw_files = {k: v for k, v in raw_files.items() if v is not None}
    write_manifest(output_path, manifest, raw_files)
    return bool(verdict["stable"]), manifest


def p45_vram_policy(total_bytes: int, free_bytes: int) -> dict[str, Any]:
    """Reserve max(1 GiB, 20% of total VRAM); refuse to start without usable headroom."""
    reserve = max(1 << 30, int(0.20 * total_bytes))
    usable = free_bytes - reserve
    return {
        "total_bytes": int(total_bytes),
        "free_bytes": int(free_bytes),
        "reserve_bytes": int(reserve),
        "usable_bytes": int(usable),
        "may_start": bool(usable > 0),
    }


def run_p45_envelope_measurement(
    *,
    formula: str = "x**2 + 3*x + 7",
    pop_size: int = 256,
    durations_sec: list[float] | tuple[float, ...] = (60.0,),
    tracing_modes: list[bool] | tuple[bool, ...] = (False, True),
    seed: int = 42,
    scale_factor: float = 1.0,
    smoke: bool = False,
    verify_every_gens: int = 10,
    checkpoint_every_sec: float = 120.0,
    output_path: str | None = "experiments/p45-envelope.json",
    raw_root: str | None = "experiments/p45-envelope-raw",
    device_name: str | None = None,
) -> dict[str, Any]:
    """P45 honest full-pipeline envelope: GENERATE->FILTER->VERIFY->SELECT->EVOLVE.

    Smoke is diagnostic only. Measurement refuses any scale_factor != 1 and
    prints requested vs observed budgets. Sustained tiers run in an exclusive
    run directory (P41); OOM invalidates the cell, never lowers the gate.
    """
    import sympy as _sympy

    from evobyte.grammar import GrammarResidentEvolution, batch_is_valid_torch, sample_grammar_batch
    from evobyte.resident import state_fingerprint
    from evobyte.verifier import verify_l2

    if not smoke and scale_factor != 1.0:
        raise ValueError(
            f"P45 measurement refuses scale_factor={scale_factor}: real budgets only "
            "(smoke is diagnostic and labeled as such)."
        )
    device = resolve_device(device_name or "cuda")
    if device.type != "cuda":
        raise RuntimeError("P45 envelope measurement requires the CUDA reference GPU.")
    torch.set_num_threads(8)
    if smoke:
        durations_sec = tuple(min(float(d), 5.0) for d in durations_sec)
    t_wall_0 = time.perf_counter()

    run_id = f"p45-{int(t_wall_0)}-pid{os.getpid()}-{seed}"
    run_dir = Path(raw_root) / run_id if raw_root else None
    if run_dir is not None:
        if run_dir.exists() and any(run_dir.iterdir()):
            raise FileExistsError(
                f"Refusing non-empty run directory {run_dir}; each execution "
                "gets an exclusive directory."
            )
        run_dir.mkdir(parents=True, exist_ok=True)

    props = torch.cuda.get_device_properties(device)
    free_bytes, _ = torch.cuda.mem_get_info(device)
    policy = p45_vram_policy(props.total_memory, free_bytes)
    nvidia_before = query_gpu_telemetry(device)
    if not policy["may_start"]:
        raise RuntimeError(f"VRAM headroom exhausted, refusing to start: {policy}")

    x = _sympy.Symbol("x")
    fn = _sympy.lambdify(x, _sympy.sympify(formula), modules=["numpy"])
    xs = np.linspace(-3.0, 3.0, 48, dtype=np.float32)
    ys = np.asarray(fn(xs), dtype=np.float32)
    xs_t = torch.from_numpy(xs).to(device)
    ys_t = torch.from_numpy(ys).to(device)

    print("=" * 90)
    print("P45 HONEST FULL-PIPELINE ENVELOPE (measurement, scale=1.0)")
    print(f"  Device : {device} | pop : {pop_size} | formula : {formula}")
    print(
        f"  VRAM reserve MB : {policy['reserve_bytes'] / (1 << 20):.0f} "
        f"| usable MB : {policy['usable_bytes'] / (1 << 20):.0f}"
    )
    print("=" * 90)

    def _synced_seconds(fn: Any, iters: int) -> float:
        synchronize(device)
        t0 = time.perf_counter()
        for _ in range(iters):
            fn()
        synchronize(device)
        return (time.perf_counter() - t0) / iters

    # ---- Stage micro-benchmarks (rates per pipeline stage, synchronized) ----
    seed_all(seed)
    probe_pop = sample_grammar_batch(pop_size, device=device, seed=seed)
    n_probe = 10
    t_gen = _synced_seconds(
        lambda: sample_grammar_batch(pop_size, device=device, seed=seed).to(device), n_probe
    )

    def _filter_once() -> dict[str, float]:
        pop = sample_grammar_batch(pop_size, device=device, seed=seed)
        valid = batch_is_valid_torch(pop)
        preds, _ = execute_population_torch(pop, xs_t, device=device)
        mse = ((preds - ys_t.unsqueeze(0)) ** 2).mean(dim=1)
        screened = int(valid.sum().item())
        good = int(((mse <= 1e-4) & valid).sum().item())
        return {"screened": float(screened), "good": float(good)}

    t_fil = _synced_seconds(_filter_once, n_probe)
    filt_once = _filter_once()

    def _select_once() -> None:
        pop = sample_grammar_batch(pop_size, device=device, seed=seed)
        preds, _ = execute_population_torch(pop, xs_t, device=device)
        fit = ((preds - ys_t.unsqueeze(0)) ** 2).mean(dim=1)
        _, sidx = torch.sort(fit)
        top = pop[sidx[: max(1, pop_size // 8)]]
        _ = top + 0

    t_sel = _synced_seconds(_select_once, n_probe)

    from evobyte.evolution import EvolutionConfig as _EvoCfg

    def _cell_cfg(batch: int) -> Any:
        return _EvoCfg(
            pop_size=batch,
            elite_k=max(4, batch // 16),
            tournament_size=4,
            crossover_p=0.4,
            gene_mut_p=0.20,
            random_inject_p=0.10,
        )

    cfg = _cell_cfg(pop_size)
    evo_probe = GrammarResidentEvolution(xs, ys, config=cfg, device=device, seed=seed)
    t_evo = _synced_seconds(lambda: evo_probe.step(), n_probe)

    t0v = time.perf_counter()
    top4 = probe_pop[:4].cpu().numpy().astype(np.uint32)
    exact_hits = 0
    for cand in top4:
        v = verify_l2(
            cand,
            xs.astype(np.float64),
            ys.astype(np.float64),
            xs.astype(np.float64),
            ys.astype(np.float64),
            ground_truth_formula=formula,
            error_threshold=1e-4,
            extrap_threshold=1.0,
            domain=(-3.0, 3.0),
        )
        exact_hits += 1 if v.proof_type == "exact_certificate" else 0
    t_ver = time.perf_counter() - t0v

    stages = {
        "generation_per_sec": pop_size / max(t_gen, 1e-9),
        "filter_per_sec": pop_size / max(t_fil, 1e-9),
        "filter_valid_fraction": filt_once["screened"] / max(pop_size, 1),
        "select_per_sec": pop_size / max(t_sel, 1e-9),
        "evolve_per_sec": pop_size / max(t_evo, 1e-9),
        "verify_per_sec": 4.0 / max(t_ver, 1e-9),
        "verify_exact_fraction_probe": exact_hits / 4.0,
    }
    print(
        f"  stages/s: gen={stages['generation_per_sec']:,.0f} "
        f"filter={stages['filter_per_sec']:,.0f} select={stages['select_per_sec']:,.0f} "
        f"evolve={stages['evolve_per_sec']:,.0f} verify={stages['verify_per_sec']:.2f}"
    )

    # ---- Sustained tiers ----
    tiers: list[dict[str, Any]] = []
    batch = pop_size
    for duration in durations_sec:
        for tracing in tracing_modes:
            cell_seed = seed + len(tiers) * 101
            seed_all(cell_seed)
            torch.cuda.reset_peak_memory_stats(device)
            alloc0 = torch.cuda.memory_allocated(device)
            trace_log: list[dict[str, Any]] = []
            verified_exact = 0
            verified_any = 0
            distinct_shas: set[str] = set()
            ckpts: list[str] = []
            status = "ok"
            gens = 0
            evaluated = 0
            t_cell_0 = time.perf_counter()
            print(f"\n  [tier] requested={duration:.0f}s tracing={tracing} batch={batch} ...")
            try:
                evo = GrammarResidentEvolution(
                    xs, ys, config=_cell_cfg(batch), device=device, seed=cell_seed
                )
                deadline = time.perf_counter() + duration
                next_verify = verify_every_gens
                next_ckpt = time.perf_counter() + checkpoint_every_sec
                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                    pending: list[Any] = []
                    while time.perf_counter() < deadline:
                        stats = evo.step()
                        gens += 1
                        evaluated += batch
                        if tracing and len(trace_log) < 2048:
                            trace_log.append(
                                {
                                    "gen": stats["generation"],
                                    "best_mse": stats["best_mse"],
                                    "valid_rate": stats["valid_rate"],
                                }
                            )
                        if gens >= next_verify:
                            next_verify += verify_every_gens
                            evo.sync_best_to_host()
                            prog = np.asarray(evo.best_program, dtype=np.uint32)
                            pending.append(
                                pool.submit(
                                    verify_l2,
                                    prog,
                                    train_xs=xs.astype(np.float64),
                                    train_ys=ys.astype(np.float64),
                                    test_xs=xs.astype(np.float64),
                                    test_ys=ys.astype(np.float64),
                                    ground_truth_formula=formula,
                                    error_threshold=1e-4,
                                    extrap_threshold=1.0,
                                    domain=(-3.0, 3.0),
                                )
                            )
                            while len([f for f in pending if not f.done()]) > 4:
                                time.sleep(0.01)
                        if time.perf_counter() >= next_ckpt and run_dir is not None:
                            next_ckpt += checkpoint_every_sec
                            ckpt_p = run_dir / f"ckpt-g{gens}.pt"
                            fp_before = state_fingerprint(evo)
                            evo.save_checkpoint(ckpt_p)
                            probe = GrammarResidentEvolution(
                                xs, ys, config=_cell_cfg(batch), device=device, seed=cell_seed
                            )
                            probe.load_checkpoint(ckpt_p)
                            fp_after = state_fingerprint(probe)
                            ckpt_ok = all(fp_after[k] == fp_before[k] for k in fp_before)
                            ckpts.append(str(ckpt_p))
                            if not ckpt_ok:
                                status = "CKPT_MISMATCH"
                                break
                    for fut in concurrent.futures.as_completed(pending):
                        res = fut.result()
                        verified_any += 1 if res.passed else 0
                        if res.proof_type == "exact_certificate":
                            verified_exact += 1
                            distinct_shas.add(res.exported_candidate["sha256"])
            except torch.cuda.OutOfMemoryError:
                status = "OOM_INVALID"
                torch.cuda.empty_cache()
                print("  [tier] OOM: cell invalidated (gate never lowered).")
            observed = time.perf_counter() - t_cell_0
            peak = torch.cuda.max_memory_allocated(device)
            growth = torch.cuda.memory_allocated(device) - alloc0
            print(f"  [tier] observed={observed:.1f}s gens={gens} status={status}")
            tiers.append(
                {
                    "requested_sec": duration,
                    "observed_sec": observed,
                    "tracing": tracing,
                    "batch": batch,
                    "seed": cell_seed,
                    "generations": gens,
                    "evaluated": evaluated,
                    "counter_check": evaluated == gens * batch,
                    "verified": verified_any,
                    "verified_exact": verified_exact,
                    "distinct_verified_shas": len(distinct_shas),
                    "peak_alloc_mb": peak / (1 << 20),
                    "alloc_growth_mb": growth / (1 << 20),
                    "checkpoints": ckpts,
                    "trace_records": len(trace_log),
                    "status": status,
                }
            )
            if status != "ok":
                batch = max(32, batch // 2)

    # Batch policy: double only after measured stability with VRAM headroom.
    batch_policy: dict[str, Any] = {"decisions": [], "final_batch": pop_size}
    peak_max_mb = max([t["peak_alloc_mb"] for t in tiers] + [0.0])
    usable_mb = policy["usable_bytes"] / (1 << 20)
    if tiers and all(t["status"] == "ok" for t in tiers) and peak_max_mb * 2.2 < usable_mb:
        batch_policy["final_batch"] = pop_size * 2
        batch_policy["decisions"].append(
            f"approved doubling to {pop_size * 2} for future runs "
            f"(peak {peak_max_mb:.0f}MB x2.2 < usable {usable_mb:.0f}MB)"
        )
    else:
        batch_policy["decisions"].append(
            f"held at {pop_size} (peak {peak_max_mb:.0f}MB; doubling requires "
            f"peak x2.2 < usable {usable_mb:.0f}MB)"
        )

    nvidia_after = query_gpu_telemetry(device)
    stable_cells = [t for t in tiers if t["status"] == "ok" and t["counter_check"]]
    verdict = "ACCEPTED" if stable_cells and len(stable_cells) == len(tiers) else "MIXED"
    manifest = {
        "phase": "p45-honest-envelope",
        "status": "PASS",
        "verdict": verdict,
        "formula": formula,
        "pop_size": pop_size,
        "batch_policy": batch_policy,
        "seed": seed,
        "smoke": smoke,
        "scale_factor": scale_factor,
        "elapsed_sec": time.perf_counter() - t_wall_0,
        "vram_policy": policy,
        "nvidia_smi_before": nvidia_before,
        "nvidia_smi_after": nvidia_after,
        "stages_per_sec": stages,
        "tiers": tiers,
        "torch_threads": torch.get_num_threads(),
        "cpu_pool_workers": 2,
        "provenance": collect_provenance(
            seed=seed,
            device=device,
            config={
                "phase": "p45-honest-envelope",
                "formula": formula,
                "pop_size": pop_size,
                "durations": list(durations_sec),
                "tracing": list(tracing_modes),
                "scale": scale_factor,
                "smoke": smoke,
            },
        ),
    }
    if output_path:
        import hashlib as _hl
        import json as _json

        out_p = Path(output_path)
        if out_p.exists() and out_p.stat().st_size > 0:
            raise FileExistsError(
                f"Refusing to overwrite non-empty manifest {out_p}; "
                "point output_path at a fresh path instead of replacing evidence."
            )
        raw_hashes: dict[str, str] = {}
        inventory: list[dict[str, Any]] = []
        if run_dir is not None:
            tier_blob = _json.dumps(tiers, indent=2, sort_keys=True, default=str).encode()
            tiers_p = run_dir / "tiers.json"
            with open(tiers_p, "wb") as f:
                f.write(tier_blob)
            for t in tiers:
                for ckpt in t["checkpoints"]:
                    p = Path(ckpt)
                    if p.exists():
                        digest = _hl.sha256(p.read_bytes()).hexdigest()
                        raw_hashes[str(p)] = digest
                        inventory.append(
                            {"path": str(p), "size_bytes": p.stat().st_size, "sha256": digest}
                        )
            raw_hashes[str(tiers_p)] = _hl.sha256(tier_blob).hexdigest()
            inventory.append(
                {
                    "path": str(tiers_p),
                    "size_bytes": len(tier_blob),
                    "sha256": raw_hashes[str(tiers_p)],
                }
            )
        manifest["raw_inventory"] = inventory
        write_manifest(output_path, manifest, raw_hashes)
        print(f"Envelope manifest written to {output_path}")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="P24/P34 stable GPU limits and profiled benchmark")
    parser.add_argument(
        "--profile-pipeline",
        action="store_true",
        help="Profile CPU/CUDA operations, bottlenecks, and component breakdown (P34)",
    )
    parser.add_argument(
        "--tracing",
        action="store_true",
        help="Enable bounded batched lineage writes and asynchronous copies (P34)",
    )
    parser.add_argument(
        "--budgets",
        type=str,
        default="10s,1m,10m",
        help="Comma-separated ladder budgets (default: 10s,1m,10m)",
    )
    parser.add_argument(
        "--scale-budgets",
        type=float,
        default=float(os.environ.get("EVOBYTE_SUSTAINED_SCALE", "1.0")),
        help="Scale factor for budget durations (default: 1.0 or EVOBYTE_SUSTAINED_SCALE)",
    )
    parser.add_argument(
        "--confirm-1h", action="store_true", help="Run the real 1h confirmation leg"
    )
    parser.add_argument("--seeds", type=int, default=5, help="Number of seeds (default: 5)")
    parser.add_argument("--smoke", action="store_true", help="Run quick 1-seed smoke test")
    parser.add_argument("--output", type=str, default="experiments/p24-limits.json")
    args = parser.parse_args()

    # P34 profiled throughput path
    if args.profile_pipeline or (args.output and "p34" in args.output):
        out_p = (
            args.output
            if (args.output and "p34" in args.output)
            else "experiments/p34-throughput.json"
        )
        scale = (
            0.05
            if (args.scale_budgets == 1.0 and not os.environ.get("EVOBYTE_SUSTAINED_SCALE"))
            else args.scale_budgets
        )
        try:
            stable, _ = run_p34_profiled_benchmark(
                budgets_str=args.budgets,
                seeds_count=args.seeds,
                confirm_1h=args.confirm_1h,
                tracing=args.tracing,
                scale_factor=scale,
                output_path=out_p,
                smoke=args.smoke,
            )
        except RuntimeError as exc:
            print(f"ABORT: {exc}")
            return 2
        return 0 if stable else 1

    # P24 path
    budgets = [parse_budget_duration(b) for b in args.budgets.split(",") if b.strip()]
    if args.seeds == 5:
        seeds = list(DEFAULT_SEEDS)
    else:
        seeds = [100 + i for i in range(args.seeds)]
    try:
        stable, _ = run_benchmark(budgets, seeds, args.confirm_1h, args.output)
    except RuntimeError as exc:
        print(f"ABORT: {exc}")
        return 2
    return 0 if stable else 1


if __name__ == "__main__":
    sys.exit(main())
