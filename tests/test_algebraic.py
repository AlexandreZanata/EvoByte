"""Unit tests for algebraic polynomial identity synthesis in Q[k] (P74)."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

from evobyte.algebraic import (
    Poly1D,
    audit_algebraic_coverage,
    synthesize_mordell_identity,
)


def test_poly1d_arithmetic():
    # p1(k) = 2 + 3k
    p1 = Poly1D.linear(3, 2)
    # p2(k) = 1 + k
    p2 = Poly1D.linear(1, 1)

    # Addition
    p_add = p1 + p2
    assert p_add.coeffs == (Fraction(3), Fraction(4))
    assert p_add.eval(0) == 3
    assert p_add.eval(2) == 11

    # Subtraction
    p_sub = p1 - p2
    assert p_sub.coeffs == (Fraction(1), Fraction(2))

    # Multiplication: (2 + 3k)(1 + k) = 2 + 5k + 3k^2
    p_mul = p1 * p2
    assert p_mul.coeffs == (Fraction(2), Fraction(5), Fraction(3))
    assert p_mul.degree == 2

    # Exact division
    q = p_mul.exact_divide(p2)
    assert q is not None
    assert q.coeffs == p1.coeffs

    # Division by non-divisor returns None
    bad_q = p1.exact_divide(Poly1D.constant(0))
    assert bad_q is None

    not_divisor = p1.exact_divide(p2)
    assert not_divisor is None


def test_mordell_rediscovery_4k_3():
    ident = synthesize_mordell_identity(4, 3)
    assert ident is not None
    assert ident.m == 4
    assert ident.r == 3
    assert ident.verify_exact() is True
    # Test values at k=0: n = 3, X = 1, Y = 6, Z = 6
    # 4/3 = 1/1 + 1/6 + 1/6 = 1 + 2/6 = 4/3
    X, Y, Z = ident.evaluate(0)
    assert 4 / Fraction(3) == Fraction(1, X) + Fraction(1, Y) + Fraction(1, Z)

    # Test values at k=1: n = 7, X = 2, Y = 28, Z = 28
    # 4/7 = 1/2 + 1/28 + 1/28 = 1/2 + 1/14 = 8/14 = 4/7
    X1, Y1, Z1 = ident.evaluate(1)
    assert 4 / Fraction(7) == Fraction(1, X1) + Fraction(1, Y1) + Fraction(1, Z1)


def test_mordell_rediscovery_3k_2():
    ident = synthesize_mordell_identity(3, 2)
    assert ident is not None
    assert ident.m == 3
    assert ident.r == 2
    assert ident.verify_exact() is True
    # Test values at k=0: n = 2, X = 1, Y = 2, Z = 2
    # 4/2 = 2 = 1/1 + 1/2 + 1/2 = 2
    X, Y, Z = ident.evaluate(0)
    assert 4 / Fraction(2) == Fraction(1, X) + Fraction(1, Y) + Fraction(1, Z)

    # Test values at k=1: n = 5, X = 2, Y = 5, Z = 10
    # 4/5 = 1/2 + 1/5 + 1/10 = 5/10 + 2/10 + 1/10 = 8/10 = 4/5
    X1, Y1, Z1 = ident.evaluate(1)
    assert 4 / Fraction(5) == Fraction(1, X1) + Fraction(1, Y1) + Fraction(1, Z1)


def test_mordell_rediscovery_8k_5():
    ident = synthesize_mordell_identity(8, 5)
    assert ident is not None
    assert ident.m == 8
    assert ident.r == 5
    assert ident.verify_exact() is True
    # Test values at k=0: n = 5, X = 2, Y = 10, Z = 5
    # 4/5 = 1/2 + 1/10 + 1/5 = 4/5
    X, Y, Z = ident.evaluate(0)
    assert 4 / Fraction(5) == Fraction(1, X) + Fraction(1, Y) + Fraction(1, Z)


def test_algebraic_identity_lean_generation():
    ident = synthesize_mordell_identity(4, 3)
    assert ident is not None
    lean_src = ident.to_lean_statement("mordell_4k_3")
    assert "theorem mordell_4k_3" in lean_src
    assert "intro k" in lean_src
    assert "ring" in lean_src


def test_congruence_family_coverage_mod24():
    coverage = audit_algebraic_coverage(24)
    assert coverage["modulus"] == 24
    assert coverage["total_residues"] == 24
    # All covered identities must be verified
    assert coverage["covered_count"] >= 10
    assert coverage["coverage_ratio"] >= 0.4
    assert coverage["verified"] is True
    # 3 and 2 mod 4/3 are covered
    assert 3 in coverage["covered_residues"] or 2 in coverage["covered_residues"]


def test_p74_acceptance_smoke(tmp_path: Path):
    from benchmarks.science_matrix import run_p74_algebraic_audit

    cfg = {
        "phase": "P74",
        "modulus": 24,
        "seed": 42,
        "allow_dirty": True,
    }
    cfg_p = tmp_path / "p74-smoke-config.json"
    cfg_p.write_text(json.dumps(cfg))
    out_p = tmp_path / "p74-out.json"

    report = run_p74_algebraic_audit(cfg_p, out_p)
    assert out_p.exists()
    assert report["phase"] == "P74"
    assert report["verdict"] == "ACCEPTED"
    assert report["coverage"]["covered_count"] >= 10
    assert len(report["classical_identities"]) == 3


def test_p74_acceptance_rejects_wrong_phase(tmp_path: Path):
    from benchmarks.science_matrix import run_p74_algebraic_audit

    cfg_p = tmp_path / "bad.json"
    cfg_p.write_text(json.dumps({"phase": "INVALID"}))
    with pytest.raises(ValueError, match="not a P74 configuration"):
        run_p74_algebraic_audit(cfg_p, tmp_path / "out.json")


def test_poly1d_substitute():
    # p(k') = 2 + 3*k'
    p = Poly1D.linear(3, 2)
    # inner(k) = 1 + 5*k
    inner = Poly1D.linear(5, 1)
    # p(inner(k)) = 2 + 3*(1 + 5*k) = 5 + 15*k
    res = p.substitute(inner)
    assert res.coeffs == (Fraction(5), Fraction(15))
    assert res.eval(2) == 35


def test_coprime_quadratic_residues_isolation():
    from evobyte.algebraic import (
        get_resistant_residues,
        is_coprime_quadratic_residue,
    )

    # Modulo 24: only 1^2 = 1
    assert get_resistant_residues(24) == [1]
    assert is_coprime_quadratic_residue(24, 1) is True
    assert is_coprime_quadratic_residue(24, 5) is False

    # Modulo 120: 1 and 49 (7^2)
    assert get_resistant_residues(120) == [1, 49]

    # Modulo 840: exactly the 6 classical Mordell resistant quadratic non-covered squares
    # 1^2, 11^2, 13^2, 17^2, 19^2, 23^2
    res_840 = get_resistant_residues(840)
    expected_840 = [1, 121, 169, 289, 361, 529]
    assert res_840 == expected_840

    # Modulo 2520: exactly 18 squares
    res_2520 = get_resistant_residues(2520)
    assert len(res_2520) == 18
    for r in expected_840:
        assert r in res_2520


def test_modular_coverage_matrix_mod24():
    from evobyte.algebraic import (
        build_congruence_coverage_matrix,
        verify_coverage_matrix_soundness,
    )

    mat = build_congruence_coverage_matrix(24)
    assert mat["modulus"] == 24
    assert mat["total_classes"] == 24
    assert mat["covered_count"] == 23
    assert mat["resistant_count"] == 1
    assert mat["resistant_classes"] == [1]
    assert mat["coverage_ratio"] == 23 / 24
    assert mat["verified"] is True
    assert len(mat["checksum"]) == 64

    sound, findings = verify_coverage_matrix_soundness(mat)
    assert sound is True
    assert findings == []


def test_modular_coverage_matrix_mod120():
    from evobyte.algebraic import (
        build_congruence_coverage_matrix,
        verify_coverage_matrix_soundness,
    )

    mat = build_congruence_coverage_matrix(120)
    assert mat["modulus"] == 120
    assert mat["covered_count"] == 118
    assert mat["resistant_count"] == 2
    assert mat["resistant_classes"] == [1, 49]
    assert mat["coverage_ratio"] == 118 / 120
    assert mat["verified"] is True

    sound, findings = verify_coverage_matrix_soundness(mat)
    assert sound is True
    assert findings == []


def test_modular_coverage_matrix_mod840():
    from evobyte.algebraic import (
        build_congruence_coverage_matrix,
        verify_coverage_matrix_soundness,
    )

    mat = build_congruence_coverage_matrix(840)
    assert mat["modulus"] == 840
    assert mat["total_classes"] == 840
    assert mat["covered_count"] == 834
    assert mat["resistant_count"] == 6
    assert mat["resistant_classes"] == [1, 121, 169, 289, 361, 529]
    assert abs(mat["coverage_ratio"] - (834 / 840)) < 1e-9
    assert mat["verified"] is True
    # Canonical immutable checksum check
    assert mat["checksum"] == "34ce9589bc7cd7684415a67ea86f1dd85ab765c8137d62c3b3d1818cdc287fa7"

    sound, findings = verify_coverage_matrix_soundness(mat)
    assert sound is True
    assert findings == []


def test_modular_coverage_matrix_mod2520():
    from evobyte.algebraic import (
        build_congruence_coverage_matrix,
        verify_coverage_matrix_soundness,
    )

    mat = build_congruence_coverage_matrix(2520)
    assert mat["modulus"] == 2520
    assert mat["covered_count"] == 2502
    assert mat["resistant_count"] == 18
    assert mat["verified"] is True

    sound, findings = verify_coverage_matrix_soundness(mat)
    assert sound is True
    assert findings == []


def test_coverage_matrix_soundness_rejections():
    from evobyte.algebraic import (
        build_congruence_coverage_matrix,
        verify_coverage_matrix_soundness,
    )

    mat = build_congruence_coverage_matrix(24)

    # Tampered checksum
    bad_mat1 = dict(mat)
    bad_mat1["checksum"] = "0" * 64
    ok1, f1 = verify_coverage_matrix_soundness(bad_mat1)
    assert ok1 is False
    assert any("CHECKSUM_MISMATCH" in x for x in f1)

    # Tampered unverified
    bad_mat2 = dict(mat)
    bad_mat2["verified"] = False
    ok2, f2 = verify_coverage_matrix_soundness(bad_mat2)
    assert ok2 is False
    assert any("UNVERIFIED_STATUS" in x for x in f2)

    # Overlap between covered and resistant
    bad_mat3 = dict(mat)
    bad_mat3["covered_classes"] = sorted(mat["covered_classes"] + [1])
    ok3, f3 = verify_coverage_matrix_soundness(bad_mat3)
    assert ok3 is False
    assert any("OVERLAP_FOUND" in x for x in f3)


def test_classify_congruence_residue():
    from evobyte.algebraic import classify_congruence_residue

    # Resistant 1 mod 840
    c1 = classify_congruence_residue(840, 1)
    assert c1["is_resistant"] is True
    assert c1["mechanism"] == "resistant_quadratic_residue"

    # Even 0 mod 840
    c0 = classify_congruence_residue(840, 0)
    assert c0["is_resistant"] is False
    assert c0["mechanism"] == "even_divisibility_2"

    # 2 mod 3 (residue 2)
    c2 = classify_congruence_residue(840, 2)
    assert c2["mechanism"] == "even_divisibility_2"

    # 2 mod 3 (residue 5: 5 % 3 == 2)
    c5 = classify_congruence_residue(840, 5)
    assert c5["mechanism"] == "mordell_2_mod_3"

    # 5 mod 8 (residue 13: 13 % 3 == 1, 13 % 8 == 5)
    c13 = classify_congruence_residue(840, 13)
    assert c13["mechanism"] == "mordell_5_mod_8"


def test_open_problems_algebraic_congruence_solver():
    from benchmarks.open_problems import check_erdos_straus_algebraic_congruence

    # Covered cases produce valid integer solutions
    for n in [2, 3, 4, 5, 7, 24, 73, 120, 840, 1007, 1680]:
        ok, det = check_erdos_straus_algebraic_congruence(n, 840)
        assert ok is True
        assert det["verified_exact"] is True
        x, y, z = det["triple"]
        assert x > 0 and y > 0 and z > 0

    # Resistant case 1009 = 840 + 169 (169 mod 840 is resistant)
    ok_res, det_res = check_erdos_straus_algebraic_congruence(1009, 840)
    assert ok_res is False
    assert det_res["classification"]["is_resistant"] is True


def test_p75_acceptance_smoke(tmp_path: Path):
    from benchmarks.science_matrix import run_p75_coverage_audit

    cfg = {
        "phase": "P75",
        "moduli": [24, 120, 840],
        "target_modulus": 840,
        "seed": 42,
        "allow_dirty": True,
    }
    cfg_p = tmp_path / "p75-smoke-config.json"
    cfg_p.write_text(json.dumps(cfg))
    out_p = tmp_path / "p75-out.json"

    report = run_p75_coverage_audit(cfg_p, out_p)
    assert out_p.exists()
    assert report["phase"] == "P75"
    assert report["verdict"] == "ACCEPTED"
    assert report["coverage_840"]["covered_count"] == 834
    assert report["coverage_840"]["resistant_count"] == 6
    assert report["coverage_840"]["checksum"] == "34ce9589bc7cd7684415a67ea86f1dd85ab765c8137d62c3b3d1818cdc287fa7"
    assert len(report["multi_moduli_summary"]) == 3


def test_p75_acceptance_rejects_wrong_phase(tmp_path: Path):
    from benchmarks.science_matrix import run_p75_coverage_audit

    cfg_p = tmp_path / "bad.json"
    cfg_p.write_text(json.dumps({"phase": "INVALID"}))
    with pytest.raises(ValueError, match="not a P75 configuration"):
        run_p75_coverage_audit(cfg_p, tmp_path / "out.json")
