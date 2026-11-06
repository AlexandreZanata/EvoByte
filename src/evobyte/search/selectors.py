"""Seletores de adição para o motor construtivo.

O seletor recebe a lista completa de ações legais, o RNG explícito e o Budget.
Retorna ``None`` somente quando não há ações ou o prazo exige parar.
"""

from __future__ import annotations

from typing import Any, Protocol, Sequence

from ..budget import Budget
from ..candidate import Candidate

Action = tuple[int, int]


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

        return rng.choice(best_actions)
