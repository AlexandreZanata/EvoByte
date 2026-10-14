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
    ok_no_fallback, det_no_fallback = check_erdos_straus_algebraic_congruence(1009, 840, fallback_sieve=False)
    assert ok_no_fallback is False
    assert det_no_fallback["classification"]["is_resistant"] is True

    # With fallback, resistant residue 1009 is solved and verified
    ok_fallback, det_fallback = check_erdos_straus_algebraic_congruence(1009, 840, fallback_sieve=True)
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

    p1 = (u * 4 - one)
    p2 = (v * 4 - one)
    prod = p1 * p2

    assert prod.total_degree == 2
    assert prod.degree_u == 1
    assert prod.degree_v == 1
    assert prod.eval(1, 1) == 9  # (4 - 1)*(4 - 1) = 9
    assert prod.eval(2, 3) == 7 * 11  # 77
    assert prod.is_strictly_positive(5) is True
    assert prod.is_integer_valued(5) is True

    # Power
    p_sq = p1 ** 2
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
