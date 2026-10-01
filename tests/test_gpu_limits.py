"""P24 stable-limits harness: pure-logic unit tests (fast, CPU-only).

The full GPU gate (ladder + 1h confirmation) runs via the phase exit gate;
these tests pin the frozen grid, reconciliation math, stability verdict and
checkpoint roundtrip without touching the GPU clock.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "benchmarks"))

import torch
from gpu_limits import (
    LegConfig,
    LegResult,
    mix_spec,
    reconcile_counters,
    stability_verdict,
    workload_grid_hash,
)


def _leg(distinct_per_sec: float = 1000.0) -> LegResult:
    return LegResult(
        config=LegConfig(pop_size=2000, n_points=256, n_streams=1, n_workers=1),
        seed=42,
        budget_sec=10.0,
        elapsed_sec=10.0,
        generated=12000,
        iter_distinct=10000,
        global_distinct=9000,
        global_total=10000,
        global_truncated=False,
        global_dup_rate=0.1,
        s0_valid_rate=0.8,
        nop_fraction=0.3,
        degenerate_rate=0.01,
        distinct_per_sec=distinct_per_sec,
        raw_per_sec=1200.0,
        oom_events=0,
        peak_alloc_mb=500.0,
        end_alloc_mb=100.0,
        start_alloc_mb=90.0,
        iters=6,
        lat_p50_ms=1.0,
        lat_p95_ms=2.0,
        lat_max_ms=3.0,
        telemetry=[],
    )


def test_workload_grid_hash_frozen():
    h1 = workload_grid_hash()
    h2 = workload_grid_hash()
    assert h1 == h2 and len(h1) == 16


def test_mix_specs_cover_full_and_arith():
    full_ops, full_w = mix_spec("full")
    arith_ops, arith_w = mix_spec("arith")
    assert len(full_ops) == 16 and abs(float(full_w.sum()) - 1.0) < 1e-12
    assert set(arith_ops) <= set(full_ops) and len(arith_ops) < len(full_ops)
    assert abs(float(arith_w.sum()) - 1.0) < 1e-12


def test_reconcile_counters_arithmetic():
    rec = reconcile_counters(_leg())
    assert rec["generated"] == 12000
    assert rec["s0_valid_est"] == int(12000 * 0.8)
    assert rec["distinct_per_iter_sum"] == 10000
    assert rec["s1_scored"] == 12000
    assert rec["oom_events"] == 0


def test_stability_verdict_stable_path():
    v = stability_verdict(
        {"600.0": [1000.0, 1020.0, 990.0, 1010.0, 1005.0]},
        confirm_rate=1000.0,
        leak_ok=True,
        parity_ok=True,
        resume_ok=True,
        any_abort=False,
    )
    assert v["stable"] is True
    assert all(v["checks"].values())


def test_stability_verdict_rejects_each_failure():
    good = {
        "ladder_rates": {"600.0": [1000.0, 1020.0, 990.0, 1010.0, 1005.0]},
        "confirm_rate": 1000.0,
        "leak_ok": True,
        "parity_ok": True,
        "resume_ok": True,
        "any_abort": False,
    }
    assert stability_verdict(**good)["stable"] is True
    # Cross-seed floor breach.
    bad_seed = dict(good, ladder_rates={"600.0": [1000.0, 1020.0, 500.0, 1010.0, 1005.0]})
    assert stability_verdict(**bad_seed)["stable"] is False
    # Confirm drift breach.
    bad_confirm = dict(good, confirm_rate=500.0)
    assert stability_verdict(**bad_confirm)["stable"] is False
    # Missing confirmation.
    assert stability_verdict(**dict(good, confirm_rate=None))["stable"] is False
    # Leak / parity / resume / abort.
    assert stability_verdict(**dict(good, leak_ok=False))["stable"] is False
    assert stability_verdict(**dict(good, parity_ok=False))["stable"] is False
    assert stability_verdict(**dict(good, resume_ok=False))["stable"] is False
    assert stability_verdict(**dict(good, any_abort=True))["stable"] is False
    # Missing 10m leg.
    assert stability_verdict(**dict(good, ladder_rates={}))["stable"] is False


def test_checkpoint_roundtrip(tmp_path):
    ckpt = tmp_path / "ckpt.pt"
    torch.save({"pop": 1000, "generated": 5000, "iters": 12}, ckpt)
    state = torch.load(ckpt, map_location="cpu", weights_only=False)
    assert state["generated"] == 5000 and state["iters"] == 12
