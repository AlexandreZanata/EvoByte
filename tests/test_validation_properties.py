"""Propriedades, casos fixos e sensibilidade dos verificadores (F01-T05)."""

from __future__ import annotations

from dataclasses import replace
from itertools import combinations
import random

import pytest

from evobyte.validation.reference import validate as validate_reference
from evobyte.validation.runtime import validate as validate_runtime


def make_payload(n, edges, claimed_m=None):
    return {
        "schema_version": 1,
        "rules_id": "girth-ge-5-v1",
        "n": n,
        "edges": [list(edge) for edge in edges],
        "claimed_m": len(edges) if claimed_m is None else claimed_m,
    }


def validate_both(raw_payload, expected_n):
    return (
        validate_reference(raw_payload, expected_n),
        validate_runtime(raw_payload, expected_n),
    )


def assert_agreement(raw_payload, expected_n, expected_valid=None):
    reference_result, runtime_result = validate_both(raw_payload, expected_n)
    context = {"n": expected_n, "edges": raw_payload.get("edges")}

    assert reference_result.valid == runtime_result.valid, context
    assert reference_result.computed_m == runtime_result.computed_m, context
    assert bool(reference_result.violations) == (not reference_result.valid), context
    assert bool(runtime_result.violations) == (not runtime_result.valid), context

    if expected_valid is not None:
        assert reference_result.valid is expected_valid, context
        assert runtime_result.valid is expected_valid, context


def random_edges(rng, n, probability):
    return [
        (u, v)
        for u, v in combinations(range(n), 2)
        if rng.random() < probability
    ]


def permuted_edges(edges, permutation):
    return [
        tuple(sorted((permutation[u], permutation[v])))
        for u, v in edges
    ]


FIXED_CASES = [
    ("empty", 8, [], True),
    ("single_vertex", 1, [], True),
    ("path", 6, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)], True),
    ("c5", 5, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)], True),
    ("c6", 6, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)], True),
    ("c3", 5, [(0, 1), (1, 2), (2, 0)], False),
    ("c4", 5, [(0, 1), (1, 2), (2, 3), (3, 0)], False),
    ("c4_with_chord", 5, [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)], False),
    ("c4_non_adjacent_pair", 4, [(0, 2), (0, 3), (1, 2), (1, 3)], False),
    ("k4", 4, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)], False),
]


@pytest.mark.parametrize(
    "case",
    FIXED_CASES,
    ids=[case[0] for case in FIXED_CASES],
)
def test_fixed_cases_agree_with_expected_verdict(case):
    _, n, edges, expected_valid = case
    payload = make_payload(n, edges)
    assert_agreement(payload, n, expected_valid=expected_valid)


MALFORMED_CASES = [
    ("loop", 5, [(2, 2)], 1),
    ("duplicate", 5, [(0, 1), (0, 1)], 2),
    ("reversed_duplicate", 5, [(0, 1), (1, 0)], 2),
    ("out_of_bounds", 5, [(0, 5)], 1),
    ("claimed_m_mismatch", 5, [(0, 1)], 2),
]


@pytest.mark.parametrize(
    "case",
    MALFORMED_CASES,
    ids=[case[0] for case in MALFORMED_CASES],
)
def test_malformed_cases_are_rejected_by_both(case):
    _, n, edges, claimed_m = case
    payload = make_payload(n, edges, claimed_m=claimed_m)
    assert_agreement(payload, n, expected_valid=False)


@pytest.mark.parametrize("seed", [0, 1, 7, 42, 12345])
@pytest.mark.parametrize("n", [2, 3, 5, 8, 12])
@pytest.mark.parametrize("probability", [0.1, 0.3, 0.6])
def test_random_graphs_agree(seed, n, probability):
    rng = random.Random(seed * 10000 + n * 100 + int(probability * 10))
    edges = random_edges(rng, n, probability)
    payload = make_payload(n, edges)
    assert_agreement(payload, n)

    reference_result, _ = validate_both(payload, n)
    for _ in range(3):
        permutation = list(range(n))
        rng.shuffle(permutation)
        permuted = permuted_edges(edges, permutation)
        permuted_payload = make_payload(n, permuted)
        assert_agreement(
            permuted_payload,
            n,
            expected_valid=reference_result.valid,
        )


def test_permuting_c5_keeps_validity_and_count():
    edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]
    payload = make_payload(5, edges)
    reference_result, runtime_result = validate_both(payload, 5)
    assert reference_result.valid is True
    assert runtime_result.valid is True
    assert reference_result.computed_m == runtime_result.computed_m == 5

    for permutation in ([1, 2, 3, 4, 0], [4, 3, 2, 1, 0], [2, 0, 4, 1, 3]):
        permuted = permuted_edges(edges, permutation)
        permuted_payload = make_payload(5, permuted)
        assert_agreement(permuted_payload, 5, expected_valid=True)
        reference_permuted, runtime_permuted = validate_both(permuted_payload, 5)
        assert reference_permuted.computed_m == runtime_permuted.computed_m == 5


def test_inserting_c3_in_c5_is_rejected_by_both():
    valid_edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]
    assert_agreement(make_payload(5, valid_edges), 5, expected_valid=True)

    with_triangle = valid_edges + [(0, 2)]
    payload = make_payload(5, with_triangle)
    reference_result, runtime_result = validate_both(payload, 5)

    assert reference_result.valid is False
    assert runtime_result.valid is False
    assert "C3_DETECTED" in {
        violation.code for violation in reference_result.violations
    }
    assert "C3_DETECTED" in {
        violation.code for violation in runtime_result.violations
    }


def test_deliberate_inverted_verdict_is_detected():
    payload = make_payload(5, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)])
    reference_result, _ = validate_both(payload, 5)
    broken = replace(reference_result, valid=not reference_result.valid)

    with pytest.raises(AssertionError):
        assert reference_result.valid == broken.valid


def test_deliberate_missing_c4_is_detected():
    payload = make_payload(5, [(0, 1), (1, 2), (2, 3), (3, 0)])
    reference_result, _ = validate_both(payload, 5)
    without_c4 = tuple(
        violation
        for violation in reference_result.violations
        if violation.code != "C4_DETECTED"
    )
    broken = replace(
        reference_result,
        valid=not without_c4,
        violations=without_c4,
    )

    with pytest.raises(AssertionError):
        assert reference_result.valid == broken.valid


def test_deliberate_missing_c3_is_detected():
    payload = make_payload(5, [(0, 1), (1, 2), (2, 0)])
    reference_result, _ = validate_both(payload, 5)
    without_c3 = tuple(
        violation
        for violation in reference_result.violations
        if violation.code != "C3_DETECTED"
    )
    broken = replace(
        reference_result,
        valid=not without_c3,
        violations=without_c3,
    )

    with pytest.raises(AssertionError):
        assert reference_result.valid == broken.valid
