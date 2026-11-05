"""P168 guard tests: faithful Lean 4 formal certificates."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from evobyte.lean_fidelity import audit_file, local_numeric_defs
from evobyte.verifier import is_lean_available

REPO = Path(__file__).resolve().parents[1]
LEAN_DIR = REPO / "lean_proofs"
FAITHFUL_FILE = LEAN_DIR / "Generated" / "FaithfulExtremalCertificates.lean"
REVIEWS_JSON = REPO / "docs" / "research" / "lean-fidelity-reviews.json"

REQUIRED_THEOREMS = {
    "EvoByte.Faithful.vdw_sample_8_valid",
    "EvoByte.Faithful.schur_sample_4_valid",
}


def _lean_toolchain_available() -> bool:
    return is_lean_available() and (LEAN_DIR / "lakefile.toml").exists()


needs_lean = pytest.mark.skipif(not _lean_toolchain_available(), reason="requires Lean 4 toolchain")


@needs_lean
def test_faithful_file_compiles_cleanly():
    completed = subprocess.run(
        ["lake", "build", "Generated.FaithfulExtremalCertificates"],
        capture_output=True,
        text=True,
        cwd=LEAN_DIR,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr + completed.stdout


@needs_lean
def test_faithful_root_library_builds_cleanly():
    """The module must be wired into the Generated library, not compiled in isolation."""
    root = (LEAN_DIR / "Generated.lean").read_text(encoding="utf-8")
    assert "Generated.FaithfulExtremalCertificates" in root
    completed = subprocess.run(
        ["lake", "build"],
        capture_output=True,
        text=True,
        cwd=LEAN_DIR,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr + completed.stdout


def test_faithful_file_has_zero_vacuous_theorems():
    text = FAITHFUL_FILE.read_text(encoding="utf-8")
    assert "sorry" not in text
    defs = local_numeric_defs(text)
    report = audit_file(FAITHFUL_FILE, defs)
    assert report["total"] == 2
    assert report["vacuous-constant"] == 0
    assert report["needs-review"] == 2


def test_faithful_entries_in_human_review_log():
    reviews = json.loads(REVIEWS_JSON.read_text(encoding="utf-8"))
    assert isinstance(reviews, list)
    faithful = {entry["theorem"] for entry in reviews if entry.get("verdict") == "faithful"}
    assert REQUIRED_THEOREMS <= faithful
    for entry in reviews:
        if entry["theorem"] in REQUIRED_THEOREMS:
            assert entry["reviewer"] == "human:Alexandre"
            assert set(entry) == {
                "theorem",
                "file",
                "informal_statement",
                "lean_statement",
                "mathlib_concepts",
                "reviewer",
                "verdict",
                "reviewed_at",
            }
            assert entry["file"] == "lean_proofs/Generated/FaithfulExtremalCertificates.lean"


def test_spec_example_coloring_is_mathematically_false():
    """Pin the reason the phase's example coloring could not be copied verbatim.

    The `[1, 1, 2, 1, 2, 2, 1, 2]` coloring of the P165 spec and the P168 spec has
    positions 1, 4, 7 (0-based 0, 3, 6) all equal to 1, i.e. a monochromatic 3-AP
    with difference 3. A `decide` proof over it must fail; the file below fixes
    the fixture to a certified valid coloring.
    """
    from evobyte.target_catalogue import verify_vanderwaerden_coloring

    spec_coloring = [1, 1, 2, 1, 2, 2, 1, 2]
    valid, _ = verify_vanderwaerden_coloring(spec_coloring, r=2, k=3)
    assert valid is False
