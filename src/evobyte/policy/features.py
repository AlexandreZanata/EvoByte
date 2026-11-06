"""Vetor de 12 características simétricas de uma ação legal.

As características seguem docs/01-scientific-protocol.md, são invariantes por
permutação de rótulos e simétricas na troca dos extremos. Nenhum identificador de
vértice entra no vetor. O cálculo não altera o candidato e mede separadamente
consultas de máscara legal e de distância.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import math
from typing import Any

from ..candidate import Candidate, create_candidate
from ..search.actions import LegalActionsError, legal_additions

FEATURES_VERSION = "symmetric-12-v1"

FEATURE_NAMES = (
    "n_over_32",
    "density",
    "legal_density",
    "degree_variance",
    "min_degree",
    "max_degree",
    "endpoint_min_degree",
    "endpoint_max_degree",
    "neighbor_degree_sum_min",
    "neighbor_degree_sum_max",
    "legal_density_delta",
    "distance",
)


class FeatureError(ValueError):
    """Erro estável da extração de características."""

    def __init__(self, message: str, code: str) -> None:
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message


@dataclass(frozen=True)
class FeatureCost:
    """Contadores separados de consultas usadas para calcular o vetor."""

    legal_mask_queries: int
    bfs_queries: int


@dataclass(frozen=True)
class FeatureVector:
    """Vetor de 12 floats finitos e a versão da especificação."""

    values: tuple[float, ...]
    version: str
    cost: FeatureCost

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "values": list(self.values),
            "cost": {
                "legal_mask_queries": self.cost.legal_mask_queries,
                "bfs_queries": self.cost.bfs_queries,
            },
        }


def _adjacency(candidate: Candidate) -> list[set[int]]:
    n = candidate.payload["n"]
    adjacency: list[set[int]] = [set() for _ in range(n)]
    for u, v in candidate.payload["edges"]:
        adjacency[u].add(v)
        adjacency[v].add(u)
    return adjacency


def _distance(
    adjacency: list[set[int]],
    source: int,
    target: int,
) -> int | None:
    distances = [-1] * len(adjacency)
    distances[source] = 0
    queue = deque([source])
    while queue:
        vertex = queue.popleft()
        if vertex == target:
            return distances[vertex]
        for neighbor in adjacency[vertex]:
            if distances[neighbor] == -1:
                distances[neighbor] = distances[vertex] + 1
                queue.append(neighbor)
    return None


def _normalized_action(action: Any, legal_actions: tuple[tuple[int, int], ...]) -> tuple[int, int]:
    if not isinstance(action, (tuple, list)) or len(action) != 2:
        raise FeatureError("ação deve ser um par [u, v]", "INVALID_ACTION")
    u, v = action
    if type(u) is not int or type(v) is not int or u == v:
        raise FeatureError(
            "ação deve conter dois vértices inteiros distintos",
            "INVALID_ACTION",
        )
    pair = (u, v) if u < v else (v, u)
    if pair not in legal_actions:
        raise FeatureError(
            f"ação não pertence à máscara legal: {pair}",
            "INVALID_ACTION",
        )
    return pair


def compute_features(candidate: Candidate, action: Any) -> FeatureVector:
    """Calcula o vetor symmetric-12-v1 sem modificar o candidato."""
    if not isinstance(candidate, Candidate):
        raise FeatureError(
            "candidato deve ser uma instância de Candidate",
            "INVALID_CANDIDATE_TYPE",
        )

    payload = candidate.payload
    n = payload.get("n") if isinstance(payload, dict) else None
    if type(n) is not int or n < 8:
        raise FeatureError(
            "n deve ser inteiro estrito >= 8",
            "INVALID_N",
        )

    try:
        legal_actions = legal_additions(candidate)
    except LegalActionsError as exc:
        raise FeatureError(
            f"candidato inválido para características: {exc.message}",
            "INVALID_CANDIDATE",
        ) from exc

    legal_mask_queries = 1
    u, v = _normalized_action(action, legal_actions)

    adjacency = _adjacency(candidate)
    degrees = [len(neighbors) for neighbors in adjacency]
    m = len(payload["edges"])
    binom = n * (n - 1) // 2

    sum_degrees = sum(degrees)
    sum_squared_degrees = sum(degree * degree for degree in degrees)
    variance_numerator = n * sum_squared_degrees - sum_degrees * sum_degrees
    variance_denominator = n * n * (n - 1) * (n - 1)

    neighbor_sum_u = sum(degrees[neighbor] for neighbor in adjacency[u])
    neighbor_sum_v = sum(degrees[neighbor] for neighbor in adjacency[v])

    after_candidate = create_candidate(
        n=n,
        edges=[*payload["edges"], [u, v]],
    )
    after_legal = legal_additions(after_candidate)
    legal_mask_queries += 1

    distance = _distance(adjacency, u, v)

    values = (
        n / 32.0,
        m / binom,
        len(legal_actions) / binom,
        variance_numerator / variance_denominator,
        min(degrees) / (n - 1),
        max(degrees) / (n - 1),
        min(degrees[u], degrees[v]) / (n - 1),
        max(degrees[u], degrees[v]) / (n - 1),
        min(neighbor_sum_u, neighbor_sum_v) / ((n - 1) * (n - 1)),
        max(neighbor_sum_u, neighbor_sum_v) / ((n - 1) * (n - 1)),
        (len(after_legal) - len(legal_actions)) / binom,
        1.0 if distance is None else min(distance, n) / n,
    )

    if not all(math.isfinite(value) for value in values):
        raise FeatureError(
            "vetor de características contém valor não finito",
            "NON_FINITE_FEATURE",
        )

    return FeatureVector(
        values=tuple(float(value) for value in values),
        version=FEATURES_VERSION,
        cost=FeatureCost(
            legal_mask_queries=legal_mask_queries,
            bfs_queries=1,
        ),
    )
