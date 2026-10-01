"""Unit tests for P23 math specialist pilot harness."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
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
    MultiHeadJointSpecialist,
    SequentialSpecialist,
    TinyMathProposer,
    build_math_corpus,
    extract_problem_features,
    get_p28_family_targets,
    get_pilot_targets,
    run_four_way_trial,
    run_p28_specialist_rematch,
    sample_multihead_candidates,
    sample_neural_candidates,
    sample_sequential_candidates,
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


def test_problem_featurizer_properties() -> None:
    xs = np.linspace(-3.0, 3.0, 64, dtype=np.float32)
    ys_lin = 3.0 * xs + 2.0
    ys_quad = xs**2 - 4.0

    f_lin = extract_problem_features(xs, ys_lin)
    f_quad = extract_problem_features(xs, ys_quad)

    assert f_lin.shape == (16,)
    assert f_quad.shape == (16,)
    assert f_lin.dtype == torch.float32
    assert f_quad.dtype == torch.float32

    assert torch.isfinite(f_lin).all()
    assert torch.isfinite(f_quad).all()

    # Features should distinguish linear from quadratic
    assert not torch.allclose(f_lin, f_quad)


def test_p28_specialist_architectures_under_cap() -> None:
    mh = MultiHeadJointSpecialist(feat_dim=16, hidden_dim=128)
    seq = SequentialSpecialist(feat_dim=16, hidden_dim=128)

    p_mh = sum(p.numel() for p in mh.parameters())
    p_seq = sum(p.numel() for p in seq.parameters())

    assert p_mh <= 5_000_000, f"MultiHead param count {p_mh} exceeds 5M cap"
    assert p_seq <= 5_000_000, f"Sequential param count {p_seq} exceeds 5M cap"

    f = torch.randn(2, 16)
    lo, ld, la, lb = mh(f)
    assert lo.shape == (2, 16, 16)
    assert ld.shape == (2, 16, 8)
    assert la.shape == (2, 16, 8)
    assert lb.shape == (2, 16, 16)

    lo_s, ld_s, la_s, lb_s = seq(f)
    assert lo_s.shape == (2, 16, 16)
    assert ld_s.shape == (2, 16, 8)
    assert la_s.shape == (2, 16, 8)
    assert lb_s.shape == (2, 16, 16)


def test_p28_sampling_with_exploration_floor() -> None:
    device = torch.device("cpu")
    mh = MultiHeadJointSpecialist(feat_dim=16, hidden_dim=128).to(device)
    seq = SequentialSpecialist(feat_dim=16, hidden_dim=128).to(device)
    feat = torch.randn(16, device=device)

    cands_mh = sample_multihead_candidates(mh, 50, feat, device=device, exploration_floor=0.10)
    assert cands_mh.shape == (50, 16)
    assert cands_mh.dtype == torch.int64

    cands_seq = sample_sequential_candidates(seq, 50, feat, device=device, exploration_floor=0.10)
    assert cands_seq.shape == (50, 16)
    assert cands_seq.dtype == torch.int64


def test_p28_family_targets() -> None:
    train_t, heldout_t = get_p28_family_targets("polynomial_arithmetic")
    assert len(train_t) >= 4
    assert len(heldout_t) >= 3

    train_keys = {t.key for t in train_t}
    heldout_keys = {t.key for t in heldout_t}
    assert train_keys.isdisjoint(heldout_keys), "Train and held-out target sets must be disjoint"

    for t in train_t + heldout_t:
        assert len(t.xs) == 64
        assert len(t.ys) == 64
        assert np.isfinite(t.xs).all()
        assert np.isfinite(t.ys).all()


def test_p28_rematch_smoke() -> None:
    report = run_p28_specialist_rematch(
        family="polynomial_arithmetic",
        seeds_count=1,
        budget_sec=0.05,
        pop_size=64,
        device_name="cpu",
        output_path=None,
    )
    assert report["manifest_version"] == "1.0"
    assert report["phase"] == "p28-specialist-rematch"
    assert report["status"] == "PASS"
    assert "ruling" in report
    assert report["ruling"]["decision"] in ("KEEP", "DROP")
    assert "amortized_cost_analysis" in report
    assert "heldout_summary_table" in report
