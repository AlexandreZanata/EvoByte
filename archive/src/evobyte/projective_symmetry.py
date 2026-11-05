"""Projective Linear Group and 2D Affine Symmetry Engine (P212).

Implements:
1. ProjectiveLinearGroup (PGL(2, q)): Action on the projective line P^1(F_q) of size q + 1
   via fractional linear (Möbius) transformations: z -> (az + b) / (cz + d) with ad - bc != 0.
   Cardinality: |PGL(2, q)| = q * (q^2 - 1).
2. AffineGroup2D (AGL(2, q)): Action on the 2D affine plane F_q^2 of size q^2
   via affine maps: v -> M v + t with M in GL(2, q) and t in F_q^2.
   Cardinality: |AGL(2, 4)| = 2880 (or 5760 with Frobenius automorphism).
3. Canonical Orbit Decomposition: Partitions k-element subsets into discrete symmetry orbits,
   enabling large combinatorial search-space compression (> 50x to 600x).

Part of the Bivariate Bicycle & Projective Geometries Program (P211-P220, D047).
"""

from __future__ import annotations

from dataclasses import dataclass
import itertools
from typing import Any, Iterable, Sequence

import numpy as np


def _mod_inv(a: int, m: int) -> int:
    """Return modular inverse of a modulo m."""
    return pow(a % m, -1, m)


# Finite field GF(4) arithmetic tables: elements {0, 1, 2, 3} where 2 is w, 3 is w^2 (w^2 = w + 1)
_GF4_ADD: list[list[int]] = [
    [0, 1, 2, 3],
    [1, 0, 3, 2],
    [2, 3, 0, 1],
    [3, 2, 1, 0],
]

_GF4_MUL: list[list[int]] = [
    [0, 0, 0, 0],
    [0, 1, 2, 3],
    [0, 2, 3, 1],
    [0, 3, 1, 2],
]

_GF4_FROB: list[int] = [0, 1, 3, 2]


class ProjectiveLinearGroup:
    """Projective Linear Group PGL(2, q) acting on P^1(F_q).

    Points of P^1(F_q) are 1-indexed {1, 2, ..., q, q+1}, where q+1 represents infinity.
    Elements are represented by normalized quadruples (a, b, c, d) in F_q with ad - bc != 0 (mod q).
    Normalization: first non-zero entry among a, c is scaled to 1.
    Total order: q * (q^2 - 1).
    """

    def __init__(self, q: int) -> None:
        if q < 2:
            raise ValueError(f"Field order q must be >= 2, got {q}")
        self.q: int = int(q)
        self.points_count: int = self.q + 1
        self.infinity: int = self.q + 1  # 1-indexed

        # Generate all canonical elements of PGL(2, q)
        elements: set[tuple[int, int, int, int]] = set()
        for a in range(self.q):
            for b in range(self.q):
                for c in range(self.q):
                    for d in range(self.q):
                        det = (a * d - b * c) % self.q
                        if det == 0:
                            continue
                        if a != 0:
                            inv_a = _mod_inv(a, self.q)
                            canon = (
                                1,
                                (b * inv_a) % self.q,
                                (c * inv_a) % self.q,
                                (d * inv_a) % self.q,
                            )
                        else:
                            inv_c = _mod_inv(c, self.q)
                            canon = (0, (b * inv_c) % self.q, 1, (d * inv_c) % self.q)
                        elements.add(canon)

        self.elements: list[tuple[int, int, int, int]] = sorted(elements)
        self._order: int = len(self.elements)
        expected_order = self.q * (self.q**2 - 1)
        if self._order != expected_order:
            raise RuntimeError(
                f"Order mismatch for PGL(2, {self.q}): got {self._order}, expected {expected_order}"
            )

        # Precompute action table: shape (order, points_count)
        self._action_table: list[list[int]] = self._build_action_table()

    @property
    def order(self) -> int:
        """Total order of the group PGL(2, q)."""
        return self._order

    def _build_action_table(self) -> list[list[int]]:
        """Precompute action of all group elements on points 1..q+1."""
        table: list[list[int]] = []
        q = self.q
        inf_pt = self.infinity

        for a, b, c, d in self.elements:
            row = [0] * (q + 2)  # 1-indexed, size q+2
            # Point infinity (q + 1)
            if c == 0:
                row[inf_pt] = inf_pt
            else:
                row[inf_pt] = ((a * _mod_inv(c, q)) % q) + 1

            # Affine points 1..q (corresponding to 0..q-1 in F_q)
            for z in range(q):
                pt = z + 1
                denom = (c * z + d) % q
                if denom == 0:
                    row[pt] = inf_pt
                else:
                    numer = (a * z + b) % q
                    row[pt] = ((numer * _mod_inv(denom, q)) % q) + 1

            table.append(row)
        return table

    def action(self, element: tuple[int, int, int, int], point: int) -> int:
        """Apply group element (a, b, c, d) to 1-indexed point in 1..q+1."""
        idx = self.elements.index(element)
        return self._action_table[idx][point]

    def orbit(self, block: Sequence[int]) -> list[tuple[int, ...]]:
        """Return all distinct blocks in the orbit of the given block."""
        unique_blocks: set[tuple[int, ...]] = set()
        for row in self._action_table:
            mapped = tuple(sorted(row[p] for p in block))
            unique_blocks.add(mapped)
        return sorted(unique_blocks)

    def canonical_representative(self, block: Sequence[int]) -> tuple[int, ...]:
        """Return the lexicographically smallest block in the orbit."""
        min_block: tuple[int, ...] | None = None
        for row in self._action_table:
            mapped = tuple(sorted(row[p] for p in block))
            if min_block is None or mapped < min_block:
                min_block = mapped
        assert min_block is not None
        return min_block

    def decompose_subsets(self, k: int) -> list[tuple[tuple[int, ...], int]]:
        """Decompose all (q+1 choose k) subsets into canonical orbits with their sizes."""
        all_subsets = list(itertools.combinations(range(1, self.points_count + 1), k))
        visited: set[tuple[int, ...]] = set()
        orbits: list[tuple[tuple[int, ...], int]] = []

        for sub in all_subsets:
            if sub in visited:
                continue
            orb = set()
            for row in self._action_table:
                img = tuple(sorted(row[x] for x in sub))
                orb.add(img)
            visited.update(orb)
            orbits.append((min(orb), len(orb)))

        return orbits


class AffineGroup2D:
    """2-Dimensional Affine Group AGL(2, q) acting on F_q^2.

    Points are 1-indexed {1, 2, ..., q^2}.
    For q=4, points represent (x, y) in GF(4)^2 indexed as 1 + x*4 + y.
    Total order: |GL(2, 4)| * 16 = 180 * 16 = 2880.
    With Frobenius automorphism: |AGammaL(2, 4)| = 5760.
    """

    def __init__(self, q: int = 4, include_frobenius: bool = True) -> None:
        if q != 4:
            raise NotImplementedError("Currently only q=4 is supported for 2D affine geometry.")
        self.q: int = 4
        self.points_count: int = 16
        self.include_frobenius: bool = include_frobenius

        # 16 points: (x, y) with x, y in GF(4) -> 1-indexed: 1 + x*4 + y
        self.points: list[tuple[int, int]] = [(x, y) for x in range(4) for y in range(4)]

        # Generate GL(2, 4): matrices (a, b, c, d) with det != 0
        gl2: list[tuple[int, int, int, int]] = []
        for a in range(4):
            for b in range(4):
                for c in range(4):
                    for d in range(4):
                        det = _GF4_ADD[_GF4_MUL[a][d]][_GF4_MUL[b][c]]
                        if det != 0:
                            gl2.append((a, b, c, d))
        self.gl2_order: int = len(gl2)  # 180

        # Build action table on points 1..16
        self._action_table: list[list[int]] = []
        frob_ops = [False, True] if include_frobenius else [False]

        for use_frob in frob_ops:
            for a, b, c, d in gl2:
                for t1 in range(4):
                    for t2 in range(4):
                        perm = [0] * 17  # 1-indexed
                        for idx, (px, py) in enumerate(self.points, start=1):
                            # Optional Frobenius automorphism on input coordinates
                            fx = _GF4_FROB[px] if use_frob else px
                            fy = _GF4_FROB[py] if use_frob else py
                            # M * p + t
                            nx = _GF4_ADD[_GF4_ADD[_GF4_MUL[a][fx]][_GF4_MUL[b][fy]]][t1]
                            ny = _GF4_ADD[_GF4_ADD[_GF4_MUL[c][fx]][_GF4_MUL[d][fy]]][t2]
                            perm[idx] = 1 + nx * 4 + ny
                        self._action_table.append(perm)

        self._order: int = len(self._action_table)

    @property
    def order(self) -> int:
        """Total order of the affine group."""
        return self._order

    def orbit(self, block: Sequence[int]) -> list[tuple[int, ...]]:
        """Return all distinct blocks in the orbit of the given block."""
        unique_blocks: set[tuple[int, ...]] = set()
        for row in self._action_table:
            mapped = tuple(sorted(row[p] for p in block))
            unique_blocks.add(mapped)
        return sorted(unique_blocks)

    def canonical_representative(self, block: Sequence[int]) -> tuple[int, ...]:
        """Return the lexicographically smallest block in the orbit."""
        min_block: tuple[int, ...] | None = None
        for row in self._action_table:
            mapped = tuple(sorted(row[p] for p in block))
            if min_block is None or mapped < min_block:
                min_block = mapped
        assert min_block is not None
        return min_block
