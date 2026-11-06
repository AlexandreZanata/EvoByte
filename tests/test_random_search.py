"""Testes da referência aleatória com reinícios (F03-T02)."""

from __future__ import annotations

import json
import random

import pytest

from evobyte.budget import Budget
from evobyte.candidate import create_candidate
from evobyte.certificates import CERTIFIED, certify
from evobyte.search.engine import (
    SearchConfig,
    SearchError,
    run_search,
)
from evobyte.search.selectors import UniformSelector
from evobyte.validation.reference import validate as validate_reference
from evobyte.validation.runtime import validate as validate_runtime

COMMIT = "a" * 40
C5_EDGES = ((0, 1), (1, 2), (2, 3), (3, 4), (0, 4))
STAR_EDGES = ((0, 1), (0, 2), (0, 3), (0, 4))


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


class ScriptedSelector:
    def __init__(self):
        self.construction = -1
        self.step = 0
        self.script = ()

    def select(self, candidate, legal_actions, rng, budget):
        if candidate.m == 0:
            self.construction += 1
            self.step = 0
            self.script = C5_EDGES if self.construction == 0 else STAR_EDGES
        if self.step >= len(self.script):
            return None
        action = self.script[self.step]
        self.step += 1
        return action


class InvalidActionSelector:
    def select(self, candidate, legal_actions, rng, budget):
        return (0, 0)


class StoppingSelector:
    def select(self, candidate, legal_actions, rng, budget):
        return None


def run_random(n=8, seed=42, limit=60.0, step=0.1, emit=None):
    return run_search(
        SearchConfig(n),
        UniformSelector(),
        make_budget(limit, step),
        random.Random(seed),
        emit,
    )


def test_random_search_stops_by_budget_and_retains_valid_best():
    events = []
    outcome = run_random(n=8, seed=7, limit=60.0, step=0.1, emit=events.append)

    assert outcome.stopped_by_budget is True
    assert outcome.elapsed_seconds >= 0.9 * 60.0
    assert outcome.constructions >= 1
    assert outcome.restarts >= 1
    assert outcome.best_m >= 1
    assert outcome.best_m == outcome.best_candidate.m
    assert outcome.best_is_maximal is True

    payload = outcome.best_candidate.payload
    assert validate_reference(payload, 8).valid is True
    assert validate_runtime(payload, 8).valid is True

    event_names = [event["event"] for event in events]
    assert event_names[0] == "start"
    assert event_names[-1] == "stop"
    assert "restart" in event_names
    assert "maximal" in event_names
    json.dumps(events)


def test_seed_repeats_the_same_search():
    first_events = []
    second_events = []
    first = run_random(n=8, seed=42, step=0.5, emit=first_events.append)
    second = run_random(n=8, seed=42, step=0.5, emit=second_events.append)

    assert first.best_candidate.canonical_bytes == second.best_candidate.canonical_bytes
    assert first.to_dict() == second.to_dict()
    assert first_events == second_events
    json.dumps(first.to_dict())


def test_tiny_budget_stops_without_spawning_work():
    outcome = run_random(n=8, seed=1, limit=60.0, step=1000.0)

    assert outcome.stopped_by_budget is True
    assert outcome.constructions == 0
    assert outcome.restarts == 0
    assert outcome.best_m == 0
    assert outcome.elapsed_seconds >= 54.0
    assert outcome.best_is_maximal is False


def test_budget_can_interrupt_a_partial_construction():
    outcome = run_random(n=8, seed=1, limit=60.0, step=10.0)

    assert outcome.stopped_by_budget is True
    assert outcome.best_m >= 1
    assert outcome.best_m == outcome.best_candidate.m
    assert validate_reference(outcome.best_candidate.payload, 8).valid is True


def test_n1_has_no_legal_actions():
    events = []
    outcome = run_random(n=1, seed=0, emit=events.append)

    assert outcome.stopped_reason == "no_legal_actions"
    assert outcome.stopped_by_budget is False
    assert outcome.constructions == 1
    assert outcome.restarts == 0
    assert outcome.best_m == 0
    assert outcome.best_is_maximal is True
    assert [event["event"] for event in events][-1] == "stop"


def test_best_survives_restarts_with_worse_constructions():
    events = []
    outcome = run_search(
        SearchConfig(5),
        ScriptedSelector(),
        make_budget(60.0, 0.1),
        random.Random(0),
        events.append,
    )

    assert outcome.best_m == 5
    assert outcome.best_is_maximal is True
    assert outcome.constructions >= 2
    assert outcome.restarts >= 1
    assert {
        tuple(edge) for edge in outcome.best_candidate.payload["edges"]
    } == set(C5_EDGES)

    maximal_m = [
        event["m"] for event in events if event["event"] == "maximal"
    ]
    assert 5 in maximal_m
    assert 4 in maximal_m

    best_values = [
        event["best_m"] for event in events if event["event"] == "new_best"
    ]
    assert best_values == sorted(best_values)
    assert max(best_values) == 5
    assert all(value <= 5 for value in best_values)


def test_selected_best_can_be_certified(tmp_path):
    outcome = run_random(n=8, seed=3, limit=60.0, step=0.1)

    certificate = certify(
        outcome.best_candidate,
        "random-run",
        8,
        COMMIT,
        tmp_path,
    )
    assert certificate.status == CERTIFIED


def test_selector_chooses_only_from_legal_actions():
    budget = make_budget(60.0, 0.1)
    selector = UniformSelector()
    rng = random.Random(7)
    candidate = create_candidate(n=4, edges=[])
    legal_actions = ((0, 1), (2, 3))

    action = selector.select(candidate, legal_actions, rng, budget)

    assert action in legal_actions
    assert selector.select(candidate, (), rng, budget) is None


def test_selector_respects_exhausted_budget():
    clock = StepClock(0.0, 10.0)
    budget = Budget(0.0, 1.0, clock)
    assert budget.can_search() is True

    assert (
        UniformSelector().select(
            create_candidate(n=4, edges=[]),
            ((0, 1),),
            random.Random(0),
            budget,
        )
        is None
    )


def test_invalid_action_stops_with_error():
    events = []

    with pytest.raises(SearchError) as exc:
        run_search(
            SearchConfig(3),
            InvalidActionSelector(),
            make_budget(60.0, 0.1),
            random.Random(0),
            events.append,
        )

    assert exc.value.code == "SELECTOR_INVALID_ACTION"
    assert any(event["event"] == "invalid_action" for event in events)


def test_selector_stopping_with_budget_is_an_error():
    with pytest.raises(SearchError) as exc:
        run_search(
            SearchConfig(3),
            StoppingSelector(),
            make_budget(60.0, 0.1),
            random.Random(0),
        )

    assert exc.value.code == "SELECTOR_STOPPED_WITH_BUDGET"


def test_invalid_inputs_are_rejected():
    with pytest.raises(SearchError) as exc:
        SearchConfig(0)
    assert exc.value.code == "INVALID_CONFIG"

    with pytest.raises(SearchError) as exc:
        run_search(object(), UniformSelector(), make_budget(), random.Random(0))
    assert exc.value.code == "INVALID_CONFIG"

    with pytest.raises(SearchError) as exc:
        run_search(SearchConfig(2), UniformSelector(), object(), random.Random(0))
    assert exc.value.code == "INVALID_BUDGET"

    with pytest.raises(SearchError) as exc:
        run_search(SearchConfig(2), object(), make_budget(), random.Random(0))
    assert exc.value.code == "INVALID_SELECTOR"
