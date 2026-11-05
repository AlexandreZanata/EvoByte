"""Ground-state candidate search (spec: docs/quantum/ROADMAP.md, Q06 scope).

Compact bitmask-defined trial state ansatz, variational energy fitness E(ψ),
and evolutionary optimization scored strictly by energy expectation.
Fidelity and E_exact are computed post-hoc for verification and never for selection.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import numpy as np

from evobyte.quantum.hamiltonians import PauliTerm, to_hamiltonian_matrix
from evobyte.quantum.pauli import PHASES

COEFF_BANK = (1.0, -1.0, 0.5, -0.5, 0.70710678, -0.70710678, 2.0, -2.0)
COMPLEXITY_W = 1e-4


@dataclass(frozen=True)
class AnsatzTerm:
    """One term in a superposition ansatz: coeff * PHASES[phase_idx] * |basis_mask>."""

    coeff: float
    basis_mask: int
    phase_idx: int = 0


def encode_ansatz(terms: list[AnsatzTerm]) -> list[tuple[float, int, int]]:
    """Serialize ansatz into (coeff, basis_mask, phase_idx) tuples."""
    return [(t.coeff, t.basis_mask, t.phase_idx % 4) for t in terms]


def decode_ansatz(encoded: list[tuple[float, int, int]], n_qubits: int) -> list[AnsatzTerm]:
    """Deserialize tuples into AnsatzTerm list with boundary checks."""
    dim = 1 << n_qubits
    terms = []
    for coeff, mask, phase in encoded:
        if mask < 0 or mask >= dim:
            raise ValueError(f"basis_mask {mask} out of range [0, {dim}) for n={n_qubits}")
        terms.append(AnsatzTerm(float(coeff), mask, phase % 4))
    return terms


def to_statevector(terms: list[AnsatzTerm], n_qubits: int) -> np.ndarray:
    """Construct normalized complex 2^N statevector from ansatz terms."""
    dim = 1 << n_qubits
    vec = np.zeros(dim, dtype=np.complex128)
    for t in terms:
        if 0 <= t.basis_mask < dim:
            vec[t.basis_mask] += t.coeff * PHASES[t.phase_idx % 4]
    norm = float(np.linalg.norm(vec))
    if norm < 1e-14:
        # Fallback to uniform normalized state
        return np.ones(dim, dtype=np.complex128) / np.sqrt(dim)
    return vec / norm


def energy_fitness(h_dense: np.ndarray, statevector: np.ndarray) -> float:
    """Variational Rayleigh quotient <psi|H|psi> for normalized state."""
    norm = float(np.linalg.norm(statevector))
    if norm < 1e-14:
        return 1e6
    psi = statevector / norm
    return float(np.real(np.vdot(psi, h_dense @ psi)))


def sample_ansatz_term(rng: np.random.Generator, n_qubits: int) -> AnsatzTerm:
    """Sample random ansatz term with bitmask in [0, 2^N - 1]."""
    mask = int(rng.integers(0, 1 << n_qubits))
    coeff = float(rng.choice(COEFF_BANK))
    phase = int(rng.integers(0, 4))
    return AnsatzTerm(coeff, mask, phase)


def sample_ansatz(rng: np.random.Generator, n_qubits: int, n_terms: int = 4) -> list[AnsatzTerm]:
    """Sample candidate ansatz with unique basis bitstrings."""
    dim = 1 << n_qubits
    actual_terms = min(n_terms, dim)
    masks = rng.choice(dim, size=actual_terms, replace=False)
    terms = []
    for m in masks:
        coeff = float(rng.choice(COEFF_BANK))
        phase = int(rng.integers(0, 4))
        terms.append(AnsatzTerm(coeff, int(m), phase))
    return terms


def mutate_ansatz(
    cand: list[AnsatzTerm], n_qubits: int, rng: np.random.Generator, p_bit: float = 0.3
) -> list[AnsatzTerm]:
    """Mutate basis bitstrings and coefficients of candidate ansatz."""
    dim = 1 << n_qubits
    res = []
    for t in cand:
        mask = t.basis_mask
        coeff = t.coeff
        phase = t.phase_idx

        # 1. Flip bit in basis bitstring
        for q in range(n_qubits):
            if rng.random() < p_bit:
                mask ^= 1 << q

        # 2. Mutate coefficient
        if rng.random() < 0.3:
            coeff = float(rng.choice(COEFF_BANK))

        # 3. Mutate phase
        if rng.random() < 0.2:
            phase = int(rng.integers(0, 4))

        res.append(AnsatzTerm(coeff, mask % dim, phase % 4))
    return res


def crossover_ansatz(
    parent_a: list[AnsatzTerm], parent_b: list[AnsatzTerm], rng: np.random.Generator
) -> tuple[list[AnsatzTerm], list[AnsatzTerm]]:
    """Recombine basis terms between two trial state candidates."""
    if len(parent_a) <= 1:
        return list(parent_a), list(parent_b)
    pt = int(rng.integers(1, len(parent_a)))
    child_a = list(parent_a[:pt] + parent_b[pt:])
    child_b = list(parent_b[:pt] + parent_a[pt:])
    return child_a, child_b


def optimize_subspace(
    terms: list[AnsatzTerm], h_dense: np.ndarray, n_qubits: int
) -> list[AnsatzTerm]:
    """Optimal coefficient projection in the subspace spanned by candidate basis states."""
    dim = 1 << n_qubits
    unique_masks = sorted({t.basis_mask % dim for t in terms})
    k = len(unique_masks)
    if k == 0:
        return terms

    h_sub = h_dense[np.ix_(unique_masks, unique_masks)]
    _evals, evecs = np.linalg.eigh(h_sub)
    opt_v = evecs[:, 0]

    opt_terms = []
    for i, m in enumerate(unique_masks):
        val = opt_v[i]
        c = float(np.abs(val))
        angle = float(np.angle(val))
        # Snap phase to nearest Z4 phase
        phase_idx = int(np.round(2.0 * angle / np.pi)) % 4
        opt_terms.append(AnsatzTerm(c, m, phase_idx))
    return opt_terms


def evolve_ground_state(
    h_terms: list[PauliTerm],
    n_qubits: int,
    pop_size: int = 40,
    generations: int = 40,
    n_terms: int = 4,
    seed: int = 0,
    target_energy: float | None = None,
    target_energy_tol: float = 1e-3,
    optimize_coefficients: bool = True,
    oracle_truth: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Search ground state by energy fitness alone, reporting post-hoc oracle metrics."""
    rng = np.random.default_rng(seed)
    h_dense = to_hamiltonian_matrix(h_terms, n_qubits)

    if target_energy is None and oracle_truth is not None:
        target_energy = float(oracle_truth["E_exact"])

    # 1. Initialize population
    population = [sample_ansatz(rng, n_qubits, n_terms) for _ in range(pop_size)]

    t0 = time.perf_counter()
    best_cand: list[AnsatzTerm] | None = None
    best_energy = float("inf")
    best_gen = 0
    tts: float | None = None
    tte: int | None = None
    total_evals = 0

    for gen in range(generations):
        energies: list[float] = []
        statevectors: list[np.ndarray] = []

        for cand in population:
            if optimize_coefficients:
                cand = optimize_subspace(cand, h_dense, n_qubits)

            psi = to_statevector(cand, n_qubits)
            e = energy_fitness(h_dense, psi)
            total_evals += 1

            energies.append(e)
            statevectors.append(psi)

            if e < best_energy:
                best_energy = e
                best_cand = cand
                best_gen = gen

                # Check if target energy reached for TTS/TTE
                if (
                    target_energy is not None
                    and abs(e - target_energy) <= target_energy_tol
                    and tts is None
                ):
                    tts = time.perf_counter() - t0
                    tte = total_evals

        # Early exit if target tolerance met
        if target_energy is not None and abs(best_energy - target_energy) <= target_energy_tol:
            break

        # 2. Reproduction
        sorted_idx = sorted(range(pop_size), key=lambda i: energies[i])
        new_pop = [population[sorted_idx[0]], population[sorted_idx[1]]]  # elitism

        # Random injection floor
        n_injected = max(1, int(pop_size * 0.15))
        for _ in range(n_injected):
            new_pop.append(sample_ansatz(rng, n_qubits, n_terms))

        while len(new_pop) < pop_size:
            # Tournament selection
            c1 = rng.choice(pop_size, size=3, replace=False)
            c2 = rng.choice(pop_size, size=3, replace=False)
            p1 = population[min(c1, key=lambda i: energies[i])]
            p2 = population[min(c2, key=lambda i: energies[i])]

            child_a, child_b = crossover_ansatz(p1, p2, rng)
            child_a = mutate_ansatz(child_a, n_qubits, rng)
            child_b = mutate_ansatz(child_b, n_qubits, rng)

            new_pop.append(child_a)
            if len(new_pop) < pop_size:
                new_pop.append(child_b)

        population = new_pop

    dt = max(time.perf_counter() - t0, 1e-9)
    assert best_cand is not None

    if (
        target_energy is not None
        and tts is None
        and abs(best_energy - target_energy) <= target_energy_tol
    ):
        tts = dt
        tte = total_evals

    # Post-hoc evaluation (strictly post-hoc, never for selection)
    best_psi = to_statevector(best_cand, n_qubits)
    fid: float | None = None
    energy_exact: float | None = None
    energy_error: float | None = None
    is_success = False

    if oracle_truth is not None:
        from evobyte.quantum.oracle import ground_state_fidelity

        energy_exact = float(oracle_truth["E_exact"])
        energy_error = abs(best_energy - energy_exact)
        fid = float(ground_state_fidelity(best_psi, oracle_truth))
        is_success = energy_error <= target_energy_tol
    elif target_energy is not None:
        energy_exact = target_energy
        energy_error = abs(best_energy - target_energy)
        is_success = energy_error <= target_energy_tol

    return {
        "best_candidate": best_cand,
        "energy_candidate": best_energy,
        "energy_exact": energy_exact,
        "energy_error": energy_error,
        "fidelity": fid,
        "success": is_success,
        "generations_run": gen + 1,
        "best_generation": best_gen,
        "evaluations": total_evals,
        "qvps": total_evals / dt,
        "elapsed_s": dt,
        "tts_s": tts,
        "tte_evals": tte,
        "seed": seed,
        "n_qubits": n_qubits,
    }
