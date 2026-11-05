"""Unit tests for Exact SAT Quantum Distance Solver (P214).

Validates:
1. Steane [[7, 1, 3]] CSS code exact distance d = 3.
2. Shor [[9, 1, 3]] CSS code exact distance d = 3.
3. Gottesman [[8, 3, 3]] non-CSS stabilizer code exact distance d = 3.
4. Bivariate [[16, 2, 4]] code exact distance d = 4.
5. Toric [[18, 2, 3]] code exact distance d = 3.
6. Cardinality encodings: Totalizer, Sorting Network, and Sequential Counter.
7. Latency gate: verification runtime << 30 seconds per instance.
"""

from __future__ import annotations

import time

import numpy as np
import pytest

from evobyte.bivariate_bicycle import bivariate_16_2_4, toric_code_2d
from evobyte.sat_distance_solver import (
    ExactSATDistanceSolver,
    extract_general_stabilizer_logicals,
    pauli_to_symplectic_vector,
    symplectic_to_pauli_string,
)


def steane_code_matrices() -> tuple[np.ndarray, np.ndarray]:
    """Return parity check matrices (HX, HZ) for Steane [[7, 1, 3]] code."""
    H = np.array(
        [
            [1, 0, 0, 1, 0, 1, 1],
            [0, 1, 0, 1, 1, 0, 1],
            [0, 0, 1, 0, 1, 1, 1],
        ],
        dtype=np.uint8,
    )
    return H, H


def shor_code_matrices() -> tuple[np.ndarray, np.ndarray]:
    """Return parity check matrices (HX, HZ) for Shor [[9, 1, 3]] code."""
    HX = np.array(
        [
            [1, 1, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 1, 1],
        ],
        dtype=np.uint8,
    )
    HZ = np.array(
        [
            [1, 1, 1, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 1, 1, 1, 1, 1, 1],
        ],
        dtype=np.uint8,
    )
    return HX, HZ


def gottesman_code_generators() -> list[str]:
    """Return 5 commuting generators for Gottesman [[8, 3, 3]] stabilizer code."""
    return [
        "YYXYYYYY",
        "ZYYYIXXI",
        "IYZZZYZI",
        "IYYIXZYX",
        "ZXXZIIZY",
    ]


def test_pauli_symplectic_conversion() -> None:
    """Test bi-directional conversion between Pauli strings and symplectic vectors."""
    pauli = "IXYZ"
    vec = pauli_to_symplectic_vector(pauli)
    assert np.array_equal(vec, [0, 1, 1, 0, 0, 0, 1, 1])
    reconstructed = symplectic_to_pauli_string(vec, 4)
    assert reconstructed == pauli


def test_steane_code_exact_sat_distance() -> None:
    """Test Steane [[7, 1, 3]] exact distance d=3 via Totalizer SAT solver."""
    HX, HZ = steane_code_matrices()
    solver = ExactSATDistanceSolver(cardinality_encoding="totalizer")

    t0 = time.perf_counter()
    cert = solver.compute_exact_distance((HX, HZ), max_distance=4)
    elapsed = time.perf_counter() - t0

    assert cert.n == 7
    assert cert.k == 1
    assert cert.d == 3
    assert cert.is_css is True
    assert cert.distance_verified is False  # Refuted d >= 4
    assert cert.minimal_logical_pauli is not None
    assert cert.minimal_logical_pauli.count("I") == 4  # Weight 3
    assert elapsed < 5.0  # Latency gate << 30s


def test_shor_code_exact_sat_distance() -> None:
    """Test Shor [[9, 1, 3]] exact distance d=3 via Sorting Network SAT solver."""
    HX, HZ = shor_code_matrices()
    solver = ExactSATDistanceSolver(cardinality_encoding="sortnetwrk")

    cert = solver.prove_distance_at_least((HX, HZ), min_distance=3)
    assert cert.n == 9
    assert cert.k == 1
    assert cert.distance_verified is True
    assert cert.proven_lower_bound == 3

    # Check that d >= 4 is refuted
    cert4 = solver.prove_distance_at_least((HX, HZ), min_distance=4)
    assert cert4.distance_verified is False
    assert cert4.d == 3


def test_gottesman_8_3_3_non_css_sat_distance() -> None:
    """Test Gottesman [[8, 3, 3]] non-CSS stabilizer code exact distance d=3."""
    gens = gottesman_code_generators()
    solver = ExactSATDistanceSolver(cardinality_encoding="totalizer")

    t0 = time.perf_counter()
    cert = solver.compute_exact_distance(gens, max_distance=4)
    elapsed = time.perf_counter() - t0

    assert cert.n == 8
    assert cert.k == 3
    assert cert.d == 3
    assert cert.is_css is False
    assert cert.minimal_logical_pauli is not None
    assert cert.minimal_logical_pauli.count("I") == 5  # Exactly weight 3 (8 - 5 = 3)
    assert elapsed < 10.0


def test_bivariate_16_2_4_sat_distance() -> None:
    """Test Bivariate [[16, 2, 4]] code exact distance d=4 via SAT."""
    code = bivariate_16_2_4()
    solver = ExactSATDistanceSolver(cardinality_encoding="totalizer")

    t0 = time.perf_counter()
    # Prove d >= 4
    cert = solver.prove_distance_at_least(code, min_distance=4)
    elapsed = time.perf_counter() - t0

    assert cert.distance_verified is True
    assert cert.proven_lower_bound == 4
    assert cert.n == 16
    assert cert.k == 2
    assert elapsed < 5.0

    # Prove that d is exactly 4 by finding weight-4 witness
    cert5 = solver.prove_distance_at_least(code, min_distance=5)
    assert cert5.distance_verified is False
    assert cert5.d == 4


def test_toric_18_2_3_sat_distance() -> None:
    """Test 2D Toric [[18, 2, 3]] code exact distance d=3 via SAT."""
    code = toric_code_2d(3, 3, compute_distance=False)
    solver = ExactSATDistanceSolver(cardinality_encoding="seqcounter")

    cert = solver.compute_exact_distance(code, max_distance=4)
    assert cert.n == 18
    assert cert.k == 2
    assert cert.d == 3
    assert cert.minimal_logical_pauli is not None


def test_find_minimal_logical() -> None:
    """Test find_minimal_logical helper method on Steane code."""
    HX, HZ = steane_code_matrices()
    solver = ExactSATDistanceSolver()
    d, pauli = solver.find_minimal_logical((HX, HZ), max_weight=4)
    assert d == 3
    assert len(pauli) == 7
    assert pauli.count("I") == 4
