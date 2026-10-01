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
    audit_historical_certificate,
    check_coordinate_bounds,
    check_diophantine_quintuple,
    check_diophantine_quintuple_independent,
    check_erdos_straus,
    check_erdos_straus_fractions,
    check_taxicab,
    check_taxicab_factorization,
    replay_and_verify_bounded_null,
    run_adversarial_rejection_suite,
    run_certificate_audit,
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


def test_dual_checkers_erdos_straus() -> None:
    # Strict solution for n=1009 within bound 10^9: (253, 85100, 944524900)
    n = 1009
    x = 253
    y = 85100
    z = 944524900

    # Checker 1: integer exact identity
    is_v1, res1, det1 = check_erdos_straus(n, x, y, z)
    assert is_v1 is True
    assert res1 == 0
    assert det1["verified_exact"] is True

    # Checker 2: rational fractions
    is_v2, diff2, det2 = check_erdos_straus_fractions(n, x, y, z)
    assert is_v2 is True
    assert diff2 == 0
    assert det2["verified_exact_fraction"] is True

    # Coordinate bounds
    in_bounds, b_info = check_coordinate_bounds(
        "erdos-straus", {"x": x, "y": y, "z": z}, max_coord=10**9
    )
    assert in_bounds is True
    assert b_info["within_bounds"] is True


def test_dual_checkers_taxicab() -> None:
    # Ta(2) = 1729 = 1^3 + 12^3 = 9^3 + 10^3
    sum_val = 1729
    a, b, c, d = 1, 12, 9, 10

    # Checker 1: sum of cubes
    is_v1, res1, _ = check_taxicab(sum_val, a, b, c, d)
    assert is_v1 is True
    assert res1 == 0

    # Checker 2: sum of cubes factorization
    is_v2, res2, det2 = check_taxicab_factorization(sum_val, a, b, c, d)
    assert is_v2 is True
    assert res2 == 0
    assert det2["verified_algebraic_identity"] is True


def test_independent_checker_diophantine_quintuple() -> None:
    # Fermat quadruple + non-square candidate e=5
    is_v, res, det = check_diophantine_quintuple_independent([1, 3, 8, 120, 5])
    assert is_v is False
    assert res != 0
    assert det["all_pairs_square"] is False

    # Domain check: 4 elements or duplicates
    is_bad1, _, _ = check_diophantine_quintuple_independent([1, 3, 8, 120])
    assert is_bad1 is False
    is_bad2, _, _ = check_diophantine_quintuple_independent([1, 1, 3, 8, 120])
    assert is_bad2 is False


def test_coordinate_bounds_reclassification() -> None:
    # Historical P29 solution for n=1009 has z=1974822872 > 10^9
    sol_historical = {"n": 1009, "x": 253, "y": 85096, "z": 1974822872}
    in_bounds, b_info = check_coordinate_bounds("erdos-straus", sol_historical, max_coord=10**9)
    assert in_bounds is False
    assert b_info["max_coordinate_value"] == 1974822872
    assert b_info["within_bounds"] is False

    # Strict reproduction check with bounds_strict=True flags bound exceedance
    repro_strict = verify_independent_reproduction(
        "erdos-straus", sol_historical, bounds_strict=True
    )
    assert repro_strict["status"] == "EXCEEDS_BOUND"
    assert repro_strict["details"]["classification"] == "exceeds_declared_coordinate_bound"

    # Historical certificate audit function test
    p29_cert_path = _REPO_ROOT / "experiments" / "p29-erdos-straus-certificate.json"
    if p29_cert_path.exists():
        audit_res = audit_historical_certificate(p29_cert_path, max_coord=10**9)
        assert audit_res is not None
        assert audit_res["reclassified_status"] == "exceeds_declared_coordinate_bound"
        assert audit_res["preserved_as_superseded_diagnostic"] is True


def test_replay_and_verify_bounded_null() -> None:
    # Bounded replay of Fermat quadruple extensions in small test window
    res = replay_and_verify_bounded_null(
        base_quadruple=[1, 3, 8, 120],
        r_start=121,
        r_end=500,
    )
    assert res["null_verified"] is True
    assert res["status"] == "exhaustive_null"
    assert res["candidates_checked"] == 380
    assert len(res["counterexamples"]) == 0


def test_adversarial_rejection_suite_open_problems() -> None:
    results = run_adversarial_rejection_suite()
    assert len(results) >= 8
    # Zero accepted false positives
    accepted_fps = [r for r in results if not r["rejected"]]
    assert len(accepted_fps) == 0
    # Every fixture must be rejected
    assert all(r["rejected"] is True for r in results)


def test_run_certificate_audit_manifest(tmp_path: Path) -> None:
    out_p = tmp_path / "p31-certificates.json"
    audit = run_certificate_audit(
        bounds_strict=True,
        output_path=out_p,
    )
    assert out_p.exists()
    assert audit["phase"] == "p31-verifier-certificates"
    assert audit["status"] == "PASS"
    assert audit["audit_summary"]["accepted_false_positives"] == 0
    assert audit["audit_summary"]["soundness_gate_passed"] is True
    assert "strict_certificates" in audit
    assert "diophantine-quintuple" in audit["strict_certificates"]
    assert "erdos-straus" in audit["strict_certificates"]
    assert "taxicab" in audit["strict_certificates"]


def test_p39_nomination_file_valid() -> None:
    import json as _json

    nom = _json.loads((_REPO_ROOT / "experiments" / "p39-nomination.json").read_text())
    assert nom["problem_id"] == "erdos-straus"
    assert nom["status"] == "preregistered"
    assert nom["instances"] == [1009, 10007, 100003]
    assert nom["bounds"]["declared_bound"] == 10**9
    assert len(nom["checkers"]) == 2
    assert "novelty_plan" in nom and "coverage" in nom


def test_p39_certified_campaign_smoke(tmp_path: Path) -> None:
    from benchmarks.open_problems import P39_ALLOWED_CLASSIFICATIONS, run_certified_campaign

    out_p = tmp_path / "p39-science.json"
    report = run_certified_campaign(
        problem_id="erdos-straus",
        freeze_manifest=_REPO_ROOT / "experiments" / "p38-confirmation.json",
        nomination_path=_REPO_ROOT / "experiments" / "p39-nomination.json",
        output_path=out_p,
        device_name="cpu",
        smoke=True,
        checkpoint_path=tmp_path / "p39-checkpoint.json",
    )
    assert out_p.exists()
    assert report["phase"] == "p39-certified-science"
    assert report["status"] == "PASS"
    assert len(report["instances"]) == 1
    assert report["instances"][0]["n"] == 1009
    assert report["classification"] in P39_ALLOWED_CLASSIFICATIONS
    assert report["soundness"]["accepted_false_positives"] == 0
    for inst in report["instances"]:
        if inst.get("certificate"):
            assert len(inst["certificate_hash"]) == 64
            assert inst["certificate"]["reproduction"]["status"] == "PASS"


def test_p39_checkpoint_resume(tmp_path: Path) -> None:
    from benchmarks.open_problems import run_certified_campaign

    ckpt = tmp_path / "p39-checkpoint.json"
    kwargs = {
        "problem_id": "erdos-straus",
        "freeze_manifest": _REPO_ROOT / "experiments" / "p38-confirmation.json",
        "nomination_path": _REPO_ROOT / "experiments" / "p39-nomination.json",
        "device_name": "cpu",
        "smoke": True,
        "checkpoint_path": ckpt,
    }
    first = run_certified_campaign(output_path=tmp_path / "p39-a.json", **kwargs)
    assert ckpt.exists()
    second = run_certified_campaign(output_path=tmp_path / "p39-b.json", **kwargs)
    assert first["instances"][0]["classification"] == second["instances"][0]["classification"]
    if second["instances"][0].get("certificate_hash"):
        assert second["instances"][0]["resumed"] is True


def test_p39_blocked_without_valid_freeze(tmp_path: Path) -> None:
    import json as _json

    from benchmarks.open_problems import run_certified_campaign

    bad_freeze = tmp_path / "bad-freeze.json"
    bad_freeze.write_text(_json.dumps({"phase": "p38", "status": "FAIL"}))
    report = run_certified_campaign(
        problem_id="erdos-straus",
        freeze_manifest=bad_freeze,
        nomination_path=_REPO_ROOT / "experiments" / "p39-nomination.json",
        output_path=tmp_path / "p39-blocked.json",
        device_name="cpu",
        smoke=True,
        checkpoint_path=None,
    )
    assert report["status"] == "FAIL"
    assert report["classification"] == "BLOCKED"


def test_p39_rejects_parallel_problems(tmp_path: Path) -> None:
    import pytest

    from benchmarks.open_problems import run_certified_campaign

    with pytest.raises(ValueError, match="one campaign per cycle"):
        run_certified_campaign(
            problem_id="erdos-straus+taxicab",
            output_path=tmp_path / "p39-bad.json",
            checkpoint_path=None,
        )
