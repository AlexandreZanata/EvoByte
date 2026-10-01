"""Deterministic CPU reference interpreter (spec: docs/VM.md)."""

from __future__ import annotations

import numpy as np

from evobyte.bytecode import CONST_BANK, N_INSTR, N_REGS, decode_instr

CLAMP = np.float32(1e30)
_TWO_PI = np.float32(2 * np.pi)


def _safe_apply(
    op: int,
    ra: np.float32,
    rb: np.float32,
    const_bank: np.ndarray = CONST_BANK,
) -> tuple[np.float32, bool]:
    """Apply one opcode with total safe-math semantics. Never returns NaN/Inf."""
    invalid = False
    a = np.float32(ra)
    b = np.float32(rb)
    if not np.isfinite(a):
        a = np.float32(0.0)
        invalid = True
    if not np.isfinite(b):
        b = np.float32(0.0)
        invalid = True

    with np.errstate(all="ignore"):
        if op == 0x01:  # ADD
            out = a + b
        elif op == 0x02:  # SUB
            out = a - b
        elif op == 0x03:  # MUL
            out = a * b
        elif op == 0x04:  # DIV
            if abs(float(b)) < 1e-12:
                return np.float32(0.0), True
            out = a / b
        elif op == 0x05:  # SIN
            out = np.float32(np.sin(np.float64(np.fmod(np.float64(a), np.float64(_TWO_PI)))))
        elif op == 0x06:  # COS
            out = np.float32(np.cos(np.float64(np.fmod(np.float64(a), np.float64(_TWO_PI)))))
        elif op == 0x07:  # EXP
            if float(a) > 20.0 or float(a) < -20.0:
                return np.float32(0.0), True
            out = np.float32(np.exp(np.float64(a)))
        elif op == 0x08:  # LOG
            if abs(float(a)) < 1e-12:
                return np.float32(0.0), True
            out = np.float32(np.log(np.float64(abs(float(a)))))
        elif op == 0x09:  # POW
            e = min(6.0, max(-6.0, float(b)))
            base = abs(float(a))
            if base < 1e-12 and e < 0.0:
                return np.float32(0.0), True
            try:
                out = np.float32(np.power(np.float32(base), np.float32(e)))
            except (OverflowError, ValueError):
                return np.float32(0.0), True
        elif op == 0x0A:  # ABS
            out = np.float32(abs(float(a)))
        elif op == 0x0B:  # SQRT
            out = np.float32(np.sqrt(abs(float(a))))
        elif op == 0x0C:  # NEG
            out = np.float32(-float(a))
        elif op == 0x0D:  # MIN
            out = np.float32(min(float(a), float(b)))
        elif op == 0x0E:  # MAX
            out = np.float32(max(float(a), float(b)))
        elif op == 0x0F:  # CSEL: ra + const[b & 0xF]
            bank = const_bank if const_bank is not None else CONST_BANK
            out = np.float32(float(a) + float(bank[int(b) & 0x0F]))
        else:
            return np.float32(0.0), True

        if not np.isfinite(out):
            return np.float32(0.0), True
        if out > CLAMP:
            return CLAMP, True
        if out < -CLAMP:
            return -CLAMP, True
        if out != 0 and abs(float(out)) < 1e-38:
            return np.float32(0.0), invalid
        return np.float32(out), invalid


def execute(
    program: np.ndarray,
    x0: np.float32,
    x1: np.float32 | None = None,
    const_bank: np.ndarray | None = None,
) -> tuple[np.float32, bool]:
    """Execute one program on one input point. Returns (output, invalid_flag)."""
    regs = np.zeros((N_REGS,), dtype=np.float32)
    regs[0] = np.float32(x0)
    regs[1] = np.float32(0.0) if x1 is None else np.float32(x1)
    invalid = False
    if not np.isfinite(regs[0]):
        regs[0] = np.float32(0.0)
        invalid = True
    if not np.isfinite(regs[1]):
        regs[1] = np.float32(0.0)
        invalid = True

    bank = const_bank if const_bank is not None else CONST_BANK

    for i in range(N_INSTR):
        op, dst, a, _b = decode_instr(program[i])
        b = int(_b)
        if op == 0x00:
            continue
        if dst >= N_REGS or a >= N_REGS:
            invalid = True
            continue
        if op != 0x0F:
            if op in (0x01, 0x02, 0x03, 0x04, 0x09, 0x0D, 0x0E) and b >= N_REGS:
                invalid = True
            rb = regs[b % N_REGS]
        else:
            rb = np.float32(b)
        out, flag = _safe_apply(op, regs[a], rb, const_bank=bank)
        regs[dst] = out
        invalid = invalid or flag

    final = regs[7]
    if not np.isfinite(final):
        return np.float32(0.0), True
    return np.float32(final), invalid


def execute_batch(
    program: np.ndarray,
    xs: np.ndarray,
    x1s: np.ndarray | None = None,
    const_bank: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Execute one program over an array of input values. Vectorized over points via loop (oracle clarity first)."""
    xs = np.asarray(xs, dtype=np.float32).ravel()
    preds = np.zeros_like(xs)
    flags = np.zeros_like(xs, dtype=bool)
    if x1s is not None:
        x1s = np.asarray(x1s, dtype=np.float32).ravel()
        if len(x1s) != len(xs):
            raise ValueError(f"xs and x1s must have the same length ({len(xs)} vs {len(x1s)})")
        for i in range(len(xs)):
            y, bad = execute(program, xs[i], x1s[i], const_bank=const_bank)
            preds[i] = y
            flags[i] = bad
    else:
        for i, x in enumerate(xs):
            y, bad = execute(program, np.float32(x), const_bank=const_bank)
            preds[i] = y
            flags[i] = bad
    return preds, flags


# --- Float64 True Execution Path (P19 Scope) ---

CLAMP_F64 = np.float64(1e300)
_TWO_PI_F64 = np.float64(2 * np.pi)
CONST_BANK_F64 = CONST_BANK.astype(np.float64)


def _safe_apply_f64(
    op: int,
    ra: np.float64,
    rb: np.float64,
    const_bank: np.ndarray | None = None,
) -> tuple[np.float64, bool]:
    """Apply one opcode with total safe-math semantics in true float64 precision."""
    invalid = False
    a = np.float64(ra)
    b = np.float64(rb)
    if not np.isfinite(a):
        a = np.float64(0.0)
        invalid = True
    if not np.isfinite(b):
        b = np.float64(0.0)
        invalid = True

    with np.errstate(all="ignore"):
        if op == 0x01:  # ADD
            out = a + b
        elif op == 0x02:  # SUB
            out = a - b
        elif op == 0x03:  # MUL
            out = a * b
        elif op == 0x04:  # DIV
            if abs(float(b)) < 1e-15:
                return np.float64(0.0), True
            out = a / b
        elif op == 0x05:  # SIN
            out = np.float64(np.sin(np.fmod(a, _TWO_PI_F64)))
        elif op == 0x06:  # COS
            out = np.float64(np.cos(np.fmod(a, _TWO_PI_F64)))
        elif op == 0x07:  # EXP
            if float(a) > 700.0 or float(a) < -700.0:
                return np.float64(0.0), True
            out = np.float64(np.exp(a))
        elif op == 0x08:  # LOG
            if abs(float(a)) < 1e-15:
                return np.float64(0.0), True
            out = np.float64(np.log(abs(float(a))))
        elif op == 0x09:  # POW
            e = min(6.0, max(-6.0, float(b)))
            base = abs(float(a))
            if base < 1e-15 and e < 0.0:
                return np.float64(0.0), True
            try:
                out = np.float64(np.power(np.float64(base), np.float64(e)))
            except (OverflowError, ValueError):
                return np.float64(0.0), True
        elif op == 0x0A:  # ABS
            out = np.float64(abs(float(a)))
        elif op == 0x0B:  # SQRT
            out = np.float64(np.sqrt(abs(float(a))))
        elif op == 0x0C:  # NEG
            out = np.float64(-float(a))
        elif op == 0x0D:  # MIN
            out = np.float64(min(float(a), float(b)))
        elif op == 0x0E:  # MAX
            out = np.float64(max(float(a), float(b)))
        elif op == 0x0F:  # CSEL: ra + const[b & 0xF]
            bank = const_bank if const_bank is not None else CONST_BANK_F64
            out = np.float64(float(a) + float(bank[int(b) & 0x0F]))
        else:
            return np.float64(0.0), True

        if not np.isfinite(out):
            return np.float64(0.0), True
        if out > CLAMP_F64:
            return CLAMP_F64, True
        if out < -CLAMP_F64:
            return -CLAMP_F64, True
        if out != 0 and abs(float(out)) < 1e-300:
            return np.float64(0.0), invalid
        return np.float64(out), invalid


def execute_f64(
    program: np.ndarray,
    x0: float | np.float64,
    x1: float | np.float64 | None = None,
    const_bank: np.ndarray | None = None,
) -> tuple[np.float64, bool]:
    """Execute one program on one input point in pure float64 precision."""
    regs = np.zeros((N_REGS,), dtype=np.float64)
    regs[0] = np.float64(x0)
    regs[1] = np.float64(0.0) if x1 is None else np.float64(x1)
    invalid = False
    if not np.isfinite(regs[0]):
        regs[0] = np.float64(0.0)
        invalid = True
    if not np.isfinite(regs[1]):
        regs[1] = np.float64(0.0)
        invalid = True

    bank = const_bank if const_bank is not None else CONST_BANK_F64

    for i in range(N_INSTR):
        op, dst, a, _b = decode_instr(program[i])
        b = int(_b)
        if op == 0x00:
            continue
        if dst >= N_REGS or a >= N_REGS:
            invalid = True
            continue
        if op != 0x0F:
            if op in (0x01, 0x02, 0x03, 0x04, 0x09, 0x0D, 0x0E) and b >= N_REGS:
                invalid = True
            rb = regs[b % N_REGS]
        else:
            rb = np.float64(b)
        out, flag = _safe_apply_f64(op, regs[a], rb, const_bank=bank)
        regs[dst] = out
        invalid = invalid or flag

    final = regs[7]
    if not np.isfinite(final):
        return np.float64(0.0), True
    return np.float64(final), invalid


def execute_batch_f64(
    program: np.ndarray,
    xs: np.ndarray,
    x1s: np.ndarray | None = None,
    const_bank: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Execute one program over an array of float64 inputs. Returns (preds, flags)."""
    xs = np.asarray(xs, dtype=np.float64).ravel()
    preds = np.zeros_like(xs, dtype=np.float64)
    flags = np.zeros_like(xs, dtype=bool)
    bank = const_bank if const_bank is not None else CONST_BANK_F64
    if x1s is not None:
        x1s = np.asarray(x1s, dtype=np.float64).ravel()
        if len(x1s) != len(xs):
            raise ValueError(f"xs and x1s must have the same length ({len(xs)} vs {len(x1s)})")
        for i in range(len(xs)):
            y, bad = execute_f64(program, xs[i], x1s[i], const_bank=bank)
            preds[i] = y
            flags[i] = bad
    else:
        for i, x in enumerate(xs):
            y, bad = execute_f64(program, np.float64(x), const_bank=bank)
            preds[i] = y
            flags[i] = bad
    return preds, flags
