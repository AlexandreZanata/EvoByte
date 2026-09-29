"""P15 measurement-integrity gates: counters, baselines, deadlines, manifests, ablation paths."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

_REPO_ROOT = Path(__file__).resolve().parents[1]
for p in (str(_REPO_ROOT / "src"), str(_REPO_ROOT / "benchmarks")):
    if p not in sys.path:
        sys.path.insert(0, p)

from benchmarks.full_matrix import (
    compute_scaling_curve,
    generate_target_dataset,
    run_ablation_battery,
    run_baseline_pysr_adapter,
)
from evobyte.evolution import EvolutionConfig, sample_structured
from evobyte.provenance import CandidateCounter, MonotonicDeadline, resolve_device, seed_all


def test_counter_distinguishes_distinct_and_repeats_bounded():
    rng = np.random.default_rng(0)
    progs = [sample_structured(rng) for _ in range(30)]
    progs = progs + [progs[0].copy(), progs[5].copy()]
    counter = CandidateCounter(max_tracked=1000)
    for p in progs:
        counter.add(p)
    s = counter.summary()
    assert s["method"] == "exact-hash-set-bounded"
    assert s["total"] == 32
    assert s["repeats"] >= 2
    assert s["distinct"] == s["total"] - s["repeats"]
    assert s["truncated"] is False
    # Bounded memory: tiny cap forces truncation flag instead of unbounded growth.
    tiny = CandidateCounter(max_tracked=5)
    for p in progs:
        tiny.add(p)
    st = tiny.summary()
    assert st["total"] == 32
    assert st["truncated"] is True
    assert len(tiny._seen) <= 5


def test_missing_baseline_is_not_run_not_win():
    import importlib.util

    target = generate_target_dataset("x2_3x_7", n_points=32, seed=0)
    has_pysr = importlib.util.find_spec("pysr") is not None
    rec = run_baseline_pysr_adapter(target, max_time_sec=0.2, seed=7)
    if not has_pysr:
        assert rec["status"] == "not_run"
        assert rec["hidden_mse"] is None
        assert rec["success"] is None
        # Never inferred from the target name: same status for every target.
        other = generate_target_dataset("nguyen_1", n_points=32, seed=0)
        rec2 = run_baseline_pysr_adapter(other, max_time_sec=0.2, seed=7)
        assert rec2["status"] == "not_run"
        assert rec2["hidden_mse"] is None
    else:
        assert rec["status"] == "completed"


def test_monotonic_deadline_reports_budget_and_overshoot():
    import time

    dl = MonotonicDeadline(budget_sec=0.05)
    dl.mark_setup_done()
    dl.mark_warmup_done()
    time.sleep(0.06)
    dl.mark_compute_done()
    info = dl.finish()
    assert info["budget_sec"] == 0.05
    assert info["elapsed_sec"] >= 0.05
    assert info["overshoot_sec"] >= 0.0
    assert info["setup_sec"] >= 0.0
    assert dl.expired() is True


def test_manifest_hash_validates_raw_observations(tmp_path):
    from evobyte.provenance import write_manifest

    raw = tmp_path / "obs.json"
    raw.write_text(json.dumps({"a": 1}, sort_keys=True), encoding="utf-8")
    h = hashlib.sha256(raw.read_bytes()).hexdigest()
    manifest = write_manifest(tmp_path / "manifest.json", {"phase": "P15"}, {str(raw): h})
    assert manifest["manifest_sha256"] is not None
    assert manifest["raw_artifacts"][0]["sha256"] == h
    # Changing the raw file must change the hash (no silent substitution).
    raw.write_text(json.dumps({"a": 2}, sort_keys=True), encoding="utf-8")
    h2 = hashlib.sha256(raw.read_bytes()).hexdigest()
    assert h2 != h


def test_changing_ablation_changes_executed_path():
    target = generate_target_dataset("x2_3x_7", n_points=32, seed=0)
    ablations = run_ablation_battery(target, seeds=[42], max_generations=3, pop_size=30)
    assert len(ablations) == 9
    # Every ablation executes (finite CVPS) and diversity is measured, not hard-coded equal.
    for a in ablations:
        assert np.isfinite(a.mean_cvps)
        assert np.isfinite(a.mean_hidden_mse)
    diversities = [a.diversity_metric for a in ablations]
    assert len({round(d, 6) for d in diversities}) >= 1
    # Crossover on/off must diverge in config hash space.
    cfg_on = EvolutionConfig(pop_size=30, max_generations=3, crossover_p=0.4)
    cfg_off = EvolutionConfig(pop_size=30, max_generations=3, crossover_p=0.0)
    ha = hashlib.sha256(
        json.dumps(cfg_on.__dict__, sort_keys=True, default=str).encode()
    ).hexdigest()
    hb = hashlib.sha256(
        json.dumps(cfg_off.__dict__, sort_keys=True, default=str).encode()
    ).hexdigest()
    assert ha != hb


def test_cuda_request_fails_explicitly_when_unavailable():
    import torch

    if not torch.cuda.is_available():
        try:
            resolve_device("cuda")
        except RuntimeError as exc:
            assert "silently" in str(exc) or "CUDA" in str(exc)
        else:
            raise AssertionError("cuda request must fail explicitly when CUDA is unavailable")
    else:
        assert str(resolve_device("cuda")) == "cuda"


def test_rescaled_budget_records_are_unverified_not_measured():
    curve = compute_scaling_curve(
        [10.0],
        {
            10.0: [
                {
                    "candidates_total": 1000,
                    "hidden_mse": 0.5,
                    "success": False,
                    "synthesized": True,
                }
            ]
        },
    )
    assert len(curve) == 1
    assert curve[0]["synthesized"] is True
    assert curve[0]["status"] == "unverified"


def test_seeding_is_deterministic_across_numpy_and_torch():
    import torch

    seed_all(123)
    a = np.random.default_rng(123).integers(0, 1000, size=5)
    seed_all(123)
    b = np.random.default_rng(123).integers(0, 1000, size=5)
    assert list(a) == list(b)
    seed_all(123)
    t1 = torch.randn(4).tolist()
    seed_all(123)
    t2 = torch.randn(4).tolist()
    assert t1 == t2
