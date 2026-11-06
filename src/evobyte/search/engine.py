"""Motor construtivo interrompível para referências não aprendidas.

O laço parte do grafo vazio, adiciona ações da máscara legal até maximalidade e
reinicia enquanto houver tempo, preservando a melhor construção observada. O
motor não certifica resultados; a certificação usa o contrato existente.
Contrato em docs/03-architecture-and-contracts.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from ..budget import Budget
from ..candidate import Candidate, create_candidate
from .actions import legal_additions
from .selectors import Selector

EventEmitter = Callable[[dict[str, Any]], None]


class SearchError(ValueError):
    """Erro estável do motor ou do seletor."""

    def __init__(self, message: str, code: str) -> None:
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message


@dataclass(frozen=True)
class SearchConfig:
    """Configuração mínima do motor construtivo."""

    n: int

    def __post_init__(self) -> None:
        if type(self.n) is not int or self.n < 1:
            raise SearchError(
                "n deve ser inteiro estrito >= 1",
                "INVALID_CONFIG",
            )


@dataclass(frozen=True)
class SearchOutcome:
    """Melhor construção retida e contadores observados pelo motor."""

    best_candidate: Candidate
    best_m: int
    constructions: int
    restarts: int
    actions_added: int
    legal_mask_queries: int
    elapsed_seconds: float
    stopped_by_budget: bool
    stopped_reason: str
    best_is_maximal: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "best_m": self.best_m,
            "best_sha256": self.best_candidate.content_sha256,
            "best_candidate": self.best_candidate.payload,
            "constructions": self.constructions,
            "restarts": self.restarts,
            "actions_added": self.actions_added,
            "legal_mask_queries": self.legal_mask_queries,
            "elapsed_seconds": self.elapsed_seconds,
            "stopped_by_budget": self.stopped_by_budget,
            "stopped_reason": self.stopped_reason,
            "best_is_maximal": self.best_is_maximal,
        }


def _emit(emit: EventEmitter | None, event: dict[str, Any]) -> None:
    if emit is not None:
        emit(event)


def _with_edge(candidate: Candidate, action: tuple[int, int]) -> Candidate:
    u, v = action
    edges = [list(edge) for edge in candidate.payload["edges"]]
    edges.append([u, v])
    return create_candidate(n=candidate.payload["n"], edges=edges)


def _action_for_event(action: Any) -> Any:
    if isinstance(action, (list, tuple)):
        return list(action)
    return str(action)


def run_search(
    config: SearchConfig,
    selector: Selector,
    budget: Budget,
    rng: Any,
    emit: EventEmitter | None = None,
) -> SearchOutcome:
    """Executa o laço construtivo até o Budget ou até não haver ações."""
    if not isinstance(config, SearchConfig):
        raise SearchError("config deve ser SearchConfig", "INVALID_CONFIG")
    if not isinstance(budget, Budget):
        raise SearchError("budget deve ser uma instância de Budget", "INVALID_BUDGET")
    if not hasattr(selector, "select") or not callable(selector.select):
        raise SearchError("selector deve expor select()", "INVALID_SELECTOR")

    n = config.n
    candidate = create_candidate(n=n, edges=[])
    best = candidate
    best_m = 0
    best_is_maximal = False
    constructions = 0
    restarts = 0
    actions_added = 0
    legal_mask_queries = 0
    stopped_reason = "budget"

    _emit(
        emit,
        {
            "event": "start",
            "n": n,
            "best_m": 0,
            "elapsed_seconds": budget.elapsed_seconds(),
        },
    )

    while budget.can_search():
        legal_actions = legal_additions(candidate)
        legal_mask_queries += 1

        if not legal_actions:
            constructions += 1
            improved = candidate.m > best_m or (
                candidate.m == best_m and not best_is_maximal
            )
            if improved:
                best = candidate
                best_m = candidate.m
                best_is_maximal = True
                _emit(
                    emit,
                    {
                        "event": "new_best",
                        "best_m": best_m,
                        "candidate_sha256": best.content_sha256,
                        "maximal": True,
                        "elapsed_seconds": budget.elapsed_seconds(),
                    },
                )
            _emit(
                emit,
                {
                    "event": "maximal",
                    "m": candidate.m,
                    "construction": constructions,
                    "best_m": best_m,
                    "elapsed_seconds": budget.elapsed_seconds(),
                },
            )

            if candidate.m == 0:
                stopped_reason = "no_legal_actions"
                break
            if not budget.can_search():
                stopped_reason = "budget"
                break

            candidate = create_candidate(n=n, edges=[])
            restarts += 1
            _emit(
                emit,
                {
                    "event": "restart",
                    "construction": constructions + 1,
                    "best_m": best_m,
                    "elapsed_seconds": budget.elapsed_seconds(),
                },
            )
            continue

        action = selector.select(candidate, legal_actions, rng, budget)
        if action is None:
            if not budget.can_search():
                stopped_reason = "budget"
                break
            _emit(
                emit,
                {
                    "event": "invalid_selector_stop",
                    "legal_actions": len(legal_actions),
                    "best_m": best_m,
                    "elapsed_seconds": budget.elapsed_seconds(),
                },
            )
            raise SearchError(
                "seletor retornou None com ações legais e saldo disponível",
                "SELECTOR_STOPPED_WITH_BUDGET",
            )

        if action not in legal_actions:
            _emit(
                emit,
                {
                    "event": "invalid_action",
                    "action": _action_for_event(action),
                    "legal_actions": len(legal_actions),
                    "elapsed_seconds": budget.elapsed_seconds(),
                },
            )
            raise SearchError(
                f"ação fora da máscara legal: {action!r}",
                "SELECTOR_INVALID_ACTION",
            )

        if not budget.can_search():
            stopped_reason = "budget"
            break

        candidate = _with_edge(candidate, action)
        actions_added += 1

        if candidate.m > best_m:
            best = candidate
            best_m = candidate.m
            best_is_maximal = False
            _emit(
                emit,
                {
                    "event": "new_best",
                    "best_m": best_m,
                    "candidate_sha256": best.content_sha256,
                    "maximal": False,
                    "elapsed_seconds": budget.elapsed_seconds(),
                },
            )

    legal_mask_queries += 1
    best_is_maximal = not legal_additions(best)
    elapsed_seconds = budget.elapsed_seconds()
    stopped_by_budget = stopped_reason == "budget"

    outcome = SearchOutcome(
        best_candidate=best,
        best_m=best_m,
        constructions=constructions,
        restarts=restarts,
        actions_added=actions_added,
        legal_mask_queries=legal_mask_queries,
        elapsed_seconds=elapsed_seconds,
        stopped_by_budget=stopped_by_budget,
        stopped_reason=stopped_reason,
        best_is_maximal=best_is_maximal,
    )
    _emit(
        emit,
        {
            "event": "stop",
            "reason": stopped_reason,
            "best_m": best_m,
            "construction": constructions,
            "restarts": restarts,
            "actions_added": actions_added,
            "legal_mask_queries": legal_mask_queries,
            "elapsed_seconds": elapsed_seconds,
        },
    )
    return outcome
