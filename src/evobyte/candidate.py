"""Estrutura e serialização canônica do candidato estrutural do EvoByte.

Contrato especificado em docs/03-architecture-and-contracts.md.
Validação estrita de tipos, índices, laços e duplicatas na entrada bruta
antes de qualquer normalização.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Mapping

SCHEMA_VERSION = 1
DEFAULT_RULES_ID = "girth-ge-5-v1"
ALLOWED_PAYLOAD_KEYS = frozenset(
    {"schema_version", "rules_id", "n", "edges", "claimed_m"}
)


class CandidateValidationError(ValueError):
    """Erro de validação na estrutura ou campos do candidato."""

    def __init__(self, message: str, code: str) -> None:
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message


def _is_strict_int(val: Any) -> bool:
    """Verifica se val é estritamente int, rejeitando bool ou subclasses."""
    return type(val) is int


def canonical_json_bytes(payload: Mapping[str, Any]) -> bytes:
    """Produz a representação canônica exata em bytes UTF-8 de um payload JSON.

    Regras:
    - Chaves ordenadas lexicograficamente.
    - Separadores compactos sem espaços (',', ':').
    - allow_nan=False.
    - Sem nova linha final.
    """
    json_str = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
        ensure_ascii=False,
    )
    return json_str.encode("utf-8")


def compute_content_sha256(canonical_bytes: bytes) -> str:
    """Calcula o hash SHA-256 em hexadecimal minúsculo dos bytes canônicos."""
    return hashlib.sha256(canonical_bytes).hexdigest()


def validate_and_normalize_payload(raw_payload: Any) -> dict[str, Any]:
    """Valida estritamente a entrada bruta e retorna o payload normalizado.

    A validação rejeita tipos incorretos (incluindo bool para inteiros),
    chaves desconhecidas, laços e duplicatas (inclusive pares invertidos)
    ANTES de ordenar ou orientar as arestas.

    Retorna um dicionário normalizado com:
    - schema_version: 1
    - rules_id: str
    - n: int
    - edges: list[list[int]] ordenadas e orientadas u < v
    - claimed_m: int
    """
    if not isinstance(raw_payload, dict):
        raise CandidateValidationError(
            f"Payload deve ser um dicionário JSON, recebido: {type(raw_payload).__name__}",
            code="INVALID_PAYLOAD_TYPE",
        )

    # 1. Checagem de chaves desconhecidas e ausentes
    payload_keys = set(raw_payload.keys())
    unknown_keys = payload_keys - ALLOWED_PAYLOAD_KEYS
    if unknown_keys:
        raise CandidateValidationError(
            f"Chaves desconhecidas no payload: {sorted(unknown_keys)}",
            code="UNKNOWN_FIELD",
        )

    missing_keys = ALLOWED_PAYLOAD_KEYS - payload_keys
    if missing_keys:
        raise CandidateValidationError(
            f"Chaves obrigatórias ausentes no payload: {sorted(missing_keys)}",
            code="MISSING_FIELD",
        )

    # 2. Validação de schema_version
    schema_ver = raw_payload["schema_version"]
    if not _is_strict_int(schema_ver) or schema_ver != SCHEMA_VERSION:
        raise CandidateValidationError(
            f"schema_version deve ser inteiro {SCHEMA_VERSION}, recebido: {schema_ver!r}",
            code="INVALID_SCHEMA_VERSION",
        )

    # 3. Validação de rules_id
    rules_id = raw_payload["rules_id"]
    if not isinstance(rules_id, str) or not rules_id.strip():
        raise CandidateValidationError(
            f"rules_id deve ser string não-vazia, recebido: {rules_id!r}",
            code="INVALID_RULES_ID",
        )
    if rules_id != DEFAULT_RULES_ID:
        raise CandidateValidationError(
            f"rules_id inesperado: esperado '{DEFAULT_RULES_ID}', recebido '{rules_id}'",
            code="UNEXPECTED_RULES_ID",
        )

    # 4. Validação de n (ordem do grafo)
    n = raw_payload["n"]
    if not _is_strict_int(n) or n < 1:
        raise CandidateValidationError(
            f"n deve ser inteiro estrito >= 1, recebido: {n!r}",
            code="INVALID_ORDER",
        )

    # 5. Validação de edges (formato de lista)
    raw_edges = raw_payload["edges"]
    if not isinstance(raw_edges, list):
        raise CandidateValidationError(
            f"edges deve ser uma lista, recebido: {type(raw_edges).__name__}",
            code="INVALID_EDGES_TYPE",
        )

    # 6. Validação de claimed_m
    claimed_m = raw_payload["claimed_m"]
    if not _is_strict_int(claimed_m) or claimed_m < 0:
        raise CandidateValidationError(
            f"claimed_m deve ser inteiro estrito >= 0, recebido: {claimed_m!r}",
            code="INVALID_CLAIMED_M",
        )
    if claimed_m != len(raw_edges):
        raise CandidateValidationError(
            f"claimed_m ({claimed_m}) diverge da quantidade de arestas fornecidas ({len(raw_edges)})",
            code="CLAIMED_M_MISMATCH",
        )

    # 7. Validação estrita da lista bruta de arestas (sem deduplicação corretiva)
    seen_raw_edges: set[tuple[int, int]] = set()

    for idx, edge in enumerate(raw_edges):
        if not isinstance(edge, (list, tuple)) or len(edge) != 2:
            raise CandidateValidationError(
                f"Aresta no índice {idx} deve ser par [u, v], recebido: {edge!r}",
                code="INVALID_EDGE_FORMAT",
            )
        u, v = edge[0], edge[1]

        if not _is_strict_int(u) or not _is_strict_int(v):
            raise CandidateValidationError(
                f"Vértices da aresta {edge!r} no índice {idx} devem ser inteiros estritos",
                code="INVALID_VERTEX_TYPE",
            )

        if u < 0 or u >= n or v < 0 or v >= n:
            raise CandidateValidationError(
                f"Vértice fora dos limites [0, {n-1}] na aresta {edge!r} no índice {idx}",
                code="INDEX_OUT_OF_BOUNDS",
            )

        # Laço: u == v
        if u == v:
            raise CandidateValidationError(
                f"Laço detectado no vértice {u} na aresta {edge!r} no índice {idx}",
                code="LOOP_DETECTED",
            )

        # Checagem de duplicata na entrada bruta (inclusive invertida)
        if (u, v) in seen_raw_edges or (v, u) in seen_raw_edges:
            raise CandidateValidationError(
                f"Aresta duplicada ou par invertido detectado: {edge!r} no índice {idx}",
                code="DUPLICATE_EDGE",
            )

        seen_raw_edges.add((u, v))

    # 8. Normalização: orientar u < v e ordenar lexicograficamente
    normalized_edges = sorted([[min(u, v), max(u, v)] for u, v in seen_raw_edges])

    return {
        "schema_version": SCHEMA_VERSION,
        "rules_id": rules_id,
        "n": n,
        "edges": normalized_edges,
        "claimed_m": len(normalized_edges),
    }


@dataclass(frozen=True)
class Candidate:
    """Representação em memória de um candidato estrutural validado."""

    payload: dict[str, Any]
    canonical_bytes: bytes
    content_sha256: str
    run_id: str | None = None

    @property
    def n(self) -> int:
        return self.payload["n"]

    @property
    def m(self) -> int:
        return self.payload["claimed_m"]

    @property
    def edges(self) -> list[list[int]]:
        return self.payload["edges"]

    @property
    def rules_id(self) -> str:
        return self.payload["rules_id"]

    def to_envelope(self) -> dict[str, Any]:
        """Gera o envelope padrão para persistência em disco ou exportação."""
        return {
            "run_id": self.run_id,
            "payload": self.payload,
            "content_sha256": self.content_sha256,
        }

    def to_canonical_json(self) -> str:
        """Retorna a string JSON canônica do payload."""
        return self.canonical_bytes.decode("utf-8")


def candidate_from_payload(
    raw_payload: Any, run_id: str | None = None
) -> Candidate:
    """Constrói um Candidate a partir de um payload bruto após validação estrita."""
    normalized = validate_and_normalize_payload(raw_payload)
    canon_bytes = canonical_json_bytes(normalized)
    sha = compute_content_sha256(canon_bytes)
    return Candidate(
        payload=normalized,
        canonical_bytes=canon_bytes,
        content_sha256=sha,
        run_id=run_id,
    )


def create_candidate(
    n: int,
    edges: list[list[int]] | list[tuple[int, int]],
    rules_id: str = DEFAULT_RULES_ID,
    run_id: str | None = None,
) -> Candidate:
    """Cria e valida um Candidate diretamente a partir dos parâmetros estruturais."""
    raw_payload = {
        "schema_version": SCHEMA_VERSION,
        "rules_id": rules_id,
        "n": n,
        "edges": [list(e) for e in edges],
        "claimed_m": len(edges),
    }
    return candidate_from_payload(raw_payload, run_id=run_id)
