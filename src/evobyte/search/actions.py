"""Adições legais em grafos simples sem C3/C4.

Um par ausente é legal quando sua adição preserva a ausência de C3/C4. Para um
grafo válido, isso equivale a distância >= 4 ou vértices em componentes
diferentes. A máscara não é um verificador final e não compartilha núcleo com os
verificadores. Contrato em docs/03-architecture-and-contracts.md.
"""

from __future__ import annotations

from collections import deque

from ..candidate import (
    Candidate,
    CandidateValidationError,
    validate_and_normalize_payload,
)


class LegalActionsError(ValueError):
    """Erro estável de entrada da máscara de adições legais."""

    def __init__(self, message: str, code: str) -> None:
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message


def _has_c3_or_c4(adjacency: list[set[int]]) -> bool:
    n = len(adjacency)
    for u in range(n):
        for v in range(u + 1, n):
            common = adjacency[u] & adjacency[v]
            if not common:
                continue
            if v in adjacency[u]:
                return True
            if len(common) >= 2:
                return True
    return False


def _validated_adjacency(candidate: Candidate) -> list[set[int]]:
    if not isinstance(candidate, Candidate):
        raise LegalActionsError(
            "candidato deve ser uma instância de Candidate",
            "INVALID_CANDIDATE_TYPE",
        )

    try:
        payload = validate_and_normalize_payload(candidate.payload)
    except CandidateValidationError as exc:
        raise LegalActionsError(
            f"candidato estrutural inválido: {exc.message}",
            "INVALID_CANDIDATE",
        ) from exc

    n = payload["n"]
    adjacency: list[set[int]] = [set() for _ in range(n)]
    for u, v in payload["edges"]:
        adjacency[u].add(v)
        adjacency[v].add(u)

    if _has_c3_or_c4(adjacency):
        raise LegalActionsError(
            "candidato contém C3 ou C4",
            "INVALID_CANDIDATE",
        )

    return adjacency


def _distances(adjacency: list[set[int]], source: int) -> list[int]:
    distances = [-1] * len(adjacency)
    distances[source] = 0
    queue = deque([source])
    while queue:
        vertex = queue.popleft()
        for neighbor in adjacency[vertex]:
            if distances[neighbor] == -1:
                distances[neighbor] = distances[vertex] + 1
                queue.append(neighbor)
    return distances


def legal_additions(candidate: Candidate) -> tuple[tuple[int, int], ...]:
    """Retorna todos e somente os pares cuja adição mantém o grafo válido."""
    adjacency = _validated_adjacency(candidate)
    n = len(adjacency)
    additions: list[tuple[int, int]] = []

    for u in range(n):
        distances = _distances(adjacency, u)
        for v in range(u + 1, n):
            if v in adjacency[u]:
                continue
            distance = distances[v]
            if distance == -1 or distance >= 4:
                additions.append((u, v))

    return tuple(additions)
