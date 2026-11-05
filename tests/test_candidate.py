"""Testes de definição, validação e serialização canônica do candidato (F01-T02)."""

import hashlib
import json
import pytest

from evobyte.candidate import (
    CandidateValidationError,
    canonical_json_bytes,
    candidate_from_payload,
    create_candidate,
    validate_and_normalize_payload,
)


def test_valid_minimal_candidate():
    # Exemplo concreto da ficha: n=5, edges=[[1, 0]], claimed_m=1 normaliza para [[0, 1]]
    cand = create_candidate(n=5, edges=[[1, 0]])
    assert cand.n == 5
    assert cand.m == 1
    assert cand.edges == [[0, 1]]
    assert cand.rules_id == "girth-ge-5-v1"


def test_empty_graph_candidate():
    cand = create_candidate(n=8, edges=[])
    assert cand.n == 8
    assert cand.m == 0
    assert cand.edges == []
    assert len(cand.content_sha256) == 64


def test_edge_order_invariance():
    # A ordem em que as arestas são fornecidas na entrada não afeta os bytes canônicos nem o hash
    cand1 = create_candidate(n=5, edges=[[0, 1], [2, 3], [1, 4]])
    cand2 = create_candidate(n=5, edges=[[1, 4], [0, 1], [2, 3]])
    cand3 = create_candidate(n=5, edges=[[3, 2], [4, 1], [1, 0]])

    assert cand1.edges == [[0, 1], [1, 4], [2, 3]]
    assert cand2.edges == [[0, 1], [1, 4], [2, 3]]
    assert cand3.edges == [[0, 1], [1, 4], [2, 3]]

    assert cand1.canonical_bytes == cand2.canonical_bytes == cand3.canonical_bytes
    assert cand1.content_sha256 == cand2.content_sha256 == cand3.content_sha256


def test_vertex_permutation_changes_hash():
    # Permutar rótulos de vértices em geral altera a representação e o hash
    cand_a = create_candidate(n=5, edges=[[0, 1]])
    cand_b = create_candidate(n=5, edges=[[0, 2]])
    assert cand_a.content_sha256 != cand_b.content_sha256


def test_canonical_json_exact_bytes():
    payload = {
        "claimed_m": 1,
        "edges": [[0, 1]],
        "n": 5,
        "rules_id": "girth-ge-5-v1",
        "schema_version": 1,
    }
    raw_bytes = canonical_json_bytes(payload)
    # Esperado: chaves em ordem alfabética, sem espaços após : e ,
    expected = b'{"claimed_m":1,"edges":[[0,1]],"n":5,"rules_id":"girth-ge-5-v1","schema_version":1}'
    assert raw_bytes == expected
    assert hashlib.sha256(expected).hexdigest() == hashlib.sha256(raw_bytes).hexdigest()


def test_rejection_of_self_loops():
    with pytest.raises(CandidateValidationError) as exc:
        create_candidate(n=5, edges=[[2, 2]])
    assert exc.value.code == "LOOP_DETECTED"


def test_rejection_of_exact_duplicates():
    raw = {
        "schema_version": 1,
        "rules_id": "girth-ge-5-v1",
        "n": 5,
        "edges": [[0, 1], [0, 1]],
        "claimed_m": 2,
    }
    with pytest.raises(CandidateValidationError) as exc:
        validate_and_normalize_payload(raw)
    assert exc.value.code == "DUPLICATE_EDGE"


def test_rejection_of_reversed_duplicates():
    # [0, 1] e [1, 0] juntos devem ser rejeitados, não corrigidos com set
    raw = {
        "schema_version": 1,
        "rules_id": "girth-ge-5-v1",
        "n": 5,
        "edges": [[0, 1], [1, 0]],
        "claimed_m": 2,
    }
    with pytest.raises(CandidateValidationError) as exc:
        validate_and_normalize_payload(raw)
    assert exc.value.code == "DUPLICATE_EDGE"


def test_rejection_of_boolean_types():
    # bool em n
    raw = {
        "schema_version": 1,
        "rules_id": "girth-ge-5-v1",
        "n": True,
        "edges": [],
        "claimed_m": 0,
    }
    with pytest.raises(CandidateValidationError) as exc:
        validate_and_normalize_payload(raw)
    assert exc.value.code == "INVALID_ORDER"

    # bool em claimed_m
    raw["n"] = 5
    raw["claimed_m"] = False
    with pytest.raises(CandidateValidationError) as exc:
        validate_and_normalize_payload(raw)
    assert exc.value.code == "INVALID_CLAIMED_M"

    # bool em vértice de aresta
    raw["claimed_m"] = 1
    raw["edges"] = [[True, 2]]
    with pytest.raises(CandidateValidationError) as exc:
        validate_and_normalize_payload(raw)
    assert exc.value.code == "INVALID_VERTEX_TYPE"


def test_rejection_of_float_types():
    raw = {
        "schema_version": 1,
        "rules_id": "girth-ge-5-v1",
        "n": 5.0,
        "edges": [],
        "claimed_m": 0,
    }
    with pytest.raises(CandidateValidationError) as exc:
        validate_and_normalize_payload(raw)
    assert exc.value.code == "INVALID_ORDER"

    raw["n"] = 5
    raw["claimed_m"] = 1
    raw["edges"] = [[0, 1.5]]
    with pytest.raises(CandidateValidationError) as exc:
        validate_and_normalize_payload(raw)
    assert exc.value.code == "INVALID_VERTEX_TYPE"


def test_rejection_of_out_of_bounds_indices():
    # Vértice < 0
    raw = {
        "schema_version": 1,
        "rules_id": "girth-ge-5-v1",
        "n": 5,
        "edges": [[-1, 2]],
        "claimed_m": 1,
    }
    with pytest.raises(CandidateValidationError) as exc:
        validate_and_normalize_payload(raw)
    assert exc.value.code == "INDEX_OUT_OF_BOUNDS"

    # Vértice >= n
    raw["edges"] = [[0, 5]]
    with pytest.raises(CandidateValidationError) as exc:
        validate_and_normalize_payload(raw)
    assert exc.value.code == "INDEX_OUT_OF_BOUNDS"


def test_rejection_of_claimed_m_mismatch():
    raw = {
        "schema_version": 1,
        "rules_id": "girth-ge-5-v1",
        "n": 5,
        "edges": [[0, 1]],
        "claimed_m": 2,  # divergente de len(edges)
    }
    with pytest.raises(CandidateValidationError) as exc:
        validate_and_normalize_payload(raw)
    assert exc.value.code == "CLAIMED_M_MISMATCH"


def test_rejection_of_malformed_edge_structures():
    raw = {
        "schema_version": 1,
        "rules_id": "girth-ge-5-v1",
        "n": 5,
        "edges": [[0]],  # aresta unitária
        "claimed_m": 1,
    }
    with pytest.raises(CandidateValidationError) as exc:
        validate_and_normalize_payload(raw)
    assert exc.value.code == "INVALID_EDGE_FORMAT"

    raw["edges"] = [[0, 1, 2]]  # tripla
    with pytest.raises(CandidateValidationError) as exc:
        validate_and_normalize_payload(raw)
    assert exc.value.code == "INVALID_EDGE_FORMAT"


def test_rejection_of_unknown_fields():
    raw = {
        "schema_version": 1,
        "rules_id": "girth-ge-5-v1",
        "n": 5,
        "edges": [],
        "claimed_m": 0,
        "extra_field": "invalido",
    }
    with pytest.raises(CandidateValidationError) as exc:
        validate_and_normalize_payload(raw)
    assert exc.value.code == "UNKNOWN_FIELD"


def test_rejection_of_missing_fields():
    raw = {
        "schema_version": 1,
        "rules_id": "girth-ge-5-v1",
        "n": 5,
        "edges": [],
    }
    with pytest.raises(CandidateValidationError) as exc:
        validate_and_normalize_payload(raw)
    assert exc.value.code == "MISSING_FIELD"


def test_candidate_envelope():
    cand = create_candidate(n=6, edges=[[2, 0], [1, 3]], run_id="run-test-01")
    envelope = cand.to_envelope()
    assert envelope["run_id"] == "run-test-01"
    assert envelope["payload"] == cand.payload
    assert envelope["content_sha256"] == cand.content_sha256


def test_does_not_check_cycles():
    # O módulo candidate lida APENAS com estrutura de dados e integridade de formato.
    # Grafos contendo C3 ou C4 NÃO devem ser rejeitados nesta camada.
    triangle = create_candidate(n=5, edges=[[0, 1], [1, 2], [2, 0]])
    assert triangle.m == 3
    assert triangle.edges == [[0, 1], [0, 2], [1, 2]]
