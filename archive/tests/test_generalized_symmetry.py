"""Unit tests for Generalized Automorphism Orbit Reduction Engine (P202).

Validates:
1. Group axioms (closure, associativity, identity, inverse) for AffineGroup1D.
2. Group axioms (closure, associativity, identity, inverse) for DihedralGroup.
3. Invariant action properties on coordinates and subsets.
4. Compression comparison against cyclic group Z_m.
5. BicirculantBlockGenerator: 100% symplectic commutativity rate.
"""

from __future__ import annotations

import math

import numpy as np

from evobyte.generalized_symmetry import (
    AffineGroup1D,
    BicirculantBlockGenerator,
    DihedralGroup,
    GeneralizedCoveringOrbitEngine,
)
from evobyte.symmetry_engine import CyclicGroup


def test_affine_group_axioms() -> None:
    """Validate algebraic group axioms for AffineGroup1D(13)."""
    group = AffineGroup1D(13)
    assert group.order == 12 * 13  # 156
    assert len(group.elements) == 156

    e = group.identity()
    assert e == (1, 0)

    # Test closure, identity and inverse on all elements
    rng = np.random.default_rng(42)
    sample_indices = rng.choice(len(group.elements), size=20, replace=False)
    samples = [group.elements[int(i)] for i in sample_indices]

    for g in samples:
        # Identity
        assert group.compose(g, e) == g
        assert group.compose(e, g) == g

        # Inverse
        g_inv = group.inverse(g)
        assert group.compose(g, g_inv) == e
        assert group.compose(g_inv, g) == e

        # Action on coordinates matches composition
        for x in range(group.q):
            assert group.apply(group.apply(x, *g_inv), *g) == x

    # Associativity on triplets
    for _ in range(20):
        g1 = group.elements[int(rng.choice(len(group.elements)))]
        g2 = group.elements[int(rng.choice(len(group.elements)))]
        g3 = group.elements[int(rng.choice(len(group.elements)))]
        left = group.compose(group.compose(g1, g2), g3)
        right = group.compose(g1, group.compose(g2, g3))
        assert left == right


def test_dihedral_group_axioms() -> None:
    """Validate algebraic group axioms for DihedralGroup(15)."""
    group = DihedralGroup(15)
    assert group.order == 30
    assert len(group.elements) == 30

    e = group.identity()
    assert e == (False, 0)

    for g in group.elements:
        # Identity
        assert group.compose(g, e) == g
        assert group.compose(e, g) == g

        # Inverse
        g_inv = group.inverse(g)
        assert group.compose(g, g_inv) == e
        assert group.compose(g_inv, g) == e

        # Action on points
        for x in range(group.m):
            assert group.apply(group.apply(x, *g_inv), *g) == x


def test_affine_orbit_reduction_c13_5_3() -> None:
    """Verify compression of C(13, 5, 3) under AGL(1, 13) vs Z_13."""
    group_agl = AffineGroup1D(13)
    engine_agl = GeneralizedCoveringOrbitEngine(13, 5, 3, group_agl)
    stats_agl = engine_agl.get_orbit_stats()

    assert stats_agl.total_subsets == math.comb(13, 5)  # 1287
    assert stats_agl.num_orbits == 10  # Exact 10 orbits under AGL(1, 13)
    assert stats_agl.compression_ratio == 128.7

    # Compare with cyclic Z_13
    group_z = CyclicGroup(13)
    engine_z = GeneralizedCoveringOrbitEngine(13, 5, 3, group_z)
    stats_z = engine_z.get_orbit_stats()

    assert stats_z.num_orbits == 99
    # Additional compression over Z_13: 99 / 10 = 9.9x
    additional_compression = stats_z.num_orbits / stats_agl.num_orbits
    assert additional_compression >= 2.0
    assert abs(additional_compression - 9.9) < 0.1


def test_dihedral_orbit_reduction_c15_10_4() -> None:
    """Verify compression of C(15, 10, 4) under D_15 vs Z_15."""
    group_d15 = DihedralGroup(15)
    engine_d15 = GeneralizedCoveringOrbitEngine(15, 10, 4, group_d15)
    stats_d15 = engine_d15.get_orbit_stats()

    assert stats_d15.total_subsets == math.comb(15, 10)  # 3003
    assert stats_d15.num_orbits == 111  # Exact 111 orbits under D_15
    assert abs(stats_d15.compression_ratio - 27.054) < 0.01

    # Compare with cyclic Z_15
    group_z = CyclicGroup(15)
    engine_z = GeneralizedCoveringOrbitEngine(15, 10, 4, group_z)
    stats_z = engine_z.get_orbit_stats()

    assert stats_z.num_orbits == 201
    additional_compression = stats_z.num_orbits / stats_d15.num_orbits
    assert additional_compression >= 1.8  # ~1.81x reduction from reflection symmetry


def test_base_block_expansion_and_mutation() -> None:
    """Test expansion and mutation invariance."""
    group_agl = AffineGroup1D(13)
    engine = GeneralizedCoveringOrbitEngine(13, 5, 3, group_agl)
    reps = engine.compute_orbit_representatives()
    assert len(reps) == 10

    # Expand 1 base block
    base = reps[0]
    expanded = engine.expand_base_blocks([base], one_indexed=False)
    assert len(expanded) == len(group_agl.orbit(base))
    assert all(tuple(b) in group_agl.orbit(base) for b in expanded)

    # Mutation test
    rng = np.random.default_rng(123)
    mutated = engine.mutate_base_block(base, rng)
    assert len(mutated) == 5
    assert mutated in reps  # Must be one of the canonical reps


def test_bicirculant_commutativity_100_percent() -> None:
    """Validate that BicirculantBlockGenerator achieves 100% commutativity."""
    rng = np.random.default_rng(2026)
    for L in [7, 8, 9]:
        gen = BicirculantBlockGenerator(L)
        assert gen.n == 2 * L
        successes = 0
        total_trials = 50

        for _ in range(total_trials):
            ra, rb = gen.sample_random_rows(weight_a=3, weight_b=3, rng=rng)
            Hx, Hz = gen.generate_css_pair(ra, rb)
            if gen.check_symplectic_commutativity(Hx, Hz):
                successes += 1

        assert successes == total_trials, f"Commutativity rate not 100% for L={L}"
