"""GPU-batched construction scoring equivalence and micro-batch (P175)."""

from __future__ import annotations

import numpy as np
import pytest

from evobyte.bytecode import encode_instr, nop_program
from evobyte.constructive import evaluate_priority
from evobyte.constructive_torch import (
    GPU_CPU_TOLERANCE,
    peak_vram_mb,
    score_batch_torch,
    within_tolerance,
)


def _fixed_triples(n: int = 16):
    progs, feats, ctxs = [], [], []
    for i in range(n):
        p = nop_program()
        p[0] = encode_instr(0x10, dst=2, a=0, b=i % 16)
        p[1] = encode_instr(0x11, dst=3, a=0, b=(i * 3) % 16)
        p[2] = encode_instr(0x01, dst=7, a=2, b=3)
        progs.append(p.copy())
        feats.append([float(i + j) for j in range(5)])
        ctxs.append([float(i * 2 + j) for j in range(4)])
    return progs, feats, ctxs


def test_batch_matches_single_cpu() -> None:
    progs, feats, ctxs = _fixed_triples()
    ref = [evaluate_priority(p, f, c) for p, f, c in zip(progs, feats, ctxs)]
    got = score_batch_torch(progs, feats, ctxs, device="cpu")
    assert len(got) == len(ref)
    assert all(a == b for a, b in zip(got, ref))


def test_batch_order_and_length_preserved() -> None:
    progs, feats, ctxs = _fixed_triples(8)
    # Malformed tail: NaN feature and empty program.
    bad_prog = np.array([], dtype=np.uint32)
    progs = progs + [bad_prog]
    feats = feats + [[float("nan")]]
    ctxs = ctxs + [[]]
    got = score_batch_torch(progs, feats, ctxs, device="cpu")
    assert len(got) == len(progs) == 9
    assert got[-1] == float("-inf")
    # Order preserved on the valid prefix.
    ref = [evaluate_priority(p, f, c) for p, f, c in zip(progs[:8], feats[:8], ctxs[:8])]
    assert all(a == b for a, b in zip(got[:8], ref))


def test_peak_vram_reports_or_none() -> None:
    import torch

    val = peak_vram_mb()
    if not torch.cuda.is_available():
        assert val is None
    else:
        assert isinstance(val, float) and val >= 0.0


@pytest.mark.slow
def test_gpu_parity_small_batch() -> None:
    import torch

    if not torch.cuda.is_available():
        pytest.skip("no CUDA")
    rng = np.random.default_rng(5)
    ops = [0x01, 0x02, 0x03, 0x0A, 0x0C, 0x0D, 0x0E, 0x0F, 0x10, 0x11]
    progs, feats, ctxs = [], [], []
    for _ in range(32):
        p = nop_program()
        for s in range(4):
            op = int(rng.choice(ops))
            dst, a = int(rng.integers(0, 8)), int(rng.integers(0, 8))
            b = int(rng.integers(0, 16)) if op in (0x0F, 0x10, 0x11) else int(rng.integers(0, 8))
            p[s] = encode_instr(op, dst, a, b)
        progs.append(p.copy())
        feats.append([float(rng.normal(0, 2)) for _ in range(7)])
        ctxs.append([float(rng.normal(0, 2)) for _ in range(5)])
    ref = [evaluate_priority(p, f, c) for p, f, c in zip(progs, feats, ctxs)]
    got = score_batch_torch(progs, feats, ctxs)
    assert len(got) == len(ref)
    assert GPU_CPU_TOLERANCE == 1e-5
    for a, b in zip(ref, got):
        assert within_tolerance(b, a), f"{b} vs {a}"
