"""Unit tests for micro neural bytecode generator (P12)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import torch

_REPO_ROOT = Path(__file__).resolve().parents[1]

from evobyte.bytecode import N_INSTR, decode_instr, is_valid
from evobyte.evolution import sample_structured
from evobyte.generator import (
    MAX_GENERATOR_PARAMS,
    MIN_GENERATOR_PARAMS,
    P53_EXPLORATION_FLOOR,
    P53_MAX_PARAMS,
    BytecodeAutoregressiveModel,
    GeneratorConfig,
    MicroGenerator,
    SequentialHistoryProposer,
    assert_generator_resource_cap,
    encode_programs_to_tensors,
    load_proposer,
    p53_position_mask_id,
    p53_proposer_schema,
    sample_proposer_standalone,
    save_proposer,
    train_sequential_proposer,
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


def test_p53_proposer_within_param_cap() -> None:
    model = SequentialHistoryProposer(feat_dim=16, gru_width=64)
    assert model.count_parameters() <= P53_MAX_PARAMS
    assert p53_position_mask_id(15) == 1
    assert all(p53_position_mask_id(t) == 0 for t in range(15))


def test_p53_proposer_is_history_conditional() -> None:
    torch.manual_seed(0)
    model = SequentialHistoryProposer(feat_dim=16, gru_width=64)
    model.eval()
    feats = torch.zeros(1, 16)
    zeros = torch.zeros(1, 3, dtype=torch.long)
    ones = torch.ones(1, 3, dtype=torch.long)
    with torch.no_grad():
        a = model.propose_step(feats, zeros, zeros, zeros, zeros)[0]
        b = model.propose_step(feats, ones, ones % 8, ones % 8, ones)[0]
    assert not torch.allclose(a, b), "position-only network is not history-conditional"


def test_p53_train_sample_save_load_roundtrip(tmp_path) -> None:
    import json as _json

    corpus = _json.loads((_REPO_ROOT / "experiments" / "p52-certified-data.json").read_text())
    train = [p for p in corpus["positives"] if p["split"] == "train"][:32]
    val = [p for p in corpus["positives"] if p["split"] == "val"][:8]

    def _feats(ps):
        return np.array([p["features_inference_only"] for p in ps], dtype=np.float32)

    def _progs(ps):
        return np.array([p["program_words"] for p in ps], dtype=np.uint32)

    res = train_sequential_proposer(
        train_features=_feats(train),
        train_programs=_progs(train),
        val_features=_feats(val),
        val_programs=_progs(val),
        seed=3,
        max_epochs=2,
        device="cpu",
    )
    assert res["best_epoch"] >= 0
    assert all(np.isfinite(res["train_curve"])) and all(np.isfinite(res["val_curve"]))
    schema = p53_proposer_schema(feature_mean=res["feature_mean"], feature_std=res["feature_std"])
    mu = np.array(res["feature_mean"])
    sg = np.array(res["feature_std"])
    probe = ((_feats(val) - mu) / sg).astype(np.float32)[:2]
    w_path = tmp_path / "p53-proposer.pt"
    save_proposer(w_path, res["model"])
    fresh = load_proposer(w_path, schema, "cpu")
    p1, o1 = sample_proposer_standalone(res["model"], probe, 8, seed=5, device="cpu")
    p2, _ = sample_proposer_standalone(fresh, probe, 8, seed=5, device="cpu")
    assert all(is_valid(p) for p in p1)
    assert all((a == b).all() for a, b in zip(p1, p2))
    assert sum(o == "floor" for o in o1) / len(o1) >= P53_EXPLORATION_FLOOR
