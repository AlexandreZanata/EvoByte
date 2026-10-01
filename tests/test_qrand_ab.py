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
    PREREGISTRATION_HASH,
    PREREGISTRATION_SPEC,
    PROBE_POINTS,
    compute_expression_signatures,
    encode_program_tensor,
    run_amplitude_arm,
    run_genetic_arm,
    run_learned_arm,
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
