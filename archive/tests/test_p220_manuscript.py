"""Tests for P220 Bivariate Discovery Manuscript and D048 Closure."""

from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PAPER_DIR = REPO_ROOT / "docs" / "bivariate-paper"
MAIN_TEX = PAPER_DIR / "main.tex"
MAIN_PDF = PAPER_DIR / "main.pdf"
REFS_BIB = PAPER_DIR / "references.bib"
LEDGER_MD = REPO_ROOT / "docs" / "research" / "claims-ledger-d047.md"
REPORT_MD = REPO_ROOT / "docs" / "research" / "p220-program-conclusion-impact-report.md"
DECISIONS_MD = REPO_ROOT / "docs" / "DECISIONS.md"
CERT_DIR_V4 = REPO_ROOT / "experiments" / "certificates" / "v4"
VERIFIER_SCRIPT = REPO_ROOT / "scripts" / "verify_bivariate_certificate.py"


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

    # C4 mandatory banned strings in main.tex
    c4_banned_strings = [
        "DISCOVERY_TIED",
        "definitive",
        "definitively",
        "unconditional",
        "zero unproven gaps",
        "primary scientific contributions",
        "successfully demonstrated",
    ]
    for banned_str in c4_banned_strings:
        assert banned_str.lower() not in content_lower, (
            f"C4 banned string '{banned_str}' found in {MAIN_TEX.name}"
        )


def test_claims_ledger_structure() -> None:
    """Check that claims-ledger-d047.md exists and contains mandatory classes."""
    assert LEDGER_MD.exists(), f"Missing {LEDGER_MD}"
    ledger_text = LEDGER_MD.read_text(encoding="utf-8")

    mandatory_classes = [
        "RECONSTRUCAO_VERIFICADA",
        "CONHECIDO_TRIVIAL",
        "COMPUTACIONAL_FRACA",
        "ESCOPO_LIMITADO",
    ]
    for cls_name in mandatory_classes:
        assert cls_name in ledger_text, (
            f"Mandatory class '{cls_name}' missing from {LEDGER_MD.name}"
        )


def test_decisions_d048_verdict() -> None:
    """Check that DECISIONS.md contains D048 with exact verdict text."""
    assert DECISIONS_MD.exists(), f"Missing {DECISIONS_MD}"
    decisions_text = DECISIONS_MD.read_text(encoding="utf-8")

    assert "D048" in decisions_text
    expected_exact_verdict = (
        "RESULTADO NULO HONESTO: nenhuma descoberta; reconstrução verificada de parâmetros já conhecidos "
        "([[20, 2, 6]], [[16, 2, 4]]), fato conhecido reformulado (paridade de k) e cotas computacionais fracas; "
        "limites delimitados em docs/research/claims-ledger-d047.md e docs/bivariate-paper/main.pdf"
    )
    assert expected_exact_verdict in decisions_text, (
        f"D048 exact verdict text missing or mismatch in {DECISIONS_MD.name}"
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


def test_v4_certificates_and_standalone_verifier() -> None:
    """Check that v4 certificates exist and standalone verifier passes offline with python3 -S."""
    assert CERT_DIR_V4.exists(), f"Missing {CERT_DIR_V4}"
    cert_files = list(CERT_DIR_V4.glob("*.json"))
    assert len(cert_files) >= 5, f"Expected at least 5 v4 certificates, found {len(cert_files)}"

    assert VERIFIER_SCRIPT.exists(), f"Missing {VERIFIER_SCRIPT}"
    for cert in cert_files:
        cmd = [sys.executable, "-S", str(VERIFIER_SCRIPT), str(cert)]
        res = subprocess.run(cmd, capture_output=True, text=True)
        assert res.returncode == 0, f"Verifier failed for {cert.name}: {res.stderr}\n{res.stdout}"


def test_dossier_and_impact_report_consistency() -> None:
    """Check that report reflects Program D047 conclusion."""
    assert REPORT_MD.exists(), f"Missing {REPORT_MD}"
    report_text = REPORT_MD.read_text(encoding="utf-8")
    assert "CONCLUÍDO" in report_text
    assert "RESULTADO NULO HONESTO" in report_text
    assert "claims-ledger-d047.md" in report_text
