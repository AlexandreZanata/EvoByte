"""Geração local de pares de treinamento por completações uniformes.

Para cada estado parcial de uma construção aleatória, amostra até oito ações
legais. Para cada ação, faz duas completações uniformes independentes até a
maximalidade e usa como alvo a média de ``m_terminal - m_estado``. Os terminais
são verificados pelo verificador de execução. Nada é treinado aqui.
Contrato em docs/01-scientific-protocol.md.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Any

from ..budget import Budget
from ..candidate import Candidate, create_candidate
from ..search.actions import LegalActionsError, legal_additions
from ..validation.runtime import validate as validate_runtime
from .features import FEATURES_VERSION, FeatureError, compute_features

ALLOWED_DATA_SIZES = frozenset({8, 10, 12, 16})
MAX_TRAINING_PAIRS = 4096
MAX_ACTIONS_PER_STATE = 8
COMPLETIONS_PER_ACTION = 2


class TrainingDataError(ValueError):
    """Erro estável do gerador de dados de treinamento."""

    def __init__(self, message: str, code: str) -> None:
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message


@dataclass(frozen=True)
class TrainingPair:
    pair_id: int
    n: int
    state_m: int
    state_sha256: str
    action: tuple[int, int]
    features: tuple[float, ...]
    target: float
    terminal_ms: tuple[int, int]
    terminal_sha256: tuple[str, str]
    features_version: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TrainingCounters:
    n: int
    max_pairs: int
    states: int
    actions_sampled: int
    pairs: int
    incomplete_pairs: int
    invalid_terminals: int
    rollouts: int
    evaluations: int
    legal_mask_queries: int
    feature_legal_mask_queries: int
    feature_bfs_queries: int
    completion_steps: int
    budget_stop: bool
    stop_reason: str


@dataclass(frozen=True)
class TrainingDataset:
    pairs: tuple[TrainingPair, ...]
    counters: TrainingCounters
    features_version: str

    def xy(self) -> tuple[tuple[tuple[float, ...], float], ...]:
        return tuple((pair.features, pair.target) for pair in self.pairs)

    def to_dict(self) -> dict[str, Any]:
        return {
            "features_version": self.features_version,
            "pairs": [pair.to_dict() for pair in self.pairs],
            "counters": asdict(self.counters),
        }


def _with_edge(candidate: Candidate, action: tuple[int, int]) -> Candidate:
    u, v = action
    edges = [list(edge) for edge in candidate.payload["edges"]]
    edges.append([u, v])
    return create_candidate(n=candidate.payload["n"], edges=edges)


def _check_inputs(
    n: Any,
    data_rng: Any,
    completion_rng: Any,
    budget: Any,
    max_pairs: Any,
    max_actions_per_state: Any,
) -> None:
    if type(n) is not int or n not in ALLOWED_DATA_SIZES:
        raise TrainingDataError(
            f"n deve estar em {sorted(ALLOWED_DATA_SIZES)}",
            "INVALID_N",
        )
    if not isinstance(budget, Budget):
        raise TrainingDataError(
            "budget deve ser uma instância de Budget",
            "INVALID_BUDGET",
        )
    for name, rng, methods in (
        ("data_rng", data_rng, ("choice", "sample")),
        ("completion_rng", completion_rng, ("choice",)),
    ):
        if not all(hasattr(rng, method) for method in methods):
            raise TrainingDataError(
                f"{name} não expõe {methods}",
                "INVALID_RNG",
            )
    if type(max_pairs) is not int or not 1 <= max_pairs <= MAX_TRAINING_PAIRS:
        raise TrainingDataError(
            f"max_pairs deve estar em [1, {MAX_TRAINING_PAIRS}]",
            "INVALID_MAX_PAIRS",
        )
    if (
        type(max_actions_per_state) is not int
        or not 1 <= max_actions_per_state <= MAX_ACTIONS_PER_STATE
    ):
        raise TrainingDataError(
            f"max_actions_per_state deve estar em [1, {MAX_ACTIONS_PER_STATE}]",
            "INVALID_MAX_ACTIONS",
        )


def generate_training_data(
    n: int,
    data_rng: Any,
    completion_rng: Any,
    budget: Budget,
    *,
    max_pairs: int = MAX_TRAINING_PAIRS,
    max_actions_per_state: int = MAX_ACTIONS_PER_STATE,
) -> TrainingDataset:
    """Gera até ``max_pairs`` pares, parando no teto ou no Budget."""
    _check_inputs(
        n,
        data_rng,
        completion_rng,
        budget,
        max_pairs,
        max_actions_per_state,
    )

    pairs: list[TrainingPair] = []
    states = 0
    actions_sampled = 0
    incomplete_pairs = 0
    invalid_terminals = 0
    rollouts = 0
    evaluations = 0
    legal_mask_queries = 0
    feature_legal_mask_queries = 0
    feature_bfs_queries = 0
    completion_steps = 0
    budget_stop = False
    stop_reason = "budget"

    state = create_candidate(n=n, edges=[])

    while len(pairs) < max_pairs:
        if not budget.can_search():
            budget_stop = True
            stop_reason = "budget"
            break

        try:
            legal_actions = legal_additions(state)
        except LegalActionsError as exc:
            raise TrainingDataError(
                f"estado inválido durante a geração: {exc.message}",
                "INVALID_STATE",
            ) from exc
        legal_mask_queries += 1

        if not legal_actions:
            state = create_candidate(n=n, edges=[])
            continue

        states += 1
        sampled_actions = data_rng.sample(
            legal_actions,
            min(max_actions_per_state, len(legal_actions)),
        )

        action_stop = False
        for action in sampled_actions:
            if len(pairs) >= max_pairs:
                stop_reason = "pair_cap"
                action_stop = True
                break
            if not budget.can_search():
                budget_stop = True
                stop_reason = "budget"
                action_stop = True
                break

            try:
                feature_vector = compute_features(state, action)
            except FeatureError as exc:
                raise TrainingDataError(
                    f"falha ao calcular características: {exc.message}",
                    "INVALID_STATE",
                ) from exc
            actions_sampled += 1
            feature_legal_mask_queries += feature_vector.cost.legal_mask_queries
            feature_bfs_queries += feature_vector.cost.bfs_queries

            base = _with_edge(state, action)
            terminal_ms: list[int] = []
            terminal_hashes: list[str] = []
            pair_complete = True
            pair_invalid = False

            for _ in range(COMPLETIONS_PER_ACTION):
                if not budget.can_search():
                    pair_complete = False
                    budget_stop = True
                    stop_reason = "budget"
                    break

                rollouts += 1
                terminal = base
                while True:
                    if not budget.can_search():
                        pair_complete = False
                        budget_stop = True
                        stop_reason = "budget"
                        break
                    try:
                        terminal_legal = legal_additions(terminal)
                    except LegalActionsError as exc:
                        raise TrainingDataError(
                            f"terminal inválido durante a geração: {exc.message}",
                            "INVALID_STATE",
                        ) from exc
                    legal_mask_queries += 1
                    if not terminal_legal:
                        break
                    terminal = _with_edge(
                        terminal,
                        completion_rng.choice(terminal_legal),
                    )
                    completion_steps += 1
                if not pair_complete:
                    break

                evaluation = validate_runtime(terminal.payload, n)
                evaluations += 1
                if not evaluation.valid:
                    invalid_terminals += 1
                    pair_complete = False
                    pair_invalid = True
                    break

                terminal_ms.append(terminal.m)
                terminal_hashes.append(terminal.content_sha256)

            if not pair_complete:
                if budget_stop:
                    incomplete_pairs += 1
                    action_stop = True
                    break
                if pair_invalid:
                    continue
                continue

            target = (
                terminal_ms[0] + terminal_ms[1]
            ) / 2.0 - state.m
            if not math.isfinite(target):
                raise TrainingDataError(
                    "alvo não finito",
                    "NON_FINITE_TARGET",
                )

            pairs.append(
                TrainingPair(
                    pair_id=len(pairs),
                    n=n,
                    state_m=state.m,
                    state_sha256=state.content_sha256,
                    action=action,
                    features=feature_vector.values,
                    target=target,
                    terminal_ms=(terminal_ms[0], terminal_ms[1]),
                    terminal_sha256=(terminal_hashes[0], terminal_hashes[1]),
                    features_version=feature_vector.version,
                )
            )

        if action_stop or len(pairs) >= max_pairs:
            if len(pairs) >= max_pairs:
                stop_reason = "pair_cap"
            break
        if not budget.can_search():
            budget_stop = True
            stop_reason = "budget"
            break

        state = _with_edge(state, data_rng.choice(legal_actions))

    if len(pairs) >= max_pairs:
        stop_reason = "pair_cap"

    counters = TrainingCounters(
        n=n,
        max_pairs=max_pairs,
        states=states,
        actions_sampled=actions_sampled,
        pairs=len(pairs),
        incomplete_pairs=incomplete_pairs,
        invalid_terminals=invalid_terminals,
        rollouts=rollouts,
        evaluations=evaluations,
        legal_mask_queries=legal_mask_queries,
        feature_legal_mask_queries=feature_legal_mask_queries,
        feature_bfs_queries=feature_bfs_queries,
        completion_steps=completion_steps,
        budget_stop=budget_stop,
        stop_reason=stop_reason,
    )
    return TrainingDataset(
        pairs=tuple(pairs),
        counters=counters,
        features_version=FEATURES_VERSION,
    )
