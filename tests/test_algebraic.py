"""Unit tests for algebraic polynomial identity synthesis in Q[k] (P74)."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

import pytest

from evobyte.algebraic import (
    Poly1D,
    audit_algebraic_coverage,
    synthesize_mordell_identity,
)
from evobyte.verifier import is_lean_available

needs_lean = pytest.mark.skipif(not is_lean_available(), reason="requires Lean 4 toolchain")


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
    assert (
        report["coverage_840"]["checksum"]
        == "34ce9589bc7cd7684415a67ea86f1dd85ab765c8137d62c3b3d1818cdc287fa7"
    )
    assert len(report["multi_moduli_summary"]) == 3


def test_p75_acceptance_rejects_wrong_phase(tmp_path: Path):
    from benchmarks.science_matrix import run_p75_coverage_audit

    cfg_p = tmp_path / "bad.json"
    cfg_p.write_text(json.dumps({"phase": "INVALID"}))
    with pytest.raises(ValueError, match="not a P75 configuration"):
        run_p75_coverage_audit(cfg_p, tmp_path / "out.json")


def test_integer_factorization():
    from evobyte.algebraic import integer_factorization

    assert integer_factorization(1) == {}
    assert integer_factorization(2) == {2: 1}
    assert integer_factorization(12) == {2: 2, 3: 1}
    assert integer_factorization(360) == {2: 3, 3: 2, 5: 1}
    assert integer_factorization(1009) == {1009: 1}


def test_get_square_divisors():
    from evobyte.algebraic import get_square_divisors

    assert get_square_divisors(1) == [1]
    assert get_square_divisors(2) == [1, 2, 4]
    divs_12 = get_square_divisors(12)
    # 12^2 = 144
    assert 144 in divs_12
    assert divs_12 == sorted(divs_12)
    assert len(divs_12) == 15  # (2*2 + 1) * (2*1 + 1) = 5 * 3 = 15


def test_quadratic_divisor_decomposition():
    from evobyte.algebraic import quadratic_divisor_decomposition

    for n in (1009, 1033, 1129, 1153, 1201):
        sol, det = quadratic_divisor_decomposition(n, max_d=100)
        assert sol is not None
        x, y, z = sol
        assert 4 * x * y * z == n * (x * y + y * z + z * x)
        assert det["verified_exact"] is True
        assert det["candidates_evaluated"] > 0
        assert det["d"] > 0


def test_rational_divisor_sieve_resistant_primes():
    from evobyte.algebraic import rational_divisor_sieve

    # Resistant quadratic residue primes mod 840 and n = 1 mod 24
    resistant_primes = [1009, 1033, 1129, 1153, 1201, 1249, 1297, 1321]
    for p in resistant_primes:
        sol, det = rational_divisor_sieve(p, max_x_steps=100)
        assert sol is not None
        x, y, z = sol
        assert 4 * x * y * z == p * (x * y + y * z + z * x)
        assert det["verified_exact"] is True
        # Sublinear candidate search: all found in under 150 candidates
        assert det["candidates_evaluated"] < 150
        # Modular prime filter pruned invalid divisors
        assert det["pruned_by_small_primes"] >= 0


def test_solve_erdos_straus_sieve():
    from evobyte.algebraic import solve_erdos_straus_sieve

    for n in (1009, 1033, 1129):
        sol, det = solve_erdos_straus_sieve(n)
        assert sol is not None
        x, y, z = sol
        assert 4 * x * y * z == n * (x * y + y * z + z * x)
        assert det["verified_exact"] is True
        assert det["method"] in ("rational_divisor_sieve", "quadratic_divisor_decomposition")


def test_benchmark_sieve_vs_baseline():
    from evobyte.algebraic import benchmark_sieve_vs_baseline

    test_instances = [1009, 1033, 1129]
    bench = benchmark_sieve_vs_baseline(test_instances)

    assert bench["instances_count"] == 3
    assert bench["false_negatives"] == 0
    assert bench["all_sieve_valid"] is True
    # Sublinear sieve must evaluate dramatically fewer candidates
    assert bench["overall_candidate_reduction"] > 100.0
    assert bench["overall_speedup"] > 1.0


def test_open_problems_algebraic_congruence_with_sieve_fallback():
    from benchmarks.open_problems import check_erdos_straus_algebraic_congruence

    # Without fallback, resistant residue 1009 returns False
    ok_no_fallback, det_no_fallback = check_erdos_straus_algebraic_congruence(
        1009, 840, fallback_sieve=False
    )
    assert ok_no_fallback is False
    assert det_no_fallback["classification"]["is_resistant"] is True

    # With fallback, resistant residue 1009 is solved and verified
    ok_fallback, det_fallback = check_erdos_straus_algebraic_congruence(
        1009, 840, fallback_sieve=True
    )
    assert ok_fallback is True
    assert det_fallback["verified_exact"] is True
    assert det_fallback["status"] == "solved_by_rational_divisor_sieve"
    x, y, z = det_fallback["triple"]
    assert 4 * x * y * z == 1009 * (x * y + y * z + z * x)


def test_p76_acceptance_smoke(tmp_path: Path):
    from benchmarks.science_matrix import run_p76_sieve_audit

    cfg = {
        "phase": "P76",
        "target_instances": [1009, 1033, 1129],
        "min_speedup": 1.0,
        "min_candidate_reduction": 100.0,
        "seed": 42,
        "allow_dirty": True,
    }
    cfg_p = tmp_path / "p76-smoke-config.json"
    cfg_p.write_text(json.dumps(cfg))
    out_p = tmp_path / "p76-out.json"

    report = run_p76_sieve_audit(cfg_p, out_p)
    assert out_p.exists()
    assert report["phase"] == "P76"
    assert report["verdict"] == "ACCEPTED"
    assert report["benchmark_summary"]["false_negatives"] == 0
    assert report["benchmark_summary"]["all_sieve_valid"] is True
    assert report["benchmark_summary"]["overall_candidate_reduction"] > 100.0


def test_p76_acceptance_rejects_wrong_phase(tmp_path: Path):
    from benchmarks.science_matrix import run_p76_sieve_audit

    cfg_p = tmp_path / "bad.json"
    cfg_p.write_text(json.dumps({"phase": "INVALID"}))
    with pytest.raises(ValueError, match="not a P76 configuration"):
        run_p76_sieve_audit(cfg_p, tmp_path / "out.json")


# ----------------------------------------------------------------------------
# P78 — Sierpiński / Schinzel generalization
# ----------------------------------------------------------------------------


def test_p78_check_schinzel_and_sierpinski():
    from evobyte.algebraic import check_schinzel, check_schinzel_fractions, check_sierpinski

    ok, residual, _ = check_sierpinski(1009, 202, 203819, 41541980942)
    assert ok and residual == 0
    ok2, _, _ = check_schinzel(5, 1009, 202, 203819, 41541980942)
    assert ok2
    okf, diff, _ = check_schinzel_fractions(5, 1009, 202, 203819, 41541980942)
    assert okf and diff == 0
    bad, res, _ = check_schinzel(5, 1009, 202, 203819, 41541980943)
    assert not bad and res != 0
    assert not check_schinzel(5, 7, 0, 1, 1)[0]
    assert not check_schinzel(0, 7, 1, 1, 1)[0]
    assert not check_schinzel(True, 7, 1, 1, 1)[0]  # type: ignore[arg-type]


@pytest.mark.parametrize("a", [4, 5, 6, 7])
def test_p78_schinzel_divisor_sieve_primes(a):
    from evobyte.algebraic import check_schinzel, schinzel_divisor_sieve

    for p in (3, 5, 7, 11, 13, 17, 19, 23, 1009):
        sol, det = schinzel_divisor_sieve(a, p)
        assert sol is not None, (a, p)
        assert check_schinzel(a, p, *sol)[0]
        assert det["verified_exact"] is True


def test_p78_sieve_invalid_inputs_and_delegation():
    from evobyte.algebraic import (
        rational_divisor_sieve,
        schinzel_divisor_sieve,
        sierpinski_divisor_sieve,
    )

    sol, det = schinzel_divisor_sieve(5, 1)
    assert sol is None and "error" in det
    sol, det = schinzel_divisor_sieve(0, 7)
    assert sol is None and "error" in det
    assert sierpinski_divisor_sieve(1009)[0] == schinzel_divisor_sieve(5, 1009)[0]
    assert rational_divisor_sieve(1009)[0] == schinzel_divisor_sieve(4, 1009)[0]


def test_p78_synthesize_sierpinski_identities_are_exact():
    from evobyte.algebraic import synthesize_sierpinski_identity

    ident = synthesize_sierpinski_identity(120, 3)  # n = 4 mod... c=1 family: X=(n+1)/4
    assert ident is not None and ident.a == 5 and ident.verify_exact()
    for k in range(1, 6):
        x, y, z = ident.evaluate(k)
        assert 5 * x * y * z == (120 * k + 3) * (x * y + y * z + z * x)
    assert synthesize_sierpinski_identity(120, 1) is None


def test_p78_coverage_matrix_sierpinski():
    from evobyte.algebraic import build_sierpinski_coverage_matrix

    cov = build_sierpinski_coverage_matrix(120)
    assert cov["a"] == 5
    assert cov["coverage_ratio"] >= 0.75
    assert cov["covered_count"] + cov["uncovered_count"] == 120
    assert cov["verified_exact"] is True
    assert 1 in cov["uncovered_residues"]


def test_p78_compare_schinzel_synthesis():
    from evobyte.algebraic import compare_schinzel_synthesis

    cmp = compare_schinzel_synthesis(a_values=[4, 5], test_instances=[3, 5, 7, 11, 13, 1009])
    assert cmp["verified"] is True
    assert set(cmp["per_numerator"]) == {"4", "5"}
    assert "sierpinski_vs_erdos_straus" in cmp["comparisons"]


def test_p78_open_problems_exposure():
    from benchmarks.open_problems import check_schinzel, check_sierpinski, run_sierpinski_campaign

    assert check_sierpinski(1009, 202, 203819, 41541980942)[0]
    assert check_schinzel(6, 7, 2, 15, 210)[0] in (True, False)
    camp = run_sierpinski_campaign([3, 7, 11, 1009])
    assert camp["all_solved"] is True


def test_p78_lean_generators():
    from evobyte.algebraic import synthesize_sierpinski_identity
    from evobyte.formal_bridge import (
        sierpinski_identity_to_lean_theorem,
        sierpinski_instance_to_lean_theorem,
    )

    ident = synthesize_sierpinski_identity(120, 3)
    thm = sierpinski_identity_to_lean_theorem(ident)
    assert "theorem sierpinski_ident_m120_r3" in thm and "5 *" in thm and "ring" in thm
    cert = sierpinski_instance_to_lean_theorem(1009, 202, 203819, 41541980942)
    assert "(5 : ℚ) / 1009" in cert and "norm_num" in cert
    with pytest.raises(ValueError):
        sierpinski_instance_to_lean_theorem(1009, 1, 2, 3)


@needs_lean
def test_p78_acceptance_smoke(tmp_path):
    import json

    from benchmarks.science_matrix import run_p78_sierpinski_audit

    cfg = {
        "phase": "P78",
        "allow_dirty": True,
        "test_instances": [3, 5, 7, 11, 13, 1009],
        "numerators": [4, 5, 6, 7],
    }
    cfg_p = tmp_path / "p78.json"
    cfg_p.write_text(json.dumps(cfg))
    report = run_p78_sierpinski_audit(cfg_p, tmp_path / "out.json")
    assert report["verdict"] == "ACCEPTED", report["findings"]
    assert report["formal"]["has_sorry"] is False

    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"phase": "X"}))
    with pytest.raises(ValueError, match="not a P78 configuration"):
        run_p78_sierpinski_audit(bad, tmp_path / "o.json")


# ----------------------------------------------------------------------------
# P79 — Blind residue confirmation and statistical selection control
# ----------------------------------------------------------------------------


def test_p79_blind_split_integrity():
    split_p = Path("experiments/p79-blind-split.json")
    assert split_p.exists()
    data = json.loads(split_p.read_text(encoding="utf-8"))
    assert data["split_id"] == "p79-blind-residue-split-v1"
    assert "H_ES" in data["tracks"] and "H_SIER" in data["tracks"]

    es_insts = data["tracks"]["H_ES"]["instances"]
    sier_insts = data["tracks"]["H_SIER"]["instances"]
    assert len(es_insts) == 20
    assert len(sier_insts) == 20

    for item in es_insts:
        assert item["a"] == 4
        assert item["modulus"] == 840
        assert item["n"] == 840 * item["k"] + item["residue"]
        assert item["n"] >= 2

    for item in sier_insts:
        assert item["a"] == 5
        assert item["modulus"] == 120
        assert item["n"] == 120 * item["k"] + item["residue"]
        assert item["n"] >= 2


def test_p79_confirmation_smoke(tmp_path):
    from benchmarks.science_matrix import run_p79_confirmation_audit

    split_p = Path("experiments/p79-blind-split.json")
    split_sha = hashlib.sha256(split_p.read_bytes()).hexdigest()

    cfg = {
        "phase": "P79",
        "split_path": str(split_p),
        "split_sha256": split_sha,
        "alpha": 0.05,
        "min_decisive_instances": 5,
        "max_baseline_y_steps": 5000,
        "max_coord": 10**9,
        "allow_dirty": True,
        "require_clean_tree": False,
    }
    cfg_p = tmp_path / "p79-smoke.json"
    cfg_p.write_text(json.dumps(cfg))
    out_p = tmp_path / "p79-out.json"

    report = run_p79_confirmation_audit(cfg_p, out_p)
    assert report["phase"] == "P79"
    assert report["verdict"] == "ACCEPTED", report["findings"]
    assert report["tracks"]["H_ES"]["outcome"] == "CONFIRMED"
    assert report["tracks"]["H_SIER"]["outcome"] == "CONFIRMED"
    assert report["tracks"]["H_ES"]["holm_adjusted_p_value"] < 0.05
    assert report["tracks"]["H_SIER"]["holm_adjusted_p_value"] < 0.05


def test_p79_confirmation_rejects_corrupted_split(tmp_path):
    from benchmarks.science_matrix import run_p79_confirmation_audit

    split_p = Path("experiments/p79-blind-split.json")
    cfg = {
        "phase": "P79",
        "split_path": str(split_p),
        "split_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
        "allow_dirty": True,
    }
    cfg_p = tmp_path / "p79-bad-sha.json"
    cfg_p.write_text(json.dumps(cfg))
    out_p = tmp_path / "p79-out.json"

    report = run_p79_confirmation_audit(cfg_p, out_p)
    assert report["verdict"] == "REJECTED"
    assert any("SPLIT_DRIFT" in f for f in report["findings"])


def test_p79_confirmation_rejects_wrong_phase(tmp_path):
    from benchmarks.science_matrix import run_p79_confirmation_audit

    cfg_p = tmp_path / "bad-phase.json"
    cfg_p.write_text(json.dumps({"phase": "INVALID"}))
    with pytest.raises(ValueError, match="not a P79 configuration"):
        run_p79_confirmation_audit(cfg_p, tmp_path / "out.json")


def test_optimal_schinzel_divisor_sieve():
    from evobyte.algebraic import optimal_erdos_straus_sieve, optimal_sierpinski_sieve

    sol_es, det_es = optimal_erdos_straus_sieve(73)
    assert sol_es is not None
    assert det_es["verified_exact"] is True
    x, y, z = sol_es
    assert 4 * x * y * z == 73 * (x * y + y * z + z * x)
    assert max(sol_es) <= det_es["theoretical_bound"]

    sol_sier, det_sier = optimal_sierpinski_sieve(73)
    assert sol_sier is not None
    assert det_sier["verified_exact"] is True
    sx, sy, sz = sol_sier
    assert 5 * sx * sy * sz == 73 * (sx * sy + sy * sz + sz * sx)


def test_optimal_divisor_benchmark_reduction():
    from evobyte.algebraic import benchmark_optimal_vs_naive_sieve

    primes = [73, 97, 193, 241, 1009, 1153]
    res = benchmark_optimal_vs_naive_sieve(primes)
    assert res["instances_tested"] == len(primes)
    assert res["average_reduction_factor"] >= 10.0
    assert res["max_reduction_factor"] >= 100.0


@needs_lean
def test_p83_acceptance_smoke(tmp_path: Path):
    from benchmarks.science_matrix import run_p83_optimal_divisor_audit

    cfg = {
        "phase": "P83",
        "output_dir": "lean_proofs/Generated",
        "project_dir": "lean_proofs",
        "min_avg_reduction_factor": 5.0,
        "seed": 42,
        "require_clean_tree": False,
    }
    cfg_p = tmp_path / "p83-smoke-config.json"
    cfg_p.write_text(json.dumps(cfg))
    out_p = tmp_path / "p83-out.json"

    report = run_p83_optimal_divisor_audit(cfg_p, out_p)
    assert out_p.exists()
    assert report["phase"] == "P83"
    assert report["verdict"] == "ACCEPTED"
    assert report["total_certificates"] >= 4
    assert report["has_sorry"] is False
    assert report["file"] is not None


def test_p83_acceptance_rejects_wrong_phase(tmp_path: Path):
    from benchmarks.science_matrix import run_p83_optimal_divisor_audit

    cfg_p = tmp_path / "bad.json"
    cfg_p.write_text(json.dumps({"phase": "INVALID"}))
    with pytest.raises(ValueError, match="not a P83 configuration"):
        run_p83_optimal_divisor_audit(cfg_p, tmp_path / "out.json")


def test_poly2d_arithmetic():
    from evobyte.algebraic import Poly2D

    u = Poly2D.var_u()
    v = Poly2D.var_v()
    one = Poly2D.constant(1)

    p1 = u * 4 - one
    p2 = v * 4 - one
    prod = p1 * p2

    assert prod.total_degree == 2
    assert prod.degree_u == 1
    assert prod.degree_v == 1
    assert prod.eval(1, 1) == 9  # (4 - 1)*(4 - 1) = 9
    assert prod.eval(2, 3) == 7 * 11  # 77
    assert prod.is_strictly_positive(5) is True
    assert prod.is_integer_valued(5) is True

    # Power
    p_sq = p1**2
    assert p_sq.eval(3, 0) == 121  # 11^2 = 121
    assert p_sq.degree_u == 2
    assert p_sq.degree_v == -1 or p_sq.degree_v == 0


def test_quadratic_identity_synthesis():
    from evobyte.algebraic import synthesize_quadratic_identities

    idents = synthesize_quadratic_identities()
    assert len(idents) >= 12

    for ident in idents:
        assert ident.verify_exact(grid_size=5) is True
        lean_thm = ident.to_lean_theorem()
        assert f"theorem {ident.name}" in lean_thm
        assert "ring" in lean_thm


def test_resistant_residues_coverage():
    from evobyte.algebraic import evaluate_resistant_residues_coverage

    res = evaluate_resistant_residues_coverage()
    assert res["total_evaluated"] >= 10
    assert res["all_verified"] is True

    # Check resistant residues are included
    instances = res["instances"]
    ns = [inst["n"] for inst in instances]
    for target in (121, 169, 289, 361, 529, 9, 49):
        assert target in ns


@needs_lean
def test_p84_acceptance_smoke(tmp_path: Path):
    from benchmarks.science_matrix import run_p84_quadratic_identities_audit

    cfg = {
        "phase": "P84",
        "output_dir": "lean_proofs/Generated",
        "project_dir": "lean_proofs",
        "min_parametric_identities": 10,
        "min_instance_certificates": 8,
        "seed": 42,
        "require_clean_tree": False,
    }
    cfg_p = tmp_path / "p84-smoke-config.json"
    cfg_p.write_text(json.dumps(cfg))
    out_p = tmp_path / "p84-out.json"

    report = run_p84_quadratic_identities_audit(cfg_p, out_p)
    assert out_p.exists()
    assert report["phase"] == "P84"
    assert report["verdict"] == "ACCEPTED"
    assert report["total_theorems"] >= 12
    assert report["has_sorry"] is False
    assert report["file"] is not None


def test_p84_acceptance_rejects_wrong_phase(tmp_path: Path):
    from benchmarks.science_matrix import run_p84_quadratic_identities_audit

    cfg_p = tmp_path / "bad.json"
    cfg_p.write_text(json.dumps({"phase": "INVALID"}))
    with pytest.raises(ValueError, match="not a P84 configuration"):
        run_p84_quadratic_identities_audit(cfg_p, tmp_path / "out.json")


def test_multiterm_diophantine_checkers():
    from evobyte.algebraic import (
        check_multiterm_diophantine,
        check_multiterm_fractions,
        is_coprime_decomposition,
    )

    # 4/13 = 1/4 + 1/18 + 1/900 + 1/975
    terms = (4, 18, 900, 975)
    ok_int, res_int, det_int = check_multiterm_diophantine(4, 13, terms)
    assert ok_int is True
    assert res_int == 0
    assert det_int["verified_exact"] is True

    ok_frac, diff_frac, det_frac = check_multiterm_fractions(4, 13, terms)
    assert ok_frac is True
    assert diff_frac == 0
    assert det_frac["verified_exact"] is True

    coprime, joint_gcd, det_coprime = is_coprime_decomposition(terms)
    assert coprime is True
    assert joint_gcd == 1
    assert det_coprime["strictly_ordered"] is True
    assert det_coprime["distinct"] is True

    # Bad terms: not an Egyptian fraction
    bad_terms = (4, 18, 900, 976)
    b_int, b_res, _ = check_multiterm_diophantine(4, 13, bad_terms)
    assert b_int is False
    assert b_res != 0

    # Non-coprime decomposition
    non_coprime_terms = (4, 26, 52)
    c, g, _ = is_coprime_decomposition(non_coprime_terms)
    assert c is False
    assert g == 2


def test_optimal_coprime_and_multiterm_sieve():
    from evobyte.algebraic import (
        multiterm_divisor_sieve,
        optimal_coprime_divisor_sieve,
    )

    # 4/5 has 3-term coprime solution
    sol3, meta3 = optimal_coprime_divisor_sieve(4, 5)
    assert sol3 is not None
    assert sol3 == (2, 5, 10)
    assert meta3["coprime"] is True

    # 4/13 has NO 3-term coprime solution
    sol3_13, _ = optimal_coprime_divisor_sieve(4, 13)
    assert sol3_13 is None

    # 4/13 has verified 4-term coprime solution
    sol4_13, meta4_13 = multiterm_divisor_sieve(4, 13, k_terms=4, require_coprime=True)
    assert sol4_13 is not None
    assert sol4_13 == (4, 18, 900, 975)
    assert meta4_13["coprime"] is True
    assert meta4_13["joint_gcd"] == 1


def test_evaluate_multiterm_coprime_coverage():
    from evobyte.algebraic import evaluate_multiterm_coprime_coverage

    cov = evaluate_multiterm_coprime_coverage()
    assert cov["total_cases"] >= 20
    assert cov["four_term_certified"] >= 20
    assert cov["all_verified"] is True


@needs_lean
def test_p86_acceptance_smoke(tmp_path: Path):
    from benchmarks.science_matrix import run_p86_multiterm_audit

    cfg = {
        "phase": "P86",
        "output_dir": "lean_proofs/Generated",
        "project_dir": "lean_proofs",
        "min_instances": 12,
        "min_theorems": 24,
        "seed": 42,
        "require_clean_tree": False,
    }
    cfg_p = tmp_path / "p86-smoke-config.json"
    cfg_p.write_text(json.dumps(cfg))
    out_p = tmp_path / "p86-out.json"

    report = run_p86_multiterm_audit(cfg_p, out_p)
    assert out_p.exists()
    assert report["phase"] == "P86"
    assert report["verdict"] == "ACCEPTED"
    assert report["total_formal_theorems"] >= 24
    assert report["has_sorry"] is False
    assert report["four_term_certified"] >= 12


def test_p86_acceptance_rejects_wrong_phase(tmp_path: Path):
    from benchmarks.science_matrix import run_p86_multiterm_audit

    cfg_p = tmp_path / "bad.json"
    cfg_p.write_text(json.dumps({"phase": "INVALID"}))
    with pytest.raises(ValueError, match="not a P86 configuration"):
        run_p86_multiterm_audit(cfg_p, tmp_path / "out.json")


def test_p87_acceptance_smoke(tmp_path: Path):
    from benchmarks.science_matrix import run_p87_large_instance_audit

    cfg = {
        "phase": "P87",
        "split_path": "experiments/p87-blind-split.json",
        "split_sha256": "26fc33e282ec611855fd26c4e33442d9c34d19d9e47e50d1da3985a486c33219",
        "alpha": 0.05,
        "min_decisive_instances": 15,
        "max_baseline_y_steps": 500,
        "max_coord": 1000000000000,
        "seed": 42,
        "require_clean_tree": False,
    }
    cfg_p = tmp_path / "p87-smoke-config.json"
    cfg_p.write_text(json.dumps(cfg))
    out_p = tmp_path / "p87-out.json"

    report = run_p87_large_instance_audit(cfg_p, out_p)
    assert out_p.exists()
    assert report["phase"] == "P87"
    assert report["verdict"] == "ACCEPTED"
    assert len(report["tracks"]) == 2
    for t_info in report["tracks"].values():
        assert t_info["outcome"] == "CONFIRMED"
        assert t_info["holm_adjusted_p_value"] < 0.05
        assert t_info["all_verified"] is True


def test_p87_acceptance_rejects_wrong_phase(tmp_path: Path):
    from benchmarks.science_matrix import run_p87_large_instance_audit

    cfg_p = tmp_path / "bad.json"
    cfg_p.write_text(json.dumps({"phase": "INVALID"}))
    with pytest.raises(ValueError, match="not a P87 configuration"):
        run_p87_large_instance_audit(cfg_p, tmp_path / "out.json")


@needs_lean
def test_p88_acceptance_smoke(tmp_path: Path):
    from benchmarks.science_matrix import run_p88_meta_theorem_campaign_audit

    cfg = {
        "phase": "P88",
        "budget_sec": 3600.0,
        "min_theorems": 350,
        "project_dir": "lean_proofs",
        "dossier_path": "docs/research/p88-formal-dossier.md",
        "allow_missing_dossier": True,
        "seed": 42,
        "require_clean_tree": False,
    }
    cfg_p = tmp_path / "p88-smoke-config.json"
    cfg_p.write_text(json.dumps(cfg))
    out_p = tmp_path / "p88-out.json"

    report = run_p88_meta_theorem_campaign_audit(cfg_p, out_p)
    assert out_p.exists()
    assert report["phase"] == "P88"
    assert report["verdict"] == "ACCEPTED"
    assert report["total_formal_theorems"] >= 350
    assert report["has_sorry"] is False
    assert report["total_modules"] == 10


def test_p88_acceptance_rejects_wrong_phase(tmp_path: Path):
    from benchmarks.science_matrix import run_p88_meta_theorem_campaign_audit

    cfg_p = tmp_path / "bad.json"
    cfg_p.write_text(json.dumps({"phase": "INVALID"}))
    with pytest.raises(ValueError, match="not a P88 configuration"):
        run_p88_meta_theorem_campaign_audit(cfg_p, tmp_path / "out.json")


def test_p95_extreme_scale_blind_partition_integrity():
    split_p = Path("experiments/p95-blind-split.json")
    assert split_p.exists()
    data = json.loads(split_p.read_text(encoding="utf-8"))
    assert data["split_id"] == "p95-extreme-scale-blind-partition-v1"
    assert data["min_n"] == 10**7
    assert data["max_n"] == 10**9
    assert data["count_per_track"] == 20
    assert data["alpha"] == 0.01

    expected_tracks = ["H_A4", "H_A5", "H_A6", "H_A7", "H_A8"]
    for t_key in expected_tracks:
        assert t_key in data["tracks"]
        t_info = data["tracks"][t_key]
        assert len(t_info["instances"]) == 20
        for inst in t_info["instances"]:
            assert inst["a"] == t_info["a"]
            assert 10**7 <= inst["n"] <= 10**9


def test_p95_sign_test_and_soundness():
    from evobyte.algebraic import (
        compute_sign_test_pvalue,
        verify_extreme_scale_confirmation_soundness,
    )

    p_20_0 = compute_sign_test_pvalue(20, 0)
    assert p_20_0 < 2e-6
    p_10_10 = compute_sign_test_pvalue(10, 10)
    assert p_10_10 == 1.0

    sound, findings = verify_extreme_scale_confirmation_soundness({}, alpha=0.01)
    assert sound is False
    assert any("NO_TRACKS" in f for f in findings)


def test_p95_confirmation_smoke(tmp_path: Path):
    from benchmarks.science_matrix import run_p95_extreme_scale_audit
    from evobyte.algebraic import generate_extreme_scale_blind_partition

    # Quick smoke partition with 8 instances per track (satisfying alpha=0.05 under Holm)
    smoke_part = generate_extreme_scale_blind_partition(
        seed=101,
        count_per_track=8,
        min_n=10**7,
        max_n=10**8,
        numerators=[4, 5],
        max_coord=10**18,
        alpha=0.05,
    )
    smoke_split_p = tmp_path / "p95-smoke-split.json"
    smoke_bytes = json.dumps(smoke_part, indent=2, sort_keys=True).encode("utf-8")
    smoke_split_p.write_bytes(smoke_bytes)
    smoke_sha = hashlib.sha256(smoke_bytes).hexdigest()

    cfg = {
        "phase": "P95",
        "split_path": str(smoke_split_p),
        "split_sha256": smoke_sha,
        "alpha": 0.05,
        "min_decisive_instances": 8,
        "max_baseline_y_steps": 500,
        "max_coord": 10**18,
        "allow_dirty": True,
        "require_clean_tree": False,
    }
    cfg_p = tmp_path / "p95-smoke-config.json"
    cfg_p.write_text(json.dumps(cfg))
    out_p = tmp_path / "p95-out.json"

    report = run_p95_extreme_scale_audit(cfg_p, out_p)
    assert out_p.exists()
    assert report["phase"] == "P95"
    assert report["verdict"] == "ACCEPTED"
    assert report["fwer_controlled"] is True
    assert len(report["tracks"]) == 2
    for t_info in report["tracks"].values():
        assert t_info["outcome"] == "CONFIRMED"
        assert t_info["all_verified"] is True


def test_p95_confirmation_rejects_corrupted_split(tmp_path: Path):
    from benchmarks.science_matrix import run_p95_extreme_scale_audit

    split_p = Path("experiments/p95-blind-split.json")
    cfg = {
        "phase": "P95",
        "split_path": str(split_p),
        "split_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
        "allow_dirty": True,
        "require_clean_tree": False,
    }
    cfg_p = tmp_path / "p95-bad-sha.json"
    cfg_p.write_text(json.dumps(cfg))
    out_p = tmp_path / "p95-out.json"

    report = run_p95_extreme_scale_audit(cfg_p, out_p)
    assert report["verdict"] == "REJECTED"
    assert any("SPLIT_DRIFT" in f for f in report["findings"])


def test_p95_confirmation_rejects_wrong_phase(tmp_path: Path):
    from benchmarks.science_matrix import run_p95_extreme_scale_audit

    cfg_p = tmp_path / "bad.json"
    cfg_p.write_text(json.dumps({"phase": "INVALID"}))
    with pytest.raises(ValueError, match="not a P95 configuration"):
        run_p95_extreme_scale_audit(cfg_p, tmp_path / "out.json")


# ==============================================================================
# P145 TESTS: SCHINZEL HIGH-ORDER MODULI CONGRUENCE DATABASE & RESISTANT ORBITS
# ==============================================================================


def test_p145_schinzel_high_moduli_database() -> None:
    """Test P145 Schinzel high moduli database construction, lifting towers, and soundness."""
    from evobyte.algebraic import (
        build_schinzel_high_moduli_database,
        compute_schinzel_coprime_residues,
        compute_schinzel_quadratic_residues,
        verify_schinzel_high_moduli_database_soundness,
    )

    qr840 = compute_schinzel_quadratic_residues(840)
    assert len(qr840) == 6
    assert qr840 == [1, 121, 169, 289, 361, 529]

    qr2520 = compute_schinzel_quadratic_residues(2520)
    assert len(qr2520) == 18

    qr5040 = compute_schinzel_quadratic_residues(5040)
    assert len(qr5040) == 36

    db = build_schinzel_high_moduli_database()
    assert len(db["pairs"]) == 12
    assert db["lifting_towers"]["2520_to_840_valid"] is True
    assert db["lifting_towers"]["5040_to_2520_valid"] is True

    sound, findings = verify_schinzel_high_moduli_database_soundness(db)
    assert sound is True
    assert findings == []


def test_p145_schinzel_high_moduli_baseline_audit() -> None:
    """Test P145 formal module audit, theorem count (>= 80), and absence of sorry."""
    from evobyte.algebraic import (
        audit_schinzel_high_moduli_baseline,
        verify_schinzel_high_moduli_baseline_soundness,
    )

    audit = audit_schinzel_high_moduli_baseline(verify_lake=False)
    assert audit["total_theorems"] >= 80
    assert audit["has_sorry"] is False
    assert audit["database_sound"] is True
    assert audit["sha256"] == "d260059205969979f4e0c5b25718502c8cb4d7c8a78f5bb9955c68d6fba770aa"

    sound, findings = verify_schinzel_high_moduli_baseline_soundness(audit, min_theorems=80)
    assert sound is True
    assert findings == []


def test_p145_soundness_validator_rejections() -> None:
    """Test that P145 soundness validator rejects defective formal baselines."""
    from evobyte.algebraic import verify_schinzel_high_moduli_baseline_soundness

    # Defect: sorry present
    bad_audit = {
        "total_theorems": 100,
        "has_sorry": True,
        "database_sound": True,
        "lake_passed": True,
    }
    sound, findings = verify_schinzel_high_moduli_baseline_soundness(bad_audit)
    assert sound is False
    assert any("SORRY_DETECTED" in f for f in findings)

    # Defect: insufficient theorems
    low_thms = {
        "total_theorems": 20,
        "has_sorry": False,
        "database_sound": True,
        "lake_passed": True,
    }
    sound, findings = verify_schinzel_high_moduli_baseline_soundness(low_thms, min_theorems=80)
    assert sound is False
    assert any("INSUFFICIENT_THEOREMS" in f for f in findings)

    # Defect: database unsound
    bad_db = {
        "total_theorems": 100,
        "has_sorry": False,
        "database_sound": False,
        "database_findings": ["TEST_CORRUPTION"],
        "lake_passed": True,
    }
    sound, findings = verify_schinzel_high_moduli_baseline_soundness(bad_db)
    assert sound is False
    assert "TEST_CORRUPTION" in findings


def test_p145_acceptance_rejects_wrong_phase(tmp_path: Path) -> None:
    """Test that P145 audit rejects invalid configuration phase."""
    import sys

    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root / "benchmarks") not in sys.path:
        sys.path.insert(0, str(repo_root / "benchmarks"))
    from benchmarks.science_matrix import run_p145_schinzel_high_moduli_audit

    cfg_p = tmp_path / "bad-p145.json"
    cfg_p.write_text(json.dumps({"phase": "INVALID"}))
    with pytest.raises(ValueError, match="not a P145 configuration"):
        run_p145_schinzel_high_moduli_audit(cfg_p, tmp_path / "out.json")


def test_p145_audit_smoke(tmp_path: Path) -> None:
    """Test smoke run of P145 audit on valid config."""
    import sys

    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root / "benchmarks") not in sys.path:
        sys.path.insert(0, str(repo_root / "benchmarks"))
    from benchmarks.science_matrix import run_p145_schinzel_high_moduli_audit

    cfg_file = repo_root / "experiments/p145-config.json"
    with open(cfg_file, encoding="utf-8") as f:
        cfg_data = json.load(f)
    cfg_data["verify_lake"] = False
    cfg_data["allow_dirty"] = True

    tmp_cfg = tmp_path / "p145-smoke-config.json"
    tmp_cfg.write_text(json.dumps(cfg_data))
    out_file = tmp_path / "p145-smoke-out.json"

    report = run_p145_schinzel_high_moduli_audit(tmp_cfg, out_file)
    assert report["phase"] == "P145"
    assert report["total_theorems"] >= 80
    assert report["has_sorry"] is False
    assert report["database_sound"] is True
    assert out_file.exists()


def test_accelerated_schinzel_quadratic_sieve() -> None:
    """Test accelerated quadratic sieve for Schinzel resistant instances across numerators."""
    from evobyte.algebraic import accelerated_schinzel_quadratic_sieve

    # Invalid inputs
    assert accelerated_schinzel_quadratic_sieve(1, a=5)[0] is None
    assert accelerated_schinzel_quadratic_sieve(10, a=0)[0] is None

    # Test resistant instances for a in {5, 6, 7, 8} with M=840
    test_cases = [
        (840 * 1 + 1, 5),
        (840 * 1 + 121, 5),
        (840 * 1 + 1, 6),
        (840 * 1 + 121, 6),
        (840 * 1 + 1, 7),
        (840 * 1 + 121, 7),
        (840 * 1 + 1, 8),
        (840 * 1 + 121, 8),
    ]
    for n, a in test_cases:
        sol, telemetry = accelerated_schinzel_quadratic_sieve(n, a=a, max_x_steps=50)
        assert sol is not None, f"Failed to solve for a={a}, n={n}"
        x, y, z = sol
        assert x > 0 and y > 0 and z > 0
        assert a * x * y * z == n * (x * y + y * z + z * x)
        assert telemetry["verified"] is True
        assert telemetry["modular_pruned"] >= 0


def test_p146_soundness_and_lake() -> None:
    """Test soundness verification and error detection for P146 baseline audit."""
    from evobyte.algebraic import (
        audit_schinzel_quadratic_sieve_baseline,
        verify_schinzel_quadratic_sieve_baseline_soundness,
    )

    audit_res = audit_schinzel_quadratic_sieve_baseline(verify_lake=False)
    assert audit_res["total_theorems"] >= 80
    assert audit_res["has_sorry"] is False
    assert audit_res["all_resistant_solved"] is True
    assert audit_res["all_solutions_valid"] is True

    # Test error detection
    corrupted = dict(audit_res)
    corrupted["has_sorry"] = True
    sound, findings = verify_schinzel_quadratic_sieve_baseline_soundness(corrupted)
    assert sound is False
    assert any("SORRY_DETECTED" in f for f in findings)

    corrupted_thms = dict(audit_res)
    corrupted_thms["total_theorems"] = 10
    sound, findings = verify_schinzel_quadratic_sieve_baseline_soundness(corrupted_thms, min_theorems=80)
    assert sound is False
    assert any("INSUFFICIENT_THEOREMS" in f for f in findings)

    corrupted_unsolved = dict(audit_res)
    corrupted_unsolved["all_resistant_solved"] = False
    sound, findings = verify_schinzel_quadratic_sieve_baseline_soundness(corrupted_unsolved)
    assert sound is False
    assert any("UNSOLVED_RESISTANT_INSTANCES" in f for f in findings)


def test_p146_acceptance_rejects_wrong_phase(tmp_path: Path) -> None:
    """Test that P146 audit rejects invalid configuration phase."""
    import sys

    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root / "benchmarks") not in sys.path:
        sys.path.insert(0, str(repo_root / "benchmarks"))
    from benchmarks.science_matrix import run_p146_schinzel_quadratic_sieve_audit

    cfg_p = tmp_path / "bad-p146.json"
    cfg_p.write_text(json.dumps({"phase": "INVALID"}))
    with pytest.raises(ValueError, match="not a P146 configuration"):
        run_p146_schinzel_quadratic_sieve_audit(cfg_p, tmp_path / "out.json")


def test_p146_audit_smoke(tmp_path: Path) -> None:
    """Test smoke run of P146 audit on valid config."""
    import sys

    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root / "benchmarks") not in sys.path:
        sys.path.insert(0, str(repo_root / "benchmarks"))
    from benchmarks.science_matrix import run_p146_schinzel_quadratic_sieve_audit

    cfg_file = repo_root / "experiments/p146-config.json"
    with open(cfg_file, encoding="utf-8") as f:
        cfg_data = json.load(f)
    cfg_data["verify_lake"] = False
    cfg_data["allow_dirty"] = True

    tmp_cfg = tmp_path / "p146-smoke-config.json"
    tmp_cfg.write_text(json.dumps(cfg_data))
    out_file = tmp_path / "p146-smoke-out.json"

    report = run_p146_schinzel_quadratic_sieve_audit(tmp_cfg, out_file)
    assert report["phase"] == "P146"
    assert report["total_theorems"] >= 80
    assert report["has_sorry"] is False
    assert report["all_resistant_solved"] is True
    assert report["all_solutions_valid"] is True
    assert out_file.exists()


def test_synthesize_polynomial_identity_for_class() -> None:
    """Test synthesis of exact parametric polynomial identities in Q[k]."""
    from evobyte.algebraic import synthesize_polynomial_identity_for_class

    res5 = synthesize_polynomial_identity_for_class(a=5, M=840, r=1, k0=1)
    assert res5 is not None
    assert res5["verified_algebraic"] is True
    assert res5["strictly_ordered"] is True
    assert res5["degrees"] == [1, 2, 3]
    assert len(res5["samples"]) == 4

    res7 = synthesize_polynomial_identity_for_class(a=7, M=840, r=121, k0=1)
    assert res7 is not None
    assert res7["verified_algebraic"] is True
    assert res7["strictly_ordered"] is True


def test_p147_database_and_soundness() -> None:
    """Test soundness verification and error detection for P147 baseline audit."""
    from evobyte.algebraic import (
        synthesize_schinzel_polynomial_database,
        verify_schinzel_polynomial_identity_synthesis_baseline_soundness,
    )

    db = synthesize_schinzel_polynomial_database(max_classes_per_pair=2)
    assert db["total_synthesized"] >= 20
    assert db["all_algebraic_valid"] is True
    assert db["all_strictly_ordered"] is True

    sound, findings = verify_schinzel_polynomial_identity_synthesis_baseline_soundness(
        db, min_identities=20
    )
    assert sound is True
    assert findings == []

    # Test error detection
    corrupted_alg = dict(db)
    corrupted_alg["all_algebraic_valid"] = False
    s_alg, f_alg = verify_schinzel_polynomial_identity_synthesis_baseline_soundness(corrupted_alg)
    assert s_alg is False
    assert any("INVALID_ALGEBRAIC_IDENTITIES" in f for f in f_alg)

    corrupted_ord = dict(db)
    corrupted_ord["all_strictly_ordered"] = False
    s_ord, f_ord = verify_schinzel_polynomial_identity_synthesis_baseline_soundness(corrupted_ord)
    assert s_ord is False
    assert any("DEGENERATE_OR_DISORDERED_POLYNOMIALS" in f for f in f_ord)

    corrupted_count = dict(db)
    corrupted_count["total_synthesized"] = 5
    s_cnt, f_cnt = verify_schinzel_polynomial_identity_synthesis_baseline_soundness(
        corrupted_count, min_identities=20
    )
    assert s_cnt is False
    assert any("INSUFFICIENT_IDENTITIES" in f for f in f_cnt)


def test_p147_acceptance_rejects_wrong_phase(tmp_path: Path) -> None:
    """Test that P147 audit rejects invalid configuration phase."""
    import sys

    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root / "benchmarks") not in sys.path:
        sys.path.insert(0, str(repo_root / "benchmarks"))
    from benchmarks.science_matrix import run_p147_polynomial_identity_synthesis_audit

    cfg_p = tmp_path / "bad-p147.json"
    cfg_p.write_text(json.dumps({"phase": "INVALID"}))
    with pytest.raises(ValueError, match="not a P147 configuration"):
        run_p147_polynomial_identity_synthesis_audit(cfg_p, tmp_path / "out.json")


def test_p147_audit_smoke(tmp_path: Path) -> None:
    """Test smoke run of P147 audit on valid config."""
    import sys

    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root / "benchmarks") not in sys.path:
        sys.path.insert(0, str(repo_root / "benchmarks"))
    from benchmarks.science_matrix import run_p147_polynomial_identity_synthesis_audit

    cfg_file = repo_root / "experiments/p147-config.json"
    with open(cfg_file, encoding="utf-8") as f:
        cfg_data = json.load(f)
    cfg_data["max_classes_per_pair"] = 1
    cfg_data["min_identities"] = 5
    cfg_data["expected_checksum"] = None
    cfg_data["allow_dirty"] = True

    tmp_cfg = tmp_path / "p147-smoke-config.json"
    tmp_cfg.write_text(json.dumps(cfg_data))
    out_file = tmp_path / "p147-smoke-out.json"

    report = run_p147_polynomial_identity_synthesis_audit(tmp_cfg, out_file)
    assert report["phase"] == "P147"
    assert report["total_synthesized"] >= 5
    assert report["all_algebraic_valid"] is True
    assert report["all_strictly_ordered"] is True
    assert out_file.exists()


def test_p148_compiler_and_theorems() -> None:
    """Test synthesis and compilation of P148 Lean 4 module."""
    from evobyte.formal_bridge import compile_schinzel_high_moduli_theorems_module

    res = compile_schinzel_high_moduli_theorems_module(max_classes_per_pair=5)
    assert res["total_theorems"] >= 100
    assert res["has_sorry"] is False
    assert Path(res["path"]).exists()


def test_p148_soundness_and_lake() -> None:
    """Test soundness verification and error detection for P148 certification baseline audit."""
    from evobyte.formal_bridge import (
        audit_schinzel_high_moduli_certification_baseline,
        verify_schinzel_high_moduli_certification_baseline_soundness,
    )

    audit_res = audit_schinzel_high_moduli_certification_baseline(verify_lake=False)
    assert audit_res["total_theorems"] >= 100
    assert audit_res["has_sorry"] is False

    sound, findings = verify_schinzel_high_moduli_certification_baseline_soundness(audit_res, min_theorems=100)
    assert sound is True
    assert findings == []

    # Test error detection
    corrupted = dict(audit_res)
    corrupted["has_sorry"] = True
    s, f = verify_schinzel_high_moduli_certification_baseline_soundness(corrupted)
    assert s is False
    assert any("SORRY_DETECTED" in x for x in f)

    corrupted_thms = dict(audit_res)
    corrupted_thms["total_theorems"] = 10
    s_thms, f_thms = verify_schinzel_high_moduli_certification_baseline_soundness(corrupted_thms, min_theorems=100)
    assert s_thms is False
    assert any("INSUFFICIENT_THEOREMS" in x for x in f_thms)

    corrupted_lake = dict(audit_res)
    corrupted_lake["lake_passed"] = False
    s_lake, f_lake = verify_schinzel_high_moduli_certification_baseline_soundness(corrupted_lake)
    assert s_lake is False
    assert any("LAKE_BUILD_FAILED" in x for x in f_lake)


def test_p148_acceptance_rejects_wrong_phase(tmp_path: Path) -> None:
    """Test that P148 audit rejects invalid configuration phase."""
    import sys

    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root / "benchmarks") not in sys.path:
        sys.path.insert(0, str(repo_root / "benchmarks"))
    from benchmarks.science_matrix import run_p148_schinzel_lean4_certification_audit

    cfg_p = tmp_path / "bad-p148.json"
    cfg_p.write_text(json.dumps({"phase": "INVALID"}))
    with pytest.raises(ValueError, match="not a P148 configuration"):
        run_p148_schinzel_lean4_certification_audit(cfg_p, tmp_path / "out.json")


def test_p148_audit_smoke(tmp_path: Path) -> None:
    """Test smoke run of P148 audit on valid config."""
    import sys

    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root / "benchmarks") not in sys.path:
        sys.path.insert(0, str(repo_root / "benchmarks"))
    from benchmarks.science_matrix import run_p148_schinzel_lean4_certification_audit

    cfg_file = repo_root / "experiments/p148-config.json"
    with open(cfg_file, encoding="utf-8") as f:
        cfg_data = json.load(f)
    cfg_data["verify_lake"] = False
    cfg_data["allow_dirty"] = True

    tmp_cfg = tmp_path / "p148-smoke-config.json"
    tmp_cfg.write_text(json.dumps(cfg_data))
    out_file = tmp_path / "p148-smoke-out.json"

    report = run_p148_schinzel_lean4_certification_audit(tmp_cfg, out_file)
    assert report["phase"] == "P148"
    assert report["total_theorems"] >= 100
    assert report["has_sorry"] is False
    assert out_file.exists()
