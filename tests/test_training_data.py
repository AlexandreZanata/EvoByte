"""Testes do gerador de pares por completações (F04-T02)."""

from __future__ import annotations

import json
import math
import random
from types import SimpleNamespace

import pytest

from evobyte.budget import Budget
from evobyte.policy import data as data_module
from evobyte.policy.data import TrainingDataError, generate_training_data
from evobyte.validation.reference import validate as validate_reference


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


def make_budget(limit=60.0, step=0.01):
    return Budget(0.0, limit, StepClock(0.0, step))


def test_generator_produces_pairs_with_formula_and_provenance(monkeypatch):
    seen_terminals = []
    real_runtime = data_module.validate_runtime

    def checking_runtime(payload, n):
        result = real_runtime(payload, n)
        assert validate_reference(payload, n).valid == result.valid
        seen_terminals.append(result.valid)
        return result

    monkeypatch.setattr(data_module, "validate_runtime", checking_runtime)

    dataset = generate_training_data(
        8,
        random.Random(1),
        random.Random(2),
        make_budget(),
        max_pairs=4,
    )

    assert len(dataset.pairs) == 4
    assert dataset.counters.stop_reason == "pair_cap"
    assert dataset.counters.budget_stop is False
    assert dataset.counters.invalid_terminals == 0
    assert dataset.counters.evaluations >= 2 * len(dataset.pairs)
    assert len(seen_terminals) == dataset.counters.evaluations
    assert all(seen_terminals)

    for pair in dataset.pairs:
        assert pair.n == 8
        assert pair.features_version == "symmetric-12-v1"
        assert len(pair.features) == 12
        assert all(math.isfinite(value) for value in pair.features)
        assert math.isfinite(pair.target)
        assert len(pair.terminal_ms) == 2
        assert len(pair.terminal_sha256) == 2
        assert pair.target == pytest.approx(
            (pair.terminal_ms[0] + pair.terminal_ms[1]) / 2.0 - pair.state_m
        )

    assert dataset.counters.actions_sampled == 4
    assert dataset.counters.feature_legal_mask_queries == 8
    assert dataset.counters.feature_bfs_queries == 4
    assert dataset.counters.legal_mask_queries > 0
    assert dataset.counters.completion_steps > 0
    assert len(dataset.xy()) == 4
    json.dumps(dataset.to_dict())


def test_generator_is_reproducible_with_same_seeds():
    first = generate_training_data(
        8,
        random.Random(10),
        random.Random(11),
        make_budget(),
        max_pairs=3,
    )
    second = generate_training_data(
        8,
        random.Random(10),
        random.Random(11),
        make_budget(),
        max_pairs=3,
    )

    assert first.pairs == second.pairs
    assert first.counters == second.counters
    assert first.to_dict() == second.to_dict()


def test_budget_stop_marks_incomplete_pair_and_excludes_it():
    budget = Budget(0.0, 60.0, CountdownClock(2))
    dataset = generate_training_data(
        8,
        random.Random(3),
        random.Random(4),
        budget,
        max_pairs=4,
    )

    assert dataset.pairs == ()
    assert dataset.counters.budget_stop is True
    assert dataset.counters.stop_reason == "budget"
    assert dataset.counters.incomplete_pairs == 1
    assert dataset.counters.actions_sampled == 1
    assert dataset.counters.rollouts == 0
    assert dataset.counters.evaluations == 0


def test_invalid_terminal_is_excluded_without_appending_pair(monkeypatch):
    real_runtime = data_module.validate_runtime
    calls = {"count": 0}

    def first_invalid(payload, n):
        calls["count"] += 1
        if calls["count"] == 1:
            return SimpleNamespace(valid=False)
        return real_runtime(payload, n)

    monkeypatch.setattr(data_module, "validate_runtime", first_invalid)

    dataset = generate_training_data(
        8,
        random.Random(5),
        random.Random(6),
        make_budget(),
        max_pairs=2,
    )

    assert len(dataset.pairs) == 2
    assert dataset.counters.invalid_terminals == 1
    assert dataset.counters.evaluations > 2 * len(dataset.pairs)


def test_max_actions_per_state_is_respected():
    dataset = generate_training_data(
        8,
        random.Random(7),
        random.Random(8),
        make_budget(),
        max_pairs=6,
        max_actions_per_state=2,
    )

    assert len(dataset.pairs) == 6
    assert dataset.counters.actions_sampled <= 2 * dataset.counters.states


def test_allowed_orders_and_xy_shape():
    dataset = generate_training_data(
        16,
        random.Random(9),
        random.Random(10),
        make_budget(),
        max_pairs=1,
    )

    pair = dataset.pairs[0]
    assert pair.n == 16
    x, y = dataset.xy()[0]
    assert x == pair.features
    assert y == pair.target


def test_invalid_arguments_are_rejected():
    with pytest.raises(TrainingDataError) as exc:
        generate_training_data(
            24, random.Random(0), random.Random(1), make_budget(), max_pairs=1
        )
    assert exc.value.code == "INVALID_N"

    with pytest.raises(TrainingDataError) as exc:
        generate_training_data(
            7, random.Random(0), random.Random(1), make_budget(), max_pairs=1
        )
    assert exc.value.code == "INVALID_N"

    with pytest.raises(TrainingDataError) as exc:
        generate_training_data(
            8, random.Random(0), random.Random(1), make_budget(), max_pairs=0
        )
    assert exc.value.code == "INVALID_MAX_PAIRS"

    with pytest.raises(TrainingDataError) as exc:
        generate_training_data(
            8, random.Random(0), random.Random(1), make_budget(), max_pairs=4097
        )
    assert exc.value.code == "INVALID_MAX_PAIRS"

    with pytest.raises(TrainingDataError) as exc:
        generate_training_data(
            8,
            random.Random(0),
            random.Random(1),
            make_budget(),
            max_actions_per_state=0,
        )
    assert exc.value.code == "INVALID_MAX_ACTIONS"

    with pytest.raises(TrainingDataError) as exc:
        generate_training_data(
            8,
            random.Random(0),
            random.Random(1),
            make_budget(),
            max_actions_per_state=9,
        )
    assert exc.value.code == "INVALID_MAX_ACTIONS"

    with pytest.raises(TrainingDataError) as exc:
        generate_training_data(
            8, object(), random.Random(1), make_budget(), max_pairs=1
        )
    assert exc.value.code == "INVALID_RNG"

    with pytest.raises(TrainingDataError) as exc:
        generate_training_data(
            8, random.Random(0), object(), make_budget(), max_pairs=1
        )
    assert exc.value.code == "INVALID_RNG"

    with pytest.raises(TrainingDataError) as exc:
        generate_training_data(
            8, random.Random(0), random.Random(1), object(), max_pairs=1
        )
    assert exc.value.code == "INVALID_BUDGET"
