"""Scaling verifier ladder, pre-registered hard targets, and bottleneck resolution (spec: Q13, docs/quantum/VERIFIER.md).

Addresses the Hilbert space exponential wall (N >= 8, 10, 12, 14) where dense
exact diagonalization becomes a memory and computational bottleneck.
Provides:
1. Matrix-free and sparse CSR Hamiltonian representations
2. Lanczos ground-state iterative solver
3. Subspace projection via symmetry reduction (Sz=0, parity)
4. Pre-registered hard target catalog with pre-declared thresholds
5. Mandatory outcome reporting (SUPPORTED, NULL, NEEDS_WORK), ensuring negative
   results are recorded with scientific integrity.

Exploratory pilot: known dimer seeds and reference-based early stopping are used.
This implementation does not satisfy a scoring-only oracle isolation protocol.
"""

from __future__ import annotations

import enum
import time
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import eigsh

from evobyte.quantum.hamiltonians import (
    PauliTerm,
    heisenberg,
    ising,
    j1j2,
)
from evobyte.quantum.pauli import PHASES


def _popcount_array(arr: np.ndarray) -> np.ndarray:
    """Vectorized bit count (popcount) across integer array."""
    if hasattr(np, "bitwise_count"):
        return np.bitwise_count(arr)
    # 32-bit parallel popcount fallback
    v = arr.astype(np.uint32)
    v = v - ((v >> 1) & 0x55555555)
    v = (v & 0x33333333) + ((v >> 2) & 0x33333333)
    return (((v + (v >> 4)) & 0x0F0F0F0F) * 0x01010101) >> 24


class VerifierTier(enum.Enum):
    """Hierarchy of verification tiers adapted to system scale."""

    FAST = "fast"
    DENSE = "dense"
    SPARSE_LANCZOS = "sparse_lanczos"
    SYMMETRY_REDUCED = "symmetry_reduced"


class OutcomeClass(enum.Enum):
    """Mandatory outcome classification per Q13 integrity rules."""

    SUPPORTED = "SUPPORTED"
    NULL = "NULL"
    NEEDS_WORK = "NEEDS_WORK"


@dataclass(frozen=True)
class HardTarget:
    """Pre-registered quantum system specification with fixed thresholds."""

    target_id: str
    model: str
    n_qubits: int
    params: dict[str, float]
    problem_type: str
    energy_tolerance: float
    fidelity_threshold: float
    max_evaluations: int
    wall_clock_timeout_sec: float
    symmetry_sector: str | None = None
    description: str = ""


# Pre-registered hard targets catalog (pre-declared before benchmark execution)
PREREGISTERED_TARGETS: dict[str, HardTarget] = {
    "T1_J1J2_MG_N6": HardTarget(
        target_id="T1_J1J2_MG_N6",
        model="j1j2",
        n_qubits=6,
        params={"j1": 1.0, "j2": 0.5},
        problem_type="ground_state",
        energy_tolerance=1e-3,
        fidelity_threshold=0.98,
        max_evaluations=3000,
        wall_clock_timeout_sec=5.0,
        symmetry_sector="sz=0",
        description="N=6 J1-J2 chain at Majumdar-Ghosh point (exact dimer ground state E0=-9.0)",
    ),
    "T2_J1J2_MG_N8": HardTarget(
        target_id="T2_J1J2_MG_N8",
        model="j1j2",
        n_qubits=8,
        params={"j1": 1.0, "j2": 0.5},
        problem_type="ground_state",
        energy_tolerance=1e-3,
        fidelity_threshold=0.98,
        max_evaluations=5000,
        wall_clock_timeout_sec=8.0,
        symmetry_sector="sz=0",
        description="N=8 J1-J2 chain at Majumdar-Ghosh point (exact dimer ground state E0=-12.0)",
    ),
    "T3_J1J2_MG_N10": HardTarget(
        target_id="T3_J1J2_MG_N10",
        model="j1j2",
        n_qubits=10,
        params={"j1": 1.0, "j2": 0.5},
        problem_type="ground_state",
        energy_tolerance=1e-3,
        fidelity_threshold=0.95,
        max_evaluations=8000,
        wall_clock_timeout_sec=12.0,
        symmetry_sector="sz=0",
        description="N=10 J1-J2 chain beyond dense N=8 limit (dimer ground state E0=-15.0)",
    ),
    "T4_ISING_CRIT_N8": HardTarget(
        target_id="T4_ISING_CRIT_N8",
        model="ising",
        n_qubits=8,
        params={"j": 1.0, "h": 1.0},
        problem_type="ground_state",
        energy_tolerance=5e-3,
        fidelity_threshold=0.90,
        max_evaluations=5000,
        wall_clock_timeout_sec=8.0,
        symmetry_sector="parity=+1",
        description="N=8 Critical Transverse-Field Ising chain (quantum critical point h/J=1)",
    ),
    "T5_HEISENBERG_N10": HardTarget(
        target_id="T5_HEISENBERG_N10",
        model="heisenberg",
        n_qubits=10,
        params={"j": 1.0},
        problem_type="ground_state",
        energy_tolerance=1e-2,
        fidelity_threshold=0.85,
        max_evaluations=6000,
        wall_clock_timeout_sec=10.0,
        symmetry_sector="sz=0",
        description="N=10 Isotropic Heisenberg XXX chain (Bethe ansatz regime)",
    ),
    "T6_UNSOLVED_FRUST_N12": HardTarget(
        target_id="T6_UNSOLVED_FRUST_N12",
        model="j1j2",
        n_qubits=12,
        params={"j1": 1.0, "j2": 0.75},
        problem_type="ground_state",
        energy_tolerance=1e-4,  # Intentionally stringent tolerance to test NULL outcome reporting
        fidelity_threshold=0.99,
        max_evaluations=1500,  # Historical budget for the negative-reporting test
        wall_clock_timeout_sec=5.0,
        symmetry_sector="sz=0",
        description="N=12 Non-dimer frustrated regime under tight budget (tests negative result reporting)",
    ),
}


@dataclass(frozen=True)
class TargetEvaluationResult:
    """Audit record and outcome report for a pre-registered hard target."""

    target_id: str
    outcome: OutcomeClass
    n_qubits: int
    model: str
    hilbert_dim: int
    evaluations: int
    wall_clock_sec: float
    discovered_energy: float
    reference_energy: float
    energy_error: float
    fidelity: float | None
    verifier_tier: VerifierTier
    reproduction_cmd: str
    details: dict[str, Any] = field(default_factory=dict)


def get_target_hamiltonian(target: HardTarget) -> list[PauliTerm]:
    """Instantiate Hamiltonian term list for a given target."""
    n = target.n_qubits
    if target.model == "j1j2":
        return j1j2(n, j1=target.params["j1"], j2=target.params["j2"])
    elif target.model == "ising":
        return ising(n, j=target.params["j"], h=target.params["h"])
    elif target.model == "heisenberg":
        return heisenberg(n, j=target.params["j"])
    else:
        raise ValueError(f"Unknown model: {target.model}")


def build_sparse_hamiltonian(terms: list[PauliTerm], n_qubits: int) -> csr_matrix:
    """Assemble sparse CSR Hamiltonian matrix in O(M * 2^N) memory and time."""
    dim = 1 << n_qubits
    k = np.arange(dim, dtype=np.uint32)

    rows_list = []
    cols_list = []
    data_list = []

    for t in terms:
        x = t.x_mask
        z = t.z_mask
        ph = t.phase
        c = t.coeff

        row = k ^ x
        col = k

        bc = _popcount_array(k & z)
        signs = 1.0 - 2.0 * (bc & 1)
        vals = (c * PHASES[ph % 4]) * signs

        rows_list.append(row)
        cols_list.append(col)
        data_list.append(vals)

    all_rows = np.concatenate(rows_list)
    all_cols = np.concatenate(cols_list)
    all_data = np.concatenate(data_list)

    return csr_matrix((all_data, (all_rows, all_cols)), shape=(dim, dim))


def hamiltonian_matvec(terms: list[PauliTerm], psi: np.ndarray, n_qubits: int) -> np.ndarray:
    """Matrix-free Hamiltonian-vector multiplication H @ psi."""
    dim = 1 << n_qubits
    out = np.zeros(dim, dtype=np.complex128)
    k = np.arange(dim, dtype=np.uint32)

    for t in terms:
        x = t.x_mask
        z = t.z_mask
        ph = t.phase
        c = t.coeff

        bc = _popcount_array(k & z)
        signs = 1.0 - 2.0 * (bc & 1)
        vals = (c * PHASES[ph % 4]) * signs

        # out[k ^ x] += vals * psi[k]
        np.add.at(out, k ^ x, vals * psi)

    return out


def lanczos_ground_state(
    terms: list[PauliTerm],
    n_qubits: int,
    max_iter: int = 150,
    tol: float = 1e-10,
    seed: int = 42,
) -> tuple[float, np.ndarray]:
    """Compute ground state energy and statevector using Lanczos iteration."""
    dim = 1 << n_qubits
    H_sparse = build_sparse_hamiltonian(terms, n_qubits)

    # Use scipy ARPACK eigsh for robust extremal eigenvalue calculation
    v0 = np.random.default_rng(seed).normal(size=dim)
    evals, evecs = eigsh(H_sparse, k=1, which="SA", tol=tol, maxiter=max_iter * 10, v0=v0)
    e0 = float(np.real(evals[0]))
    psi0 = evecs[:, 0]
    # Phase convention: make largest component real and positive
    max_idx = int(np.argmax(np.abs(psi0)))
    phase_factor = psi0[max_idx] / abs(psi0[max_idx]) if abs(psi0[max_idx]) > 1e-12 else 1.0
    psi0 = psi0 / phase_factor
    return e0, psi0


def symmetry_reduced_ground_state(
    terms: list[PauliTerm],
    n_qubits: int,
    sector: str = "sz=0",
    seed: int = 42,
) -> tuple[float, np.ndarray, np.ndarray]:
    """Compute exact ground state within symmetry-reduced subspace.

    Returns:
        (E0, psi0_full_basis, subspace_basis_indices)
    """
    dim = 1 << n_qubits
    k = np.arange(dim, dtype=np.uint32)

    if sector == "sz=0":
        sub_basis = k[_popcount_array(k) == (n_qubits // 2)]
    else:
        raise ValueError(f"Unsupported symmetry sector: {sector}")

    sub_dim = len(sub_basis)
    idx_map = {int(b): i for i, b in enumerate(sub_basis)}

    # Keep the projection sparse: only its lowest eigenpair is needed.
    rows: list[int] = []
    cols: list[int] = []
    values: list[complex] = []
    for t in terms:
        x = t.x_mask
        z = t.z_mask
        ph = t.phase
        c = t.coeff
        phase_factor = c * PHASES[ph % 4]

        for j_sub, col in enumerate(sub_basis):
            row = col ^ x
            row_int = int(row)
            if row_int in idx_map:
                i_sub = idx_map[row_int]
                sign = 1.0 - 2.0 * (((col & z).bit_count()) & 1)
                rows.append(i_sub)
                cols.append(j_sub)
                values.append(phase_factor * sign)

    H_sub = csr_matrix((values, (rows, cols)), shape=(sub_dim, sub_dim))
    if sub_dim <= 2:
        evals, evecs = np.linalg.eigh(H_sub.toarray())
    else:
        v0 = np.random.default_rng(seed).normal(size=sub_dim)
        evals, evecs = eigsh(H_sub, k=1, which="SA", tol=1e-10, v0=v0)
    e0 = float(np.real(evals[0]))
    psi_sub = evecs[:, 0]

    # Lift subspace state back to full 2^N Hilbert space
    psi_full = np.zeros(dim, dtype=np.complex128)
    for i_sub, b in enumerate(sub_basis):
        psi_full[b] = psi_sub[i_sub]

    return e0, psi_full, sub_basis


def ansatz_energy_fast(
    terms: list[PauliTerm],
    ansatz_terms: Sequence[tuple[float, int, int]],
) -> float:
    """Rayleigh quotient <psi|H|psi> evaluated in O(K * M) bitwise operations.

    Args:
        terms: List of PauliTerm Hamiltonian definitions.
        ansatz_terms: Sequence of (coeff, basis_mask, phase_idx).
    """
    mask_to_unnorm: dict[int, complex] = {}
    for c, m, p in ansatz_terms:
        val = c * PHASES[p % 4]
        mask_to_unnorm[m] = mask_to_unnorm.get(m, 0.0 + 0.0j) + val

    tot_norm_sq = sum(abs(v) ** 2 for v in mask_to_unnorm.values())
    if tot_norm_sq < 1e-14:
        return 1e6

    norm = np.sqrt(tot_norm_sq)
    mask_to_val: dict[int, complex] = {m: v / norm for m, v in mask_to_unnorm.items()}

    exp_val = 0.0
    for t in terms:
        c_t = t.coeff
        x_t = t.x_mask
        z_t = t.z_mask
        ph_t = t.phase
        term_factor = c_t * PHASES[ph_t % 4]

        for m_b, val_b in mask_to_val.items():
            m_a = m_b ^ x_t
            if m_a in mask_to_val:
                val_a = mask_to_val[m_a]
                sign = 1.0 - 2.0 * (((m_b & z_t).bit_count()) & 1)
                matrix_el = term_factor * sign
                exp_val += np.real(np.conj(val_a) * matrix_el * val_b)

    return float(exp_val)


def build_dimer_product_ansatz(n_qubits: int) -> list[tuple[float, int, int]]:
    """Construct exact Majumdar-Ghosh dimer product state: |s_01> (x) |s_23> ..."""
    pairs = [(2 * k, 2 * k + 1) for k in range(n_qubits // 2)]
    terms = [(1.0, 0, 0)]  # (coeff, mask, phase)
    for i, j in pairs:
        new_terms = []
        for c, m, p in terms:
            # bit i=1, bit j=0 -> (1 << i)
            new_terms.append((float(c), m | (1 << i), p % 4))
            # bit i=0, bit j=1 -> (1 << j) with relative sign -1
            new_terms.append((float(-c), m | (1 << j), p % 4))
        terms = new_terms
    return terms


def run_hard_target_search(
    target: HardTarget,
    seed: int = 42,
) -> TargetEvaluationResult:
    """Execute the configured pilot with known seeds and reference-based stopping."""
    rng = np.random.default_rng(seed)
    t0 = time.perf_counter()

    h_terms = get_target_hamiltonian(target)
    n = target.n_qubits
    dim = 1 << n

    # Step 1: Pre-compute reference ground state using appropriate verifier tier
    # Reference energies also control early stopping below; this is a pilot.
    if target.symmetry_sector == "sz=0" and n >= 6:
        e_ref, psi_ref, _ = symmetry_reduced_ground_state(h_terms, n, sector="sz=0", seed=seed)
        tier = VerifierTier.SYMMETRY_REDUCED
    elif n >= 8:
        e_ref, psi_ref = lanczos_ground_state(h_terms, n, seed=seed)
        tier = VerifierTier.SPARSE_LANCZOS
    else:
        e_ref, psi_ref = lanczos_ground_state(h_terms, n, seed=seed)
        tier = VerifierTier.FAST

    # Step 2: Search algorithm, including the known dimer motif where applicable
    best_energy = float("inf")
    best_ansatz: list[tuple[float, int, int]] = []
    evals = 0

    # Initialize population of candidates
    pop: list[list[tuple[float, int, int]]] = []

    # If model is J1-J2, include dimer motif among candidates
    if target.model == "j1j2":
        pop.append(build_dimer_product_ansatz(n))

    # Random superposition candidates
    while len(pop) < 40:
        n_terms = int(rng.integers(2, min(16, dim)))
        masks = rng.choice(dim, size=n_terms, replace=False)
        cand = [
            (float(rng.choice([1.0, -1.0, 0.5, -0.5])), int(m), int(rng.integers(0, 4)))
            for m in masks
        ]
        pop.append(cand)

    # Evolution loop respecting budget and wall-clock timeout
    while evals < target.max_evaluations:
        if (time.perf_counter() - t0) >= target.wall_clock_timeout_sec:
            break

        scored = []
        for cand in pop:
            if evals >= target.max_evaluations:
                break
            evals += 1
            e_val = ansatz_energy_fast(h_terms, cand)
            scored.append((e_val, cand))
            if e_val < best_energy:
                best_energy = e_val
                best_ansatz = cand

            if abs(best_energy - e_ref) <= target.energy_tolerance:
                break

        if abs(best_energy - e_ref) <= target.energy_tolerance:
            break

        # Selection and mutation
        scored.sort(key=lambda x: x[0])
        elites = [c for _, c in scored[:10]]
        new_pop = list(elites)

        while len(new_pop) < len(pop):
            parent = elites[rng.integers(0, len(elites))]
            child = []
            for c, m, p in parent:
                # Mutate bitstring
                new_m = m
                for q in range(n):
                    if rng.random() < 0.15:
                        new_m ^= 1 << q
                # Mutate coeff
                new_c = c * float(rng.choice([1.0, -1.0, 0.5, 2.0])) if rng.random() < 0.2 else c
                # Mutate phase
                new_p = (p + int(rng.integers(0, 4))) % 4 if rng.random() < 0.1 else p
                child.append((new_c, new_m % dim, new_p))
            new_pop.append(child)

        pop = new_pop

    dt = time.perf_counter() - t0
    energy_err = abs(best_energy - e_ref)

    # Reconstruct statevector for fidelity post-hoc scoring
    cand_vec = np.zeros(dim, dtype=np.complex128)
    for c, m, p in best_ansatz:
        cand_vec[m] += c * PHASES[p % 4]
    norm_val = np.linalg.norm(cand_vec)
    if norm_val > 1e-14:
        cand_vec = cand_vec / norm_val
        fid = float(abs(np.vdot(psi_ref, cand_vec)) ** 2)
    else:
        fid = 0.0

    # Determine pre-registered outcome classification
    if evals == 0 or not np.isfinite(best_energy):
        outcome = OutcomeClass.NEEDS_WORK
    elif energy_err <= target.energy_tolerance and (
        fid >= target.fidelity_threshold or target.fidelity_threshold <= 0.0
    ):
        outcome = OutcomeClass.SUPPORTED
    elif evals >= target.max_evaluations or dt >= target.wall_clock_timeout_sec:
        outcome = OutcomeClass.NULL
    else:
        outcome = OutcomeClass.NEEDS_WORK

    repro_cmd = (
        f"python3 benchmarks/qforge_hard_matrix.py --targets {target.target_id} --seed {seed}"
    )

    return TargetEvaluationResult(
        target_id=target.target_id,
        outcome=outcome,
        n_qubits=n,
        model=target.model,
        hilbert_dim=dim,
        evaluations=evals,
        wall_clock_sec=dt,
        discovered_energy=best_energy,
        reference_energy=e_ref,
        energy_error=energy_err,
        fidelity=fid,
        verifier_tier=tier,
        reproduction_cmd=repro_cmd,
        details={
            "seed": seed,
            "seeded_known_ansatz": target.model == "j1j2",
            "reference_used_for_early_stop": True,
            "research_acceptance": "provisional",
            "description": target.description,
            "target_energy_tolerance": target.energy_tolerance,
            "target_fidelity_threshold": target.fidelity_threshold,
            "best_ansatz_term_count": len(best_ansatz),
        },
    )
