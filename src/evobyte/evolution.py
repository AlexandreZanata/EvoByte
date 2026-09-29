"""Generation primitives: pure + structured random (P03 scope)."""

from __future__ import annotations

import numpy as np

from evobyte.bytecode import N_INSTR, N_REGS, OPCODES, encode_instr, is_valid

STRUCTURED_OP_RATIOS = np.array(
    [0.25, 0.12, 0.12, 0.10, 0.06, 0.03, 0.03, 0.03, 0.02, 0.02, 0.03, 0.02, 0.03, 0.03, 0.03, 0.08],
    dtype=np.float64,
)
STRUCTURED_OP_RATIOS /= STRUCTURED_OP_RATIOS.sum()
STRUCTURED_OPS = np.array(sorted(OPCODES.keys()), dtype=np.int64)


def sample_pure(rng: np.random.Generator) -> np.ndarray:
    """Uniform random program (raw bytes, usually invalid)."""
    words = rng.integers(0, 2**32, size=(N_INSTR,), dtype=np.int64).astype(np.uint32)
    return words


def sample_structured(rng: np.random.Generator, p_nop: float = 0.35) -> np.ndarray:
    """Opcode-aware sampler: valid registers, NOP padding, output write guaranteed."""
    prog = np.zeros((N_INSTR,), dtype=np.uint32)
    n_active = int(rng.integers(2, N_INSTR + 1))
    for i in range(n_active):
        if rng.random() < p_nop:
            continue
        op = int(rng.choice(STRUCTURED_OPS, p=STRUCTURED_OP_RATIOS))
        if op == 0x00:
            continue
        dst = int(rng.integers(0, N_REGS))
        a = int(rng.integers(0, N_REGS))
        b = int(rng.integers(0, 256))
        if op == 0x0F:
            b = int(rng.integers(0, 16))
        prog[i] = encode_instr(op, dst, a, b)
    # Guarantee at least one write to r7 so S0 has a chance.
    if not any((int(w) >> 8) & 0xFF == 7 and (int(w) & 0xFF) != 0 for w in prog):
        op = int(rng.choice([0x01, 0x02, 0x03, 0x0F]))
        prog[n_active - 1] = encode_instr(op, 7, int(rng.integers(0, N_REGS)), int(rng.integers(0, 16)))
    return prog


def sample_valid(rng: np.random.Generator, structured: bool = True, max_tries: int = 100) -> np.ndarray:
    """Rejection-sample until S0-valid (bounded tries; raises on failure)."""
    sampler = sample_structured if structured else sample_pure
    for _ in range(max_tries):
        prog = sampler(rng)
        if is_valid(prog):
            return prog
    raise RuntimeError(f"no valid program in {max_tries} tries")


def mutate_point(program: np.ndarray, rng: np.random.Generator, p_byte: float = 0.02) -> np.ndarray:
    """Flip random bytes with probability p_byte per byte."""
    raw = program.view(np.uint8).copy()
    mask = rng.random(raw.shape) < p_byte
    raw[mask] = rng.integers(0, 256, size=int(mask.sum()), dtype=np.int64).astype(np.uint8)
    out = raw.view(np.uint32).copy()
    # Clamp opcodes into the known table so mutation stays in-schema.
    for i in range(N_INSTR):
        op = int(out[i]) & 0xFF
        if op not in OPCODES:
            out[i] = np.uint32((int(out[i]) & 0xFFFFFF00) | 0x00)
    return out


def crossover_single_point(a: np.ndarray, b: np.ndarray, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """Single-point crossover over 16 slots."""
    pt = int(rng.integers(1, N_INSTR))
    c1 = np.concatenate([a[:pt], b[pt:]]).astype(np.uint32)
    c2 = np.concatenate([b[:pt], a[pt:]]).astype(np.uint32)
    return c1, c2
