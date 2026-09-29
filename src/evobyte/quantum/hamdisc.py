"""Hamiltonian rediscovery from quantum dynamics (spec: Q11).

Simulates quantum state dynamics under a target Hamiltonian, generates observable
trajectories, scores candidate Hamiltonians by dynamics-matching error, and recovers
sparse Pauli term structure and continuous interaction coefficients.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np

from evobyte.quantum.hamiltonians import PauliTerm, decode_hamiltonian, to_hamiltonian_matrix
from evobyte.quantum.pauli import Pauli, decode_human


@dataclass(frozen=True)
class DynamicsDataset:
    """Structured dataset of quantum state dynamics and observable trajectories."""

    n_qubits: int
    initial_states: list[np.ndarray]
    times: np.ndarray
    observable_terms: list[PauliTerm]
    observed_trajectories: np.ndarray  # shape: (n_states, n_times, n_observables)
    sha256_hash: str
    metadata: dict[str, Any]


# -----------------------------------------------------------------------------
# Standard Benchmark Hamiltonians
# -----------------------------------------------------------------------------

def xyz_field_benchmark(
    n_qubits: int = 2,
    jx: float = 1.0,
    jy: float = 0.5,
    jz: float = 0.8,
    hz: float = 0.4,
) -> list[PauliTerm]:
    """Anisotropic XYZ Hamiltonian with transverse field: a*XX + b*YY + c*ZZ + h*Z."""
    if n_qubits < 2:
        raise ValueError("xyz_field_benchmark requires n_qubits >= 2")
    terms: list[PauliTerm] = []
    # 2-qubit interactions along open chain
    for i in range(n_qubits - 1):
        j = i + 1
        # XX: x_mask has bits i and j
        xm_xx = (1 << i) | (1 << j)
        terms.append(PauliTerm(coeff=jx, x_mask=xm_xx, z_mask=0, phase=0))
        # YY: x_mask and z_mask have bits i and j, phase 2
        xm_yy = (1 << i) | (1 << j)
        zm_yy = (1 << i) | (1 << j)
        terms.append(PauliTerm(coeff=jy, x_mask=xm_yy, z_mask=zm_yy, phase=2))
        # ZZ: z_mask has bits i and j
        zm_zz = (1 << i) | (1 << j)
        terms.append(PauliTerm(coeff=jz, x_mask=0, z_mask=zm_zz, phase=0))
    # 1-qubit field on first qubit
    terms.append(PauliTerm(coeff=hz, x_mask=0, z_mask=1, phase=0))
    return terms


def ising_transverse_benchmark(
    n_qubits: int = 2,
    jz: float = 1.0,
    hx: float = 0.5,
) -> list[PauliTerm]:
    """Transverse-field Ising benchmark: -J ZZ - h X."""
    if n_qubits < 2:
        raise ValueError("ising_transverse_benchmark requires n_qubits >= 2")
    terms: list[PauliTerm] = []
    for i in range(n_qubits):
        terms.append(PauliTerm(coeff=-hx, x_mask=(1 << i), z_mask=0, phase=0))
    for i in range(n_qubits - 1):
        terms.append(PauliTerm(coeff=-jz, x_mask=0, z_mask=(1 << i) | (1 << (i + 1)), phase=0))
    return terms


# -----------------------------------------------------------------------------
# Dynamics Simulator & Observable Measurement
# -----------------------------------------------------------------------------

def build_default_initial_states(n_qubits: int) -> list[np.ndarray]:
    """Construct an informationally complete, asymmetry-breaking set of initial states."""
    dim = 1 << n_qubits
    states: list[np.ndarray] = []

    # 1. Computational ground |00...0> and all-ones |11...1>
    s0 = np.zeros(dim, dtype=np.complex128)
    s0[0] = 1.0
    states.append(s0)

    s_all = np.zeros(dim, dtype=np.complex128)
    s_all[dim - 1] = 1.0
    states.append(s_all)

    # 2. Computational single-excitation states |0...1...0> for each qubit
    for q in range(n_qubits):
        sq = np.zeros(dim, dtype=np.complex128)
        sq[1 << q] = 1.0
        states.append(sq)

    # 3. Superposition states (|+0...0>, |0+...0>) breaking symmetry
    for q in range(n_qubits):
        sp = np.zeros(dim, dtype=np.complex128)
        sp[0] = 1.0 / np.sqrt(2)
        sp[1 << q] = 1.0 / np.sqrt(2)
        states.append(sp)

    # 4. Off-axis states (|+1...0>, |1+...0>) breaking local Z degeneracies
    if n_qubits >= 2:
        s_p1 = np.zeros(dim, dtype=np.complex128)
        s_p1[1] = 1.0 / np.sqrt(2)
        s_p1[3] = 1.0 / np.sqrt(2)
        states.append(s_p1)

        s_1p = np.zeros(dim, dtype=np.complex128)
        s_1p[2] = 1.0 / np.sqrt(2)
        s_1p[3] = 1.0 / np.sqrt(2)
        states.append(s_1p)

        # 5. Entangled Bell state on first two qubits
        bell = np.zeros(dim, dtype=np.complex128)
        bell[0] = 1.0 / np.sqrt(2)
        bell[3] = 1.0 / np.sqrt(2)
        states.append(bell)

    return states


def build_default_observable_terms(n_qubits: int) -> list[PauliTerm]:
    """Construct standard 1-local and nearest-neighbor 2-local Pauli observables."""
    obs: list[PauliTerm] = []
    # 1-local Pauli observables on all qubits
    for q in range(n_qubits):
        obs.append(PauliTerm(1.0, 1 << q, 0, 0))          # X_q
        obs.append(PauliTerm(1.0, 1 << q, 1 << q, 1))     # Y_q
        obs.append(PauliTerm(1.0, 0, 1 << q, 0))          # Z_q

    # 2-local Pauli correlators on adjacent pairs
    for i in range(n_qubits - 1):
        j = i + 1
        xm = (1 << i) | (1 << j)
        zm = (1 << i) | (1 << j)
        obs.append(PauliTerm(1.0, xm, 0, 0))              # X_i X_j
        obs.append(PauliTerm(1.0, xm, zm, 2))             # Y_i Y_j
        obs.append(PauliTerm(1.0, 0, zm, 0))              # Z_i Z_j

    return obs


def simulate_dynamics(
    terms: Sequence[PauliTerm],
    n_qubits: int,
    initial_states: Sequence[np.ndarray],
    times: np.ndarray,
    observable_terms: Sequence[PauliTerm],
) -> np.ndarray:
    """Compute time-dependent expectation values of observables for each initial state."""
    n_states = len(initial_states)
    n_times = len(times)
    n_obs = len(observable_terms)

    if not terms:
        # Trivial zero Hamiltonian: state does not evolve
        res = np.zeros((n_states, n_times, n_obs), dtype=np.float64)
        obs_mats = [to_hamiltonian_matrix([o], n_qubits) for o in observable_terms]
        for s_idx, psi0 in enumerate(initial_states):
            vals = [float(np.real(psi0.conj().T @ o_mat @ psi0)) for o_mat in obs_mats]
            for t_idx in range(n_times):
                res[s_idx, t_idx, :] = vals
        return res

    h_mat = to_hamiltonian_matrix(terms, n_qubits)
    evals, evecs = np.linalg.eigh(h_mat)
    obs_mats = [to_hamiltonian_matrix([o], n_qubits) for o in observable_terms]

    trajectories = np.zeros((n_states, n_times, n_obs), dtype=np.float64)
    for s_idx, psi0 in enumerate(initial_states):
        # Basis change: psi0 in eigenbasis
        psi0_diag = evecs.conj().T @ psi0
        for t_idx, t in enumerate(times):
            # Unitary evolution in diagonal eigenbasis: e^{-i E_k t}
            phase_factors = np.exp(-1j * evals * t)
            psi_t = evecs @ (psi0_diag * phase_factors)
            for o_idx, o_mat in enumerate(obs_mats):
                val = float(np.real(psi_t.conj().T @ o_mat @ psi_t))
                trajectories[s_idx, t_idx, o_idx] = val

    return trajectories


def generate_dynamics_dataset(
    target_terms: Sequence[PauliTerm],
    n_qubits: int,
    initial_states: Sequence[np.ndarray] | None = None,
    times: np.ndarray | None = None,
    observable_terms: Sequence[PauliTerm] | None = None,
    seed: int = 0,
) -> DynamicsDataset:
    """Generate reproducible dynamics dataset with cryptographic SHA-256 provenance."""
    if initial_states is None:
        initial_states = build_default_initial_states(n_qubits)
    if times is None:
        times = np.linspace(0.1, 1.5, 10, dtype=np.float64)
    if observable_terms is None:
        observable_terms = build_default_observable_terms(n_qubits)

    trajectories = simulate_dynamics(
        terms=target_terms,
        n_qubits=n_qubits,
        initial_states=initial_states,
        times=times,
        observable_terms=observable_terms,
    )

    # Compute provenance hash
    hasher = hashlib.sha256()
    hasher.update(f"n_qubits={n_qubits}".encode())
    hasher.update(times.tobytes())
    hasher.update(trajectories.tobytes())
    sha256 = hasher.hexdigest()

    metadata = {
        "n_qubits": n_qubits,
        "n_initial_states": len(initial_states),
        "n_times": len(times),
        "n_observables": len(observable_terms),
        "target_terms_count": len(target_terms),
        "seed": seed,
    }

    return DynamicsDataset(
        n_qubits=n_qubits,
        initial_states=list(initial_states),
        times=times,
        observable_terms=list(observable_terms),
        observed_trajectories=trajectories,
        sha256_hash=sha256,
        metadata=metadata,
    )


# -----------------------------------------------------------------------------
# Dynamics-Matching Fitness & Dictionary
# -----------------------------------------------------------------------------

def dynamics_matching_fitness(
    candidate_terms: Sequence[PauliTerm],
    dataset: DynamicsDataset,
    lambda_sparse: float = 1e-4,
    lambda_comp: float = 1e-3,
) -> tuple[float, float]:
    """Compute (dynamics_mse, total_fitness) for a candidate Hamiltonian."""
    pred_trajectories = simulate_dynamics(
        terms=candidate_terms,
        n_qubits=dataset.n_qubits,
        initial_states=dataset.initial_states,
        times=dataset.times,
        observable_terms=dataset.observable_terms,
    )

    diff = pred_trajectories - dataset.observed_trajectories
    mse = float(np.mean(diff**2))

    l1_norm = sum(abs(t.coeff) for t in candidate_terms)
    n_terms = len(candidate_terms)
    total_loss = mse + lambda_sparse * l1_norm + lambda_comp * n_terms

    return mse, total_loss


def build_klocal_pauli_dictionary(n_qubits: int, max_k: int = 2) -> list[tuple[int, int, int]]:
    """Build compact dictionary of non-identity 1-local and 2-local Pauli words."""
    words: list[tuple[int, int, int]] = []
    # 1-local terms
    for i in range(n_qubits):
        words.append((1 << i, 0, 0))            # X_i
        words.append((1 << i, 1 << i, 1))       # Y_i
        words.append((0, 1 << i, 0))            # Z_i

    # 2-local terms
    if max_k >= 2:
        for i in range(n_qubits):
            for j in range(i + 1, n_qubits):
                xm_i, zm_i = 1 << i, 1 << i
                xm_j, zm_j = 1 << j, 1 << j
                # 9 combinations: {X, Y, Z} x {X, Y, Z}
                combos = [
                    (xm_i | xm_j, 0, 0),                        # X_i X_j
                    (xm_i | xm_j, zm_j, 1),                     # X_i Y_j
                    (xm_i, zm_j, 0),                            # X_i Z_j
                    (xm_i | xm_j, zm_i, 1),                     # Y_i X_j
                    (xm_i | xm_j, zm_i | zm_j, 2),              # Y_i Y_j
                    (xm_i, zm_i | zm_j, 1),                     # Y_i Z_j
                    (xm_j, zm_i, 0),                            # Z_i X_j
                    (xm_j, zm_i | zm_j, 1),                     # Z_i Y_j
                    (0, zm_i | zm_j, 0),                        # Z_i Z_j
                ]
                words.extend(combos)

    return words


# -----------------------------------------------------------------------------
# Structural Recovery Evaluation
# -----------------------------------------------------------------------------

def evaluate_structural_recovery(
    discovered_terms: Sequence[PauliTerm],
    true_terms: Sequence[PauliTerm],
    coeff_tol: float = 0.05,
) -> dict[str, float]:
    """Compute precision, recall, F1 score, and coefficient errors."""
    def term_key(t: PauliTerm) -> tuple[int, int, int]:
        return (t.x_mask, t.z_mask, t.phase)

    # Prune negligible terms
    disc_filtered = [t for t in discovered_terms if abs(t.coeff) > 1e-3]
    true_dict = {term_key(t): t.coeff for t in true_terms if abs(t.coeff) > 1e-4}
    disc_dict = {term_key(t): t.coeff for t in disc_filtered}

    true_keys = set(true_dict.keys())
    disc_keys = set(disc_dict.keys())

    tp_keys = true_keys & disc_keys
    tp = len(tp_keys)
    fp = len(disc_keys - true_keys)
    fn = len(true_keys - disc_keys)

    prec = tp / len(disc_keys) if disc_keys else 0.0
    rec = tp / len(true_keys) if true_keys else 0.0
    f1 = (2.0 * prec * rec / (prec + rec)) if (prec + rec) > 0.0 else 0.0

    # Coefficient errors on true terms
    coeff_diffs = []
    for k in true_keys:
        disc_val = disc_dict.get(k, 0.0)
        true_val = true_dict[k]
        coeff_diffs.append(abs(disc_val - true_val))

    mae = float(np.mean(coeff_diffs)) if coeff_diffs else 0.0
    max_err = float(np.max(coeff_diffs)) if coeff_diffs else 0.0

    return {
        "precision": prec,
        "recall": rec,
        "f1": f1,
        "coeff_mae": mae,
        "coeff_max_err": max_err,
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
    }


# -----------------------------------------------------------------------------
# Evolutionary Search with Local Optimization
# -----------------------------------------------------------------------------

def _optimize_active_coeffs(
    active_dict: dict[int, float],
    dictionary: list[tuple[int, int, int]],
    dataset: DynamicsDataset,
    steps: int = 25,
    step_size: float = 0.2,
) -> dict[int, float]:
    """Deterministic coordinate search on active Pauli coefficients with term-swap local search."""
    cur_dict = active_dict.copy()
    keys = list(cur_dict.keys())
    if not keys:
        return cur_dict

    def score_dict(d: dict[int, float]) -> float:
        cand_terms = [
            PauliTerm(coeff=c, x_mask=dictionary[idx][0], z_mask=dictionary[idx][1], phase=dictionary[idx][2])
            for idx, c in d.items() if abs(c) > 1e-4
        ]
        _, loss = dynamics_matching_fitness(cand_terms, dataset)
        return loss

    cur_loss = score_dict(cur_dict)
    delta = step_size
    for _ in range(steps):
        improved = False
        for k in keys:
            for d in [delta, -delta]:
                test_dict = cur_dict.copy()
                test_dict[k] += d
                loss = score_dict(test_dict)
                if loss < cur_loss - 1e-7:
                    cur_loss = loss
                    cur_dict = test_dict
                    improved = True
                    break
        if not improved:
            delta *= 0.5
            if delta < 1e-4:
                break

    # Term Swap Local Step: test swapping each active term with unused dictionary words
    if cur_loss > 1e-5:
        unused = [i for i in range(len(dictionary)) if i not in cur_dict]
        for old_k in list(cur_dict.keys()):
            for new_k in unused:
                test_dict = cur_dict.copy()
                val = test_dict.pop(old_k)
                test_dict[new_k] = val
                loss = score_dict(test_dict)
                if loss < cur_loss - 1e-7:
                    cur_loss = loss
                    cur_dict = test_dict
                    for d_k in list(cur_dict.keys()):
                        for d_val in [0.1, -0.1]:
                            ref_dict = cur_dict.copy()
                            ref_dict[d_k] += d_val
                            ref_loss = score_dict(ref_dict)
                            if ref_loss < cur_loss - 1e-7:
                                cur_loss = ref_loss
                                cur_dict = ref_dict
                    break

    return {k: c for k, c in cur_dict.items() if abs(c) > 0.02}


def _single_evolution_run(
    dataset: DynamicsDataset,
    dictionary: list[tuple[int, int, int]],
    pop_size: int,
    max_generations: int,
    early_stop_mse: float,
    rng: np.random.Generator,
) -> tuple[dict[int, float], float, float, int, int]:
    dict_len = len(dictionary)
    pop: list[dict[int, float]] = []
    for _ in range(pop_size):
        n_t = int(rng.integers(1, min(5, dict_len + 1)))
        chosen = rng.choice(dict_len, size=n_t, replace=False)
        ind = {int(idx): float(rng.uniform(-1.0, 1.0)) for idx in chosen}
        pop.append(ind)

    best_ind: dict[int, float] = {}
    best_loss = float("inf")
    best_mse = float("inf")
    evals = 0

    for gen in range(max_generations):
        evaluated: list[tuple[float, float, dict[int, float]]] = []
        for ind in pop:
            evals += 1
            cand_terms = [
                PauliTerm(coeff=c, x_mask=dictionary[idx][0], z_mask=dictionary[idx][1], phase=dictionary[idx][2])
                for idx, c in ind.items() if abs(c) > 1e-4
            ]
            mse, loss = dynamics_matching_fitness(cand_terms, dataset)
            evaluated.append((loss, mse, ind))

        evaluated.sort(key=lambda x: x[0])
        if evaluated[0][0] < best_loss:
            best_loss, best_mse, best_ind = evaluated[0]

        # Memetic elite refinement on top candidates
        n_elites_to_tune = min(5, len(evaluated))
        for i in range(n_elites_to_tune):
            opt_ind = _optimize_active_coeffs(evaluated[i][2], dictionary, dataset)
            cand_terms = [
                PauliTerm(coeff=c, x_mask=dictionary[idx][0], z_mask=dictionary[idx][1], phase=dictionary[idx][2])
                for idx, c in opt_ind.items() if abs(c) > 1e-4
            ]
            opt_mse, opt_loss = dynamics_matching_fitness(cand_terms, dataset)
            if opt_loss < best_loss:
                best_loss = opt_loss
                best_mse = opt_mse
                best_ind = opt_ind
            evaluated[i] = (opt_loss, opt_mse, opt_ind)

        if best_mse <= early_stop_mse:
            break

        # Selection and genetic reproduction
        evaluated.sort(key=lambda x: x[0])
        elites = [ind for _, _, ind in evaluated[:8]]
        new_pop = [e.copy() for e in elites]

        while len(new_pop) < pop_size:
            pool_size = max(5, int(len(evaluated) * 0.4))
            p_a = evaluated[rng.integers(0, pool_size)][2]
            p_b = evaluated[rng.integers(0, pool_size)][2]

            child: dict[int, float] = {}
            all_keys = set(p_a.keys()) | set(p_b.keys())
            for k in all_keys:
                if k in p_a and k in p_b:
                    child[k] = 0.5 * (p_a[k] + p_b[k])
                elif rng.random() < 0.6:
                    child[k] = p_a[k] if k in p_a else p_b[k]

            if rng.random() < 0.35 and len(child) < 8:
                unused = [i for i in range(dict_len) if i not in child]
                if unused:
                    child[int(rng.choice(unused))] = float(rng.uniform(-1.0, 1.0))
            if rng.random() < 0.35 and len(child) > 1:
                del_k = int(rng.choice(list(child.keys())))
                del child[del_k]
            for k in list(child.keys()):
                if rng.random() < 0.35:
                    child[k] += float(rng.normal(0, 0.2))

            new_pop.append(child)

        pop = new_pop

    return best_ind, best_mse, best_loss, gen + 1, evals


def rediscover_hamiltonian_from_dynamics(
    dataset: DynamicsDataset,
    max_k: int = 2,
    pop_size: int = 80,
    max_generations: int = 25,
    max_restarts: int = 3,
    early_stop_mse: float = 1e-6,
    seed: int = 0,
) -> dict[str, Any]:
    """Evolve sparse Pauli Hamiltonian matching observed quantum dynamics with multi-restart."""
    t0 = time.perf_counter()
    rng = np.random.default_rng(seed)
    dictionary = build_klocal_pauli_dictionary(dataset.n_qubits, max_k=max_k)

    global_best_ind: dict[int, float] = {}
    global_best_mse = float("inf")
    global_best_loss = float("inf")
    total_evals = 0
    total_gens = 0

    for _ in range(max_restarts):
        ind, mse, loss, gens, evals = _single_evolution_run(
            dataset=dataset,
            dictionary=dictionary,
            pop_size=pop_size,
            max_generations=max_generations,
            early_stop_mse=early_stop_mse,
            rng=rng,
        )
        total_evals += evals
        total_gens += gens

        if mse < global_best_mse:
            global_best_mse = mse
            global_best_loss = loss
            global_best_ind = ind

        if global_best_mse <= early_stop_mse:
            break

    dt = max(time.perf_counter() - t0, 1e-9)

    final_terms = [
        PauliTerm(coeff=float(c), x_mask=dictionary[idx][0], z_mask=dictionary[idx][1], phase=dictionary[idx][2])
        for idx, c in sorted(global_best_ind.items()) if abs(c) > 0.01
    ]

    return {
        "discovered_terms": final_terms,
        "dynamics_mse": global_best_mse,
        "fitness": global_best_loss,
        "generations": total_gens,
        "evaluations": total_evals,
        "elapsed_s": dt,
        "expression": decode_hamiltonian(final_terms, dataset.n_qubits),
        "seed": seed,
    }
