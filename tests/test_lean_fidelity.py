"""P162 guard tests: Lean statement fidelity classifier and review registry schema."""

from __future__ import annotations

import json
from pathlib import Path

from evobyte.lean_fidelity import (
    audit_directory,
    classify_statement,
    extract_statements,
    local_numeric_defs,
)

REPO = Path(__file__).resolve().parents[1]
GENERATED = REPO / "lean_proofs" / "Generated"
FIDELITY_JSON = REPO / "experiments" / "p162-lean-fidelity.json"
REVIEWS_JSON = REPO / "docs" / "research" / "lean-fidelity-reviews.json"

CONSTANT_FIXTURE = "def foo : Nat := 5\ntheorem bar : foo = 5 := rfl\n"
NUMERIC_LITERAL_FIXTURE = "theorem t : (3:ℤ)^2 - (2:ℤ)^3 > 0 := by decide\n"
BINDER_FIXTURE = "theorem t (n : ℕ) (h : n ≥ 2) : n^2 ≥ 4 := by nlinarith\n"
SCHINZEL_FIXTURE = """theorem schinzel_identity_a5_m840_r1 (k : ℚ) :
    let n : ℚ := 840 * k + 1
    let X : ℚ := 168*k + 1
    let Y : ℚ := 42*k + (168*k + 1)*(840*k + 1)/4 + 1/4
    let Z : ℚ := (168*k + 1)*(840*k + 1)^2/4 + (168*k + 1)*(840*k + 1)/4
    5 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring
"""

REVIEW_KEYS = {
    "theorem",
    "file",
    "informal_statement",
    "lean_statement",
    "mathlib_concepts",
    "reviewer",
    "verdict",
    "reviewed_at",
}


def label_of(text: str, name: str) -> str:
    """Classify one named theorem statement inside a Lean source text."""
    defs = local_numeric_defs(text)
    for theorem_name, statement in extract_statements(text):
        if theorem_name == name:
            return classify_statement(statement, defs)
    raise AssertionError(f"theorem {name} not found in fixture")


def test_constant_statement_is_vacuous():
    assert label_of(CONSTANT_FIXTURE, "bar") == "vacuous-constant"


def test_numeric_literal():
    assert label_of(NUMERIC_LITERAL_FIXTURE, "t") == "numeric-literal"


def test_binder_needs_review():
    assert label_of(BINDER_FIXTURE, "t") == "needs-review"


def test_let_statement_not_cut_early():
    statements = dict(extract_statements(SCHINZEL_FIXTURE))
    assert "let Z" in statements["schinzel_identity_a5_m840_r1"]
    assert (
        classify_statement(
            statements["schinzel_identity_a5_m840_r1"], local_numeric_defs(SCHINZEL_FIXTURE)
        )
        == "needs-review"
    )


def test_degrey_is_flagged():
    text = (GENERATED / "HadwigerNelsonColoringTheorems.lean").read_text(encoding="utf-8")
    assert label_of(text, "degrey_chromatic_lower_bound") == "vacuous-constant"


def test_directory_totals_match_recorded_json():
    recorded = json.loads(FIDELITY_JSON.read_text(encoding="utf-8"))
    assert audit_directory(GENERATED)["totals"] == recorded["totals"]


def test_reviews_registry_schema():
    reviews = json.loads(REVIEWS_JSON.read_text(encoding="utf-8"))
    assert isinstance(reviews, list)
    for entry in reviews:
        assert set(entry) == REVIEW_KEYS
        assert entry["reviewer"].startswith("human:")
        assert entry["verdict"] in {"faithful", "not-faithful"}
