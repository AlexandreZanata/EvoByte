"""Tests for Schrödinger residual fitness and staged evaluation (spec: Q10).

Validates residual scoring, boundary/normalization constraint penalties,
finite-difference Hamiltonian action, analytic sanity oracles, and
staged evolutionary rediscovery on solvable quantum systems.
"""

from __future__ import annotations

import numpy as np
import pytest

from evobyte.quantum.residual import (
    StrictnessStage,
    box_analytic_ground_state,
    box_potential,
    build_box_ground_program,
    build_qho_ground_program,
    compute_residual,
    evaluate_program_staged,
    hamiltonian_action,
    qho_analytic_ground_state,
    qho_potential,
    search_wavefunction_residual,
)


def test_qho_analytic_solution_scores_near_zero_residual():
    """Sanity oracle: exact QHO ground state scores ~0 residual across all stages."""
    xs = np.linspace(-4.0, 4.0, 256, dtype=np.float32)
    psi_exact, e_exact = qho_analytic_ground_state(xs, omega=1.0)
    pot = qho_potential(xs, omega=1.0)

    res = compute_residual(
        psi_exact,
        xs,
        pot,
        stage=StrictnessStage.STRICT,
        target_energy=e_exact,
        analytical_psi=psi_exact,
        analytical_e=e_exact,
    )

    assert res.is_valid
    assert res.residual_norm < 1e-4
    assert res.norm_error < 1e-5
    assert res.boundary_error < 1e-5
    assert res.total_loss < 1e-3
    assert abs(res.rayleigh_energy - 0.5) < 1e-4
    assert res.analytical_fidelity is not None
    assert abs(res.analytical_fidelity - 1.0) < 1e-6
    assert res.analytical_energy_error is not None
    assert res.analytical_energy_error < 1e-4


def test_box_analytic_solution_scores_near_zero_residual():
    """Sanity oracle: exact Particle in a Box ground state scores ~0 residual."""
    xs = np.linspace(0.0, np.pi, 256, dtype=np.float32)
    psi_exact, e_exact = box_analytic_ground_state(xs, length=np.pi)
    pot = box_potential(xs, length=np.pi)

    res = compute_residual(
        psi_exact,
        xs,
        pot,
        stage=StrictnessStage.STRICT,
        target_energy=e_exact,
        analytical_psi=psi_exact,
        analytical_e=e_exact,
    )

    assert res.is_valid
    assert res.residual_norm < 1e-3
    assert res.norm_error < 1e-5
    assert res.boundary_error < 1e-5
    assert res.total_loss < 1e-3
    assert abs(res.rayleigh_energy - 0.5) < 1e-4
    assert res.analytical_fidelity is not None
    assert abs(res.analytical_fidelity - 1.0) < 1e-6
    assert res.analytical_energy_error is not None
    assert res.analytical_energy_error < 1e-4


def test_hamiltonian_action_finite_difference_accuracy():
    """Verify 4th-order finite difference achieves high interior accuracy."""
    xs = np.linspace(-4.0, 4.0, 256, dtype=np.float64)
    psi, e0 = qho_analytic_ground_state(xs)
    pot = qho_potential(xs)

    h_psi = hamiltonian_action(psi, xs, pot, order=4)
    expected = e0 * psi

    interior_diff = np.abs(h_psi - expected)[4:-4]
    max_err = float(np.max(interior_diff))
    assert max_err < 1e-4


def test_bytecode_programs_staged_progression():
    """Verify deterministic bytecode programs advance cleanly across stages."""
    box_prog = build_box_ground_program()
    qho_prog = build_qho_ground_program()

    # Box program progression
    for stage in [StrictnessStage.FAST, StrictnessStage.DENSE, StrictnessStage.HIGH_PRECISION]:
        res = evaluate_program_staged(box_prog, "box", target_energy=0.5, max_stage=stage)
        assert res.is_valid
        assert res.residual_norm < 1e-2

    res_box_strict = evaluate_program_staged(box_prog, "box", target_energy=0.5, max_stage=StrictnessStage.STRICT)
    assert res_box_strict.is_valid
    assert res_box_strict.analytical_fidelity is not None
    assert abs(res_box_strict.analytical_fidelity - 1.0) < 1e-5

    # QHO program progression
    for stage in [StrictnessStage.FAST, StrictnessStage.DENSE, StrictnessStage.HIGH_PRECISION]:
        res = evaluate_program_staged(qho_prog, "qho", target_energy=0.5, max_stage=stage)
        assert res.is_valid
        assert res.residual_norm < 1e-2

    res_qho_strict = evaluate_program_staged(qho_prog, "qho", target_energy=0.5, max_stage=StrictnessStage.STRICT)
    assert res_qho_strict.is_valid
    assert res_qho_strict.analytical_fidelity is not None
    assert abs(res_qho_strict.analytical_fidelity - 1.0) < 1e-5


def test_invalid_wavefunction_rejection():
    """Verify non-finite or trivial zero states are rejected."""
    xs = np.linspace(0.0, np.pi, 32, dtype=np.float32)
    pot = box_potential(xs)

    # All-zero wavefunction
    psi_zero = np.zeros_like(xs)
    res_zero = compute_residual(psi_zero, xs, pot)
    assert not res_zero.is_valid
    assert res_zero.total_loss >= 1e6

    # Wavefunction containing NaN
    psi_nan = np.ones_like(xs)
    psi_nan[5] = np.nan
    res_nan = compute_residual(psi_nan, xs, pot)
    assert not res_nan.is_valid
    assert res_nan.total_loss >= 1e6


def test_boundary_error_penalty():
    """Verify that states violating Dirichlet boundary conditions receive penalties."""
    xs = np.linspace(0.0, np.pi, 128, dtype=np.float32)
    pot = box_potential(xs)

    # Flat state psi(x) = 1 does not vanish at x=0 or x=pi
    psi_flat = np.ones_like(xs)
    res_flat = compute_residual(psi_flat, xs, pot, w_bc=10.0)

    # Sine state psi(x) = sin(x) vanishes at boundaries
    psi_sin = np.sin(xs)
    res_sin = compute_residual(psi_sin, xs, pot, w_bc=10.0)

    assert res_flat.boundary_error > 0.5
    assert res_sin.boundary_error < 1e-10
    assert res_flat.total_loss > res_sin.total_loss


def test_evolutionary_rediscovery_box():
    """Task 3: staged rediscovery run on Particle in a Box."""
    res = search_wavefunction_residual(
        system_name="box",
        target_energy=0.5,
        pop_size=300,
        generations=20,
        seed=1,
        seed_templates=None,
    )
    assert res["residual_norm"] < 0.05
    assert res["fidelity"] is not None
    assert res["fidelity"] > 0.99


def test_evolutionary_rediscovery_qho():
    """Task 3: staged rediscovery run on Quantum Harmonic Oscillator."""
    res = search_wavefunction_residual(
        system_name="qho",
        target_energy=0.5,
        pop_size=200,
        generations=15,
        seed=0,
    )
    assert res["residual_norm"] < 0.05
    assert res["fidelity"] is not None
    assert res["fidelity"] > 0.99


def test_unknown_system_raises():
    """Verify unknown system raises ValueError."""
    prog = np.zeros(16, dtype=np.uint32)
    with pytest.raises(ValueError, match="unknown system"):
        evaluate_program_staged(prog, "unknown_system")
