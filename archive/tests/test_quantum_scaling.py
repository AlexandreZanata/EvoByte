"""Tests for scaling verifier ladder, sparse Lanczos, and pre-registered hard targets (spec: Q13).

Validates sparse Hamiltonian assembly, matrix-free matvec, Lanczos ground-state solver,
symmetry-reduced subspace diagonalization, fast ansatz energy evaluation, and
mandatory pre-registered outcome reporting (SUPPORTED / NULL).
"""

from __future__ import annotations

import math
from dataclasses import replace

import numpy as np

from evobyte.quantum.hamiltonians import heisenberg, ising, j1j2
from evobyte.quantum.oracle import exact, to_hamiltonian_matrix
from evobyte.quantum.pauli import PHASES
from evobyte.quantum.scaling import (
    PREREGISTERED_TARGETS,
    OutcomeClass,
    VerifierTier,
    ansatz_energy_fast,
    build_dimer_product_ansatz,
    build_sparse_hamiltonian,
    hamiltonian_matvec,
    lanczos_ground_state,
    run_hard_target_search,
    symmetry_reduced_ground_state,
)


def test_sparse_hamiltonian_matches_dense_oracle():
    """Verify build_sparse_hamiltonian matches dense to_hamiltonian_matrix exactly."""
    for n in (2, 3, 4):
        for h_fn in (
            lambda n=n: ising(n, 1.0, 1.0),
            lambda n=n: heisenberg(n, 1.0),
            lambda n=n: j1j2(n, 1.0, 0.5) if n >= 3 else ising(n),
        ):
            terms = h_fn()
            h_dense = to_hamiltonian_matrix(terms, n)
            h_sparse = build_sparse_hamiltonian(terms, n).toarray()
            np.testing.assert_allclose(h_sparse, h_dense, atol=1e-12)


def test_matrix_free_matvec_matches_dense():
    """Verify matrix-free hamiltonian_matvec matches H_dense @ psi exactly."""
    rng = np.random.default_rng(123)
    for n in (2, 3, 4):
        terms = j1j2(n, 1.0, 0.5) if n >= 3 else ising(n)
        h_dense = to_hamiltonian_matrix(terms, n)

        dim = 1 << n
        psi = rng.normal(size=dim) + 1j * rng.normal(size=dim)
        psi /= np.linalg.norm(psi)

        matvec_out = hamiltonian_matvec(terms, psi, n)
        dense_out = h_dense @ psi
        np.testing.assert_allclose(matvec_out, dense_out, atol=1e-12)


def test_lanczos_vs_dense_exact_ground_state():
    """Verify Lanczos solver computes exact ground state energy and state within 1e-8."""
    for n in (4, 6):
        terms = j1j2(n, 1.0, 0.5)
        res_exact = exact(terms, n)
        e_exact = res_exact["E_exact"]
        psi_exact = res_exact["psi_exact"]

        e_lanczos, psi_lanczos = lanczos_ground_state(terms, n)
        assert np.isclose(e_lanczos, e_exact, atol=1e-8)

        # State fidelity
        fid = float(abs(np.vdot(psi_exact, psi_lanczos)) ** 2)
        assert fid > 0.999999


def test_symmetry_reduced_ground_state():
    """Verify symmetry-reduced Sz=0 ground state matches exact full-space solver."""
    for n in (4, 6):
        terms = j1j2(n, 1.0, 0.5)
        e_exact = exact(terms, n)["E_exact"]

        e_sub, psi_full, sub_basis = symmetry_reduced_ground_state(terms, n, sector="sz=0")
        assert np.isclose(e_sub, e_exact, atol=1e-8)
        assert len(sub_basis) == math.comb(n, n // 2)

        # Check that psi_full is normalized
        assert np.isclose(np.linalg.norm(psi_full), 1.0, atol=1e-10)
        h_dense = to_hamiltonian_matrix(terms, n)
        assert np.linalg.norm(h_dense @ psi_full - e_sub * psi_full) < 1e-8


def test_fast_ansatz_energy_evaluation():
    """Verify O(K*M) ansatz_energy_fast reproduces statevector Rayleigh quotient."""
    n = 4
    terms = j1j2(n, 1.0, 0.5)
    dimer_ansatz = build_dimer_product_ansatz(n)

    # Fast evaluation
    e_fast = ansatz_energy_fast(terms, dimer_ansatz)

    # Reconstruct statevector
    dim = 1 << n
    vec = np.zeros(dim, dtype=np.complex128)
    for c, m, p in dimer_ansatz:
        vec[m] += c * PHASES[p % 4]
    vec /= np.linalg.norm(vec)

    h_dense = to_hamiltonian_matrix(terms, n)
    e_dense = float(np.real(np.vdot(vec, h_dense @ vec)))

    assert np.isclose(e_fast, e_dense, atol=1e-12)
    assert np.isclose(e_fast, -6.0, atol=1e-12)  # Exact Majumdar-Ghosh value for N=4


def test_preregistered_catalog_structure():
    """Verify pre-registered target definitions follow binding protocol."""
    assert len(PREREGISTERED_TARGETS) >= 5
    for tid, target in PREREGISTERED_TARGETS.items():
        assert target.target_id == tid
        assert target.n_qubits >= 6
        assert target.energy_tolerance > 0.0
        assert target.max_evaluations > 0
        assert target.wall_clock_timeout_sec > 0.0


def test_run_hard_target_supported_outcome():
    """Verify supported target T1_J1J2_MG_N6 correctly achieves SUPPORTED outcome."""
    target = PREREGISTERED_TARGETS["T1_J1J2_MG_N6"]
    res = run_hard_target_search(target, seed=42)

    assert res.outcome == OutcomeClass.SUPPORTED
    assert res.n_qubits == 6
    assert res.energy_error <= target.energy_tolerance
    assert res.fidelity is not None and res.fidelity >= target.fidelity_threshold
    assert res.verifier_tier in (VerifierTier.SYMMETRY_REDUCED, VerifierTier.SPARSE_LANCZOS)
    assert res.details["seeded_known_ansatz"] is True
    assert res.details["reference_used_for_early_stop"] is True
    assert res.details["research_acceptance"] == "provisional"


def test_run_hard_target_null_outcome():
    """Verify the fixed budgeted pilot honestly reports its unreached thresholds."""
    target = PREREGISTERED_TARGETS["T6_UNSOLVED_FRUST_N12"]
    res = run_hard_target_search(target, seed=42)

    # Must honestly report NULL (budget exhausted, tolerance unreached) without falsifying convergence
    assert res.outcome == OutcomeClass.NULL
    assert res.energy_error > target.energy_tolerance
    assert res.evaluations <= target.max_evaluations


def test_matrix_report_rejects_incomplete_and_inconsistent_outcomes():
    from benchmarks.qforge_hard_matrix import report_passes

    target = PREREGISTERED_TARGETS["T1_J1J2_MG_N6"]
    result = run_hard_target_search(target, seed=42)
    assert report_passes([result])
    assert not report_passes([])
    for invalid in (
        replace(result, outcome=OutcomeClass.NEEDS_WORK),
        replace(result, discovered_energy=float("inf")),
        replace(result, reference_energy=float("nan")),
        replace(result, fidelity=float("nan")),
        replace(result, fidelity=0.0),
        replace(result, evaluations=0),
        replace(result, evaluations=target.max_evaluations + 1),
        replace(result, energy_error=1.0),
        replace(result, outcome=OutcomeClass.NULL),
    ):
        assert not report_passes([invalid])

    negative = replace(
        result,
        outcome=OutcomeClass.NULL,
        discovered_energy=result.reference_energy + 1.0,
        energy_error=1.0,
        fidelity=0.0,
        evaluations=target.max_evaluations,
    )
    assert report_passes([negative])
    assert not report_passes([replace(negative, evaluations=1)])


def test_matrix_cli_fails_for_needs_work(monkeypatch):
    from benchmarks import qforge_hard_matrix

    target = PREREGISTERED_TARGETS["T1_J1J2_MG_N6"]
    result = replace(run_hard_target_search(target, seed=42), outcome=OutcomeClass.NEEDS_WORK)
    monkeypatch.setattr("sys.argv", ["qforge_hard_matrix", "--targets", target.target_id])
    monkeypatch.setattr(qforge_hard_matrix, "probe", dict)
    monkeypatch.setattr(qforge_hard_matrix, "get_git_commit", lambda: "test")
    monkeypatch.setattr(
        qforge_hard_matrix, "run_hard_target_search", lambda *args, **kwargs: result
    )
    assert qforge_hard_matrix.main() == 1
