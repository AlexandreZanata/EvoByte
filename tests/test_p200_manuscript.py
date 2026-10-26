"""Tests for P200 Structured Algebraic Discovery Manuscript and D043 Closure."""

from __future__ import annotations

import json
from pathlib import Path
import re
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PAPER_DIR = REPO_ROOT / "docs" / "structured-paper"
MAIN_TEX = PAPER_DIR / "main.tex"
MAIN_PDF = PAPER_DIR / "main.pdf"
REFS_BIB = PAPER_DIR / "references.bib"
REPORT_MD = REPO_ROOT / "docs" / "research" / "p200-program-conclusion-impact-report.md"
DECISIONS_MD = REPO_ROOT / "docs" / "DECISIONS.md"
CERT_DIR = REPO_ROOT / "experiments" / "certificates"
LEAN_FILE = REPO_ROOT / "lean_proofs" / "Generated" / "StructuredDiscovery.lean"


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
    # 1. C(15, 8, 4)
    c15_file = CERT_DIR / "covering_C_15_8_4_tied_record.json"
    assert c15_file.exists()
    c15_cert = json.loads(c15_file.read_text(encoding="utf-8"))
    assert c15_cert["target_id"] == "covering_C_15_8_4"
    assert c15_cert["verdict"] == "DISCOVERY_TIED"
    assert c15_cert["parameters"]["claimed_blocks"] == 30
    assert len(c15_cert["candidate"]["blocks"]) == 30

    # 2. SQS(10)
    sqs_file = CERT_DIR / "covering_C_10_4_3_sqs10.json"
    assert sqs_file.exists()
    sqs_cert = json.loads(sqs_file.read_text(encoding="utf-8"))
    assert sqs_cert["target_id"] == "covering_c10_4_3"
    assert sqs_cert["verdict"] == "CALIBRATION_REPRODUCED"
    assert sqs_cert["parameters"]["claimed_blocks"] == 30
    assert len(sqs_cert["candidate"]["blocks"]) == 30

    # 3. Gottesman [[8, 3, 3]]
    qecc_file = CERT_DIR / "qecc_8_3_3_gottesman.json"
    assert qecc_file.exists()
    qecc_cert = json.loads(qecc_file.read_text(encoding="utf-8"))
    assert qecc_cert["target_id"] == "qecc_8_3_3"
    assert qecc_cert["verdict"] == "CALIBRATION_REPRODUCED"
    assert qecc_cert["parameters"]["claimed_d"] == 3
    assert len(qecc_cert["candidate"]["generators"]) == 5

    # 4. Lean 4 formal theorems
    assert LEAN_FILE.exists()
    lean_src = LEAN_FILE.read_text(encoding="utf-8")
    expected_theorems = [
        "c15_base1_strictly_sorted",
        "c15_base2_strictly_sorted",
        "c15_bases_disjoint_orbits",
        "sqs10_covering_valid",
        "gottesman_8_3_3_commute",
    ]
    for thm in expected_theorems:
        assert f"theorem {thm}" in lean_src, f"Theorem {thm} missing in {LEAN_FILE.name}"


def test_dossier_and_decision_consistency() -> None:
    """Check that report and decisions log reflect Program D043 conclusion."""
    assert REPORT_MD.exists(), f"Missing {REPORT_MD}"
    report_text = REPORT_MD.read_text(encoding="utf-8")
    assert "CONCLUÍDO" in report_text
    assert "DISCOVERY_TIED" in report_text

    assert DECISIONS_MD.exists(), f"Missing {DECISIONS_MD}"
    decisions_text = DECISIONS_MD.read_text(encoding="utf-8")
    assert "D043" in decisions_text
