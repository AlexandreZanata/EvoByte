"""Tests for Hamiltonian rediscovery from dynamics (spec: Q11).

Validates dynamics simulator, cryptographic dataset provenance, sanity oracle
(true Hamiltonian scores ~0 dynamics error), structural metrics, and evolutionary
rediscovery of terms and coefficients.
"""

from __future__ import annotations

import numpy as np
import pytest

from evobyte.quantum.hamdisc import (
    build_default_initial_states,
    build_default_observable_terms,
    build_klocal_pauli_dictionary,
    dynamics_matching_fitness,
    evaluate_structural_recovery,
    generate_dynamics_dataset,
    ising_transverse_benchmark,
    rediscover_hamiltonian_from_dynamics,
    simulate_dynamics,
    xyz_field_benchmark,
)
from evobyte.quantum.hamiltonians import PauliTerm


def test_dynamics_simulator_and_dataset_generation():
    """Verify dynamics simulator runs and generates structured dataset with SHA-256."""
    target = xyz_field_benchmark(n_qubits=2, jx=1.0, jy=0.5, jz=0.8, hz=0.4)
    ds = generate_dynamics_dataset(target, n_qubits=2, seed=42)

    assert ds.n_qubits == 2
    assert len(ds.initial_states) > 0
    assert len(ds.times) == 10
    assert len(ds.observable_terms) > 0
    assert ds.observed_trajectories.shape == (len(ds.initial_states), len(ds.times), len(ds.observable_terms))
    assert isinstance(ds.sha256_hash, str) and len(ds.sha256_hash) == 64
    assert not np.isnan(ds.observed_trajectories).any()


def test_true_hamiltonian_scores_near_zero_dynamics_error():
    """Sanity oracle (Task 2): true Hamiltonian scores ~0 dynamics error."""
    target = xyz_field_benchmark(n_qubits=2, jx=1.0, jy=0.5, jz=0.8, hz=0.4)
    ds = generate_dynamics_dataset(target, n_qubits=2)

    mse, total_loss = dynamics_matching_fitness(target, ds, lambda_sparse=0.0, lambda_comp=0.0)
    assert mse < 1e-14


def test_perturbed_and_wrong_hamiltonian_incur_error():
    """Verify that perturbed or wrong terms incur distinct dynamics error penalties."""
    target = xyz_field_benchmark(n_qubits=2, jx=1.0, jy=0.5, jz=0.8, hz=0.4)
    ds = generate_dynamics_dataset(target, n_qubits=2)

    # Small perturbation (5% coefficient offset)
    perturbed = [
        PauliTerm(t.coeff * 1.05, t.x_mask, t.z_mask, t.phase) for t in target
    ]
    mse_pert, _ = dynamics_matching_fitness(perturbed, ds, lambda_sparse=0.0, lambda_comp=0.0)
    assert 1e-5 < mse_pert < 1e-2

    # Completely wrong Hamiltonian (e.g. single wrong Pauli term)
    wrong = [PauliTerm(1.0, 1, 0, 0)]
    mse_wrong, _ = dynamics_matching_fitness(wrong, ds, lambda_sparse=0.0, lambda_comp=0.0)
    assert mse_wrong > 0.1


def test_klocal_pauli_dictionary_cardinality():
    """Verify dictionary generates all 1-local and 2-local Pauli words."""
    # N=2: 3*2 + 9*1 = 15 words
    dict_2 = build_klocal_pauli_dictionary(n_qubits=2, max_k=2)
    assert len(dict_2) == 15
    assert len(set(dict_2)) == 15  # All unique

    # N=3: 3*3 + 9*3 = 36 words
    dict_3 = build_klocal_pauli_dictionary(n_qubits=3, max_k=2)
    assert len(dict_3) == 36
    assert len(set(dict_3)) == 36


def test_evaluate_structural_recovery_metrics():
    """Verify precision, recall, and coefficient error metrics."""
    true_terms = [
        PauliTerm(1.0, 3, 0, 0),   # XX
        PauliTerm(0.5, 3, 3, 2),   # YY
        PauliTerm(0.8, 0, 3, 0),   # ZZ
    ]

    # Exact match
    metrics_exact = evaluate_structural_recovery(true_terms, true_terms)
    assert metrics_exact["precision"] == 1.0
    assert metrics_exact["recall"] == 1.0
    assert metrics_exact["f1"] == 1.0
    assert metrics_exact["coeff_mae"] == 0.0

    # Discovered has 1 false positive (extra term)
    cand_with_fp = true_terms + [PauliTerm(0.3, 1, 0, 0)]
    metrics_fp = evaluate_structural_recovery(cand_with_fp, true_terms)
    assert metrics_fp["precision"] == 3.0 / 4.0
    assert metrics_fp["recall"] == 1.0

    # Discovered misses 1 term (false negative)
    cand_with_fn = true_terms[:2]
    metrics_fn = evaluate_structural_recovery(cand_with_fn, true_terms)
    assert metrics_fn["precision"] == 1.0
    assert metrics_fn["recall"] == 2.0 / 3.0


def test_empty_hamiltonian_dynamics():
    """Verify empty Hamiltonian gracefully outputs static expectation values."""
    psi0 = np.array([1, 0, 0, 0], dtype=np.complex128)
    times = np.array([0.0, 1.0, 2.0])
    obs = [PauliTerm(1.0, 0, 1, 0)]  # Z0
    traj = simulate_dynamics([], 2, [psi0], times, obs)
    assert traj.shape == (1, 3, 1)
    np.testing.assert_allclose(traj[0, :, 0], 1.0)


def test_evolutionary_rediscovery_single_seed():
    """Task 3 verification: rediscovery finds exact terms with high fidelity."""
    target = xyz_field_benchmark(n_qubits=2, jx=1.0, jy=0.5, jz=0.8, hz=0.4)
    ds = generate_dynamics_dataset(target, n_qubits=2, seed=0)

    res = rediscover_hamiltonian_from_dynamics(
        dataset=ds,
        max_k=2,
        pop_size=80,
        max_generations=25,
        early_stop_mse=1e-6,
        seed=1,
    )

    assert res["dynamics_mse"] < 1e-5
    metrics = evaluate_structural_recovery(res["discovered_terms"], target)
    assert metrics["precision"] >= 0.99
    assert metrics["recall"] >= 0.99
    assert metrics["coeff_mae"] < 0.05
