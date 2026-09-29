"""Pauli search engine skeleton (Q04 scope): candidate codec + seeded search.

Candidate = fixed list of (coeff, x_mask, z_mask) terms, n_terms in
{1, 2, 4, 8, 16}. Fitness: commutator_error + complexity_penalty.
Dense matrices are used here only because N is tiny (smoke scale); the
bitwise prefilter (commutes_bitwise) runs first, mirroring the cascade.
"""

from __future__ import annotations

import time

import numpy as np

from evobyte.quantum.hamiltonians import (
    PauliTerm,
    commutator_norm,
    commutes_bitwise,
    hamiltonian_hash,
)
from evobyte.quantum.pauli import Pauli

COEFF_BANK = (1.0, -1.0, 0.5, -0.5, 2.0)
COMPLEXITY_W = 1e-3


def sample_term(rng: np.random.Generator, n_qubits: int) -> PauliTerm:
    """Uniform random Pauli string with a bank coefficient."""
    x = int(rng.integers(0, 2**n_qubits))
    z = int(rng.integers(0, 2**n_qubits))
    c = COEFF_BANK[int(rng.integers(0, len(COEFF_BANK)))]
    return PauliTerm(c, x, z)


def sample_candidate(rng: np.random.Generator, n_qubits: int, n_terms: int) -> list[PauliTerm]:
    """Random operator candidate with exactly n_terms."""
    if n_terms not in (1, 2, 4, 8, 16):
        raise ValueError(f"n_terms must be in {{1,2,4,8,16}}, got {n_terms}")
    return [sample_term(rng, n_qubits) for _ in range(n_terms)]


def fitness(h_terms: list[PauliTerm], cand: list[PauliTerm], n: int) -> dict:
    """commutator_error + complexity_penalty (lower is better)."""
    err = commutator_norm(h_terms, cand, n)
    comp = float(len(cand)) + 0.5 * len({(t.x_mask, t.z_mask) for t in cand})
    return {"fitness": err + COMPLEXITY_W * comp, "commutator_error": err, "complexity": comp}


def random_conserved_search(h_terms: list[PauliTerm], n: int, budget: int,
                            n_terms: int, seed: int) -> dict:
    """Seeded pure-random baseline: return best candidate + throughput."""
    rng = np.random.default_rng(seed)
    best: dict | None = None
    t0 = time.perf_counter()
    for _ in range(budget):
        cand = sample_candidate(rng, n, n_terms)
        # Stage-0 analogue: bitwise prefilter before the dense norm.
        if n_terms == 1:
            t = cand[0]
            if not commutes_bitwise(h_terms, Pauli(t.x_mask, t.z_mask, 0, n)):
                continue
        out = fitness(h_terms, cand, n)
        if best is None or out["fitness"] < best["fitness"]:
            best = {"candidate": cand, **out}
    dt = max(time.perf_counter() - t0, 1e-9)
    assert best is not None
    return {**best, "budget": budget, "qps": budget / dt,
            "hamiltonian_hash": hamiltonian_hash(h_terms), "seed": seed}
