"""P167 guard tests: standalone certificate verifier and exporter."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

from evobyte.certificate_exporter import (
    Certificate,
    export_certificate,
    load_certificate,
    verify_with_oracle,
    write_certificate,
)

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "verify_certificate_standalone.py"
SAMPLE = REPO / "dist" / "external-validation" / "sample_certificate.json"

VALID_COLORING = [1, 1, 2, 2, 1, 1, 2, 3, 2, 3, 3, 1, 3, 1, 1, 2, 1, 2, 2, 3, 1, 3, 3, 2, 3, 2]


def _load_standalone():
    spec = importlib.util.spec_from_file_location("verify_certificate_standalone", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_standalone_verifier_on_valid_vdw():
    standalone = _load_standalone()
    valid, message = standalone.verify_vdw_pure(VALID_COLORING, r=3, k=3)
    assert valid is True
    assert message.startswith("VERIFIED")


def test_standalone_verifier_on_corrupted_vdw():
    standalone = _load_standalone()
    corrupted = list(VALID_COLORING)
    corrupted[0] = corrupted[3] = corrupted[6]  # positions 1, 4 and 7 become monochromatic
    valid, message = standalone.verify_vdw_pure(corrupted, r=3, k=3)
    assert valid is False
    assert "monochromatic AP" in message


def test_standalone_script_cli_execution(tmp_path):
    certificate = export_certificate(
        candidate=VALID_COLORING,
        target_id="vanderwaerden_w3_3",
        certificate_type="vanderwaerden",
        parameters={"r": 3, "k": 3},
        reference_literature="Chvatal (1970); known exact value W(3,3)=27",
        reproduction_seed=707,
    )
    path = tmp_path / "certificate.json"
    write_certificate(path, certificate)

    completed = subprocess.run(
        [sys.executable, str(SCRIPT), str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert "SUCCESS" in completed.stdout

    corrupted_path = tmp_path / "corrupted.json"
    document = load_certificate(path)
    document["coloring"][0] = document["coloring"][3]
    corrupted_path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    rejected = subprocess.run(
        [sys.executable, str(SCRIPT), str(corrupted_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert rejected.returncode == 1
    assert "FAILED" in rejected.stderr


def test_sample_certificate_verifies_with_both_implementations():
    standalone = _load_standalone()
    document = load_certificate(SAMPLE)
    assert document["certificate_type"] in {"vanderwaerden", "schur"}
    if document["certificate_type"] == "vanderwaerden":
        valid, _ = standalone.verify_vdw_pure(document["coloring"], document["r"], document["k"])
    else:
        valid, _ = standalone.verify_schur_pure(document["partition"], document["k"])
    assert valid is True

    certificate = Certificate(
        target_id=document["target_id"],
        certificate_type=document["certificate_type"],
        candidate=tuple(
            document["coloring"]
            if document["certificate_type"] == "vanderwaerden"
            else document["partition"]
        ),
        parameters=(
            {"r": document["r"], "k": document["k"]}
            if document["certificate_type"] == "vanderwaerden"
            else {"k": document["k"]}
        ),
        reference_literature=document["reference_literature"],
        reproduction_seed=document["reproduction_seed"],
    )
    assert certificate.sha256_checksum() == document["sha256_checksum"]
    ok, message = verify_with_oracle(certificate)
    assert ok is True, message


def test_exporter_rejects_invalid_candidate():
    corrupted = list(VALID_COLORING)
    corrupted[0] = corrupted[3] = corrupted[6]
    with pytest.raises(ValueError):
        export_certificate(
            candidate=corrupted,
            target_id="vanderwaerden_w3_3",
            certificate_type="vanderwaerden",
            parameters={"r": 3, "k": 3},
            reference_literature="Chvatal (1970); known exact value W(3,3)=27",
            reproduction_seed=707,
        )


def test_standalone_script_imports_only_stdlib():
    """The autonomous verifier must not import anything outside the standard library."""
    import ast

    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert imported <= {"hashlib", "json", "sys", "__future__"}, imported
