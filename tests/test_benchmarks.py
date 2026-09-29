"""Unit tests for P13 benchmark matrix, baselines, ablations, and hypothesis verification."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "benchmarks"))

from benchmarks.full_matrix import (
    TARGET_REGISTRY,
    compute_pareto_front,
    compute_scaling_curve,
    generate_target_dataset,
    parse_budget_str,
    run_ablation_battery,
    run_baseline_classical,
    run_baseline_gp,
    run_baseline_pysr_adapter,
    run_baseline_random,
    run_evobyte_full,
    run_full_benchmark_matrix,
)


def test_parse_budget_str():
    assert parse_budget_str("10s") == 10.0
    assert parse_budget_str("1m") == 60.0
    assert parse_budget_str("10min") == 600.0
    assert parse_budget_str("1h") == 3600.0
    assert parse_budget_str("45") == 45.0


def test_suite_dataset_generation():
    for key in TARGET_REGISTRY:
        ds = generate_target_dataset(key, n_points=64, seed=42)
        assert ds.key == key
        assert len(ds.data_hash) == 16
        for split_name in ("train", "val", "hidden", "extrapolation"):
            xs, ys = ds.splits[split_name]
            assert len(xs) == 64
            assert len(ys) == 64
            assert np.all(np.isfinite(xs))
            assert np.all(np.isfinite(ys))

    # Verify deterministic data hash
    ds1 = generate_target_dataset("x2_3x_7", n_points=64, seed=0)
    ds2 = generate_target_dataset("x2_3x_7", n_points=64, seed=0)
    assert ds1.data_hash == ds2.data_hash


def test_baseline_random():
    target = generate_target_dataset("x_plus_1", n_points=32, seed=0)
    rec = run_baseline_random(target, max_time_sec=0.2, seed=42, batch_size=50)
    assert rec["method"] == "Random"
    assert rec["candidates_total"] > 0
    assert rec["cvps"] > 0
    assert np.isfinite(rec["train_mse"])
    assert rec["program_size"] >= 0


def test_baseline_gp():
    target = generate_target_dataset("x_plus_1", n_points=32, seed=0)
    rec = run_baseline_gp(target, max_time_sec=0.2, seed=42, pop_size=20)
    assert rec["method"] == "Classic-GP"
    assert rec["candidates_total"] > 0
    assert np.isfinite(rec["train_mse"])
    assert rec["program_size"] > 0


def test_baseline_classical():
    target = generate_target_dataset("x_plus_1", n_points=32, seed=0)
    rec = run_baseline_classical(target, max_time_sec=0.2, seed=42)
    assert rec["method"] == "Classical-SR"
    assert rec["success"] is True
    assert rec["hidden_mse"] < 1e-4


def test_baseline_pysr_adapter():
    target = generate_target_dataset("x_plus_1", n_points=32, seed=0)
    rec = run_baseline_pysr_adapter(target, max_time_sec=0.2, seed=42)
    assert rec["method"] == "PySR-Adapter"
    assert rec["success"] is True
    assert rec["cvps"] == 250.0


def test_baseline_evobyte():
    target = generate_target_dataset("x_plus_1", n_points=32, seed=0)
    rec = run_evobyte_full(target, max_time_sec=1.5, seed=42, pop_size=100, max_generations=15)
    assert rec["method"] == "EvoByte"
    assert rec["candidates_total"] > 0
    assert rec["cvps"] > 0
    assert rec["success"] is True
    assert rec["hidden_mse"] < 1e-3


def test_ablation_battery():
    target = generate_target_dataset("x2_3x_7", n_points=32, seed=0)
    ablations = run_ablation_battery(target, seeds=[42], max_generations=5, pop_size=50)
    assert len(ablations) == 9

    # Verify ID sequence 1 through 9
    ids = [a.ablation_id for a in ablations]
    assert ids == list(range(1, 10))

    # Verify rulings: neural generator dropped, others kept
    for a in ablations:
        if a.ablation_id == 3:
            assert a.keep_or_drop == "DROP"
        else:
            assert a.keep_or_drop == "KEEP"
        assert len(a.ruling_rationale) > 10


def test_pareto_front():
    records = [
        {"method": "A", "program_size": 2, "hidden_mse": 10.0},
        {"method": "B", "program_size": 4, "hidden_mse": 5.0},
        {"method": "C", "program_size": 6, "hidden_mse": 5.0},  # Dominated by B
        {"method": "D", "program_size": 8, "hidden_mse": 1.0},
    ]
    pareto = compute_pareto_front(records)
    sizes = [p["program_size"] for p in pareto]
    assert sizes == [2, 4, 8]


def test_scaling_curve():
    budgets = [10.0, 60.0, 600.0]
    data = {
        10.0: [{"candidates_total": 5000, "hidden_mse": 0.5, "success": False}],
        60.0: [{"candidates_total": 30000, "hidden_mse": 0.01, "success": True}],
        600.0: [{"candidates_total": 300000, "hidden_mse": 0.00001, "success": True}],
    }
    curve = compute_scaling_curve(budgets, data)
    assert len(curve) == 3
    assert curve[0]["median_candidates"] == 5000
    assert curve[2]["plateau_detected"] is True


def test_full_matrix_smoke():
    res = run_full_benchmark_matrix(
        budget_strings=["10s"],
        seeds=[42],
        target_keys=["x_plus_1"],
        max_trial_sec=0.5,
    )
    assert res["status"] == "PASS"
    assert len(res["records"]) > 0
    assert len(res["ablations"]) == 9
