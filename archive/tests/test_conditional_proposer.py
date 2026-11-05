"""Unit and integration tests for P107 lightweight conditional neural proposer."""

from __future__ import annotations

import tempfile
from pathlib import Path

import torch

from evobyte.models import (
    CANONICAL_ALGEBRAIC_IDENTITIES,
    CANONICAL_LEAN_TACTICS,
    P107_MAX_PARAMS,
    StructuredConditionalProposer,
    encode_divisor_features,
    encode_instance_features,
)
from evobyte.training import (
    evaluate_proposer_vs_baselines,
    train_conditional_proposer,
)


def test_proposer_parameter_and_memory_limit():
    model = StructuredConditionalProposer()
    params = model.count_parameters()
    mem = model.resident_memory_mb()

    assert params <= P107_MAX_PARAMS, f"Parameters {params} exceeded 5M"
    assert params > 100_000, f"Model too trivial: {params} params"
    assert mem < 100.0, f"Memory {mem} MB exceeded 100 MB"


def test_feature_encoders_deterministic():
    f1 = encode_instance_features(4, 101)
    f2 = encode_instance_features(4, 101)
    assert torch.equal(f1, f2)
    assert f1.shape[0] == 45

    d1 = encode_divisor_features(4, 101, 7)
    d2 = encode_divisor_features(4, 101, 7)
    assert torch.equal(d1, d2)
    assert d1.shape[0] == 18


def test_proposer_forward_shapes():
    model = StructuredConditionalProposer()
    inst_f = torch.randn(2, 45)
    div_f = torch.randn(2, 5, 18)

    out = model(inst_f, div_f)
    assert "instance_embed" in out
    assert "tactic_logits" in out
    assert "identity_logits" in out
    assert "divisor_scores" in out

    assert out["instance_embed"].shape == (2, 256)
    assert out["tactic_logits"].shape == (2, len(CANONICAL_LEAN_TACTICS))
    assert out["identity_logits"].shape == (2, len(CANONICAL_ALGEBRAIC_IDENTITIES))
    assert out["divisor_scores"].shape == (2, 5)


def test_zero_hallucination_ranking():
    model = StructuredConditionalProposer()
    candidates = [4, 12, 101, 7, 19, 202]
    ranked = model.rank_divisors(4, 101, candidates)

    assert set(ranked) == set(candidates), "Proposer invented or dropped candidates!"
    assert len(ranked) == len(candidates)
    # Check that it's a valid permutation
    assert sorted(ranked) == sorted(candidates)


def test_closed_vocabulary_tactics_and_identities():
    model = StructuredConditionalProposer()
    tactics = model.predict_tactics(4, 101)
    assert len(tactics) == len(CANONICAL_LEAN_TACTICS)
    prob_sum = sum(p for _, p in tactics)
    assert abs(prob_sum - 1.0) < 1e-4
    for name, p in tactics:
        assert name in CANONICAL_LEAN_TACTICS
        assert 0.0 <= p <= 1.0

    identities = model.predict_identities(4, 101)
    assert len(identities) == len(CANONICAL_ALGEBRAIC_IDENTITIES)
    prob_sum_id = sum(p for _, p in identities)
    assert abs(prob_sum_id - 1.0) < 1e-4
    for name, p in identities:
        assert name in CANONICAL_ALGEBRAIC_IDENTITIES
        assert 0.0 <= p <= 1.0


def test_checkpoint_save_and_reload():
    model = StructuredConditionalProposer()
    candidates = [3, 7, 11, 15]

    with tempfile.TemporaryDirectory() as tmp_dir:
        ckpt_path = Path(tmp_dir) / "test_model.pt"
        model.save_checkpoint(ckpt_path, metadata={"tag": "p107_test"})

        loaded_model, meta = StructuredConditionalProposer.load_checkpoint(ckpt_path)
        assert meta.get("tag") == "p107_test"

        r1 = model.rank_divisors(4, 97, candidates)
        r2 = loaded_model.rank_divisors(4, 97, candidates)
        assert r1 == r2


def test_training_reproducibility():
    r1 = train_conditional_proposer(max_epochs=3, instance_count=15, seed=42)
    r2 = train_conditional_proposer(max_epochs=3, instance_count=15, seed=42)

    assert r1["status"] == "PASS"
    assert r2["status"] == "PASS"
    assert r1["val_loss_history"] == r2["val_loss_history"]
    assert r1["best_val_loss"] == r2["best_val_loss"]


def test_proposer_vs_baselines_speedup():
    train_res = train_conditional_proposer(max_epochs=4, instance_count=20, seed=42)
    model = train_res["model"]

    eval_res = evaluate_proposer_vs_baselines(model)
    assert eval_res["zero_hallucination"] is True
    assert eval_res["hallucinations"] == 0
    assert eval_res["sound"] is True
    assert eval_res["speedup_vs_naive"] >= 1.5, f"Speedup {eval_res['speedup_vs_naive']} < 1.5"
