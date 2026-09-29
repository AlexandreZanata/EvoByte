"""Symplectic algebra tests (Q00 gate). No GPU, no network."""

import numpy as np

from evobyte.quantum.pauli import (
    Pauli,
    commutes_with,
    decode_human,
    identity,
    multiply,
    single,
    to_matrix,
)


def test_single_constructors():
    assert single(0, "X", 2) == Pauli(0b01, 0, 0, 2)
    assert single(1, "Z", 2) == Pauli(0, 0b10, 0, 2)
    assert single(0, "Y", 1) == Pauli(1, 1, 1, 1)
    assert identity(3) == Pauli(0, 0, 0, 3)


def test_multiply_table():
    n = 1
    x, z, y, i = single(0, "X", n), single(0, "Z", n), single(0, "Y", n), identity(n)
    assert multiply(x, x) == i
    assert multiply(y, y) == i
    assert multiply(z, z) == i
    # X*Z = -iY -> (x=1, z=1, phase=0) decodes as XZ = -iY. Correct.
    assert multiply(x, z) == Pauli(1, 1, 0, n)
    # Z*X = +iY -> phase 2 (-1) times XZ = +iY. Correct.
    assert multiply(z, x) == Pauli(1, 1, 2, n)
    # Y*X = -iZ.
    assert multiply(y, x) == Pauli(0, 1, 3, n)


def test_algebra_matches_matrices():
    rng = np.random.default_rng(0)
    for _ in range(50):
        n = 3
        a = Pauli(int(rng.integers(0, 8)), int(rng.integers(0, 8)), int(rng.integers(0, 4)), n)
        b = Pauli(int(rng.integers(0, 8)), int(rng.integers(0, 8)), int(rng.integers(0, 4)), n)
        np.testing.assert_allclose(to_matrix(multiply(a, b)), to_matrix(a) @ to_matrix(b), atol=1e-12)


def test_commutation_parity():
    n = 2
    x0, z0 = single(0, "X", n), single(0, "Z", n)
    assert not commutes_with(x0, z0)  # same qubit: anticommute
    x1 = single(1, "X", n)
    assert commutes_with(x0, x1)  # disjoint qubits: commute
    # XX vs YY on 2 qubits: two per-qubit anticommutations -> overall commute.
    xx = Pauli(0b11, 0, 0, n)
    yy = Pauli(0b11, 0b11, 2, n)
    assert commutes_with(xx, yy)
    assert commutes_with(identity(n), yy)


def test_single_y_matrix_is_true_y():
    # Locks the convention: (x=1, z=1, phase=1) must equal Y, i.e. i * XZ.
    y_true = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
    np.testing.assert_allclose(to_matrix(single(0, "Y", 1)), y_true, atol=1e-12)


def test_decode_human_smoke():
    assert decode_human(identity(2)) == "I"
    assert decode_human(single(1, "Y", 2)) == "i*Y1"
