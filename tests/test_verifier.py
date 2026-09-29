"""Verifier tests (P04 gate, runnable already on the skeleton)."""

import numpy as np

from evobyte.bytecode import encode_instr, nop_program
from evobyte.verifier import cascade_evaluate, complexity, evaluate


def _x2_program():
    # r2 = r0*r0 ; r7 = r2 + 0  (shape check only; not exact target)
    p = nop_program()
    p[0] = encode_instr(0x03, dst=2, a=0, b=0)
    p[1] = encode_instr(0x01, dst=7, a=2, b=2)
    return p


def test_complexity_counts():
    p = nop_program()
    assert complexity(p) == 0.0
    assert complexity(_x2_program()) > 0.0


def test_evaluate_finite():
    xs = np.linspace(-2, 2, 64, dtype=np.float32)
    ys = xs * xs
    out = evaluate(_x2_program(), xs, ys)
    assert np.isfinite(out["fitness"])


def test_cascade_kills_bad_fast():
    rng = np.random.default_rng(0)
    xs = np.linspace(-10, 10, 512, dtype=np.float32)
    ys = xs * xs + 3 * xs + 7
    bad = nop_program()
    bad[0] = encode_instr(0x05, dst=7, a=0, b=0)  # sin(x) vs quadratic
    out = cascade_evaluate(bad, xs, ys, elite_err=1e-6, k=4.0)
    assert out["killed"] is True
    assert out["stage"] <= 2
