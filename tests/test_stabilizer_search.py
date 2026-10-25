"""Tests for stabilizer search reusing Q-Forge operators (P181)."""

from __future__ import annotations

import ast
from pathlib import Path
import unittest.mock

import numpy as np

from evobyte.qecc_verifier import check_stabilizer
from evobyte.stabilizer_search import (
    candidate_to_strings,
    crossover_stabilizer_sets,
    fitness_stabilizer_set,
    mutate_stabilizer_set,
    random_stabilizer_set,
    repair_commutation,
    strings_to_candidate,
)

REPO_ROOT = Path(__file__).resolve().parent.parent

# Known 5-qubit code generators [[5,1,3]]
FIVE_QUBIT_STRS = ["XZZXI", "IXZZX", "XIXZZ", "ZXIXZ"]


def test_repair_keeps_commuting_sets() -> None:
    """Test 1: Commuting set is strictly preserved; broken set is repaired or rejected."""
    cand = strings_to_candidate(FIVE_QUBIT_STRS)
    ok, fixed = repair_commutation(cand)
    assert ok is True
    assert np.array_equal(fixed, cand)

    # Intentionally break commutation by flipping 1 bit
    broken = cand.copy()
    broken[1, 0] ^= 1  # change first qubit of row 1
    ok_rep, fixed_rep = repair_commutation(broken)
    if ok_rep:
        # Check that fixed candidate is truly valid according to independent P179 verifier
        fixed_strs = candidate_to_strings(fixed_rep)
        ok_p179, payload = check_stabilizer(fixed_strs)
        assert ok_p179 is True, f"Repaired set failed P179 check: {payload}"
        assert payload["n"] == 5
        assert payload["k"] == 1
        assert not np.array_equal(fixed_rep, broken)
    else:
        # Honest rejection when repair cannot construct valid basis
        assert not np.array_equal(fixed_rep, broken)


def test_fitness_uses_p179_verifier_only() -> None:
    """Test 2: Fitness strictly delegates distance evaluation to P179 verifier."""
    cand = strings_to_candidate(FIVE_QUBIT_STRS)

    # Mock P179 returning d = 7 (arbitrary value to prove score comes from oracle)
    with unittest.mock.patch("evobyte.stabilizer_search.code_distance") as mock_dist:
        mock_dist.return_value = (True, {"n": 5, "k": 1, "d": 7})
        score, is_rec = fitness_stabilizer_set(cand, n=5, k=1, best_known_value=3)
        assert mock_dist.called
        assert score == 7.0
        assert is_rec is True

    # Mock P179 returning failure
    with unittest.mock.patch("evobyte.stabilizer_search.code_distance") as mock_dist:
        mock_dist.return_value = (False, "invalid code")
        score, is_rec = fitness_stabilizer_set(cand, n=5, k=1, best_known_value=3)
        assert score == 0.0
        assert is_rec is False

    # Malformed candidate returns 0.0 without querying verifier
    with unittest.mock.patch("evobyte.stabilizer_search.code_distance") as mock_dist:
        bad_cand = np.zeros((1, 3))  # odd dimension
        score, is_rec = fitness_stabilizer_set(bad_cand, n=5, k=1)
        assert score == 0.0
        assert is_rec is False
        assert not mock_dist.called


def test_mutation_crossover_preserve_shape() -> None:
    """Test 3: Mutation and crossover preserve (n-k) x 2n shape and are deterministic with fixed seed."""
    cand_a = strings_to_candidate(FIVE_QUBIT_STRS)
    cand_b = strings_to_candidate(FIVE_QUBIT_STRS)
    expected_shape = (4, 10)

    rng1 = np.random.default_rng(181)
    mut1 = mutate_stabilizer_set(cand_a, rng1)
    assert mut1.shape == expected_shape

    rng2 = np.random.default_rng(181)
    mut2 = mutate_stabilizer_set(cand_a, rng2)
    assert np.array_equal(mut1, mut2)

    rng_x = np.random.default_rng(42)
    child_a, child_b = crossover_stabilizer_sets(cand_a, cand_b, rng_x)
    assert child_a.shape == expected_shape
    assert child_b.shape == expected_shape


def test_malformed_rejected() -> None:
    """Test 4: Malformed inputs (dimension, symbol, k > n) are rejected without exceptions."""
    # 1D array
    ok, _ = repair_commutation(np.zeros(10))
    assert ok is False

    # Odd second dimension
    ok, _ = repair_commutation(np.zeros((2, 7)))
    assert ok is False

    # Invalid symbols outside {0, 1}
    bad_sym = np.zeros((2, 8), dtype=int)
    bad_sym[0, 0] = 2
    ok, _ = repair_commutation(bad_sym)
    assert ok is False

    # k < 0 (m > n)
    too_many_rows = np.zeros((6, 10), dtype=np.uint8)  # m=6 > n=5 -> k=-1
    ok, _ = repair_commutation(too_many_rows)
    assert ok is False

    # None, strings, empty
    assert repair_commutation(None)[0] is False
    assert repair_commutation("not an array")[0] is False
    assert repair_commutation([])[0] is False


def test_qforge_operators_reused() -> None:
    """Test 5: stabilizer_search imports and invokes Q-Forge evolution/pauli operators."""
    src_file = REPO_ROOT / "src" / "evobyte" / "stabilizer_search.py"
    tree = ast.parse(src_file.read_text(encoding="utf-8"))

    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)

    assert "evobyte.quantum.pauli" in imports
    assert "evobyte.quantum.evolution_q" in imports

    cand = strings_to_candidate(FIVE_QUBIT_STRS)
    rng = np.random.default_rng(42)

    # Verify mutate_candidate call delegation
    with unittest.mock.patch("evobyte.stabilizer_search.mutate_candidate") as mock_mut:
        mock_mut.side_effect = lambda terms, **kwargs: terms
        mutate_stabilizer_set(cand, rng)
        assert mock_mut.called

    # Verify crossover_candidates call delegation
    with unittest.mock.patch("evobyte.stabilizer_search.crossover_candidates") as mock_cross:
        mock_cross.side_effect = lambda t_a, t_b, **kwargs: (t_a, t_b)
        crossover_stabilizer_sets(cand, cand, rng)
        assert mock_cross.called

    # Verify commutes_with call delegation
    with unittest.mock.patch("evobyte.stabilizer_search.commutes_with") as mock_comm:
        mock_comm.return_value = True
        repair_commutation(cand)
        assert mock_comm.called
