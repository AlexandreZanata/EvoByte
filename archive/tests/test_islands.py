"""Unit tests for the island model and ring migration (P10)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from evobyte.islands import (
    P69_MIGRATION_POLICIES,
    P69_SIGNATURE_MODULI,
    IslandModel,
    IslandRunnerConfig,
    get_default_island_configs,
    p69_migrate,
    p69_recombine,
    p69_residual,
    p69_signature,
    p69_signature_distance,
    run_evolution_islands,
)


def test_default_island_configs() -> None:
    configs = get_default_island_configs(pop_per_island=250)
    assert len(configs) == 4
    names = [c.name for c in configs]
    assert names == ["small-size", "high-mutation", "low-mutation", "high-novelty"]

    # Verify distinct pressures
    c_small = configs[0]
    c_high = configs[1]
    c_low = configs[2]
    c_nov = configs[3]

    assert c_small.complexity_weight > c_high.complexity_weight
    assert c_high.point_mut_p > c_low.point_mut_p
    assert c_high.large_mut_p > c_low.large_mut_p
    assert c_low.crossover_p > c_high.crossover_p
    assert c_nov.novelty_weight > 0.0


def test_ring_migration_topology() -> None:
    config = IslandRunnerConfig(n_islands=4, total_pop_size=40, migration_interval=5, migration_k=3)
    rng = np.random.default_rng(123)
    model = IslandModel(config, rng)

    # Tag each island's population distinctly
    for i in range(4):
        model.populations[i][:] = i + 10  # Island 0: 10, Island 1: 11, etc.

    migrations = model.migrate_ring(k=3)
    assert len(migrations) == 4
    # Ring: 0->1, 1->2, 2->3, 3->0
    assert migrations == [(0, 1, 3), (1, 2, 3), (2, 3, 3), (3, 0, 3)]

    # Check that destination received the immigrants
    assert np.all(model.populations[1][-3:] == 10)  # Island 1 got from 0
    assert np.all(model.populations[2][-3:] == 11)  # Island 2 got from 1
    assert np.all(model.populations[3][-3:] == 12)  # Island 3 got from 2
    assert np.all(model.populations[0][-3:] == 13)  # Island 0 got from 3


def test_migration_preserves_determinism_per_seed() -> None:
    xs = np.linspace(-3.0, 3.0, 32, dtype=np.float32)
    ys = xs * xs + 2.0 * xs + 1.0

    config = IslandRunnerConfig(
        n_islands=4,
        total_pop_size=100,  # 25 per island
        migration_interval=3,  # migration triggers at gen 3 and gen 6
        migration_k=2,
        max_generations=6,
    )

    rng1 = np.random.default_rng(888)
    res1 = run_evolution_islands(xs, ys, config, rng1)

    rng2 = np.random.default_rng(888)
    res2 = run_evolution_islands(xs, ys, config, rng2)

    # 1. Best overall program and fitness must match exactly
    assert np.array_equal(res1["best_program"], res2["best_program"])
    assert res1["best_mse"] == pytest.approx(res2["best_mse"])
    assert res1["best_expression"] == res2["best_expression"]

    # 2. All 4 island populations must be bit-identical
    for i in range(4):
        assert np.array_equal(res1["model"].populations[i], res2["model"].populations[i])


def test_islands_checkpoint_hook(tmp_path: Path) -> None:
    from evobyte.archive import load_checkpoint

    xs = np.linspace(-2.0, 2.0, 16, dtype=np.float32)
    ys = xs + 3.0

    ckpt_path = tmp_path / "island_ckpt.pkl"
    config = IslandRunnerConfig(
        n_islands=4,
        total_pop_size=80,
        max_generations=4,
        checkpoint_interval=2,
        checkpoint_path=ckpt_path,
    )
    rng = np.random.default_rng(777)

    run_evolution_islands(xs, ys, config, rng)
    assert ckpt_path.exists()

    loaded = load_checkpoint(ckpt_path)
    assert loaded["generation"] == 4
    assert len(loaded["populations"]) == 4
    for pop in loaded["populations"]:
        assert len(pop) == 20


def _p69_islands():
    return [
        [(2, 3, 6), (2, 3, 7), (5, 5, 5)],
        [(3, 4, 12), (4, 4, 12), (1, 1, 2)],
        [(2, 4, 4), (3, 3, 6), (7, 7, 7)],
        [(3, 18, 18), (2, 2, 3), (9, 9, 9)],
    ]


def test_p69_signature_distance_and_residual() -> None:
    assert P69_SIGNATURE_MODULI == (2, 3, 5)
    assert set(P69_MIGRATION_POLICIES) == {"residue", "elite", "random", "none"}
    assert p69_signature((2, 3, 6)) == p69_signature((2, 3, 6))
    assert p69_signature_distance((0, 1), (0, 1)) == 0
    assert p69_signature_distance((0, 1), (1, 0)) == 2
    assert p69_residual(4, (2, 3, 6)) == 0
    assert p69_residual(4, (2, 3, 7)) == 4


def test_p69_recombine_records_parents_and_domain() -> None:
    first = p69_recombine((2, 3, 7), (5, 5, 5), seed=0)
    assert first == p69_recombine((2, 3, 7), (5, 5, 5), seed=0)
    assert first["rejected"] is False
    assert first["parents"] == [(2, 3, 7), (5, 5, 5)]
    assert first["child"] is not None
    assert min(first["child"]) >= 1
    tiny = p69_recombine((1, 1, 1), (10**9 + 5, 10**9 + 5, 10**9 + 5), seed=0)
    assert tiny["rejected"] is True
    assert tiny["child"] is None
    assert tiny["parents"] == [(1, 1, 1), (10**9 + 5, 10**9 + 5, 10**9 + 5)]


def test_p69_migrate_constant_population_and_ancestry() -> None:
    import pytest

    for policy in ("residue", "elite", "random"):
        rep = p69_migrate(_p69_islands(), 4, policy=policy, seed=0)
        assert [len(isl) for isl in rep["islands"]] == [3, 3, 3, 3]
        assert len(rep["moves"]) == 4
        for move in rep["moves"]:
            assert move["dst"] == (move["src"] + 1) % 4
            assert len(move["parents"]) in (1, 2)
            if move["recombined"]:
                assert len(move["parents"]) == 2
    assert p69_migrate(_p69_islands(), 4, policy="residue", seed=0) == p69_migrate(
        _p69_islands(), 4, policy="residue", seed=0
    )
    same = p69_migrate(_p69_islands(), 4, policy="none", seed=0)
    assert same["islands"] == _p69_islands()
    assert same["moves"] == []
    with pytest.raises(ValueError, match="Unknown P69 migration policy"):
        p69_migrate(_p69_islands(), 4, policy="oracle", seed=0)


def test_p69_elite_picks_best_residual() -> None:
    islands = [[(5, 5, 5), (2, 3, 7), (2, 3, 6)], [(1, 1, 2)]]
    rep = p69_migrate(islands, 4, policy="elite", seed=0)
    assert rep["moves"][0]["emigrant"] == (2, 3, 6)
