"""Pauli search engine (spec: docs/quantum/REPRESENTATION.md, Q04 scope).

Candidate layout: list of [coeff_id, x_mask, z_mask] terms (n_terms in {1, 2, 4, 8, 16}).
Samplers: pure (uniform random bits) vs structured (1-local and 2-local physical operators).
Fitness: commutator_error + complexity_penalty.
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


def encode_candidate(cand: list[PauliTerm]) -> list[tuple[int, int, int]]:
    """Encode PauliTerm candidate into list of (coeff_id, x_mask, z_mask) tuples."""
    encoded = []
    for term in cand:
        try:
            coeff_id = COEFF_BANK.index(term.coeff)
        except ValueError:
            # Pick closest coefficient in bank
            coeff_id = int(np.argmin([abs(c - term.coeff) for c in COEFF_BANK]))
        encoded.append((coeff_id, term.x_mask, term.z_mask))
    return encoded


def decode_candidate(encoded: list[tuple[int, int, int]], n_qubits: int) -> list[PauliTerm]:
    """Decode list of (coeff_id, x_mask, z_mask) tuples into PauliTerm list."""
    terms = []
    for coeff_id, x_mask, z_mask in encoded:
        if not (0 <= coeff_id < len(COEFF_BANK)):
            raise ValueError(f"coeff_id {coeff_id} out of range [0, {len(COEFF_BANK)})")
        if x_mask < 0 or z_mask < 0:
            raise ValueError("masks must be non-negative")
        if (x_mask >> n_qubits) or (z_mask >> n_qubits):
            raise ValueError(f"mask exceeds n_qubits={n_qubits} width")
        coeff = COEFF_BANK[coeff_id]
        phase = (x_mask & z_mask).bit_count() % 4
        terms.append(PauliTerm(coeff, x_mask, z_mask, phase))
    return terms


def sample_pure_term(rng: np.random.Generator, n_qubits: int) -> PauliTerm:
    """Uniform random Pauli string with a bank coefficient."""
    x = int(rng.integers(0, 1 << n_qubits))
    z = int(rng.integers(0, 1 << n_qubits))
    coeff_id = int(rng.integers(0, len(COEFF_BANK)))
    c = COEFF_BANK[coeff_id]
    phase = (x & z).bit_count() % 4
    return PauliTerm(c, x, z, phase)


def sample_structured_term(rng: np.random.Generator, n_qubits: int) -> PauliTerm:
    """Sample structured Pauli term biased towards 1-local and 2-local physical operators."""
    coeff_id = int(rng.integers(0, len(COEFF_BANK)))
    c = COEFF_BANK[coeff_id]
    if n_qubits <= 1:
        kind = ("X", "Y", "Z")[int(rng.integers(0, 3))]
        xm = 1 if kind in ("X", "Y") else 0
        zm = 1 if kind in ("Z", "Y") else 0
        phase = (xm & zm).bit_count() % 4
        return PauliTerm(c, xm, zm, phase)

    mode = int(rng.integers(0, 3))
    if mode == 0:
        # 1-local single-qubit Pauli
        q = int(rng.integers(0, n_qubits))
        kind = ("X", "Y", "Z")[int(rng.integers(0, 3))]
        xm = (1 << q) if kind in ("X", "Y") else 0
        zm = (1 << q) if kind in ("Z", "Y") else 0
    elif mode == 1:
        # 2-local nearest-neighbor bond
        q = int(rng.integers(0, n_qubits - 1))
        kind = ("X", "Y", "Z")[int(rng.integers(0, 3))]
        xm = ((1 << q) | (1 << (q + 1))) if kind in ("X", "Y") else 0
        zm = ((1 << q) | (1 << (q + 1))) if kind in ("Z", "Y") else 0
    else:
        # 2-local arbitrary pair
        q1, q2 = sorted(rng.choice(n_qubits, size=2, replace=False))
        kind = ("X", "Y", "Z")[int(rng.integers(0, 3))]
        xm = ((1 << q1) | (1 << q2)) if kind in ("X", "Y") else 0
        zm = ((1 << q1) | (1 << q2)) if kind in ("Z", "Y") else 0

    phase = (xm & zm).bit_count() % 4
    return PauliTerm(c, xm, zm, phase)


def sample_candidate(
    rng: np.random.Generator, n_qubits: int, n_terms: int, structured: bool = False
) -> list[PauliTerm]:
    """Random operator candidate with exactly n_terms (pure or structured)."""
    if n_terms not in (1, 2, 4, 8, 16):
        raise ValueError(f"n_terms must be in {{1,2,4,8,16}}, got {n_terms}")
    sampler = sample_structured_term if structured else sample_pure_term
    return [sampler(rng, n_qubits) for _ in range(n_terms)]


def sample_term(rng: np.random.Generator, n_qubits: int) -> PauliTerm:
    """Legacy alias for sample_pure_term."""
    return sample_pure_term(rng, n_qubits)


def fitness(h_terms: list[PauliTerm], cand: list[PauliTerm], n: int) -> dict:
    """commutator_error + complexity_penalty (lower is better)."""
    err = commutator_norm(h_terms, cand, n)
    comp = float(len(cand)) + 0.5 * len({(t.x_mask, t.z_mask) for t in cand})
    return {"fitness": err + COMPLEXITY_W * comp, "commutator_error": err, "complexity": comp}


def random_conserved_search(
    h_terms: list[PauliTerm],
    n: int,
    budget: int,
    n_terms: int = 1,
    seed: int = 0,
    structured: bool = False,
) -> dict:
    """Seeded random search baseline (pure or structured): return best candidate + throughput."""
    rng = np.random.default_rng(seed)
    best: dict | None = None
    t0 = time.perf_counter()
    for _ in range(budget):
        cand = sample_candidate(rng, n, n_terms, structured=structured)
        # Stage-0 analogue: bitwise prefilter before the dense norm.
        if n_terms == 1:
            t = cand[0]
            if not commutes_bitwise(h_terms, Pauli(t.x_mask, t.z_mask, t.phase, n)):
                continue
        out = fitness(h_terms, cand, n)
        if best is None or out["fitness"] < best["fitness"]:
            best = {"candidate": cand, **out}
    dt = max(time.perf_counter() - t0, 1e-9)
    if best is None:
        cand = sample_candidate(rng, n, n_terms, structured=structured)
        out = fitness(h_terms, cand, n)
        best = {"candidate": cand, **out}
    return {
        **best,
        "budget": budget,
        "qps": budget / dt,
        "hamiltonian_hash": hamiltonian_hash(h_terms),
        "seed": seed,
        "sampler": "structured" if structured else "pure",
        "n_terms": n_terms,
    }
