"""Tests for P208 Lean 4 Formal Verification Gate.

Strict verification constraints:
1. `Generated.GeneralizedDiscovery` compiles cleanly under Lake with return code 0.
2. `#print axioms` is strictly restricted to standard Lean axioms [propext, Classical.choice, Quot.sound].
3. Zero `sorry` tokens in the formal Lean modules.
4. All theorems classified as 'needs-review' with zero 'vacuous-constant'.
5. All theorems registered as 'faithful' in `docs/research/lean-fidelity-reviews.json`.
6. Hermetic shell verifier `scripts/verify_lean_p208.sh` succeeds with code 0.
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
GENERALIZED_LEAN = LEAN_DIR / "Generated" / "GeneralizedDiscovery.lean"
FORMAL_LEAN = REPO / "formal" / "lean" / "EvoByte" / "GeneralizedDiscovery.lean"
REVIEWS_JSON = REPO / "docs" / "research" / "lean-fidelity-reviews.json"
VERIFY_SCRIPT = REPO / "scripts" / "verify_lean_p208.sh"

REQUIRED_THEOREMS = {
    "EvoByte.Generalized.steane_7_1_3_commute",
    "EvoByte.Generalized.shor_9_1_3_commute",
    "EvoByte.Generalized.qecc_14_3_4_commute",
    "EvoByte.Generalized.qecc_16_5_4_commute",
    "EvoByte.Generalized.ag23_affine_covering_valid",
    "EvoByte.Generalized.ag23_blocks_strictly_sorted",
    "EvoByte.Generalized.agl13_orbit_obstruction",
    "EvoByte.Generalized.dihedral15_orbit_obstruction",
}


def _lean_available() -> bool:
    return is_lean_available() and (LEAN_DIR / "lakefile.toml").exists()


needs_lean = pytest.mark.skipif(not _lean_available(), reason="requires Lean 4 toolchain")


def test_generalized_discovery_files_exist_and_have_zero_sorry() -> None:
    """Both formal file paths exist and contain zero unproven 'sorry' tokens."""
    assert GENERALIZED_LEAN.is_file(), f"Missing {GENERALIZED_LEAN}"
    assert FORMAL_LEAN.is_file(), f"Missing {FORMAL_LEAN}"

    text_gen = GENERALIZED_LEAN.read_text(encoding="utf-8")
    text_formal = FORMAL_LEAN.read_text(encoding="utf-8")

    assert "sorry" not in text_gen, f"Found 'sorry' in {GENERALIZED_LEAN}"
    assert "sorry" not in text_formal, f"Found 'sorry' in {FORMAL_LEAN}"


def test_generalized_discovery_theorems_have_zero_vacuous_statements() -> None:
    """All theorems express genuine mathematical properties (zero vacuous-constant)."""
    text = GENERALIZED_LEAN.read_text(encoding="utf-8")
    defs = local_numeric_defs(text)
    report = audit_file(GENERALIZED_LEAN, defs)

    assert report["total"] == 8
    assert report["vacuous-constant"] == 0
    assert report["numeric-literal"] == 0
    assert report["needs-review"] == 8


def test_all_generalized_theorems_have_faithful_reviews() -> None:
    """All required P208 theorems are recorded as 'faithful' in the human review registry."""
    assert REVIEWS_JSON.is_file()
    reviews = json.loads(REVIEWS_JSON.read_text(encoding="utf-8"))
    reviewed_names = {r["theorem"] for r in reviews if r.get("verdict") == "faithful"}

    missing = REQUIRED_THEOREMS - reviewed_names
    assert not missing, f"Missing faithful reviews for: {missing}"


def test_root_generated_library_imports_generalized_discovery() -> None:
    """Generated.lean library root imports Generated.GeneralizedDiscovery."""
    root_text = (LEAN_DIR / "Generated.lean").read_text(encoding="utf-8")
    assert "import Generated.GeneralizedDiscovery" in root_text


@pytest.mark.slow
@needs_lean
def test_lake_build_generalized_discovery_cleanly() -> None:
    """`lake build Generated.GeneralizedDiscovery` compiles with code 0."""
    res = subprocess.run(
        ["lake", "build", "Generated.GeneralizedDiscovery"],
        capture_output=True,
        text=True,
        cwd=LEAN_DIR,
        check=False,
    )
    assert res.returncode == 0, f"Lake build failed:\n{res.stderr}\n{res.stdout}"


@pytest.mark.slow
@needs_lean
def test_hermetic_script_verify_lean_p208() -> None:
    """The standalone hermetic verification script scripts/verify_lean_p208.sh succeeds."""
    assert VERIFY_SCRIPT.is_file()
    res = subprocess.run(
        [str(VERIFY_SCRIPT)],
        capture_output=True,
        text=True,
        cwd=REPO,
        check=False,
    )
    assert res.returncode == 0, f"verify_lean_p208.sh failed:\n{res.stderr}\n{res.stdout}"
    assert "All P208 Lean 4 formal verification gates passed cleanly!" in res.stdout
