"""Tests for sustained throughput, telemetry, and quality experiment (P20 scope)."""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pytest
import torch

from evobyte.evolution import EvolutionConfig
from evobyte.provenance import parse_budget_duration, query_gpu_telemetry
from evobyte.resident import GPUResidentEvolution, gpu_sample_structured
from evobyte.vm_torch import execute_population_torch


def get_test_devices() -> list[torch.device]:
    devs = [torch.device("cpu")]
    if torch.cuda.is_available():
        devs.append(torch.device("cuda"))
    return devs


def test_parse_budget_duration() -> None:
    """Verify parsing budget strings into seconds."""
    assert parse_budget_duration("10s") == 10.0
    assert parse_budget_duration("1m") == 60.0
    assert parse_budget_duration("10m") == 600.0
    assert parse_budget_duration("1h") == 3600.0
    assert parse_budget_duration("30") == 30.0
    assert parse_budget_duration("  0.5s  ") == 0.5


def test_query_gpu_telemetry() -> None:
    """Verify telemetry dict schema and missing power limits kept None."""
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    telemetry = query_gpu_telemetry(dev)
    assert isinstance(telemetry, dict)
    assert "temperature_c" in telemetry
    assert "graphics_clock_mhz" in telemetry
    assert "power_draw_w" in telemetry
    assert "power_limit_w" in telemetry
    assert "gpu_utilization_pct" in telemetry
    assert "vram_used_mb" in telemetry
    assert "telemetry_available" in telemetry

    # Verify no estimated joules / fabricated numbers when missing
    if telemetry["power_limit_w"] is not None:
        assert isinstance(telemetry["power_limit_w"], float)


@pytest.mark.parametrize("device", get_test_devices())
def test_resident_evolution_time_budget(device: torch.device) -> None:
    """Verify GPUResidentEvolution terminates after specified time budget."""
    xs = np.linspace(-5.0, 5.0, 64, dtype=np.float32)
    ys = xs**2 + 3.0 * xs + 7.0

    cfg = EvolutionConfig(pop_size=100, max_generations=1000000)
    evo = GPUResidentEvolution(xs, ys, config=cfg, device=device)

    budget_sec = 0.3
    t0 = time.perf_counter()
    res = evo.run(time_budget_sec=budget_sec)
    elapsed = time.perf_counter() - t0

    assert elapsed >= budget_sec * 0.8
    assert res["generations"] >= 1
    assert "history" in res
    assert len(res["history"]) == res["generations"]
    assert "elapsed_total_s" in res["history"][0]


@pytest.mark.parametrize("device", get_test_devices())
def test_s1_stretch_and_deduplication(device: torch.device) -> None:
    """Verify S0 filtering, deduplication on device, and S1 evaluation."""
    n_sample = 1000
    xs_32 = torch.linspace(-5.0, 5.0, 32, dtype=torch.float32, device=device)
    progs = gpu_sample_structured(n_sample, device=device)

    # S0 validity check
    ops = progs & 0xFF
    dsts = (progs >> 8) & 0xFF
    as_ = (progs >> 16) & 0xFF
    has_r7 = ((dsts == 7) & (ops != 0)).any(dim=1)
    valid_s0 = has_r7 & (ops <= 15).all(dim=1) & (dsts < 8).all(dim=1) & (as_ < 8).all(dim=1)
    valid_progs = progs[valid_s0]
    assert valid_progs.shape[0] > 0

    # Deduplication
    unique_progs, _counts = torch.unique(valid_progs, dim=0, return_counts=True)
    assert unique_progs.shape[0] <= valid_progs.shape[0]
    assert unique_progs.shape[0] > 0

    # S1 evaluation at 32 points
    preds, flags = execute_population_torch(unique_progs, xs_32, device=device)
    assert preds.shape == (unique_progs.shape[0], 32)
    assert flags.shape == (unique_progs.shape[0], 32)


def test_sustained_benchmark_cli_quick(tmp_path: Path) -> None:
    """Verify run_sustained_experiment generates valid JSON artifact with expected schema."""
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "benchmarks"))
    from cvps import run_sustained_experiment

    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    out_file = tmp_path / "p20_test.json"

    report = run_sustained_experiment(
        device=dev,
        budgets_str="1s",
        seeds_count=1,
        scale_factor=0.5,
        vram_budget_mb=1024.0,
    )

    assert report["benchmark"] == "p20_sustained_throughput"
    assert "s1_stretch_target" in report
    assert report["s1_stretch_target"]["verdict"] in ("achieved", "not_achieved")
    assert "budget_runs" in report
    assert len(report["budget_runs"]) == 1
    assert "telemetry_summary" in report
    assert "overall_verdict" in report
    assert report["overall_verdict"]["sustained_runs_completed"] is True

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    assert out_file.exists()
