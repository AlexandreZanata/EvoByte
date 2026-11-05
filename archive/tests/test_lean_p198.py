"""Tests for P198 Lean 4 Formal Verification Gate.

Strict verification constraints:
1. `Generated.StructuredDiscovery` compiles cleanly under Lake with return code 0.
2. `#print axioms` is strictly restricted to standard Lean axioms [propext, Classical.choice, Quot.sound].
3. Zero `sorry` tokens in the formal Lean modules.
4. All theorems classified as 'needs-review' with zero 'vacuous-constant'.
5. All theorems registered as 'faithful' in `docs/research/lean-fidelity-reviews.json`.
6. Hermetic shell verifier `scripts/verify_lean_p198.sh` succeeds with code 0.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess

import pytest

from evobyte.lean_fidelity import audit_file, local_numeric_defs
from evobyte.verifier import is_lean_available

REPO = Path(__file__).resolve().parents[1]
LEAN_DIR = REPO / "lean_proofs"
STRUCTURED_LEAN = LEAN_DIR / "Generated" / "StructuredDiscovery.lean"
FORMAL_LEAN = REPO / "formal" / "lean" / "EvoByte" / "StructuredDiscovery.lean"
REVIEWS_JSON = REPO / "docs" / "research" / "lean-fidelity-reviews.json"
VERIFY_SCRIPT = REPO / "scripts" / "verify_lean_p198.sh"

REQUIRED_THEOREMS = {
    "EvoByte.Structured.gottesman_8_3_3_commute",
    "EvoByte.Structured.c15_base1_strictly_sorted",
    "EvoByte.Structured.c15_base2_strictly_sorted",
    "EvoByte.Structured.c15_bases_disjoint_orbits",
    "EvoByte.Structured.sqs10_covering_valid",
}


def _lean_available() -> bool:
    return is_lean_available() and (LEAN_DIR / "lakefile.toml").exists()


needs_lean = pytest.mark.skipif(not _lean_available(), reason="requires Lean 4 toolchain")


def test_structured_discovery_files_exist_and_have_zero_sorry() -> None:
    """Both formal file paths exist and contain zero unproven 'sorry' tokens."""
    assert STRUCTURED_LEAN.is_file(), f"Missing {STRUCTURED_LEAN}"
    assert FORMAL_LEAN.is_file(), f"Missing {FORMAL_LEAN}"

    text_gen = STRUCTURED_LEAN.read_text(encoding="utf-8")
    text_formal = FORMAL_LEAN.read_text(encoding="utf-8")

    assert "sorry" not in text_gen, f"Found 'sorry' in {STRUCTURED_LEAN}"
    assert "sorry" not in text_formal, f"Found 'sorry' in {FORMAL_LEAN}"


def test_structured_discovery_theorems_have_zero_vacuous_statements() -> None:
    """All theorems express genuine mathematical properties (zero vacuous-constant)."""
    text = STRUCTURED_LEAN.read_text(encoding="utf-8")
    defs = local_numeric_defs(text)
    report = audit_file(STRUCTURED_LEAN, defs)

    assert report["total"] == 5
    assert report["vacuous-constant"] == 0
    assert report["numeric-literal"] == 0
    assert report["needs-review"] == 5


def test_all_structured_theorems_have_faithful_reviews() -> None:
    """All required P198 theorems are recorded as 'faithful' in the human review registry."""
    assert REVIEWS_JSON.is_file()
    reviews = json.loads(REVIEWS_JSON.read_text(encoding="utf-8"))
    reviewed_names = {r["theorem"] for r in reviews if r.get("verdict") == "faithful"}

    missing = REQUIRED_THEOREMS - reviewed_names
    assert not missing, f"Missing faithful reviews for: {missing}"


def test_root_generated_library_imports_structured_discovery() -> None:
    """Generated.lean library root imports Generated.StructuredDiscovery."""
    root_text = (LEAN_DIR / "Generated.lean").read_text(encoding="utf-8")
    assert "import Generated.StructuredDiscovery" in root_text


@pytest.mark.slow
@needs_lean
def test_lake_build_structured_discovery_cleanly() -> None:
    """`lake build Generated.StructuredDiscovery` compiles with code 0."""
    res = subprocess.run(
        ["lake", "build", "Generated.StructuredDiscovery"],
        capture_output=True,
        text=True,
        cwd=LEAN_DIR,
        check=False,
    )
    assert res.returncode == 0, f"Lake build failed:\n{res.stderr}\n{res.stdout}"


@pytest.mark.slow
@needs_lean
def test_hermetic_script_verify_lean_p198() -> None:
    """The standalone hermetic verification script scripts/verify_lean_p198.sh succeeds."""
    assert VERIFY_SCRIPT.is_file()
    res = subprocess.run(
        [str(VERIFY_SCRIPT)],
        capture_output=True,
        text=True,
        cwd=REPO,
        check=False,
    )
    assert res.returncode == 0, f"verify_lean_p198.sh failed:\n{res.stderr}\n{res.stdout}"
    assert "All Lean 4 formal verification gates passed cleanly!" in res.stdout
