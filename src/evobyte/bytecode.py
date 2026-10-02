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
    [
        0.0,
        1.0,
        -1.0,
        2.0,
        0.5,
        3.14159,
        2.71828,
        10.0,
        0.1,
        -0.5,
        7.0,
        3.0,
        0.01,
        100.0,
        -10.0,
        0.001,
    ],
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


COMPACT_PROFILE_REVISION = 0
COMPACT_ALLOWED_OPS = (0x00, 0x01, 0x02, 0x03, 0x0F)  # NOP, ADD, SUB, MUL, CSEL


def _exact_rational(value: float) -> str:
    """Exact rational of the stored binary float value.

    Same rule the P42 checker applies, so profile constants and certified
    objects agree. Decimal slots (0.1, 0.01, 0.001) are NOT 1/10-style
    ideals; only integer slots reduce to small integers.
    """
    from fractions import Fraction as _Fraction

    return str(_Fraction(str(float(value))))


def compact_candidate_profile() -> dict:
    """Frozen P49 compact-candidate profile for polynomial_arithmetic.

    The existing v0 codec already satisfies the family (integer ids, allowed
    ops, register refs, bounded rational constants), so no codec change, no
    OPCODE_VERSION bump and no interpreter fork. Announced coverage is the
    defined grammar only, never universal mathematics.
    """
    bank = [float(c) for c in list(CONST_BANK)]
    approximate = {i for i, c in enumerate(bank) if i in (5, 6)}
    return {
        "profile": "p49-compact-polynomial",
        "profile_revision": COMPACT_PROFILE_REVISION,
        "opcode_version": int(OPCODE_VERSION),
        "word_count": int(N_INSTR),
        "word_bits": 32,
        "program_bytes": int(BYTES_PER_CANDIDATE),
        "registers": int(N_REGS),
        "output_register": 7,
        "allowed_ops": [{"code": int(op), "name": OPCODES[op]} for op in COMPACT_ALLOWED_OPS],
        "constants": [
            {
                "index": i,
                "float32": c,
                "exact": (
                    "approximate-transcendental-slot" if i in approximate else _exact_rational(c)
                ),
            }
            for i, c in enumerate(bank)
        ],
        "coverage": "grammar-defined only: Horner degree<=3 / expression trees "
        "depth<=3 over bank rationals; text/Lean/SymPy live only at the "
        "certification boundary",
    }


def compact_encode(program: np.ndarray) -> bytes:
    """Encode validated words to the 64-byte compact form."""
    words = np.ascontiguousarray(np.asarray(program, dtype=np.uint32))
    if words.shape != (N_INSTR,):
        raise ValueError(f"compact form needs exactly {N_INSTR} words")
    return words.tobytes()


def compact_decode(blob: bytes) -> np.ndarray:
    """Decode the 64-byte compact form back to words (length-checked)."""
    if len(blob) != BYTES_PER_CANDIDATE:
        raise ValueError(f"compact form needs exactly {BYTES_PER_CANDIDATE} bytes, got {len(blob)}")
    return np.frombuffer(bytes(blob), dtype=np.uint32).copy()


def validate_compact_candidate(program: np.ndarray, opcode_version: int = OPCODE_VERSION) -> dict:
    """Validate a compact candidate: version, shape, refs, S0 rules."""
    reasons: list[str] = []
    if int(opcode_version) != int(OPCODE_VERSION):
        reasons.append(
            f"unknown_opcode_version: got {opcode_version!r}, frozen codec is {int(OPCODE_VERSION)}"
        )
        return {"ok": False, "reasons": reasons}
    words = np.asarray(program)
    if words.shape != (N_INSTR,) or words.dtype != np.uint32:
        reasons.append(f"bad_shape_or_dtype: {words.shape}/{words.dtype}")
        return {"ok": False, "reasons": reasons}
    for i, word in enumerate(words):
        op, dst, a, _b = decode_instr(word)
        if op not in OPCODES:
            reasons.append(f"slot {i}: unknown opcode {op:#x}")
        if dst >= N_REGS or a >= N_REGS:
            reasons.append(f"slot {i}: register out of range dst={dst} a={a}")
        if op not in COMPACT_ALLOWED_OPS and op in OPCODES:
            reasons.append(f"slot {i}: opcode {OPCODES[op]} outside the compact profile")
    if not is_valid(words):
        reasons.append("s0_validity_failed")
    return {"ok": not reasons, "reasons": reasons}


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
