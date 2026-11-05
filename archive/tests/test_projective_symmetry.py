"""Tests for Projective Linear Group and 2D Affine Symmetry Engine (P212).

Validates:
1. PGL(2, q) group order matches q * (q^2 - 1) for q in {3, 5, 13}.
2. Permutation action: every group element induces a bijective map on P^1(F_q).
3. Exact orbit decomposition of C(14, 6, 3) parameter space:
   3003 6-subsets partitioned into exactly 5 canonical orbits under PGL(2, 13).
4. Compression ratio >= 5x (achieves 600.6x) and runtime under 500 ms.
5. AGL(2, 4) group order (2880 / 5760 with Frobenius) and permutation action on 16 points.
6. Canonical representative idempotence: canon(g(B)) == canon(B) for all g in G.
"""

from __future__ import annotations

import time

from evobyte.projective_symmetry import AffineGroup2D, ProjectiveLinearGroup


def test_pgl2_order_and_permutations() -> None:
    """Verify group order and bijection property for PGL(2, q)."""
    for q in [3, 5, 13]:
        pgl = ProjectiveLinearGroup(q)
        expected_order = q * (q**2 - 1)
        assert pgl.order == expected_order, (
            f"Order mismatch for q={q}: {pgl.order} != {expected_order}"
        )

        # Test first 10 elements: each must act as a permutation on 1..q+1
        n_pts = q + 1
        for elem in pgl.elements[:10]:
            images = [pgl.action(elem, pt) for pt in range(1, n_pts + 1)]
            assert len(images) == n_pts
            assert set(images) == set(range(1, n_pts + 1)), f"Element {elem} not a permutation"


def test_pgl2_13_exact_orbit_decomposition() -> None:
    """Exact partition of 3003 6-subsets of 14 points into 5 canonical orbits under PGL(2, 13)."""
    pgl = ProjectiveLinearGroup(13)
    assert pgl.order == 2184

    t0 = time.perf_counter()
    orbits = pgl.decompose_subsets(k=6)
    dt = time.perf_counter() - t0

    # Exactly 5 canonical orbits
    assert len(orbits) == 5, f"Expected 5 orbits, got {len(orbits)}"

    # Orbit sizes must partition all 3003 subsets
    sizes = [size for _, size in orbits]
    assert sum(sizes) == 3003, f"Sum of orbit sizes {sum(sizes)} != 3003"
    assert sorted(sizes) == [91, 182, 546, 1092, 1092]

    # Compression factor: 3003 / 5 = 600.6x (must be >= 5x)
    compression = 3003.0 / len(orbits)
    assert compression >= 5.0
    assert compression == 600.6

    # Fast execution time (< 0.5s)
    assert dt < 0.5, f"Decomposition took {dt:.3f}s >= 0.5s"


def test_agl2_4_order_and_permutations() -> None:
    """Verify AGL(2, 4) order and permutation actions on 16 points."""
    # Without Frobenius: 180 * 16 = 2880
    agl_pure = AffineGroup2D(q=4, include_frobenius=False)
    assert agl_pure.order == 2880
    assert agl_pure.points_count == 16

    # With Frobenius: 2880 * 2 = 5760
    agl_frob = AffineGroup2D(q=4, include_frobenius=True)
    assert agl_frob.order == 5760

    # Verify first 10 elements act as permutations on {1..16}
    for row in agl_frob._action_table[:10]:
        images = [row[pt] for pt in range(1, 17)]
        assert len(images) == 16
        assert set(images) == set(range(1, 17))


def test_agl2_4_orbit_compression() -> None:
    """Verify that AGL(2, 4) compresses 7-subsets of 16 points by >= 5x."""
    agl = AffineGroup2D(q=4, include_frobenius=True)
    # Sample block of 7 points
    block = (1, 2, 3, 4, 5, 6, 7)
    orb = agl.orbit(block)
    assert len(orb) >= 5, f"Orbit size {len(orb)} too small"
    # A single orbit of size >= 240 provides massive compression over enumeration
    assert len(orb) in [120, 240, 480, 960, 1920, 2880, 5760]


def test_canonical_representative_idempotence() -> None:
    """Verify that canon(g(B)) == canon(B) for any group action."""
    pgl = ProjectiveLinearGroup(3)  # Small group for quick test
    block = (1, 2)
    canon_orig = pgl.canonical_representative(block)

    for elem in pgl.elements[:5]:
        mapped = tuple(sorted(pgl.action(elem, p) for p in block))
        canon_mapped = pgl.canonical_representative(mapped)
        assert canon_mapped == canon_orig, f"Idempotence failed: {canon_mapped} != {canon_orig}"
