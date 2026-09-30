"""Unit tests for Quality Diversity (MAP-Elites and Novelty Search, P09)."""

from __future__ import annotations

import numpy as np
import pytest

from evobyte.bytecode import N_INSTR, encode_instr
from evobyte.diversity import (
    MapElitesGrid,
    NoveltyArchive,
    QDConfig,
    classify_family,
    compute_behavior_descriptor,
    compute_trend_feature,
    run_evolution_qd,
)


def test_classify_family() -> None:
    # 1. Polynomial
    p_poly = np.zeros(N_INSTR, dtype=np.uint32)
    p_poly[0] = encode_instr(0x01, 7, 0, 1)  # ADD
    p_poly[1] = encode_instr(0x03, 7, 0, 0)  # MUL
    assert classify_family(p_poly) == "polynomial"

    # 2. Trig
    p_trig = np.zeros(N_INSTR, dtype=np.uint32)
    p_trig[0] = encode_instr(0x05, 7, 0, 0)  # SIN
    assert classify_family(p_trig) == "trig"

    # 3. Exp / Log
    p_exp = np.zeros(N_INSTR, dtype=np.uint32)
    p_exp[0] = encode_instr(0x07, 7, 0, 0)  # EXP
    assert classify_family(p_exp) == "exp_log"

    # 4. Power / Root
    p_pow = np.zeros(N_INSTR, dtype=np.uint32)
    p_pow[0] = encode_instr(0x09, 7, 0, 1)  # POW
    assert classify_family(p_pow) == "power_root"

    # 5. Piecewise
    p_piece = np.zeros(N_INSTR, dtype=np.uint32)
    p_piece[0] = encode_instr(0x0A, 7, 0, 0)  # ABS
    assert classify_family(p_piece) == "piecewise"


def test_compute_behavior_descriptor() -> None:
    # Constant vector -> zeros
    c_vec = np.ones(32, dtype=np.float32) * 5.0
    desc_c = compute_behavior_descriptor(c_vec)
    assert np.all(desc_c == 0.0)

    # Linear vector -> mean 0, std 1
    lin_vec = np.linspace(-10.0, 10.0, 64, dtype=np.float32)
    desc_lin = compute_behavior_descriptor(lin_vec)
    assert desc_lin.shape == (64,)
    assert float(np.mean(desc_lin)) == pytest.approx(0.0, abs=1e-5)
    assert float(np.std(desc_lin)) == pytest.approx(1.0, abs=1e-2)

    # 2D batch
    batch = np.stack([lin_vec, lin_vec * 2.0])
    desc_batch = compute_behavior_descriptor(batch)
    assert desc_batch.shape == (2, 64)


def test_compute_trend_feature() -> None:
    xs = np.linspace(-5.0, 5.0, 50, dtype=np.float32)

    # Perfect positive correlation
    r_pos = compute_trend_feature(xs, xs * 3.0 + 1.0)
    assert r_pos == pytest.approx(1.0, abs=1e-4)

    # Perfect negative correlation
    r_neg = compute_trend_feature(xs, -xs * 2.0)
    assert r_neg == pytest.approx(-1.0, abs=1e-4)

    # Constant
    r_zero = compute_trend_feature(xs, np.zeros_like(xs))
    assert r_zero == pytest.approx(0.0, abs=1e-4)


def test_map_elites_grid() -> None:
    grid = MapElitesGrid(size_bins=16, behavior_bins=10)
    assert grid.coverage() == 0.0
    assert grid.occupied_count() == 0

    xs = np.linspace(-5.0, 5.0, 32, dtype=np.float32)
    preds1 = xs * 2.0
    desc1 = compute_behavior_descriptor(preds1)

    prog1 = np.zeros(N_INSTR, dtype=np.uint32)
    prog1[0] = encode_instr(0x01, 7, 0, 1)  # size 1

    # Add first elite
    added = grid.add(prog1, fitness=1.5, descriptor=desc1, xs=xs, preds=preds1)
    assert added is True
    assert grid.occupied_count() == 1
    assert grid.coverage() == pytest.approx(1.0 / 160.0)

    # Add worse candidate in same cell
    added_worse = grid.add(prog1, fitness=2.5, descriptor=desc1, xs=xs, preds=preds1)
    assert added_worse is False
    assert grid.occupied_count() == 1

    # Add better candidate in same cell
    added_better = grid.add(prog1, fitness=0.5, descriptor=desc1, xs=xs, preds=preds1)
    assert added_better is True
    assert grid.occupied_count() == 1
    assert grid.get_elites()[0]["fitness"] == pytest.approx(0.5)

    # Add candidate with different size and behavior
    prog2 = np.zeros(N_INSTR, dtype=np.uint32)
    prog2[0] = encode_instr(0x05, 1, 0, 0)  # SIN
    prog2[1] = encode_instr(0x01, 7, 1, 0)  # size 2
    preds2 = -xs * 5.0
    desc2 = compute_behavior_descriptor(preds2)

    added2 = grid.add(prog2, fitness=0.8, descriptor=desc2, xs=xs, preds=preds2)
    assert added2 is True
    assert grid.occupied_count() == 2
    assert "polynomial" in grid.get_unique_families()
    assert "trig" in grid.get_unique_families()


def test_novelty_archive_vectorized() -> None:
    arch = NoveltyArchive(max_size=50)
    for _ in range(20):
        arch.add(np.random.randn(32).astype(np.float32))

    pop_descs = np.random.randn(10, 32).astype(np.float32)
    scores = arch.compute_novelty_scores(pop_descs, k=5)
    assert scores.shape == (10,)
    assert np.all(scores >= 0.0)


def test_coverage_grows_and_elites_span_at_least_3_families() -> None:
    xs = np.linspace(-3.0, 3.0, 32, dtype=np.float32)
    ys = xs * xs + 2.0 * xs + 1.0

    config = QDConfig(
        pop_size=100,
        elite_k=16,
        max_generations=15,
        novelty_weight=0.05,
        map_elites_size_bins=16,
        map_elites_behav_bins=10,
    )
    rng = np.random.default_rng(42)

    coverages = []

    def on_gen(stats: dict) -> None:
        coverages.append(stats["grid_coverage"])

    res = run_evolution_qd(xs, ys, config, rng, on_generation=on_gen)

    # 1. Assert coverage grows
    assert len(coverages) >= 2
    assert coverages[-1] >= coverages[0]
    assert res["grid_coverage"] > 0.05  # > 5% of cells filled

    # 2. Assert elites span >= 3 distinct families
    families = res["unique_families"]
    assert len(families) >= 3, f"Expected >= 3 families, got {families}"
