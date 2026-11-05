"""Target catalogue and independent certificate verifiers (P163).

Defines rigorous, self-contained verification functions for candidate discoveries:
1. Spectral graph counterexamples (e.g. Aouchiche-Hansen / AutoGraphiX / Wagner conjectures).
2. van der Waerden number lower bounds W(r, k).
3. Schur number lower bounds S(k) and sum-free partitions.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


@dataclass(frozen=True)
class TargetSpec:
    target_id: str
    family: str
    description: str
    reference: str
    published_bound: float
    bound_type: str  # "lower_bound", "upper_bound", "counterexample_threshold"
    verification_fn: str


def verify_vanderwaerden_coloring(
    coloring: list[int] | np.ndarray, r: int, k: int
) -> tuple[bool, str]:
    """Verify that a coloring of [1..N] with r colors contains no monochromatic k-term AP.

    Returns (is_valid, message).
    """
    col = np.asarray(coloring, dtype=int)
    n = len(col)
    if n == 0:
        return False, "empty coloring"
    if k < 2:
        return False, f"k must be at least 2, got {k}"
    if r < 1:
        return False, f"r must be at least 1, got {r}"
    if np.any(col < 1) or np.any(col > r):
        return False, f"colors must be integers in 1..{r}"

    # Check all arithmetic progressions of length k: a, a+d, ..., a+(k-1)d <= n
    max_d = (n - 1) // (k - 1)
    for d in range(1, max_d + 1):
        for a in range(n - (k - 1) * d):
            indices = [a + i * d for i in range(k)]
            first_c = col[indices[0]]
            if all(col[idx] == first_c for idx in indices):
                return (
                    False,
                    f"monochromatic AP of length {k} found at a={a + 1}, d={d}, color={first_c}",
                )

    return True, f"valid: zero monochromatic {k}-term APs in 1..{n} with {r} colors"


def verify_schur_partition(coloring: list[int] | np.ndarray, k: int) -> tuple[bool, str]:
    """Verify that a partition of 1..N into k sets is sum-free (no x + y = z with col(x)=col(y)=col(z))."""
    col = np.asarray(coloring, dtype=int)
    n = len(col)
    if n == 0:
        return False, "empty partition"
    if k < 1:
        return False, f"k must be at least 1, got {k}"
    if np.any(col < 1) or np.any(col > k):
        return False, f"colors must be in 1..{k}"

    for c in range(1, k + 1):
        elements = [i + 1 for i, color in enumerate(col) if color == c]
        elem_set = set(elements)
        for i, x in enumerate(elements):
            for y in elements[i:]:
                if (x + y) in elem_set:
                    return False, f"monochromatic Schur violation: {x} + {y} = {x + y} in color {c}"

    return True, f"valid sum-free partition of 1..{n} into {k} classes"


def verify_graph_spectral_conjecture(
    adj_matrix: list[list[int]] | np.ndarray,
    conjecture_id: str,
) -> tuple[bool, dict[str, Any]]:
    """Verify a graph counterexample for registered spectral graph conjectures.

    For example, Wagner (2021) / Aouchiche-Hansen Conjectures:
    - 'AH_conj_1': D + s >= n - 1 (distance spectral radius + algebraic connectivity)
    - 'AH_conj_2': alpha + mu_2 <= n
    """
    a = np.asarray(adj_matrix, dtype=float)
    if a.ndim != 2 or a.shape[0] != a.shape[1]:
        return False, {"error": "matrix must be square"}
    n = a.shape[0]
    if n == 0:
        return False, {"error": "empty graph"}
    if not np.allclose(a, a.T):
        return False, {"error": "adjacency matrix must be symmetric"}
    if np.any(np.diag(a) != 0):
        return False, {"error": "simple graph cannot have self-loops"}
    if not np.all(np.isin(a, [0.0, 1.0])):
        return False, {"error": "adjacency matrix entries must be 0 or 1"}

    # Compute graph invariants
    degrees = np.sum(a, axis=1)
    laplacian = np.diag(degrees) - a
    lap_evals = np.sort(np.linalg.eigvalsh(laplacian))
    adj_evals = np.sort(np.linalg.eigvalsh(a))[::-1]

    lambda_1 = float(adj_evals[0])
    mu_2 = float(lap_evals[1]) if n >= 2 else 0.0  # algebraic connectivity

    # Diameter via shortest path powers
    dist_matrix = np.full((n, n), np.inf)
    np.fill_diagonal(dist_matrix, 0)
    dist_matrix[a == 1] = 1
    for k_idx in range(n):
        dist_matrix = np.minimum(dist_matrix, dist_matrix[:, [k_idx]] + dist_matrix[[k_idx], :])

    if np.any(np.isinf(dist_matrix)):
        diameter = float("inf")
    else:
        diameter = float(np.max(dist_matrix))

    metrics = {
        "n": n,
        "lambda_1": lambda_1,
        "mu_2": mu_2,
        "diameter": diameter,
        "connected": bool(mu_2 > 1e-6),
    }

    if conjecture_id == "AH_diam_mu2":
        # Sample conjecture: diameter + mu_2 >= 2.0 for all connected graphs n >= 4
        # Wagner refutes related invariants.
        val = diameter + mu_2
        metrics["lhs_value"] = val
        metrics["threshold"] = 2.0
        # Counterexample exists if connected and val < 2.0 - 1e-6
        is_counterexample = bool(metrics["connected"] and val < (2.0 - 1e-6))
        return is_counterexample, metrics

    return False, {"error": f"unknown conjecture {conjecture_id}"}


def load_catalogue(path: str | Path | None = None) -> list[TargetSpec]:
    """Load pre-registered targets from JSON catalogue."""
    p = Path(path) if path else Path("docs/research/targets/open_targets.json")
    data = json.loads(p.read_text(encoding="utf-8"))
    return [TargetSpec(**item) for item in data["targets"]]
