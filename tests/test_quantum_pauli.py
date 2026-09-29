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


def test_64_qubit_algebra():
    n = 64
    x63 = single(63, "X", n)
    z63 = single(63, "Z", n)
    y63 = single(63, "Y", n)
    x62 = single(62, "X", n)

    assert x63.x_mask == (1 << 63)
    assert z63.z_mask == (1 << 63)
    assert y63.weight() == 1

    # Same qubit anticommutes, different qubits commute
    assert not commutes_with(x63, z63)
    assert commutes_with(x63, x62)
    assert commutes_with(x63, single(62, "Z", n))

    # Multiplication on bit 63
    assert multiply(x63, x63) == identity(n)
    assert multiply(x63, z63) == Pauli(1 << 63, 1 << 63, 0, n)
    assert multiply(z63, x63) == Pauli(1 << 63, 1 << 63, 2, n)

    # Full 64-qubit strings
    all_ones = (1 << 64) - 1
    all_x = Pauli(all_ones, 0, 0, n)
    all_z = Pauli(0, all_ones, 0, n)
    assert all_x.weight() == 64
    assert all_z.weight() == 64
    # 64 anticommuting pairs -> even parity (0) -> commutes!
    assert commutes_with(all_x, all_z)

    # 63-qubit strings: 63 anticommuting pairs -> odd parity (1) -> anticommutes!
    n63 = 63
    all_x_63 = Pauli((1 << 63) - 1, 0, 0, n63)
    all_z_63 = Pauli(0, (1 << 63) - 1, 0, n63)
    assert not commutes_with(all_x_63, all_z_63)


def test_pauli_validation_errors():
    import pytest

    with pytest.raises(ValueError, match="n_qubits must be >= 0"):
        Pauli(0, 0, 0, -1)

    with pytest.raises(ValueError, match="masks must be >= 0"):
        Pauli(-1, 0, 0, 2)
    with pytest.raises(ValueError, match="masks must be >= 0"):
        Pauli(0, -1, 0, 2)

    with pytest.raises(ValueError, match="mask exceeds n_qubits width"):
        Pauli(4, 0, 0, 2)
    with pytest.raises(ValueError, match="mask exceeds n_qubits width"):
        Pauli(0, 4, 0, 2)
    with pytest.raises(ValueError, match="mask exceeds n_qubits width"):
        Pauli(1, 0, 0, 0)
    with pytest.raises(ValueError, match="mask exceeds n_qubits width"):
        Pauli(0, 1, 0, 0)

    # 64-qubit overflow
    with pytest.raises(ValueError, match="mask exceeds n_qubits width"):
        Pauli(1 << 64, 0, 0, 64)

    # Single invalid inputs
    with pytest.raises(ValueError, match="unknown pauli kind"):
        single(0, "W", 2)
    with pytest.raises(ValueError, match="qubit -1 out of range"):
        single(-1, "X", 2)
    with pytest.raises(ValueError, match="qubit 2 out of range"):
        single(2, "X", 2)

    # Width mismatches
    with pytest.raises(ValueError, match="width mismatch in multiply"):
        multiply(Pauli(0, 0, 0, 2), Pauli(0, 0, 0, 3))
    with pytest.raises(ValueError, match="width mismatch in commutes_with"):
        commutes_with(Pauli(0, 0, 0, 2), Pauli(0, 0, 0, 3))

    # Dense matrix refusal for n > 12
    with pytest.raises(ValueError, match="dense matrix refused"):
        to_matrix(Pauli(0, 0, 0, 13))


def test_algebraic_identities():
    rng = np.random.default_rng(42)
    n = 4
    for _ in range(30):
        masks = [int(rng.integers(0, 1 << n)) for _ in range(6)]
        phases = [int(rng.integers(0, 4)) for _ in range(3)]
        a = Pauli(masks[0], masks[1], phases[0], n)
        b = Pauli(masks[2], masks[3], phases[1], n)
        c = Pauli(masks[4], masks[5], phases[2], n)

        # Associativity: (A * B) * C == A * (B * C)
        ab_c = multiply(multiply(a, b), c)
        a_bc = multiply(a, multiply(b, c))
        assert ab_c == a_bc

        # Identity: A * I == A and I * A == A
        i = identity(n)
        assert multiply(a, i) == a
        assert multiply(i, a) == a

        # Self-commutation: A always commutes with A
        assert commutes_with(a, a)

    # Phase modulo wrapping
    p_wrapped = Pauli(1, 0, 5, 2)
    assert p_wrapped.phase == 1
    p_neg = Pauli(1, 0, -1, 2)
    assert p_neg.phase == 3


def test_zero_qubit_system():
    i0 = identity(0)
    assert i0.n_qubits == 0
    assert i0.weight() == 0
    assert multiply(i0, i0) == i0
    assert commutes_with(i0, i0)
    mat = to_matrix(i0)
    assert mat.shape == (1, 1)
    assert mat[0, 0] == 1.0 + 0.0j
