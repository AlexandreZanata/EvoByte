"""Motor construtivo interrompível para referências não aprendidas.

O laço parte do grafo vazio, adiciona ações da máscara legal até maximalidade e,
conforme a configuração, reinicia ou perturba a construção atual. O melhor
candidato é sempre preservado. O motor não certifica resultados; a certificação
usa o contrato existente. Contrato em docs/03-architecture-and-contracts.md.
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
    """Configuração do motor: construtiva ou local com perturbação."""

    n: int
    k_max: int = 0
    stagnation_limit: int | None = None

    def __post_init__(self) -> None:
        if type(self.n) is not int or self.n < 1:
            raise SearchError(
                "n deve ser inteiro estrito >= 1",
                "INVALID_CONFIG",
            )
        if type(self.k_max) is not int or self.k_max < 0:
            raise SearchError(
                "k_max deve ser inteiro estrito >= 0",
                "INVALID_CONFIG",
            )
        if self.k_max == 0:
            if self.stagnation_limit is not None:
                raise SearchError(
                    "stagnation_limit deve ser None no modo construtivo",
                    "INVALID_CONFIG",
                )
        elif (
            type(self.stagnation_limit) is not int
            or self.stagnation_limit < 1
        ):
            raise SearchError(
                "stagnation_limit deve ser inteiro estrito >= 1 no modo local",
                "INVALID_CONFIG",
            )

    @property
    def local(self) -> bool:
        return self.k_max > 0


@dataclass(frozen=True)
class SearchOutcome:
    """Melhor construção retida e contadores observados pelo motor."""

    best_candidate: Candidate
    best_m: int
    constructions: int
    restarts: int
    perturbations: int
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
            "perturbations": self.perturbations,
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


def _perturb(
    candidate: Candidate,
    k_max: int,
    rng: Any,
) -> tuple[Candidate, list[list[int]]]:
    edges = [list(edge) for edge in candidate.payload["edges"]]
    if not edges:
        return candidate, []

    count = rng.randint(1, min(k_max, len(edges)))
    removed = rng.sample(edges, count)
    removed_keys = {tuple(sorted(edge)) for edge in removed}
    remaining = [
        edge
        for edge in edges
        if tuple(sorted(edge)) not in removed_keys
    ]
    reduced = create_candidate(
        n=candidate.payload["n"],
        edges=remaining,
    )
    return reduced, removed


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
    *,
    perturbation_rng: Any | None = None,
) -> SearchOutcome:
    """Executa o laço até o Budget ou até não haver ações.

    Com ``k_max=0`` o motor reinicia em maximalidade. Com ``k_max>0`` ele remove
    de 1 até ``k_max`` arestas, preenche novamente e reinicia após
    ``stagnation_limit`` ciclos sem melhora do melhor ``m``.
    """
    if not isinstance(config, SearchConfig):
        raise SearchError("config deve ser SearchConfig", "INVALID_CONFIG")
    if not isinstance(budget, Budget):
        raise SearchError("budget deve ser uma instância de Budget", "INVALID_BUDGET")
    if not hasattr(selector, "select") or not callable(selector.select):
        raise SearchError("selector deve expor select()", "INVALID_SELECTOR")

    removal_rng = perturbation_rng if perturbation_rng is not None else rng
    if config.local and (
        not hasattr(removal_rng, "randint")
        or not hasattr(removal_rng, "sample")
    ):
        raise SearchError(
            "perturbation_rng deve expor randint() e sample()",
            "INVALID_PERTURBATION_RNG",
        )

    n = config.n
    candidate = create_candidate(n=n, edges=[])
    best = candidate
    best_m = 0
    best_is_maximal = False
    constructions = 0
    restarts = 0
    perturbations = 0
    actions_added = 0
    legal_mask_queries = 0
    stagnation = 0
    improved_since_fill = False
    stopped_reason = "budget"

    _emit(
        emit,
        {
            "event": "start",
            "n": n,
            "k_max": config.k_max,
            "stagnation_limit": config.stagnation_limit,
            "best_m": 0,
            "elapsed_seconds": budget.elapsed_seconds(),
        },
    )

    while budget.can_search():
        legal_actions = legal_additions(candidate)
        legal_mask_queries += 1

        if not legal_actions:
            constructions += 1
            strict_improvement = candidate.m > best_m
            improved = strict_improvement or (
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
            if strict_improvement:
                improved_since_fill = True
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

            if not config.local:
                candidate = create_candidate(n=n, edges=[])
                restarts += 1
                _emit(
                    emit,
                    {
                        "event": "restart",
                        "reason": "maximality",
                        "construction": constructions + 1,
                        "best_m": best_m,
                        "stagnation": 0,
                        "elapsed_seconds": budget.elapsed_seconds(),
                    },
                )
                continue

            if improved_since_fill:
                stagnation = 0
            else:
                stagnation += 1
            improved_since_fill = False

            if stagnation >= config.stagnation_limit:
                candidate = create_candidate(n=n, edges=[])
                restarts += 1
                _emit(
                    emit,
                    {
                        "event": "restart",
                        "reason": "stagnation",
                        "construction": constructions + 1,
                        "best_m": best_m,
                        "stagnation": stagnation,
                        "elapsed_seconds": budget.elapsed_seconds(),
                    },
                )
                stagnation = 0
                continue

            candidate, removed = _perturb(candidate, config.k_max, removal_rng)
            perturbations += 1
            _emit(
                emit,
                {
                    "event": "perturbation",
                    "removed": removed,
                    "removed_count": len(removed),
                    "m": candidate.m,
                    "stagnation": stagnation,
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
            improved_since_fill = True
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
        perturbations=perturbations,
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
            "perturbations": perturbations,
            "actions_added": actions_added,
            "legal_mask_queries": legal_mask_queries,
            "elapsed_seconds": elapsed_seconds,
        },
    )
    return outcome
