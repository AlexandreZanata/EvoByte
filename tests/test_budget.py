"""Testes do relógio e orçamento temporal (F02-T02)."""

from __future__ import annotations

import math
import time

import pytest

from evobyte.budget import Budget, BudgetError


class FakeClock:
    def __init__(self, value=0.0):
        self.value = value
        self.calls = 0

    def __call__(self):
        self.calls += 1
        return self.value

    def advance(self, seconds):
        self.value += seconds

    def set(self, value):
        self.value = value


class CountingClock:
    def __init__(self, start=0.0):
        self.value = start
        self.calls = 0

    def __call__(self):
        self.calls += 1
        self.value += 1.0
        return self.value


def decision_flags(budget):
    return {
        "can_search": budget.can_search(),
        "should_finalize": budget.should_finalize(),
        "past_finalize_deadline": budget.past_finalize_deadline(),
        "should_terminate": budget.should_terminate(),
        "should_kill": budget.should_kill(),
        "timed_out": budget.timed_out(),
        "is_overrun": budget.is_overrun(),
    }


def test_default_clock_is_monotonic():
    budget = Budget(0.0, 60.0)

    assert budget.clock is time.monotonic


def test_short_scale_milestones():
    budget = Budget(1000.0, 60.0, FakeClock(1000.0))

    assert budget.search_stop_seconds == 54.0
    assert budget.finalize_by_seconds == 57.0
    assert budget.terminate_at_seconds == 58.0
    assert budget.kill_at_seconds == 59.0
    assert budget.training_limit_seconds == 12.0
    assert budget.generation_limit_seconds == 11.5
    assert budget.tuning_limit_seconds == 0.5
    assert budget.generation_limit_seconds + budget.tuning_limit_seconds == 12.0


def test_full_scale_milestones():
    budget = Budget(1000.0, 600.0, FakeClock(1000.0))

    assert budget.search_stop_seconds == 540.0
    assert budget.finalize_by_seconds == 570.0
    assert budget.terminate_at_seconds == 580.0
    assert budget.kill_at_seconds == 590.0
    assert budget.training_limit_seconds == 120.0
    assert budget.generation_limit_seconds == 115.0
    assert budget.tuning_limit_seconds == 5.0


def test_fractional_scale_milestones():
    budget = Budget(0.0, 6.0, FakeClock(0.0))

    assert budget.search_stop_seconds == pytest.approx(5.4)
    assert budget.finalize_by_seconds == pytest.approx(5.7)
    assert budget.terminate_at_seconds == pytest.approx(5.8)
    assert budget.kill_at_seconds == pytest.approx(5.9)
    assert budget.training_limit_seconds == pytest.approx(1.2)
    assert budget.generation_limit_seconds == pytest.approx(1.15)
    assert budget.tuning_limit_seconds == pytest.approx(0.05)


@pytest.mark.parametrize(
    "elapsed, expected, balance, overrun",
    [
        (
            0.0,
            {
                "can_search": True,
                "should_finalize": False,
                "past_finalize_deadline": False,
                "should_terminate": False,
                "should_kill": False,
                "timed_out": False,
                "is_overrun": False,
            },
            600.0,
            0.0,
        ),
        (
            539.999,
            {
                "can_search": True,
                "should_finalize": False,
                "past_finalize_deadline": False,
                "should_terminate": False,
                "should_kill": False,
                "timed_out": False,
                "is_overrun": False,
            },
            pytest.approx(60.001),
            0.0,
        ),
        (
            540.0,
            {
                "can_search": False,
                "should_finalize": True,
                "past_finalize_deadline": False,
                "should_terminate": False,
                "should_kill": False,
                "timed_out": False,
                "is_overrun": False,
            },
            60.0,
            0.0,
        ),
        (
            569.999,
            {
                "can_search": False,
                "should_finalize": True,
                "past_finalize_deadline": False,
                "should_terminate": False,
                "should_kill": False,
                "timed_out": False,
                "is_overrun": False,
            },
            pytest.approx(30.001),
            0.0,
        ),
        (
            570.0,
            {
                "can_search": False,
                "should_finalize": True,
                "past_finalize_deadline": True,
                "should_terminate": False,
                "should_kill": False,
                "timed_out": False,
                "is_overrun": False,
            },
            30.0,
            0.0,
        ),
        (
            580.0,
            {
                "can_search": False,
                "should_finalize": True,
                "past_finalize_deadline": True,
                "should_terminate": True,
                "should_kill": False,
                "timed_out": False,
                "is_overrun": False,
            },
            20.0,
            0.0,
        ),
        (
            589.999,
            {
                "can_search": False,
                "should_finalize": True,
                "past_finalize_deadline": True,
                "should_terminate": True,
                "should_kill": False,
                "timed_out": False,
                "is_overrun": False,
            },
            pytest.approx(10.001),
            0.0,
        ),
        (
            590.0,
            {
                "can_search": False,
                "should_finalize": True,
                "past_finalize_deadline": True,
                "should_terminate": True,
                "should_kill": True,
                "timed_out": False,
                "is_overrun": False,
            },
            10.0,
            0.0,
        ),
        (
            599.999,
            {
                "can_search": False,
                "should_finalize": True,
                "past_finalize_deadline": True,
                "should_terminate": True,
                "should_kill": True,
                "timed_out": False,
                "is_overrun": False,
            },
            pytest.approx(0.001),
            0.0,
        ),
        (
            600.0,
            {
                "can_search": False,
                "should_finalize": True,
                "past_finalize_deadline": True,
                "should_terminate": True,
                "should_kill": True,
                "timed_out": True,
                "is_overrun": False,
            },
            0.0,
            0.0,
        ),
        (
            600.5,
            {
                "can_search": False,
                "should_finalize": True,
                "past_finalize_deadline": True,
                "should_terminate": True,
                "should_kill": True,
                "timed_out": True,
                "is_overrun": True,
            },
            pytest.approx(-0.5),
            pytest.approx(0.5),
        ),
    ],
)
def test_full_scale_boundaries(elapsed, expected, balance, overrun):
    clock = FakeClock(1000.0)
    budget = Budget(1000.0, 600.0, clock)
    clock.advance(elapsed)

    assert decision_flags(budget) == expected
    assert budget.balance_seconds() == balance
    assert budget.overrun_seconds() == overrun


@pytest.mark.parametrize(
    "elapsed, can_search, should_finalize, should_terminate, should_kill, timed_out",
    [
        (53.999, True, False, False, False, False),
        (54.0, False, True, False, False, False),
        (57.0, False, True, False, False, False),
        (58.0, False, True, True, False, False),
        (59.0, False, True, True, True, False),
        (60.0, False, True, True, True, True),
    ],
)
def test_short_scale_boundaries(
    elapsed,
    can_search,
    should_finalize,
    should_terminate,
    should_kill,
    timed_out,
):
    clock = FakeClock(1000.0)
    budget = Budget(1000.0, 60.0, clock)
    clock.advance(elapsed)

    assert budget.can_search() is can_search
    assert budget.should_finalize() is should_finalize
    assert budget.should_terminate() is should_terminate
    assert budget.should_kill() is should_kill
    assert budget.timed_out() is timed_out


def test_negative_balance_is_not_ignored():
    clock = FakeClock(0.0)
    budget = Budget(0.0, 10.0, clock)
    clock.advance(12.0)

    assert budget.elapsed_seconds() == 12.0
    assert budget.balance_seconds() == -2.0
    assert budget.overrun_seconds() == 2.0
    assert budget.is_overrun() is True
    assert budget.timed_out() is True
    assert budget.can_search() is False


def test_training_is_counted_in_wall_time():
    clock = FakeClock(0.0)
    budget = Budget(0.0, 60.0, clock)
    clock.advance(10.0)

    assert budget.training_limit_seconds == 12.0
    assert budget.training_remaining_seconds() == 2.0
    assert budget.can_train() is True
    assert budget.balance_seconds() == 50.0

    clock.advance(3.0)

    assert budget.training_remaining_seconds() == -1.0
    assert budget.can_train() is False
    assert budget.balance_seconds() == 47.0


def test_clock_went_backwards_is_rejected():
    clock = FakeClock(100.0)
    budget = Budget(100.0, 60.0, clock)
    clock.set(99.0)

    with pytest.raises(BudgetError) as exc:
        budget.elapsed_seconds()

    assert exc.value.code == "CLOCK_WENT_BACKWARDS"


def test_clock_cannot_decrease_after_reading():
    clock = FakeClock(100.0)
    budget = Budget(100.0, 60.0, clock)
    clock.advance(5.0)
    assert budget.elapsed_seconds() == 5.0

    clock.set(103.0)

    with pytest.raises(BudgetError) as exc:
        budget.elapsed_seconds()

    assert exc.value.code == "CLOCK_WENT_BACKWARDS"


@pytest.mark.parametrize("bad_value", [math.nan, math.inf, -math.inf, "agora"])
def test_invalid_clock_value_is_rejected(bad_value):
    budget = Budget(0.0, 60.0, lambda: bad_value)

    with pytest.raises(BudgetError) as exc:
        budget.elapsed_seconds()

    assert exc.value.code == "INVALID_CLOCK"


def test_invalid_t0_and_limit_are_rejected():
    with pytest.raises(BudgetError) as exc:
        Budget(math.nan, 60.0)
    assert exc.value.code == "INVALID_T0"

    with pytest.raises(BudgetError) as exc:
        Budget(True, 60.0)
    assert exc.value.code == "INVALID_T0"

    for limit in (0, -1, math.nan, True):
        with pytest.raises(BudgetError) as exc:
            Budget(0.0, limit)
        assert exc.value.code == "INVALID_LIMIT"


def test_clock_must_be_callable():
    with pytest.raises(BudgetError) as exc:
        Budget(0.0, 60.0, clock=123)

    assert exc.value.code == "INVALID_CLOCK"


def test_stage_times_and_cpu_total():
    clock = FakeClock(0.0)
    budget = Budget(0.0, 60.0, clock)

    generation = budget.record_stage(
        "generation",
        wall_seconds=10.0,
        cpu_seconds=9.5,
    )
    search = budget.record_stage("search", wall_seconds=20.0)
    save = budget.record_stage("save", wall_seconds=1.0, cpu_seconds=0.5)

    assert generation.wall_seconds == 10.0
    assert generation.cpu_seconds == 9.5
    assert search.cpu_seconds is None
    assert save.cpu_seconds == 0.5
    assert [stage.stage for stage in budget.stage_times()] == [
        "generation",
        "search",
        "save",
    ]
    assert budget.cpu_seconds_total() is None


def test_cpu_seconds_total_requires_complete_measurements():
    budget = Budget(0.0, 60.0, FakeClock(0.0))

    assert budget.cpu_seconds_total() is None

    budget.record_stage("generation", wall_seconds=10.0, cpu_seconds=9.5)
    budget.record_stage("save", wall_seconds=1.0, cpu_seconds=0.5)

    assert budget.cpu_seconds_total() == 10.0


def test_stage_wall_times_do_not_double_count_wall():
    clock = FakeClock(0.0)
    budget = Budget(0.0, 60.0, clock)
    clock.advance(5.0)

    budget.record_stage("search", wall_seconds=100.0)

    assert budget.elapsed_seconds() == 5.0
    assert budget.balance_seconds() == 55.0
    snapshot = budget.snapshot()
    assert snapshot["elapsed_seconds"] == 5.0
    assert snapshot["stages"][0]["wall_seconds"] == 100.0


def test_stage_validation():
    budget = Budget(0.0, 60.0, FakeClock(0.0))
    budget.record_stage("search", wall_seconds=1.0)

    with pytest.raises(BudgetError) as exc:
        budget.record_stage("search", wall_seconds=2.0)
    assert exc.value.code == "DUPLICATE_STAGE"

    with pytest.raises(BudgetError) as exc:
        budget.record_stage("", wall_seconds=1.0)
    assert exc.value.code == "INVALID_STAGE_NAME"

    for wall in (-1, math.nan, True):
        with pytest.raises(BudgetError) as exc:
            budget.record_stage(f"stage-{wall}", wall_seconds=wall)
        assert exc.value.code == "INVALID_STAGE_TIME"

    with pytest.raises(BudgetError) as exc:
        budget.record_stage("cpu", wall_seconds=1.0, cpu_seconds=-1)
    assert exc.value.code == "INVALID_STAGE_TIME"


def test_snapshot_uses_single_clock_read():
    clock = CountingClock(0.0)
    budget = Budget(0.0, 60.0, clock)

    snapshot = budget.snapshot()

    assert clock.calls == 1
    assert snapshot["elapsed_seconds"] == 1.0


def test_snapshot_payload():
    clock = FakeClock(1000.0)
    budget = Budget(1000.0, 60.0, clock)
    clock.advance(10.0)
    budget.record_stage("training", wall_seconds=10.0, cpu_seconds=9.0)

    snapshot = budget.snapshot()

    assert snapshot["limit_seconds"] == 60.0
    assert snapshot["elapsed_seconds"] == 10.0
    assert snapshot["balance_seconds"] == 50.0
    assert snapshot["overrun_seconds"] == 0.0
    assert snapshot["milestones"] == {
        "search_stop_s": 54.0,
        "finalize_by_s": 57.0,
        "terminate_at_s": 58.0,
        "kill_at_s": 59.0,
    }
    assert snapshot["training"] == {
        "limit_s": 12.0,
        "generation_limit_s": 11.5,
        "tuning_limit_s": 0.5,
        "remaining_s": 2.0,
    }
    assert snapshot["decisions"] == {
        "can_search": True,
        "should_finalize": False,
        "past_finalize_deadline": False,
        "should_terminate": False,
        "should_kill": False,
        "timed_out": False,
        "is_overrun": False,
    }
    assert snapshot["stages"] == [
        {
            "stage": "training",
            "wall_seconds": 10.0,
            "cpu_seconds": 9.0,
        }
    ]
    assert snapshot["cpu_seconds_total"] == 9.0


def test_elapsed_starts_at_zero_and_uses_t0():
    clock = FakeClock(1000.0)
    budget = Budget(1000.0, 60.0, clock)

    assert budget.elapsed_seconds() == 0.0
    assert budget.balance_seconds() == 60.0

    clock.advance(2.5)

    assert budget.elapsed_seconds() == 2.5
    assert budget.balance_seconds() == 57.5
