"""Quantum circuit bytecode tests (Q07 gate).

Verifies frozen v0 gate table integrity, codec roundtrips, qubit-range validity,
critical-path depth math, NOP-equivalent padding invariance, human log decoding,
and exact unitary matrix properties.
"""

from __future__ import annotations

import numpy as np
import pytest

from evobyte.quantum.circuit import (
    CIRCUIT_BYTECODE_VERSION,
    OPCODE_CNOT,
    OPCODE_CZ,
    OPCODE_H,
    OPCODE_NOP,
    OPCODE_RX,
    OPCODE_RY,
    OPCODE_RZ,
    OPCODE_S,
    OPCODE_SWAP,
    OPCODE_T,
    OPCODE_X,
    OPCODE_Y,
    OPCODE_Z,
    V0_GATE_TABLE,
    CircuitInstruction,
    circuit_depth,
    circuit_to_unitary,
    decode_circuit,
    decode_circuit_text,
    encode_circuit,
    gate_count,
    is_valid_circuit,
    pad_circuit,
    single_qubit_gate_matrix,
    strip_nops,
    two_qubit_count,
    validate_circuit,
)


def test_frozen_v0_gate_table():
    assert CIRCUIT_BYTECODE_VERSION == 0
    assert len(V0_GATE_TABLE) == 13

    expected = {
        0: ("NOP", 0, False),
        1: ("H", 1, False),
        2: ("X", 1, False),
        3: ("Y", 1, False),
        4: ("Z", 1, False),
        5: ("S", 1, False),
        6: ("T", 1, False),
        7: ("RX", 1, True),
        8: ("RY", 1, True),
        9: ("RZ", 1, True),
        10: ("CNOT", 2, False),
        11: ("CZ", 2, False),
        12: ("SWAP", 2, False),
    }

    for op, (name, arity, param) in expected.items():
        assert op in V0_GATE_TABLE
        info = V0_GATE_TABLE[op]
        assert info.name == name
        assert info.num_qubits == arity
        assert info.is_parameterized == param


def test_circuit_codec_roundtrip():
    insts = [
        CircuitInstruction(OPCODE_H, 0, 0, 0.0),
        CircuitInstruction(OPCODE_CNOT, 0, 1, 0.0),
        CircuitInstruction(OPCODE_RZ, 1, 0, float(np.pi / 3)),
        CircuitInstruction(OPCODE_SWAP, 0, 2, 0.0),
        CircuitInstruction(OPCODE_NOP, 0, 0, 0.0),
    ]

    arr = encode_circuit(insts)
    assert arr.shape == (5, 4)
    assert arr.dtype == np.float64

    decoded = decode_circuit(arr)
    assert len(decoded) == 5
    for orig, dec in zip(insts, decoded):
        assert dec.gate == orig.gate
        assert dec.qubit_a == orig.qubit_a
        assert dec.qubit_b == orig.qubit_b
        assert abs(dec.param - orig.param) < 1e-12

    # Empty circuit
    assert len(decode_circuit(encode_circuit([]))) == 0

    # 1D flattened buffer
    decoded_flat = decode_circuit(arr.flatten())
    assert decoded_flat == decoded

    # Invalid buffer shape
    with pytest.raises(ValueError, match="not a multiple of 4"):
        decode_circuit(np.array([1.0, 2.0, 3.0]))

    with pytest.raises(ValueError, match="expected 2D buffer"):
        decode_circuit(np.zeros((3, 5)))


def test_circuit_validation():
    n = 3

    # Valid circuit
    valid_c = [
        CircuitInstruction(OPCODE_H, 0),
        CircuitInstruction(OPCODE_CNOT, 0, 2),
        CircuitInstruction(OPCODE_RX, 1, 0, np.pi / 2),
        CircuitInstruction(OPCODE_NOP),
    ]
    assert validate_circuit(valid_c, n)
    assert is_valid_circuit(valid_c, n)

    # Unknown opcode
    with pytest.raises(ValueError, match="unknown gate opcode 99"):
        validate_circuit([CircuitInstruction(99, 0)], n)
    assert not is_valid_circuit([CircuitInstruction(99, 0)], n)

    # Qubit out of range (1-qubit)
    with pytest.raises(ValueError, match="qubit_a=3 out of range"):
        validate_circuit([CircuitInstruction(OPCODE_H, 3)], n)

    # Qubit out of range negative
    with pytest.raises(ValueError, match="qubit_a=-1 out of range"):
        validate_circuit([CircuitInstruction(OPCODE_H, -1)], n)

    # Qubit out of range (2-qubit)
    with pytest.raises(ValueError, match="qubit_b=3 out of range"):
        validate_circuit([CircuitInstruction(OPCODE_CNOT, 0, 3)], n)

    # Identical operands on 2-qubit gate
    with pytest.raises(ValueError, match="must be distinct"):
        validate_circuit([CircuitInstruction(OPCODE_CNOT, 1, 1)], n)

    with pytest.raises(ValueError, match="must be distinct"):
        validate_circuit([CircuitInstruction(OPCODE_CZ, 2, 2)], n)

    # Non-finite parameter
    with pytest.raises(ValueError, match="not finite"):
        validate_circuit([CircuitInstruction(OPCODE_RX, 0, 0, float("nan"))], n)

    with pytest.raises(ValueError, match="not finite"):
        validate_circuit([CircuitInstruction(OPCODE_RY, 0, 0, float("inf"))], n)


def test_depth_and_accounting():
    n = 4

    # 1. Empty circuit
    assert gate_count([]) == 0
    assert two_qubit_count([]) == 0
    assert circuit_depth([], n) == 0

    # 2. Parallel 1-qubit gates on different qubits -> depth 1
    c_par = [
        CircuitInstruction(OPCODE_H, 0),
        CircuitInstruction(OPCODE_X, 1),
        CircuitInstruction(OPCODE_Z, 2),
    ]
    assert gate_count(c_par) == 3
    assert two_qubit_count(c_par) == 0
    assert circuit_depth(c_par, n) == 1

    # 3. Sequential 1-qubit gates on same qubit -> depth 3
    c_seq = [
        CircuitInstruction(OPCODE_H, 0),
        CircuitInstruction(OPCODE_X, 0),
        CircuitInstruction(OPCODE_Z, 0),
    ]
    assert circuit_depth(c_seq, n) == 3

    # 4. Standard Bell pair circuit: H(0), CNOT(0, 1) -> depth 2
    c_bell = [
        CircuitInstruction(OPCODE_H, 0),
        CircuitInstruction(OPCODE_CNOT, 0, 1),
    ]
    assert gate_count(c_bell) == 2
    assert two_qubit_count(c_bell) == 1
    assert circuit_depth(c_bell, n) == 2

    # 5. Interleaved 2-qubit and 1-qubit gates:
    # Layer 1: H(0), H(1) (depth 1)
    # Layer 2: CNOT(0, 1) (depth 2)
    # Layer 3: H(0), H(1) (depth 3)
    c_inter = [
        CircuitInstruction(OPCODE_H, 0),
        CircuitInstruction(OPCODE_H, 1),
        CircuitInstruction(OPCODE_CNOT, 0, 1),
        CircuitInstruction(OPCODE_H, 0),
        CircuitInstruction(OPCODE_H, 1),
    ]
    assert circuit_depth(c_inter, n) == 3
    assert gate_count(c_inter) == 5
    assert two_qubit_count(c_inter) == 1

    # 6. Disconnected qubits: gates on q[2] in parallel do not increase depth beyond max
    c_disjoint = [
        CircuitInstruction(OPCODE_H, 0),
        CircuitInstruction(OPCODE_CNOT, 0, 1),
        CircuitInstruction(OPCODE_Z, 2),  # parallel with layer 1
    ]
    assert circuit_depth(c_disjoint, n) == 2


def test_nop_equivalent_padding():
    n = 3
    c = [
        CircuitInstruction(OPCODE_H, 0),
        CircuitInstruction(OPCODE_CNOT, 0, 1),
        CircuitInstruction(OPCODE_RX, 2, 0, np.pi / 4),
    ]

    base_depth = circuit_depth(c, n)
    base_gates = gate_count(c)
    base_two_q = two_qubit_count(c)
    base_u = circuit_to_unitary(c, n)

    # Pad to length 10
    padded = pad_circuit(c, 10)
    assert len(padded) == 10
    assert gate_count(padded) == base_gates
    assert two_qubit_count(padded) == base_two_q
    assert circuit_depth(padded, n) == base_depth

    # Strip NOPs restores original
    assert strip_nops(padded) == c

    # Unitary invariance: U(pad(c)) == U(c)
    padded_u = circuit_to_unitary(padded, n)
    np.testing.assert_allclose(padded_u, base_u, atol=1e-12)

    # Padding error when target < current length
    with pytest.raises(ValueError, match="exceeds target_length"):
        pad_circuit(c, 2)


def test_human_decoder():
    c = [
        CircuitInstruction(OPCODE_H, 0),
        CircuitInstruction(OPCODE_CNOT, 0, 1),
        CircuitInstruction(OPCODE_RZ, 1, 0, np.pi / 2),
        CircuitInstruction(OPCODE_NOP),
    ]

    compact = decode_circuit_text(c, multiline=False)
    assert compact == "H q[0]; CNOT q[0], q[1]; RZ(1.5708) q[1]; NOP"

    multi = decode_circuit_text(c, multiline=True)
    expected_lines = [
        "H q[0]",
        "CNOT q[0], q[1]",
        "RZ(1.5708) q[1]",
        "NOP",
    ]
    assert multi.split("\n") == expected_lines


def test_unitary_gate_algebra():
    # 1. H^2 = I
    h = single_qubit_gate_matrix(OPCODE_H)
    np.testing.assert_allclose(h @ h, np.eye(2), atol=1e-12)

    # 2. Pauli squares: X^2 = Y^2 = Z^2 = I
    for op in (OPCODE_X, OPCODE_Y, OPCODE_Z):
        m = single_qubit_gate_matrix(op)
        np.testing.assert_allclose(m @ m, np.eye(2), atol=1e-12)

    # 3. Phase gates: S^2 = Z, T^2 = S, T^4 = Z
    s = single_qubit_gate_matrix(OPCODE_S)
    z = single_qubit_gate_matrix(OPCODE_Z)
    t = single_qubit_gate_matrix(OPCODE_T)
    np.testing.assert_allclose(s @ s, z, atol=1e-12)
    np.testing.assert_allclose(t @ t, s, atol=1e-12)
    np.testing.assert_allclose(t @ t @ t @ t, z, atol=1e-12)

    # 4. Rotation gates: RX(0) = I, RX(pi) = -iX
    rx0 = single_qubit_gate_matrix(OPCODE_RX, 0.0)
    np.testing.assert_allclose(rx0, np.eye(2), atol=1e-12)

    x = single_qubit_gate_matrix(OPCODE_X)
    rx_pi = single_qubit_gate_matrix(OPCODE_RX, np.pi)
    np.testing.assert_allclose(rx_pi, -1.0j * x, atol=1e-12)

    # 5. Two-qubit involutions: CNOT^2 = I, CZ^2 = I, SWAP^2 = I
    for op in (OPCODE_CNOT, OPCODE_CZ, OPCODE_SWAP):
        c2 = [CircuitInstruction(op, 0, 1), CircuitInstruction(op, 0, 1)]
        u2 = circuit_to_unitary(c2, 2)
        np.testing.assert_allclose(u2, np.eye(4), atol=1e-12)

    # 6. Bell state preparation: |00> -> (|00> + |11>) / sqrt(2)
    c_bell = [
        CircuitInstruction(OPCODE_H, 0),
        CircuitInstruction(OPCODE_CNOT, 0, 1),
    ]
    u_bell = circuit_to_unitary(c_bell, 2)
    psi_00 = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.complex128)
    psi_out = u_bell @ psi_00
    expected_bell = np.array([1.0 / np.sqrt(2), 0.0, 0.0, 1.0 / np.sqrt(2)], dtype=np.complex128)
    np.testing.assert_allclose(psi_out, expected_bell, atol=1e-12)
