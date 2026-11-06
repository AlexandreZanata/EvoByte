"""Testes do verificador de execução por bitsets (F01-T04)."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import subprocess
import sys

import pytest

from evobyte.validation import ValidationResult
from evobyte.validation.runtime import VALIDATOR_ID, VALIDATOR_VERSION, validate


def make_payload(n, edges, claimed_m=None):
    return {
        "schema_version": 1,
        "rules_id": "girth-ge-5-v1",
        "n": n,
        "edges": [list(edge) for edge in edges],
        "claimed_m": len(edges) if claimed_m is None else claimed_m,
    }


def override_payload(n, **overrides):
    payload = {
        "schema_version": 1,
        "rules_id": "girth-ge-5-v1",
        "n": n,
        "edges": [],
        "claimed_m": 0,
    }
    payload.update(overrides)
    return payload


def codes(result):
    return {violation.code for violation in result.violations}


def assert_cycle_witness(result, payload, code, expected_length):
    violation = next(item for item in result.violations if item.code == code)
    witness = violation.witness
    assert witness is not None
    assert len(witness) == expected_length
    assert len(set(witness)) == expected_length

    edges = {frozenset(edge) for edge in payload["edges"]}
    for index, vertex in enumerate(witness):
        neighbor = witness[(index + 1) % expected_length]
        assert frozenset((vertex, neighbor)) in edges


def test_empty_graph_is_valid():
    result = validate(make_payload(8, []), 8)
    assert isinstance(result, ValidationResult)
    assert result.valid is True
    assert result.computed_m == 0
    assert result.violations == ()
    assert result.validator_id == VALIDATOR_ID
    assert result.validator_version == VALIDATOR_VERSION
    assert isinstance(result.payload_sha256, str)
    assert len(result.payload_sha256) == 64


def test_single_vertex_empty_graph_is_valid():
    result = validate(make_payload(1, []), 1)
    assert result.valid is True
    assert result.computed_m == 0


def test_tree_is_valid():
    payload = make_payload(6, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5]])
    result = validate(payload, 6)
    assert result.valid is True
    assert result.computed_m == 5


def test_c5_is_valid():
    payload = make_payload(5, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]])
    result = validate(payload, 5)
    assert result.valid is True
    assert result.computed_m == 5


def test_c6_is_valid():
    payload = make_payload(6, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]])
    result = validate(payload, 6)
    assert result.valid is True
    assert result.computed_m == 6


def test_c3_is_rejected_with_witness():
    payload = make_payload(5, [[0, 1], [1, 2], [2, 0]])
    result = validate(payload, 5)
    assert result.valid is False
    assert result.computed_m == 3
    assert codes(result) == {"C3_DETECTED"}
    assert_cycle_witness(result, payload, "C3_DETECTED", 3)


def test_c4_is_rejected_with_witness():
    payload = make_payload(5, [[0, 1], [1, 2], [2, 3], [3, 0]])
    result = validate(payload, 5)
    assert result.valid is False
    assert codes(result) == {"C4_DETECTED"}
    assert_cycle_witness(result, payload, "C4_DETECTED", 4)


def test_c4_between_non_adjacent_vertices_is_detected():
    payload = make_payload(4, [[0, 2], [0, 3], [1, 2], [1, 3]])
    result = validate(payload, 4)
    assert result.valid is False
    assert codes(result) == {"C4_DETECTED"}
    assert_cycle_witness(result, payload, "C4_DETECTED", 4)


def test_chorded_c4_is_rejected():
    payload = make_payload(5, [[0, 1], [1, 2], [2, 3], [3, 0], [0, 2]])
    result = validate(payload, 5)
    assert result.valid is False
    assert "C4_DETECTED" in codes(result)
    assert "C3_DETECTED" in codes(result)
    assert_cycle_witness(result, payload, "C4_DETECTED", 4)


def test_k4_is_rejected():
    payload = make_payload(4, [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]])
    result = validate(payload, 4)
    assert result.valid is False
    assert "C3_DETECTED" in codes(result)
    assert "C4_DETECTED" in codes(result)
    assert_cycle_witness(result, payload, "C3_DETECTED", 3)
    assert_cycle_witness(result, payload, "C4_DETECTED", 4)


def test_triangle_with_single_common_neighbor_is_not_reported_as_c4():
    payload = make_payload(5, [[0, 1], [1, 2], [2, 0]])
    result = validate(payload, 5)
    assert codes(result) == {"C3_DETECTED"}


def test_n_mismatch_is_rejected():
    payload = make_payload(5, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]])
    result = validate(payload, 6)
    assert result.valid is False
    assert result.computed_m == 5
    assert codes(result) == {"N_MISMATCH"}


MALFORMED_CASES = [
    ("payload_not_dict", lambda: ("nao-e-dict", 5), "INVALID_PAYLOAD_TYPE"),
    (
        "unknown_field",
        lambda: (override_payload(5, extra="proibido"), 5),
        "UNKNOWN_FIELD",
    ),
    (
        "missing_field",
        lambda: (
            {
                key: value
                for key, value in make_payload(5, []).items()
                if key != "claimed_m"
            },
            5,
        ),
        "MISSING_FIELD",
    ),
    (
        "schema_version",
        lambda: (override_payload(5, schema_version=2), 5),
        "INVALID_SCHEMA_VERSION",
    ),
    (
        "rules_id",
        lambda: (override_payload(5, rules_id="outra-regra"), 5),
        "UNEXPECTED_RULES_ID",
    ),
    ("order_bool", lambda: (make_payload(True, []), 5), "INVALID_ORDER"),
    ("order_float", lambda: (make_payload(5.0, []), 5), "INVALID_ORDER"),
    (
        "edges_type",
        lambda: (override_payload(5, edges={"0,1"}, claimed_m=0), 5),
        "INVALID_EDGES_TYPE",
    ),
    (
        "claimed_m_bool",
        lambda: (override_payload(5, claimed_m=True), 5),
        "INVALID_CLAIMED_M",
    ),
    (
        "claimed_m_mismatch",
        lambda: (make_payload(5, [[0, 1]], claimed_m=2), 5),
        "CLAIMED_M_MISMATCH",
    ),
    (
        "edge_format",
        lambda: (override_payload(5, edges=[[0]], claimed_m=1), 5),
        "INVALID_EDGE_FORMAT",
    ),
    (
        "vertex_bool",
        lambda: (override_payload(5, edges=[[True, 2]], claimed_m=1), 5),
        "INVALID_VERTEX_TYPE",
    ),
    (
        "vertex_float",
        lambda: (override_payload(5, edges=[[0, 1.5]], claimed_m=1), 5),
        "INVALID_VERTEX_TYPE",
    ),
    (
        "index_negative",
        lambda: (make_payload(5, [[-1, 2]]), 5),
        "INDEX_OUT_OF_BOUNDS",
    ),
    (
        "index_high",
        lambda: (make_payload(5, [[0, 5]]), 5),
        "INDEX_OUT_OF_BOUNDS",
    ),
    ("loop", lambda: (make_payload(5, [[2, 2]]), 5), "LOOP_DETECTED"),
    (
        "duplicate",
        lambda: (make_payload(5, [[0, 1], [0, 1]]), 5),
        "DUPLICATE_EDGE",
    ),
    (
        "reversed_duplicate",
        lambda: (make_payload(5, [[0, 1], [1, 0]]), 5),
        "DUPLICATE_EDGE",
    ),
]


@pytest.mark.parametrize(
    "case",
    [case for case in MALFORMED_CASES],
    ids=[case[0] for case in MALFORMED_CASES],
)
def test_structural_rejections(case):
    _, build, expected_code = case
    raw_payload, expected_n = build()
    result = validate(raw_payload, expected_n)
    assert result.valid is False
    assert expected_code in codes(result)


def test_invalid_expected_n_is_rejected():
    payload = make_payload(5, [])
    for expected_n in (True, 0, -1, 5.0, None):
        result = validate(payload, expected_n)
        assert result.valid is False
        assert "INVALID_EXPECTED_N" in codes(result)


def test_computed_m_remains_readable_for_bad_edges():
    payload = override_payload(5, edges=[[0, "x"], [1, 2]], claimed_m=2)
    result = validate(payload, 5)
    assert result.valid is False
    assert result.computed_m == 2


def test_computed_m_is_null_when_edges_are_unreadable():
    payload = override_payload(5, edges="nao-e-lista", claimed_m=0)
    result = validate(payload, 5)
    assert result.valid is False
    assert result.computed_m is None


def test_claimed_m_is_not_trusted():
    payload = make_payload(5, [[0, 1], [1, 2], [2, 3], [3, 0]])
    result = validate(payload, 5)
    assert result.valid is False
    assert result.computed_m == 4
    assert "C4_DETECTED" in codes(result)


def test_payload_sha256_matches_canonical_bytes():
    payload = make_payload(5, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]])
    result = validate(payload, 5)
    expected = (
        b'{"claimed_m":5,"edges":[[0,1],[1,2],[2,3],[3,4],[4,0]],'
        b'"n":5,"rules_id":"girth-ge-5-v1","schema_version":1}'
    )
    assert result.payload_sha256 == hashlib.sha256(expected).hexdigest()


def test_payload_sha256_is_null_when_not_canonicalizable():
    payload = override_payload(5, edges=[{1, 2}], claimed_m=1)
    result = validate(payload, 5)
    assert result.valid is False
    assert result.payload_sha256 is None


def test_code_commit_comes_from_environment(monkeypatch):
    monkeypatch.setenv("EVOBYTE_CODE_COMMIT", "cafebabe")
    result = validate(make_payload(5, []), 5)
    assert result.code_commit == "cafebabe"

    monkeypatch.delenv("EVOBYTE_CODE_COMMIT")
    result = validate(make_payload(5, []), 5)
    assert result.code_commit is None


def test_runtime_import_is_independent():
    root = Path(__file__).resolve().parents[1]
    script = (
        "import sys\n"
        "import evobyte.validation.runtime as runtime\n"
        "forbidden = ('numpy', 'torch', 'evobyte.candidate', "
        "'evobyte.validation.reference', 'evobyte.search.engine')\n"
        "loaded = [name for name in forbidden if name in sys.modules]\n"
        "assert not loaded, loaded\n"
        "assert runtime.VALIDATOR_ID\n"
    )
    env = dict(os.environ)
    env["PYTHONPATH"] = str(root / "src") + os.pathsep + env.get("PYTHONPATH", "")
    subprocess.run(
        [sys.executable, "-c", script],
        check=True,
        timeout=30,
        cwd=root,
        env=env,
    )
