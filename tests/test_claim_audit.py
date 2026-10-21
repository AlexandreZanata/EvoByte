"""P161 guard tests: integrality of unit-fraction identities and retraction banners."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from evobyte.claim_audit import (
    audit_schinzel_text,
    evaluate_expr,
    integral_k_count,
    parse_schinzel_identities,
)

REPO = Path(__file__).resolve().parents[1]
LEAN_SCHINZEL = REPO / "lean_proofs" / "Generated" / "SchinzelHighModuliTheorems.lean"
BASELINES_JSON = REPO / "experiments" / "p155-baselines" / "summary_baselines.json"
MANUSCRIPT = REPO / "docs" / "paper" / "main.tex"

# Snapshot of the measured P155 baseline summary. The raw artifact lives under
# `experiments/p155-baselines/`, which is git-ignored (large artifacts are never
# committed), so the guard keeps a committed copy of the numbers it checks the
# manuscript against. When the raw artifact is present locally, the two must agree.
P155_BASELINE_SNAPSHOT = {
    "budgets_sec": [0.4, 0.8],
    "comparison": {
        "Classical-SR": {
            "completed_runs": 20,
            "success_rate": 1.0,
            "mean_hidden_mse": 3.9130647490056724e-13,
        },
        "EvoByte": {
            "completed_runs": 20,
            "success_rate": 0.8,
            "mean_hidden_mse": 0.9786504719908017,
        },
        "PySR-Adapter": {
            "completed_runs": 0,
            "success_rate": 0.0,
        },
    },
}

VALID_FIXTURE = """theorem schinzel_identity_a4_m3_r2 (k : ℚ) :
    let n : ℚ := 3*k + 2
    let X : ℚ := 3*k + 2
    let Y : ℚ := k + 1
    let Z : ℚ := (3*k + 2)*(k + 1)
"""

RATIONAL_ONLY_FIXTURE = """theorem schinzel_identity_a5_m840_r1 (k : ℚ) :
    let n : ℚ := 840 * k + 1
    let X : ℚ := 168*k + 1
    let Y : ℚ := 42*k + (168*k + 1)*(840*k + 1)/4 + 1/4
    let Z : ℚ := (168*k + 1)*(840*k + 1)^2/4 + (168*k + 1)*(840*k + 1)/4
"""

FALSE_FIXTURE = """theorem schinzel_identity_a4_m3_r2 (k : ℚ) :
    let n : ℚ := 3*k + 2
    let X : ℚ := 3*k + 2
    let Y : ℚ := k + 1
    let Z : ℚ := k + 7
"""


def test_valid_identity_is_integral():
    identities = parse_schinzel_identities(VALID_FIXTURE)
    assert len(identities) == 1
    assert integral_k_count(identities[0], range(50)) == 50


def test_rational_only_identity_is_rejected():
    identities = parse_schinzel_identities(RATIONAL_ONLY_FIXTURE)
    assert len(identities) == 1
    assert integral_k_count(identities[0], range(50)) == 0


def test_unsafe_expression_raises():
    with pytest.raises(ValueError):
        evaluate_expr("__import__('os')", 1)


def test_false_identity_raises():
    identities = parse_schinzel_identities(FALSE_FIXTURE)
    assert len(identities) == 1
    with pytest.raises(ValueError):
        integral_k_count(identities[0], range(50))


def test_p150_schinzel_regression():
    summary = audit_schinzel_text(LEAN_SCHINZEL.read_text(encoding="utf-8"), k_max=50)
    assert summary["identities"] == 58
    assert summary["integral_for_all_k"] == 9
    assert summary["integral_for_no_k"] == 49


def load_baseline_summary() -> dict:
    """Return the measured P155 summary, falling back to the committed snapshot."""
    if not BASELINES_JSON.exists():
        return P155_BASELINE_SNAPSHOT
    live = json.loads(BASELINES_JSON.read_text(encoding="utf-8"))
    assert live["budgets_sec"] == P155_BASELINE_SNAPSHOT["budgets_sec"]
    for method, expected in P155_BASELINE_SNAPSHOT["comparison"].items():
        measured = live["comparison"][method]
        for key, value in expected.items():
            assert measured[key] == value, f"P155 snapshot drift on {method}.{key}"
    return live


def test_manuscript_abstract_matches_baseline_data():
    baselines = load_baseline_summary()
    tex = MANUSCRIPT.read_text(encoding="utf-8")
    match = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", tex, re.S)
    assert match is not None, "manuscript has no abstract environment"
    abstract = match.group(1)

    if baselines["comparison"]["PySR-Adapter"]["completed_runs"] == 0:
        for hit in re.finditer(r"PySR", abstract):
            window = abstract[max(0, hit.start() - 120) : hit.end() + 120]
            assert "not executed" in window, (
                "PySR mentioned without 'not executed' in the abstract: " + window
            )

    if max(baselines["budgets_sec"]) < 10:
        assert "1\\,h" not in abstract
        assert "10\\,s" not in abstract

    comparison = baselines["comparison"]
    if comparison["Classical-SR"]["success_rate"] > comparison["EvoByte"]["success_rate"]:
        assert "not supported" in abstract, (
            "the honest baseline beats EvoByte but the abstract does not report it"
        )


def test_retraction_banners_present():
    reports = [
        REPO / "docs" / "research" / "p150-novelty-audit-report.md",
        REPO / "docs" / "research" / "p158-h1-verdict-report.md",
        REPO / "docs" / "research" / "p144-discrepancy-covering-dossier.md",
        REPO / "docs" / "research" / "p152-constructive-algebraic-dossier.md",
    ]
    for report in reports:
        head = report.read_text(encoding="utf-8")[:400]
        assert "RETRATADO (P161" in head or "REVISADO (P161" in head, (
            f"missing retraction banner in {report.name}"
        )
