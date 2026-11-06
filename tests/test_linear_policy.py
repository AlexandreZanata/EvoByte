"""Testes do ajuste ridge e do seletor linear (F04-T03)."""

from __future__ import annotations

import json
import math
import random
import sys
import numpy as np
import pytest

from evobyte.budget import Budget
from evobyte.candidate import create_candidate
from evobyte.policy.data import TrainingCounters, TrainingDataset
from evobyte.policy.features import FEATURES_VERSION, compute_features
@pytest.fixture(scope="module", autouse=True)
def _drop_numpy_after_policy_tests():
    yield
    for name in list(sys.modules):
        if name == "numpy" or name.startswith("numpy."):
            del sys.modules[name]


from evobyte.policy.linear import (
    LinearPolicy,
    LinearPolicyError,
    TrainingFailure,
    fit_linear_policy,
    policy_hash,
)


class StepClock:
    def __init__(self, start=0.0, step=0.01):
        self.value = start
        self.step = step

    def __call__(self):
        current = self.value
        self.value += self.step
        return current


class CountdownClock:
    def __init__(self, true_calls):
        self.remaining = true_calls

    def __call__(self):
        self.remaining -= 1
        return 0.0 if self.remaining >= 0 else 1000.0


class SpyRng:
    def __init__(self, index=0):
        self.index = index
        self.options = None

    def choice(self, options):
        self.options = list(options)
        return self.options[self.index % len(self.options)]


def make_budget(limit=60.0, step=0.01):
    return Budget(0.0, limit, StepClock(0.0, step))


def synthetic_pairs(count=40, seed=0):
    rng = random.Random(seed)
    pairs = []
    rows = []
    targets = []
    for _ in range(count):
        x = tuple(rng.uniform(-1.0, 1.0) for _ in range(12))
        y = 2.0 * x[0] - x[1] + 0.5
        pairs.append((x, y))
        rows.append(x)
        targets.append(y)
    return pairs, np.asarray(rows), np.asarray(targets)


def zero_weights():
    return tuple(0.0 for _ in range(12))


def feature8_weights():
    weights = [0.0] * 12
    weights[7] = 1.0
    return tuple(weights)


def make_policy(weights):
    intercept = 0.0
    return LinearPolicy(
        weights=weights,
        intercept=intercept,
        features_version=FEATURES_VERSION,
        ridge_lambda=1.0,
        training_pairs=32,
        training_seconds=0.0,
        weights_sha256=policy_hash(weights, intercept),
    )


def test_ridge_matches_independent_least_squares():
    pairs, features, targets = synthetic_pairs()
    policy = fit_linear_policy(
        pairs,
        ridge_lambda=0.1,
        budget=make_budget(),
    )

    assert isinstance(policy, LinearPolicy)
    design = np.column_stack([features, np.ones(len(pairs))])
    penalty_rows = math.sqrt(0.1) * np.eye(12, 13)
    stacked = np.vstack([design, penalty_rows])
    stacked_targets = np.concatenate([targets, np.zeros(12)])
    expected, *_ = np.linalg.lstsq(stacked, stacked_targets, rcond=None)

    assert np.allclose(np.asarray(policy.parameters), expected, atol=1e-9)

    assert len(policy.weights) == 12
    assert len(policy.parameters) == 13
    assert policy.parameters[-1] == policy.intercept
    assert policy.training_pairs == 40
    assert policy.training_seconds >= 0.0
    assert policy.ridge_lambda == 0.1
    assert policy.features_version == FEATURES_VERSION
    assert policy.weights_sha256 == policy_hash(policy.weights, policy.intercept)
    json.dumps(policy.to_dict())


def test_score_uses_dot_product_and_intercept():
    policy = make_policy((1.0, 2.0) + (0.0,) * 10)
    policy = LinearPolicy(
        weights=policy.weights,
        intercept=0.5,
        features_version=policy.features_version,
        ridge_lambda=policy.ridge_lambda,
        training_pairs=policy.training_pairs,
        training_seconds=policy.training_seconds,
        weights_sha256=policy_hash(policy.weights, 0.5),
    )
    features = (1.0, 3.0) + (0.0,) * 10

    assert policy.score(features) == pytest.approx(0.5 + 1.0 + 6.0)


def test_minimum_32_pairs_is_enforced():
    pairs, _, _ = synthetic_pairs()
    failure = fit_linear_policy(
        pairs[:31],
        ridge_lambda=1.0,
        budget=make_budget(),
    )

    assert isinstance(failure, TrainingFailure)
    assert failure.status == "training_failed"
    assert failure.code == "INSUFFICIENT_PAIRS"
    assert failure.pairs == 31
    assert failure.training_seconds == 0.0
    json.dumps(failure.to_dict())

    policy = fit_linear_policy(
        pairs[:32],
        ridge_lambda=1.0,
        budget=make_budget(),
    )
    assert isinstance(policy, LinearPolicy)
    assert policy.training_pairs == 32


def test_nonfinite_and_wrong_dimension_are_rejected():
    pairs, _, _ = synthetic_pairs()
    bad_x = list(pairs)
    x, y = bad_x[0]
    bad_x[0] = ((float("nan"),) + x[1:], y)
    failure = fit_linear_policy(
        bad_x, ridge_lambda=1.0, budget=make_budget()
    )
    assert failure.code == "NON_FINITE_VALUE"

    bad_y = list(pairs)
    x, y = bad_y[0]
    bad_y[0] = (x, float("inf"))
    failure = fit_linear_policy(
        bad_y, ridge_lambda=1.0, budget=make_budget()
    )
    assert failure.code == "NON_FINITE_VALUE"

    bad_dimension = list(pairs)
    x, y = bad_dimension[0]
    bad_dimension[0] = (x[:11], y)
    failure = fit_linear_policy(
        bad_dimension, ridge_lambda=1.0, budget=make_budget()
    )
    assert failure.code == "INVALID_DIMENSION"


def test_features_version_mismatch_is_training_failed():
    counters = TrainingCounters(
        n=8,
        max_pairs=4096,
        states=0,
        actions_sampled=0,
        pairs=0,
        incomplete_pairs=0,
        invalid_terminals=0,
        rollouts=0,
        evaluations=0,
        legal_mask_queries=0,
        feature_legal_mask_queries=0,
        feature_bfs_queries=0,
        completion_steps=0,
        budget_stop=False,
        stop_reason="pair_cap",
    )
    dataset = TrainingDataset(
        pairs=(),
        counters=counters,
        features_version="other-version",
    )

    failure = fit_linear_policy(
        dataset,
        ridge_lambda=1.0,
        budget=make_budget(),
    )

    assert isinstance(failure, TrainingFailure)
    assert failure.code == "FEATURES_VERSION_MISMATCH"


def test_training_time_cap_is_explicit():
    pairs, _, _ = synthetic_pairs()

    before = fit_linear_policy(
        pairs,
        ridge_lambda=1.0,
        budget=Budget(0.0, 60.0, CountdownClock(0)),
    )
    assert before.code == "TRAINING_TIME_EXCEEDED"
    assert before.training_seconds == 0.0

    during = fit_linear_policy(
        pairs,
        ridge_lambda=1.0,
        budget=Budget(0.0, 60.0, CountdownClock(1)),
    )
    assert during.code == "TRAINING_TIME_EXCEEDED"
    assert during.training_seconds >= 0.0


def test_numerical_failure_is_explicit():
    rows = [(tuple(0.0 for _ in range(12)), 1.0) for _ in range(40)]
    failure = fit_linear_policy(
        rows,
        ridge_lambda=0.0,
        budget=make_budget(),
    )

    assert failure.code == "NUMERICAL_FAILURE"


def test_invalid_arguments_are_rejected():
    pairs, _, _ = synthetic_pairs()

    for lam in (-0.1, float("nan"), float("inf"), True):
        with pytest.raises(LinearPolicyError) as exc:
            fit_linear_policy(pairs, ridge_lambda=lam, budget=make_budget())
        assert exc.value.code == "INVALID_LAMBDA"

    with pytest.raises(LinearPolicyError) as exc:
        fit_linear_policy(pairs, ridge_lambda=1.0, budget=object())
    assert exc.value.code == "INVALID_BUDGET"

    with pytest.raises(LinearPolicyError) as exc:
        fit_linear_policy(object(), ridge_lambda=1.0, budget=make_budget())
    assert exc.value.code == "INVALID_PAIRS"

    with pytest.raises(LinearPolicyError) as exc:
        fit_linear_policy(
            pairs,
            ridge_lambda=1.0,
            budget=make_budget(),
            features_version="other",
        )
    assert exc.value.code == "INVALID_FEATURES_VERSION"


def test_selector_chooses_max_score_with_uniform_tie_break():
    candidate = create_candidate(n=8, edges=[[0, 1], [0, 2], [0, 3]])
    from evobyte.search.actions import legal_additions

    actions = legal_additions(candidate)
    policy = make_policy(feature8_weights())
    rng = SpyRng(0)

    action = policy.select(candidate, actions, rng, make_budget())

    assert action in {(0, 4), (0, 5), (0, 6), (0, 7)}
    assert set(rng.options) == {(0, 4), (0, 5), (0, 6), (0, 7)}

    tied_policy = make_policy(zero_weights())
    tied_rng = SpyRng(3)
    tied_action = tied_policy.select(
        candidate,
        actions,
        tied_rng,
        make_budget(),
    )
    assert tied_action in actions
    assert set(tied_rng.options) == set(actions)


def test_selector_respects_no_actions_and_expired_budget():
    candidate = create_candidate(n=8, edges=[])
    policy = make_policy(zero_weights())

    assert policy.select(candidate, (), SpyRng(), make_budget()) is None
    assert (
        policy.select(
            candidate,
            ((0, 1),),
            SpyRng(),
            Budget(0.0, 60.0, CountdownClock(0)),
        )
        is None
    )


def test_scores_are_invariant_under_permutation():
    pairs, _, _ = synthetic_pairs()
    policy = fit_linear_policy(
        pairs,
        ridge_lambda=0.1,
        budget=make_budget(),
    )
    assert isinstance(policy, LinearPolicy)

    candidate = create_candidate(n=8, edges=[[0, 1], [2, 3]])
    action = (0, 2)
    permutation = [3, 5, 1, 0, 4, 2, 7, 6]
    permuted_edges = [
        tuple(sorted((permutation[u], permutation[v])))
        for u, v in candidate.payload["edges"]
    ]
    permuted = create_candidate(n=8, edges=permuted_edges)
    permuted_action = (permutation[0], permutation[2])

    base_features = compute_features(candidate, action).values
    permuted_features = compute_features(permuted, permuted_action).values

    assert policy.score(base_features) == policy.score(permuted_features)


def test_score_rejects_invalid_vectors():
    policy = make_policy(zero_weights())

    with pytest.raises(LinearPolicyError) as exc:
        policy.score((0.0,) * 11)
    assert exc.value.code == "INVALID_FEATURE_VECTOR"

    with pytest.raises(LinearPolicyError) as exc:
        policy.score((float("nan"),) + (0.0,) * 11)
    assert exc.value.code == "NON_FINITE_FEATURE"


def test_does_not_import_torch():
    assert "torch" not in sys.modules
