"""Tests for P27 Quantum-Inspired Randomness Hypotheses A/B Testing Harness."""

from __future__ import annotations

import sys
from pathlib import Path

import torch

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "benchmarks"))

from benchmarks.qrand_ab import (
    LITERATURE_NOTE,
    P37_ARMS,
    P37_HYPOTHESIS,
    P37_LITERATURE_NOTE,
    P37_PREREGISTRATION_HASH,
    P37_PREREGISTRATION_SPEC,
    PREREGISTRATION_HASH,
    PREREGISTRATION_SPEC,
    PROBE_POINTS,
    compute_expression_signatures,
    encode_program_tensor,
    p55_budget_gate,
    run_amplitude_arm,
    run_bigram_arm,
    run_controlled_qrand,
    run_genetic_arm,
    run_learned_arm,
    run_p37_genetic_arm,
    run_qrand_experiment,
    run_uniform_arm,
)


def test_preregistration_hash_and_literature() -> None:
    assert len(PREREGISTRATION_HASH) == 64
    assert "HYPOTHESIS: amplitude-distribution" in PREREGISTRATION_SPEC
    assert "FALSIFICATION THRESHOLD" in PREREGISTRATION_SPEC
    assert "EQUATIONS" in PREREGISTRATION_SPEC
    assert len(LITERATURE_NOTE["prior_art"]) >= 2
    assert "novelty_boundary" in LITERATURE_NOTE


def test_encode_program_tensor() -> None:
    dev = torch.device("cpu")
    ops = torch.randint(0, 16, (20, 16), device=dev)
    progs = encode_program_tensor(ops, dev)
    assert progs.shape == (20, 16)
    # Ensure every program writes to r7 (dst field in bits 8-15 is 7)
    dsts = (progs >> 8) & 0xFF
    op_codes = progs & 0xFF
    has_r7 = ((dsts == 7) & (op_codes != 0)).any(dim=1)
    assert has_r7.all()


def test_compute_expression_signatures() -> None:
    dev = torch.device("cpu")
    ops = torch.full((5, 16), 0x01, dtype=torch.int64, device=dev)  # ADD
    progs = encode_program_tensor(ops, dev)
    probe_xs = torch.from_numpy(PROBE_POINTS).to(dev)

    sigs = compute_expression_signatures(progs, probe_xs, dev)
    assert isinstance(sigs, set)


def test_search_arms_execute() -> None:
    dev = torch.device("cpu")
    xs_tr = torch.linspace(-5.0, 5.0, 32, device=dev)
    ys_tr = xs_tr**2 + 3.0 * xs_tr + 7.0
    xs_te = torch.linspace(-5.0, 5.0, 32, device=dev)
    ys_te = xs_te**2 + 3.0 * xs_te + 7.0
    probe_xs = torch.from_numpy(PROBE_POINTS).to(dev)

    # 1. Uniform
    u = run_uniform_arm(
        xs_train=xs_tr,
        ys_train=ys_tr,
        xs_test=xs_te,
        ys_test=ys_te,
        probe_xs=probe_xs,
        device=dev,
        budget_sec=0.1,
        pop_size=20,
    )
    assert u["arm"] == "uniform"
    assert u["candidates_evaluated"] > 0
    assert "held_out_mse" in u

    # 2. Learned
    l_arm = run_learned_arm(
        xs_train=xs_tr,
        ys_train=ys_tr,
        xs_test=xs_te,
        ys_test=ys_te,
        probe_xs=probe_xs,
        device=dev,
        budget_sec=0.1,
        pop_size=20,
    )
    assert l_arm["arm"] == "learned-dist"
    assert l_arm["candidates_evaluated"] > 0

    # 3. Genetic
    g = run_genetic_arm(
        xs_train=xs_tr,
        ys_train=ys_tr,
        xs_test=xs_te,
        ys_test=ys_te,
        probe_xs=probe_xs,
        device=dev,
        budget_sec=0.1,
        pop_size=20,
    )
    assert g["arm"] == "genetic"
    assert g["candidates_evaluated"] > 0

    # 4. Amplitude
    a = run_amplitude_arm(
        xs_train=xs_tr,
        ys_train=ys_tr,
        xs_test=xs_te,
        ys_test=ys_te,
        probe_xs=probe_xs,
        device=dev,
        budget_sec=0.1,
        pop_size=20,
    )
    assert a["arm"] == "amplitude-distribution"
    assert a["candidates_evaluated"] > 0


def test_full_experiment_fast(tmp_path: Path) -> None:
    out_file = tmp_path / "test-p27.json"
    manifest = run_qrand_experiment(
        hypothesis_name="amplitude-distribution",
        seeds_count=2,
        budget_sec=0.1,
        pop_size=20,
        device_name="cpu",
        output_path=out_file,
    )

    assert out_file.exists()
    assert manifest["phase"] == "p27-qrand-hypotheses"
    assert manifest["status"] == "complete"
    assert "verdict" in manifest
    assert manifest["verdict"] in ("CONFIRMED", "PARTIAL", "FALSIFIED_NULL")
    assert "comparisons" in manifest
    assert "aggregates_by_arm" in manifest
    assert len(manifest["aggregates_by_arm"]) == 4
    assert "manifest_sha256" in manifest


def test_p37_preregistration_and_literature() -> None:
    assert P37_HYPOTHESIS == "dependency-correlated"
    assert len(P37_PREREGISTRATION_HASH) == 64
    assert "HYPOTHESIS: dependency-correlated" in P37_PREREGISTRATION_SPEC
    assert "MATCHED CLASSICAL CONTROL" in P37_PREREGISTRATION_SPEC
    assert "FALSIFICATION / VERDICT RULE" in P37_PREREGISTRATION_SPEC
    assert "UNCERTAINTY" in P37_PREREGISTRATION_SPEC
    assert len(P37_LITERATURE_NOTE["prior_art"]) >= 2
    assert "novelty_boundary" in P37_LITERATURE_NOTE


def test_p37_bigram_arms_execute() -> None:
    from benchmarks.qrand_ab import _p37_task_grids

    dev = torch.device("cpu")
    grids = _p37_task_grids("x**2+3*x+7")
    xs_tr = torch.from_numpy(grids["train_xs"].astype("float32")).to(dev)
    ys_tr = torch.from_numpy(grids["train_ys"].astype("float32")).to(dev)
    probe_xs = torch.from_numpy(PROBE_POINTS).to(dev)

    for arm in ("matched-classical", "dependency-correlated"):
        r = run_bigram_arm(
            arm=arm,
            xs_train=xs_tr,
            ys_train=ys_tr,
            probe_xs=probe_xs,
            device=dev,
            budget_sec=0.2,
            pop_size=16,
            gt_formula="x**2+3*x+7",
            grids=grids,
        )
        assert r["arm"] == arm
        assert r["candidates_evaluated"] > 0
        for key in ("sample_sec", "eval_sec", "update_sec", "trace_sec", "warmup_sec"):
            assert r[key] >= 0.0
        assert "certificate" in r and "verified" in r and "verified_per_sec" in r
        assert "time_to_certified_sec" in r and "censored" in r

    g = run_p37_genetic_arm(
        xs_train=xs_tr,
        ys_train=ys_tr,
        probe_xs=probe_xs,
        device=dev,
        budget_sec=0.2,
        pop_size=16,
        gt_formula="x**2+3*x+7",
        grids=grids,
    )
    assert g["arm"] == "genetic"
    assert g["candidates_evaluated"] > 0
    assert "verified_per_sec" in g


def test_p37_controlled_pilot_smoke(tmp_path: Path) -> None:
    out_file = tmp_path / "p37-smoke.json"
    manifest = run_controlled_qrand(
        hypothesis="dependency-correlated",
        budgets_str="0.3s",
        seeds_count=1,
        scale_factor=1.0,
        device_name="cpu",
        output_path=out_file,
        smoke=True,
        pop_size=16,
    )
    assert out_file.exists()
    assert manifest["phase"] == "p37-controlled-qrand"
    assert manifest["status"] == "complete"
    assert manifest["hypothesis"]["name"] == "dependency-correlated"
    assert manifest["hypothesis"]["preregistration_hash"] == P37_PREREGISTRATION_HASH
    assert manifest["verdict"] in ("GAIN", "NULL", "LOSS")
    assert set(manifest["aggregates_by_arm"]) == set(P37_ARMS)
    assert "paired_diff_ci95" in manifest["comparisons"]
    assert "manifest_sha256" in manifest


def test_p37_rejects_parallel_mechanisms(tmp_path: Path) -> None:
    import pytest

    with pytest.raises(ValueError, match="exactly one mechanism"):
        run_controlled_qrand(
            hypothesis="amplitude-distribution+dependency-correlated",
            budgets_str="0.3s",
            seeds_count=1,
            device_name="cpu",
            output_path=tmp_path / "p37-bad.json",
            smoke=True,
        )


def test_p55_budget_gate_defers_without_budget_or_mechanism() -> None:
    gate = p55_budget_gate({})
    assert gate["execute"] is False
    assert gate["compute_sec"] == 0.0
    assert any("budget" in m for m in gate["missing"])
    assert gate["historical"]["phase"] == "P37"
    assert gate["historical"]["result"] == "NULL"

    partial = p55_budget_gate({"approved_budget_sec": 600.0})
    assert partial["execute"] is False
    assert any("mechanism" in m for m in partial["missing"])

    complete = p55_budget_gate(
        {
            "approved_budget_sec": 600.0,
            "mechanism": "single-test-transform",
            "procedure": {
                "metric": "certified success",
                "paired_analysis": "paired",
                "multiple_comparison_correction": "holm",
                "keep_rule": "ci",
            },
        }
    )
    assert complete["execute"] is True
    assert complete["missing"] == []
