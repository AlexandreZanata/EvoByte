"""Symplectic binary Pauli algebra (spec: docs/quantum/REPRESENTATION.md).

Encoding per qubit: I = 00, X = 10, Z = 01, Y = 11 as (x, z) bits.
Operator convention: P = PHASES[phase] * X^x Z^z, phase in Z4.
Single-Pauli phases: I, X, Z -> 0; Y -> 1 (since Y = iXZ).

Hot-path rules use ints + XOR/AND/POPCOUNT only. Matrices exist solely for
the small-N exact oracle and strict checks — never for bulk search.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

PHASES = (1.0 + 0.0j, 0.0 + 1.0j, -1.0 + 0.0j, 0.0 - 1.0j)

_SINGLE_MATS = {
    (0, 0): np.array([[1, 0], [0, 1]], dtype=np.complex128),
    (1, 0): np.array([[0, 1], [1, 0]], dtype=np.complex128),
    (0, 1): np.array([[1, 0], [0, -1]], dtype=np.complex128),
    # NOTE: (1, 1) is X @ Z = [[0, -1], [1, 0]], NOT Y. The Y operator is
    # recovered via its phase: single-Y carries phase 1, i * XZ = Y.
    (1, 1): np.array([[0, -1], [1, 0]], dtype=np.complex128),
}

_KIND_BITS = {"I": (0, 0, 0), "X": (1, 0, 0), "Z": (0, 1, 0), "Y": (1, 1, 1)}


@dataclass(frozen=True)
class Pauli:
    """One Pauli string: x_mask / z_mask ints, phase in Z4, width n_qubits."""

    x_mask: int
    z_mask: int
    phase: int = 0
    n_qubits: int = 0

    def __post_init__(self) -> None:
        if self.n_qubits < 0:
            raise ValueError("n_qubits must be >= 0")
        if self.x_mask < 0 or self.z_mask < 0:
            raise ValueError("masks must be >= 0")
        if (self.x_mask >> self.n_qubits) or (self.z_mask >> self.n_qubits):
            raise ValueError("mask exceeds n_qubits width")
        object.__setattr__(self, "phase", self.phase % 4)

    def weight(self) -> int:
        """Number of non-identity qubits."""
        return (self.x_mask | self.z_mask).bit_count()


def single(qubit: int, kind: str, n_qubits: int) -> Pauli:
    """Single-qubit Pauli on `qubit` (0 = least-significant)."""
    if kind not in _KIND_BITS:
        raise ValueError(f"unknown pauli kind: {kind}")
    if not (0 <= qubit < n_qubits):
        raise ValueError(f"qubit {qubit} out of range for n={n_qubits}")
    x, z, phase = _KIND_BITS[kind]
    return Pauli(x << qubit if x else 0, z << qubit if z else 0, phase, n_qubits)


def identity(n_qubits: int) -> Pauli:
    """Identity string."""
    return Pauli(0, 0, 0, n_qubits)


def multiply(a: Pauli, b: Pauli) -> Pauli:
    """Product via XOR masks + Z4 phase from the symplectic form.

    X^x1 Z^z1 X^x2 Z^z2 = (-1)^(z1.x2) X^(x1+x2) Z^(z1+z2).
    """
    if a.n_qubits != b.n_qubits:
        raise ValueError("width mismatch in multiply")
    sign = (a.z_mask & b.x_mask).bit_count() % 2
    return Pauli(
        a.x_mask ^ b.x_mask, a.z_mask ^ b.z_mask, (a.phase + b.phase + 2 * sign) % 4, a.n_qubits
    )


def commutes_with(a: Pauli, b: Pauli) -> bool:
    """True iff the symplectic inner product is even (parity rule)."""
    if a.n_qubits != b.n_qubits:
        raise ValueError("width mismatch in commutes_with")
    parity = ((a.x_mask & b.z_mask).bit_count() + (a.z_mask & b.x_mask).bit_count()) % 2
    return parity == 0


def to_matrix(p: Pauli) -> np.ndarray:
    """Dense 2^N matrix (oracle/strict use only; exponential cost)."""
    n = p.n_qubits
    if n > 12:
        raise ValueError(f"dense matrix refused for n={n} > 12 (oracle limit)")
    result = np.array([[1.0 + 0.0j]], dtype=np.complex128)
    for q in range(n - 1, -1, -1):
        result = np.kron(result, _SINGLE_MATS[((p.x_mask >> q) & 1, (p.z_mask >> q) & 1)])
    return PHASES[p.phase] * result


def decode_human(p: Pauli) -> str:
    """Human-readable form for logs only. Never used in the hot path."""
    parts = []
    for q in range(p.n_qubits):
        bits = ((p.x_mask >> q) & 1, (p.z_mask >> q) & 1)
        kind = next(k for k, v in _KIND_BITS.items() if v[:2] == bits)
        if kind != "I":
            parts.append(f"{kind}{q}")
    body = " ".join(parts) if parts else "I"
    # The printed Y already includes iXZ; remove that phase from the prefix.
    relative_phase = (p.phase - (p.x_mask & p.z_mask).bit_count()) % 4
    coeff = {0: "", 1: "i*", 2: "-1*", 3: "-i*"}[relative_phase]
    return f"{coeff}{body}"
