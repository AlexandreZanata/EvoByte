"""Verificador de execução independente para grafos sem C3 e sem C4.

Usa bitsets de vizinhança e não compartilha parser, adjacência ou núcleo de
violações com o verificador de referência. Contrato em
docs/03-architecture-and-contracts.md.
"""

from __future__ import annotations

import hashlib
import json
import os
from typing import Any

from . import ValidationResult, Violation

VALIDATOR_ID = "evobyte-runtime"
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


def _lowest_bit_index(bits: int) -> int:
    return (bits & -bits).bit_length() - 1


def _detect_triangles(adjacency: list[int]) -> list[Violation]:
    violations: list[Violation] = []
    reported: set[tuple[int, ...]] = set()

    for u in range(len(adjacency)):
        for v in range(u + 1, len(adjacency)):
            if not (adjacency[u] >> v) & 1:
                continue
            common = adjacency[u] & adjacency[v]
            if common == 0:
                continue
            w = _lowest_bit_index(common)
            triangle = (u, v, w)
            key = tuple(sorted(triangle))
            if key in reported:
                continue
            reported.add(key)
            violations.append(Violation("C3_DETECTED", triangle))

    return violations


def _detect_c4(adjacency: list[int]) -> list[Violation]:
    violations: list[Violation] = []
    reported: set[tuple[int, ...]] = set()

    for u in range(len(adjacency)):
        for v in range(u + 1, len(adjacency)):
            common = adjacency[u] & adjacency[v]
            if common.bit_count() < 2:
                continue

            x = _lowest_bit_index(common)
            remaining = common & ~(1 << x)
            y = _lowest_bit_index(remaining)

            key = tuple(sorted((u, v, x, y)))
            if key in reported:
                continue
            reported.add(key)
            violations.append(Violation("C4_DETECTED", (x, u, y, v)))

    return violations


def validate(raw_payload: Any, expected_n: Any) -> ValidationResult:
    """Valida um payload bruto usando interseções de bitsets de vizinhança.

    A estrutura é conferida de forma própria; somente uma entrada estruturalmente
    válida é convertida em bitsets. Arestas não podem ter vizinho comum (C3) e
    qualquer par distinto de vértices pode ter no máximo um vizinho comum (C4).
    """
    violations: list[Violation] = []
    payload_sha256 = _canonical_sha256(raw_payload)
    computed_m: int | None = None

    expected_n_valid = _is_strict_int(expected_n) and expected_n >= 1
    if not expected_n_valid:
        violations.append(Violation("INVALID_EXPECTED_N", (expected_n,)))

    if not isinstance(raw_payload, dict):
        violations.append(
            Violation("INVALID_PAYLOAD_TYPE", (type(raw_payload).__name__,))
        )
        return _result(violations, None, payload_sha256)

    present_keys = set(raw_payload.keys())
    unknown_keys = sorted(present_keys - ALLOWED_PAYLOAD_KEYS)
    if unknown_keys:
        violations.append(Violation("UNKNOWN_FIELD", tuple(unknown_keys)))
    missing_keys = sorted(ALLOWED_PAYLOAD_KEYS - present_keys)
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

    forward_count = 0
    for _ in edges:
        forward_count += 1
    reverse_count = 0
    for _ in reversed(edges):
        reverse_count += 1

    if forward_count != reverse_count:
        violations.append(
            Violation("EDGE_COUNT_UNSTABLE", (forward_count, reverse_count))
        )
    else:
        computed_m = forward_count

    claimed_m = raw_payload["claimed_m"]
    if not _is_strict_int(claimed_m) or claimed_m < 0:
        violations.append(Violation("INVALID_CLAIMED_M", (claimed_m,)))
    elif computed_m is not None and claimed_m != computed_m:
        violations.append(Violation("CLAIMED_M_MISMATCH", (claimed_m, computed_m)))

    valid_edges: list[tuple[int, int]] = []
    seen_edges: set[tuple[int, int]] = set()

    for position, edge in enumerate(edges):
        if not isinstance(edge, (list, tuple)) or len(edge) != 2:
            violations.append(Violation("INVALID_EDGE_FORMAT", (position,)))
            continue

        u, v = edge[0], edge[1]
        if not _is_strict_int(u) or not _is_strict_int(v):
            violations.append(Violation("INVALID_VERTEX_TYPE", (position,)))
            continue

        if u == v:
            violations.append(Violation("LOOP_DETECTED", (position, u)))
            continue

        if n_valid and (u < 0 or u >= n or v < 0 or v >= n):
            violations.append(Violation("INDEX_OUT_OF_BOUNDS", (position, u, v)))
            continue

        if (u, v) in seen_edges or (v, u) in seen_edges:
            violations.append(Violation("DUPLICATE_EDGE", (position, u, v)))
            continue

        seen_edges.add((u, v))
        valid_edges.append((u, v))

    if violations:
        return _result(violations, computed_m, payload_sha256)

    adjacency = [0] * n
    for u, v in valid_edges:
        adjacency[u] |= 1 << v
        adjacency[v] |= 1 << u

    violations.extend(_detect_triangles(adjacency))
    violations.extend(_detect_c4(adjacency))

    return _result(violations, computed_m, payload_sha256)
