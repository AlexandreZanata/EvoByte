"""Verificador de referência independente para grafos sem C3 e sem C4.

Implementação legível, sem motor, sem NumPy e sem o parser estrutural de
``evobyte.candidate``. Contrato em docs/03-architecture-and-contracts.md.
"""

from __future__ import annotations

import hashlib
import json
import os
from typing import Any

from . import ValidationResult, Violation

VALIDATOR_ID = "evobyte-reference"
VALIDATOR_VERSION = "1"
SCHEMA_VERSION = 1
RULES_ID = "girth-ge-5-v1"
ALLOWED_PAYLOAD_KEYS = frozenset(
    {"schema_version", "rules_id", "n", "edges", "claimed_m"}
)


def _is_strict_int(value: Any) -> bool:
    return type(value) is int


def _code_commit() -> str | None:
    return os.environ.get("EVOBYTE_CODE_COMMIT") or None


def _canonical_sha256(raw_payload: Any) -> str | None:
    try:
        encoded = json.dumps(
            raw_payload,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
            ensure_ascii=False,
        ).encode("utf-8")
    except (TypeError, ValueError):
        return None
    return hashlib.sha256(encoded).hexdigest()


def _count_edges_twice(edges: list[Any]) -> tuple[int, int]:
    first = 0
    for _ in edges:
        first += 1
    second = 0
    for _ in edges:
        second += 1
    return first, second


def _result(
    violations: list[Violation],
    computed_m: int | None,
    payload_sha256: str | None,
) -> ValidationResult:
    return ValidationResult(
        valid=not violations,
        computed_m=computed_m,
        violations=tuple(violations),
        validator_id=VALIDATOR_ID,
        validator_version=VALIDATOR_VERSION,
        code_commit=_code_commit(),
        payload_sha256=payload_sha256,
    )


def _closes_cycle(adjacency: list[set[int]], order: tuple[int, ...]) -> bool:
    for index, vertex in enumerate(order):
        neighbor = order[(index + 1) % len(order)]
        if neighbor not in adjacency[vertex]:
            return False
    return True


def validate(raw_payload: Any, expected_n: Any) -> ValidationResult:
    """Valida um payload bruto contra as regras de cintura >= 5.

    A estrutura é verificada de forma própria, antes de qualquer enumeração.
    Se houver qualquer violação estrutural, a enumeração de ciclos é omitida
    para não emitir testemunhos sobre uma adjacência não confiável.
    """
    violations: list[Violation] = []
    payload_sha256 = _canonical_sha256(raw_payload)

    expected_n_valid = _is_strict_int(expected_n) and expected_n >= 1
    if not expected_n_valid:
        violations.append(Violation("INVALID_EXPECTED_N", (expected_n,)))

    if not isinstance(raw_payload, dict):
        violations.append(
            Violation("INVALID_PAYLOAD_TYPE", (type(raw_payload).__name__,))
        )
        return _result(violations, None, payload_sha256)

    payload_keys = set(raw_payload.keys())
    unknown_keys = sorted(payload_keys - ALLOWED_PAYLOAD_KEYS)
    if unknown_keys:
        violations.append(Violation("UNKNOWN_FIELD", tuple(unknown_keys)))
    missing_keys = sorted(ALLOWED_PAYLOAD_KEYS - payload_keys)
    if missing_keys:
        violations.append(Violation("MISSING_FIELD", tuple(missing_keys)))
        return _result(violations, None, payload_sha256)

    schema_version = raw_payload["schema_version"]
    if not _is_strict_int(schema_version) or schema_version != SCHEMA_VERSION:
        violations.append(Violation("INVALID_SCHEMA_VERSION", (schema_version,)))

    rules_id = raw_payload["rules_id"]
    if not isinstance(rules_id, str) or not rules_id.strip():
        violations.append(Violation("INVALID_RULES_ID", (rules_id,)))
    elif rules_id != RULES_ID:
        violations.append(Violation("UNEXPECTED_RULES_ID", (rules_id,)))

    n = raw_payload["n"]
    n_valid = _is_strict_int(n) and n >= 1
    if not n_valid:
        violations.append(Violation("INVALID_ORDER", (n,)))
    elif expected_n_valid and n != expected_n:
        violations.append(Violation("N_MISMATCH", (n, expected_n)))

    edges = raw_payload["edges"]
    if not isinstance(edges, list):
        violations.append(Violation("INVALID_EDGES_TYPE", (type(edges).__name__,)))
        return _result(violations, None, payload_sha256)

    first_count, second_count = _count_edges_twice(edges)
    if first_count != second_count:
        violations.append(
            Violation("EDGE_COUNT_UNSTABLE", (first_count, second_count))
        )
        computed_m = None
    else:
        computed_m = first_count

    claimed_m = raw_payload["claimed_m"]
    if not _is_strict_int(claimed_m) or claimed_m < 0:
        violations.append(Violation("INVALID_CLAIMED_M", (claimed_m,)))
    elif computed_m is not None and claimed_m != computed_m:
        violations.append(Violation("CLAIMED_M_MISMATCH", (claimed_m, computed_m)))

    seen_edges: set[tuple[int, int]] = set()
    for index, edge in enumerate(edges):
        if not isinstance(edge, (list, tuple)) or len(edge) != 2:
            violations.append(Violation("INVALID_EDGE_FORMAT", (index,)))
            continue

        u, v = edge[0], edge[1]
        if not _is_strict_int(u) or not _is_strict_int(v):
            violations.append(Violation("INVALID_VERTEX_TYPE", (index,)))
            continue

        if u == v:
            violations.append(Violation("LOOP_DETECTED", (index, u)))
            continue

        if n_valid and (u < 0 or u >= n or v < 0 or v >= n):
            violations.append(Violation("INDEX_OUT_OF_BOUNDS", (index, u, v)))
            continue

        if (u, v) in seen_edges or (v, u) in seen_edges:
            violations.append(Violation("DUPLICATE_EDGE", (index, u, v)))
            continue

        seen_edges.add((u, v))

    if violations:
        return _result(violations, computed_m, payload_sha256)

    adjacency: list[set[int]] = [set() for _ in range(n)]
    for u, v in seen_edges:
        adjacency[u].add(v)
        adjacency[v].add(u)

    for a in range(n):
        for b in range(a + 1, n):
            if b not in adjacency[a]:
                continue
            for c in range(b + 1, n):
                if c in adjacency[a] and c in adjacency[b]:
                    violations.append(Violation("C3_DETECTED", (a, b, c)))

    for a in range(n):
        for b in range(a + 1, n):
            for c in range(b + 1, n):
                for d in range(c + 1, n):
                    for order in ((a, b, c, d), (a, b, d, c), (a, c, b, d)):
                        if _closes_cycle(adjacency, order):
                            violations.append(Violation("C4_DETECTED", order))
                            break

    return _result(violations, computed_m, payload_sha256)
