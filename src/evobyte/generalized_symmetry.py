"""Generalized Automorphism Orbit Reduction Engine (P202).

Implements non-cyclic and higher-order algebraic group actions:
1. 1-Dimensional Affine Group AGL(1, q): x -> (ax + b) mod q with gcd(a, q) = 1.
2. Dihedral Group D_m: Rotations and reflections acting on m vertices.
3. Generalized Covering Orbit Engine: Computes canonical orbit representatives,
   sub-orbit partitioning, and compression statistics.
4. Quasi-Cyclic Bicirculant Generator: Generates coupled 2-block stabilizer
   matrices breaking pure circulant symmetry while preserving symplectic orthogonality.

Part of the Generalized Symmetries & Non-Circulant Quantum Codes Program (P201-P210, D045).
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
import math
from typing import Any, Protocol, Sequence

import numpy as np

from evobyte.symmetry_engine import circulant_matrix


def _extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    """Extended Euclidean algorithm: returns (gcd, x, y) such that a*x + b*y = gcd."""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = _extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y


def _mod_inverse(a: int, m: int) -> int:
    """Modular inverse of a modulo m."""
    gcd, x, _ = _extended_gcd(a % m, m)
    if gcd != 1:
        raise ValueError(f"No modular inverse for {a} modulo {m}")
    return (x % m + m) % m


class GroupAction(Protocol):
    """Protocol for algebraic group actions on discrete coordinate sets."""

    @property
    def order(self) -> int: ...

    def orbit(self, block: Sequence[int]) -> list[tuple[int, ...]]: ...

    def canonical_representative(self, block: Sequence[int]) -> tuple[int, ...]: ...


class AffineGroup1D:
    """1-Dimensional Affine Group AGL(1, q) acting on Z_q.

    Elements are pairs (a, b) where a in Z_q*, gcd(a, q) = 1, and b in Z_q.
    Action on x: g(x) = (a*x + b) mod q.
    Composition: (a1, b1) * (a2, b2) = ((a1*a2) mod q, (a1*b2 + b1) mod q).
    """

    def __init__(self, q: int) -> None:
        if q <= 1:
            raise ValueError(f"Affine group modulus must be > 1, got {q}")
        self.q: int = int(q)
        # Compute units in Z_q
        self.units: list[int] = [a for a in range(1, self.q) if math.gcd(a, self.q) == 1]
        self.elements: list[tuple[int, int]] = [(a, b) for a in self.units for b in range(self.q)]
        self._order: int = len(self.elements)

    @property
    def order(self) -> int:
        """Total order of the affine group: phi(q) * q."""
        return self._order

    def identity(self) -> tuple[int, int]:
        """Return the group identity element (1, 0)."""
        return (1, 0)

    def compose(self, g1: tuple[int, int], g2: tuple[int, int]) -> tuple[int, int]:
        """Group multiplication: g1 * g2."""
        a1, b1 = g1
        a2, b2 = g2
        return ((a1 * a2) % self.q, (a1 * b2 + b1) % self.q)

    def inverse(self, g: tuple[int, int]) -> tuple[int, int]:
        """Group inverse: (a, b)^(-1) = (a^(-1), -a^(-1)*b)."""
        a, b = g
        a_inv = _mod_inverse(a, self.q)
        b_inv = (-a_inv * b) % self.q
        return (a_inv, b_inv)

    def apply(self, x: int, a: int = 1, b: int = 0) -> int:
        """Apply affine transformation: (a*x + b) mod q."""
        return (a * x + b) % self.q

    def apply_to_subset(self, block: Sequence[int], a: int = 1, b: int = 0) -> tuple[int, ...]:
        """Apply affine transformation to all elements of a subset and sort."""
        return tuple(sorted((a * x + b) % self.q for x in block))

    def orbit(self, block: Sequence[int]) -> list[tuple[int, ...]]:
        """Compute the full orbit of a subset under AGL(1, q)."""
        unique: set[tuple[int, ...]] = set()
        orbit_list: list[tuple[int, ...]] = []
        for a, b in self.elements:
            img = self.apply_to_subset(block, a=a, b=b)
            if img not in unique:
                unique.add(img)
                orbit_list.append(img)
        return orbit_list

    def canonical_representative(self, block: Sequence[int]) -> tuple[int, ...]:
        """Return the lexicographically smallest subset in the affine orbit."""
        return min(self.apply_to_subset(block, a=a, b=b) for a, b in self.elements)


class DihedralGroup:
    """Dihedral Group D_m of symmetries of a regular m-gon acting on Z_m.

    Elements are pairs (reflection: bool, shift: int), where:
    - If reflection is False: rotation x -> (x + shift) mod m
    - If reflection is True: reflection x -> (-x + shift) mod m
    Order: 2m.
    """

    def __init__(self, m: int) -> None:
        if m < 3:
            raise ValueError(f"Dihedral group m must be >= 3, got {m}")
        self.m: int = int(m)
        self.elements: list[tuple[bool, int]] = [
            (refl, s) for refl in (False, True) for s in range(self.m)
        ]
        self._order: int = 2 * self.m

    @property
    def order(self) -> int:
        """Total order of D_m: 2m."""
        return self._order

    def identity(self) -> tuple[bool, int]:
        """Return the identity element (False, 0)."""
        return (False, 0)

    def compose(self, g1: tuple[bool, int], g2: tuple[bool, int]) -> tuple[bool, int]:
        """Group composition of two dihedral operations."""
        r1, s1 = g1
        r2, s2 = g2
        # If r1 is True, reflection negates the following shift:
        # r1(r2(x + s2) + s1)
        r_new = r1 ^ r2
        if not r1:
            s_new = (s1 + s2) % self.m
        else:
            s_new = (s1 - s2) % self.m
        return (r_new, s_new)

    def inverse(self, g: tuple[bool, int]) -> tuple[bool, int]:
        """Inverse element in D_m."""
        r, s = g
        if not r:
            return (False, (-s) % self.m)
        # Reflection is self-inverse: (s, s) * (s, s) = identity
        return (True, s)

    def apply(self, x: int, reflection: bool = False, shift: int = 0) -> int:
        """Apply dihedral operation to a point x in Z_m."""
        if not reflection:
            return (x + shift) % self.m
        return (-x + shift) % self.m

    def apply_to_subset(
        self, block: Sequence[int], reflection: bool = False, shift: int = 0
    ) -> tuple[int, ...]:
        """Apply dihedral operation to all points of a subset and sort."""
        if not reflection:
            return tuple(sorted((x + shift) % self.m for x in block))
        return tuple(sorted((-x + shift) % self.m for x in block))

    def orbit(self, block: Sequence[int]) -> list[tuple[int, ...]]:
        """Compute the full orbit under D_m."""
        unique: set[tuple[int, ...]] = set()
        orbit_list: list[tuple[int, ...]] = []
        for refl, s in self.elements:
            img = self.apply_to_subset(block, reflection=refl, shift=s)
            if img not in unique:
                unique.add(img)
                orbit_list.append(img)
        return orbit_list

    def canonical_representative(self, block: Sequence[int]) -> tuple[int, ...]:
        """Return lexicographically smallest subset in D_m orbit."""
        return min(
            self.apply_to_subset(block, reflection=refl, shift=s) for refl, s in self.elements
        )


@dataclass(frozen=True)
class GeneralizedOrbitStats:
    """Exact reduction statistics for generalized automorphism actions."""

    v: int
    k: int
    t: int
    group_name: str
    group_order: int
    total_subsets: int
    num_orbits: int
    compression_ratio: float
    max_orbit_size: int
    min_orbit_size: int


class GeneralizedCoveringOrbitEngine:
    """Generic orbit reduction engine for covering designs under arbitrary groups."""

    def __init__(self, v: int, k: int, t: int, group: GroupAction) -> None:
        if not (1 <= t <= k <= v):
            raise ValueError(f"Invalid covering parameters: 1 <= t ({t}) <= k ({k}) <= v ({v})")
        self.v: int = v
        self.k: int = k
        self.t: int = t
        self.group: GroupAction = group
        self._orbit_representatives: list[tuple[int, ...]] | None = None

    def compute_orbit_representatives(self) -> list[tuple[int, ...]]:
        """Compute all canonical orbit representatives for k-subsets."""
        if self._orbit_representatives is not None:
            return list(self._orbit_representatives)

        seen: set[tuple[int, ...]] = set()
        representatives: list[tuple[int, ...]] = []
        for subset in combinations(range(self.v), self.k):
            rep = self.group.canonical_representative(subset)
            if rep not in seen:
                seen.add(rep)
                representatives.append(rep)

        self._orbit_representatives = representatives
        return list(representatives)

    def get_orbit_stats(self) -> GeneralizedOrbitStats:
        """Compute exact reduction metrics and compression factors."""
        reps = self.compute_orbit_representatives()
        total = math.comb(self.v, self.k)
        num_orbits = len(reps)
        compression = total / num_orbits if num_orbits > 0 else 1.0

        sizes = [len(self.group.orbit(r)) for r in reps]
        group_name = type(self.group).__name__
        return GeneralizedOrbitStats(
            v=self.v,
            k=self.k,
            t=self.t,
            group_name=group_name,
            group_order=self.group.order,
            total_subsets=total,
            num_orbits=num_orbits,
            compression_ratio=compression,
            max_orbit_size=max(sizes) if sizes else 0,
            min_orbit_size=min(sizes) if sizes else 0,
        )

    def expand_base_blocks(
        self, base_blocks: Sequence[Sequence[int]], one_indexed: bool = True
    ) -> list[list[int]]:
        """Expand base blocks into full collection of blocks under the group."""
        expanded: set[tuple[int, ...]] = set()
        for base in base_blocks:
            for transformed in self.group.orbit(base):
                expanded.add(transformed)

        sorted_blocks = sorted(list(b) for b in expanded)
        if one_indexed:
            return [[x + 1 for x in b] for b in sorted_blocks]
        return sorted_blocks

    def sample_base_blocks(
        self, num_base_blocks: int, rng: np.random.Generator
    ) -> list[tuple[int, ...]]:
        """Uniformly sample base blocks from canonical representatives."""
        reps = self.compute_orbit_representatives()
        indices = rng.choice(
            len(reps),
            size=min(num_base_blocks, len(reps)),
            replace=False,
        )
        return [reps[int(i)] for i in indices]

    def mutate_base_block(
        self, base_block: Sequence[int], rng: np.random.Generator
    ) -> tuple[int, ...]:
        """Mutate a base block by single element swap and return canonical rep."""
        elements = set(base_block)
        available = [x for x in range(self.v) if x not in elements]
        if not available:
            return tuple(sorted(base_block))

        remove_elem = rng.choice(list(elements))
        add_elem = rng.choice(available)
        new_set = (elements - {remove_elem}) | {add_elem}
        return self.group.canonical_representative(list(new_set))


class BicirculantBlockGenerator:
    """Generator of quasi-cyclic bicirculant stabilizer codes.

    Constructs 2-block parity matrices:
    H_X = (A | B), H_Z = (B^T | A^T)
    where A and B are circulant matrices of size L x L (total qubits n = 2L).
    Since A and B are circulant, they commute under matrix multiplication (A * B = B * A).
    Hence:
    H_X * H_Z^T = A * (B^T)^T + B * (A^T)^T = A * B + B * A = 2 * A * B = 0 (mod 2).
    This algebraically guarantees 100% symplectic commutativity by construction.
    Coupled non-circulant matrices can be formed by introducing permutation shifts P.
    """

    def __init__(self, block_size: int) -> None:
        if block_size <= 1:
            raise ValueError(f"Block size L must be > 1, got {block_size}")
        self.L: int = block_size
        self.n: int = 2 * block_size

    def generate_css_pair(
        self, row_a: Sequence[int], row_b: Sequence[int]
    ) -> tuple[np.ndarray, np.ndarray]:
        """Generate (H_X, H_Z) binary matrices of shape (L, 2L)."""
        A = circulant_matrix(row_a)
        B = circulant_matrix(row_b)
        H_X = np.hstack([A, B])
        H_Z = np.hstack([B.T, A.T])
        return H_X, H_Z

    def check_symplectic_commutativity(self, H_X: np.ndarray, H_Z: np.ndarray) -> bool:
        """Check whether H_X * H_Z^T == 0 (mod 2)."""
        prod = (H_X @ H_Z.T) % 2
        return bool(np.all(prod == 0))

    def to_pauli_strings(self, H_X: np.ndarray, H_Z: np.ndarray) -> tuple[list[str], list[str]]:
        """Convert binary check matrices into Pauli string generator lists."""
        x_strings: list[str] = []
        for row in H_X:
            chars = ["X" if b else "I" for b in row]
            x_strings.append("".join(chars))

        z_strings: list[str] = []
        for row in H_Z:
            chars = ["Z" if b else "I" for b in row]
            z_strings.append("".join(chars))

        return x_strings, z_strings

    def sample_random_rows(
        self, weight_a: int, weight_b: int, rng: np.random.Generator
    ) -> tuple[np.ndarray, np.ndarray]:
        """Sample binary initial rows for A and B with fixed Hamming weights."""
        row_a = np.zeros(self.L, dtype=np.uint8)
        row_b = np.zeros(self.L, dtype=np.uint8)

        idx_a = rng.choice(self.L, size=min(weight_a, self.L), replace=False)
        row_a[idx_a] = 1

        idx_b = rng.choice(self.L, size=min(weight_b, self.L), replace=False)
        row_b[idx_b] = 1

        return row_a, row_b
