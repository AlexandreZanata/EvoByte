"""Independent QECC stabilizer verifier calibration (P179)."""

from __future__ import annotations

import ast
import sys
import time
from pathlib import Path

from evobyte.qecc_verifier import (
    centralizer_contains,
    check_stabilizer,
    code_distance,
    commutes,
    parse_pauli,
    stabilizer_contains,
)

STEANE = ["IIIXXXX", "IXXIIXX", "XIXIXIX", "IIIZZZZ", "IZZIIZZ", "ZIZIZIZ"]
SHOR = [
    "ZZIIIIIII",
    "IZZIIIIII",
    "IIIZZIIII",
    "IIIIZZIII",
    "IIIIIIZZI",
    "IIIIIIIZZ",
    "XXXXXXIII",
    "IIIXXXXXX",
]


def test_steane_distance_3() -> None:
    for g in STEANE:
        assert len(g) == 7 and all(c in "IXYZ" for c in g)
    ok, payload = check_stabilizer(STEANE)
    assert ok is True
    assert payload["k"] == 1 and payload["n"] == 7
    ok, result = code_distance(STEANE)
    assert ok is True
    assert result["d"] == 3 and result["k"] == 1
    _, (lx, lz) = parse_pauli(result["logical"], 7)
    assert centralizer_contains((lx, lz), STEANE) == (True, True)
    assert stabilizer_contains((lx, lz), STEANE) == (True, False)


def test_shor_distance_3() -> None:
    ok, payload = check_stabilizer(SHOR)
    assert ok is True
    assert payload["k"] == 1 and payload["n"] == 9
    ok, result = code_distance(SHOR)
    assert ok is True
    assert result["d"] == 3 and result["k"] == 1


def test_rejects_noncommuting() -> None:
    ok, reason = check_stabilizer(["XXXXIII", "ZZZIIII", "IIIIIII"])
    assert ok is False and isinstance(reason, str)
    ok, result = code_distance(["XXXXIII", "ZZZIIII", "IIIIIII"])
    assert ok is False
    assert "d" not in (result if isinstance(result, dict) else {})
    assert commutes(([1, 0, 0], [0, 0, 0]), ([0, 0, 0], [1, 0, 0])) == (True, False)


def test_rejects_dependent_and_malformed() -> None:
    ok, _ = check_stabilizer(["XXXXIII", "XXXXIII", "IIIIIII"])
    assert ok is False  # duplicate row: rank drops
    ok, _ = check_stabilizer(["WXXXIII", "ZZZIIII", "IIIIIII"])
    assert ok is False
    ok, _ = check_stabilizer(["XXXIII", "ZZZIIII"])
    assert ok is False  # inconsistent length
    ok, _ = check_stabilizer([])
    assert ok is False
    ok, _ = check_stabilizer([(-1, "XXXXIII")])
    assert ok is False  # non-+1 phase never silently accepted
    ok, _ = parse_pauli("XX", 3)
    assert ok is False


def test_weight_bounded_finds_logical_fast() -> None:
    for gens in (STEANE, SHOR):
        t0 = time.perf_counter()
        ok, result = code_distance(gens)
        elapsed = time.perf_counter() - t0
        assert ok is True and result["d"] == 3
        assert elapsed < 0.5, elapsed


def test_module_is_stdlib_plus_numpy() -> None:
    import sysconfig

    path = Path("src/evobyte/qecc_verifier.py")
    tree = ast.parse(path.read_text(encoding="utf-8"))
    stdlib = sys.stdlib_module_names
    allowed = set(stdlib) | {"numpy"}
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported.add(node.module.split(".")[0])
    assert imported <= allowed, imported - allowed
    assert "numpy" not in imported  # exact core needs no third-party at all
    assert imported <= set(stdlib)


def test_distance_is_deterministic() -> None:
    first = [code_distance(g) for g in (STEANE, SHOR)]
    second = [code_distance(g) for g in (STEANE, SHOR)]
    assert first == second  # lexicographic sweep, no randomness anywhere
