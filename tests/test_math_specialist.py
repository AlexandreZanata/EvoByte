"""Unit tests for P23 math specialist pilot harness."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import torch

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "src"))
sys.path.insert(0, str(_REPO_ROOT / "benchmarks"))

from benchmarks.math_db import RAW_PATH
from benchmarks.math_specialist import (
    CountingOpcodeDistributor,
    MathCorpus,
    TinyMathProposer,
    build_math_corpus,
    get_pilot_targets,
    run_four_way_trial,
    sample_neural_candidates,
    train_neural_proposer,
)
from evobyte.bytecode import N_INSTR


def test_build_math_corpus_isolation() -> None:
    if not RAW_PATH.exists():
        pytest.skip("GSM8K dataset not downloaded; run math_db.py --download")

    corpus = build_math_corpus(seed=0)
    assert isinstance(corpus, MathCorpus)
    assert corpus.n_hidden_sealed == 199
    assert corpus.n_train_rows == 923
    assert corpus.n_val_rows == 197
    assert len(corpus.corpus_hash) == 64
    assert len(corpus.chains) > 0
    assert "ADD" in corpus.operator_counts
    assert "MUL" in corpus.operator_counts


def test_counting_distributor() -> None:
    # Test with synthetic corpus if needed or real corpus
    fake_corpus = MathCorpus(
        chains=[{"expr": "2 + 3", "result": "5", "computed": 5}],
        operator_counts={"ADD": 10, "SUB": 5, "MUL": 15, "DIV": 2, "POW": 0},
        corpus_hash="0" * 64,
        n_train_rows=10,
        n_val_rows=2,
        n_hidden_sealed=199,
    )
    device = torch.device("cpu")
    dist = CountingOpcodeDistributor(fake_corpus, device=device)

    assert dist.param_count == 0
    assert dist.training_time_sec >= 0.0

    samples = dist.sample(16)
    assert samples.shape == (16, N_INSTR)
    assert samples.dtype == torch.int64


def test_tiny_neural_proposer_capacity_and_sampling() -> None:
    device = torch.device("cpu")
    model = TinyMathProposer(hidden_dim=128).to(device)
    param_count = sum(p.numel() for p in model.parameters())

    # Constraint: <= 5M parameters
    assert param_count <= 5_000_000
    assert param_count > 1000

    fake_corpus = MathCorpus(
        chains=[],
        operator_counts={"ADD": 100, "SUB": 50, "MUL": 150, "DIV": 20, "POW": 0},
        corpus_hash="0" * 64,
        n_train_rows=10,
        n_val_rows=2,
        n_hidden_sealed=199,
    )
    trained_model, billed = train_neural_proposer(fake_corpus, device=device, epochs=1)
    assert billed["model_parameters"] == param_count
    assert billed["training_time_sec"] >= 0.0
    assert "final_loss" in billed

    cands = sample_neural_candidates(trained_model, 8, device=device)
    assert cands.shape == (8, N_INSTR)
    assert cands.dtype == torch.int64


def test_pilot_targets() -> None:
    targets = get_pilot_targets()
    assert len(targets) == 5
    for t in targets:
        assert len(t.xs) == 64
        assert len(t.ys) == 64
        assert t.key.startswith("target_")


def test_four_way_trial_smoke() -> None:
    targets = get_pilot_targets()
    device = torch.device("cpu")
    fake_corpus = MathCorpus(
        chains=[],
        operator_counts={"ADD": 10, "SUB": 5, "MUL": 10, "DIV": 5, "POW": 0},
        corpus_hash="0" * 64,
        n_train_rows=10,
        n_val_rows=2,
        n_hidden_sealed=199,
    )
    dist = CountingOpcodeDistributor(fake_corpus, device=device)

    res = run_four_way_trial(
        arm="genetic",
        target=targets[0],
        budget_sec=0.05,
        seed=42,
        device=device,
        distributor=dist,
    )
    assert res["arm"] == "genetic"
    assert res["target"] == targets[0].key
    assert "search_cvps" in res
    assert "best_mse" in res
    assert "candidates_total" in res
