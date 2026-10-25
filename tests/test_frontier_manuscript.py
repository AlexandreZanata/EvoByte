"""Tests for P189 Frontier Discovery Manuscript.

Performs static integrity checks on main.tex, references.bib, and the manuscript dossier:
1. test_no_sorry_or_todo_in_manuscript: verifies no forbidden tokens (sorry, TODO, FIXME, quebramos)
2. test_cites_and_refs_resolve: ensures every citation exists in references.bib and every ref has a label
3. test_manuscript_type_matches_verdicts: confirms declared type matches empirical verdicts (honest nulls)
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PAPER_DIR = REPO_ROOT / "docs" / "frontier-paper"
MAIN_TEX = PAPER_DIR / "main.tex"
REFS_BIB = PAPER_DIR / "references.bib"
DOSSIER_MD = REPO_ROOT / "docs" / "research" / "p189-manuscript-dossier.md"


def test_no_sorry_or_todo_in_manuscript() -> None:
    """Check that main.tex contains no banned keywords or unverified claims."""
    assert MAIN_TEX.exists(), f"Missing {MAIN_TEX}"
    content = MAIN_TEX.read_text(encoding="utf-8")
    content_lower = content.lower()

    banned_keywords = ["sorry", "todo", "fixme", "quebramos"]
    for banned in banned_keywords:
        assert banned not in content_lower, f"Banned keyword '{banned}' found in main.tex"

    banned_phrases = [
        "we broke the record",
        "descobrimos novo recorde",
        "new record discovered",
        "new record found",
    ]
    for phrase in banned_phrases:
        assert phrase not in content_lower, f"Unverified discovery claim '{phrase}' found in main.tex"


def test_cites_and_refs_resolve() -> None:
    """Check that all cites resolve in references.bib and all refs have corresponding labels."""
    assert MAIN_TEX.exists(), f"Missing {MAIN_TEX}"
    assert REFS_BIB.exists(), f"Missing {REFS_BIB}"

    tex = MAIN_TEX.read_text(encoding="utf-8")
    bib = REFS_BIB.read_text(encoding="utf-8")

    # Extract all bibtex keys
    bib_keys = set(re.findall(r"@\w+\s*\{\s*([^,\s]+)\s*,", bib))

    # Extract all citations in tex
    cited_keys: set[str] = set()
    for match in re.finditer(r"\\cite[a-zA-Z*]*\{([^}]+)\}", tex):
        for key in match.group(1).split(","):
            cleaned = key.strip()
            if cleaned:
                cited_keys.add(cleaned)

    missing_cites = cited_keys - bib_keys
    assert not missing_cites, f"Missing citation keys in {REFS_BIB.name}: {sorted(missing_cites)}"

    # Extract all labels and refs in tex
    labels = set(re.findall(r"\\label\{([^}]+)\}", tex))
    refs: set[str] = set()
    for match in re.finditer(r"\\(?:ref|pageref|eqref)\{([^}]+)\}", tex):
        for key in match.group(1).split(","):
            cleaned = key.strip()
            if cleaned:
                refs.add(cleaned)

    missing_refs = refs - labels
    assert not missing_refs, f"Missing labels for refs in {MAIN_TEX.name}: {sorted(missing_refs)}"


def test_manuscript_type_matches_verdicts() -> None:
    """Check that the manuscript type declared in the dossier matches literal campaign verdicts."""
    assert DOSSIER_MD.exists(), f"Missing {DOSSIER_MD}"
    dossier_text = DOSSIER_MD.read_text(encoding="utf-8")

    # Check declared manuscript type in dossier
    assert "nulos honestos" in dossier_text, "Dossier must declare 'nulos honestos'"
    assert "human_review: pending" in dossier_text, "Dossier must record human_review: pending"

    # Load campaign results to verify no active discovery
    audit_file = REPO_ROOT / "experiments" / "p186-novelty-audit.json"
    assert audit_file.exists(), f"Missing {audit_file}"
    audit = json.loads(audit_file.read_text(encoding="utf-8"))
    confirmed_count = audit.get("summary", {}).get("confirmed", -1)
    assert confirmed_count == 0, f"Expected 0 confirmed claims in P186 audit, found {confirmed_count}"
    assert audit.get("overall_verdict") == "NO_ACTIVE_DISCOVERY_CLAIMS"

    # Check H2 verdict
    h2_file = REPO_ROOT / "experiments" / "p174-h2-results.json"
    if h2_file.exists():
        h2 = json.loads(h2_file.read_text(encoding="utf-8"))
        assert h2.get("verdict") == "H2_NOT_SUPPORTED", "H2 verdict must be H2_NOT_SUPPORTED"

    # Check that main.tex explicitly identifies as honest null results
    tex = MAIN_TEX.read_text(encoding="utf-8")
    assert "null-result" in tex.lower() or "honest null" in tex.lower(), (
        "main.tex must explicitly identify the paper as a null-result study"
    )
