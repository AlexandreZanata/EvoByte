"""Unit tests for Level-2 strict verification, float64 execution, and discovery evidence (P19)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from evobyte.archive import EliteArchive, write_hall_of_fame_entry
from evobyte.bytecode import CONST_BANK, encode_instr, nop_program
from evobyte.constants import TunableProgram
from evobyte.verifier import (
    check_ordinary_math,
    check_symbolic_equivalence,
    export_reproducible_candidate,
    program_to_sympy,
    reproduce_candidate,
    verify_l2,
)


def _build_exact_quadratic_program() -> np.ndarray:
    """Build exact y = x^2 + 3x + 7 program."""
    p = nop_program()
    p[0] = encode_instr(0x0F, dst=3, a=1, b=11)  # r3 = r1 + 3.0 = 3.0
    p[1] = encode_instr(0x03, dst=3, a=3, b=0)  # r3 = r3 * r0 = 3x
    p[2] = encode_instr(0x03, dst=2, a=0, b=0)  # r2 = r0 * r0 = x^2
    p[3] = encode_instr(0x01, dst=4, a=2, b=3)  # r4 = r2 + r3 = x^2 + 3x
    p[4] = encode_instr(0x0F, dst=7, a=4, b=10)  # r7 = r4 + 7.0 = x^2 + 3x + 7
    return p


def test_ordinary_math_valid_polynomial():
    prog = _build_exact_quadratic_program()
    xs = np.linspace(-10.0, 10.0, 100, dtype=np.float64)
    valid, err = check_ordinary_math(prog, xs)
    assert valid is True
    assert err is None


def test_ordinary_math_catches_div_zero():
    # Program: r7 = r0 / r0 (fails at x=0 in ordinary math)
    p = nop_program()
    p[0] = encode_instr(0x04, dst=7, a=0, b=0)
    xs = np.array([-1.0, 0.0, 1.0], dtype=np.float64)
    valid, err = check_ordinary_math(p, xs)
    assert valid is False
    assert err is not None
    assert "Singularity: division by near-zero" in err


def test_ordinary_math_catches_negative_sqrt():
    # Program: r7 = sqrt(r0) (fails on negative x in ordinary math)
    p = nop_program()
    p[0] = encode_instr(0x0B, dst=7, a=0, b=0)
    xs = np.array([1.0, 2.0, -0.5], dtype=np.float64)
    valid, err = check_ordinary_math(p, xs)
    assert valid is False
    assert err is not None
    assert "Domain violation: sqrt of negative" in err


def test_program_to_sympy_and_equivalence():
    prog = _build_exact_quadratic_program()
    sym_expr = program_to_sympy(prog)
    assert sym_expr is not None

    eq, detail = check_symbolic_equivalence(sym_expr, "x2_3x_7")
    assert eq is True
    assert detail == "exact_identity_unconditional"


def test_l2_verify_known_correct_program():
    prog = _build_exact_quadratic_program()

    # Generate disjoint splits
    train_xs = np.linspace(-10.0, 10.0, 64, dtype=np.float64)
    train_ys = train_xs**2 + 3 * train_xs + 7

    test_xs = np.linspace(-9.9, 9.9, 128, dtype=np.float64)
    test_ys = test_xs**2 + 3 * test_xs + 7

    extrap_xs = np.array([-50.0, -25.0, 25.0, 50.0], dtype=np.float64)
    extrap_ys = extrap_xs**2 + 3 * extrap_xs + 7

    adv_xs = np.array([-10.0, 0.0, 10.0, 1e-12, -1e-12], dtype=np.float64)

    res = verify_l2(
        program=prog,
        train_xs=train_xs,
        train_ys=train_ys,
        test_xs=test_xs,
        test_ys=test_ys,
        extrap_xs=extrap_xs,
        extrap_ys=extrap_ys,
        adversarial_xs=adv_xs,
        ground_truth_formula="x2_3x_7",
    )

    assert res.passed is True
    assert res.decision == "VERIFIED_DISCOVERY"
    assert res.f64_test_mse < 1e-12
    assert res.f32_test_mse < 1e-10
    assert res.f64_f32_divergence < 1e-10
    assert res.symbolic_equivalent is True
    assert res.proof_type == "exact_certificate"
    assert res.ordinary_math_valid is True
    assert res.adversarial_invalid_rate == 0.0


def test_l2_verify_deliberate_overfit_rejected():
    # Construct an overfit: outputs 7.0 for small x, but diverges elsewhere
    # e.g., constant 7.0
    p_overfit = nop_program()
    p_overfit[0] = encode_instr(0x0F, dst=7, a=1, b=10)  # r7 = 7.0

    # On train points x ~ 0, error is small:
    train_xs = np.array([-0.05, 0.0, 0.05], dtype=np.float64)
    train_ys = train_xs**2 + 3 * train_xs + 7  # ~ 7.0

    # On test points, target varies widely from 7:
    test_xs = np.linspace(-10.0, 10.0, 50, dtype=np.float64)
    test_ys = test_xs**2 + 3 * test_xs + 7

    extrap_xs = np.array([-40.0, 40.0], dtype=np.float64)
    extrap_ys = extrap_xs**2 + 3 * extrap_xs + 7

    res = verify_l2(
        program=p_overfit,
        train_xs=train_xs,
        train_ys=train_ys,
        test_xs=test_xs,
        test_ys=test_ys,
        extrap_xs=extrap_xs,
        extrap_ys=extrap_ys,
        ground_truth_formula="x2_3x_7",
    )

    assert res.passed is False
    assert "REJECTED" in res.decision
    assert any(
        r in res.reasons
        for r in (
            "overfit_memorization",
            "test_error_exceeds_threshold",
            "extrapolation_divergence",
        )
    )


def test_l2_verify_protected_exploit_rejected():
    # Program that divides by (x - 2.0), protected VM sets to 0.0 at x=2.0
    # CONST_BANK[3] == 2.0
    p = nop_program()
    p[0] = encode_instr(0x02, dst=2, a=0, b=1)  # r2 = x - 0
    p[1] = encode_instr(0x0F, dst=3, a=1, b=3)  # r3 = 2.0
    p[2] = encode_instr(0x02, dst=4, a=0, b=3)  # r4 = x - 2.0
    p[3] = encode_instr(0x04, dst=7, a=0, b=4)  # r7 = x / (x - 2.0)

    train_xs = np.array([-1.0, 1.0, 3.0], dtype=np.float64)
    train_ys = train_xs**2 + 3 * train_xs + 7

    test_xs = np.array([2.0, 4.0], dtype=np.float64)  # includes singularity at x=2.0
    test_ys = test_xs**2 + 3 * test_xs + 7

    res = verify_l2(
        program=p,
        train_xs=train_xs,
        train_ys=train_ys,
        test_xs=test_xs,
        test_ys=test_ys,
        ground_truth_formula="x2_3x_7",
    )

    assert res.passed is False
    assert "protected_domain_exploit" in res.reasons


def test_l2_verify_rounding_sensitive_rejected():
    # Program that exploits float32 truncation:
    # In float32, ((2^24 + x) - 2^24) == 0.0 for x in [-0.4, 0.4]
    # But in float64, it equals x.
    # We craft a candidate that adds 10 * ((2^24 + x) - 2^24) to the target formula.
    # In float32: error is 0.
    # In float64: error is 100 * x^2, which fails!
    custom_bank = CONST_BANK.copy().astype(np.float64)
    custom_bank[15] = 16777216.0  # 2^24

    # Build program:
    # r3 = r0 + c (via CSEL b=15)
    # r4 = r3 - c (via CSEL + NEG or SUB)
    # r5 = r4 * 10.0 (where 10.0 from CONST_BANK)
    # r7 = (x^2 + 3x + 7) + r5
    p = _build_exact_quadratic_program()
    # Now modify p[5..10]
    p[5] = encode_instr(0x0F, dst=2, a=0, b=15)  # r2 = x + 2^24
    p[6] = encode_instr(0x0F, dst=3, a=1, b=15)  # r3 = 2^24
    p[7] = encode_instr(0x02, dst=5, a=2, b=3)  # r5 = (x + 2^24) - 2^24
    p[8] = encode_instr(0x03, dst=5, a=5, b=5)  # r5 = r5^2
    p[9] = encode_instr(0x01, dst=7, a=7, b=5)  # r7 = r7 + r5

    xs = np.linspace(-0.4, 0.4, 30, dtype=np.float64)
    ys = xs**2 + 3 * xs + 7

    res = verify_l2(
        program=p,
        train_xs=xs,
        train_ys=ys,
        test_xs=xs,
        test_ys=ys,
        constants=custom_bank,
        ground_truth_formula="x2_3x_7",
    )

    assert res.passed is False
    assert "float_precision_divergence" in res.reasons


def test_archive_null_for_unmeasured_errors(tmp_path: Path):
    db_file = tmp_path / "elites_p19.db"
    archive = EliteArchive(db_file)

    prog = _build_exact_quadratic_program()
    # Insert provisional elite with no test/val error
    ins = archive.add_elite(
        program=prog,
        generation=1,
        fitness=0.01,
        train_error=0.01,
        validation_error=None,
        test_error=None,
        status="provisional",
        domain="[-10, 10]",
    )
    assert ins is True

    sha = export_reproducible_candidate(prog)["sha256"]
    row = archive.get_by_hash(sha)
    assert row is not None
    assert row["validation_error"] is None  # True NULL, not 0.0!
    assert row["test_error"] is None  # True NULL, not 0.0!
    assert row["status"] == "provisional"
    assert row["verifier_outcome"] == "unverified"

    # Update verification
    updated = archive.update_verification(
        sha256=sha,
        test_error=1.5e-12,
        extrapolation_error=3.0e-11,
        verifier_outcome="verified_discovery",
        status="confirmed",
    )
    assert updated is True

    row_up = archive.get_by_hash(sha)
    assert row_up["status"] == "confirmed"
    assert row_up["test_error"] == pytest.approx(1.5e-12)
    assert row_up["extrapolation_error"] == pytest.approx(3.0e-11)
    assert row_up["verifier_outcome"] == "verified_discovery"
    archive.close()


def test_hall_of_fame_requires_strict_evidence(tmp_path: Path):
    fame_file = tmp_path / "fame_strict.jsonl"

    # 1. Provisional elite without test/extrap error -> rejected in strict mode
    entry_provisional = {
        "rank": 1,
        "fitness": 0.01,
        "expression": "x^2 + 3x + 7",
        "generation": 1,
        "train_error": 0.0,
        "status": "provisional",
    }
    assert (
        write_hall_of_fame_entry(fame_file, entry_provisional, require_strict_evidence=True)
        is False
    )

    # 2. Candidate with test error but no extrapolation -> rejected
    entry_no_extrap = {
        "rank": 1,
        "fitness": 0.01,
        "expression": "x^2 + 3x + 7",
        "generation": 1,
        "train_error": 0.0,
        "test_error": 1e-12,
        "status": "confirmed",
    }
    assert (
        write_hall_of_fame_entry(fame_file, entry_no_extrap, require_strict_evidence=True) is False
    )

    # 3. Confirmed discovery with test and extrapolation evidence -> accepted!
    entry_confirmed = {
        "rank": 1,
        "fitness": 0.001,
        "expression": "x^2 + 3x + 7",
        "generation": 10,
        "train_error": 0.0,
        "validation_error": 1e-12,
        "test_error": 1e-12,
        "extrapolation_error": 2e-11,
        "status": "confirmed",
        "verifier_outcome": "verified_discovery",
    }
    assert (
        write_hall_of_fame_entry(fame_file, entry_confirmed, require_strict_evidence=True) is True
    )
    assert fame_file.exists()
    with open(fame_file, "r", encoding="utf-8") as f:
        line = f.readline()
    record = json.loads(line)
    assert record["test_error"] == pytest.approx(1e-12)
    assert record["extrapolation_error"] == pytest.approx(2e-11)
    assert record["status"] == "confirmed"


def test_exported_candidate_reproduction():
    prog = _build_exact_quadratic_program()
    xs = np.linspace(-5.0, 5.0, 50, dtype=np.float64)
    expected = xs**2 + 3 * xs + 7

    export_dict = export_reproducible_candidate(
        program=prog,
        linear_head=(1.0, 0.0),
        domain="[-5, 5]",
        recorded_predictions=expected,
        recorded_mse=0.0,
        verifier_outcome="VERIFIED_DISCOVERY",
    )

    reproduced = reproduce_candidate(export_dict, xs)
    np.testing.assert_allclose(reproduced, expected, rtol=1e-12)
    np.testing.assert_allclose(reproduced, export_dict["recorded_predictions"], rtol=1e-12)


def test_tunable_program_execute_f64():
    prog = _build_exact_quadratic_program()
    tunable = TunableProgram(prog)
    tunable.linear_head = (2.0, 5.0)

    xs = np.array([1.0, 2.0, 3.0], dtype=np.float64)
    base = xs**2 + 3 * xs + 7
    expected = 2.0 * base + 5.0

    preds, flags = tunable.execute_f64(xs)
    np.testing.assert_allclose(preds, expected, rtol=1e-12)
    assert not np.any(flags)


def _build_coincident_false_program() -> np.ndarray:
    """x^2 + 3x + 7 + 1e-12*x^8: train-coincident, symbolically distinct."""
    p = nop_program()
    p[0] = encode_instr(0x0F, dst=5, a=1, b=15)  # r5 = 0.001
    p[1] = encode_instr(0x03, dst=5, a=5, b=5)  # r5 = 1e-6
    p[2] = encode_instr(0x03, dst=6, a=5, b=5)  # r6 = 1e-12
    p[3] = encode_instr(0x03, dst=2, a=0, b=0)  # r2 = x^2
    p[4] = encode_instr(0x03, dst=4, a=2, b=2)  # r4 = x^4
    p[5] = encode_instr(0x03, dst=4, a=4, b=4)  # r4 = x^8
    p[6] = encode_instr(0x03, dst=6, a=6, b=4)  # r6 = 1e-12 * x^8
    p[7] = encode_instr(0x0F, dst=3, a=1, b=11)  # r3 = 3.0
    p[8] = encode_instr(0x03, dst=3, a=3, b=0)  # r3 = 3x
    p[9] = encode_instr(0x01, dst=5, a=2, b=3)  # r5 = x^2 + 3x
    p[10] = encode_instr(0x0F, dst=7, a=5, b=10)  # r7 = x^2 + 3x + 7
    p[11] = encode_instr(0x01, dst=7, a=7, b=6)  # r7 += 1e-12 * x^8
    return p


def test_p42_true_identity_unified_symbols() -> None:
    from evobyte.grammar import HornerPoly, compile_horner_to_bytecode

    prog, _ = compile_horner_to_bytecode(HornerPoly(coeff_indices=[1, 0, 2]))
    prog = np.asarray(prog, dtype=np.uint32)
    sym_expr = program_to_sympy(prog)
    # String ground truth parses with plain symbols; unified hypotheses must still match.
    eq, detail = check_symbolic_equivalence(sym_expr, "x**2 - 1")
    assert eq is True
    assert detail == "exact_identity_unconditional"
    eq_dom, detail_dom = check_symbolic_equivalence(sym_expr, "x**2 - 1", domain=(-3.0, 3.0))
    assert eq_dom is True
    assert "exact_identity_on_domain" in detail_dom


def test_p42_false_identity_coincident_on_train_rejected() -> None:
    prog = _build_coincident_false_program()
    train_xs = np.linspace(-3.0, 3.0, 48, dtype=np.float64)
    train_ys = train_xs**2 + 3 * train_xs + 7
    test_xs = np.linspace(-2.9, 2.9, 32, dtype=np.float64)
    test_ys = test_xs**2 + 3 * test_xs + 7
    extrap_xs = np.concatenate([np.linspace(-6.0, -3.5, 16), np.linspace(3.5, 6.0, 16)])
    extrap_ys = extrap_xs**2 + 3 * extrap_xs + 7
    res = verify_l2(
        program=prog,
        train_xs=train_xs,
        train_ys=train_ys,
        test_xs=test_xs,
        test_ys=test_ys,
        extrap_xs=extrap_xs,
        extrap_ys=extrap_ys,
        ground_truth_formula="x**2 + 3*x + 7",
        domain=(-3.0, 3.0),
    )
    assert res.train_mse < 1e-4
    assert res.symbolic_equivalent is False
    assert res.proof_type == "numerical_evidence"


def test_p42_symbol_hypothesis_mismatch_rejected() -> None:
    prog = _build_exact_quadratic_program()
    sym_expr = program_to_sympy(prog, var_name="y")
    eq, _ = check_symbolic_equivalence(sym_expr, "x**2 + 3*x + 7", var_name="x")
    assert eq is False


def test_p42_invalid_numeric_certificate_rejected() -> None:
    p = nop_program()
    p[0] = encode_instr(0x04, dst=7, a=0, b=0)  # r7 = x / x (invalid at x = 0)
    xs = np.array([-1.0, 0.0, 1.0], dtype=np.float64)
    res = verify_l2(
        program=p,
        train_xs=xs,
        train_ys=np.array([1.0, 1.0, 1.0]),
        test_xs=xs,
        test_ys=np.array([1.0, 1.0, 1.0]),
        ground_truth_formula="1",
    )
    assert res.passed is False
    assert res.symbolic_equivalent is False
    assert res.proof_type == "numerical_evidence"


def test_p42_pole_in_domain_rejected() -> None:
    import sympy as _sympy

    x = _sympy.Symbol("x", real=True)
    cand = (x**2 - 1) / (x - 1)
    eq, detail = check_symbolic_equivalence(cand, x + 1, domain=(-3.0, 3.0))
    assert eq is False
    assert "pole_in_domain" in detail
    eq_free, _ = check_symbolic_equivalence(cand, x + 1, domain=(2.0, 3.0))
    assert eq_free is True
