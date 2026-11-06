"""Confronto exaustivo dos dois verificadores independentes (F01-T05).

Enumera todos os subconjuntos de pares de vértices para n = 1..6, sem usar o
motor de busca nem a máscara de ações legais. A geração é feita apenas com
``itertools.combinations`` e bits de máscara.
"""

from __future__ import annotations

from itertools import combinations

from evobyte.validation.reference import validate as validate_reference
from evobyte.validation.runtime import validate as validate_runtime

EXPECTED_GRAPH_COUNT = 33867


def make_payload(n, edges):
    return {
        "schema_version": 1,
        "rules_id": "girth-ge-5-v1",
        "n": n,
        "edges": [list(edge) for edge in edges],
        "claimed_m": len(edges),
    }


def assert_agreement(raw_payload, expected_n, edges):
    reference_result = validate_reference(raw_payload, expected_n)
    runtime_result = validate_runtime(raw_payload, expected_n)

    context = {"n": expected_n, "edges": edges}
    assert reference_result.valid == runtime_result.valid, context
    assert reference_result.computed_m == runtime_result.computed_m, context
    assert reference_result.computed_m == len(edges), context
    assert bool(reference_result.violations) == (not reference_result.valid), context
    assert bool(runtime_result.violations) == (not runtime_result.valid), context


def test_all_labeled_graphs_up_to_six():
    total = 0

    for n in range(1, 7):
        pairs = list(combinations(range(n), 2))
        for mask in range(1 << len(pairs)):
            edges = [
                list(pair)
                for index, pair in enumerate(pairs)
                if mask & (1 << index)
            ]
            assert_agreement(make_payload(n, edges), n, edges)
            total += 1

    assert total == EXPECTED_GRAPH_COUNT
