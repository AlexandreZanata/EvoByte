"""Tests for external math-DB harness (GSM8K): parser, sealed splits, max-GPU smoke."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "benchmarks"))

from math_db import (
    EXPECTED_N,
    EXPECTED_SHA256,
    extract_chains,
    make_splits,
    parse_final_answer,
)


def test_parse_final_answer() -> None:
    assert parse_final_answer("blah\n#### 18") == 18.0
    assert parse_final_answer("#### -3.5") == -3.5
    assert parse_final_answer("no marker") is None


def test_extract_chains_guarded() -> None:
    chains = extract_chains("Janet sells 16 - 3 - 4 = <<16-3-4=9>>9 eggs. Makes <<9*2=18>>.")
    assert len(chains) == 2
    assert chains[0]["computed"] == 9.0
    assert chains[0]["claimed"] == 9.0
    assert chains[1]["computed"] == 18.0
    # Non-arithmetic / code injection must not evaluate.
    bad = extract_chains("<<__import__('os').system('x')=1>>")
    assert bad[0]["computed"] is None
    div0 = extract_chains("<<1/0=0>>")
    assert div0[0]["computed"] is None


def test_splits_seal_hidden() -> None:
    s = make_splits(EXPECTED_N, seed=0)
    assert len(s["train"]) == int(0.7 * EXPECTED_N)
    assert len(s["hidden"]) == EXPECTED_N - len(s["train"]) - len(s["val"])
    assert not (set(s["train"]) & set(s["hidden"]))
    assert not (set(s["val"]) & set(s["hidden"]))
    # Deterministic.
    assert make_splits(EXPECTED_N, seed=0)["hidden"] == s["hidden"]


def test_pin_constants_documented() -> None:
    assert EXPECTED_N == 1319
    assert len(EXPECTED_SHA256) == 64


def test_smoke_benchmark_max_gpu_safe() -> None:
    from math_db import RAW_PATH, run_smoke_benchmark

    if not RAW_PATH.exists():
        import pytest

        pytest.skip("gsm8k raw not downloaded (run math_db.py --download)")
    rep = run_smoke_benchmark(limit=32)
    assert rep["hidden_touched"] is False
    assert rep["n_hidden_sealed"] > 0
    assert rep["problems_per_sec"] > 0
    assert rep["chains_total"] >= 0
