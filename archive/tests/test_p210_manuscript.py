"""Tests for P210 Generalized Discovery Manuscript and D045 Closure."""

from __future__ import annotations

import json
from pathlib import Path
import re
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PAPER_DIR = REPO_ROOT / "docs" / "generalized-paper"
MAIN_TEX = PAPER_DIR / "main.tex"
MAIN_PDF = PAPER_DIR / "main.pdf"
REFS_BIB = PAPER_DIR / "references.bib"
REPORT_MD = REPO_ROOT / "docs" / "research" / "p210-program-conclusion-impact-report.md"
DECISIONS_MD = REPO_ROOT / "docs" / "DECISIONS.md"
CERT_DIR = REPO_ROOT / "experiments" / "certificates"
LEAN_FILE = REPO_ROOT / "lean_proofs" / "Generated" / "GeneralizedDiscovery.lean"


def test_manuscript_static_checks() -> None:
    """Check that main.tex contains no banned keywords or uncertified claims."""
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
        assert phrase not in content_lower, (
            f"Unverified discovery claim '{phrase}' found in main.tex"
        )


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


def test_manuscript_pdf_exists_and_valid() -> None:
    """Check that main.pdf exists and has plausible non-empty size (> 100 KB)."""
    assert MAIN_PDF.exists(), f"Missing compiled PDF: {MAIN_PDF}"
    size = MAIN_PDF.stat().st_size
    assert size > 100_000, f"PDF too small ({size} bytes), possible compilation failure."


def test_claims_match_empirical_certificates() -> None:
    """Check that claims in main.tex match canonical discovery certificates."""
    # 1. QECC [[14, 3, 4]]
    qecc14_file = CERT_DIR / "qecc_14_3_tied_record.json"
    assert qecc14_file.exists()
    cert14 = json.loads(qecc14_file.read_text(encoding="utf-8"))
    assert cert14["target_id"] == "qecc_14_3_noncirculant"
    assert cert14["verdict"] == "DISCOVERY_TIED"
    assert cert14["parameters"]["claimed_d"] == 4
    assert len(cert14["candidate"]["generators"]) == 11

    # 2. QECC [[16, 5, 4]]
    qecc16_file = CERT_DIR / "qecc_16_5_tied_record.json"
    assert qecc16_file.exists()
    cert16 = json.loads(qecc16_file.read_text(encoding="utf-8"))
    assert cert16["target_id"] == "qecc_16_5_noncirculant"
    assert cert16["verdict"] == "DISCOVERY_TIED"
    assert cert16["parameters"]["claimed_d"] == 4
    assert len(cert16["candidate"]["generators"]) == 11

    # 3. C(13, 5, 3) NULL_BOUND
    c13_file = CERT_DIR / "covering_C_13_5_3_null_bound.json"
    assert c13_file.exists()
    cert13 = json.loads(c13_file.read_text(encoding="utf-8"))
    assert cert13["target_id"] == "covering_C_13_5_3_affine"
    assert cert13["verdict"] == "NULL_BOUND"
    assert cert13["candidate"]["min_orbit_length"] == 39

    # 4. C(15, 10, 4) NULL_BOUND
    c15_file = CERT_DIR / "covering_C_15_10_4_null_bound.json"
    assert c15_file.exists()
    cert15 = json.loads(c15_file.read_text(encoding="utf-8"))
    assert cert15["target_id"] == "covering_C_15_10_4_affine"
    assert cert15["verdict"] == "NULL_BOUND"
    assert cert15["candidate"]["min_orbit_length"] == 15

    # 5. Lean 4 formal theorems
    assert LEAN_FILE.exists()
    lean_src = LEAN_FILE.read_text(encoding="utf-8")
    expected_theorems = [
        "steane_7_1_3_commute",
        "shor_9_1_3_commute",
        "qecc_14_3_4_commute",
        "qecc_16_5_4_commute",
        "ag23_affine_covering_valid",
        "ag23_blocks_strictly_sorted",
        "agl13_orbit_obstruction",
        "dihedral15_orbit_obstruction",
    ]
    for thm in expected_theorems:
        assert f"theorem {thm}" in lean_src, f"Theorem {thm} missing in {LEAN_FILE.name}"


def test_dossier_and_decision_consistency() -> None:
    """Check that report and decisions log reflect Program D045 conclusion."""
    assert REPORT_MD.exists(), f"Missing {REPORT_MD}"
    report_text = REPORT_MD.read_text(encoding="utf-8")
    assert "CONCLUÍDO" in report_text
    assert "DISCOVERY_TIED" in report_text

    assert DECISIONS_MD.exists(), f"Missing {DECISIONS_MD}"
    decisions_text = DECISIONS_MD.read_text(encoding="utf-8")
    assert "D046" in decisions_text
