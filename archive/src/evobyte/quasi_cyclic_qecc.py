"""Quasi-Cyclic & Lifted Product Non-Circulant Quantum Error-Correcting Codes Engine (P203).

Provides algebraic constructions for CSS quantum stabilizer codes breaking pure circulant
symmetry while guaranteeing 100% symplectic commutativity by mathematical construction:
1. BicirculantQECCEngine: Quasi-cyclic 2-block codes H_X = (A | B), H_Z = (B^T | A^T).
   Commutativity H_X * H_Z^T = A*B + B*A = 2*A*B = 0 (mod 2) holds for all circulant A, B.
2. LiftedProductQECCEngine: Generalized hypergraph / lifted products of two classical complexes:
   H_X = (A (x) I | I (x) B), H_Z = (I (x) B^T | A^T (x) I).
   Commutativity holds identically for all binary matrices A, B.
3. Fast CSS distance evaluator: Computes d = min(d_X, d_Z) via bit-parallel kernel searches.

Part of the Generalized Symmetries & Non-Circulant Quantum Codes Program (P201-P210, D045).
"""

from __future__ import annotations

from dataclasses import dataclass
import itertools
from typing import Sequence

import numpy as np

from evobyte.symmetry_engine import circulant_matrix


def gf2_basis_and_indices(mat: np.ndarray) -> tuple[list[int], list[int]]:
    """Compute GF(2) basis bit-vectors and corresponding row indices."""
    basis: list[int] = []
    selected_indices: list[int] = []
    for idx, row in enumerate(mat):
        v = int(sum(int(b) << i for i, b in enumerate(row)))
        w = v
        for b in basis:
            w = min(w, w ^ b)
        if w:
            hb = w.bit_length() - 1
            for i, b in enumerate(basis):
                if (b >> hb) & 1:
                    basis[i] = b ^ w
            basis.append(w)
            basis.sort(reverse=True)
            selected_indices.append(idx)
    return basis, selected_indices


def gf2_rank(mat: np.ndarray) -> int:
    """Compute exact GF(2) matrix rank."""
    basis, _ = gf2_basis_and_indices(mat)
    return len(basis)


def in_gf2_span(vec: int, basis: Sequence[int]) -> bool:
    """Check if integer bit-vector lies in GF(2) row span."""
    w = vec
    for b in basis:
        if w ^ b < w:
            w ^= b
    return w == 0


def verify_symplectic_orthogonality(HX: np.ndarray, HZ: np.ndarray) -> bool:
    """Verify symplectic condition HX * HZ^T == 0 (mod 2)."""
    prod = (HX @ HZ.T) % 2
    return bool(np.all(prod == 0))


def css_exact_distance(HX: np.ndarray, HZ: np.ndarray, max_weight: int = 5) -> tuple[int, int, int]:
    """Compute exact CSS code distance d = min(d_X, d_Z) up to max_weight.

    Returns:
        (d, d_X, d_Z) where d_X is minimum weight non-trivial X logical operator,
        and d_Z is minimum weight non-trivial Z logical operator.
        Returns (0, 0, 0) if k <= 0.
        If no logical operator is found up to max_weight, returns max_weight + 1.
    """
    _mx, n = HX.shape
    basis_x, _ = gf2_basis_and_indices(HX)
    basis_z, _ = gf2_basis_and_indices(HZ)
    rx = len(basis_x)
    rz = len(basis_z)
    k = n - rx - rz
    if k <= 0:
        return 0, 0, 0

    if not verify_symplectic_orthogonality(HX, HZ):
        raise ValueError("Check matrices do not commute symplectically!")

    hx_int = [int(sum(int(b) << i for i, b in enumerate(row))) for row in HX]
    hz_int = [int(sum(int(b) << i for i, b in enumerate(row))) for row in HZ]

    # Search d_X: non-zero x in ker(HZ) \ span(HX)
    dx = max_weight + 1
    for w in range(1, max_weight + 1):
        found = False
        for pos in itertools.combinations(range(n), w):
            v = sum(1 << p for p in pos)
            # v in ker(HZ) iff popcount(v & r) % 2 == 0 for all r in HZ
            if all((bin(v & r).count("1") & 1) == 0 for r in hz_int):
                if not in_gf2_span(v, basis_x):
                    dx = w
                    found = True
                    break
        if found:
            break

    # Search d_Z: non-zero z in ker(HX) \ span(HZ)
    dz = max_weight + 1
    for w in range(1, max_weight + 1):
        found = False
        for pos in itertools.combinations(range(n), w):
            v = sum(1 << p for p in pos)
            # v in ker(HX) iff popcount(v & r) % 2 == 0 for all r in HX
            if all((bin(v & r).count("1") & 1) == 0 for r in hx_int):
                if not in_gf2_span(v, basis_z):
                    dz = w
                    found = True
                    break
        if found:
            break

    d = min(dx, dz)
    return d, dx, dz


@dataclass(frozen=True)
class QuasiCyclicStabilizer:
    """Represents a quasi-cyclic or lifted product CSS quantum stabilizer code."""

    n: int
    k: int
    d: int | None
    HX: np.ndarray
    HZ: np.ndarray
    code_family: str
    row_a: tuple[int, ...] | None = None
    row_b: tuple[int, ...] | None = None

    @property
    def is_valid(self) -> bool:
        """Check if code has valid symplectic orthogonality and non-negative k."""
        if self.n <= 0 or self.k < 0:
            return False
        rx = gf2_rank(self.HX)
        rz = gf2_rank(self.HZ)
        if self.n - rx - rz != self.k:
            return False
        return verify_symplectic_orthogonality(self.HX, self.HZ)

    def to_pauli_strings(self) -> list[str]:
        """Convert check matrices into list of Pauli generator strings."""
        generators: list[str] = []
        for row in self.HX:
            generators.append("".join("X" if b else "I" for b in row))
        for row in self.HZ:
            generators.append("".join("Z" if b else "I" for b in row))
        return generators

    def compute_distance(self, max_weight: int = 5) -> int:
        """Compute exact code distance d."""
        d, _, _ = css_exact_distance(self.HX, self.HZ, max_weight=max_weight)
        return d


class BicirculantQECCEngine:
    """Quasi-cyclic 2-block stabilizer code engine.

    Constructs parity check matrices:
    H_X = (A | B), H_Z = (B^T | A^T)
    where A and B are circulant matrices of size L x L.
    Total qubits n = 2L.
    Symplectic commutativity:
    H_X * H_Z^T = A * B + B * A = 2 * A * B = 0 (mod 2) by matrix commutativity.
    """

    def __init__(self, block_size: int) -> None:
        if block_size <= 1:
            raise ValueError(f"Block size L must be > 1, got {block_size}")
        self.L: int = block_size
        self.n: int = 2 * block_size

    def sample_random_rows(
        self, weight_a: int, weight_b: int, rng: np.random.Generator
    ) -> tuple[np.ndarray, np.ndarray]:
        """Sample binary initial rows for A and B with prescribed Hamming weights."""
        row_a = np.zeros(self.L, dtype=np.uint8)
        row_b = np.zeros(self.L, dtype=np.uint8)

        idx_a = rng.choice(self.L, size=min(weight_a, self.L), replace=False)
        row_a[idx_a] = 1

        idx_b = rng.choice(self.L, size=min(weight_b, self.L), replace=False)
        row_b[idx_b] = 1

        return row_a, row_b

    def generate_code(
        self,
        row_a: Sequence[int],
        row_b: Sequence[int],
        target_k: int | None = None,
        compute_d: bool = False,
        max_weight: int = 5,
    ) -> QuasiCyclicStabilizer:
        """Generate a QuasiCyclicStabilizer instance from row_a and row_b.

        Extracts an independent basis of check rows. If target_k is given and
        k < target_k, selectively reduces check rows to achieve exact target_k.
        """
        A = circulant_matrix(row_a)
        B = circulant_matrix(row_b)
        HX_full = np.hstack([A, B]).astype(np.uint8)
        HZ_full = np.hstack([B.T, A.T]).astype(np.uint8)

        # Extract independent rows
        _, idx_x = gf2_basis_and_indices(HX_full)
        _, idx_z = gf2_basis_and_indices(HZ_full)

        HX_basis = HX_full[idx_x]
        HZ_basis = HZ_full[idx_z]

        current_k = self.n - len(HX_basis) - len(HZ_basis)

        # If target_k is requested and larger than current_k, drop check rows
        if target_k is not None and target_k > current_k:
            diff = target_k - current_k
            # Drop from HZ or HX while keeping valid
            drop_z = min(diff, len(HZ_basis))
            if drop_z > 0:
                HZ_basis = HZ_basis[:-drop_z]
                diff -= drop_z
            if diff > 0 and len(HX_basis) > diff:
                HX_basis = HX_basis[:-diff]
            current_k = self.n - len(HX_basis) - len(HZ_basis)

        d_val: int | None = None
        if compute_d and current_k > 0:
            d_val, _, _ = css_exact_distance(HX_basis, HZ_basis, max_weight=max_weight)

        return QuasiCyclicStabilizer(
            n=self.n,
            k=current_k,
            d=d_val,
            HX=HX_basis,
            HZ=HZ_basis,
            code_family="bicirculant_css",
            row_a=tuple(int(x) for x in row_a),
            row_b=tuple(int(x) for x in row_b),
        )

    def search_code(
        self,
        weight_a: int,
        weight_b: int,
        num_trials: int,
        rng: np.random.Generator,
        target_k: int | None = None,
        min_distance: int | None = None,
        max_weight: int = 5,
    ) -> list[QuasiCyclicStabilizer]:
        """Search for quasi-cyclic stabilizer codes matching criteria."""
        results: list[QuasiCyclicStabilizer] = []
        for _ in range(num_trials):
            ra, rb = self.sample_random_rows(weight_a, weight_b, rng)
            code = self.generate_code(
                ra,
                rb,
                target_k=target_k,
                compute_d=(min_distance is not None),
                max_weight=max_weight,
            )
            if target_k is not None and code.k != target_k:
                continue
            if min_distance is not None:
                if code.d is not None and code.d >= min_distance:
                    results.append(code)
            else:
                results.append(code)
        return results


class LiftedProductQECCEngine:
    """Lifted Product / Generalized Hypergraph Product code engine.

    Given classical check matrices H1 (m1 x n1) and H2 (m2 x n2),
    constructs quantum check matrices:
    H_X = (H1 (x) I_m2 | I_m1 (x) H2)
    H_Z = (I_n1 (x) H2^T | H1^T (x) I_n2)
    Total qubits n = n1 * m2 + m1 * n2.
    Symplectic condition:
    H_X * H_Z^T = (H1 (x) I_m2)(I_n1 (x) H2) + (I_m1 (x) H2)(H1 (x) I_n2)
                = H1 (x) H2 + H1 (x) H2 = 0 (mod 2).
    """

    @staticmethod
    def generate_code(
        H1: np.ndarray,
        H2: np.ndarray,
        compute_d: bool = False,
        max_weight: int = 5,
    ) -> QuasiCyclicStabilizer:
        """Construct a lifted product quantum code from classical parity matrices."""
        m1, n1 = H1.shape
        m2, n2 = H2.shape
        n_total = n1 * m2 + m1 * n2

        HX_left = np.kron(H1, np.eye(m2, dtype=np.uint8))
        HX_right = np.kron(np.eye(m1, dtype=np.uint8), H2)
        HX_full = np.hstack([HX_left, HX_right]).astype(np.uint8) % 2

        HZ_left = np.kron(np.eye(n1, dtype=np.uint8), H2.T)
        HZ_right = np.kron(H1.T, np.eye(n2, dtype=np.uint8))
        HZ_full = np.hstack([HZ_left, HZ_right]).astype(np.uint8) % 2

        _, idx_x = gf2_basis_and_indices(HX_full)
        _, idx_z = gf2_basis_and_indices(HZ_full)

        HX_basis = HX_full[idx_x]
        HZ_basis = HZ_full[idx_z]

        k = n_total - len(HX_basis) - len(HZ_basis)
        d_val: int | None = None
        if compute_d and k > 0:
            d_val, _, _ = css_exact_distance(HX_basis, HZ_basis, max_weight=max_weight)

        return QuasiCyclicStabilizer(
            n=n_total,
            k=k,
            d=d_val,
            HX=HX_basis,
            HZ=HZ_basis,
            code_family="lifted_product",
        )
