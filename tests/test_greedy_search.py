"""Testes do seletor guloso por graus (F03-T03)."""

from __future__ import annotations

import random

import pytest

from evobyte.budget import Budget
from evobyte.candidate import create_candidate
from evobyte.certificates import CERTIFIED, certify
from evobyte.search.actions import legal_additions
from evobyte.search.engine import SearchConfig, run_search
from evobyte.search.selectors import GreedySelector
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


class SpyRng:
    def __init__(self, result_index=0):
        self.result_index = result_index
        self.options = None

    def choice(self, options):
        self.options = list(options)
        return self.options[self.result_index % len(self.options)]


def test_unique_maximum_sum_of_degrees_is_selected():
    candidate = create_candidate(
        n=6,
        edges=[[0, 1], [0, 2], [3, 4], [3, 5]],
    )
    legal = legal_additions(candidate)
    rng = SpyRng(0)

    action = GreedySelector().select(candidate, legal, rng, make_budget())

    assert action == (0, 3)
    assert rng.options == [(0, 3)]


@pytest.mark.parametrize("result_index", [0, 1])
def test_unique_maximum_does_not_depend_on_tie_choice(result_index):
    candidate = create_candidate(
        n=6,
        edges=[[0, 1], [0, 2], [3, 4], [3, 5]],
    )
    legal = legal_additions(candidate)
    rng = SpyRng(result_index)

    action = GreedySelector().select(candidate, legal, rng, make_budget())

    assert action == (0, 3)
    assert rng.options == [(0, 3)]


def test_ties_offer_all_maximum_actions_to_rng():
    candidate = create_candidate(n=4, edges=[[0, 1], [2, 3]])
    legal = legal_additions(candidate)
    assert set(legal) == {(0, 2), (0, 3), (1, 2), (1, 3)}

    rng = SpyRng(2)
    action = GreedySelector().select(candidate, legal, rng, make_budget())

    assert rng.options == list(legal)
    assert action == legal[2]

    last_rng = SpyRng(3)
    last_action = GreedySelector().select(
        candidate,
        legal,
        last_rng,
        make_budget(),
    )
    assert last_action == legal[3]
    assert last_action != legal[0]


def test_selector_does_not_modify_candidate():
    candidate = create_candidate(
        n=6,
        edges=[[0, 1], [0, 2], [3, 4], [3, 5]],
    )
    legal = legal_additions(candidate)
    before_payload = dict(candidate.payload)
    before_bytes = candidate.canonical_bytes

    GreedySelector().select(candidate, legal, SpyRng(0), make_budget())

    assert candidate.payload == before_payload
    assert candidate.canonical_bytes == before_bytes


def test_selector_returns_none_without_actions_or_budget():
    candidate = create_candidate(n=4, edges=[[0, 1]])
    rng = SpyRng(0)

    assert (
        GreedySelector().select(candidate, (), rng, make_budget())
        is None
    )
    assert rng.options is None

    clock = StepClock(0.0, 10.0)
    budget = Budget(0.0, 1.0, clock)
    assert budget.can_search() is True
    assert (
        GreedySelector().select(
            candidate,
            ((0, 2),),
            SpyRng(0),
            budget,
        )
        is None
    )


def test_selector_returns_only_given_action():
    candidate = create_candidate(n=4, edges=[[0, 1], [2, 3]])
    legal = legal_additions(candidate)

    action = GreedySelector().select(
        candidate,
        legal,
        random.Random(0),
        make_budget(),
    )

    assert action in legal


def test_unique_maximum_is_equivariant_under_permutation():
    candidate = create_candidate(
        n=6,
        edges=[[0, 1], [0, 2], [3, 4], [3, 5]],
    )
    legal = legal_additions(candidate)
    permutation = [3, 5, 1, 0, 4, 2]
    permuted_edges = [
        tuple(sorted((permutation[u], permutation[v])))
        for u, v in candidate.payload["edges"]
    ]
    permuted = create_candidate(n=6, edges=permuted_edges)
    permuted_legal = legal_additions(permuted)

    rng = SpyRng(0)
    action = GreedySelector().select(
        permuted,
        permuted_legal,
        rng,
        make_budget(),
    )
    expected = tuple(sorted((permutation[0], permutation[3])))

    assert action == expected
    assert rng.options == [expected]


def test_tied_maximum_set_is_equivariant_under_permutation():
    candidate = create_candidate(n=4, edges=[[0, 1], [2, 3]])
    legal = set(legal_additions(candidate))
    permutation = [2, 0, 3, 1]
    permuted_edges = [
        tuple(sorted((permutation[u], permutation[v])))
        for u, v in candidate.payload["edges"]
    ]
    permuted = create_candidate(n=4, edges=permuted_edges)
    permuted_legal = set(legal_additions(permuted))

    rng = SpyRng(0)
    GreedySelector().select(
        permuted,
        tuple(sorted(permuted_legal)),
        rng,
        make_budget(),
    )
    expected = {
        tuple(sorted((permutation[u], permutation[v])))
        for u, v in legal
    }

    assert set(rng.options) == expected


@pytest.mark.parametrize("n", [5, 6, 8])
def test_greedy_through_engine_produces_valid_maximal_candidate(n):
    outcome = run_search(
        SearchConfig(n),
        GreedySelector(),
        make_budget(60.0, 0.05),
        random.Random(11),
    )

    assert outcome.best_m == outcome.best_candidate.m
    assert outcome.best_is_maximal is True
    assert outcome.constructions >= 1
    assert outcome.restarts >= 1
    assert outcome.stopped_by_budget is True
    assert validate_reference(outcome.best_candidate.payload, n).valid is True
    assert validate_runtime(outcome.best_candidate.payload, n).valid is True


def test_greedy_is_reproducible_with_same_seed():
    first = run_search(
        SearchConfig(6),
        GreedySelector(),
        make_budget(60.0, 0.2),
        random.Random(5),
    )
    second = run_search(
        SearchConfig(6),
        GreedySelector(),
        make_budget(60.0, 0.2),
        random.Random(5),
    )

    assert first.best_candidate.canonical_bytes == second.best_candidate.canonical_bytes
    assert first.to_dict() == second.to_dict()


def test_greedy_best_can_be_certified(tmp_path):
    outcome = run_search(
        SearchConfig(5),
        GreedySelector(),
        make_budget(60.0, 0.05),
        random.Random(3),
    )

    certificate = certify(
        outcome.best_candidate,
        "greedy-run",
        5,
        COMMIT,
        tmp_path,
    )

    assert certificate.status == CERTIFIED
