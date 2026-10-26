"""Unit and property tests for Algebraic Symmetry and Orbit Reduction Engine (P192).

Validates:
1. Formal group action axioms of Z_m and orbit invariance.
2. Covering design orbit partitioning, base block expansion, and difference multisets.
3. Circulant matrix commutativity over GF(2).
4. Symplectic commutativity preservation rate >= 90% for QECC candidates.
5. Parameter compression factor >= 4x for all narrow-gap frontier targets.
6. Non-degeneracy (full rank, no zero-weight or duplicate rows).
7. Factory and benchmark integration with P191 narrow-gap catalogue.
"""

from __future__ import annotations

import math
import time

import numpy as np
import pytest

from evobyte.symmetry_engine import (
    CoveringOrbitEngine,
    CyclicGroup,
    QuasiCyclicStabilizerEngine,
    benchmark_all_p191_symmetry_reductions,
    circulant_matrix,
    cyclic_convolution,
    get_symmetry_engine_for_target,
    gf2_rank,
)


def test_cyclic_group_axioms() -> None:
    """Validate Z_m group action axioms and orbit properties."""
    g = CyclicGroup(order=13)

    # 1. Identity action: shift = 0
    assert g.apply(5, shift=0) == 5
    assert g.apply_to_subset((1, 4, 7), shift=0) == (1, 4, 7)

    # 2. Additivity of shifts: (x + a) + b = x + (a + b) mod m
    assert g.apply(g.apply(4, shift=5), shift=9) == g.apply(4, shift=14)

    # 3. Canonical representative is an invariant orbit label
    block = (2, 5, 9)
    rep = g.canonical_representative(block)
    for s in range(13):
        shifted = g.apply_to_subset(block, shift=s)
        assert g.canonical_representative(shifted) == rep

    # 4. Error on non-positive order
    with pytest.raises(ValueError):
        CyclicGroup(order=0)


def test_covering_orbit_engine_partition() -> None:
    """Validate that orbits partition combinations(range(v), k) into disjoint sets."""
    engine = CoveringOrbitEngine(v=7, k=3, t=2)
    reps = engine.compute_orbit_representatives()
    stats = engine.get_orbit_stats()

    # Total blocks C(7,3) = 35
    assert stats.total_blocks == 35
    # For v=7 (prime), orbits have size 7, so 35 / 7 = 5 orbits
    assert stats.num_orbits == 5
    assert stats.compression_ratio == 7.0

    # Every subset must belong to exactly one orbit
    all_reconstructed: set[tuple[int, ...]] = set()
    for rep in reps:
        orbit = engine.group.orbit(rep)
        for b in orbit:
            assert b not in all_reconstructed, f"Duplicate block {b} across orbits"
            all_reconstructed.add(b)

    assert len(all_reconstructed) == 35


def test_covering_compression_ratios() -> None:
    """Gate 2: Compression factor must exceed 4x for all P191 covering targets."""
    # Target 1: C(13, 6, 3)
    e13 = CoveringOrbitEngine(v=13, k=6, t=3)
    stats13 = e13.get_orbit_stats()
    assert stats13.compression_ratio >= 13.0
    assert stats13.compression_ratio >= 4.0
    assert stats13.num_orbits == 132
    assert stats13.total_blocks == 1716

    # Target 2: C(14, 6, 3)
    e14 = CoveringOrbitEngine(v=14, k=6, t=3)
    stats14 = e14.get_orbit_stats()
    assert stats14.compression_ratio >= 13.8
    assert stats14.compression_ratio >= 4.0
    assert stats14.num_orbits == 217
    assert stats14.total_blocks == 3003

    # Target 3: C(15, 8, 4)
    e15 = CoveringOrbitEngine(v=15, k=8, t=4)
    stats15 = e15.get_orbit_stats()
    assert stats15.compression_ratio >= 15.0
    assert stats15.compression_ratio >= 4.0
    assert stats15.num_orbits == 429
    assert stats15.total_blocks == 6435


def test_covering_orbit_invariance_and_expansion() -> None:
    """Validate that expanding base blocks produces a cyclically invariant design."""
    engine = CoveringOrbitEngine(v=13, k=6, t=3)
    reps = engine.compute_orbit_representatives()

    # Expand 2 base blocks
    base_blocks = reps[:2]
    expanded_1idx = engine.expand_base_blocks(base_blocks, one_indexed=True)
    expanded_0idx = engine.expand_base_blocks(base_blocks, one_indexed=False)

    assert len(expanded_1idx) == 26
    assert len(expanded_0idx) == 26

    # Invariance check under Z_13 shift
    assert engine.group.is_invariant(expanded_0idx, shift=1)
    assert engine.group.is_invariant(expanded_0idx, shift=5)

    # Difference multiset computation
    sig = engine.difference_signature(base_blocks[0])
    assert len(sig) > 0
    # Sum of differences in block of size k is k*(k-1) = 6*5 = 30
    assert sum(sig.values()) == 30


def test_covering_base_block_mutation() -> None:
    """Validate mutation of base blocks preserves canonical orbit representative format."""
    engine = CoveringOrbitEngine(v=13, k=6, t=3)
    reps = engine.compute_orbit_representatives()
    rng = np.random.default_rng(123)

    initial_base = reps[0]
    mutated = engine.mutate_base_block(initial_base, rng)

    assert len(mutated) == 6
    assert all(0 <= x < 13 for x in mutated)
    assert mutated in reps  # Must belong to the frozen set of orbit representatives


def test_circulant_matrix_algebraic_properties() -> None:
    """Validate that circulant matrices commute and preserve cyclic convolution over GF(2)."""
    L = 7
    v1 = np.array([1, 0, 1, 1, 0, 0, 0], dtype=np.uint8)
    v2 = np.array([0, 1, 1, 0, 1, 0, 0], dtype=np.uint8)

    C1 = circulant_matrix(v1)
    C2 = circulant_matrix(v2)

    # 1. Fundamental theorem of circulant matrices: C1 @ C2 == C2 @ C1
    prod1 = (C1 @ C2) % 2
    prod2 = (C2 @ C1) % 2
    assert np.array_equal(prod1, prod2)

    # 2. First row of product is cyclic convolution of v1 and v2
    conv = cyclic_convolution(v1, v2)
    assert np.array_equal(prod1[0], conv)


def test_quasi_cyclic_commutativity_rate() -> None:
    """Gate 2 & Falsifiable Question: Commutativity rate must be >= 90%."""
    # Test on n=14, k=3, m=11 (L=7, c=2)
    engine_14 = QuasiCyclicStabilizerEngine(n=14, k=3, block_size=7)
    stats_14 = engine_14.measure_commutativity_preservation(n_samples=200)

    assert stats_14["commutativity_rate_pct"] >= 90.0
    assert stats_14["non_degenerate_rate_pct"] >= 90.0

    # Test on n=16, k=5, m=11 (L=8, c=2)
    engine_16 = QuasiCyclicStabilizerEngine(n=16, k=5, block_size=8)
    stats_16 = engine_16.measure_commutativity_preservation(n_samples=200)

    assert stats_16["commutativity_rate_pct"] >= 90.0
    assert stats_16["non_degenerate_rate_pct"] >= 90.0


def test_quasi_cyclic_parameter_compression() -> None:
    """Gate 2 & Falsifiable Question: Parameter compression must be >= 4x."""
    engine_14 = QuasiCyclicStabilizerEngine(n=14, k=3, block_size=7)
    comp_14 = engine_14.parameter_compression_factor()
    assert comp_14 >= 4.0
    # Full: 11 * 28 = 308; Seed: 28; Ratio = 11.0x
    assert math.isclose(comp_14, 11.0, rel_tol=1e-3)

    engine_16 = QuasiCyclicStabilizerEngine(n=16, k=5, block_size=8)
    comp_16 = engine_16.parameter_compression_factor()
    assert comp_16 >= 4.0
    # Full: 11 * 32 = 352; Seed: 32; Ratio = 11.0x
    assert math.isclose(comp_16, 11.0, rel_tol=1e-3)


def test_non_degenerate_candidates() -> None:
    """Ensure generated stabilizer candidates are non-degenerate."""
    engine = QuasiCyclicStabilizerEngine(n=14, k=3, block_size=7)
    rng = np.random.default_rng(42)

    for _ in range(20):
        ok, cand = engine.generate_circulant_css_candidate(rng)
        assert ok is True
        assert cand.shape == (11, 28)

        # 1. Full rank m = 11
        assert gf2_rank(cand) == 11

        # 2. No zero-weight rows
        weights = np.sum(cand, axis=1)
        assert np.all(weights >= 2), f"Found row with weight < 2: {weights}"

        # 3. No duplicate rows
        unique_rows = {tuple(row) for row in cand}
        assert len(unique_rows) == 11


def test_target_factory_and_benchmark() -> None:
    """Integration test with narrow-gap catalogue targets."""
    # Test factory for each P191 target
    targets = [
        "covering_C_13_6_3",
        "covering_C_14_6_3",
        "covering_C_15_8_4",
        "qecc_14_3_open",
        "qecc_16_5_open",
    ]
    for tid in targets:
        engine = get_symmetry_engine_for_target(tid)
        assert engine is not None

    with pytest.raises(KeyError):
        get_symmetry_engine_for_target("unknown_target_xyz")

    # Run comprehensive benchmark across all 5 targets
    t0 = time.perf_counter()
    bench = benchmark_all_p191_symmetry_reductions()
    dt = time.perf_counter() - t0

    assert len(bench) == 5
    for tid, res in bench.items():
        assert res["target_threshold_met"] is True
        assert res["compression_factor"] >= 4.0

    assert dt < 1.0, f"Benchmark took {dt:.3f}s >= 1.0s"
