"""Testes de integração dos braços aprendido e sem treino (F04-T04)."""

from __future__ import annotations

import random
from types import SimpleNamespace

import pytest

from evobyte.budget import Budget
from evobyte.candidate import create_candidate
from evobyte.certificates import CERTIFIED, certify
from evobyte.policy.data import generate_training_data
from evobyte.policy.linear import LinearPolicy, TrainingFailure, fit_linear_policy
from evobyte.search.actions import legal_additions
from evobyte.search.engine import SearchConfig, run_search
from evobyte.search.selectors import (
    GreedySelector,
    LinearWeightsSelector,
    ManualSelector,
    SelectorError,
    UniformSelector,
    make_selector,
)

COMMIT = "a" * 40


class StepClock:
    def __init__(self, start=0.0, step=0.01):
        self.value = start
        self.step = step

    def __call__(self):
        current = self.value
        self.value += self.step
        return current


def make_budget(limit=60.0, step=0.01):
    return Budget(0.0, limit, StepClock(0.0, step))


class SpyRng:
    def __init__(self, index=0):
        self.index = index
        self.options = None

    def choice(self, options):
        self.options = list(options)
        return self.options[self.index % len(self.options)]


def synthetic_pairs(count=40, seed=0):
    rng = random.Random(seed)
    pairs = []
    for _ in range(count):
        x = tuple(rng.uniform(-1.0, 1.0) for _ in range(12))
        pairs.append((x, 2.0 * x[0] - x[1] + 0.5))
    return pairs


def init_weights(seed):
    rng = random.Random(seed)
    return tuple(rng.gauss(0.0, 1.0) for _ in range(12))


def feature8_weights():
    weights = [0.0] * 12
    weights[7] = 1.0
    return tuple(weights)



def test_factory_exposes_six_arms():
    policy = SimpleNamespace(
        weights=tuple(0.0 for _ in range(12)),
        intercept=0.0,
    )

    assert isinstance(make_selector("random"), UniformSelector)
    assert isinstance(make_selector("greedy"), GreedySelector)
    assert isinstance(make_selector("local_uniform"), UniformSelector)
    assert isinstance(
        make_selector("local_manual", p=0.5),
        ManualSelector,
    )
    linear = make_selector("local_linear", policy=policy)
    assert isinstance(linear, LinearWeightsSelector)
    assert linear.intercept == 0.0
    untrained = make_selector(
        "local_untrained",
        weights=tuple(range(12)),
    )
    assert isinstance(untrained, LinearWeightsSelector)

    with pytest.raises(SelectorError) as exc:
        make_selector("local_manual")
    assert exc.value.code == "INVALID_P"

    with pytest.raises(SelectorError) as exc:
        make_selector("local_linear")
    assert exc.value.code == "INVALID_POLICY"

    with pytest.raises(SelectorError) as exc:
        make_selector("local_untrained")
    assert exc.value.code == "INVALID_WEIGHTS"

    with pytest.raises(SelectorError) as exc:
        make_selector("unknown")
    assert exc.value.code == "UNKNOWN_METHOD"


def test_linear_weights_selector_measures_features_and_ties():
    candidate = create_candidate(n=8, edges=[[0, 1], [0, 2], [0, 3]])
    actions = legal_additions(candidate)
    selector = make_selector("local_untrained", weights=feature8_weights())
    rng = SpyRng(0)

    action = selector.select(candidate, actions, rng, make_budget())

    assert action in {(0, 4), (0, 5), (0, 6), (0, 7)}
    assert set(rng.options) == {(0, 4), (0, 5), (0, 6), (0, 7)}
    assert selector.selections == 1
    assert selector.feature_evaluations == len(actions)
    assert selector.feature_legal_mask_queries == 2 * len(actions)
    assert selector.feature_bfs_queries == len(actions)
    assert "feature_evaluations" in selector.to_dict()

    assert selector.select(candidate, (), SpyRng(), make_budget()) is None
    assert (
        selector.select(
            candidate,
            actions,
            SpyRng(),
            Budget(0.0, 60.0, lambda: 1000.0),
        )
        is None
    )

    for bad_weights in ((0.0,) * 11, (float("nan"),) + (0.0,) * 11, "123"):
        with pytest.raises(SelectorError) as exc:
            make_selector("local_untrained", weights=bad_weights)
        assert exc.value.code == "INVALID_WEIGHTS"


def test_untrained_and_trained_share_engine(tmp_path):
    policy = fit_linear_policy(
        synthetic_pairs(40, 0),
        ridge_lambda=1.0,
        budget=make_budget(),
    )
    assert isinstance(policy, LinearPolicy)

    trained = make_selector("local_linear", policy=policy)
    untrained = make_selector(
        "local_untrained",
        weights=init_weights(1),
    )

    for selector in (trained, untrained):
        outcome = run_search(
            SearchConfig(8, k_max=1, stagnation_limit=2),
            selector,
            make_budget(),
            random.Random(3),
            perturbation_rng=random.Random(4),
        )
        assert outcome.best_m == outcome.best_candidate.m
        assert outcome.perturbations > 0
        assert outcome.stopped_by_budget is True
        assert selector.feature_evaluations > 0

        certificate = certify(
            outcome.best_candidate,
            "learned-integration",
            8,
            COMMIT,
            tmp_path,
        )
        assert certificate.status == CERTIFIED


def test_training_precedes_search_within_same_budget():
    budget = make_budget()
    dataset = generate_training_data(
        8,
        random.Random(10),
        random.Random(11),
        budget,
        max_pairs=40,
    )
    policy = fit_linear_policy(
        dataset,
        ridge_lambda=1.0,
        budget=budget,
    )
    assert isinstance(policy, LinearPolicy)
    selector = make_selector("local_linear", policy=policy)
    outcome = run_search(
        SearchConfig(8, k_max=1, stagnation_limit=2),
        selector,
        budget,
        random.Random(12),
        perturbation_rng=random.Random(13),
    )

    assert policy.training_seconds >= 0.0
    assert outcome.best_m == outcome.best_candidate.m
    assert outcome.stopped_by_budget is True


def test_training_failure_uses_empty_candidate(tmp_path):
    budget = make_budget()
    dataset = generate_training_data(
        8,
        random.Random(20),
        random.Random(21),
        budget,
        max_pairs=2,
    )
    failure = fit_linear_policy(
        dataset,
        ridge_lambda=1.0,
        budget=budget,
    )

    assert isinstance(failure, TrainingFailure)
    assert failure.code == "INSUFFICIENT_PAIRS"
    empty = create_candidate(n=8, edges=[])
    certificate = certify(empty, "training-failed", 8, COMMIT, tmp_path)
    assert certificate.status == CERTIFIED


def test_streams_are_separate_and_reproducible():
    first = init_weights(1)
    second = init_weights(2)
    assert first != second

    pairs_a = synthetic_pairs(40, 1)
    pairs_b = synthetic_pairs(40, 1)
    pairs_c = synthetic_pairs(40, 2)
    policy_a = fit_linear_policy(
        pairs_a, ridge_lambda=1.0, budget=make_budget()
    )
    policy_b = fit_linear_policy(
        pairs_b, ridge_lambda=1.0, budget=make_budget()
    )
    policy_c = fit_linear_policy(
        pairs_c, ridge_lambda=1.0, budget=make_budget()
    )

    assert policy_a.weights == policy_b.weights
    assert policy_a.weights != policy_c.weights


def test_no_weight_reuse_between_fits():
    first = fit_linear_policy(
        synthetic_pairs(40, 3), ridge_lambda=1.0, budget=make_budget()
    )
    second = fit_linear_policy(
        synthetic_pairs(40, 4), ridge_lambda=1.0, budget=make_budget()
    )

    assert first.weights != second.weights
    assert first.weights_sha256 != second.weights_sha256
