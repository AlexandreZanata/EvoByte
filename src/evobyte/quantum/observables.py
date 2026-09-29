"""Quantum observable simulation, dataset generation, and hashing (spec: Q09).

Simulates physical observables (ground energy, spectral gap, magnetization,
correlations, entanglement entropy) over parameter grids, computing cryptographic
hashes for dataset provenance.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np

from evobyte.quantum.hamiltonians import (
    PauliTerm,
    heisenberg,
    ising,
    to_hamiltonian_matrix,
)
from evobyte.quantum.oracle import exact


@dataclass(frozen=True)
class ObservableDataset:
    """Structured dataset of quantum observables over parameter grids."""

    model: str
    n_qubits: int
    features: np.ndarray  # shape (N_points, N_features)
    feature_names: tuple[str, ...]
    targets: dict[str, np.ndarray]  # target_name -> 1D array of shape (N_points,)
    sha256_hash: str
    metadata: dict[str, Any]

    def to_arrays(self, target_name: str) -> tuple[np.ndarray, np.ndarray]:
        """Extract (X, y) arrays for symbolic regression on given target."""
        if target_name not in self.targets:
            raise KeyError(f"target {target_name} not found; available: {list(self.targets.keys())}")
        return self.features.copy(), self.targets[target_name].copy()


# -----------------------------------------------------------------------------
# Observables Measurement
# -----------------------------------------------------------------------------

def ground_energy(h_terms: list[PauliTerm], n_qubits: int) -> float:
    """Exact ground state energy E_0."""
    truth = exact(h_terms, n_qubits)
    return float(truth["E_exact"])


def spectral_gap(h_terms: list[PauliTerm], n_qubits: int) -> float:
    """Spectral gap E_1 - E_0."""
    truth = exact(h_terms, n_qubits)
    energies = truth["energies"]
    if len(energies) < 2:
        return 0.0
    return float(max(0.0, energies[1] - energies[0]))


def magnetization_x(psi: np.ndarray, n_qubits: int) -> float:
    """Mean transverse magnetization (1/N) <sum_i X_i>."""
    norm = np.linalg.norm(psi)
    if norm < 1e-14:
        return 0.0
    psi_norm = psi / norm

    # Sum of single-qubit X expectations
    dim = 1 << n_qubits
    total_x = 0.0
    for q in range(n_qubits):
        # X on qubit q flips bit q
        val = 0.0
        for i in range(dim):
            j = i ^ (1 << q)
            val += np.real(np.conj(psi_norm[i]) * psi_norm[j])
        total_x += val

    return float(total_x / n_qubits)


def magnetization_z(psi: np.ndarray, n_qubits: int) -> float:
    """Mean longitudinal magnetization (1/N) <sum_i Z_i>."""
    norm = np.linalg.norm(psi)
    if norm < 1e-14:
        return 0.0
    psi_norm = psi / norm

    dim = 1 << n_qubits
    probs = np.abs(psi_norm) ** 2
    total_z = 0.0
    for q in range(n_qubits):
        # Z eigenvalue on qubit q: +1 if bit=0, -1 if bit=1
        bit_mask = 1 << q
        val = sum(probs[i] if ((i & bit_mask) == 0) else -probs[i] for i in range(dim))
        total_z += val

    return float(total_z / n_qubits)


def correlation_zz(psi: np.ndarray, n_qubits: int, q1: int, q2: int) -> float:
    """Connected two-point correlation <Z_q1 Z_q2> - <Z_q1><Z_q2>."""
    norm = np.linalg.norm(psi)
    if norm < 1e-14:
        return 0.0
    psi_norm = psi / norm
    dim = 1 << n_qubits
    probs = np.abs(psi_norm) ** 2

    m1 = 1 << q1
    m2 = 1 << q2

    exp_z1 = sum(probs[i] if ((i & m1) == 0) else -probs[i] for i in range(dim))
    exp_z2 = sum(probs[i] if ((i & m2) == 0) else -probs[i] for i in range(dim))

    # Z1 Z2 is +1 if same parity on q1 and q2, -1 if opposite
    exp_z1z2 = 0.0
    for i in range(dim):
        b1 = (i >> q1) & 1
        b2 = (i >> q2) & 1
        sign = 1.0 if b1 == b2 else -1.0
        exp_z1z2 += sign * probs[i]

    return float(exp_z1z2 - exp_z1 * exp_z2)


def entanglement_entropy(psi: np.ndarray, n_qubits: int, subsystem_size: int = 1) -> float:
    """Bipartite von Neumann entanglement entropy S(rho_A) = -Tr(rho_A log2 rho_A)."""
    if subsystem_size <= 0 or subsystem_size >= n_qubits:
        raise ValueError(f"subsystem_size {subsystem_size} must be in [1, {n_qubits - 1}]")

    norm = np.linalg.norm(psi)
    if norm < 1e-14:
        return 0.0
    psi_norm = psi / norm

    dim_a = 1 << subsystem_size
    dim_b = 1 << (n_qubits - subsystem_size)

    # Reshape state into bipartite tensor (dim_a, dim_b)
    # where basis index i = i_a * dim_b + i_b
    psi_matrix = psi_norm.reshape((dim_a, dim_b))

    # Reduced density matrix rho_A = psi_matrix @ psi_matrix.conj().T
    rho_a = psi_matrix @ psi_matrix.conj().T

    evals = np.linalg.eigvalsh(rho_a)
    # Keep strictly positive eigenvalues
    evals = evals[evals > 1e-14]
    if len(evals) == 0:
        return 0.0

    entropy = -float(np.sum(evals * np.log2(evals)))
    return float(max(0.0, entropy))


# -----------------------------------------------------------------------------
# Dataset Generation and Provenance
# -----------------------------------------------------------------------------

def compute_dataset_hash(features: np.ndarray, targets: dict[str, np.ndarray]) -> str:
    """Compute SHA-256 hash across features and all target arrays for provenance."""
    hasher = hashlib.sha256()
    hasher.update(np.ascontiguousarray(features, dtype=np.float64).tobytes())
    for name in sorted(targets.keys()):
        hasher.update(name.encode("utf-8"))
        hasher.update(np.ascontiguousarray(targets[name], dtype=np.float64).tobytes())
    return hasher.hexdigest()[:16]


def generate_observable_dataset(
    model: str,
    n_qubits: int,
    param_grid: dict[str, Sequence[float]],
    observables: Sequence[str] | None = None,
) -> ObservableDataset:
    """Generate structured quantum observable dataset over parameter grid with SHA-256 hash."""
    allowed_obs = {"energy", "gap", "mag_x", "mag_z", "entropy"}
    target_names = list(allowed_obs if observables is None else set(observables))

    feature_keys = sorted(param_grid.keys())
    grid_arrays = [np.asarray(param_grid[k], dtype=np.float64) for k in feature_keys]

    mesh = np.meshgrid(*grid_arrays, indexing="ij")
    n_points = mesh[0].size
    flat_features = np.column_stack([m.ravel() for m in mesh])

    target_data: dict[str, list[float]] = {name: [] for name in target_names}

    for row in flat_features:
        param_dict = dict(zip(feature_keys, row))
        j_val = float(param_dict.get("J", 1.0))
        h_val = float(param_dict.get("h", 1.0))

        if model == "heisenberg":
            h_terms = heisenberg(n_qubits, j=j_val)
        elif model == "ising":
            h_terms = ising(n_qubits, j=j_val, h=h_val)
        else:
            raise ValueError(f"unknown model: {model}")

        owe = exact(h_terms, n_qubits)
        psi_0 = owe["psi_exact"]

        if "energy" in target_names:
            target_data["energy"].append(float(owe["E_exact"]))
        if "gap" in target_names:
            evals = owe["energies"]
            gap_val = float(max(0.0, evals[1] - evals[0])) if len(evals) > 1 else 0.0
            target_data["gap"].append(gap_val)
        if "mag_x" in target_names:
            target_data["mag_x"].append(magnetization_x(psi_0, n_qubits))
        if "mag_z" in target_names:
            target_data["mag_z"].append(magnetization_z(psi_0, n_qubits))
        if "entropy" in target_names:
            target_data["entropy"].append(entanglement_entropy(psi_0, n_qubits, subsystem_size=1))

    target_arrays = {k: np.array(v, dtype=np.float64) for k, v in target_data.items()}
    ds_hash = compute_dataset_hash(flat_features, target_arrays)

    metadata = {
        "model": model,
        "n_qubits": n_qubits,
        "n_points": n_points,
        "feature_keys": feature_keys,
        "target_names": target_names,
    }

    return ObservableDataset(
        model=model,
        n_qubits=n_qubits,
        features=flat_features,
        feature_names=tuple(feature_keys),
        targets=target_arrays,
        sha256_hash=ds_hash,
        metadata=metadata,
    )


def split_observable_dataset(
    dataset: ObservableDataset,
    target_name: str,
    train_fraction: float = 0.6,
    val_fraction: float = 0.2,
    extrap_fraction: float = 0.2,
    seed: int = 42,
) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """Partition dataset into train, in-domain holdout validation, and out-of-domain extrapolation splits."""
    xs, ys = dataset.to_arrays(target_name)
    n = len(xs)

    # Sort by first feature to allow clean out-of-domain extrapolation
    sort_idx = np.argsort(xs[:, 0])
    xs_sorted = xs[sort_idx]
    ys_sorted = ys[sort_idx]

    n_extrap = int(np.round(n * extrap_fraction))
    n_in_domain = n - n_extrap

    # Out-of-domain extrapolation: top values of feature 0
    xs_extrap = xs_sorted[n_in_domain:]
    ys_extrap = ys_sorted[n_in_domain:]

    # In-domain points
    xs_in = xs_sorted[:n_in_domain]
    ys_in = ys_sorted[:n_in_domain]

    # Deterministic train/validation split within in-domain
    rng = np.random.default_rng(seed)
    in_perm = rng.permutation(len(xs_in))
    n_train = int(np.round(n_in_domain * (train_fraction / (train_fraction + val_fraction))))

    train_idx = in_perm[:n_train]
    val_idx = in_perm[n_train:]

    return {
        "train": (xs_in[train_idx], ys_in[train_idx]),
        "validation": (xs_in[val_idx], ys_in[val_idx]),
        "extrapolation": (xs_extrap, ys_extrap),
    }
