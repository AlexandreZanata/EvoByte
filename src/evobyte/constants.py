"""Constant optimization: tunable slots, local search, and linear least squares (spec: docs/CONSTANTS.md, P11)."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import numpy as np

from evobyte.bytecode import CONST_BANK, N_INSTR, decode_instr, decode_human, encode_instr
from evobyte.vm import execute_batch


MAX_TUNABLE_SLOTS = 4
ABSURD_CONSTANT_THRESHOLD = 1e6


def extract_csel_slots(program: np.ndarray) -> list[tuple[int, int]]:
    """Extract up to MAX_TUNABLE_SLOTS (instr_idx, bank_idx) for CSEL instructions."""
    slots = []
    for idx in range(N_INSTR):
        op, dst, a, b = decode_instr(program[idx])
        if op == 0x0F:  # CSEL
            bank_idx = int(b) & 0x0F
            slots.append((idx, bank_idx))
            if len(slots) >= MAX_TUNABLE_SLOTS:
                break
    return slots


class TunableProgram:
    """Wrapper around a bytecode program with up to 4 tunable constant slots."""

    def __init__(
        self,
        program: np.ndarray,
        initial_constants: np.ndarray | None = None,
    ) -> None:
        self.program = np.asarray(program, dtype=np.uint32).copy()
        raw_slots = extract_csel_slots(self.program)
        self.custom_bank = CONST_BANK.copy()
        self.linear_head: tuple[float, float] = (1.0, 0.0)

        # Ensure all extracted CSEL slots have unique bank indices so each can be tuned independently
        used_bank_indices = set()
        for idx in range(N_INSTR):
            op, dst, a, b = decode_instr(self.program[idx])
            if op == 0x0F:
                used_bank_indices.add(int(b) & 0x0F)

        self.csel_slots = []
        assigned_indices = set()
        next_free_bank_idx = 15

        for instr_idx, bank_idx in raw_slots:
            if bank_idx not in assigned_indices:
                assigned_indices.add(bank_idx)
                self.csel_slots.append((instr_idx, bank_idx))
            else:
                while next_free_bank_idx in used_bank_indices or next_free_bank_idx in assigned_indices:
                    next_free_bank_idx -= 1
                    if next_free_bank_idx < 0:
                        break
                if next_free_bank_idx >= 0:
                    new_bank_idx = next_free_bank_idx
                    self.custom_bank[new_bank_idx] = self.custom_bank[bank_idx]
                    op, dst, a, _ = decode_instr(self.program[instr_idx])
                    self.program[instr_idx] = encode_instr(op, dst, a, new_bank_idx)
                    assigned_indices.add(new_bank_idx)
                    self.csel_slots.append((instr_idx, new_bank_idx))
                    next_free_bank_idx -= 1
                else:
                    self.csel_slots.append((instr_idx, bank_idx))

        # Initialize slots with bank fallback values
        if initial_constants is not None:
            self.slots = np.asarray(initial_constants, dtype=np.float32).copy()
            for i, (_, bank_idx) in enumerate(self.csel_slots):
                if i < len(self.slots):
                    self.custom_bank[bank_idx] = self.slots[i]
        else:
            self.slots = np.array([self.custom_bank[bank_idx] for _, bank_idx in self.csel_slots], dtype=np.float32)

    def get_slots(self) -> np.ndarray:
        return self.slots.copy()

    def set_slots(self, values: np.ndarray) -> None:
        vals = np.asarray(values, dtype=np.float32)
        n = min(len(vals), len(self.slots))
        self.slots[:n] = vals[:n]
        for i in range(n):
            _, bank_idx = self.csel_slots[i]
            self.custom_bank[bank_idx] = self.slots[i]

    def execute(self, xs: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Execute program with current tunable constant slots and linear head."""
        preds, flags = execute_batch(self.program, xs, const_bank=self.custom_bank)
        if self.linear_head != (1.0, 0.0):
            preds = self.linear_head[0] * preds + self.linear_head[1]
        return preds, flags

    def decode_expression(self) -> str:
        """Decode program replacing CSEL bank constants with actual fitted values and affine head."""
        parts = []
        csel_counter = 0
        for idx in range(N_INSTR):
            op, dst, a, b = decode_instr(self.program[idx])
            if op == 0x00:
                continue
            if op == 0x0F:
                if csel_counter < len(self.slots):
                    val = self.slots[csel_counter]
                    parts.append(f"CSEL r{dst}, r{a}, const={val:.5g}")
                    csel_counter += 1
                else:
                    parts.append(f"CSEL r{dst}, r{a}, {b:#04x}")
            else:
                name = {
                    0x01: "ADD", 0x02: "SUB", 0x03: "MUL", 0x04: "DIV",
                    0x05: "SIN", 0x06: "COS", 0x07: "EXP", 0x08: "LOG",
                    0x09: "POW", 0x0A: "ABS", 0x0B: "SQRT", 0x0C: "NEG",
                    0x0D: "MIN", 0x0E: "MAX",
                }.get(op, f"OP{op:#x}")
                parts.append(f"{name} r{dst}, r{a}, {b:#04x}")
        body = " ; ".join(parts) if parts else "NOP"
        if self.linear_head != (1.0, 0.0):
            w1, w0 = self.linear_head
            return f"{w1:.5g} * ({body}) + {w0:.5g}"
        return body


def fit_linear_head(
    program: np.ndarray,
    xs: np.ndarray,
    ys: np.ndarray,
) -> tuple[float, float, float, int]:
    """Fit affine output head: y_pred = w1 * prog(x) + w0 via closed-form OLS."""
    preds, flags = execute_batch(program, xs)
    if flags.any() or not np.all(np.isfinite(preds)):
        return 1.0, 0.0, float("inf"), 1

    # Design matrix [preds, 1]
    X = np.stack([preds, np.ones_like(preds)], axis=1)
    try:
        w, residuals, rank, s = np.linalg.lstsq(X, ys, rcond=None)
        w1, w0 = float(w[0]), float(w[1])
        fitted_preds = w1 * preds + w0
        mse = float(np.mean((fitted_preds - ys) ** 2))
        return w1, w0, mse, 1
    except Exception:
        mse_base = float(np.mean((preds - ys) ** 2))
        return 1.0, 0.0, mse_base, 1


def fit_constants_local_search(
    tunable_prog: TunableProgram,
    xs: np.ndarray,
    ys: np.ndarray,
    max_steps: int = 100,
    initial_step: float = 0.5,
    patience: int = 15,
) -> dict[str, Any]:
    """Hill-climbing local search combining coordinate exploration and adaptive Gaussian perturbation."""
    t0 = time.perf_counter()
    n_slots = len(tunable_prog.slots)
    if n_slots == 0:
        preds, flags = tunable_prog.execute(xs)
        mse = float(np.mean((preds - ys) ** 2)) if not flags.any() else float("inf")
        return {
            "optimizer": "local_search",
            "steps": 0,
            "time_sec": time.perf_counter() - t0,
            "initial_mse": mse,
            "final_mse": mse,
            "delta_mse": 0.0,
            "best_slots": tunable_prog.get_slots(),
        }

    preds, flags = tunable_prog.execute(xs)
    init_mse = float(np.mean((preds - ys) ** 2)) if not flags.any() else float("inf")

    best_slots = tunable_prog.get_slots()
    if np.any(np.abs(best_slots) > ABSURD_CONSTANT_THRESHOLD):
        best_slots = np.clip(best_slots, -ABSURD_CONSTANT_THRESHOLD, ABSURD_CONSTANT_THRESHOLD)
        tunable_prog.set_slots(best_slots)

    best_mse = init_mse
    step_size = initial_step
    no_improve = 0
    actual_steps = 0

    for step in range(1, max_steps + 1):
        actual_steps += 1
        improved = False

        # Phase 1: Coordinate exploration (+/- step_size along each slot axis)
        for dim in range(n_slots):
            for direction in [1.0, -1.0]:
                cand_slots = best_slots.copy()
                cand_slots[dim] += direction * step_size
                if np.abs(cand_slots[dim]) > ABSURD_CONSTANT_THRESHOLD:
                    continue

                tunable_prog.set_slots(cand_slots)
                preds, flags = tunable_prog.execute(xs)
                if flags.any() or not np.all(np.isfinite(preds)):
                    continue

                cand_mse = float(np.mean((preds - ys) ** 2))
                if cand_mse < best_mse - 1e-9:
                    best_mse = cand_mse
                    best_slots = cand_slots.copy()
                    improved = True

        # Phase 2: Gaussian perturbation if coordinate moves stalled
        if not improved:
            perturbation = np.random.randn(n_slots).astype(np.float32) * step_size
            cand_slots = best_slots + perturbation
            if not np.any(np.abs(cand_slots) > ABSURD_CONSTANT_THRESHOLD):
                tunable_prog.set_slots(cand_slots)
                preds, flags = tunable_prog.execute(xs)
                if not flags.any() and np.all(np.isfinite(preds)):
                    cand_mse = float(np.mean((preds - ys) ** 2))
                    if cand_mse < best_mse - 1e-9:
                        best_mse = cand_mse
                        best_slots = cand_slots.copy()
                        improved = True

        if improved:
            no_improve = 0
            step_size = min(step_size * 1.08, 5.0)
        else:
            no_improve += 1
            if no_improve >= patience:
                step_size *= 0.5
                no_improve = 0
                if step_size < 1e-6:
                    break

    tunable_prog.set_slots(best_slots)
    elapsed = time.perf_counter() - t0

    return {
        "optimizer": "local_search",
        "steps": actual_steps,
        "time_sec": elapsed,
        "initial_mse": init_mse,
        "final_mse": best_mse,
        "delta_mse": max(0.0, init_mse - best_mse),
        "best_slots": best_slots,
    }


def tune_promoted_candidate(
    program: np.ndarray,
    xs: np.ndarray,
    ys: np.ndarray,
    max_steps: int = 100,
) -> dict[str, Any]:
    """S3/L2 promotion hook: fits linear head and tunable constant slots."""
    t0 = time.perf_counter()
    tunable = TunableProgram(program)

    # Initial baseline evaluation
    preds_init, flags_init = tunable.execute(xs)
    init_mse = float(np.mean((preds_init - ys) ** 2)) if not flags_init.any() else float("inf")

    # 1. Closed-form linear head fit on raw program
    w1_lin, w0_lin, mse_lin, steps_lin = fit_linear_head(program, xs, ys)

    # 2. Local search on tunable slots
    res_local = fit_constants_local_search(tunable, xs, ys, max_steps=max_steps)

    # 3. Check combined local search + linear head
    preds_tuned, flags_tuned = tunable.execute(xs)
    if not flags_tuned.any() and np.all(np.isfinite(preds_tuned)):
        X = np.stack([preds_tuned, np.ones_like(preds_tuned)], axis=1)
        try:
            w_comb, _, _, _ = np.linalg.lstsq(X, ys, rcond=None)
            w1_comb, w0_comb = float(w_comb[0]), float(w_comb[1])
            fitted_comb = w1_comb * preds_tuned + w0_comb
            mse_comb = float(np.mean((fitted_comb - ys) ** 2))
        except Exception:
            mse_comb = float("inf")
            w1_comb, w0_comb = 1.0, 0.0
    else:
        mse_comb = float("inf")
        w1_comb, w0_comb = 1.0, 0.0

    # Pick the best configuration
    candidates = [
        (init_mse, "none", (1.0, 0.0), False),
        (mse_lin, "linear_head_ols", (w1_lin, w0_lin), False),
        (res_local["final_mse"], "local_search", (1.0, 0.0), True),
        (mse_comb, "local_search+linear_head", (w1_comb, w0_comb), True),
    ]
    candidates.sort(key=lambda c: c[0])
    best_mse, opt_name, chosen_head, use_tuned = candidates[0]

    if not use_tuned:
        tunable = TunableProgram(program)
    tunable.linear_head = chosen_head

    total_time = time.perf_counter() - t0
    total_steps = res_local["steps"] + steps_lin + 1

    return {
        "program": tunable.program,
        "optimizer": opt_name,
        "initial_mse": init_mse,
        "final_mse": best_mse,
        "delta_mse": max(0.0, init_mse - best_mse),
        "steps": total_steps,
        "time_sec": total_time,
        "slots": tunable.get_slots(),
        "linear_head": tunable.linear_head,
        "tunable_program": tunable,
        "expression": tunable.decode_expression(),
    }


def evaluate_tunable(
    tunable: TunableProgram,
    xs: np.ndarray,
    ys: np.ndarray,
) -> dict[str, float]:
    """Evaluate a TunableProgram on (xs, ys) returning mse, mae, and invalid_rate."""
    preds, flags = tunable.execute(xs)
    if flags.any() or not np.all(np.isfinite(preds)):
        return {"mse": float("inf"), "mae": float("inf"), "invalid_rate": 1.0}
    preds_f = np.asarray(preds, dtype=np.float64)
    ys_f = np.asarray(ys, dtype=np.float64)
    mse = float(np.mean((preds_f - ys_f) ** 2))
    mae = float(np.mean(np.abs(preds_f - ys_f)))
    return {"mse": mse, "mae": mae, "invalid_rate": 0.0}


