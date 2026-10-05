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
    BoundedLineageTracker,
    LegConfig,
    LegResult,
    check_full_verifier_acceptance,
    mix_spec,
    profile_pipeline_components,
    reconcile_counters,
    run_p34_profiled_benchmark,
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


def test_bounded_lineage_tracker_capacity_and_backpressure() -> None:
    tracker = BoundedLineageTracker(capacity=5, device=torch.device("cpu"))
    prog = torch.zeros(16, dtype=torch.int64)
    mse = torch.tensor(0.5, dtype=torch.float32)

    for i in range(8):
        tracker.record_iteration_async(i, prog, mse, 100, 90)

    summary = tracker.summary()
    assert summary["capacity"] == 5
    assert summary["stored_records"] == 5
    assert summary["total_recorded"] == 8
    assert summary["dropped_count"] == 3


def test_profile_pipeline_components_cpu() -> None:
    cfg = LegConfig(pop_size=64, n_points=32, n_streams=1, n_workers=1, mix="arith", length="short")
    device = torch.device("cpu")
    prof = profile_pipeline_components(cfg, device=device, n_iters=3, with_tracing=True)

    assert "mean_wall_ms" in prof
    assert "breakdown_ms" in prof
    assert "breakdown_pct" in prof
    assert "primary_bottleneck" in prof
    assert prof["tracing_enabled"] is True
    assert prof["breakdown_ms"]["lineage_tracing"] >= 0.0


def test_check_full_verifier_acceptance() -> None:
    if not torch.cuda.is_available():
        return
    res = check_full_verifier_acceptance(n_programs=64, n_points=64, seed=42)
    assert res["n_programs"] == 64
    assert res["valid_count"] > 0
    assert res["acceptance_rate"] >= 0.99
    assert res["passed"] is True


def test_stability_verdict_with_tracing_check() -> None:
    good = {
        "ladder_rates": {"600.0": [1000.0, 1020.0, 990.0, 1010.0, 1005.0]},
        "confirm_rate": 1000.0,
        "leak_ok": True,
        "parity_ok": True,
        "resume_ok": True,
        "any_abort": False,
        "tracing_overhead_ok": True,
    }
    assert stability_verdict(**good)["stable"] is True

    # Tracing overhead exceeded target (> 15%)
    bad_tracing = dict(good, tracing_overhead_ok=False)
    assert stability_verdict(**bad_tracing)["stable"] is False


def _hash_historical_p34_raw() -> dict[str, str]:
    import hashlib as _hl

    root = Path(__file__).resolve().parents[1] / "experiments" / "p34-raw"
    digests: dict[str, str] = {}
    if root.exists():
        for child in sorted(root.iterdir()):
            if child.is_file():
                digests[child.name] = _hl.sha256(child.read_bytes()).hexdigest()
    return digests


def test_p34_smoke_execution(tmp_path: Path) -> None:
    if not torch.cuda.is_available():
        return
    before = _hash_historical_p34_raw()
    out_file = tmp_path / "p34-test.json"
    stable, manifest = run_p34_profiled_benchmark(
        budgets_str="0.05s",
        seeds_count=1,
        confirm_1h=True,
        tracing=True,
        scale_factor=0.05,
        output_path=str(out_file),
        raw_dir=str(tmp_path / "p34-raw"),
        smoke=True,
    )
    assert manifest["phase"] == "p34-profiled-throughput"
    assert manifest["status"] in ("PASS", "FAIL")
    assert "workload_profiling" in manifest
    assert "tracing_evaluation" in manifest
    assert "distinct_s0_valid_candidates_per_sec_32pts" in manifest
    assert "full_verifier_acceptance_rate" in manifest
    assert manifest["tracing_evaluation"]["target_met"] is True
    assert stable is True
    # P41: the smoke wrote to its exclusive directory; historical evidence untouched.
    assert (tmp_path / "p34-raw" / "telemetry-p34.jsonl").exists()
    assert _hash_historical_p34_raw() == before


def test_p34_refuses_sealed_raw_dir(tmp_path: Path) -> None:
    import pytest

    raw_dir = tmp_path / "p34-raw"
    raw_dir.mkdir()
    (raw_dir / "telemetry-p34.jsonl").write_text('{"sealed": true}\n')
    if not torch.cuda.is_available():
        with pytest.raises(RuntimeError):
            run_p34_profiled_benchmark(
                budgets_str="0.05s",
                seeds_count=1,
                output_path=str(tmp_path / "p34-x.json"),
                raw_dir=str(raw_dir),
                smoke=True,
            )
        return
    with pytest.raises(FileExistsError, match="Refusing to overwrite"):
        run_p34_profiled_benchmark(
            budgets_str="0.05s",
            seeds_count=1,
            output_path=str(tmp_path / "p34-x.json"),
            raw_dir=str(raw_dir),
            smoke=True,
        )


def test_write_manifest_exclusive_seals_before_manifest(tmp_path: Path) -> None:
    import pytest

    from evobyte.provenance import verify_manifest_integrity, write_manifest_exclusive

    manifest_p = tmp_path / "m.json"
    raw_p = tmp_path / "raw" / "evidence.jsonl"
    sealed = write_manifest_exclusive(
        manifest_p, {"phase": "P41-test"}, {str(raw_p): b'{"n": 1}\n'}
    )
    assert sealed["raw_inventory"] == [
        {"path": str(raw_p), "size_bytes": 9, "sha256": sealed["raw_artifacts"][0]["sha256"]}
    ]
    assert verify_manifest_integrity(manifest_p)["ok"] is True
    # Second seal into the same destinations is refused, never silently replaced.
    with pytest.raises(FileExistsError, match="Refusing to overwrite"):
        write_manifest_exclusive(manifest_p, {"phase": "P41-test"}, {str(raw_p): b"{}"})
    # A single flipped byte in sealed evidence is detected.
    with open(raw_p, "ab") as f:
        f.write(b" ")
    assert verify_manifest_integrity(manifest_p)["ok"] is False


def test_p45_measurement_refuses_scaled_budgets() -> None:
    import pytest
    from gpu_limits import run_p45_envelope_measurement

    with pytest.raises(ValueError, match="refuses scale_factor"):
        run_p45_envelope_measurement(scale_factor=0.5, output_path=None, raw_root=None)


def test_p45_vram_policy_math() -> None:
    from gpu_limits import p45_vram_policy

    full = p45_vram_policy(8_000_000_000, 7_700_000_000)
    assert full["reserve_bytes"] == 1_600_000_000
    assert full["may_start"] is True
    tight = p45_vram_policy(8_000_000_000, 1_000_000_000)
    assert tight["may_start"] is False
    small = p45_vram_policy(2_000_000_000, 1_900_000_000)
    assert small["reserve_bytes"] == 1 << 30


def test_p45_smoke_measurement_tmp(tmp_path: Path) -> None:
    if not torch.cuda.is_available():
        return
    from gpu_limits import run_p45_envelope_measurement

    from evobyte.provenance import verify_manifest_integrity

    out_p = tmp_path / "p45-smoke.json"
    manifest = run_p45_envelope_measurement(
        durations_sec=[3],
        tracing_modes=[True],
        pop_size=32,
        seed=42,
        smoke=True,
        verify_every_gens=5,
        checkpoint_every_sec=2,
        output_path=str(out_p),
        raw_root=str(tmp_path / "raw"),
    )
    assert manifest["verdict"] in ("ACCEPTED", "MIXED")
    assert manifest["smoke"] is True
    assert set(manifest["stages_per_sec"]) >= {
        "generation_per_sec",
        "filter_per_sec",
        "select_per_sec",
        "evolve_per_sec",
        "verify_per_sec",
    }
    assert len(manifest["tiers"]) == 1
    assert manifest["tiers"][0]["counter_check"] is True
    assert verify_manifest_integrity(out_p)["ok"] is True
    assert all(r["size_bytes"] > 0 for r in manifest["raw_inventory"])
    # A second seal into the same manifest path is refused, never replaced.
    import pytest as _pytest

    with _pytest.raises(FileExistsError, match="Refusing to overwrite"):
        run_p45_envelope_measurement(
            durations_sec=[3],
            tracing_modes=[True],
            pop_size=32,
            seed=42,
            smoke=True,
            output_path=str(out_p),
            raw_root=str(tmp_path / "raw2"),
        )
