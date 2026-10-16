"""Unit tests for hermetic open problems database, dependent typing, and audit (P105)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from benchmarks.science_matrix import run_p105_open_problems_database_audit
from evobyte.open_problems import (
    DEFAULT_DB_PATH,
    area_to_lean,
    audit_open_problems_database,
    cert_type_to_lean,
    generate_open_problems_lean_code,
    load_open_problems,
    partition_open_problems,
    safe_id_name,
    verify_open_problems_database_soundness,
)


def test_load_open_problems_success():
    problems = load_open_problems(DEFAULT_DB_PATH)
    assert len(problems) == 100
    for p in problems:
        assert "id" in p and p["id"]
        assert "statement_sha256" in p and p["statement_sha256"]
        assert "certificate_type" in p and p["certificate_type"]
        assert "area" in p


def test_load_open_problems_nonexistent():
    with pytest.raises(FileNotFoundError):
        load_open_problems("nonexistent_path.json")


def test_partition_open_problems_determinism_and_disjointness():
    problems = load_open_problems(DEFAULT_DB_PATH)

    part1 = partition_open_problems(problems, blind_ratio=0.30, seed=42)
    part2 = partition_open_problems(problems, blind_ratio=0.30, seed=42)

    assert part1["total_count"] == 100
    assert part1["dev_count"] == 70
    assert part1["blind_count"] == 30
    assert part1["leakage_detected"] is False

    dev_set = set(part1["dev_ids"])
    blind_set = set(part1["blind_ids"])
    assert len(dev_set & blind_set) == 0
    assert len(dev_set | blind_set) == 100

    # Determinism
    assert part1["split_hash"] == part2["split_hash"]
    assert part1["dev_hash"] == part2["dev_hash"]
    assert part1["blind_hash"] == part2["blind_hash"]

    # Different seed yields different split
    part3 = partition_open_problems(problems, blind_ratio=0.30, seed=999)
    assert part1["split_hash"] != part3["split_hash"]


def test_area_and_cert_mappings():
    assert area_to_lean("number theory") == "ProblemArea.numberTheory"
    assert area_to_lean("additive combinatorics") == "ProblemArea.additiveCombinatorics"
    assert area_to_lean("primes") == "ProblemArea.primes"
    assert area_to_lean("geometry") == "ProblemArea.geometry"
    assert area_to_lean("graph theory") == "ProblemArea.graphTheory"
    assert area_to_lean("combinatorics") == "ProblemArea.combinatorics"
    assert area_to_lean("group theory") == "ProblemArea.algebra"
    assert area_to_lean("diophantine equations") == "ProblemArea.diophantine"
    assert area_to_lean("unknown topic") == "ProblemArea.other"

    assert cert_type_to_lean("proof_or_counterexample") == "CertificateType.proofOrCounterexample"
    assert (
        cert_type_to_lean("construction_or_impossibility")
        == "CertificateType.constructionOrImpossibility"
    )

    assert safe_id_name("erdos-3") == "erdos_3"
    assert safe_id_name("erdos-128-b") == "erdos_128_b"


def test_generate_open_problems_lean_code():
    problems = load_open_problems(DEFAULT_DB_PATH)
    part = partition_open_problems(problems, blind_ratio=0.30, seed=42)
    code = generate_open_problems_lean_code(part)

    assert "namespace EvoByte.OpenProblems" in code
    assert "inductive ProblemArea" in code
    assert "inductive CertificateType" in code
    assert "inductive ProblemPartition" in code
    assert "structure ProblemSignature" in code
    assert "theorem partition_disjoint" in code
    assert "theorem partition_exhaustive" in code
    assert "theorem erdos_graham_solution_3" in code
    assert "theorem catalan_solution" in code
    assert "def sig_erdos_3" in code
    assert "theorem sig_erdos_3_partition" in code
    assert "sorry" not in code


def test_audit_open_problems_database_smoke():
    res = audit_open_problems_database(verify_lake=False)
    assert res["phase"] == "P105"
    assert res["total_problems"] == 100
    assert res["dev_count"] == 70
    assert res["blind_count"] == 30
    assert res["leakage_detected"] is False
    assert res["has_sorry"] is False
    assert res["theorem_count"] >= 100


def test_verify_open_problems_database_soundness():
    good_summary = {
        "total_problems": 100,
        "dev_count": 70,
        "blind_count": 30,
        "leakage_detected": False,
        "has_sorry": False,
        "theorem_count": 108,
        "lake_passed": True,
    }
    sound, findings = verify_open_problems_database_soundness(good_summary)
    assert sound is True
    assert len(findings) == 0

    bad_summary = {
        "total_problems": 90,
        "dev_count": 60,
        "blind_count": 30,
        "leakage_detected": True,
        "has_sorry": True,
        "theorem_count": 50,
        "lake_passed": False,
        "lake_reasons": ["build error"],
    }
    sound, findings = verify_open_problems_database_soundness(bad_summary)
    assert sound is False
    assert any("INSUFFICIENT_PROBLEMS" in f for f in findings)
    assert any("DATASET_LEAKAGE" in f for f in findings)
    assert any("SORRY_DETECTED" in f for f in findings)
    assert any("INSUFFICIENT_THEOREMS" in f for f in findings)
    assert any("LAKE_BUILD_FAILED" in f for f in findings)


def test_p105_acceptance_rejects_wrong_phase(tmp_path: Path):
    cfg_p = tmp_path / "bad.json"
    cfg_p.write_text(json.dumps({"phase": "INVALID"}))
    with pytest.raises(ValueError, match="not a P105 configuration"):
        run_p105_open_problems_database_audit(cfg_p, tmp_path / "out.json")


def test_p105_acceptance_audit_smoke(tmp_path: Path):
    cfg = {
        "phase": "P105",
        "acceptance_phase": "P105",
        "min_problems": 100,
        "min_theorems": 100,
        "blind_ratio": 0.30,
        "budget_sec": 3600.0,
        "database_path": "docs/research/open-problems.json",
        "generated_path": "lean_proofs/Generated/OpenProblemSignatures.lean",
        "project_dir": "lean_proofs",
        "allow_dirty": True,
        "require_clean_tree": False,
        "verify_lake": False,
        "seed": 42,
    }
    cfg_p = tmp_path / "p105-smoke.json"
    cfg_p.write_text(json.dumps(cfg))
    out_p = tmp_path / "p105-out.json"

    report = run_p105_open_problems_database_audit(cfg_p, out_p)
    assert out_p.exists()
    assert report["phase"] == "P105"
    assert report["verdict"] == "ACCEPTED"
    assert report["total_problems"] == 100
    assert report["theorem_count"] >= 100
    assert report["has_sorry"] is False
