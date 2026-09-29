"""VM conformance tests (P02 gate). Oracle vectors, no GPU/network."""

import numpy as np

from evobyte.bytecode import encode_instr, nop_program
from evobyte.vm import execute, execute_batch


def _prog_single(op, a=0, b=0):
    p = nop_program()
    p[0] = encode_instr(op, dst=7, a=a, b=b)
    return p


def test_all_ops_finite_on_edges():
    edges = np.array([0.0, 1.0, -1.0, 1e-12, -1e-12, 1e20, -1e20, 3.14], dtype=np.float32)
    for op in [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F]:
        prog = _prog_single(op, a=0, b=1 if op not in (0x0F,) else 5)
        # x1 (r1) defaults to 0; exercise via x1 for two-operand ops
        for x in edges:
            y, _bad = execute(prog, np.float32(x), np.float32(2.0))
            assert np.isfinite(y), f"op {op:#x} escaped non-finite on x={x}"


def test_nan_inf_inputs_never_escape():
    prog = _prog_single(0x01)
    for bad in [np.float32(np.inf), np.float32(-np.inf), np.float32(np.nan)]:
        y, flag = execute(prog, bad, bad)
        assert np.isfinite(y)


def test_x_plus_one():
    # r7 = r0 + 1 via CSEL bank index 1
    p = nop_program()
    p[0] = encode_instr(0x0F, dst=7, a=0, b=1)
    pred, _ = execute_batch(p, np.array([1.0, 2.0, -5.0], dtype=np.float32))
    np.testing.assert_allclose(pred, [2.0, 3.0, -4.0], rtol=1e-6)


def test_div_by_zero_flagged_not_nan():
    p = nop_program()
    p[0] = encode_instr(0x04, dst=7, a=0, b=1)  # r0 / r1, r1 = 0
    y, bad = execute(p, np.float32(5.0), np.float32(0.0))
    assert bad is True
    assert y == np.float32(0.0)
