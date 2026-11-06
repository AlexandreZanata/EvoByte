"""Testes da máscara de adições legais (F03-T01)."""

from __future__ import annotations

from itertools import combinations
import random

import pytest

from evobyte.candidate import (
    Candidate,
    canonical_json_bytes,
    compute_content_sha256,
    create_candidate,
)
from evobyte.search.actions import LegalActionsError, legal_additions
from evobyte.validation.reference import validate as validate_reference


def make_payload(n, edges):
    return {
        "schema_version": 1,
        "rules_id": "girth-ge-5-v1",
        "n": n,
        "edges": [list(edge) for edge in edges],
        "claimed_m": len(edges),
    }


def add_pair(payload, pair):
    u, v = sorted(pair)
    edges = [list(edge) for edge in payload["edges"]] + [[u, v]]
    edges.sort()
    return {
        "schema_version": payload["schema_version"],
        "rules_id": payload["rules_id"],
        "n": payload["n"],
        "edges": edges,
        "claimed_m": len(edges),
    }


def absent_pairs(n, edges):
    existing = {tuple(sorted(edge)) for edge in edges}
    return [
        pair
        for pair in combinations(range(n), 2)
        if pair not in existing
    ]


def test_empty_graph_has_all_pairs_legal():
    candidate = create_candidate(n=5, edges=[])

    assert legal_additions(candidate) == tuple(combinations(range(5), 2))


def test_path_additions_are_forbidden_at_distance_two_and_three():
    candidate = create_candidate(n=4, edges=[[0, 1], [1, 2], [2, 3]])

    assert legal_additions(candidate) == ()
    assert (0, 3) not in legal_additions(candidate)


def test_path_of_five_allows_only_distance_four():
    candidate = create_candidate(
        n=5,
        edges=[[0, 1], [1, 2], [2, 3], [3, 4]],
    )

    assert legal_additions(candidate) == ((0, 4),)
    assert validate_reference(
        add_pair(candidate.payload, (0, 4)),
        5,
    ).valid is True


def test_c5_has_no_legal_addition():
    candidate = create_candidate(
        n=5,
        edges=[[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]],
    )

    assert legal_additions(candidate) == ()


def test_disconnected_components_allow_cross_edges():
    candidate = create_candidate(n=4, edges=[[0, 1], [2, 3]])

    assert legal_additions(candidate) == (
        (0, 2),
        (0, 3),
        (1, 2),
        (1, 3),
    )


def test_star_has_no_legal_addition():
    candidate = create_candidate(n=4, edges=[[0, 1], [0, 2], [0, 3]])

    assert legal_additions(candidate) == ()


def test_small_orders():
    assert legal_additions(create_candidate(n=1, edges=[])) == ()
    assert legal_additions(create_candidate(n=2, edges=[])) == ((0, 1),)
    assert legal_additions(create_candidate(n=2, edges=[[0, 1]])) == ()


def test_mask_does_not_mutate_candidate():
    candidate = create_candidate(
        n=8,
        edges=[[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]],
    )
    before_payload = {
        key: value
        for key, value in candidate.payload.items()
    }
    before_bytes = candidate.canonical_bytes

    legal_additions(candidate)

    assert candidate.payload == before_payload
    assert candidate.canonical_bytes == before_bytes


@pytest.mark.parametrize(
    "edges",
    [
        [[0, 1], [1, 2], [2, 0]],
        [[0, 1], [1, 2], [2, 3], [3, 0]],
        [[0, 1], [1, 2], [2, 3], [3, 0], [0, 2]],
    ],
    ids=["c3", "c4", "chorded-c4"],
)
def test_invalid_cycle_candidate_is_rejected(edges):
    candidate = create_candidate(n=5, edges=edges)

    with pytest.raises(LegalActionsError) as exc:
        legal_additions(candidate)

    assert exc.value.code == "INVALID_CANDIDATE"


def test_structurally_invalid_candidate_is_rejected():
    payload = make_payload(5, [])
    payload["edges"] = [[0, 0]]
    payload["claimed_m"] = 1
    canonical = canonical_json_bytes(payload)
    forged = Candidate(
        payload=payload,
        canonical_bytes=canonical,
        content_sha256=compute_content_sha256(canonical),
    )

    with pytest.raises(LegalActionsError) as exc:
        legal_additions(forged)

    assert exc.value.code == "INVALID_CANDIDATE"


def test_invalid_candidate_type_is_rejected():
    with pytest.raises(LegalActionsError) as exc:
        legal_additions(None)

    assert exc.value.code == "INVALID_CANDIDATE_TYPE"


def test_exhaustive_masks_match_reference_up_to_five():
    total = 0

    for n in range(1, 6):
        pairs = list(combinations(range(n), 2))
        for mask in range(1 << len(pairs)):
            edges = [
                list(pair)
                for index, pair in enumerate(pairs)
                if mask & (1 << index)
            ]
            payload = make_payload(n, edges)
            expected_result = validate_reference(payload, n)
            candidate = create_candidate(n=n, edges=edges)

            if not expected_result.valid:
                with pytest.raises(LegalActionsError) as exc:
                    legal_additions(candidate)
                assert exc.value.code == "INVALID_CANDIDATE"
                total += 1
                continue

            mask_actions = set(legal_additions(candidate))
            for pair in absent_pairs(n, edges):
                added = validate_reference(add_pair(payload, pair), n)
                assert (pair in mask_actions) == added.valid, (n, edges, pair)
            total += 1

    assert total == 1099


def random_valid_graph(rng, n):
    edges = set()
    for vertex in range(1, n):
        parent = rng.randrange(vertex)
        edges.add(tuple(sorted((vertex, parent))))

    attempts = 0
    while attempts < 12:
        attempts += 1
        pair = tuple(sorted(rng.sample(range(n), 2)))
        if pair in edges:
            continue
        candidate_edges = sorted(edges | {pair})
        if validate_reference(make_payload(n, candidate_edges), n).valid:
            edges.add(pair)

    return sorted(edges)


def sample_absent_pairs(rng, n, edges, mask_actions, limit=30):
    absent = absent_pairs(n, edges)
    inside = [pair for pair in absent if pair in mask_actions]
    outside = [pair for pair in absent if pair not in mask_actions]
    picked = []
    picked.extend(rng.sample(inside, min(limit, len(inside))))
    picked.extend(rng.sample(outside, min(limit, len(outside))))
    return picked


@pytest.mark.parametrize("n", [8, 12, 16, 24, 32])
@pytest.mark.parametrize("seed", [0, 1])
def test_random_valid_graphs_agree_with_reference(n, seed):
    rng = random.Random(seed * 1000 + n)
    edges = random_valid_graph(rng, n)
    payload = make_payload(n, edges)
    assert validate_reference(payload, n).valid is True
    candidate = create_candidate(n=n, edges=edges)

    mask_actions = set(legal_additions(candidate))
    if n <= 16:
        pairs_to_check = absent_pairs(n, edges)
    else:
        pairs_to_check = sample_absent_pairs(rng, n, edges, mask_actions)

    for pair in pairs_to_check:
        added = validate_reference(add_pair(payload, pair), n)
        assert (pair in mask_actions) == added.valid, (n, seed, pair)


def test_mask_is_equivariant_under_permutations():
    base_edges = [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]
    candidate = create_candidate(n=8, edges=base_edges)
    base_mask = set(legal_additions(candidate))

    for permutation in (
        [3, 1, 7, 0, 5, 2, 6, 4],
        [7, 6, 5, 4, 3, 2, 1, 0],
        [1, 2, 3, 4, 5, 6, 7, 0],
    ):
        permuted_edges = [
            tuple(sorted((permutation[u], permutation[v])))
            for u, v in base_edges
        ]
        permuted = create_candidate(n=8, edges=permuted_edges)
        permuted_mask = set(legal_additions(permuted))
        expected = {
            tuple(sorted((permutation[u], permutation[v])))
            for u, v in base_mask
        }
        assert permuted_mask == expected
