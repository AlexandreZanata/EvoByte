"""Tests for streaming GPU cascade and bounded memory (P18 scope)."""

from __future__ import annotations

import numpy as np
import pytest
import torch

from evobyte.cascade import (
    CascadeConfig,
    StreamingGPUCascade,
    audit_cascade_accuracy,
    get_representative_indices,
    query_available_vram_mb,
)
from evobyte.evolution import EvolutionConfig
from evobyte.resident import GPUResidentEvolution, gpu_sample_pure, gpu_sample_structured


def get_test_devices() -> list[torch.device]:
    devs = [torch.device("cpu")]
    if torch.cuda.is_available():
        devs.append(torch.device("cuda"))
    return devs


@pytest.mark.parametrize("device", get_test_devices())
def test_representative_indices_span_domain(device: torch.device) -> None:
    total = 1000
    n_samples = 32
    idx = get_representative_indices(total, n_samples, device=device)

    assert len(idx) == n_samples
    assert idx.device.type == device.type
    assert idx[0].item() == 0
    assert idx[-1].item() == total - 1
    # Strictly increasing
    assert (idx[1:] > idx[:-1]).all()


@pytest.mark.parametrize("device", get_test_devices())
def test_vram_query(device: torch.device) -> None:
    budget = query_available_vram_mb(device, budget_mb=4000.0)
    assert budget > 0.0


@pytest.mark.parametrize("device", get_test_devices())
def test_streaming_cascade_evaluation_and_counters(device: torch.device) -> None:
    torch.manual_seed(42)
    cfg = CascadeConfig(
        s1_points=32,
        s2_points=64,
        k_cutoff=4.0,
        enable_cascade=True,
    )
    cascade = StreamingGPUCascade(config=cfg, device=device)

    n_progs = 60
    struct_progs = gpu_sample_structured(50, device=device)
    pure_progs = gpu_sample_pure(10, device=device)
    programs = torch.cat([struct_progs, pure_progs], dim=0)

    xs = torch.linspace(-5.0, 5.0, 128, device=device)
    ys = xs**2 + 3.0 * xs + 7.0

    fitness, mse, counters = cascade.evaluate(programs, xs, ys, elite_score=10.0)

    assert fitness.shape == (n_progs,)
    assert mse.shape == (n_progs,)
    assert fitness.device.type == device.type

    # Verify stage accounting reconciliation
    assert counters.s0_entries == n_progs
    assert counters.s0_survivors + counters.s0_rejected_invalid == counters.s0_entries
    assert counters.s1_entries == counters.s0_survivors
    assert (
        counters.s1_survivors + counters.s1_rejected_error + counters.s1_rejected_invalid
        == counters.s1_entries
    )
    assert counters.s2_entries == counters.s1_survivors
    assert counters.s3_entries == counters.s2_survivors


@pytest.mark.parametrize("device", get_test_devices())
def test_streaming_cascade_no_cascade_mode(device: torch.device) -> None:
    torch.manual_seed(42)
    cfg = CascadeConfig(enable_cascade=False)
    cascade = StreamingGPUCascade(config=cfg, device=device)

    programs = gpu_sample_structured(20, device=device)
    xs = torch.linspace(-5.0, 5.0, 64, device=device)
    ys = xs**2

    fitness, _, counters = cascade.evaluate(programs, xs, ys)
    assert fitness.shape == (20,)
    assert counters.s3_entries == counters.s0_survivors


@pytest.mark.parametrize("device", get_test_devices())
def test_cascade_accuracy_audit(device: torch.device) -> None:
    torch.manual_seed(101)
    cfg = CascadeConfig(
        s1_points=32,
        s2_points=128,
        k_cutoff=8.0,
        enable_cascade=True,
    )
    cascade = StreamingGPUCascade(config=cfg, device=device)

    programs = gpu_sample_structured(50, device=device)
    xs = torch.linspace(-5.0, 5.0, 256, device=device)
    ys = xs**2 + 2.0 * xs + 1.0

    audit_res = audit_cascade_accuracy(programs, xs, ys, cascade, top_k=8)

    assert "false_rejection_rate" in audit_res
    assert "quality_loss" in audit_res
    assert audit_res["false_rejection_rate"] <= 0.05
    assert audit_res["passed_predeclared_audit"] is True


@pytest.mark.parametrize("device", get_test_devices())
def test_gpu_resident_evolution_with_cascade(device: torch.device) -> None:
    torch.manual_seed(2026)
    xs = np.linspace(-5.0, 5.0, 128, dtype=np.float32)
    ys = xs**2 + 3.0 * xs + 7.0

    casc_cfg = CascadeConfig(s1_points=32, s2_points=64, k_cutoff=6.0)
    cascade = StreamingGPUCascade(config=casc_cfg, device=device)

    evo_cfg = EvolutionConfig(pop_size=50, elite_k=8)
    evo = GPUResidentEvolution(xs, ys, config=evo_cfg, device=device, cascade=cascade)

    step_res = evo.step()
    assert "cascade_counters" in step_res
    counters = step_res["cascade_counters"]
    assert counters["s0_entries"] == 50
    assert counters["s1_entries"] > 0
