"""Tests for GPU-resident evolutionary cycle (P17 scope)."""

from __future__ import annotations

import numpy as np
import pytest
import torch

from evobyte.evolution import EvolutionConfig
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
