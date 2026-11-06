"""Relógio monotônico e orçamento temporal de uma execução.

Marcos são frações do limite B, incluindo treino de até 0.20B. O saldo pode
ficar negativo e o excesso é registrado, nunca ignorado. Tempo de parede vem do
relógio monotônico injetável; CPU é registrada por etapa e somada separadamente.
Contrato em docs/05-experiment-budget.md.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
import time
from typing import Any, Callable

SEARCH_STOP_NUMERATOR = 9
SEARCH_STOP_DENOMINATOR = 10

FINALIZE_BY_NUMERATOR = 19
FINALIZE_BY_DENOMINATOR = 20

TERMINATE_AT_NUMERATOR = 29
TERMINATE_AT_DENOMINATOR = 30

KILL_AT_NUMERATOR = 59
KILL_AT_DENOMINATOR = 60

TRAINING_LIMIT_NUMERATOR = 1
TRAINING_LIMIT_DENOMINATOR = 5

GENERATION_PART = 115
TUNING_PART = 5
TRAINING_PARTS = 120


class BudgetError(ValueError):
    """Erro estável de configuração ou medição do orçamento."""

    def __init__(self, message: str, code: str) -> None:
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message


def _is_finite_number(value: Any) -> bool:
    return type(value) in (int, float) and math.isfinite(value)


def _validate_seconds(value: Any, name: str, code: str) -> float:
    if not _is_finite_number(value) or value < 0:
        raise BudgetError(f"{name} deve ser número finito >= 0", code)
    return float(value)


@dataclass(frozen=True)
class StageTime:
    """Tempo de parede e CPU observados em uma etapa."""

    stage: str
    wall_seconds: float
    cpu_seconds: float | None = None


class Budget:
    """Orçamento de parede e CPU com marcos proporcionais ao limite B."""

    def __init__(
        self,
        t0: float,
        limit_seconds: float,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if not _is_finite_number(t0):
            raise BudgetError("t0 deve ser número finito", "INVALID_T0")
        if not _is_finite_number(limit_seconds) or limit_seconds <= 0:
            raise BudgetError(
                "limit_seconds deve ser número finito > 0",
                "INVALID_LIMIT",
            )
        if not callable(clock):
            raise BudgetError("clock deve ser chamável", "INVALID_CLOCK")

        self.t0 = float(t0)
        self.limit_seconds = float(limit_seconds)
        self.clock = clock
        self._last_now = self.t0
        self._stages: dict[str, StageTime] = {}

        self.search_stop_seconds = self._fraction(
            SEARCH_STOP_NUMERATOR, SEARCH_STOP_DENOMINATOR
        )
        self.finalize_by_seconds = self._fraction(
            FINALIZE_BY_NUMERATOR, FINALIZE_BY_DENOMINATOR
        )
        self.terminate_at_seconds = self._fraction(
            TERMINATE_AT_NUMERATOR, TERMINATE_AT_DENOMINATOR
        )
        self.kill_at_seconds = self._fraction(
            KILL_AT_NUMERATOR, KILL_AT_DENOMINATOR
        )
        self.training_limit_seconds = self._fraction(
            TRAINING_LIMIT_NUMERATOR, TRAINING_LIMIT_DENOMINATOR
        )
        self.generation_limit_seconds = (
            self.training_limit_seconds * GENERATION_PART / TRAINING_PARTS
        )
        self.tuning_limit_seconds = (
            self.training_limit_seconds * TUNING_PART / TRAINING_PARTS
        )

    def _fraction(self, numerator: int, denominator: int) -> float:
        return self.limit_seconds * numerator / denominator

    def _read_clock(self) -> float:
        value = self.clock()
        if not _is_finite_number(value):
            raise BudgetError("clock retornou valor não finito", "INVALID_CLOCK")
        if value < self._last_now:
            raise BudgetError("clock retrocedeu", "CLOCK_WENT_BACKWARDS")
        self._last_now = float(value)
        return float(value)

    def now(self) -> float:
        return self._read_clock()

    def elapsed_seconds(self) -> float:
        return self._read_clock() - self.t0

    def balance_seconds(self) -> float:
        return self.limit_seconds - self.elapsed_seconds()

    def overrun_seconds(self) -> float:
        return max(0.0, self.elapsed_seconds() - self.limit_seconds)

    def is_overrun(self) -> bool:
        return self.elapsed_seconds() > self.limit_seconds

    def timed_out(self) -> bool:
        return self.elapsed_seconds() >= self.limit_seconds

    def can_search(self) -> bool:
        return self.elapsed_seconds() < self.search_stop_seconds

    def should_finalize(self) -> bool:
        return self.elapsed_seconds() >= self.search_stop_seconds

    def past_finalize_deadline(self) -> bool:
        return self.elapsed_seconds() >= self.finalize_by_seconds

    def should_terminate(self) -> bool:
        return self.elapsed_seconds() >= self.terminate_at_seconds

    def should_kill(self) -> bool:
        return self.elapsed_seconds() >= self.kill_at_seconds

    def training_remaining_seconds(self) -> float:
        return self.training_limit_seconds - self.elapsed_seconds()

    def can_train(self) -> bool:
        return self.elapsed_seconds() < self.training_limit_seconds

    def record_stage(
        self,
        stage: str,
        *,
        wall_seconds: float,
        cpu_seconds: float | None = None,
    ) -> StageTime:
        if not isinstance(stage, str) or not stage.strip():
            raise BudgetError(
                "stage deve ser string não vazia",
                "INVALID_STAGE_NAME",
            )
        if stage in self._stages:
            raise BudgetError(
                f"etapa já registrada: {stage}",
                "DUPLICATE_STAGE",
            )

        wall = _validate_seconds(
            wall_seconds,
            "wall_seconds",
            "INVALID_STAGE_TIME",
        )
        cpu: float | None = None
        if cpu_seconds is not None:
            cpu = _validate_seconds(
                cpu_seconds,
                "cpu_seconds",
                "INVALID_STAGE_TIME",
            )

        recorded = StageTime(stage=stage, wall_seconds=wall, cpu_seconds=cpu)
        self._stages[stage] = recorded
        return recorded

    def stage_times(self) -> tuple[StageTime, ...]:
        return tuple(self._stages.values())

    def cpu_seconds_total(self) -> float | None:
        stages = tuple(self._stages.values())
        if not stages or any(stage.cpu_seconds is None for stage in stages):
            return None
        return sum(
            stage.cpu_seconds
            for stage in stages
            if stage.cpu_seconds is not None
        )

    def _decision_flags(self, elapsed: float) -> dict[str, bool]:
        return {
            "can_search": elapsed < self.search_stop_seconds,
            "should_finalize": elapsed >= self.search_stop_seconds,
            "past_finalize_deadline": elapsed >= self.finalize_by_seconds,
            "should_terminate": elapsed >= self.terminate_at_seconds,
            "should_kill": elapsed >= self.kill_at_seconds,
            "timed_out": elapsed >= self.limit_seconds,
            "is_overrun": elapsed > self.limit_seconds,
        }

    def snapshot(self) -> dict[str, Any]:
        elapsed = self.elapsed_seconds()
        return {
            "limit_seconds": self.limit_seconds,
            "elapsed_seconds": elapsed,
            "balance_seconds": self.limit_seconds - elapsed,
            "overrun_seconds": max(0.0, elapsed - self.limit_seconds),
            "milestones": {
                "search_stop_s": self.search_stop_seconds,
                "finalize_by_s": self.finalize_by_seconds,
                "terminate_at_s": self.terminate_at_seconds,
                "kill_at_s": self.kill_at_seconds,
            },
            "training": {
                "limit_s": self.training_limit_seconds,
                "generation_limit_s": self.generation_limit_seconds,
                "tuning_limit_s": self.tuning_limit_seconds,
                "remaining_s": self.training_limit_seconds - elapsed,
            },
            "decisions": self._decision_flags(elapsed),
            "stages": [asdict(stage) for stage in self.stage_times()],
            "cpu_seconds_total": self.cpu_seconds_total(),
        }
