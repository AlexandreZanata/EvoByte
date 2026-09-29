"""Schrödinger residual search and staged evaluation (spec: Q10).

Evolves wavefunctions scored by the stationary Schrödinger residual
||Hψ - Eψ|| + normalization_error + boundary_error + complexity_penalty
under a staged fast -> dense -> high-precision -> strict doctrine.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import IntEnum
from typing import Any, Callable, Sequence

import numpy as np

from evobyte.bytecode import OPCODES, decode_human, encode_instr
from evobyte.evolution import EvolutionConfig, mutate_candidate, sample_structured
from evobyte.vm import execute_batch


class StrictnessStage(IntEnum):
    """Evaluation stages per Q10 doctrine."""

    FAST = 1           # Coarse grid (32 pts), 2nd-order FD, early rejection
    DENSE = 2          # Dense grid (128 pts), 4th-order FD, boundary verification
    HIGH_PRECISION = 3 # High-precision grid (256 pts), 4th-order FD, fine integration
    STRICT = 4         # Oracle verification: exact analytical comparison


@dataclass(frozen=True)
class ResidualResult:
    """Detailed evaluation metrics for Schrödinger residual."""

    stage: StrictnessStage
    residual_norm: float
    rayleigh_energy: float
    norm_error: float
    boundary_error: float
    complexity: float
    total_loss: float
    is_valid: bool
    target_energy: float | None = None
    analytical_fidelity: float | None = None
    analytical_energy_error: float | None = None


# -----------------------------------------------------------------------------
# Solvable Potentials & Analytic Sanity Solutions
# -----------------------------------------------------------------------------

def qho_potential(xs: np.ndarray, omega: float = 1.0) -> np.ndarray:
    """Harmonic oscillator potential V(x) = 0.5 * omega^2 * x^2."""
    return 0.5 * (omega**2) * (xs**2)


def box_potential(xs: np.ndarray, length: float = np.pi) -> np.ndarray:
    """Infinite square well potential V(x) = 0 on (0, length)."""
    return np.zeros_like(xs)


def qho_analytic_ground_state(xs: np.ndarray, omega: float = 1.0) -> tuple[np.ndarray, float]:
    """Analytical ground state psi_0(x) = (omega/pi)^(1/4) * exp(-0.5 * omega * x^2), E_0 = 0.5 * omega."""
    prefactor = (omega / np.pi) ** 0.25
    psi = prefactor * np.exp(-0.5 * omega * (xs**2))
    return psi, 0.5 * omega


def box_analytic_ground_state(xs: np.ndarray, length: float = np.pi) -> tuple[np.ndarray, float]:
    """Analytical ground state psi_1(x) = sqrt(2/L) * sin(pi * x / L), E_1 = pi^2 / (2 * L^2)."""
    psi = np.sqrt(2.0 / length) * np.sin(np.pi * xs / length)
    e_0 = (np.pi**2) / (2.0 * (length**2))
    return psi, float(e_0)


def build_qho_ground_program() -> np.ndarray:
    """Construct deterministic EvoByte bytecode program computing exp(-0.5 * x^2)."""
    prog = np.zeros(16, dtype=np.uint32)
    # r1 = r0 * r0 (x^2)
    prog[0] = encode_instr(0x03, 1, 0, 0)
    # r2 = r6 + const_bank[9] (where r6 is 0.0 initially, const_bank[9] = -0.5)
    prog[1] = encode_instr(0x0F, 2, 6, 9)
    # r3 = r1 * r2 (-0.5 * x^2)
    prog[2] = encode_instr(0x03, 3, 1, 2)
    # r7 = exp(r3)
    prog[3] = encode_instr(0x07, 7, 3, 0)
    return prog


def build_box_ground_program(length: float = np.pi) -> np.ndarray:
    """Construct deterministic EvoByte bytecode program computing sin(x) for L=pi."""
    prog = np.zeros(16, dtype=np.uint32)
    # r7 = sin(r0)
    prog[0] = encode_instr(0x05, 7, 0, 0)
    return prog


# -----------------------------------------------------------------------------
# Hamiltonian Action and Finite Difference
# -----------------------------------------------------------------------------

def hamiltonian_action(
    psi: np.ndarray,
    xs: np.ndarray,
    potential: np.ndarray,
    order: int = 4,
    mass: float = 1.0,
) -> np.ndarray:
    """Compute H psi = -(1 / 2m) d^2 psi / dx^2 + V(x) psi via finite differences."""
    n = len(xs)
    dx = float(xs[1] - xs[0])
    d2 = np.zeros_like(psi)

    if order >= 4 and n >= 5:
        # 4th-order central difference interior
        dx2_12 = 12.0 * (dx**2)
        d2[2:-2] = (-psi[4:] + 16.0 * psi[3:-1] - 30.0 * psi[2:-2] + 16.0 * psi[1:-3] - psi[:-4]) / dx2_12
        # 2nd-order boundary layers
        dx2 = dx**2
        d2[1] = (psi[2] - 2.0 * psi[1] + psi[0]) / dx2
        d2[-2] = (psi[-1] - 2.0 * psi[-2] + psi[-3]) / dx2
        d2[0] = (-2.0 * psi[0] + psi[1]) / dx2
        d2[-1] = (-2.0 * psi[-1] + psi[-2]) / dx2
    else:
        # 2nd-order central difference
        dx2 = dx**2
        d2[1:-1] = (psi[2:] - 2.0 * psi[1:-1] + psi[:-2]) / dx2
        d2[0] = (-2.0 * psi[0] + psi[1]) / dx2
        d2[-1] = (-2.0 * psi[-1] + psi[-2]) / dx2

    kinetic = -(0.5 / mass) * d2
    return kinetic + potential * psi


# -----------------------------------------------------------------------------
# Schrödinger Residual Evaluation
# -----------------------------------------------------------------------------

def compute_residual(
    psi: np.ndarray,
    xs: np.ndarray,
    potential: np.ndarray,
    stage: StrictnessStage = StrictnessStage.DENSE,
    target_energy: float | None = None,
    w_norm: float = 0.05,
    w_bc: float = 10.0,
    complexity_val: float = 0.0,
    w_comp: float = 1e-4,
    analytical_psi: np.ndarray | None = None,
    analytical_e: float | None = None,
) -> ResidualResult:
    """Compute stationary Schrödinger residual ||Hψ - Eψ|| + boundary/norm penalties."""
    dx = float(xs[1] - xs[0])
    raw_norm_sq = float(np.sum(psi**2) * dx)

    # Rejection of trivial zero, flat, or non-finite wavefunctions
    if not np.all(np.isfinite(psi)) or raw_norm_sq < 1e-12:
        return ResidualResult(
            stage=stage,
            residual_norm=1e6,
            rayleigh_energy=1e6,
            norm_error=1.0,
            boundary_error=1e6,
            complexity=complexity_val,
            total_loss=1e6,
            is_valid=False,
            target_energy=target_energy,
        )

    # Normalized wavefunction for scale-invariant residual
    norm = np.sqrt(raw_norm_sq)
    psi_norm = psi / norm

    # Hamiltonian action
    order = 4 if stage in (StrictnessStage.DENSE, StrictnessStage.HIGH_PRECISION, StrictnessStage.STRICT) else 2
    h_psi = hamiltonian_action(psi_norm, xs, potential, order=order)

    # Rayleigh quotient expectation <psi|H|psi>
    e_rayleigh = float(np.sum(psi_norm * h_psi) * dx)
    e_eval = target_energy if target_energy is not None else e_rayleigh

    # Residual vector: (H - E) psi evaluated on interior points
    diff = (h_psi - e_eval * psi_norm)[1:-1]
    res_norm = float(np.sqrt(np.sum(diff**2) * dx))

    # Boundary conditions: psi at endpoints should vanish for bound states
    boundary_error = float(psi_norm[0] ** 2 + psi_norm[-1] ** 2)

    # Norm constraint penalty (drives unscaled raw program toward unit norm)
    norm_error = float(abs(raw_norm_sq - 1.0))

    total_loss = res_norm + w_norm * norm_error + w_bc * boundary_error + w_comp * complexity_val

    # Optional analytical comparison
    fid: float | None = None
    e_err: float | None = None
    if analytical_psi is not None and analytical_e is not None:
        ana_norm = analytical_psi / np.sqrt(np.sum(analytical_psi**2) * dx)
        overlap = float(abs(np.sum(psi_norm * ana_norm) * dx))
        fid = float(np.clip(overlap**2, 0.0, 1.0))
        e_err = float(abs(e_rayleigh - analytical_e))

    return ResidualResult(
        stage=stage,
        residual_norm=res_norm,
        rayleigh_energy=e_rayleigh,
        norm_error=norm_error,
        boundary_error=boundary_error,
        complexity=complexity_val,
        total_loss=total_loss,
        is_valid=True,
        target_energy=target_energy,
        analytical_fidelity=fid,
        analytical_energy_error=e_err,
    )


# -----------------------------------------------------------------------------
# Staged Evaluator & Search Loop
# -----------------------------------------------------------------------------

def evaluate_program_staged(
    program: np.ndarray,
    system_name: str,
    target_energy: float | None = None,
    max_stage: StrictnessStage = StrictnessStage.STRICT,
    w_norm: float = 0.05,
    w_bc: float = 10.0,
    w_comp: float = 1e-4,
) -> ResidualResult:
    """Evaluate a single EvoByte program across staged strictness levels."""
    # Define grid parameters per system
    if system_name == "qho":
        x_min, x_max = -4.0, 4.0
        potential_fn = qho_potential
        analytic_fn = qho_analytic_ground_state
    elif system_name == "box":
        x_min, x_max = 0.0, np.pi
        potential_fn = box_potential
        analytic_fn = box_analytic_ground_state
    else:
        raise ValueError(f"unknown system: {system_name}")

    comp = float(sum((int(w) & 0xFF) != 0 for w in program))

    # Stage 1: Fast (32 points)
    xs_fast = np.linspace(x_min, x_max, 32, dtype=np.float32)
    preds_fast, invalid_fast = execute_batch(program, xs_fast)
    if invalid_fast.any():
        return ResidualResult(
            stage=StrictnessStage.FAST,
            residual_norm=1e6,
            rayleigh_energy=1e6,
            norm_error=1.0,
            boundary_error=1e6,
            complexity=comp,
            total_loss=1e6,
            is_valid=False,
        )

    res_fast = compute_residual(
        preds_fast, xs_fast, potential_fn(xs_fast),
        stage=StrictnessStage.FAST,
        target_energy=target_energy,
        w_norm=w_norm,
        w_bc=w_bc,
        complexity_val=comp,
        w_comp=w_comp,
    )
    if max_stage == StrictnessStage.FAST or not res_fast.is_valid or res_fast.total_loss > 50.0:
        return res_fast

    # Stage 2: Dense (128 points)
    xs_dense = np.linspace(x_min, x_max, 128, dtype=np.float32)
    preds_dense, invalid_dense = execute_batch(program, xs_dense)
    if invalid_dense.any():
        return ResidualResult(
            stage=StrictnessStage.DENSE,
            residual_norm=1e6,
            rayleigh_energy=1e6,
            norm_error=1.0,
            boundary_error=1e6,
            complexity=comp,
            total_loss=1e6,
            is_valid=False,
        )

    res_dense = compute_residual(
        preds_dense, xs_dense, potential_fn(xs_dense),
        stage=StrictnessStage.DENSE,
        target_energy=target_energy,
        w_norm=w_norm,
        w_bc=w_bc,
        complexity_val=comp,
        w_comp=w_comp,
    )
    if max_stage == StrictnessStage.DENSE or not res_dense.is_valid or res_dense.total_loss > 10.0:
        return res_dense

    # Stage 3: High Precision (256 points)
    xs_hp = np.linspace(x_min, x_max, 256, dtype=np.float32)
    preds_hp, invalid_hp = execute_batch(program, xs_hp)
    if invalid_hp.any():
        return ResidualResult(
            stage=StrictnessStage.HIGH_PRECISION,
            residual_norm=1e6,
            rayleigh_energy=1e6,
            norm_error=1.0,
            boundary_error=1e6,
            complexity=comp,
            total_loss=1e6,
            is_valid=False,
        )

    res_hp = compute_residual(
        preds_hp, xs_hp, potential_fn(xs_hp),
        stage=StrictnessStage.HIGH_PRECISION,
        target_energy=target_energy,
        w_norm=w_norm,
        w_bc=w_bc,
        complexity_val=comp,
        w_comp=w_comp,
    )
    if max_stage == StrictnessStage.HIGH_PRECISION or not res_hp.is_valid:
        return res_hp

    # Stage 4: Strict (Golden oracle comparison)
    ana_psi, ana_e = analytic_fn(xs_hp)
    return compute_residual(
        preds_hp, xs_hp, potential_fn(xs_hp),
        stage=StrictnessStage.STRICT,
        target_energy=target_energy,
        w_norm=w_norm,
        w_bc=w_bc,
        complexity_val=comp,
        w_comp=w_comp,
        analytical_psi=ana_psi,
        analytical_e=ana_e,
    )


def search_wavefunction_residual(
    system_name: str,
    target_energy: float | None = None,
    pop_size: int = 200,
    generations: int = 40,
    seed: int = 0,
    early_stop_residual: float = 0.05,
    seed_templates: Sequence[np.ndarray] | None = None,
) -> dict[str, Any]:
    """Evolve wavefunction programs scored by Schrödinger residual under staged doctrine."""
    from evobyte.evolution import step_generation

    rng = np.random.default_rng(seed)

    # 1. Initialize population
    pop_list: list[np.ndarray] = []
    if seed_templates is not None:
        for t in seed_templates:
            pop_list.append(t.copy())
    elif system_name == "qho":
        pop_list.append(build_qho_ground_program())

    while len(pop_list) < pop_size:
        pop_list.append(sample_structured(rng))

    population = np.stack(pop_list)
    config = EvolutionConfig(
        pop_size=pop_size,
        elite_k=max(2, int(pop_size * 0.08)),
        tournament_size=4,
        crossover_p=0.4,
        gene_mut_p=0.12,
        large_mut_p=0.08,
        point_mut_p=0.02,
        random_inject_p=0.15,
        max_generations=generations,
    )

    t0 = time.perf_counter()
    best_prog = population[0].copy()
    best_score = float("inf")
    best_gen = 0
    total_evals = 0

    for gen in range(generations):
        scores_list = []
        for prog in population:
            total_evals += 1
            res_fast = evaluate_program_staged(
                prog, system_name, target_energy, max_stage=StrictnessStage.FAST
            )
            scores_list.append(res_fast.total_loss)

        scores = np.array(scores_list, dtype=np.float64)
        min_idx = int(np.argmin(scores))

        if scores[min_idx] < best_score:
            best_score = float(scores[min_idx])
            best_prog = population[min_idx].copy()
            best_gen = gen

        # Early exit check at dense stage
        dense_res = evaluate_program_staged(
            best_prog, system_name, target_energy, max_stage=StrictnessStage.DENSE
        )
        if dense_res.residual_norm <= early_stop_residual and dense_res.boundary_error <= 0.05:
            break

        # Advance population using step_generation
        population = step_generation(population, scores, config, rng)

    dt = max(time.perf_counter() - t0, 1e-9)

    # Final Strict Evaluation on best discovered program
    final_strict = evaluate_program_staged(best_prog, system_name, target_energy, max_stage=StrictnessStage.STRICT)

    return {
        "best_program": best_prog,
        "best_expression": decode_human(best_prog),
        "result": final_strict,
        "residual_norm": final_strict.residual_norm,
        "energy": final_strict.rayleigh_energy,
        "fidelity": final_strict.analytical_fidelity,
        "energy_error": final_strict.analytical_energy_error,
        "generations_run": gen + 1,
        "evaluations": total_evals,
        "elapsed_s": dt,
        "system": system_name,
        "seed": seed,
    }
