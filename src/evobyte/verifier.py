"""Level-1 scoring + cascade + early stop (spec: docs/VERIFIER.md)."""

from __future__ import annotations

import numpy as np

from evobyte.bytecode import is_valid
from evobyte.vm import execute_batch

W_ERR = 1.0
W_COMPLEXITY = 1e-3
W_INVALID = 1.0
W_VAL_GAP = 0.5
PENALTY_INVALID = 1e9


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


def score_predictions(
    pred: np.ndarray,
    target: np.ndarray,
    invalid: np.ndarray,
    comp: float,
    val_pred: np.ndarray | None = None,
    val_target: np.ndarray | None = None,
) -> float:
    """Scalar fitness (lower is better). All inputs finite by VM contract."""
    pred = np.asarray(pred, dtype=np.float64)
    target = np.asarray(target, dtype=np.float64)
    mse = float(np.mean((pred - target) ** 2))
    mae = float(np.mean(np.abs(pred - target)))
    norm_err = mse + 0.1 * mae
    invalid_rate = float(np.mean(invalid)) if invalid.size else 0.0

    val_gap = 0.0
    if val_pred is not None and val_target is not None:
        val_pred = np.asarray(val_pred, dtype=np.float64)
        val_target = np.asarray(val_target, dtype=np.float64)
        val_mse = float(np.mean((val_pred - val_target) ** 2))
        val_mae = float(np.mean(np.abs(val_pred - val_target)))
        val_err = val_mse + 0.1 * val_mae
        val_gap = max(0.0, val_err - norm_err)

    return W_ERR * norm_err + W_COMPLEXITY * comp + W_INVALID * invalid_rate + W_VAL_GAP * val_gap


def evaluate(
    program: np.ndarray,
    xs: np.ndarray,
    ys: np.ndarray,
    val_xs: np.ndarray | None = None,
    val_ys: np.ndarray | None = None,
) -> dict:
    """Full S3-style evaluation of one program on (xs, ys) with optional validation set."""
    pred, invalid = execute_batch(program, xs)
    comp = complexity(program)

    val_pred = None
    if val_xs is not None and val_ys is not None:
        val_pred, _ = execute_batch(program, val_xs)

    fitness = score_predictions(pred, ys, invalid, comp, val_pred=val_pred, val_target=val_ys)
    mse = float(np.mean((np.asarray(pred, float) - np.asarray(ys, float)) ** 2))
    mae = float(np.mean(np.abs(np.asarray(pred, float) - np.asarray(ys, float))))
    norm_err = mse + 0.1 * mae

    val_gap = 0.0
    if val_pred is not None and val_ys is not None:
        val_mse = float(np.mean((np.asarray(val_pred, float) - np.asarray(val_ys, float)) ** 2))
        val_mae = float(np.mean(np.abs(np.asarray(val_pred, float) - np.asarray(val_ys, float))))
        val_gap = max(0.0, (val_mse + 0.1 * val_mae) - norm_err)

    return {
        "fitness": fitness,
        "mse": mse,
        "mae": mae,
        "norm_err": norm_err,
        "complexity": comp,
        "invalid_rate": float(np.mean(invalid)) if invalid.size else 0.0,
        "val_gap": val_gap,
    }


def cascade_evaluate(
    program: np.ndarray,
    xs: np.ndarray,
    ys: np.ndarray,
    elite_err: float = 1.0,
    k: float = 4.0,
    val_xs: np.ndarray | None = None,
    val_ys: np.ndarray | None = None,
) -> dict:
    """S0(validity) -> S1(32) -> S2(256) -> S3(up to 4096) with early termination.

    Returns dict with stage reached, fitness, and kill flag.
    """
    comp = complexity(program)
    if not is_valid(program):
        return {
            "stage": 0,
            "fitness": PENALTY_INVALID,
            "mse": float("inf"),
            "mae": float("inf"),
            "norm_err": float("inf"),
            "killed": True,
            "complexity": comp,
            "invalid_rate": 1.0,
            "val_gap": 0.0,
        }

    n = len(xs)
    stage_sizes = [min(32, n), min(256, n), min(4096, n)]
    stages = []
    for s in stage_sizes:
        if not stages or s > stages[-1]:
            stages.append(s)

    last_sub = None
    for stage_i, m in enumerate(stages):
        sub = evaluate(program, xs[:m], ys[:m])
        last_sub = sub
        if m >= 8 and sub["norm_err"] > k * max(elite_err, 1e-12):
            return {
                "stage": stage_i + 1,
                "fitness": sub["fitness"],
                "mse": sub["mse"],
                "mae": sub["mae"],
                "norm_err": sub["norm_err"],
                "killed": True,
                "complexity": comp,
                "invalid_rate": sub["invalid_rate"],
                "val_gap": sub["val_gap"],
            }

    if val_xs is not None and val_ys is not None:
        last_sub = evaluate(program, xs[: stages[-1]], ys[: stages[-1]], val_xs, val_ys)

    return {
        "stage": len(stages),
        "fitness": last_sub["fitness"],
        "mse": last_sub["mse"],
        "mae": last_sub["mae"],
        "norm_err": last_sub["norm_err"],
        "killed": False,
        "complexity": comp,
        "invalid_rate": last_sub["invalid_rate"],
        "val_gap": last_sub["val_gap"],
    }


def cascade_evaluate_population(
    programs: list[np.ndarray],
    xs: np.ndarray,
    ys: np.ndarray,
    elite_err: float = 1.0,
    k: float = 4.0,
) -> dict:
    """Evaluate a population of candidates through the cascade and report stage accounting."""
    results = []
    total = len(programs)
    stage_kills = {0: 0, 1: 0, 2: 0, 3: 0}

    for prog in programs:
        res = cascade_evaluate(prog, xs, ys, elite_err=elite_err, k=k)
        results.append(res)
        if res["killed"]:
            st = res["stage"]
            stage_kills[st] = stage_kills.get(st, 0) + 1

    stage_survivors = {}
    current = total
    for s in range(4):
        stage_survivors[s] = current
        current = max(0, current - stage_kills.get(s, 0))

    final_survivors = sum(1 for r in results if not r["killed"])
    kill_rates = {s: (stage_kills.get(s, 0) / total) if total else 0.0 for s in range(4)}

    return {
        "results": results,
        "total": total,
        "stage_survivors": stage_survivors,
        "stage_kills": stage_kills,
        "kill_rates": kill_rates,
        "survivors": final_survivors,
        "survival_rate": final_survivors / total if total else 0.0,
    }
