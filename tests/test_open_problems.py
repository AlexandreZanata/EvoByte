"""Unit tests for P29 open problems and verifiable certificates."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "src"))
sys.path.insert(0, str(_REPO_ROOT / "benchmarks"))

from benchmarks.open_problems import (
    PROBLEM_REGISTRY,
    check_diophantine_quintuple,
    check_erdos_straus,
    check_taxicab,
    run_open_problem_campaign,
    verify_independent_reproduction,
)


def test_problem_registry_structure() -> None:
    assert "erdos-straus" in PROBLEM_REGISTRY
    assert "taxicab" in PROBLEM_REGISTRY
    assert "diophantine-quintuple" in PROBLEM_REGISTRY

    es = PROBLEM_REGISTRY["erdos-straus"]
    assert es.certificate_type == "integer_exact_certificate"
    assert len(es.literature_citations) >= 2
    assert "rediscovery" in es.classification_rules

    dq = PROBLEM_REGISTRY["diophantine-quintuple"]
    assert dq.certificate_type == "bounded_null_certificate"
    assert "null-campaign" in dq.classification_rules


def test_erdos_straus_exact_checker() -> None:
    # Known exact solution for n=1009: 4/1009 = 1/253 + 1/85096 + 1/1974822872
    n = 1009
    x = 253
    y = 85096
    z = 1974822872

    is_valid, residual, details = check_erdos_straus(n, x, y, z)
    assert is_valid is True
    assert residual == 0
    assert details["lhs"] == details["rhs"]

    # Negative test with corrupted z
    is_bad, bad_res, _ = check_erdos_straus(n, x, y, z + 1)
    assert is_bad is False
    assert bad_res != 0

    # Non-positive input
    is_neg, _, _ = check_erdos_straus(n, -1, y, z)
    assert is_neg is False


def test_taxicab_exact_checker() -> None:
    # 1729 = 1^3 + 12^3 = 9^3 + 10^3
    is_valid, residual, details = check_taxicab(1729, 1, 12, 9, 10)
    assert is_valid is True
    assert residual == 0
    assert details["sum1"] == 1729
    assert details["sum2"] == 1729

    # Negative test
    is_bad, _, _ = check_taxicab(1729, 1, 12, 9, 11)
    assert is_bad is False


def test_diophantine_quintuple_exact_checker() -> None:
    # Fermat quadruple: {1, 3, 8, 120} has all pairwise products + 1 as squares
    # Test extending with a non-quintuple (e.g. 5)
    is_valid, _res, details = check_diophantine_quintuple([1, 3, 8, 120, 5])
    assert is_valid is False
    assert details["all_pairs_square"] is False

    # Negative test: non-distinct or non-5 elements
    is_bad1, _, _ = check_diophantine_quintuple([1, 3, 8, 120])
    assert is_bad1 is False
    is_bad2, _, _ = check_diophantine_quintuple([1, 1, 3, 8, 120])
    assert is_bad2 is False


def test_independent_reproduction_verifier() -> None:
    solution_data = {
        "n": 1009,
        "x": 253,
        "y": 85096,
        "z": 1974822872,
    }
    repro = verify_independent_reproduction("erdos-straus", solution_data)
    assert repro["status"] == "PASS"
    assert len(repro["reproduction_hash"]) == 64
    assert repro["reproduction_time_sec"] >= 0.0


def test_open_problems_smoke_campaign() -> None:
    device = "cpu"
    report = run_open_problem_campaign(
        problem_id="erdos-straus",
        device_name=device,
        output_path=None,
        smoke=True,
    )
    assert report["manifest_version"] == "1.0"
    assert report["phase"] == "p29-open-problems"
    assert report["status"] == "PASS"
    assert report["classification"] in ("rediscovery", "verified-construction")
    assert "certificate_bundle" in report
    cert = report["certificate_bundle"]
    assert cert["problem_id"] == "erdos-straus"
    assert len(cert["certificate_hash"]) == 64
    assert cert["independent_reproduction"]["status"] == "PASS"
