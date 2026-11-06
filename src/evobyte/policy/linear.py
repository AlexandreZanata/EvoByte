"""Ajuste ridge mínimo e seletor linear por maior escore.

Treze parâmetros: 12 pesos e intercepto. A penalidade ridge incide somente sobre
os pesos; o intercepto não é penalizado. Há um único ajuste após os dados, sem
treino online, CUDA ou PyTorch. Falhas de treino são explícitas, nunca trocadas
silenciosamente por heurística. Contrato em docs/01-scientific-protocol.md.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
import hashlib
import math
import time
from typing import Any

import numpy as np

from ..budget import Budget
from ..candidate import canonical_json_bytes
from .data import TrainingDataset
from .features import FEATURES_VERSION, compute_features

MIN_TRAINING_PAIRS = 32
FEATURE_DIMENSION = 12
PARAMETER_COUNT = 13


class LinearPolicyError(ValueError):
    """Erro estável de argumentos do ajuste ou do escore."""

    def __init__(self, message: str, code: str) -> None:
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message


@dataclass(frozen=True)
class TrainingFailure:
    status: str
    code: str
    reason: str
    pairs: int
    training_seconds: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "code": self.code,
            "reason": self.reason,
            "pairs": self.pairs,
            "training_seconds": self.training_seconds,
        }


def _failure(
    code: str,
    reason: str,
    pairs: int,
    training_seconds: float = 0.0,
) -> TrainingFailure:
    return TrainingFailure(
        status="training_failed",
        code=code,
        reason=reason,
        pairs=pairs,
        training_seconds=training_seconds,
    )


def _is_finite_number(value: Any) -> bool:
    return type(value) in (int, float) and math.isfinite(value)


def policy_hash(
    weights: Sequence[float],
    intercept: float,
    features_version: str = FEATURES_VERSION,
) -> str:
    payload = {
        "features_version": features_version,
        "weights": list(weights),
        "intercept": intercept,
    }
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


@dataclass(frozen=True)
class LinearPolicy:
    weights: tuple[float, ...]
    intercept: float
    features_version: str
    ridge_lambda: float
    training_pairs: int
    training_seconds: float
    weights_sha256: str

    @property
    def parameters(self) -> tuple[float, ...]:
        return (*self.weights, self.intercept)

    def score(self, features: Sequence[float]) -> float:
        if not isinstance(features, (tuple, list)) or len(features) != FEATURE_DIMENSION:
            raise LinearPolicyError(
                "vetor de características deve ter 12 valores",
                "INVALID_FEATURE_VECTOR",
            )
        values = []
        for value in features:
            if not _is_finite_number(value):
                raise LinearPolicyError(
                    "vetor de características contém valor não finito",
                    "NON_FINITE_FEATURE",
                )
            values.append(float(value))
        total = self.intercept + sum(
            weight * value for weight, value in zip(self.weights, values)
        )
        if not math.isfinite(total):
            raise LinearPolicyError(
                "escore não finito",
                "NON_FINITE_SCORE",
            )
        return total

    def select(self, candidate, legal_actions, rng, budget) -> tuple[int, int] | None:
        if not legal_actions or not budget.can_search():
            return None

        scored = []
        for action in legal_actions:
            feature_vector = compute_features(candidate, action)
            scored.append((self.score(feature_vector.values), action))

        best_score = max(score for score, _ in scored)
        best_actions = [
            action for score, action in scored if score == best_score
        ]
        return rng.choice(best_actions)

    def to_dict(self) -> dict[str, Any]:
        return {
            "features_version": self.features_version,
            "weights": list(self.weights),
            "intercept": self.intercept,
            "parameters": list(self.parameters),
            "ridge_lambda": self.ridge_lambda,
            "training_pairs": self.training_pairs,
            "training_seconds": self.training_seconds,
            "weights_sha256": self.weights_sha256,
        }


def _extract_pairs(pairs: Any, features_version: str) -> list[Any]:
    if isinstance(pairs, TrainingDataset):
        if pairs.features_version != features_version:
            raise _VersionMismatch(len(pairs.pairs))
        return list(pairs.xy())
    if isinstance(pairs, Sequence) and not isinstance(pairs, (str, bytes)):
        return list(pairs)
    raise LinearPolicyError(
        "pairs deve ser TrainingDataset ou sequência de pares (x, y)",
        "INVALID_PAIRS",
    )


class _VersionMismatch(Exception):
    def __init__(self, pairs: int) -> None:
        super().__init__("features_version divergente")
        self.pairs = pairs


def _validated_matrix(data: list[Any]) -> tuple[np.ndarray, np.ndarray] | TrainingFailure:
    xs = []
    ys = []
    for item in data:
        if not isinstance(item, (tuple, list)) or len(item) != 2:
            return _failure(
                "INVALID_DIMENSION",
                "cada par deve ser (x, y)",
                len(data),
            )
        x, y = item
        if not isinstance(x, (tuple, list)) or len(x) != FEATURE_DIMENSION:
            return _failure(
                "INVALID_DIMENSION",
                "cada x deve ter 12 valores",
                len(data),
            )
        x_values = []
        for value in x:
            if not _is_finite_number(value):
                return _failure(
                    "NON_FINITE_VALUE",
                    "x contém valor não finito",
                    len(data),
                )
            x_values.append(float(value))
        if not _is_finite_number(y):
            return _failure(
                "NON_FINITE_VALUE",
                "y contém valor não finito",
                len(data),
            )
        xs.append(x_values)
        ys.append(float(y))
    return np.asarray(xs, dtype=float), np.asarray(ys, dtype=float)


def fit_linear_policy(
    pairs: Any,
    *,
    ridge_lambda: float,
    budget: Budget,
    features_version: str = FEATURES_VERSION,
) -> LinearPolicy | TrainingFailure:
    """Ajusta uma única vez o ridge e devolve política ou training_failed."""
    if not isinstance(budget, Budget):
        raise LinearPolicyError(
            "budget deve ser uma instância de Budget",
            "INVALID_BUDGET",
        )
    if not _is_finite_number(ridge_lambda) or ridge_lambda < 0:
        raise LinearPolicyError(
            "ridge_lambda deve ser número finito >= 0",
            "INVALID_LAMBDA",
        )
    if features_version != FEATURES_VERSION:
        raise LinearPolicyError(
            f"features_version deve ser {FEATURES_VERSION}",
            "INVALID_FEATURES_VERSION",
        )

    try:
        data = _extract_pairs(pairs, features_version)
    except _VersionMismatch as exc:
        return _failure(
            "FEATURES_VERSION_MISMATCH",
            "versão de características do dataset diverge",
            exc.pairs,
        )

    pair_count = len(data)
    if pair_count < MIN_TRAINING_PAIRS:
        return _failure(
            "INSUFFICIENT_PAIRS",
            f"mínimo de {MIN_TRAINING_PAIRS} pares",
            pair_count,
        )

    validated = _validated_matrix(data)
    if isinstance(validated, TrainingFailure):
        return validated
    features, targets = validated

    if not budget.can_search():
        return _failure(
            "TRAINING_TIME_EXCEEDED",
            "teto de treino esgotado antes do ajuste",
            pair_count,
        )

    started = time.monotonic()
    design = np.column_stack([features, np.ones(pair_count)])
    penalty = np.eye(PARAMETER_COUNT) * float(ridge_lambda)
    penalty[-1, -1] = 0.0

    try:
        beta = np.linalg.solve(
            design.T @ design + penalty,
            design.T @ targets,
        )
    except np.linalg.LinAlgError:
        return _failure(
            "NUMERICAL_FAILURE",
            "sistema ridge singular ou não resolvido",
            pair_count,
            time.monotonic() - started,
        )

    training_seconds = time.monotonic() - started
    if not np.all(np.isfinite(beta)):
        return _failure(
            "NUMERICAL_FAILURE",
            "coeficientes não finitos",
            pair_count,
            training_seconds,
        )
    if not budget.can_search():
        return _failure(
            "TRAINING_TIME_EXCEEDED",
            "teto de treino esgotado durante o ajuste",
            pair_count,
            training_seconds,
        )

    weights = tuple(float(value) for value in beta[:-1])
    intercept = float(beta[-1])
    return LinearPolicy(
        weights=weights,
        intercept=intercept,
        features_version=features_version,
        ridge_lambda=float(ridge_lambda),
        training_pairs=pair_count,
        training_seconds=training_seconds,
        weights_sha256=policy_hash(weights, intercept, features_version),
    )
