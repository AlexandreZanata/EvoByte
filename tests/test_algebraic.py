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
