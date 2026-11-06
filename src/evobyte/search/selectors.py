"""Seletores de adição para o motor construtivo.

O seletor recebe a lista completa de ações legais, o RNG explícito e o Budget.
Retorna ``None`` somente quando não há ações ou o prazo exige parar.
"""

from __future__ import annotations

import math
from typing import Any, Protocol, Sequence

from ..budget import Budget
from ..candidate import Candidate
from ..policy.features import compute_features

Action = tuple[int, int]


class SelectorError(ValueError):
    """Erro estável de configuração de seletor."""

    def __init__(self, message: str, code: str) -> None:
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message


class Selector(Protocol):
    def select(
        self,
        candidate: Candidate,
        legal_actions: Sequence[Action],
        rng: Any,
        budget: Budget,
    ) -> Action | None: ...


class UniformSelector:
    """Escolhe uniformemente entre todas as ações legais."""

    def select(
        self,
        candidate: Candidate,
        legal_actions: Sequence[Action],
        rng: Any,
        budget: Budget,
    ) -> Action | None:
        if not legal_actions or not budget.can_search():
            return None
        return rng.choice(legal_actions)


class GreedySelector:
    """Escolhe a aresta legal de maior soma de graus, com desempate uniforme."""

    def select(
        self,
        candidate: Candidate,
        legal_actions: Sequence[Action],
        rng: Any,
        budget: Budget,
    ) -> Action | None:
        if not legal_actions or not budget.can_search():
            return None
        return rng.choice(_best_by_degree(candidate, legal_actions))


def _best_by_degree(
    candidate: Candidate,
    legal_actions: Sequence[Action],
) -> list[Action]:
    degrees = [0] * candidate.n
    for u, v in candidate.payload["edges"]:
        degrees[u] += 1
        degrees[v] += 1

    best_score = -1
    best_actions: list[Action] = []
    for action in legal_actions:
        u, v = action
        score = degrees[u] + degrees[v]
        if score > best_score:
            best_score = score
            best_actions = [action]
        elif score == best_score:
            best_actions.append(action)
    return best_actions


class ManualSelector:
    """Maior soma de graus com probabilidade p; uniforme com 1-p."""

    def __init__(self, p: float) -> None:
        if type(p) not in (int, float) or not math.isfinite(p) or not 0 <= p <= 1:
            raise SelectorError(
                "p deve ser número finito em [0, 1]",
                "INVALID_P",
            )
        self.p = float(p)

    def select(
        self,
        candidate: Candidate,
        legal_actions: Sequence[Action],
        rng: Any,
        budget: Budget,
    ) -> Action | None:
        if not legal_actions or not budget.can_search():
            return None
        if rng.random() < self.p:
            return rng.choice(_best_by_degree(candidate, legal_actions))
        return rng.choice(legal_actions)



class LinearWeightsSelector:
    """Seletor linear com pesos fornecidos e mesmas 12 características."""

    def __init__(self, weights: Sequence[float], intercept: float = 0.0) -> None:
        if not isinstance(weights, (list, tuple)) or len(weights) != 12:
            raise SelectorError(
                "weights deve conter 12 valores",
                "INVALID_WEIGHTS",
            )
        values = []
        for weight in weights:
            if type(weight) not in (int, float) or not math.isfinite(weight):
                raise SelectorError(
                    "weights deve conter valores finitos",
                    "INVALID_WEIGHTS",
                )
            values.append(float(weight))
        if type(intercept) not in (int, float) or not math.isfinite(intercept):
            raise SelectorError(
                "intercept deve ser finito",
                "INVALID_WEIGHTS",
            )
        self.weights = tuple(values)
        self.intercept = float(intercept)
        self.selections = 0
        self.feature_evaluations = 0
        self.feature_legal_mask_queries = 0
        self.feature_bfs_queries = 0

    def select(
        self,
        candidate: Candidate,
        legal_actions: Sequence[Action],
        rng: Any,
        budget: Budget,
    ) -> Action | None:
        if not legal_actions or not budget.can_search():
            return None

        self.selections += 1
        scored = []
        for action in legal_actions:
            feature_vector = compute_features(candidate, action)
            self.feature_evaluations += 1
            self.feature_legal_mask_queries += feature_vector.cost.legal_mask_queries
            self.feature_bfs_queries += feature_vector.cost.bfs_queries
            score = self.intercept + sum(
                weight * value
                for weight, value in zip(self.weights, feature_vector.values)
            )
            scored.append((score, action))

        best_score = max(score for score, _ in scored)
        best_actions = [
            action for score, action in scored if score == best_score
        ]
        return rng.choice(best_actions)

    def to_dict(self) -> dict[str, Any]:
        return {
            "weights": list(self.weights),
            "intercept": self.intercept,
            "selections": self.selections,
            "feature_evaluations": self.feature_evaluations,
            "feature_legal_mask_queries": self.feature_legal_mask_queries,
            "feature_bfs_queries": self.feature_bfs_queries,
        }


def make_selector(
    method: str,
    *,
    p: float | None = None,
    weights: Sequence[float] | None = None,
    intercept: float = 0.0,
    policy: Any | None = None,
) -> Any:
    """Fábrica dos seis braços sem alterar o motor."""
    if method in ("random", "local_uniform"):
        return UniformSelector()
    if method == "greedy":
        return GreedySelector()
    if method == "local_manual":
        if p is None:
            raise SelectorError("p é obrigatório", "INVALID_P")
        return ManualSelector(p)
    if method == "local_linear":
        if (
            policy is None
            or not hasattr(policy, "weights")
            or not hasattr(policy, "intercept")
        ):
            raise SelectorError(
                "política ajustada é obrigatória",
                "INVALID_POLICY",
            )
        return LinearWeightsSelector(policy.weights, policy.intercept)
    if method == "local_untrained":
        if weights is None:
            raise SelectorError(
                "pesos iniciais são obrigatórios",
                "INVALID_WEIGHTS",
            )
        return LinearWeightsSelector(weights, intercept)
    raise SelectorError(
        f"método desconhecido: {method!r}",
        "UNKNOWN_METHOD",
    )
