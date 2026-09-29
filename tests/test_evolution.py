"""Evolution primitives tests (P03 gate). Seed discipline, validity bounds, reproducibility."""

import numpy as np
import pytest

from evobyte.bytecode import N_INSTR, N_REGS, OPCODES, decode_instr, is_valid
from evobyte.evolution import (
    EvolutionConfig,
    crossover_single_point,
    mutate_block,
    mutate_point,
    run_evolution,
    sample_pure,
    sample_structured,
    sample_valid,
    select_topk,
    select_tournament,
    step_generation,
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


def test_select_tournament():
    rng = np.random.default_rng(42)
    fits = np.array([10.0, 5.0, 20.0, 1.0, 50.0])
    # Tournament selection should choose the candidate with lowest fitness among sampled
    idx = select_tournament(fits, tournament_size=3, rng=rng)
    assert 0 <= idx < len(fits)
    assert fits[idx] < 50.0  # Lowest in sample


def test_select_topk():
    fits = np.array([10.0, 1.0, 5.0, 20.0])
    pop = np.zeros((4, N_INSTR), dtype=np.uint32)
    pop[1, 0] = 111  # corresponds to fit 1.0
    pop[2, 0] = 222  # corresponds to fit 5.0
    top2 = select_topk(pop, fits, k=2)
    assert len(top2) == 2
    assert top2[0, 0] == 111
    assert top2[1, 0] == 222


def test_mutate_block():
    rng = np.random.default_rng(42)
    base = sample_structured(rng)
    mut = mutate_block(base, rng, p_block=1.0, max_block_len=4)
    assert not np.array_equal(base, mut)
    for word in mut:
        op, dst, a, b = decode_instr(word)
        assert op in OPCODES
        assert dst < N_REGS
        assert a < N_REGS


def test_random_injection_floor():
    # Attempting < 10% injection should fail
    with pytest.raises(ValueError, match="random_inject_p must be >= 0.10"):
        EvolutionConfig(random_inject_p=0.05)

    # Valid config
    config = EvolutionConfig(pop_size=100, elite_k=10, random_inject_p=0.10)
    rng = np.random.default_rng(123)
    pop = np.stack([sample_structured(rng) for _ in range(100)])
    fits = np.linspace(0.1, 10.0, 100)

    next_pop = step_generation(pop, fits, config, rng)
    assert len(next_pop) == 100
    # Top 10 elites preserved verbatim
    assert np.array_equal(next_pop[:10], pop[:10])


def test_seeded_repeatability_full_loop():
    xs = np.linspace(-3.0, 3.0, 32, dtype=np.float32)
    ys = xs * xs + 2.0

    config = EvolutionConfig(pop_size=50, elite_k=5, max_generations=5)
    rng1 = np.random.default_rng(777)
    res1 = run_evolution(xs, ys, config, rng1)

    rng2 = np.random.default_rng(777)
    res2 = run_evolution(xs, ys, config, rng2)

    assert np.array_equal(res1["best_program"], res2["best_program"])
    assert res1["best_fitness"] == pytest.approx(res2["best_fitness"])
    assert res1["best_expression"] == res2["best_expression"]


def test_archive_and_checkpoint_hooks(tmp_path):
    from evobyte.archive import EliteArchive, load_checkpoint

    xs = np.linspace(-2.0, 2.0, 16, dtype=np.float32)
    ys = 2.0 * xs + 1.0

    db_path = tmp_path / "elites.db"
    ckpt_path = tmp_path / "ckpt.pkl"
    archive = EliteArchive(db_path)

    config = EvolutionConfig(
        pop_size=30,
        elite_k=4,
        max_generations=4,
        checkpoint_interval=2,
        checkpoint_path=ckpt_path,
    )
    rng = np.random.default_rng(999)

    run_evolution(xs, ys, config, rng, archive=archive)
    assert archive.count() >= 1
    archive.close()

    assert ckpt_path.exists()
    loaded = load_checkpoint(ckpt_path)
    assert loaded["generation"] == 4
    assert len(loaded["population"]) == 30
