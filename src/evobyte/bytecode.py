"""Opcode table v0 + codec + S0 validity (spec: docs/BYTECODE.md)."""

from __future__ import annotations

import numpy as np

OPCODE_VERSION = 0

N_INSTR = 16
N_REGS = 8
BYTES_PER_CANDIDATE = 64  # 16 instr x 4 bytes

OPCODES = {
    0x00: "NOP",
    0x01: "ADD",
    0x02: "SUB",
    0x03: "MUL",
    0x04: "DIV",
    0x05: "SIN",
    0x06: "COS",
    0x07: "EXP",
    0x08: "LOG",
    0x09: "POW",
    0x0A: "ABS",
    0x0B: "SQRT",
    0x0C: "NEG",
    0x0D: "MIN",
    0x0E: "MAX",
    0x0F: "CSEL",
}
NAME_TO_OP = {v: k for k, v in OPCODES.items()}

CONST_BANK = np.array(
    [0.0, 1.0, -1.0, 2.0, 0.5, 3.14159, 2.71828, 10.0,
     0.1, -0.5, 7.0, 3.0, 0.01, 100.0, -10.0, 0.001],
    dtype=np.float32,
)

# Domain-risky ops for S0 rule 4: chains longer than MAX_RISKY_CHAIN with no
# intervening bounded op are rejected before data evaluation.
RISKY_OPS = frozenset({0x04, 0x07, 0x08, 0x09, 0x0B})  # DIV, EXP, LOG, POW, SQRT
MAX_RISKY_CHAIN = 4


def encode_instr(op: int, dst: int = 7, a: int = 0, b: int = 0) -> np.uint32:
    """Pack [OP, DST, A, B] bytes into one uint32 (little-endian view)."""
    if op not in OPCODES:
        raise ValueError(f"unknown opcode: {op:#x}")
    if not (0 <= dst < N_REGS and 0 <= a < N_REGS):
        raise ValueError(f"register out of range: dst={dst} a={a}")
    if not (0 <= b < 256):
        raise ValueError(f"operand byte out of range: b={b}")
    return np.uint32((op & 0xFF) | ((dst & 0xFF) << 8) | ((a & 0xFF) << 16) | ((b & 0xFF) << 24))


def decode_instr(word: np.uint32) -> tuple[int, int, int, int]:
    """Unpack uint32 into (op, dst, a, b) bytes."""
    w = int(word)
    return (w & 0xFF, (w >> 8) & 0xFF, (w >> 16) & 0xFF, (w >> 24) & 0xFF)


def nop_program() -> np.ndarray:
    """Return a 16-slot NOP-padded program."""
    return np.zeros((N_INSTR,), dtype=np.uint32)


def is_valid(program: np.ndarray) -> bool:
    """S0 validity: shapes, ranges, one write to output, one non-NOP.

    Rule 4 (risky chains): more than MAX_RISKY_CHAIN consecutive domain-risky
    ops (DIV/EXP/LOG/POW/SQRT) with no intervening bounded op is rejected.
    NOPs are skipped: they neither extend nor reset a run. Execution still
    guards every op; this static rule only cheaply discards stacks of
    unguarded-domain ops before any data evaluation.
    """
    if program.shape != (N_INSTR,) or program.dtype != np.uint32:
        return False
    seen_non_nop = False
    output_written = False
    risky_run = 0
    for word in program:
        op, dst, a, b = decode_instr(word)
        if op not in OPCODES:
            return False
        if dst >= N_REGS or a >= N_REGS:
            return False
        if op == 0x0F and (b & 0x0F) >= len(CONST_BANK):
            return False
        if op == 0x00:
            continue
        seen_non_nop = True
        if dst == 7:
            output_written = True
        if op in RISKY_OPS:
            risky_run += 1
            if risky_run > MAX_RISKY_CHAIN:
                return False
        else:
            risky_run = 0
    return seen_non_nop and output_written


def decode_human(program: np.ndarray) -> str:
    """Human-readable form for logs only. Never used in the hot path."""
    parts = []
    for word in program:
        op, dst, a, b = decode_instr(word)
        name = OPCODES.get(op, f"OP{op:#x}")
        if name == "NOP":
            continue
        parts.append(f"{name} r{dst}, r{a}, {b:#04x}")
    return " ; ".join(parts) if parts else "NOP"
