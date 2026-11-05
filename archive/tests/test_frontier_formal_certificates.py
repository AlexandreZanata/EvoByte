"""Tests for P185 Frontier Formal Certificates in Lean 4.

Verifies:
- FrontierDiscoveryCertificates.lean compiles without errors or 'sorry'.
- Module is properly wired into the Generated library root.
- Lean fidelity classifier classifies all theorems as 'needs-review' with zero 'vacuous-constant'.
- Every certificate theorem has an explicit 'faithful' human review log entry.
- Broken fixtures are rejected by reference verifiers.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from evobyte.frontier_catalogue import (
    verify_covering_design,
    verify_weak_schur_partition,
)
from evobyte.lean_fidelity import audit_file, local_numeric_defs
from evobyte.verifier import is_lean_available

REPO = Path(__file__).resolve().parents[1]
LEAN_DIR = REPO / "lean_proofs"
FRONTIER_FILE = LEAN_DIR / "Generated" / "FrontierDiscoveryCertificates.lean"
REVIEWS_JSON = REPO / "docs" / "research" / "lean-fidelity-reviews.json"

REQUIRED_FRONTIER_THEOREMS = {
    "EvoByte.Frontier.fano_covering_valid",
    "EvoByte.Frontier.weak_schur_sample_8_valid",
    "EvoByte.Frontier.steane_generators_commute",
}


def _lean_toolchain_available() -> bool:
    return is_lean_available() and (LEAN_DIR / "lakefile.toml").exists()


needs_lean = pytest.mark.skipif(not _lean_toolchain_available(), reason="requires Lean 4 toolchain")


@pytest.mark.slow
@needs_lean
def test_frontier_file_compiles_cleanly() -> None:
    """The frontier formal certificates module must compile cleanly in Lake."""
    completed = subprocess.run(
        ["lake", "build", "Generated.FrontierDiscoveryCertificates"],
        capture_output=True,
        text=True,
        cwd=LEAN_DIR,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr + completed.stdout


@pytest.mark.slow
@needs_lean
def test_frontier_root_library_builds_cleanly() -> None:
    """The module must be wired into the Generated library, not compiled in isolation."""
    root = (LEAN_DIR / "Generated.lean").read_text(encoding="utf-8")
    assert "Generated.FrontierDiscoveryCertificates" in root
    completed = subprocess.run(
        ["lake", "build"],
        capture_output=True,
        text=True,
        cwd=LEAN_DIR,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr + completed.stdout


def test_frontier_file_has_zero_vacuous_theorems() -> None:
    """No theorem in FrontierDiscoveryCertificates may be a vacuous equality of numeric defs."""
    text = FRONTIER_FILE.read_text(encoding="utf-8")
    assert "sorry" not in text
    defs = local_numeric_defs(text)
    report = audit_file(FRONTIER_FILE, defs)
    assert report["total"] == 3
    assert report["vacuous-constant"] == 0
    assert report["numeric-literal"] == 0
    assert report["needs-review"] == 3


def test_no_sorry_anywhere_in_file() -> None:
    """Zero sorry or admit allowed anywhere in the formal file."""
    text = FRONTIER_FILE.read_text(encoding="utf-8")
    assert "sorry" not in text
    assert "admit" not in text


def test_frontier_entries_in_human_review_log() -> None:
    """Every theorem must be transcribed in lean-fidelity-reviews.json with faithful human review."""
    reviews = json.loads(REVIEWS_JSON.read_text(encoding="utf-8"))
    assert isinstance(reviews, list)
    faithful = {entry["theorem"] for entry in reviews if entry.get("verdict") == "faithful"}
    assert REQUIRED_FRONTIER_THEOREMS <= faithful

    for entry in reviews:
        if entry["theorem"] in REQUIRED_FRONTIER_THEOREMS:
            assert entry["reviewer"] == "human:Alexandre"
            assert entry["file"] == "lean_proofs/Generated/FrontierDiscoveryCertificates.lean"
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


def test_spec_broken_fixture_is_rejected() -> None:
    """Broken or corrupt configurations must be rejected by reference verifiers."""
    # Fano with missing block leaves subsets uncovered
    broken_fano = [[1, 2, 3], [1, 4, 5], [1, 6, 7], [2, 4, 6], [2, 5, 7], [3, 4, 7]]
    ok_cov, _ = verify_covering_design(broken_fano, 7, 3, 2)
    assert not ok_cov

    # Weak Schur partition with monochromatic x < y and x + y = z
    # E.g. [1, 1, 1, ...] has 1 + 2 = 3 with 1, 2, 3 all in class 1
    broken_ws = [1, 1, 1, 1, 1, 1, 1, 1]
    ok_ws, msg_ws = verify_weak_schur_partition(broken_ws, 2)
    assert not ok_ws
    assert "weak Schur violation" in msg_ws
