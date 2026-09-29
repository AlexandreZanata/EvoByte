"""Exact-diagonalization oracle tests (Q03 gate).

Verifies golden spectra for laboratory models, spectral decomposition,
hermiticity enforcement, energy/fidelity metrics, and scoring-only isolation.
"""

from pathlib import Path
import numpy as np
import pytest

from evobyte.quantum.hamiltonians import PauliTerm, heisenberg, ising, j1j2
from evobyte.quantum.oracle import (
    ORACLE_MAX_QUBITS,
    assert_scoring_only_isolation,
    commutator_norm,
    energy,
    energy_and_fidelity,
    exact,
    fidelity,
    to_hamiltonian_matrix,
)


def test_ising_two_qubit_golden_values():
    # 1. Pure coupling (J=1, h=0): H = -ZZ
    # Eigenvalues: -1 (doublet: |00>, |11>), +1 (doublet: |01>, |10>)
    out_coupling = exact(ising(2, j=1.0, h=0.0), 2)
    np.testing.assert_allclose(
        sorted(out_coupling["energies"]), [-1.0, -1.0, 1.0, 1.0], atol=1e-12
    )
    assert abs(out_coupling["E_exact"] - (-1.0)) < 1e-12

    # 2. Pure transverse field (J=0, h=1): H = -X0 - X1
    # Eigenvalues: -2 (singlet |++>), 0 (doublet |+->, |-+>), +2 (singlet |--->)
    out_field = exact(ising(2, j=0.0, h=1.0), 2)
    np.testing.assert_allclose(
        sorted(out_field["energies"]), [-2.0, 0.0, 0.0, 2.0], atol=1e-12
    )
    assert abs(out_field["E_exact"] - (-2.0)) < 1e-12

    # 3. Transverse Ising at critical point (J=1, h=1): H = -ZZ - X0 - X1
    # Analytical eigenvalues: -sqrt(5), -1, +1, +sqrt(5)
    out_crit = exact(ising(2, j=1.0, h=1.0), 2)
    expected_crit = sorted([-np.sqrt(5), -1.0, 1.0, np.sqrt(5)])
    np.testing.assert_allclose(sorted(out_crit["energies"]), expected_crit, atol=1e-12)
    assert abs(out_crit["E_exact"] - (-np.sqrt(5))) < 1e-12


def test_heisenberg_two_qubit_golden_values():
    # Two-qubit Heisenberg XXX bond: J (XX + YY + ZZ)
    # Singlet S=0 (energy -3J), Triplet S=1 (energy +1J, 3-fold degenerate)
    out1 = exact(heisenberg(2, j=1.0), 2)
    np.testing.assert_allclose(sorted(out1["energies"]), [-3.0, 1.0, 1.0, 1.0], atol=1e-12)
    assert abs(out1["E_exact"] - (-3.0)) < 1e-12

    # Singlet state is |psi_singlet> = (|01> - |10>) / sqrt(2)
    psi_singlet = np.array([0.0, 1.0 / np.sqrt(2), -1.0 / np.sqrt(2), 0.0], dtype=np.complex128)
    fid = fidelity(out1["psi_exact"], psi_singlet)
    assert abs(fid - 1.0) < 1e-12

    # Scaled coupling J=2.5 -> energies -7.5, +2.5, +2.5, +2.5
    out2 = exact(heisenberg(2, j=2.5), 2)
    np.testing.assert_allclose(sorted(out2["energies"]), [-7.5, 2.5, 2.5, 2.5], atol=1e-12)
    assert abs(out2["E_exact"] - (-7.5)) < 1e-12


def test_hermiticity_and_spectral_properties():
    # Check full spectral decomposition for N=2..4 Heisenberg and Ising
    for n in (2, 3, 4):
        for h_terms in (ising(n), heisenberg(n), j1j2(n) if n >= 3 else ising(n)):
            out = exact(h_terms, n)
            h = to_hamiltonian_matrix(h_terms, n)

            # 1. Hermiticity
            np.testing.assert_allclose(h, h.conj().T, atol=1e-12)

            # 2. Ascending order
            evals = out["energies"]
            assert np.all(np.diff(evals) >= -1e-12)

            # 3. Ground energy matches evals[0]
            assert abs(out["E_exact"] - evals[0]) < 1e-12

            # 4. Eigenvector relation: H * psi_k = lambda_k * psi_k
            evecs = out["eigenvectors"]
            for k in range(len(evals)):
                psi_k = evecs[:, k]
                np.testing.assert_allclose(h @ psi_k, evals[k] * psi_k, atol=1e-11)

            # 5. Orthonormality: V^dag V = I
            np.testing.assert_allclose(evecs.conj().T @ evecs, np.eye(2**n), atol=1e-11)


def test_non_hermitian_matrix_rejected():
    # Construct an artificial non-Hermitian operator term
    # E.g. a single term with complex coefficient not balanced
    non_herm = [PauliTerm(1.0 + 1.0j, 1, 0, 0)]  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="hamiltonian matrix is not hermitian"):
        exact(non_herm, 1)


def test_energy_and_fidelity_metrics():
    n = 2
    h_terms = heisenberg(n, j=1.0)
    out = exact(h_terms, n)

    # 1. Candidate is exact ground state
    psi_gs = out["psi_exact"]
    metrics_gs = energy_and_fidelity(h_terms, n, psi_gs, oracle_truth=out)
    assert abs(metrics_gs["energy_candidate"] - (-3.0)) < 1e-12
    assert abs(metrics_gs["energy_exact"] - (-3.0)) < 1e-12
    assert abs(metrics_gs["energy_error"]) < 1e-12
    assert abs(metrics_gs["fidelity"] - 1.0) < 1e-12

    # 2. Candidate is orthogonal excited state (triplet)
    psi_triplet = out["eigenvectors"][:, 1]
    metrics_ex = energy_and_fidelity(h_terms, n, psi_triplet, oracle_truth=out)
    assert abs(metrics_ex["energy_candidate"] - 1.0) < 1e-12
    assert abs(metrics_ex["energy_error"] - 4.0) < 1e-12  # 1.0 - (-3.0) = 4.0
    assert abs(metrics_ex["fidelity"]) < 1e-12

    # 3. Null state rejection
    with pytest.raises(ValueError, match="cannot evaluate energy of null state"):
        energy(h_terms, n, np.zeros((4,), dtype=np.complex128))


def test_oracle_max_qubits_guard():
    # Refuse N > ORACLE_MAX_QUBITS
    with pytest.raises(ValueError, match=f"oracle refused for n={ORACLE_MAX_QUBITS + 1}"):
        to_hamiltonian_matrix(ising(2), ORACLE_MAX_QUBITS + 1)


def test_scoring_only_isolation_audit():
    # Audit: search modules must NOT import exact or psi_exact
    search_file = Path(__file__).resolve().parents[1] / "src" / "evobyte" / "quantum" / "search.py"
    assert_scoring_only_isolation([search_file])
