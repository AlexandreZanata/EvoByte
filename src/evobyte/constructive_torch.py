"""GPU-batched priority scoring for the greedy constructor (P175).

Parity convention (declared tolerance): GPU scores must satisfy
``np.testing.assert_allclose(gpu, cpu, rtol=1e-5, atol=1e-5)`` — the same
combined relative/absolute convention used by ``tests/test_vm_torch.py``.
Pure absolute tolerance is magnitude-dependent in float32 (1 ulp at 2.3e7
is 2.0), so large-magnitude EXP outputs are judged by relative error.
``GPU_CPU_TOLERANCE`` is used as both rtol and atol.
"""

from __future__ import annotations

import math

import numpy as np
import torch

from evobyte.bytecode import N_INSTR, N_REGS
from evobyte.constructive import evaluate_priority
from evobyte.vm_torch import _safe_apply_torch, get_const_bank_tensor

GPU_CPU_TOLERANCE = 1e-5


def within_tolerance(gpu: float, cpu: float, tol: float = GPU_CPU_TOLERANCE) -> bool:
    """allclose-style check: |g-c| <= atol + rtol*|c| (handles -inf pairs)."""
    if gpu == cpu == float("-inf"):
        return True
    if not (math.isfinite(gpu) and math.isfinite(cpu)):
        return False
    return abs(gpu - cpu) <= tol + tol * abs(cpu)


def _want_gpu(device: object | None) -> torch.device | None:
    """Return a CUDA device when explicitly or implicitly requested and present.

    `device="cpu"` (or any CPU device) forces the CPU fallback. Any other
    request resolves to CUDA only when `torch.cuda.is_available()`.
    """
    if device is not None:
        try:
            d = torch.device(device)  # type: ignore[arg-type]
        except Exception:
            return None
        if d.type != "cuda" or not torch.cuda.is_available():
            return None
        return d
    if not torch.cuda.is_available():
        return None
    try:
        from evobyte.vm_torch import get_default_device

        dflt = get_default_device()
        return dflt if dflt.type == "cuda" else None
    except Exception:
        return None


def peak_vram_mb(device: object | None = None) -> float | None:
    """Current CUDA peak allocation in MiB, or None without CUDA. Never raises."""
    try:
        if not torch.cuda.is_available():
            return None
        dev: torch.device | None = None
        if device is not None:
            try:
                dev = torch.device(device)  # type: ignore[arg-type]
            except Exception:
                dev = None
        peak = torch.cuda.max_memory_allocated(dev)
        return float(peak) / float(2**20)
    except Exception:
        return None


def _as_program_words(prog: object) -> np.ndarray | None:
    try:
        arr = np.asarray(prog, dtype=np.uint32)
    except Exception:
        return None
    if arr.shape != (N_INSTR,):
        return None
    return arr


def _as_float_list(bank: object) -> list[float] | None:
    if bank is None:
        return None
    try:
        if isinstance(bank, torch.Tensor):
            vals = bank.detach().to("cpu").flatten().tolist()
        elif isinstance(bank, np.ndarray):
            vals = bank.flatten().tolist()
        else:
            vals = list(bank)  # type: ignore[arg-type]
    except Exception:
        return None
    out: list[float] = []
    for v in vals:
        try:
            f = float(v)
        except Exception:
            return None
        if not math.isfinite(f):
            return None
        out.append(f)
    return out


def _score_batch_gpu(
    prog_words: list[np.ndarray | None],
    feat_lists: list[list[float] | None],
    ctx_lists: list[list[float] | None],
    dev: torch.device,
) -> list[float]:
    n = len(prog_words)
    valid = np.ones((n,), dtype=bool)
    feat_mat = np.zeros((n, 16), dtype=np.float32)
    ctx_mat = np.zeros((n, 16), dtype=np.float32)
    prog_stack = np.zeros((n, N_INSTR), dtype=np.int64)

    for i in range(n):
        pw = prog_words[i]
        fl = feat_lists[i]
        cl = ctx_lists[i]
        if pw is None or fl is None or cl is None:
            valid[i] = False
            continue
        w = pw.astype(np.int64)
        prog_stack[i] = w
        ops = w & 0xFF
        dsts = (w >> 8) & 0xFF
        aas = (w >> 16) & 0xFF
        non_nop = ops != 0x00
        if bool(((dsts[non_nop] >= N_REGS).any() or (aas[non_nop] >= N_REGS).any())):
            valid[i] = False
            continue
        k = min(len(fl), 16)
        if k:
            feat_mat[i, :k] = np.asarray(fl[:k], dtype=np.float32)
        k = min(len(cl), 16)
        if k:
            ctx_mat[i, :k] = np.asarray(cl[:k], dtype=np.float32)

    # Items pre-marked invalid still execute harmlessly below; their outputs
    # are overridden with -inf at the end (single sync).
    prog_t = torch.from_numpy(prog_stack).to(dev)
    feat_t = torch.from_numpy(feat_mat).to(dev)
    ctx_t = torch.from_numpy(ctx_mat).to(dev)
    regs = torch.zeros((n, N_REGS), dtype=torch.float32, device=dev)
    regs[:, :7] = feat_t[:, :7]
    const_bank = get_const_bank_tensor(dev)

    with torch.no_grad():
        for step in range(N_INSTR):
            words = prog_t[:, step]
            ops = words & 0xFF
            if bool((ops == 0x00).all()):
                continue
            dsts = (words >> 8) & 0xFF
            aas = (words >> 16) & 0xFF
            bs = (words >> 24) & 0xFF
            # CTX
            m = ops == 0x10
            if bool(m.any()):
                rows = torch.nonzero(m).squeeze(1)
                nib = (bs[rows] & 0x0F).to(torch.long)
                regs[rows, dsts[rows]] = ctx_t[rows, nib]
            # FEAT
            m = ops == 0x11
            if bool(m.any()):
                rows = torch.nonzero(m).squeeze(1)
                nib = (bs[rows] & 0x0F).to(torch.long)
                regs[rows, dsts[rows]] = feat_t[rows, nib]
            # Remaining ops via the shared safe-math kernel (same numerics
            # as the CPU path; pre-validated banks/regs are finite).
            rest = ops[(ops != 0x00) & (ops != 0x10) & (ops != 0x11)]
            if rest.numel() == 0:
                continue
            for op_t in torch.unique(rest).tolist():
                op = int(op_t)
                m = ops == op
                rows = torch.nonzero(m).squeeze(1)
                if rows.numel() == 0:
                    continue
                if op == 0x0F:
                    rb = bs[rows].to(dtype=torch.float32)
                else:
                    rb = regs[rows, (bs[rows] % N_REGS).to(torch.long)]
                out, _flag = _safe_apply_torch(
                    op, regs[rows, aas[rows].to(torch.long)], rb, bs[rows], const_bank
                )
                regs[rows, dsts[rows].to(torch.long)] = out

    vals = regs[:, 7].to("cpu").tolist()
    return [
        float(v) if bool(valid[i]) and math.isfinite(float(v)) else float("-inf")
        for i, v in enumerate(vals)
    ]


def score_batch_torch(
    programs: object,
    features_batch: object,
    contexts_batch: object,
    device: object | None = None,
) -> list[float]:
    """Score a batch of (program, features, context) triples.

    CUDA path executes the same v1 priority semantics vectorized on `device`;
    otherwise (or on any GPU failure) delegates item-by-item to
    `constructive.evaluate_priority` on CPU. Returns Python floats in order;
    malformed items yield `-inf`, never an exception.
    """
    try:
        prog_list = list(programs)  # type: ignore[arg-type]
    except Exception:
        return []
    try:
        feat_list = list(features_batch)  # type: ignore[arg-type]
    except Exception:
        feat_list = []
    try:
        ctx_list = list(contexts_batch)  # type: ignore[arg-type]
    except Exception:
        ctx_list = []
    n = len(prog_list)
    dev = _want_gpu(device)
    if dev is None:
        out: list[float] = []
        for i in range(n):
            p = prog_list[i]
            f = feat_list[i] if i < len(feat_list) else None
            c = ctx_list[i] if i < len(ctx_list) else None
            try:
                out.append(float(evaluate_priority(p, f, c)))  # type: ignore[arg-type]
            except Exception:
                out.append(float("-inf"))
        return out
    try:
        prog_words = [_as_program_words(p) for p in prog_list]
        feat_parsed = [
            _as_float_list(feat_list[i]) if i < len(feat_list) else None for i in range(n)
        ]
        ctx_parsed = [_as_float_list(ctx_list[i]) if i < len(ctx_list) else None for i in range(n)]
        return _score_batch_gpu(prog_words, feat_parsed, ctx_parsed, dev)
    except Exception:
        out = []
        for i in range(n):
            p = prog_list[i]
            f = feat_list[i] if i < len(feat_list) else None
            c = ctx_list[i] if i < len(ctx_list) else None
            try:
                out.append(float(evaluate_priority(p, f, c)))  # type: ignore[arg-type]
            except Exception:
                out.append(float("-inf"))
        return out
