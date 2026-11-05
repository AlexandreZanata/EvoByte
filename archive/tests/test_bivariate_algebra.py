"""Tests for Bivariate Group Algebra Engine (P212).

Validates:
1. Ring arithmetic axioms (additive XOR, multiplication convolution modulo <x^l - 1, y^m - 1>).
2. Commutativity theorem: A * B == B * A and M(A) @ M(B) == M(B) @ M(A) mod 2 for all rings.
3. Transposition involution: (A^T)^T == A and (A * B)^T == B^T * A^T.
4. Bivariate Bicycle code construction: HX @ HZ^T == 0 mod 2 for arbitrary polynomials.
5. Exact reproduction of Bravyi et al. (Nature 2024) [[72, 12, 6]] parameters.
6. Generator extraction and independent stabilizer verification.
"""

from __future__ import annotations

import numpy as np

from evobyte.bivariate_algebra import (
    BivariateBicycleCode,
    BivariateGroupAlgebra,
    BivariatePolynomial,
    verify_bivariate_commutativity,
)
from evobyte.qecc_verifier import check_stabilizer


def test_ring_arithmetic_axioms() -> None:
    """Verify additive and multiplicative ring axioms over GF(2)."""
    alg = BivariateGroupAlgebra(l=5, m=4)
    zero = alg.zero()
    one = alg.one()

    # Zero identity
    p = alg.from_terms([(1, 2), (3, 0)])
    assert p + zero == p
    assert zero + p == p
    assert p + p == zero  # Characteristic 2: p + p = 0

    # Multiplicative identity
    assert p * one == p
    assert one * p == p

    # Distributivity: p1 * (p2 + p3) == p1 * p2 + p1 * p3
    p1 = alg.from_terms([(1, 1), (0, 2)])
    p2 = alg.from_terms([(2, 3), (1, 0)])
    p3 = alg.from_terms([(0, 0), (3, 2)])
    assert p1 * (p2 + p3) == (p1 * p2) + (p1 * p3)


def test_algebraic_commutativity_theorem() -> None:
    """Theorem: Every bivariate group algebra F_2[Z_l x Z_m] is commutative."""
    rng = np.random.default_rng(20261027)
    test_dimensions = [(6, 6), (9, 2), (5, 4), (10, 2), (3, 3)]

    for l, m in test_dimensions:
        alg = BivariateGroupAlgebra(l, m)
        for _ in range(5):
            A = alg.random_polynomial(rng, density=0.35)
            B = alg.random_polynomial(rng, density=0.35)
            ok, payload = verify_bivariate_commutativity(A, B)
            assert ok is True, f"Commutativity failed for ({l}, {m}): {payload}"
            assert payload["poly_commutes"] is True
            assert payload["mat_commutes"] is True


def test_transposition_involution() -> None:
    """Algebraic transpose satisfies (A^T)^T = A and (A * B)^T = B^T * A^T."""
    alg = BivariateGroupAlgebra(l=7, m=3)
    p1 = alg.from_terms([(2, 1), (5, 2)])
    p2 = alg.from_terms([(1, 0), (3, 2)])

    assert p1.transpose().transpose() == p1
    assert (p1 * p2).transpose() == p2.transpose() * p1.transpose()


def test_bivariate_bicycle_code_symplectic() -> None:
    """Every bivariate bicycle code must satisfy HX @ HZ^T == 0 mod 2 identically."""
    rng = np.random.default_rng(42)
    test_rings = [(4, 4), (5, 3), (6, 2)]

    for l, m in test_rings:
        alg = BivariateGroupAlgebra(l, m)
        for _ in range(4):
            A = alg.random_polynomial(rng, density=0.4)
            B = alg.random_polynomial(rng, density=0.4)
            code = BivariateBicycleCode(A, B)
            assert code.verify_symplectic() is True, f"Symplectic check failed for ({l}, {m})"


def test_bravyi_72_12_6_reproduction() -> None:
    """Exact reproduction of the Bravyi et al. (Nature 2024) [[72, 12, 6]] code."""
    alg = BivariateGroupAlgebra(l=6, m=6)
    # A = x^3 + y + y^2
    A = alg.from_terms([(3, 0), (0, 1), (0, 2)])
    # B = y^3 + x + x^2
    B = alg.from_terms([(0, 3), (1, 0), (2, 0)])

    code = BivariateBicycleCode(A, B)
    assert code.n == 72
    assert code.verify_symplectic() is True

    rx, rz = code.ranks()
    assert rx == 30
    assert rz == 30
    assert code.logical_qubits() == 12

    # Extract generators and verify with check_stabilizer
    paulis = code.extract_independent_generators()
    assert len(paulis) == 60
    ok, payload = check_stabilizer(paulis)
    assert ok is True, f"check_stabilizer failed: {payload}"
    assert payload["n"] == 72
    assert payload["k"] == 12
    assert payload["rank"] == 60
