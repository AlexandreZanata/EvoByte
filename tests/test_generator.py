"""Unit tests for micro neural bytecode generator (P12)."""

from __future__ import annotations

import numpy as np
import pytest
import torch

from evobyte.bytecode import N_INSTR, decode_instr, is_valid
from evobyte.evolution import sample_structured
from evobyte.generator import (
    MAX_GENERATOR_PARAMS,
    MIN_GENERATOR_PARAMS,
    BytecodeAutoregressiveModel,
    GeneratorConfig,
    MicroGenerator,
    assert_generator_resource_cap,
    encode_programs_to_tensors,
)


def test_generator_param_count_and_vram_cap() -> None:
    model = BytecodeAutoregressiveModel(
        d_model=128,
        nhead=4,
        num_layers=3,
        dim_feedforward=256,
    )
    caps = assert_generator_resource_cap(model, max_mb=100.0)

    assert MIN_GENERATOR_PARAMS <= caps["param_count"] <= MAX_GENERATOR_PARAMS
    assert caps["resident_mb"] <= 100.0
    assert caps["param_count"] == model.count_parameters()
    assert caps["resident_mb"] == pytest.approx(model.resident_memory_mb(), abs=1e-3)


def test_generator_rejection_of_undersized_model() -> None:
    # Model with very small dimensions that has < 100K params
    tiny_model = BytecodeAutoregressiveModel(
        d_model=16,
        nhead=2,
        num_layers=1,
        dim_feedforward=32,
    )
    with pytest.raises(ValueError, match="below minimum threshold"):
        assert_generator_resource_cap(tiny_model)


def test_generator_rejection_of_oversized_model() -> None:
    # Model that exceeds 5M params
    huge_model = BytecodeAutoregressiveModel(
        d_model=512,
        nhead=8,
        num_layers=12,
        dim_feedforward=2048,
    )
    with pytest.raises(ValueError, match="exceeds maximum cap"):
        assert_generator_resource_cap(huge_model)


def test_generator_rejection_of_exceeded_vram_cap() -> None:
    model = BytecodeAutoregressiveModel(
        d_model=128,
        nhead=4,
        num_layers=3,
        dim_feedforward=256,
    )
    # Exceeding an artificially low 0.5 MB cap
    with pytest.raises(ValueError, match="exceeds VRAM cap"):
        assert_generator_resource_cap(model, max_mb=0.5)


def test_generator_unconditional_sampling_s0_valid() -> None:
    cfg = GeneratorConfig(d_model=128, nhead=4, num_layers=2, dim_feedforward=256)
    gen = MicroGenerator(config=cfg, device="cpu")

    samples = gen.sample_candidates(n=16, temperature=0.8)
    assert samples.shape == (16, N_INSTR)
    assert samples.dtype == np.uint32

    # Every sampled candidate must be syntactically valid (has write to r7, valid ops)
    for i in range(16):
        prog = samples[i]
        assert is_valid(prog)


def test_generator_prefix_conditioned_sampling() -> None:
    cfg = GeneratorConfig(d_model=128, nhead=4, num_layers=2, dim_feedforward=256)
    gen = MicroGenerator(config=cfg, device="cpu")

    # Create dummy elite program
    rng = np.random.default_rng(42)
    elite = sample_structured(rng)

    k = 4
    elites = np.stack([elite] * 4)
    samples = gen.sample_candidates(
        n=4,
        elites=elites,
        p_prefix_condition=1.0,
        min_prefix=k,
        max_prefix=k,
        temperature=0.7,
    )

    # Prefix of length k must match the original elite
    for i in range(4):
        for step in range(k):
            op_orig, dst_orig, a_orig, b_orig = decode_instr(elite[step])
            op_samp, dst_samp, a_samp, b_samp = decode_instr(samples[i, step])
            assert op_orig == op_samp
            assert dst_orig == dst_samp
            assert a_orig == a_samp
            # b register is masked modulo 8 unless CSEL
            if op_orig == 0x0F:
                assert (b_orig & 0x0F) == (b_samp & 0x0F)
            else:
                assert (b_orig % 8) == (b_samp % 8)


def test_generator_training_on_elites() -> None:
    cfg = GeneratorConfig(d_model=128, nhead=4, num_layers=2, dim_feedforward=256, lr=5e-3)
    gen = MicroGenerator(config=cfg, device="cpu")

    rng = np.random.default_rng(123)
    elites = np.stack([sample_structured(rng) for _ in range(16)])

    # Record initial loss
    ops, dsts, as_, bs = encode_programs_to_tensors(elites, device="cpu")
    with torch.no_grad():
        init_loss = float(gen.model.forward_loss(ops, dsts, as_, bs).item())

    # Train for 5 epochs
    res = gen.train_on_elites(elites, epochs=8)
    assert res["steps"] > 0
    assert res["time_sec"] > 0

    with torch.no_grad():
        final_loss = float(gen.model.forward_loss(ops, dsts, as_, bs).item())

    assert final_loss < init_loss


def test_generator_pipeline_step() -> None:
    cfg = GeneratorConfig(d_model=128, nhead=4, num_layers=2, dim_feedforward=256)
    gen = MicroGenerator(config=cfg, device="cpu")

    rng = np.random.default_rng(999)
    elites = np.stack([sample_structured(rng) for _ in range(8)])

    candidates, stats = gen.pipeline_step(
        elites=elites,
        n_candidates=10,
        rng=rng,
        p_mutation=0.2,
        train_epochs=2,
    )

    assert candidates.shape == (10, N_INSTR)
    assert stats["candidates_count"] == 10
    assert stats["total_pipeline_time_sec"] > 0.0
    for cand in candidates:
        assert is_valid(cand)
