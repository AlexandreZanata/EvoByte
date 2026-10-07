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


# ==============================================================================
# P67 entrega 1 — H06 macros como referências a blocos existentes
# ==============================================================================
#
# Sem mudança de opcode/codec/semântica (sem ADR, sem bump de versão):
# macros são referências a sequências existentes, expandidas antes da
# execução. Mineração conta subsequências não-NOP canônicas (registradores
# renomeados por primeira aparição) em programas development, top ≤ 32.
# Equivalência macro≡expansão vale por construção (mesmo stream sob o
# intérprete congelado) e é demonstrada por round-trip + execução igual.

P67_MAX_MACROS = 32

P67_MACRO_MIN_LEN = 2

P67_MACRO_MAX_LEN = 4


def p67_canonical_seq(words: list[int]) -> tuple[tuple[int, int, int, int], ...]:
    """Canonical form: opcodes and b-bytes kept, registers remapped by order
    of first appearance (same shape, different registers → same macro)."""
    remap: dict[int, int] = {}
    out = []
    for word in words:
        op, dst, a, b = decode_instr(np.uint32(word))
        for reg in (dst, a):
            if reg not in remap:
                remap[reg] = len(remap)
        out.append((op, remap[dst], remap[a], b))
    return tuple(out)


def p67_mine_macros(
    programs: list[np.ndarray],
    min_len: int = P67_MACRO_MIN_LEN,
    max_len: int = P67_MACRO_MAX_LEN,
    top_k: int = P67_MAX_MACROS,
) -> list[dict[str, object]]:
    """Mine recurrent non-NOP subsequences (deterministic, exact counts)."""
    from collections import Counter as _Counter

    counts: _Counter[tuple[tuple[int, int, int, int], ...]] = _Counter()
    first_seen: dict[tuple[tuple[int, int, int, int], ...], list[int]] = {}
    for prog in programs:
        words = [int(w) for w in np.asarray(prog, dtype=np.uint32).tolist()]
        body = [w for w in words if decode_instr(np.uint32(w))[0] != 0x00]
        for size in range(int(min_len), int(max_len) + 1):
            for i in range(len(body) - size + 1):
                window = body[i : i + size]
                key = p67_canonical_seq(window)
                counts[key] += 1
                if key not in first_seen:
                    first_seen[key] = window
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], len(kv[0]), kv[0]))
    macros = []
    for idx, (key, count) in enumerate(ranked[: int(top_k)]):
        expansion = first_seen[key]
        regs = sorted(
            {decode_instr(np.uint32(w))[1] for w in expansion}
            | {decode_instr(np.uint32(w))[2] for w in expansion}
        )
        macros.append(
            {
                "id": f"M{idx:02d}",
                "length": len(expansion),
                "count": int(count),
                "canonical": [list(t) for t in key],
                "expansion": [int(w) for w in expansion],
                "domain": {
                    "registers": regs,
                    "n_regs": N_REGS,
                    "opcode_version": OPCODE_VERSION,
                },
            }
        )
    return macros


def p67_expand_tokens(
    tokens: list[tuple[str, object]], macros: list[dict[str, object]]
) -> np.ndarray | None:
    """Expand (\"instr\", word) / (\"macro\", id) tokens into a 16-slot program.

    Returns None when the expansion overflows the program or references an
    unknown macro or invalid word (never silently truncates).
    """
    by_id = {str(m["id"]): m for m in macros}
    words: list[int] = []
    for kind, payload in tokens:
        if kind == "instr":
            words.append(int(payload))  # type: ignore[arg-type]
        elif kind == "macro":
            macro = by_id.get(str(payload))
            if macro is None:
                return None
            words.extend(int(w) for w in macro["expansion"])  # type: ignore[union-attr]
        else:
            return None
    if len(words) > N_INSTR:
        return None
    for word in words:
        op, dst, a, _b = decode_instr(np.uint32(word))
        if op not in OPCODES or dst >= N_REGS or a >= N_REGS:
            return None
    prog = nop_program()
    prog[: len(words)] = np.asarray(words, dtype=np.uint32)
    return prog


def p67_compress_program(
    program: np.ndarray, macros: list[dict[str, object]]
) -> list[tuple[str, object]]:
    """Greedy longest-match compression of non-NOP runs (deterministic)."""
    words = [int(w) for w in np.asarray(program, dtype=np.uint32).tolist()]
    table = sorted(
        ((m["id"], [int(w) for w in m["expansion"]]) for m in macros),  # type: ignore[union-attr]
        key=lambda kv: (-len(kv[1]), str(kv[0])),
    )
    tokens: list[tuple[str, object]] = []
    i = 0
    while i < len(words):
        op, _, _, _ = decode_instr(np.uint32(words[i]))
        if op == 0x00:
            i += 1
            continue
        hit = None
        for mid, expansion in table:
            if words[i : i + len(expansion)] == expansion:
                hit = (mid, len(expansion))
                break
        if hit is None:
            tokens.append(("instr", words[i]))
            i += 1
        else:
            tokens.append(("macro", hit[0]))
            i += hit[1]
    return tokens


# ==============================================================================
# P67 entrega 2 — H06 comparação de bibliotecas com custos
# ==============================================================================
#
# Aprendida (minerada) × clássica de mesmo tamanho × aleatória. Clássica =
# idiomas fixos documentados (quadrado, dobro, negação, deslocamento…);
# aleatória = bigramas seedados. Custos de mineração, verificação
# (equivalência de cada macro) e expansão faturados por biblioteca; sem
# mineração no final. Compactação e certificado são medidas separadas:
# aqui só compactação + round-trip.

P67_CLASSICAL_SHAPES = (
    ((0x03, 0, 0), (0x01, 0, 0)),
    ((0x03, 0, 0), (0x02, 0, 0)),
    ((0x01, 0, 1), (0x01, 0, 0)),
    ((0x0C, 0, 0), (0x01, 0, 0)),
    ((0x0A, 0, 0), (0x03, 0, 0)),
    ((0x02, 0, 1), (0x02, 0, 0)),
    ((0x03, 0, 1), (0x0C, 0, 0)),
    ((0x01, 0, 2), (0x03, 0, 0)),
)


def p67_classical_library(size: int) -> list[dict[str, object]]:
    """Frozen classical idioms over r0–r2, truncated to the requested size."""
    macros = []
    for idx, shape in enumerate(P67_CLASSICAL_SHAPES[: int(size)]):
        expansion = [int(encode_instr(op, dst=2, a=reg, b=1)) for op, reg, _ in shape]
        macros.append(
            {
                "id": f"C{idx:02d}",
                "length": len(expansion),
                "count": 0,
                "canonical": [list(t) for t in p67_canonical_seq(expansion)],
                "expansion": expansion,
                "domain": {"registers": [0, 2], "n_regs": N_REGS, "opcode_version": OPCODE_VERSION},
            }
        )
    return macros


def p67_random_library(size: int, seed: int = 0) -> list[dict[str, object]]:
    """Seeded random bigrams over safe arithmetic ops (honest weak baseline)."""
    import random as _random

    rng = _random.Random(int(seed))
    ops = [0x01, 0x02, 0x03, 0x0C]
    macros = []
    for idx in range(int(size)):
        expansion = [
            int(encode_instr(rng.choice(ops), dst=rng.randint(0, 7), a=rng.randint(0, 7), b=1)),
            int(encode_instr(rng.choice(ops), dst=rng.randint(0, 7), a=rng.randint(0, 7), b=1)),
        ]
        macros.append(
            {
                "id": f"R{idx:02d}",
                "length": len(expansion),
                "count": 0,
                "canonical": [list(t) for t in p67_canonical_seq(expansion)],
                "expansion": expansion,
                "domain": {"registers": [0, 7], "n_regs": N_REGS, "opcode_version": OPCODE_VERSION},
            }
        )
    return macros


def p67_compare_libraries(
    programs: list[np.ndarray], library_size: int = 8, seed: int = 0
) -> dict[str, object]:
    """Learned vs same-size classical vs random: compression plus billed costs."""
    import time as _time

    libs: dict[str, list[dict[str, object]]] = {}
    costs: dict[str, dict[str, float]] = {}
    t0 = _time.perf_counter()
    libs["learned"] = p67_mine_macros(programs, top_k=int(library_size))
    costs["learned"] = {"mine_sec": _time.perf_counter() - t0}
    t0 = _time.perf_counter()
    libs["classical"] = p67_classical_library(len(libs["learned"]))
    costs["classical"] = {"mine_sec": _time.perf_counter() - t0}
    t0 = _time.perf_counter()
    libs["random"] = p67_random_library(len(libs["learned"]), seed=int(seed))
    costs["random"] = {"mine_sec": _time.perf_counter() - t0}
    out: dict[str, object] = {}
    for name, lib in libs.items():
        t1 = _time.perf_counter()
        verified = 0
        for macro in lib:
            rebuilt = p67_expand_tokens([("macro", macro["id"])], lib)
            if rebuilt is not None and [int(w) for w in rebuilt if decode_instr(w)[0] != 0x00] == [
                int(w)
                for w in macro["expansion"]  # type: ignore[union-attr]
            ]:
                verified += 1
        verify_sec = _time.perf_counter() - t1
        t1 = _time.perf_counter()
        ratios = []
        roundtrip = 0
        for prog in programs:
            tokens = p67_compress_program(prog, lib)
            rebuilt = p67_expand_tokens(tokens, lib)
            body = [
                int(w) for w in np.asarray(prog).tolist() if decode_instr(np.uint32(w))[0] != 0x00
            ]
            if (
                rebuilt is not None
                and [
                    int(w)
                    for w in np.asarray(rebuilt).tolist()
                    if decode_instr(np.uint32(w))[0] != 0x00
                ]
                == body
            ):
                roundtrip += 1
                ratios.append(1.0 - len(tokens) / max(1, len(body)))
        expand_sec = _time.perf_counter() - t1
        out[name] = {
            "size": len(lib),
            "mine_sec": costs[name]["mine_sec"],
            "verified": verified,
            "verify_sec": verify_sec,
            "roundtrip_ok": roundtrip,
            "compression_mean": (sum(ratios) / len(ratios)) if ratios else 0.0,
            "expand_sec": expand_sec,
        }
    return out
