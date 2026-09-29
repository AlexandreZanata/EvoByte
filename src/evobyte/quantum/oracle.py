"""Exact-diagonalization oracle (spec: docs/quantum/VERIFIER.md, Q03 scope).

SCORING-ONLY DISCIPLINE:
Ground-truth diagonalization (E_exact, psi_exact, full spectrum) exists
strictly for post-hoc scoring, threshold validation, and benchmark metrics.
Oracle outputs must NEVER flow into candidate generation, mutation, crossover,
or generation-loop selection inputs.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from evobyte.quantum.pauli import Pauli, to_matrix

ORACLE_MAX_QUBITS = 12


def to_hamiltonian_matrix(terms: Any, n: int) -> np.ndarray:
    """Build dense 2^N Hermitian matrix from PauliTerm list."""
    if n > ORACLE_MAX_QUBITS:
        raise ValueError(f"oracle refused for n={n} > {ORACLE_MAX_QUBITS}")
    dim = 2**n
    h = np.zeros((dim, dim), dtype=np.complex128)
    for t in terms:
        h += t.coeff * to_matrix(Pauli(t.x_mask, t.z_mask, t.phase, n))
    return h


def operator_matrix(terms: Any, n: int) -> np.ndarray:
    """Dense candidate-operator matrix (strict verification only)."""
    return to_hamiltonian_matrix(terms, n)


def exact(terms: Any, n: int) -> dict[str, Any]:
    """Exact diagonalization oracle -> E_exact, psi_exact (scoring only)."""
    h = to_hamiltonian_matrix(terms, n)
    if not np.allclose(h, h.conj().T, atol=1e-12):
        raise ValueError("hamiltonian matrix is not hermitian")
    evals, evecs = np.linalg.eigh(h)
    return {
        "energies": evals,
        "E_exact": float(evals[0]),
        "psi_exact": evecs[:, 0],
        "eigenvectors": evecs,
    }


def commutator_norm(h_terms: Any, o_terms: Any, n: int) -> float:
    """Frobenius norm ||H*O - O*H||_F (strict verification)."""
    h = to_hamiltonian_matrix(h_terms, n)
    o = operator_matrix(o_terms, n)
    return float(np.linalg.norm(h @ o - o @ h, ord="fro"))


def energy(h_terms: Any, n: int, psi: np.ndarray) -> float:
    """Expectation value <psi|H|psi> for normalized state psi."""
    h = to_hamiltonian_matrix(h_terms, n)
    norm = np.linalg.norm(psi)
    if norm < 1e-14:
        raise ValueError("cannot evaluate energy of null state")
    psi_norm = psi / norm
    return float(np.real(np.vdot(psi_norm, h @ psi_norm)))


def fidelity(a: np.ndarray, b: np.ndarray) -> float:
    """State fidelity |<a|b>|^2 normalized (post-hoc scoring only)."""
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a < 1e-14 or norm_b < 1e-14:
        return 0.0
    overlap = np.vdot(a / norm_a, b / norm_b)
    return float(abs(overlap) ** 2)


def ground_state_fidelity(
    psi: np.ndarray, oracle_truth: dict[str, Any], tol: float = 1e-6
) -> float:
    """Fidelity to ground eigenspace, properly handling degenerate ground states."""
    norm = np.linalg.norm(psi)
    if norm < 1e-14:
        return 0.0
    psi_norm = psi / norm
    evals = oracle_truth["energies"]
    evecs = oracle_truth["eigenvectors"]
    e0 = float(oracle_truth["E_exact"])
    deg_indices = [i for i, ev in enumerate(evals) if abs(ev - e0) <= tol]
    fid = sum(abs(np.vdot(evecs[:, i], psi_norm)) ** 2 for i in deg_indices)
    return float(np.clip(fid, 0.0, 1.0))


def energy_and_fidelity(
    h_terms: Any, n: int, psi_candidate: np.ndarray, oracle_truth: dict[str, Any] | None = None
) -> dict[str, float]:
    """Joint evaluation of candidate energy, error vs exact, and ground-state fidelity."""
    truth = exact(h_terms, n) if oracle_truth is None else oracle_truth
    e_cand = energy(h_terms, n, psi_candidate)
    e_exact = float(truth["E_exact"])
    fid = ground_state_fidelity(psi_candidate, truth)
    return {
        "energy_candidate": e_cand,
        "energy_exact": e_exact,
        "energy_error": abs(e_cand - e_exact),
        "fidelity": fid,
    }


def assert_scoring_only_isolation(source_files: list[str | Path]) -> None:
    """Audit helper: asserts search/generation files never import exact or psi_exact."""
    prohibited_tokens = ("from evobyte.quantum.oracle import exact", "psi_exact")
    for file_path in source_files:
        path = Path(file_path)
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8")
        for token in prohibited_tokens:
            if token in content:
                raise AssertionError(
                    f"Scoring-only isolation failure in {path}: contains prohibited token '{token}'"
                )
