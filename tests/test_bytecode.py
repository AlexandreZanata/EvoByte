"""Bytecode codec tests (P01 gate). No GPU, no network."""

import numpy as np

from evobyte.bytecode import (
    BYTES_PER_CANDIDATE,
    CONST_BANK,
    N_INSTR,
    OPCODES,
    decode_human,
    decode_instr,
    encode_instr,
    is_valid,
    nop_program,
    p67_canonical_seq,
    p67_compress_program,
    p67_expand_tokens,
    p67_mine_macros,
)


def test_opcode_table_has_16_entries():
    assert len(OPCODES) == 16
    assert OPCODES[0x00] == "NOP"
    assert len(CONST_BANK) == 16


def test_candidate_size_math():
    assert BYTES_PER_CANDIDATE == 64
    assert N_INSTR * 4 == BYTES_PER_CANDIDATE
    # VRAM math from ARCHITECTURE.md: 1M x 64B = 64MB
    assert (1_000_000 * BYTES_PER_CANDIDATE) == 64_000_000


def test_encode_decode_roundtrip():
    w = encode_instr(0x03, dst=7, a=0, b=0)
    assert decode_instr(w) == (0x03, 7, 0, 0)


def test_nop_program_invalid():
    assert not is_valid(nop_program())


def test_valid_program_passes():
    prog = nop_program()
    prog[0] = encode_instr(0x01, dst=7, a=0, b=1)
    assert is_valid(prog)


def test_unknown_opcode_rejected():
    prog = nop_program()
    prog[0] = np.uint32(0xFF | (7 << 8))  # op 0xFF not in table
    assert not is_valid(prog)


def test_decode_human_never_empty():
    assert decode_human(nop_program()) == "NOP"


def _chain_prog(ops):
    prog = nop_program()
    for i, op in enumerate(ops):
        prog[i] = encode_instr(op, dst=7, a=0, b=1)
    return prog


def test_risky_chain_of_four_passes():
    assert is_valid(_chain_prog([0x04, 0x08, 0x09, 0x07]))


def test_risky_chain_of_five_rejected():
    assert not is_valid(_chain_prog([0x04, 0x08, 0x09, 0x07, 0x0B]))


def test_bounded_op_resets_risky_chain():
    assert is_valid(_chain_prog([0x04, 0x04, 0x04, 0x04, 0x01, 0x04, 0x04]))


def test_nop_skipped_in_risky_chain():
    prog = nop_program()
    prog[0] = encode_instr(0x04, dst=7, a=0, b=1)
    prog[1] = encode_instr(0x04, dst=7, a=0, b=1)
    # slot 2 stays NOP: skipped, run continues
    prog[3] = encode_instr(0x04, dst=7, a=0, b=1)
    prog[4] = encode_instr(0x04, dst=7, a=0, b=1)
    prog[5] = encode_instr(0x04, dst=7, a=0, b=1)
    assert not is_valid(prog)


def test_p49_compact_profile_limits():
    from evobyte.bytecode import (
        COMPACT_ALLOWED_OPS,
        OPCODE_VERSION,
        compact_candidate_profile,
    )

    profile = compact_candidate_profile()
    assert profile["profile"] == "p49-compact-polynomial"
    assert profile["opcode_version"] == OPCODE_VERSION == 0
    assert profile["program_bytes"] == 64
    assert profile["registers"] == 8 and profile["output_register"] == 7
    assert [o["code"] for o in profile["allowed_ops"]] == [0x00, 0x01, 0x02, 0x03, 0x0F]
    assert len(profile["constants"]) == 16
    exact = {c["index"]: c["exact"] for c in profile["constants"]}
    assert exact[1] == "1" and exact[3] == "2" and exact[10] == "7"
    assert "approximate" in profile["constants"][5]["exact"]
    assert "approximate" in profile["constants"][6]["exact"]
    from fractions import Fraction as _Fraction

    for i, c in enumerate(CONST_BANK):
        if i not in (5, 6):
            assert _Fraction(exact[i]) == _Fraction(str(float(c)))
    assert COMPACT_ALLOWED_OPS == (0x00, 0x01, 0x02, 0x03, 0x0F)


def test_p49_compact_roundtrip_bytes():
    from evobyte.bytecode import compact_decode, compact_encode

    prog = nop_program()
    prog[0] = encode_instr(0x03, dst=7, a=0, b=0)
    blob = compact_encode(prog)
    assert len(blob) == 64
    back = compact_decode(blob)
    assert back.dtype == np.uint32 and (back == prog).all()


def test_p49_compact_rejects_invalid_refs_and_versions():
    from evobyte.bytecode import validate_compact_candidate

    bad_reg = nop_program()
    bad_reg[0] = np.uint32(0x01 | (9 << 8))
    verdict = validate_compact_candidate(bad_reg)
    assert verdict["ok"] is False
    assert any("register" in r for r in verdict["reasons"])

    bad_op = nop_program()
    bad_op[0] = np.uint32(0xFF | (7 << 8))
    assert validate_compact_candidate(bad_op)["ok"] is False

    off_profile = nop_program()
    off_profile[0] = encode_instr(0x05, dst=7, a=0, b=0)  # SIN: S0-valid, off-profile
    verdict = validate_compact_candidate(off_profile)
    assert verdict["ok"] is False
    assert any("outside the compact profile" in r for r in verdict["reasons"])

    good = nop_program()
    good[0] = encode_instr(0x01, dst=7, a=0, b=1)
    assert validate_compact_candidate(good)["ok"] is True
    assert validate_compact_candidate(good, opcode_version=999)["ok"] is False

    try:
        from evobyte.bytecode import compact_decode as _d

        _d(b"short")
    except ValueError as exc:
        assert "64 bytes" in str(exc)
    else:
        raise AssertionError("short blob must be rejected")


def _p67_dense_programs():
    first = nop_program()
    first[0] = encode_instr(0x03, dst=2, a=0, b=0)
    first[1] = encode_instr(0x01, dst=7, a=2, b=2)
    second = nop_program()
    second[0] = encode_instr(0x03, dst=4, a=0, b=0)
    second[1] = encode_instr(0x01, dst=7, a=4, b=4)
    third = nop_program()
    third[0] = encode_instr(0x02, dst=1, a=0, b=0)
    third[1] = encode_instr(0x03, dst=2, a=0, b=0)
    third[2] = encode_instr(0x01, dst=7, a=2, b=2)
    return [first, second, third]


def test_p67_canonical_seq_renames_registers():
    a = [int(encode_instr(0x03, dst=2, a=0, b=1)), int(encode_instr(0x01, dst=7, a=2, b=1))]
    b = [int(encode_instr(0x03, dst=4, a=0, b=1)), int(encode_instr(0x01, dst=7, a=4, b=1))]
    assert p67_canonical_seq(a) == p67_canonical_seq(b)
    c = [int(encode_instr(0x02, dst=2, a=0, b=1)), int(encode_instr(0x01, dst=7, a=2, b=1))]
    assert p67_canonical_seq(a) != p67_canonical_seq(c)
    d = [int(encode_instr(0x03, dst=2, a=0, b=1)), int(encode_instr(0x01, dst=7, a=2, b=9))]
    assert p67_canonical_seq(a) != p67_canonical_seq(d)


def test_p67_mine_macros_deterministic_and_capped():
    progs = _p67_dense_programs()
    first = p67_mine_macros(progs)
    assert first == p67_mine_macros(progs)
    assert len(first) <= 32
    assert first[0]["count"] >= 2
    assert first[0]["length"] in (2, 3, 4)
    assert all(r < 8 for r in first[0]["domain"]["registers"])
    assert first[0]["domain"]["opcode_version"] == 0
    assert [m["id"] for m in first] == [f"M{i:02d}" for i in range(len(first))]


def test_p67_roundtrip_and_execution_equality():
    from evobyte.verifier import evaluate

    progs = _p67_dense_programs()
    macros = p67_mine_macros(progs)
    xs = np.linspace(-2, 2, 64, dtype=np.float32)
    ys = xs * xs
    for prog in progs:
        tokens = p67_compress_program(prog, macros)
        rebuilt = p67_expand_tokens(tokens, macros)
        assert rebuilt is not None
        assert list(np.asarray(rebuilt).tolist()) == list(np.asarray(prog).tolist())
        if is_valid(prog):
            assert evaluate(rebuilt, xs, ys)["fitness"] == evaluate(prog, xs, ys)["fitness"]


def test_p67_expand_rejects_overflow_and_unknown():
    macros = p67_mine_macros(_p67_dense_programs())
    assert p67_expand_tokens([("macro", "M99")], macros) is None
    assert p67_expand_tokens([("bogus", 0)], macros) is None
    many = [("instr", int(encode_instr(0x01, dst=7, a=0, b=0)))] * 17
    assert p67_expand_tokens(many, macros) is None
