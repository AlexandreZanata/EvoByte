"""VM conformance tests (P02 gate). Oracle vectors, no GPU/network."""

import numpy as np

from evobyte.bytecode import encode_instr, nop_program
from evobyte.vm import CLAMP, execute, execute_batch


def _prog_single(op, a=0, b=0):
    p = nop_program()
    p[0] = encode_instr(op, dst=7, a=a, b=b)
    return p


def test_all_ops_finite_on_edges():
    edges = np.array(
        [
            0.0,
            -0.0,
            1.0,
            -1.0,
            1e-12,
            -1e-12,
            1e-30,
            -1e-30,
            1e-38,
            1e-40,
            1e20,
            -1e20,
            1e30,
            -1e30,
            1e38,
            -1e38,
            3.14159,
            float("inf"),
            float("-inf"),
            float("nan"),
        ],
        dtype=np.float32,
    )
    for op in range(0x10):
        prog = _prog_single(op, a=0, b=1 if op not in (0x0F,) else 5)
        for x in edges:
            y, bad = execute(prog, np.float32(x), np.float32(2.0))
            assert np.isfinite(y), f"op {op:#x} escaped non-finite on x={x}: {y}"
            assert isinstance(bad, (bool, np.bool_))
            assert abs(y) <= CLAMP


def test_nan_inf_inputs_never_escape():
    for op in [0x01, 0x03, 0x04, 0x05, 0x07, 0x08, 0x09, 0x0F]:
        prog = _prog_single(op, a=0, b=1)
        for bad_val in [np.float32(np.inf), np.float32(-np.inf), np.float32(np.nan)]:
            y, flag = execute(prog, bad_val, bad_val)
            assert np.isfinite(y), f"escaped non-finite for op {op:#x} on input {bad_val}"
            assert flag is True


def test_x_plus_one():
    # r7 = r0 + 1 via CSEL bank index 1
    p = nop_program()
    p[0] = encode_instr(0x0F, dst=7, a=0, b=1)
    pred, flags = execute_batch(p, np.array([1.0, 2.0, -5.0], dtype=np.float32))
    np.testing.assert_allclose(pred, [2.0, 3.0, -4.0], rtol=1e-6)
    assert not np.any(flags)


def test_quadratic_end_to_end():
    # y = x^2 + 3x + 7
    # r0 = x, r1 = 0 (zero-init)
    # CONST_BANK[11] == 3.0, CONST_BANK[10] == 7.0
    p = nop_program()
    p[0] = encode_instr(0x0F, dst=3, a=1, b=11)  # r3 = r1 + 3.0 = 3.0
    p[1] = encode_instr(0x03, dst=3, a=3, b=0)  # r3 = r3 * r0 = 3x
    p[2] = encode_instr(0x03, dst=2, a=0, b=0)  # r2 = r0 * r0 = x^2
    p[3] = encode_instr(0x01, dst=4, a=2, b=3)  # r4 = r2 + r3 = x^2 + 3x
    p[4] = encode_instr(0x0F, dst=7, a=4, b=10)  # r7 = r4 + 7.0 = x^2 + 3x + 7

    xs = np.array([-5.0, -3.0, -1.0, 0.0, 1.0, 2.0, 5.0], dtype=np.float32)
    expected = xs**2 + 3 * xs + 7
    preds, flags = execute_batch(p, xs)
    np.testing.assert_allclose(preds, expected, rtol=1e-6)
    assert not np.any(flags)


def test_div_by_zero_flagged_not_nan():
    p = nop_program()
    p[0] = encode_instr(0x04, dst=7, a=0, b=1)  # r0 / r1, r1 = 0
    y, bad = execute(p, np.float32(5.0), np.float32(0.0))
    assert bad is True
    assert y == np.float32(0.0)


def test_log_near_zero_flagged():
    p = _prog_single(0x08, a=0)  # LOG(|r0|)
    y, bad = execute(p, np.float32(1e-15))
    assert bad is True
    assert y == np.float32(0.0)


def test_exp_domain_guard():
    p = _prog_single(0x07, a=0)  # EXP(r0)
    # Outside [-20, 20]
    y_hi, bad_hi = execute(p, np.float32(25.0))
    assert bad_hi is True
    assert y_hi == np.float32(0.0)

    y_lo, bad_lo = execute(p, np.float32(-25.0))
    assert bad_lo is True
    assert y_lo == np.float32(0.0)

    # In range
    y_norm, bad_norm = execute(p, np.float32(0.0))
    assert bad_norm is False
    np.testing.assert_allclose(y_norm, 1.0, rtol=1e-6)


def test_pow_domain_guard():
    p = _prog_single(0x09, a=0, b=1)  # r0 ** r1
    # 0 ** -2 -> division by zero
    y, bad = execute(p, np.float32(0.0), np.float32(-2.0))
    assert bad is True
    assert np.isfinite(y)


def test_clamp_and_flush():
    # Overflow clamp
    p_add = _prog_single(0x01, a=0, b=1)
    y_clamped, bad_clamp = execute(p_add, np.float32(1e30), np.float32(1e30))
    assert bad_clamp is True
    assert y_clamped == np.float32(1e30)

    # Subnormal flush to 0.0
    p_mul = _prog_single(0x03, a=0, b=1)
    y_flush, _ = execute(p_mul, np.float32(1e-20), np.float32(1e-20))
    assert y_flush == np.float32(0.0)


def test_determinism():
    p = nop_program()
    p[0] = encode_instr(0x05, dst=2, a=0, b=0)  # sin(x)
    p[1] = encode_instr(0x07, dst=3, a=2, b=0)  # exp(sin(x))
    p[2] = encode_instr(0x01, dst=7, a=3, b=0)  # exp(sin(x)) + x

    xs = np.linspace(-3.0, 3.0, 50, dtype=np.float32)
    pred1, flag1 = execute_batch(p, xs)
    for _ in range(5):
        pred2, flag2 = execute_batch(p, xs)
        assert np.array_equal(pred1, pred2)
        assert np.array_equal(flag1, flag2)


def test_execute_batch_with_two_inputs():
    p = nop_program()
    p[0] = encode_instr(0x01, dst=7, a=0, b=1)  # r7 = r0 + r1
    xs = np.array([1.0, 2.0, 3.0], dtype=np.float32)
    x1s = np.array([10.0, 20.0, 30.0], dtype=np.float32)
    preds, flags = execute_batch(p, xs, x1s)
    np.testing.assert_allclose(preds, [11.0, 22.0, 33.0], rtol=1e-6)
    assert not np.any(flags)


def test_fuzz_1k_random_programs_no_nan_inf():
    rng = np.random.default_rng(42)
    edge_inputs = np.array(
        [-1e35, -1e20, -1.0, -1e-13, 0.0, 1e-13, 1.0, 1e20, 1e35, np.nan, np.inf, -np.inf],
        dtype=np.float32,
    )
    for _ in range(1000):
        # Generate arbitrary 16-instr program from random uint32 words
        prog = rng.integers(0, 2**32, size=16, dtype=np.uint64).astype(np.uint32)
        for x in edge_inputs:
            y, bad = execute(prog, x, np.float32(1.5))
            assert np.isfinite(y), f"escaped non-finite on random program with input {x}: {y}"
            assert isinstance(bad, (bool, np.bool_))
            assert abs(y) <= CLAMP


def test_f64_execution_accuracy():
    from evobyte.vm import CLAMP_F64, execute_batch_f64, execute_f64

    # r7 = r0 + r1
    p = nop_program()
    p[0] = encode_instr(0x01, dst=7, a=0, b=1)

    y, flag = execute_f64(p, 1e-15, 1e-15)
    assert isinstance(y, (float, np.float64))
    np.testing.assert_allclose(y, 2e-15, rtol=1e-12)
    assert not flag

    # Batch f64
    xs = np.array([1e-12, 1.0, 1e12], dtype=np.float64)
    preds, flags = execute_batch_f64(p, xs)
    np.testing.assert_allclose(preds, xs, rtol=1e-12)
    assert not np.any(flags)

    # Large values within float64 clamp
    p_exp = nop_program()
    p_exp[0] = encode_instr(0x07, dst=7, a=0, b=0)  # exp(x)
    y_large, flag_large = execute_f64(
        p_exp, 50.0
    )  # exp(50) ~ 5.18e21 (escaped float32, valid in f64)
    assert np.isfinite(y_large)
    assert abs(y_large) <= CLAMP_F64
    assert not flag_large
