"""Bivariate Group Algebra Engine (P212).

Implements 2-dimensional abelian group algebras F_2[Z_l x Z_m] = F_2[x, y] / <x^l - 1, y^m - 1>:
1. BivariatePolynomial: Polynomial arithmetic over GF(2) with 2D cyclic wrap-around.
2. BivariateGroupAlgebra: Factory for polynomial rings, Kronecker shift representations,
   and algebraic involution.
3. BivariateBicycleCode: Canonical CSS quantum stabilizer code generator from polynomial pairs
   (A(x, y), B(x, y)) with guaranteed symplectic orthogonality (HX @ HZ^T = 0 mod 2).
4. Commutativity Verification: Exact algebraic theorem testing proving AB = BA identically.

Part of the Bivariate Bicycle & Projective Geometries Program (P211-P220, D047).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Sequence

import numpy as np


def _shift_matrix(dim: int, p: int) -> np.ndarray:
    """Return a dim x dim cyclic shift matrix with shift p (S^p)."""
    p = p % dim
    mat = np.zeros((dim, dim), dtype=np.uint8)
    for i in range(dim):
        mat[i, (i + p) % dim] = 1
    return mat


def _gf2_rank(mat: np.ndarray) -> int:
    """Compute the rank of a binary matrix over GF(2) via Gaussian elimination."""
    m = mat.copy() % 2
    r, c = m.shape
    rank = 0
    for col in range(c):
        pivot = None
        for row in range(rank, r):
            if m[row, col] == 1:
                pivot = row
                break
        if pivot is not None:
            if pivot != rank:
                m[[rank, pivot]] = m[[pivot, rank]]
            for row in range(r):
                if row != rank and m[row, col] == 1:
                    m[row] = (m[row] + m[rank]) % 2
            rank += 1
            if rank == r:
                break
    return rank


@dataclass(frozen=True)
class BivariatePolynomial:
    """An immutable bivariate polynomial in F_2[x, y] / <x^l - 1, y^m - 1>.

    Coefficients are elements of GF(2), represented as a frozenset of (i, j) monomial powers
    satisfying 0 <= i < l and 0 <= j < m.
    """

    l: int
    m: int
    coeffs: frozenset[tuple[int, int]]

    def __post_init__(self) -> None:
        if self.l <= 0 or self.m <= 0:
            raise ValueError(f"Dimensions must be positive, got l={self.l}, m={self.m}")
        # Validate that all terms are strictly in [0, l) x [0, m)
        for i, j in self.coeffs:
            if not (0 <= i < self.l and 0 <= j < self.m):
                raise ValueError(
                    f"Term ({i}, {j}) out of bounds for ring of size {self.l} x {self.m}"
                )

    @property
    def weight(self) -> int:
        """Hamming weight: number of non-zero monomials."""
        return len(self.coeffs)

    @property
    def is_zero(self) -> bool:
        """True if the polynomial is zero."""
        return len(self.coeffs) == 0

    def __add__(self, other: BivariatePolynomial) -> BivariatePolynomial:
        """Add two polynomials over GF(2) (symmetric difference of monomial sets)."""
        if self.l != other.l or self.m != other.m:
            raise ValueError(f"Ring mismatch: ({self.l}, {self.m}) vs ({other.l}, {other.m})")
        return BivariatePolynomial(self.l, self.m, self.coeffs ^ other.coeffs)

    def __mul__(self, other: BivariatePolynomial) -> BivariatePolynomial:
        """Multiply two polynomials with 2D cyclic convolution modulo x^l - 1 and y^m - 1."""
        if self.l != other.l or self.m != other.m:
            raise ValueError(f"Ring mismatch: ({self.l}, {self.m}) vs ({other.l}, {other.m})")

        term_counts: dict[tuple[int, int], int] = {}
        for i1, j1 in self.coeffs:
            for i2, j2 in other.coeffs:
                prod = ((i1 + i2) % self.l, (j1 + j2) % self.m)
                term_counts[prod] = term_counts.get(prod, 0) + 1

        new_coeffs = frozenset(term for term, count in term_counts.items() if count % 2 == 1)
        return BivariatePolynomial(self.l, self.m, new_coeffs)

    def transpose(self) -> BivariatePolynomial:
        """Involution / algebraic transpose: maps x^i y^j -> x^{-i} y^{-j}."""
        new_coeffs = frozenset(((-i) % self.l, (-j) % self.m) for i, j in self.coeffs)
        return BivariatePolynomial(self.l, self.m, new_coeffs)

    def to_matrix(self) -> np.ndarray:
        """Convert polynomial to its (lm) x (lm) binary matrix representation over GF(2).

        M = sum_{(i, j) in coeffs} S_l^i (x) S_m^j  (mod 2).
        """
        dim = self.l * self.m
        mat = np.zeros((dim, dim), dtype=np.uint8)
        if not self.coeffs:
            return mat

        for i, j in self.coeffs:
            term = np.kron(_shift_matrix(self.l, i), _shift_matrix(self.m, j))
            mat = (mat + term) % 2
        return mat


class BivariateGroupAlgebra:
    """Factory for bivariate group algebra F_2[Z_l x Z_m]."""

    def __init__(self, l: int, m: int) -> None:
        if l <= 0 or m <= 0:
            raise ValueError(f"Dimensions l, m must be positive, got l={l}, m={m}")
        self.l: int = int(l)
        self.m: int = int(m)
        self.matrix_dim: int = self.l * self.m

    def zero(self) -> BivariatePolynomial:
        """Return the zero polynomial."""
        return BivariatePolynomial(self.l, self.m, frozenset())

    def one(self) -> BivariatePolynomial:
        """Return the identity polynomial 1 = x^0 y^0."""
        return BivariatePolynomial(self.l, self.m, frozenset([(0, 0)]))

    def x(self, power: int = 1) -> BivariatePolynomial:
        """Return x^power monomial."""
        return BivariatePolynomial(self.l, self.m, frozenset([(power % self.l, 0)]))

    def y(self, power: int = 1) -> BivariatePolynomial:
        """Return y^power monomial."""
        return BivariatePolynomial(self.l, self.m, frozenset([(0, power % self.m)]))

    def from_terms(self, terms: Iterable[tuple[int, int]]) -> BivariatePolynomial:
        """Construct polynomial from an iterable of (i, j) powers with GF(2) reduction."""
        term_counts: dict[tuple[int, int], int] = {}
        for i, j in terms:
            canon = (int(i) % self.l, int(j) % self.m)
            term_counts[canon] = term_counts.get(canon, 0) + 1
        coeffs = frozenset(term for term, count in term_counts.items() if count % 2 == 1)
        return BivariatePolynomial(self.l, self.m, coeffs)

    def random_polynomial(
        self,
        rng: np.random.Generator | None = None,
        density: float = 0.3,
    ) -> BivariatePolynomial:
        """Sample a random polynomial with the given monomial probability density."""
        if rng is None:
            rng = np.random.default_rng()
        terms = []
        for i in range(self.l):
            for j in range(self.m):
                if rng.random() < density:
                    terms.append((i, j))
        return self.from_terms(terms)


class BivariateBicycleCode:
    """Bivariate Bicycle CSS quantum code constructor.

    Given A, B in F_2[Z_l x Z_m]:
      H_X = (M(A) | M(B))
      H_Z = (M(B)^T | M(A)^T)

    Number of physical qubits: n = 2 * l * m.
    Commutativity theorem: M(A) M(B) = M(B) M(A) mod 2, ensuring H_X H_Z^T = 0 mod 2.
    """

    def __init__(self, A: BivariatePolynomial, B: BivariatePolynomial) -> None:
        if A.l != B.l or A.m != B.m:
            raise ValueError(f"Ring mismatch: ({A.l}, {A.m}) vs ({B.l}, {B.m})")
        self.A: BivariatePolynomial = A
        self.B: BivariatePolynomial = B
        self.l: int = A.l
        self.m: int = A.m
        self.n: int = 2 * self.l * self.m

        # Compute matrix representations
        self.mat_A: np.ndarray = A.to_matrix()
        self.mat_B: np.ndarray = B.to_matrix()

        # Build parity check matrices
        self.HX: np.ndarray = np.hstack([self.mat_A, self.mat_B]).astype(np.uint8)
        self.HZ: np.ndarray = np.hstack([self.mat_B.T, self.mat_A.T]).astype(np.uint8)

        self._rx: int | None = None
        self._rz: int | None = None

    def verify_symplectic(self) -> bool:
        """Verify symplectic orthogonality: H_X @ H_Z^T == 0 (mod 2)."""
        comm = (self.HX @ self.HZ.T) % 2
        return bool(np.all(comm == 0))

    def ranks(self) -> tuple[int, int]:
        """Compute (rank(H_X), rank(H_Z)) over GF(2)."""
        if self._rx is None:
            self._rx = _gf2_rank(self.HX)
            self._rz = _gf2_rank(self.HZ)
        assert self._rz is not None
        return self._rx, self._rz

    def logical_qubits(self) -> int:
        """Compute the number of logical qubits k = n - rank(H_X) - rank(H_Z)."""
        rx, rz = self.ranks()
        return self.n - rx - rz

    def extract_independent_generators(self) -> tuple[str, ...]:
        """Extract linearly independent stabilizer generators as Pauli strings."""

        def _get_indep_rows(mat: np.ndarray) -> list[int]:
            m = mat.copy() % 2
            r, c = m.shape
            indep = []
            echelon: list[np.ndarray] = []
            for i in range(r):
                row = m[i].copy()
                for e in echelon:
                    lead = int(np.argmax(e == 1))
                    if row[lead] == 1:
                        row = (row + e) % 2
                if np.any(row == 1):
                    echelon.append(row)
                    indep.append(i)
            return indep

        ix = _get_indep_rows(self.HX)
        iz = _get_indep_rows(self.HZ)

        paulis: list[str] = []
        for i in ix:
            paulis.append("".join("X" if b == 1 else "I" for b in self.HX[i]))
        for i in iz:
            paulis.append("".join("Z" if b == 1 else "I" for b in self.HZ[i]))

        return tuple(paulis)


def verify_bivariate_commutativity(
    A: BivariatePolynomial,
    B: BivariatePolynomial,
) -> tuple[bool, dict[str, Any]]:
    """Algebraic test verifying commutativity both as polynomials and as matrices.

    Checks:
    1. A * B == B * A in F_2[x, y] / <x^l - 1, y^m - 1>.
    2. M(A) @ M(B) == M(B) @ M(A) (mod 2).
    """
    prod_ab = A * B
    prod_ba = B * A
    poly_commutes = prod_ab.coeffs == prod_ba.coeffs

    mat_A = A.to_matrix()
    mat_B = B.to_matrix()
    mat_comm = (mat_A @ mat_B + mat_B @ mat_A) % 2
    mat_commutes = bool(np.all(mat_comm == 0))

    ok = poly_commutes and mat_commutes
    payload = {
        "poly_commutes": poly_commutes,
        "mat_commutes": mat_commutes,
        "l": A.l,
        "m": A.m,
        "weight_A": A.weight,
        "weight_B": B.weight,
    }
    return ok, payload
