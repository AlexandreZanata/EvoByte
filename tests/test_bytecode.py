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
