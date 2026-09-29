"""Unit tests for P14 scientific dataset specifications and Domain L2 verification."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "benchmarks"))

from benchmarks.science_matrix import (
    PREREGISTERED_SCIENCE_SPECS,
    check_adversarial_domain,
    check_non_degeneracy,
    check_units_scaling,
    compute_r2,
    generate_scientific_splits,
    run_science_matrix,
    verify_scientific_candidate_l2,
)
from evobyte.bytecode import encode_instr, nop_program


def test_preregistered_specs():
    assert len(PREREGISTERED_SCIENCE_SPECS) >= 5
    keys = [s.key for s in PREREGISTERED_SCIENCE_SPECS]
    assert "kepler_third_law" in keys
    assert "boyle_gas_law" in keys
    assert "stefan_boltzmann" in keys
    assert "michaelis_menten" in keys
    assert "lorentz_factor" in keys

    for s in PREREGISTERED_SCIENCE_SPECS:
        assert len(s.name) > 0
        assert len(s.license_name) > 0
        assert len(s.input_unit) > 0
        assert len(s.output_unit) > 0
        assert s.train_range[0] < s.train_range[1]
        assert s.extrap_range[0] < s.extrap_range[1]
        assert s.r2_threshold > 0.90


def test_generate_scientific_splits():
    spec = PREREGISTERED_SCIENCE_SPECS[0]
    splits, h = generate_scientific_splits(spec, n_points=32)
    assert len(h) == 16
    for k in ("train", "val", "hidden", "extrapolation"):
        xs, ys = splits[k]
        assert len(xs) == 32
        assert len(ys) == 32
        assert np.all(np.isfinite(xs))
        assert np.all(np.isfinite(ys))

    # Verify deterministic hash
    _, h2 = generate_scientific_splits(spec, n_points=32)
    assert h == h2


def test_compute_r2():
    y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0], dtype=np.float64)
    assert abs(compute_r2(y_true, y_true) - 1.0) < 1e-9

    y_pred_bad = np.array([10.0, 10.0, 10.0, 10.0, 10.0], dtype=np.float64)
    assert compute_r2(y_true, y_pred_bad) < 0.1


def test_check_non_degeneracy_constant_guard():
    # Program that outputs a constant (e.g. always 5.0 in r7 from r2=0 + bank[12]=5.0)
    prog = nop_program()
    prog[0] = encode_instr(0x0F, dst=7, a=2, b=12)  # CSEL r7 = r2(0.0) + const[12](5.0)

    xs_probe = np.linspace(1.0, 10.0, 50, dtype=np.float32)
    ok, reasons = check_non_degeneracy(prog, xs_probe)
    assert ok is False
    assert any("Constant-only" in r for r in reasons)


def test_check_units_scaling():
    # Construct candidate that computes y = x^1.5 = x * sqrt(x)
    prog = nop_program()
    prog[0] = encode_instr(0x0B, dst=1, a=0, b=0)  # SQRT r1 = sqrt(x)
    prog[1] = encode_instr(0x03, dst=7, a=0, b=1)  # MUL r7 = x * sqrt(x)

    ok, exp = check_units_scaling(prog, base_x=4.0, expected_exponent=1.5)
    assert ok is True
    assert exp is not None
    assert abs(exp - 1.5) < 0.05

    # Fail check if expected exponent doesn't match
    ok_fail, _ = check_units_scaling(prog, base_x=4.0, expected_exponent=2.0)
    assert ok_fail is False


def test_check_adversarial_domain():
    prog = nop_program()
    prog[0] = encode_instr(0x04, dst=7, a=0, b=0)  # DIV r7 = x / x

    ok, _ = check_adversarial_domain(prog, [0.01, 1.0, 100.0])
    assert ok is True


def test_verify_scientific_candidate_l2_kepler():
    spec = next(s for s in PREREGISTERED_SCIENCE_SPECS if s.key == "kepler_third_law")
    splits, _ = generate_scientific_splits(spec, n_points=64)

    # Exact Kepler program: r1 = sqrt(x), r7 = x * r1
    prog = nop_program()
    prog[0] = encode_instr(0x0B, dst=1, a=0, b=0)  # SQRT r1 = sqrt(x)
    prog[1] = encode_instr(0x03, dst=7, a=0, b=1)  # MUL r7 = x * sqrt(x)

    res = verify_scientific_candidate_l2(prog, spec, splits)
    assert res.status == "SUPPORTED"
    assert res.train_r2 > 0.999
    assert res.hidden_r2 > 0.999
    assert res.extrapolation_passed is True
    assert res.units_scaling_passed is True
    assert res.adversarial_passed is True
    assert res.non_degenerate is True
    assert len(res.failure_reasons) == 0


def test_science_matrix_smoke():
    res = run_science_matrix(preregistered_only=True, seeds=[42], max_trial_sec=0.5)
    assert res["status"] == "PASS"
    assert len(res["datasets"]) >= 5
