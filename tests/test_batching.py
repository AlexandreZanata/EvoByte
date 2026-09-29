"""Tests for VRAM-aware chunking and OOM-safe execution (P06 gate)."""

from unittest.mock import patch

import numpy as np
import pytest
import torch

from evobyte.batching import (
    compute_chunk_size,
    execute_chunked,
    get_recommended_cascade_policy,
)
from evobyte.evolution import sample_structured
from evobyte.vm_torch import execute_population_torch


def test_compute_chunk_size_scaling():
    # As points increase, max candidates per chunk must decrease
    c_256 = compute_chunk_size(256, vram_budget_mb=7500.0)
    c_1024 = compute_chunk_size(1024, vram_budget_mb=7500.0)
    c_4096 = compute_chunk_size(4096, vram_budget_mb=7500.0)

    assert c_256 > c_1024 > c_4096
    assert c_4096 >= 1

    # As budget increases, chunk size increases
    c_low_budget = compute_chunk_size(256, vram_budget_mb=1000.0)
    c_high_budget = compute_chunk_size(256, vram_budget_mb=7500.0)
    assert c_high_budget > c_low_budget

    with pytest.raises(ValueError):
        compute_chunk_size(0)
    with pytest.raises(ValueError):
        compute_chunk_size(256, vram_budget_mb=-100)


def test_execute_chunked_conformance_with_unchunked():
    rng = np.random.default_rng(42)
    P = 50
    B = 64
    progs = np.stack([sample_structured(rng) for _ in range(P)])
    xs = np.linspace(-5.0, 5.0, B, dtype=np.float32)

    # Reference unchunked execution
    ref_preds, ref_flags = execute_population_torch(progs, xs)

    # Chunked execution with chunk_size = 13 (non-divisor)
    chunked_preds, chunked_flags = execute_chunked(progs, xs, chunk_size=13)

    assert torch.allclose(chunked_preds, ref_preds, rtol=1e-5, atol=1e-5)
    assert torch.equal(chunked_flags, ref_flags)


def test_execute_chunked_empty_population():
    xs = np.linspace(-1.0, 1.0, 32, dtype=np.float32)
    empty_progs = np.empty((0, 16), dtype=np.uint32)
    preds, flags = execute_chunked(empty_progs, xs)
    assert preds.shape == (0, 32)
    assert flags.shape == (0, 32)


def test_oom_safe_dynamic_shrink_fallback():
    rng = np.random.default_rng(99)
    P = 40
    B = 32
    progs = np.stack([sample_structured(rng) for _ in range(P)])
    xs = np.linspace(-2.0, 2.0, B, dtype=np.float32)

    real_execute = execute_population_torch
    attempt_sizes = []

    def mock_execute(batch, xs, x1s=None, device=None):
        attempt_sizes.append(len(batch))
        # Simulate OOM if batch slice > 10
        if len(batch) > 10:
            raise MemoryError("Simulated OOM for testing fallback")
        return real_execute(batch, xs, x1s=x1s, device=device)

    # Start with initial chunk_size=20; should fail, shrink to 10, and succeed
    with patch("evobyte.batching.execute_population_torch", side_effect=mock_execute):
        preds, flags = execute_chunked(progs, xs, chunk_size=20)

    assert preds.shape == (P, B)
    assert flags.shape == (P, B)
    # Verifies that it attempted 20, hit OOM, shrunk to 10, and processed in chunks of 10
    assert 20 in attempt_sizes
    assert 10 in attempt_sizes
    assert min(attempt_sizes) <= 10


def test_recommended_cascade_policy():
    policy = get_recommended_cascade_policy(vram_budget_mb=7500.0)
    assert policy["vram_budget_mb"] == 7500.0
    stages = policy["stages"]
    assert len(stages) == 3
    for s in stages:
        assert s["chunk_size"] >= 1
        assert s["est_vram_mb"] <= 7500.0
