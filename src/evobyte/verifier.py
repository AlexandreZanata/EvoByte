"""Level-1 scoring + cascade + early stop (spec: docs/VERIFIER.md)."""

from __future__ import annotations

import numpy as np

from evobyte.bytecode import N_INSTR, OPCODES, decode_instr
from evobyte.vm import execute_batch

W_ERR = 1.0
W_COMPLEXITY = 1e-3
W_INVALID = 1.0


def complexity(program: np.ndarray) -> float:
    """Cheap parsimony: non-NOP count + 0.5 * distinct ops."""
    ops = set()
    count = 0
    for word in program:
        op = int(word) & 0xFF
        if op == 0x00:
            continue
        count += 1
        ops.add(op)
    return float(count) + 0.5 * float(len(ops))


def score_predictions(pred: np.ndarray, target: np.ndarray, invalid: np.ndarray, comp: float) -> float:
    """Scalar fitness (lower is better). All inputs finite by VM contract."""
    pred = np.asarray(pred, dtype=np.float64)
    target = np.asarray(target, dtype=np.float64)
    mse = float(np.mean((pred - target) ** 2))
    mae = float(np.mean(np.abs(pred - target)))
    invalid_rate = float(np.mean(invalid)) if invalid.size else 0.0
    return W_ERR * (mse + 0.1 * mae) + W_COMPLEXITY * comp + W_INVALID * invalid_rate


def evaluate(program: np.ndarray, xs: np.ndarray, ys: np.ndarray) -> dict:
    """Full S3-style evaluation of one program on (xs, ys)."""
    pred, invalid = execute_batch(program, xs)
    comp = complexity(program)
    fitness = score_predictions(pred, ys, invalid, comp)
    mse = float(np.mean((np.asarray(pred, float) - np.asarray(ys, float)) ** 2))
    return {"fitness": fitness, "mse": mse, "complexity": comp,
            "invalid_rate": float(np.mean(invalid)) if invalid.size else 0.0}


def cascade_evaluate(program: np.ndarray, xs: np.ndarray, ys: np.ndarray,
                     elite_err: float = 1.0, k: float = 4.0) -> dict:
    """S1(32) -> S2(256) -> S3(full) with early termination.

    Returns dict with stage reached, fitness, and kill flag.
    """
    n = len(xs)
    stages = [min(32, n), min(256, n), n]
    for stage_i, m in enumerate(stages):
        sub = evaluate(program, xs[:m], ys[:m])
        if m >= 8 and sub["mse"] > k * max(elite_err, 1e-12):
            return {"stage": stage_i + 1, "fitness": sub["fitness"], "mse": sub["mse"],
                    "killed": True, "complexity": sub["complexity"],
                    "invalid_rate": sub["invalid_rate"]}
        if m == n:
            return {"stage": stage_i + 1, "fitness": sub["fitness"], "mse": sub["mse"],
                    "killed": False, "complexity": sub["complexity"],
                    "invalid_rate": sub["invalid_rate"]}
    raise AssertionError("unreachable")
