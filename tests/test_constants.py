"""Unit tests for constant optimization: tunable slots, local search, and linear head (P11)."""

from __future__ import annotations

import numpy as np
import pytest

from evobyte.bytecode import CONST_BANK, N_INSTR, encode_instr
from evobyte.constants import (
    ABSURD_CONSTANT_THRESHOLD,
    TunableProgram,
    evaluate_tunable,
    fit_constants_local_search,
    fit_linear_head,
    tune_promoted_candidate,
)


def test_tunable_program_bank_fallback() -> None:
    prog = np.zeros(N_INSTR, dtype=np.uint32)
    # CSEL r2 = r7 + CONST_BANK[5] (3.14159)
    prog[0] = encode_instr(0x0F, 2, 7, 5)
    # CSEL r3 = r7 + CONST_BANK[10] (7.0)
    prog[1] = encode_instr(0x0F, 3, 7, 10)
    # ADD r7 = r2 + r3
    prog[2] = encode_instr(0x01, 7, 2, 3)

    tunable = TunableProgram(prog)
    slots = tunable.get_slots()
    assert len(slots) == 2
    assert slots[0] == pytest.approx(CONST_BANK[5])
    assert slots[1] == pytest.approx(CONST_BANK[10])

    xs = np.linspace(-2.0, 2.0, 10, dtype=np.float32)
    preds_init, flags_init = tunable.execute(xs)
    assert not flags_init.any()
    assert np.allclose(preds_init, CONST_BANK[5] + CONST_BANK[10])

    # Now set custom slots
    tunable.set_slots(np.array([10.0, 20.0], dtype=np.float32))
    assert np.allclose(tunable.get_slots(), [10.0, 20.0])
    preds_new, flags_new = tunable.execute(xs)
    assert not flags_new.any()
    assert np.allclose(preds_new, 30.0)

    # Check decoded expression
    expr = tunable.decode_expression()
    assert "const=10" in expr
    assert "const=20" in expr


def test_fit_linear_head() -> None:
    # Program: y = x^2
    prog = np.zeros(N_INSTR, dtype=np.uint32)
    prog[0] = encode_instr(0x03, 7, 0, 0)  # MUL r7 = r0 * r0

    xs = np.linspace(-3.0, 3.0, 50, dtype=np.float32)
    # True target with linear scaling and bias: y = 2.5 * x^2 - 1.2
    ys = 2.5 * xs * xs - 1.2

    w1, w0, mse, steps = fit_linear_head(prog, xs, ys)
    assert w1 == pytest.approx(2.5, abs=1e-4)
    assert w0 == pytest.approx(-1.2, abs=1e-4)
    assert mse < 1e-6
    assert steps == 1


def test_local_search_on_tunable_slots() -> None:
    # Program: y = c0 * x
    prog = np.zeros(N_INSTR, dtype=np.uint32)
    # CSEL r2 = r7 + CONST_BANK[0] (0.0)
    prog[0] = encode_instr(0x0F, 2, 7, 0)
    # MUL r7 = r0 * r2
    prog[1] = encode_instr(0x03, 7, 0, 2)

    tunable = TunableProgram(prog)
    xs = np.linspace(-2.0, 2.0, 40, dtype=np.float32)
    # Target with non-bank constant 0.173
    ys = 0.173 * xs

    res = fit_constants_local_search(tunable, xs, ys, max_steps=60, initial_step=0.05)
    assert res["steps"] > 0
    assert res["time_sec"] > 0
    assert res["final_mse"] < res["initial_mse"]
    # Constant should be tuned very close to 0.173
    assert tunable.get_slots()[0] == pytest.approx(0.173, abs=0.02)


def test_absurd_constant_penalty() -> None:
    prog = np.zeros(N_INSTR, dtype=np.uint32)
    prog[0] = encode_instr(0x0F, 7, 7, 0)
    tunable = TunableProgram(prog)

    # Attempting to set absurd constant
    tunable.set_slots(np.array([ABSURD_CONSTANT_THRESHOLD * 2.0], dtype=np.float32))
    xs = np.linspace(-1.0, 1.0, 10, dtype=np.float32)
    ys = np.zeros_like(xs)

    res = fit_constants_local_search(tunable, xs, ys, max_steps=20)
    # Absurd constants rejected during search, candidate stays finite and <= ABSURD_CONSTANT_THRESHOLD
    assert np.all(np.abs(res["best_slots"]) <= ABSURD_CONSTANT_THRESHOLD)

    # Search toward a huge target must not exceed threshold
    prog2 = np.zeros(N_INSTR, dtype=np.uint32)
    prog2[0] = encode_instr(0x0F, 2, 7, 0)
    prog2[1] = encode_instr(0x03, 7, 0, 2)  # r7 = x * c
    tunable2 = TunableProgram(prog2)
    ys_huge = 1e9 * xs
    res2 = fit_constants_local_search(tunable2, xs, ys_huge, max_steps=40, initial_step=1e5)
    assert np.all(np.abs(res2["best_slots"]) <= ABSURD_CONSTANT_THRESHOLD)


def test_tune_promoted_candidate_hook() -> None:
    prog = np.zeros(N_INSTR, dtype=np.uint32)
    prog[0] = encode_instr(0x0F, 2, 7, 0)
    prog[1] = encode_instr(0x03, 7, 0, 2)

    xs = np.linspace(-2.0, 2.0, 32, dtype=np.float32)
    ys = 0.456 * xs + 0.123

    res = tune_promoted_candidate(prog, xs, ys, max_steps=40)
    assert "optimizer" in res
    assert "steps" in res
    assert "time_sec" in res
    assert res["final_mse"] <= res["initial_mse"]
    assert res["delta_mse"] >= 0.0


def test_tunable_program_duplicate_csel_remapping() -> None:
    # Program with two CSELs both referencing bank index 0
    prog = np.zeros(N_INSTR, dtype=np.uint32)
    prog[0] = encode_instr(0x0F, 2, 7, 0)  # CSEL r2 = const[0]
    prog[1] = encode_instr(0x0F, 3, 7, 0)  # CSEL r3 = const[0] (should be remapped to unique index)
    prog[2] = encode_instr(0x01, 7, 2, 3)  # r7 = r2 + r3

    tunable = TunableProgram(prog)
    assert len(tunable.slots) == 2
    # Setting different values for slot 0 and slot 1
    tunable.set_slots(np.array([1.5, 2.5], dtype=np.float32))

    xs = np.linspace(-1.0, 1.0, 5, dtype=np.float32)
    preds, flags = tunable.execute(xs)
    assert not flags.any()
    assert np.allclose(preds, 4.0)


def test_tune_promoted_candidate_combined() -> None:
    # Program: y = c * x
    prog = np.zeros(N_INSTR, dtype=np.uint32)
    prog[0] = encode_instr(0x0F, 2, 7, 0)
    prog[1] = encode_instr(0x03, 7, 0, 2)

    xs = np.linspace(-3.0, 3.0, 40, dtype=np.float32)
    ys = 2.5 * xs + 1.25

    res = tune_promoted_candidate(prog, xs, ys, max_steps=50)
    assert res["final_mse"] < 1e-4
    assert res["optimizer"] in ["linear_head_ols", "local_search", "local_search+linear_head"]
    # Verify execution matches target
    preds, _ = res["tunable_program"].execute(xs)
    assert np.allclose(preds, ys, atol=1e-2)


def test_evaluate_tunable() -> None:
    prog = np.zeros(N_INSTR, dtype=np.uint32)
    prog[0] = encode_instr(0x0F, 7, 7, 0)
    tunable = TunableProgram(prog)
    tunable.set_slots(np.array([3.14], dtype=np.float32))

    xs = np.linspace(0.0, 1.0, 5, dtype=np.float32)
    ys = np.full_like(xs, 3.14)

    ev = evaluate_tunable(tunable, xs, ys)
    assert ev["mse"] < 1e-6
    assert ev["mae"] < 1e-6
    assert ev["invalid_rate"] == 0.0

