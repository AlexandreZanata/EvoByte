"""Stabilizer-set search reusing Q-Forge operators (P181).

Implements evolutionary search for quantum stabilizer codes [[n,k,d]] over
symplectic binary matrices (n-k) x 2n, reusing Q-Forge operators from
evobyte.quantum.pauli and evobyte.quantum.evolution_q, with fitness evaluated
strictly by the independent P179 QECC verifier.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from evobyte.qecc_verifier import check_stabilizer, code_distance
from evobyte.quantum.evolution_q import (
    crossover_candidates,
    mutate_candidate,
    tournament_select,
)
from evobyte.quantum.hamiltonians import PauliTerm
from evobyte.quantum.pauli import Pauli, commutes_with


def _gf2_solve(m_mat: np.ndarray, s_vec: np.ndarray) -> np.ndarray | None:
    """Solve M @ x = s over GF(2) via Gaussian elimination."""
    nrows, ncols = m_mat.shape
    aug = np.hstack([m_mat.copy(), s_vec.reshape(-1, 1)]).astype(np.uint8)

    pivot_cols: list[int] = []
    r = 0
    for c in range(ncols):
        if r >= nrows:
            break
        piv = np.where(aug[r:, c] == 1)[0]
        if len(piv) == 0:
            continue
        piv_row = r + piv[0]
        if piv_row != r:
            aug[[r, piv_row]] = aug[[piv_row, r]]
        pivot_cols.append(c)
        for i in range(nrows):
            if i != r and aug[i, c] == 1:
                aug[i] ^= aug[r]
        r += 1

    for i in range(r, nrows):
        if aug[i, -1] == 1:
            return None

    x = np.zeros(ncols, dtype=np.uint8)
    for i, c in enumerate(pivot_cols):
        x[c] = aug[i, -1]
    return x


def _gf2_rank(rows: list[np.ndarray] | np.ndarray) -> int:
    """Compute rank of binary matrix over GF(2)."""
    if len(rows) == 0:
        return 0
    m_mat = np.array(rows, dtype=np.uint8).copy()
    r = 0
    nrows, ncols = m_mat.shape
    for c in range(ncols):
        if r >= nrows:
            break
        piv = np.where(m_mat[r:, c] == 1)[0]
        if len(piv) == 0:
            continue
        piv_row = r + piv[0]
        if piv_row != r:
            m_mat[[r, piv_row]] = m_mat[[piv_row, r]]
        for i in range(nrows):
            if i != r and m_mat[i, c] == 1:
                m_mat[i] ^= m_mat[r]
        r += 1
    return r


def candidate_to_strings(candidate: np.ndarray) -> list[str]:
    """Convert binary matrix of shape (m, 2n) into list of Pauli strings."""
    m, d2 = candidate.shape
    n = d2 // 2
    mapping = {(0, 0): "I", (1, 0): "X", (0, 1): "Z", (1, 1): "Y"}
    strings = []
    for i in range(m):
        row = candidate[i]
        s = "".join(mapping[(int(row[q]), int(row[n + q]))] for q in range(n))
        strings.append(s)
    return strings


def strings_to_candidate(strings: list[str]) -> np.ndarray:
    """Convert list of Pauli strings into binary matrix of shape (m, 2n)."""
    m = len(strings)
    if m == 0:
        raise ValueError("strings cannot be empty")
    n = len(strings[0])
    mapping = {"I": (0, 0), "X": (1, 0), "Z": (0, 1), "Y": (1, 1)}
    cand = np.zeros((m, 2 * n), dtype=np.uint8)
    for i, s in enumerate(strings):
        if len(s) != n:
            raise ValueError("inconsistent string length")
        for q, c in enumerate(s):
            x, z = mapping[c]
            cand[i, q] = x
            cand[i, n + q] = z
    return cand


def candidate_to_paulis(candidate: np.ndarray) -> list[Pauli]:
    """Convert binary matrix into Q-Forge Pauli objects."""
    m, d2 = candidate.shape
    n = d2 // 2
    paulis = []
    for i in range(m):
        row = candidate[i]
        xm = 0
        zm = 0
        for q in range(n):
            if row[q]:
                xm |= 1 << q
            if row[n + q]:
                zm |= 1 << q
        phase = (xm & zm).bit_count() % 4
        paulis.append(Pauli(x_mask=xm, z_mask=zm, phase=phase, n_qubits=n))
    return paulis


def candidate_to_terms(candidate: np.ndarray) -> list[PauliTerm]:
    """Convert binary matrix into Q-Forge PauliTerms."""
    m, d2 = candidate.shape
    n = d2 // 2
    terms = []
    for i in range(m):
        row = candidate[i]
        xm = 0
        zm = 0
        for q in range(n):
            if row[q]:
                xm |= 1 << q
            if row[n + q]:
                zm |= 1 << q
        phase = (xm & zm).bit_count() % 4
        terms.append(PauliTerm(coeff=1.0, x_mask=xm, z_mask=zm, phase=phase))
    return terms


def terms_to_candidate(terms: list[PauliTerm], n: int) -> np.ndarray:
    """Convert list of Q-Forge PauliTerms back to binary matrix of shape (m, 2n)."""
    m = len(terms)
    cand = np.zeros((m, 2 * n), dtype=np.uint8)
    for i, t in enumerate(terms):
        for q in range(n):
            if (t.x_mask >> q) & 1:
                cand[i, q] = 1
            if (t.z_mask >> q) & 1:
                cand[i, n + q] = 1
    return cand


def repair_commutation(candidate: Any) -> tuple[bool, np.ndarray]:
    """Verify and repair commutation of stabilizer candidate using GF(2) linear algebra.

    Returns (ok, fixed). If candidate is already commuting and independent,
    returns (True, copy). If commutation can be repaired, returns (True, fixed).
    If malformed or irrepairable, returns (False, candidate).
    """
    try:
        arr = np.asarray(candidate)
    except Exception:
        return False, candidate

    if arr.ndim != 2 or arr.size == 0:
        return False, arr
    if arr.shape[1] % 2 != 0:
        return False, arr

    m, d2 = arr.shape
    n = d2 // 2
    k = n - m
    if k < 0 or k >= n:
        return False, arr

    if np.any((arr != 0) & (arr != 1)):
        return False, arr

    cand = arr.astype(np.uint8)

    # 1. Fast check: is it already mutually commuting and rank m?
    paulis = candidate_to_paulis(cand)
    all_commute = True
    for i in range(m):
        for j in range(i + 1, m):
            if not commutes_with(paulis[i], paulis[j]):
                all_commute = False
                break
        if not all_commute:
            break

    if all_commute and _gf2_rank(cand) == m:
        return True, cand.copy()

    # 2. Sequential GF(2) symplectic syndrome projection
    basis: list[np.ndarray] = []
    for i in range(m):
        g = cand[i].copy()
        if len(basis) > 0:
            m_mat = np.zeros((len(basis), 2 * n), dtype=np.uint8)
            for j, b in enumerate(basis):
                m_mat[j, :n] = b[n:]
                m_mat[j, n:] = b[:n]
            synd = (m_mat @ g) % 2
            if np.any(synd):
                delta = _gf2_solve(m_mat, synd)
                if delta is None:
                    return False, cand
                g = (g ^ delta) % 2

        if np.all(g == 0):
            return False, cand
        if _gf2_rank(basis + [g]) != len(basis) + 1:
            return False, cand
        basis.append(g)

    fixed = np.array(basis, dtype=np.uint8)
    return True, fixed


def random_stabilizer_set(n: int, k: int, rng: np.random.Generator) -> np.ndarray:
    """Generate a random valid stabilizer candidate matrix of shape (n-k, 2n)."""
    if n <= 0 or k < 0 or k >= n:
        raise ValueError(f"Invalid parameters n={n}, k={k}")
    m = n - k

    for _ in range(100):
        cand = rng.integers(0, 2, size=(m, 2 * n), dtype=np.uint8)
        ok, fixed = repair_commutation(cand)
        if ok:
            return fixed

    # Deterministic fallback: diagonal X and Z generators
    fallback = np.zeros((m, 2 * n), dtype=np.uint8)
    for i in range(m):
        fallback[i, i] = 1
    return fallback


def mutate_stabilizer_set(
    candidate: np.ndarray, rng: np.random.Generator, p_term: float = 0.5
) -> np.ndarray:
    """Mutate candidate matrix using Q-Forge's mutate_candidate operator."""
    m, d2 = candidate.shape
    n = d2 // 2
    terms = candidate_to_terms(candidate)
    mutated_terms = mutate_candidate(terms, n_qubits=n, rng=rng, p_term=p_term, p_replace=0.0)
    return terms_to_candidate(mutated_terms, n)


def crossover_stabilizer_sets(
    a: np.ndarray, b: np.ndarray, rng: np.random.Generator
) -> tuple[np.ndarray, np.ndarray]:
    """Crossover two stabilizer candidates using Q-Forge's crossover_candidates operator."""
    if a.shape != b.shape:
        raise ValueError("Candidate shapes must match for crossover")
    d2 = a.shape[1]
    n = d2 // 2
    terms_a = candidate_to_terms(a)
    terms_b = candidate_to_terms(b)
    child_terms_a, child_terms_b = crossover_candidates(terms_a, terms_b, rng=rng)
    return terms_to_candidate(child_terms_a, n), terms_to_candidate(child_terms_b, n)


def fitness_stabilizer_set(
    candidate: Any, n: int, k: int, best_known_value: int = 0
) -> tuple[float, bool]:
    """Lexicographic fitness for stabilizer candidate.

    Returns (score, is_record_candidate):
    score = exact d computed by P179 verifier (0.0 if invalid);
    is_record_candidate = True if valid and d > best_known_value.
    """
    ok, fixed = repair_commutation(candidate)
    if not ok:
        return 0.0, False

    strings = candidate_to_strings(fixed)
    ok_dist, res = code_distance(strings)
    if not ok_dist or not isinstance(res, dict):
        return 0.0, False

    d = float(res.get("d", 0))
    is_record = bool(d > best_known_value)
    return d, is_record
