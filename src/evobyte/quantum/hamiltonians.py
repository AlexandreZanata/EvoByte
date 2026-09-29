"""Known Hamiltonians as compact PauliTerm lists + small-N exact oracle.

Layout follows docs/quantum/REPRESENTATION.md: Hamiltonian = PauliTerm[N]
(coefficient + x_mask + z_mask). Dense matrices and diagonalization exist
only here (oracle / strict checks), never in bulk search.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

import numpy as np

from evobyte.quantum.pauli import PHASES, Pauli, commutes_with, decode_human, to_matrix

ORACLE_MAX_QUBITS = 12


@dataclass(frozen=True)
class PauliTerm:
    """One Hamiltonian term: coeff * PHASES[phase] * X^x_mask Z^z_mask.

    phase counts Y singles mod 4 (each Y = iXZ): a YY bond term carries
    phase 2, since (iXZ)x(iXZ) = -XXZZ as matrices.
    """

    coeff: float
    x_mask: int
    z_mask: int
    phase: int = 0


def decode_term(term: PauliTerm, n_qubits: int) -> str:
    """Human-readable representation of a single Hamiltonian term for logs."""
    p = Pauli(term.x_mask, term.z_mask, term.phase, n_qubits)
    pauli_str = decode_human(p)
    return f"{term.coeff:+.4f}*{pauli_str}"


def decode_hamiltonian(terms: list[PauliTerm], n_qubits: int) -> str:
    """Human-readable representation of a full Hamiltonian for logs."""
    if not terms:
        return "0"
    return " + ".join(decode_term(t, n_qubits) for t in terms)


def _bond(i: int, j: int, kinds: str, coeff: float) -> list[PauliTerm]:
    """Two-qubit Pauli words on qubits i, j, one term per kind in `kinds`."""
    terms = []
    for k in kinds:
        xm = ((1 << i) | (1 << j)) if k in ("X", "Y") else 0
        zm = ((1 << i) | (1 << j)) if k in ("Z", "Y") else 0
        # Each Y single contributes phase 1 (Y = iXZ); a YY bond has two.
        phase = (xm & zm).bit_count() % 4
        terms.append(PauliTerm(coeff, xm, zm, phase))
    return terms


def ising(n: int, j: float = 1.0, h: float = 1.0) -> list[PauliTerm]:
    """Transverse-field Ising, open chain: -J Σ ZZ - h Σ X."""
    if n < 2:
        raise ValueError("ising needs n >= 2")
    terms = [PauliTerm(-h, 1 << i, 0) for i in range(n)]
    for i in range(n - 1):
        terms.append(PauliTerm(-j, 0, (1 << i) | (1 << (i + 1))))
    return terms


def heisenberg(n: int, j: float = 1.0) -> list[PauliTerm]:
    """Heisenberg XXX, open chain: J Σ (XX + YY + ZZ)."""
    if n < 2:
        raise ValueError("heisenberg needs n >= 2")
    terms: list[PauliTerm] = []
    for i in range(n - 1):
        terms.extend(_bond(i, i + 1, "XYZ", j))
    return terms


def j1j2(n: int, j1: float = 1.0, j2: float = 0.5) -> list[PauliTerm]:
    """J1-J2 chain: J1 nearest-neighbour XXX + J2 next-nearest XXX."""
    if n < 3:
        raise ValueError("j1j2 needs n >= 3")
    terms = heisenberg(n, j1)
    for i in range(n - 2):
        terms.extend(_bond(i, i + 2, "XYZ", j2))
    return terms


def total_sz(n: int) -> list[PauliTerm]:
    """Total magnetization Σ Zi (known to commute with Heisenberg)."""
    return [PauliTerm(1.0, 0, 1 << i) for i in range(n)]


def ising_parity(n: int) -> Pauli:
    """Global spin-flip Π Xi (known to commute with transverse Ising)."""
    return Pauli((1 << n) - 1, 0, 0, n)


def hamiltonian_hash(terms: list[PauliTerm]) -> str:
    """Stable id for Hall of Fame rows and run records."""
    canon = sorted((t.coeff, t.x_mask, t.z_mask, t.phase) for t in terms)
    return hashlib.sha256(repr(canon).encode()).hexdigest()[:16]


def to_hamiltonian_matrix(terms: list[PauliTerm], n: int) -> np.ndarray:
    """Dense Hermitian (oracle/strict only)."""
    if n > ORACLE_MAX_QUBITS:
        raise ValueError(f"oracle refused for n={n} > {ORACLE_MAX_QUBITS}")
    dim = 2**n
    h = np.zeros((dim, dim), dtype=np.complex128)
    for t in terms:
        h += t.coeff * to_matrix(Pauli(t.x_mask, t.z_mask, t.phase, n))
    return h


def operator_matrix(terms: list[PauliTerm], n: int) -> np.ndarray:
    """Dense candidate-operator matrix (strict checks only)."""
    return to_hamiltonian_matrix(terms, n)


def exact(terms: list[PauliTerm], n: int) -> dict:
    """Exact diagonalization oracle -> E_exact, psi_exact (scoring only)."""
    h = to_hamiltonian_matrix(terms, n)
    if not np.allclose(h, h.conj().T):
        raise ValueError("hamiltonian matrix is not hermitian")
    evals, evecs = np.linalg.eigh(h)
    return {"energies": evals, "E_exact": float(evals[0]), "psi_exact": evecs[:, 0]}


def commutator_norm(h_terms: list[PauliTerm], o_terms: list[PauliTerm], n: int) -> float:
    """||H·O - O·H||_F (strict verification; bit-algebra prefilter lives in pauli)."""
    h = to_hamiltonian_matrix(h_terms, n)
    o = operator_matrix(o_terms, n)
    return float(np.linalg.norm(h @ o - o @ h, ord="fro"))


def commutes_bitwise(h_terms: list[PauliTerm], o: Pauli) -> bool:
    """Cheap necessary check: candidate commutes with every H term bitwise."""
    n = o.n_qubits
    return all(commutes_with(Pauli(t.x_mask, t.z_mask, 0, n), o) for t in h_terms)


def energy(h_terms: list[PauliTerm], n: int, psi: np.ndarray) -> float:
    """Expectation <ψ|H|ψ> (assumes normalized psi)."""
    h = to_hamiltonian_matrix(h_terms, n)
    return float(np.real(np.vdot(psi, h @ psi)))


def fidelity(a: np.ndarray, b: np.ndarray) -> float:
    """|<a|b>|^2 (post-hoc scoring only, never selection)."""
    return float(abs(np.vdot(a, b)) ** 2)


def phase_of(p: Pauli) -> complex:
    """Complex phase factor of a Pauli string."""
    return PHASES[p.phase]
