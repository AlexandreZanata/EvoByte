"""Testes das 12 características simétricas (F04-T01)."""

from __future__ import annotations

import math
import random

import pytest

from evobyte.candidate import create_candidate
from evobyte.policy.features import (
    FEATURE_NAMES,
    FEATURES_VERSION,
    FeatureError,
    compute_features,
)


def test_feature_specification_metadata():
    assert len(FEATURE_NAMES) == 12
    assert len(set(FEATURE_NAMES)) == 12
    assert FEATURES_VERSION == "symmetric-12-v1"


def test_empty_graph_features_are_calculated_manually():
    candidate = create_candidate(n=8, edges=[])
    result = compute_features(candidate, (0, 1))

    expected = (
        0.25,
        0.0,
        1.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        -1.0 / 28.0,
        1.0,
    )
    assert result.version == FEATURES_VERSION
    assert len(result.values) == 12
    assert result.values == pytest.approx(expected)
    assert all(math.isfinite(value) for value in result.values)
    assert result.cost.legal_mask_queries == 2
    assert result.cost.bfs_queries == 1


def test_two_component_features_are_calculated_manually():
    candidate = create_candidate(n=8, edges=[[0, 1], [2, 3]])
    result = compute_features(candidate, (0, 2))

    expected = (
        0.25,
        1.0 / 14.0,
        13.0 / 14.0,
        1.0 / 196.0,
        0.0,
        1.0 / 7.0,
        1.0 / 7.0,
        1.0 / 7.0,
        1.0 / 49.0,
        1.0 / 49.0,
        -1.0 / 7.0,
        1.0,
    )
    assert result.values == pytest.approx(expected)
    assert result.cost.legal_mask_queries == 2
    assert result.cost.bfs_queries == 1


def test_connected_distance_feature():
    candidate = create_candidate(
        n=8,
        edges=[[0, 1], [1, 2], [2, 3], [3, 4]],
    )
    result = compute_features(candidate, (0, 4))

    assert result.values[11] == pytest.approx(4.0 / 8.0)


def test_swapping_action_extremes_does_not_change_vector():
    candidate = create_candidate(n=8, edges=[[0, 1], [2, 3]])

    forward = compute_features(candidate, (0, 2))
    reverse = compute_features(candidate, (2, 0))

    assert forward.values == reverse.values
    assert forward.version == reverse.version
    assert forward.cost == reverse.cost


def test_features_are_exactly_invariant_under_100_permutations():
    candidate = create_candidate(n=8, edges=[[0, 1], [2, 3]])
    base = compute_features(candidate, (0, 2))
    rng = random.Random(2026)

    for _ in range(100):
        permutation = list(range(8))
        rng.shuffle(permutation)
        edges = [
            tuple(sorted((permutation[u], permutation[v])))
            for u, v in candidate.payload["edges"]
        ]
        permuted = create_candidate(n=8, edges=edges)
        action = (permutation[0], permutation[2])
        result = compute_features(permuted, action)

        assert result.values == base.values
        assert result.version == base.version
        assert result.cost == base.cost


def test_computation_does_not_modify_candidate():
    candidate = create_candidate(n=8, edges=[[0, 1], [2, 3]])
    before_payload = {
        key: value
        for key, value in candidate.payload.items()
    }
    before_bytes = candidate.canonical_bytes

    compute_features(candidate, (0, 2))

    assert candidate.payload == before_payload
    assert candidate.canonical_bytes == before_bytes


def test_action_must_be_legal():
    candidate = create_candidate(n=8, edges=[[0, 1], [2, 3]])
    path = create_candidate(
        n=8,
        edges=[[0, 1], [1, 2], [2, 3], [3, 4]],
    )

    for item, action in (
        (candidate, (0, 1)),
        (path, (0, 2)),
        (candidate, (0, 0)),
        (candidate, (0, 8)),
        (candidate, (0,)),
        (candidate, (0, "1")),
    ):
        with pytest.raises(FeatureError) as exc:
            compute_features(item, action)
        assert exc.value.code == "INVALID_ACTION"


def test_n_below_eight_is_rejected():
    candidate = create_candidate(n=7, edges=[])

    with pytest.raises(FeatureError) as exc:
        compute_features(candidate, (0, 1))

    assert exc.value.code == "INVALID_N"


def test_invalid_candidate_is_rejected():
    candidate = create_candidate(
        n=8,
        edges=[[0, 1], [1, 2], [2, 0]],
    )

    with pytest.raises(FeatureError) as exc:
        compute_features(candidate, (0, 1))

    assert exc.value.code == "INVALID_CANDIDATE"


def test_invalid_candidate_type_is_rejected():
    with pytest.raises(FeatureError) as exc:
        compute_features(None, (0, 1))

    assert exc.value.code == "INVALID_CANDIDATE_TYPE"
