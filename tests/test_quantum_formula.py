"""Tests for quantum observable simulation and formula rediscovery (Q09 gate).

Verifies analytical observable accuracy (energy, gap, magnetization, entropy),
dataset generation and SHA-256 hashing, dataset splitting, and symbolic rediscovery.
"""

from __future__ import annotations

import numpy as np

from evobyte.evolution import EvolutionConfig, run_evolution
from evobyte.quantum.hamiltonians import ising
from evobyte.quantum.observables import (
    entanglement_entropy,
    generate_observable_dataset,
    ground_energy,
    magnetization_x,
    spectral_gap,
    split_observable_dataset,
)
from evobyte.quantum.oracle import exact


def test_analytical_observables_two_qubit_ising():
    # 2-qubit Ising at J=1.0: H = -ZZ - h(X0 + X1)
    # Analytical: E_0(h) = -sqrt(1 + 4h^2)
    # Analytical: Gap(h) = sqrt(1 + 4h^2) - 1
    # Analytical: M_x(h) = 2h / sqrt(1 + 4h^2)
    for h_val in (0.0, 0.5, 1.0, 2.0):
        h_terms = ising(2, j=1.0, h=h_val)
        e0 = ground_energy(h_terms, 2)
        gap = spectral_gap(h_terms, 2)

        expected_e0 = -np.sqrt(1.0 + 4.0 * h_val**2)
        expected_gap = np.sqrt(1.0 + 4.0 * h_val**2) - 1.0

        assert abs(e0 - expected_e0) < 1e-12
        assert abs(gap - expected_gap) < 1e-12

        owe = exact(h_terms, 2)
        psi_0 = owe["psi_exact"]
        mx = magnetization_x(psi_0, 2)
        expected_mx = (2.0 * h_val) / np.sqrt(1.0 + 4.0 * h_val**2) if h_val > 0 else 0.0
        assert abs(mx - expected_mx) < 1e-10


def test_entanglement_entropy():
    # 1. Product state |00> has zero entanglement entropy
    psi_prod = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.complex128)
    s_prod = entanglement_entropy(psi_prod, 2, subsystem_size=1)
    assert abs(s_prod) < 1e-12

    # 2. Maximally entangled Bell state (|00> + |11>)/sqrt(2) has S = 1.0 bit
    psi_bell = np.array([1.0, 0.0, 0.0, 1.0], dtype=np.complex128) / np.sqrt(2.0)
    s_bell = entanglement_entropy(psi_bell, 2, subsystem_size=1)
    assert abs(s_bell - 1.0) < 1e-12


def test_dataset_generation_and_hashing():
    # Generate grid over h in [0, 2] with J=1
    param_grid = {"h": np.linspace(0.0, 2.0, 11)}
    ds1 = generate_observable_dataset("ising", 2, param_grid)
    ds2 = generate_observable_dataset("ising", 2, param_grid)

    assert ds1.sha256_hash == ds2.sha256_hash
    assert len(ds1.features) == 11
    assert "energy" in ds1.targets
    assert "gap" in ds1.targets
    assert "mag_x" in ds1.targets
    assert "entropy" in ds1.targets

    # Check split partitioning
    splits = split_observable_dataset(
        ds1, "energy", train_fraction=0.6, val_fraction=0.2, extrap_fraction=0.2
    )
    assert "train" in splits
    assert "validation" in splits
    assert "extrapolation" in splits

    xs_train, _ys_train = splits["train"]
    xs_val, _ys_val = splits["validation"]
    xs_extrap, _ys_extrap = splits["extrapolation"]

    assert len(xs_train) + len(xs_val) + len(xs_extrap) == 11
    assert len(xs_train) > 0
    assert len(xs_extrap) > 0


def test_symbolic_rediscovery_quantum_scaling():
    # Target scaling relation: E_0(J) = -3 J (Heisenberg XXX for N=2)
    # Generate training data over J in [0.5, 4.0]
    param_grid = {"J": np.linspace(0.5, 4.0, 32)}
    ds = generate_observable_dataset("heisenberg", 2, param_grid, observables=["energy"])

    xs, ys = ds.to_arrays("energy")
    xs_train = xs.ravel().astype(np.float32)
    ys_train = ys.astype(np.float32)

    config = EvolutionConfig(
        pop_size=500,
        elite_k=16,
        max_generations=50,
        early_stop_fitness=1e-5,
    )
    rng = np.random.default_rng(0)
    res = run_evolution(xs_train, ys_train, config, rng)

    assert res["best_mse"] < 1e-4
    assert res["time_sec"] < 15.0
