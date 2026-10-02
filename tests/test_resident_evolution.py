"""Tests for GPU-resident evolutionary cycle (P17 scope)."""

from __future__ import annotations

import numpy as np
import pytest
import torch

from evobyte.evolution import EvolutionConfig
from evobyte.grammar import GrammarResidentEvolution
from evobyte.resident import (
    GPUResidentEvolution,
    gpu_crossover_single_point,
    gpu_mutate,
    gpu_sample_pure,
    gpu_sample_structured,
    gpu_tournament_selection,
)


def get_test_devices() -> list[torch.device]:
    devs = [torch.device("cpu")]
    if torch.cuda.is_available():
        devs.append(torch.device("cuda"))
    return devs


@pytest.mark.parametrize("device", get_test_devices())
def test_gpu_sample_structured_validity(device: torch.device) -> None:
    torch.manual_seed(42)
    n = 100
    progs = gpu_sample_structured(n, device=device)
    assert progs.shape == (n, 16)
    assert progs.device.type == device.type

    ops = progs & 0xFF
    dsts = (progs >> 8) & 0xFF
    as_ = (progs >> 16) & 0xFF
    bs = (progs >> 24) & 0xFF

    # Opcodes within valid 0x00..0x0F range
    assert (ops >= 0).all() and (ops <= 15).all()
    # Dsts within 0..7
    assert (dsts >= 0).all() and (dsts <= 7).all()
    # As within 0..7
    assert (as_ >= 0).all() and (as_ <= 7).all()
    # Bs within valid register/const ranges
    assert (bs >= 0).all() and (bs <= 15).all()

    # Every candidate has at least one write to r7
    has_r7 = ((dsts == 7) & (ops != 0)).any(dim=1)
    assert has_r7.all()


@pytest.mark.parametrize("device", get_test_devices())
def test_gpu_sample_pure(device: torch.device) -> None:
    n = 50
    progs = gpu_sample_pure(n, device=device)
    assert progs.shape == (n, 16)
    assert progs.device.type == device.type


@pytest.mark.parametrize("device", get_test_devices())
def test_gpu_tournament_selection(device: torch.device) -> None:
    torch.manual_seed(123)
    p_len = 100
    pop = gpu_sample_structured(p_len, device=device)
    fitness = torch.linspace(0.1, 10.0, p_len, device=device)

    winners = gpu_tournament_selection(pop, fitness, n_winners=30, tournament_size=4, pool_size=20)
    assert winners.shape == (30, 16)
    assert winners.device.type == device.type


@pytest.mark.parametrize("device", get_test_devices())
def test_gpu_crossover_and_mutation(device: torch.device) -> None:
    torch.manual_seed(999)
    p1 = gpu_sample_structured(20, device=device)
    p2 = gpu_sample_structured(20, device=device)

    c1, c2 = gpu_crossover_single_point(p1, p2, crossover_p=1.0)
    assert c1.shape == (20, 16)
    assert c2.shape == (20, 16)

    mut = gpu_mutate(c1, p_gene=0.2, p_block=0.2, p_byte=0.1)
    assert mut.shape == (20, 16)
    ops = mut & 0xFF
    # Verify opcode table clamping
    assert (ops >= 0).all() and (ops <= 15).all()


@pytest.mark.parametrize("device", get_test_devices())
def test_gpu_resident_evolution_step_and_diversity(device: torch.device) -> None:
    torch.manual_seed(42)
    xs = np.linspace(-5.0, 5.0, 32, dtype=np.float32)
    ys = xs**2 + 2.0 * xs + 1.0

    cfg = EvolutionConfig(pop_size=100, elite_k=10, random_inject_p=0.15)
    evo = GPUResidentEvolution(xs, ys, config=cfg, device=device)

    assert evo.population.device.type == device.type
    stats1 = evo.step()
    assert stats1["generation"] == 1
    assert stats1["valid_rate"] > 0.0
    assert 0.0 <= stats1["duplicate_rate"] < 1.0
    assert stats1["step_time_s"] > 0.0

    stats2 = evo.step()
    assert stats2["generation"] == 2
    assert evo.population.shape == (100, 16)
    assert evo.population.device.type == device.type


@pytest.mark.parametrize("device", get_test_devices())
def test_gpu_resident_evolution_deterministic_resume(
    device: torch.device, tmp_path: pytest.TempPathFactory
) -> None:
    xs = np.linspace(-5.0, 5.0, 32, dtype=np.float32)
    ys = xs**2 + 3.0 * xs + 7.0
    cfg = EvolutionConfig(pop_size=60, elite_k=8, max_generations=10)

    # 1. Uninterrupted run for 8 generations
    torch.manual_seed(2026)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(2026)

    evo_full = GPUResidentEvolution(xs, ys, config=cfg, device=device)
    history_full = [evo_full.step() for _ in range(8)]
    final_pop_full = evo_full.population.clone()

    # 2. Split run: 4 generations, checkpoint, resume for 4 generations
    torch.manual_seed(2026)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(2026)

    evo_part = GPUResidentEvolution(xs, ys, config=cfg, device=device)
    for _ in range(4):
        evo_part.step()

    ckpt_path = tmp_path / "resident_ckpt.pt"
    evo_part.save_checkpoint(ckpt_path)

    # Resume in new instance
    evo_resumed = GPUResidentEvolution(xs, ys, config=cfg, device=device)
    evo_resumed.load_checkpoint(ckpt_path)

    history_part2 = [evo_resumed.step() for _ in range(4)]

    # Check identical generations 5-8
    for i in range(4):
        full_stat = history_full[4 + i]
        res_stat = history_part2[i]
        assert full_stat["generation"] == res_stat["generation"]
        assert np.isclose(full_stat["best_fitness"], res_stat["best_fitness"], rtol=1e-6)
        assert np.isclose(full_stat["best_mse"], res_stat["best_mse"], rtol=1e-6)

    assert torch.equal(final_pop_full, evo_resumed.population)


def _p43_fresh_grammar(seed: int, pop_size: int = 16) -> GrammarResidentEvolution:
    import random as _random

    xs = np.linspace(-3.0, 3.0, 48, dtype=np.float32)
    ys = xs**2 + 3.0 * xs + 7.0
    cfg = EvolutionConfig(pop_size=pop_size, elite_k=4, random_inject_p=0.10)
    _random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    return GrammarResidentEvolution(xs, ys, config=cfg, device=torch.device("cpu"), seed=seed)


def test_p43_grammar_resume_matches_uninterrupted(tmp_path) -> None:
    from evobyte.grammar import rebuild_from_checkpoint
    from evobyte.resident import state_fingerprint

    straight = _p43_fresh_grammar(7)
    straight.run(max_generations=10, early_stop_mse=0.0)
    ref = state_fingerprint(straight)

    part = _p43_fresh_grammar(7)
    part.run(max_generations=4, early_stop_mse=0.0)
    ckpt = tmp_path / "grammar-exact.pt"
    part.save_checkpoint(ckpt)

    resumed = rebuild_from_checkpoint(str(ckpt), device="cpu")
    resumed.run(max_generations=6, early_stop_mse=0.0)
    got = state_fingerprint(resumed)

    assert got["generation"] == ref["generation"] == 10
    assert got["population_sha256"] == ref["population_sha256"]
    assert got["best_program_sha256"] == ref["best_program_sha256"]
    assert got["torch_cpu_rng_sha256"] == ref["torch_cpu_rng_sha256"]
    assert got["numpy_rng_sha256"] == ref["numpy_rng_sha256"]
    assert got["counters"] == ref["counters"]


def test_p43_checkpoint_refusals_are_explicit(tmp_path) -> None:
    from evobyte.grammar import rebuild_from_checkpoint
    from evobyte.resident import IncompatibleCheckpointError

    evo = _p43_fresh_grammar(11)
    evo.run(max_generations=2, early_stop_mse=0.0)
    good = tmp_path / "good.pt"
    evo.save_checkpoint(good)

    raw = good.read_bytes()
    trunc = tmp_path / "trunc.pt"
    trunc.write_bytes(raw[: len(raw) // 2])
    with pytest.raises(IncompatibleCheckpointError, match="truncated_or_unreadable"):
        rebuild_from_checkpoint(str(trunc), device="cpu")

    legacy = tmp_path / "legacy.pt"
    torch.save({"generation": 1}, legacy)
    with pytest.raises(IncompatibleCheckpointError, match="legacy_or_foreign"):
        rebuild_from_checkpoint(str(legacy), device="cpu")

    with pytest.raises(IncompatibleCheckpointError, match="version_mismatch"):
        rebuild_from_checkpoint(str(good), device="cpu", expected={"torch_version": "0.0.0"})
    with pytest.raises(IncompatibleCheckpointError, match="config_mismatch"):
        rebuild_from_checkpoint(str(good), device="cpu", expected={"config": {"pop_size": 9999}})


def test_p44_torch_mutator_validity_and_locality() -> None:
    from evobyte.grammar import (
        batch_is_valid_torch,
        grammar_mutate_batch_torch,
        sample_grammar_batch,
    )

    dev = torch.device("cpu")
    torch.manual_seed(11)
    pop = sample_grammar_batch(128, device=dev, seed=11)
    torch.manual_seed(11)
    mutated = grammar_mutate_batch_torch(pop, device=dev, p_mut=0.30)
    assert mutated.shape == pop.shape and mutated.device.type == "cpu"

    gate = batch_is_valid_torch(mutated).cpu().numpy()
    assert bool(gate.all()), "torch-mutated batch must be fully S0-valid"
    w0 = pop.cpu().numpy().astype(np.int64)
    w1 = mutated.cpu().numpy().astype(np.int64)
    changed = w0 != w1
    assert bool(((~changed) | np.isin(w0 & 0xFF, [1, 2, 15])).all())
    assert bool((((w1 >> 8) & 0xFF) < 8).all() and (((w1 >> 16) & 0xFF) < 8).all())

    torch.manual_seed(11)
    again = grammar_mutate_batch_torch(pop, device=dev, p_mut=0.30)
    assert torch.equal(mutated, again)


def test_p44_validity_gate_matches_cpu_reference() -> None:
    from evobyte.bytecode import encode_instr, is_valid, nop_program
    from evobyte.grammar import batch_is_valid_torch, sample_grammar_batch

    dev = torch.device("cpu")
    pop = sample_grammar_batch(64, device=dev, seed=5).cpu().numpy().astype(np.uint32)
    bad_reg = nop_program()
    bad_reg[0] = np.uint32(0x01 | (9 << 8))
    risky = nop_program()
    for i, op in enumerate([0x01, 0x04, 0x07, 0x08, 0x09, 0x0B]):
        risky[i] = encode_instr(op, dst=7, a=0, b=0)
    mix = np.stack([pop[0], bad_reg, risky])
    mix_t = torch.from_numpy(mix.astype(np.int64)).to(dev)
    gate = batch_is_valid_torch(mix_t).cpu().numpy()
    ref = np.array([is_valid(p) for p in mix])
    assert (gate == ref).all()
    assert gate.tolist() == [True, False, False]


def test_p44_no_host_transfer_in_resident_loop() -> None:
    import unittest.mock as _mock

    evo = _p43_fresh_grammar(7, pop_size=16)
    with (
        _mock.patch.object(
            torch.Tensor, "cpu", side_effect=AssertionError("host transfer in loop")
        ),
        _mock.patch.object(
            torch.Tensor, "numpy", side_effect=AssertionError("host transfer in loop")
        ),
    ):
        for _ in range(3):
            evo.step()
    assert evo._best_stale is True
    evo.sync_best_to_host()
    assert evo._best_stale is False
    assert evo.best_program.shape == (16,)


def test_p44_engine_determinism_per_backend() -> None:
    import random as _random

    from evobyte.evolution import EvolutionConfig
    from evobyte.grammar import GrammarResidentEvolution
    from evobyte.resident import state_fingerprint

    for dev in [torch.device("cpu")] + (
        [torch.device("cuda")] if torch.cuda.is_available() else []
    ):

        def _fresh(device: torch.device = dev) -> GrammarResidentEvolution:
            _random.seed(21)
            np.random.seed(21)
            torch.manual_seed(21)
            xs = np.linspace(-3.0, 3.0, 48, dtype=np.float32)
            ys = xs**2 + 3.0 * xs + 7.0
            cfg = EvolutionConfig(pop_size=16, elite_k=4, random_inject_p=0.10)
            return GrammarResidentEvolution(xs, ys, config=cfg, device=device, seed=21)

        first = _fresh()
        first.run(max_generations=6, early_stop_mse=0.0)
        second = _fresh()
        second.run(max_generations=6, early_stop_mse=0.0)
        fa, fb = state_fingerprint(first), state_fingerprint(second)
        assert fa["population_sha256"] == fb["population_sha256"]
