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
