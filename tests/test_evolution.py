"""Evolution primitives tests (P03 gate). Seed discipline, validity bounds, reproducibility."""

import numpy as np
import pytest

from evobyte.bytecode import N_INSTR, N_REGS, OPCODES, decode_instr, is_valid
from evobyte.evolution import (
    crossover_single_point,
    mutate_point,
    sample_pure,
    sample_structured,
    sample_valid,
)


def test_sample_pure_shape_and_dtype():
    rng = np.random.default_rng(42)
    prog = sample_pure(rng)
    assert prog.shape == (N_INSTR,)
    assert prog.dtype == np.uint32


def test_sample_pure_seeded_reproducibility():
    rng1 = np.random.default_rng(12345)
    rng2 = np.random.default_rng(12345)
    p1 = sample_pure(rng1)
    p2 = sample_pure(rng2)
    assert np.array_equal(p1, p2)

    rng3 = np.random.default_rng(54321)
    p3 = sample_pure(rng3)
    assert not np.array_equal(p1, p3)


def test_sample_pure_low_validity():
    rng = np.random.default_rng(0)
    progs = [sample_pure(rng) for _ in range(100)]
    valid_count = sum(is_valid(p) for p in progs)
    # Raw random uint32 bytes should almost never produce valid programs
    assert valid_count / len(progs) <= 0.05


def test_sample_structured_shape_and_dtype():
    rng = np.random.default_rng(42)
    prog = sample_structured(rng)
    assert prog.shape == (N_INSTR,)
    assert prog.dtype == np.uint32


def test_sample_structured_seeded_reproducibility():
    rng1 = np.random.default_rng(999)
    rng2 = np.random.default_rng(999)
    p1 = sample_structured(rng1)
    p2 = sample_structured(rng2)
    assert np.array_equal(p1, p2)

    rng3 = np.random.default_rng(888)
    p3 = sample_structured(rng3)
    assert not np.array_equal(p1, p3)


def test_sample_structured_high_validity():
    rng = np.random.default_rng(100)
    n = 500
    progs = [sample_structured(rng) for _ in range(n)]
    valid_count = sum(is_valid(p) for p in progs)
    pass_rate = valid_count / n
    # Structured sampler should achieve > 95% S0 validity
    assert pass_rate >= 0.95, f"Expected >= 95% validity, got {pass_rate:.2%}"


def test_sample_structured_bounds_and_output_write():
    rng = np.random.default_rng(200)
    for _ in range(100):
        prog = sample_structured(rng)
        has_r7_write = False
        for word in prog:
            op, dst, a, b = decode_instr(word)
            assert op in OPCODES
            assert dst < N_REGS
            assert a < N_REGS
            if op == 0x0F:
                assert b < 16
            elif op != 0x00:
                assert b < N_REGS
            if dst == 7 and op != 0x00:
                has_r7_write = True
        assert has_r7_write


def test_sample_valid_structured():
    rng = np.random.default_rng(300)
    for _ in range(50):
        prog = sample_valid(rng, structured=True, max_tries=50)
        assert is_valid(prog)


def test_sample_valid_pure_fails_bounded_tries():
    rng = np.random.default_rng(400)
    with pytest.raises(RuntimeError, match="no valid program"):
        sample_valid(rng, structured=False, max_tries=10)


def test_mutate_point_seeded_reproducibility():
    rng = np.random.default_rng(42)
    base = sample_structured(rng)

    rng1 = np.random.default_rng(777)
    rng2 = np.random.default_rng(777)
    m1 = mutate_point(base, rng1, p_byte=0.05)
    m2 = mutate_point(base, rng2, p_byte=0.05)
    assert np.array_equal(m1, m2)

    # All opcodes in mutated program must stay in schema
    for word in m1:
        op, _, _, _ = decode_instr(word)
        assert op in OPCODES


def test_crossover_seeded_reproducibility():
    rng = np.random.default_rng(42)
    p1 = sample_structured(rng)
    p2 = sample_structured(rng)

    rng1 = np.random.default_rng(555)
    rng2 = np.random.default_rng(555)
    c1_a, c2_a = crossover_single_point(p1, p2, rng1)
    c1_b, c2_b = crossover_single_point(p1, p2, rng2)
    assert np.array_equal(c1_a, c1_b)
    assert np.array_equal(c2_a, c2_b)
    assert c1_a.shape == (N_INSTR,)
    assert c2_a.shape == (N_INSTR,)
