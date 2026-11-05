"""Unit tests for small bivariate bicycle code exhaustive census (P222).

Calibration tests (a)-(e) mandated by P222:
(a) [[20, 2, 6]] => (2, 6)
(b) [[16, 2, 4]] => (2, 4)
(c) For l=5, m=2 the enumeration space has exactly 39,600 pairs
(d) Symplectic commutativity H_X H_Z^T = 0 on 200 random pairs (seed 42)
(e) Landmark Bravyi [[72, 12, 6]] code has k=12 (rank-only check)
"""

from __future__ import annotations

import random
from evobyte.bb_census import (
    basis_of,
    checks,
    enumerate_space,
    exact_distance,
)


def test_calibration_code_20_2_6() -> None:
    """Test (a): [[20, 2, 6]] yields (k=2, d=6)."""
    l, m = 5, 2
    A = [(0, 0), (0, 1), (1, 1), (2, 1)]
    B = [(0, 1), (1, 1), (2, 0), (2, 1)]
    hx, hz = checks(l, m, A, B)
    k, d = exact_distance(hx, hz, 2 * l * m, wmax=7)
    assert k == 2, f"Expected k=2, got {k}"
    assert d == 6, f"Expected d=6, got {d}"


def test_calibration_code_16_2_4() -> None:
    """Test (b): [[16, 2, 4]] yields (k=2, d=4)."""
    l, m = 2, 4
    A = [(0, 0), (0, 2), (1, 0), (1, 3)]
    B = [(0, 1), (1, 0), (1, 2), (1, 3)]
    hx, hz = checks(l, m, A, B)
    k, d = exact_distance(hx, hz, 2 * l * m, wmax=7)
    assert k == 2, f"Expected k=2, got {k}"
    assert d == 4, f"Expected d=4, got {d}"


def test_enumeration_space_size() -> None:
    """Test (c): for l=5, m=2 the enumeration space has exactly 39,600 pairs."""
    pairs = enumerate_space(5, 2)
    assert len(pairs) == 39600, f"Expected 39,600 pairs, got {len(pairs)}"


def test_symplectic_commutativity_200_pairs() -> None:
    """Test (d): symplectic commutativity H_X H_Z^T = 0 mod 2 on 200 random pairs."""
    rng = random.Random(42)

    def par(x: int) -> int:
        return bin(x).count("1") & 1

    for _ in range(200):
        l = rng.randint(2, 6)
        m = rng.randint(l, 6)
        pts = [(i, j) for i in range(l) for j in range(m)]
        a_size = rng.choice([3, 4])
        b_size = rng.choice([3, 4])
        A = rng.sample(pts, a_size)
        B = rng.sample(pts, b_size)
        hx, hz = checks(l, m, A, B)
        for x in hx:
            for z in hz:
                assert par(x & z) == 0, f"Commutativity failed for l={l}, m={m}"


def test_bravyi_code_rank() -> None:
    """Test (e): Bravyi [[72, 12, 6]] code has k=12 (rank-only check, no distance)."""
    l, m = 6, 6
    A = {(3, 0), (0, 1), (0, 2)}
    B = {(0, 3), (1, 0), (2, 0)}
    hx, hz = checks(l, m, A, B)
    bx, bz = basis_of(hx), basis_of(hz)
    n = 2 * l * m
    k = n - len(bx) - len(bz)
    assert len(bx) == 30, f"Expected rx=30, got {len(bx)}"
    assert len(bz) == 30, f"Expected rz=30, got {len(bz)}"
    assert k == 12, f"Expected k=12, got {k}"
