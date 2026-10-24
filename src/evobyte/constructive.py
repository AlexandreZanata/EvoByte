"""Deterministic greedy constructor guided by priority programs (P173)."""

from __future__ import annotations

import math
from typing import Any, Callable

import numpy as np

from evobyte.bytecode import CONST_BANK, N_INSTR, N_REGS, decode_instr
from evobyte.vm import _safe_apply


def evaluate_priority(
    program: np.ndarray,
    features: list[float] | np.ndarray,
    context: list[float] | np.ndarray,
) -> float:
    """Carrega features em r0..r6, zera r7, executa o programa v1 e retorna r7.

    Entrada malformada (tamanho errado, NaN) retorna -inf, nunca levanta.
    """
    try:
        if program is None:
            return -float("inf")
        prog = np.asarray(program, dtype=np.uint32)
        if prog.shape != (N_INSTR,):
            return -float("inf")

        if features is None or context is None:
            return -float("inf")

        feat_list = [float(x) for x in features]
        ctx_list = [float(x) for x in context]

        for val in feat_list:
            if not math.isfinite(val):
                return -float("inf")
        for val in ctx_list:
            if not math.isfinite(val):
                return -float("inf")

        regs = np.zeros(N_REGS, dtype=np.float32)
        for i in range(min(7, len(feat_list))):
            regs[i] = np.float32(feat_list[i])
        regs[7] = np.float32(0.0)

        for word in prog:
            op, dst, a, _b = decode_instr(word)
            b = int(_b)
            if op == 0x00:
                continue
            if dst >= N_REGS or a >= N_REGS:
                return -float("inf")

            if op == 0x10:  # CTX: r[dst] = ctx[b & 0x0F]
                idx = b & 0x0F
                val = ctx_list[idx] if 0 <= idx < len(ctx_list) else 0.0
                regs[dst] = np.float32(val)
                continue
            elif op == 0x11:  # FEAT: r[dst] = feat[b & 0x0F]
                idx = b & 0x0F
                val = feat_list[idx] if 0 <= idx < len(feat_list) else 0.0
                regs[dst] = np.float32(val)
                continue

            if op != 0x0F:
                rb = regs[b % N_REGS]
            else:
                rb = np.float32(b)

            out, _flag = _safe_apply(op, regs[a], rb, const_bank=CONST_BANK)
            regs[dst] = out

        result = float(regs[7])
        if not math.isfinite(result):
            return -float("inf")
        return result
    except Exception:
        return -float("inf")


def greedy_construct(
    candidates: list[Any] | tuple[Any, ...],
    priority_fn: Callable[[Any, dict[str, Any]], float],
    is_feasible_fn: Callable[..., bool],
    is_complete_fn: Callable[..., bool],
    max_steps: int | None = None,
) -> tuple[list[Any], int, int]:
    """Determinístico: a cada passo pontua os candidatos restantes, escolhe o maior

    (desempate: menor índice), adiciona se feasible. Retorna (built_list, steps,
    evaluations). `priority_fn(move, context) -> float`; `context` é dict com
    estado parcial (ex: tamanho atual, cobertura, orçamento restante).
    """
    built_list: list[Any] = []
    remaining = list(candidates)
    steps = 0
    evaluations = 0

    context: dict[str, Any] = {
        "size": 0,
        "built": built_list,
        "steps": 0,
    }

    def _check_complete(bl: list[Any], ctx: dict[str, Any]) -> bool:
        try:
            return bool(is_complete_fn(bl, ctx))
        except TypeError:
            try:
                return bool(is_complete_fn(bl))
            except Exception:
                return False

    def _check_feasible(cand: Any, bl: list[Any], ctx: dict[str, Any]) -> bool:
        try:
            return bool(is_feasible_fn(cand, bl, ctx))
        except TypeError:
            try:
                return bool(is_feasible_fn(cand, bl))
            except TypeError:
                try:
                    return bool(is_feasible_fn(cand))
                except Exception:
                    return False

    while remaining:
        if max_steps is not None and steps >= max_steps:
            break
        if _check_complete(built_list, context):
            break

        best_idx = 0
        best_score = -float("inf")
        best_cand = remaining[0]

        for idx, cand in enumerate(remaining):
            try:
                score = float(priority_fn(cand, context))
            except Exception:
                score = -float("inf")
            evaluations += 1

            if score > best_score:
                best_score = score
                best_idx = idx
                best_cand = cand

        chosen = remaining.pop(best_idx)
        steps += 1

        if _check_feasible(chosen, built_list, context):
            built_list.append(chosen)
            context["size"] = len(built_list)
            context["built"] = built_list

        context["steps"] = steps

    return built_list, steps, evaluations
