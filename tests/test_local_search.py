"""Testes das perturbações e referências locais (F03-T04)."""

from __future__ import annotations

import math
import random

import pytest

from evobyte.budget import Budget
from evobyte.candidate import create_candidate
from evobyte.certificates import CERTIFIED, certify
from evobyte.search.actions import legal_additions
from evobyte.search.engine import SearchConfig, SearchError, run_search
from evobyte.search.selectors import (
    GreedySelector,
    ManualSelector,
    SelectorError,
    UniformSelector,
)
from evobyte.validation.reference import validate as validate_reference
from evobyte.validation.runtime import validate as validate_runtime

COMMIT = "a" * 40


class StepClock:
    def __init__(self, start=0.0, step=0.1):
        self.value = start
        self.step = step

    def __call__(self):
        current = self.value
        self.value += self.step
        return current


def make_budget(limit=60.0, step=0.1):
    return Budget(0.0, limit, StepClock(0.0, step))


class ManualSpy:
    def __init__(self, random_value, choice_index=0):
        self.random_value = random_value
        self.choice_index = choice_index
        self.options = None
        self.random_calls = 0

    def random(self):
        self.random_calls += 1
        return self.random_value

    def choice(self, options):
        self.options = list(options)
        return self.options[self.choice_index % len(self.options)]


class FirstLegalSelector:
    def select(self, candidate, legal_actions, rng, budget):
        if not legal_actions or not budget.can_search():
            return None
        return legal_actions[0]


class ValidatingUniformSelector:
    def __init__(self, n):
        self.n = n
        self.checked = 0
        self._uniform = UniformSelector()

    def select(self, candidate, legal_actions, rng, budget):
        assert validate_reference(candidate.payload, self.n).valid
        self.checked += 1
        return self._uniform.select(candidate, legal_actions, rng, budget)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"k_max": -1, "stagnation_limit": 1},
        {"k_max": 1, "stagnation_limit": 0},
        {"k_max": 1, "stagnation_limit": None},
        {"k_max": 0, "stagnation_limit": 3},
        {"k_max": True, "stagnation_limit": 1},
        {"k_max": 1, "stagnation_limit": True},
    ],
)
def test_invalid_local_config_is_rejected(kwargs):
    with pytest.raises(SearchError) as exc:
        SearchConfig(8, **kwargs)

    assert exc.value.code == "INVALID_CONFIG"


@pytest.mark.parametrize("p", [-0.1, 1.1, math.nan, math.inf, True])
def test_invalid_manual_probability_is_rejected(p):
    with pytest.raises(SelectorError) as exc:
        ManualSelector(p)

    assert exc.value.code == "INVALID_P"


def test_manual_p1_always_uses_degree_priority():
    candidate = create_candidate(
        n=6,
        edges=[[0, 1], [0, 2], [3, 4], [3, 5]],
    )
    legal = legal_additions(candidate)
    rng = ManualSpy(0.99, 0)

    action = ManualSelector(1.0).select(candidate, legal, rng, make_budget())

    assert action == (0, 3)
    assert rng.options == [(0, 3)]
    assert rng.random_calls == 1


def test_manual_p0_is_uniform():
    candidate = create_candidate(n=4, edges=[[0, 1], [2, 3]])
    legal = legal_additions(candidate)
    rng = ManualSpy(0.0, 3)

    action = ManualSelector(0.0).select(candidate, legal, rng, make_budget())

    assert action == legal[3]
    assert rng.options == list(legal)


def test_manual_probability_selects_branch():
    candidate = create_candidate(
        n=6,
        edges=[[0, 1], [0, 2], [3, 4], [3, 5]],
    )
    legal = legal_additions(candidate)

    greedy_rng = ManualSpy(0.2, 0)
    greedy_action = ManualSelector(0.5).select(
        candidate,
        legal,
        greedy_rng,
        make_budget(),
    )
    assert greedy_action == (0, 3)
    assert greedy_rng.options == [(0, 3)]

    uniform_rng = ManualSpy(0.8, 0)
    uniform_action = ManualSelector(0.5).select(
        candidate,
        legal,
        uniform_rng,
        make_budget(),
    )
    assert uniform_action == legal[0]
    assert uniform_rng.options == list(legal)


def test_local_first_legal_perturbs_restarts_and_keeps_best():
    events = []
    outcome = run_search(
        SearchConfig(5, k_max=1, stagnation_limit=1),
        FirstLegalSelector(),
        make_budget(60.0, 0.01),
        random.Random(0),
        events.append,
        perturbation_rng=random.Random(1),
    )

    assert outcome.best_m == 4
    assert outcome.best_is_maximal is True
    assert {
        tuple(edge) for edge in outcome.best_candidate.payload["edges"]
    } == {(0, 1), (0, 2), (0, 3), (0, 4)}
    assert outcome.perturbations >= 1
    assert outcome.restarts >= 1
    assert outcome.stopped_by_budget is True

    assert any(
        event["event"] == "perturbation"
        and 1 <= event["removed_count"] <= 1
        for event in events
    )
    assert any(
        event["event"] == "restart" and event["reason"] == "stagnation"
        for event in events
    )

    best_values = [
        event["best_m"] for event in events if event["event"] == "new_best"
    ]
    assert best_values == sorted(best_values)
    maximal_values = [
        event["m"] for event in events if event["event"] == "maximal"
    ]
    assert outcome.best_m >= max(maximal_values)


def test_local_uniform_perturbs_and_preserves_validity():
    outcome = run_search(
        SearchConfig(8, k_max=3, stagnation_limit=2),
        UniformSelector(),
        make_budget(60.0, 0.02),
        random.Random(4),
        perturbation_rng=random.Random(5),
    )

    assert outcome.perturbations >= 1
    assert outcome.constructions >= 1
    assert outcome.stopped_by_budget is True
    assert outcome.best_is_maximal is True
    assert outcome.best_m >= 1
    assert validate_reference(outcome.best_candidate.payload, 8).valid is True
    assert validate_runtime(outcome.best_candidate.payload, 8).valid is True


def test_local_moves_preserve_validity_on_every_selection():
    selector = ValidatingUniformSelector(5)
    outcome = run_search(
        SearchConfig(5, k_max=1, stagnation_limit=2),
        selector,
        make_budget(60.0, 0.01),
        random.Random(2),
        perturbation_rng=random.Random(3),
    )

    assert selector.checked > 0
    assert outcome.perturbations >= 1
    assert validate_reference(outcome.best_candidate.payload, 5).valid is True
    assert validate_runtime(outcome.best_candidate.payload, 5).valid is True


def test_local_best_can_be_certified(tmp_path):
    outcome = run_search(
        SearchConfig(5, k_max=1, stagnation_limit=1),
        FirstLegalSelector(),
        make_budget(60.0, 0.01),
        random.Random(0),
        perturbation_rng=random.Random(1),
    )

    certificate = certify(
        outcome.best_candidate,
        "local-run",
        5,
        COMMIT,
        tmp_path,
    )

    assert certificate.status == CERTIFIED


@pytest.mark.parametrize(
    "selector, config",
    [
        (UniformSelector(), SearchConfig(6)),
        (GreedySelector(), SearchConfig(6)),
        (UniformSelector(), SearchConfig(6, k_max=1, stagnation_limit=2)),
        (ManualSelector(0.5), SearchConfig(6, k_max=1, stagnation_limit=2)),
    ],
    ids=["random", "greedy", "local_uniform", "local_manual"],
)
def test_four_references_share_engine(selector, config):
    outcome = run_search(
        config,
        selector,
        make_budget(60.0, 0.05),
        random.Random(9),
        perturbation_rng=random.Random(10),
    )

    assert outcome.stopped_by_budget is True
    assert outcome.constructions >= 1
    assert outcome.best_m == outcome.best_candidate.m
    assert validate_reference(outcome.best_candidate.payload, 6).valid is True
    assert validate_runtime(outcome.best_candidate.payload, 6).valid is True
    if config.local:
        assert outcome.perturbations >= 1
    else:
        assert outcome.perturbations == 0


def test_invalid_perturbation_rng_is_rejected():
    with pytest.raises(SearchError) as exc:
        run_search(
            SearchConfig(5, k_max=1, stagnation_limit=1),
            FirstLegalSelector(),
            make_budget(),
            random.Random(0),
            perturbation_rng=object(),
        )

    assert exc.value.code == "INVALID_PERTURBATION_RNG"
