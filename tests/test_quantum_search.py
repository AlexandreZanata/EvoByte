"""Conserved-operator search engine tests (Q04 gate).

Verifies candidate codec, pure vs structured samplers, seeded reproducibility,
and baseline commutator convergence on 2-qubit models.
"""

import numpy as np
import pytest

from evobyte.quantum.hamiltonians import PauliTerm, heisenberg, ising
from evobyte.quantum.search import (
    COEFF_BANK,
    decode_candidate,
    encode_candidate,
    fitness,
    random_conserved_search,
    sample_candidate,
    sample_pure_term,
    sample_structured_term,
)


def test_codec_roundtrip():
    terms = [
        PauliTerm(1.0, 0b01, 0b00, 0),
        PauliTerm(-1.0, 0b11, 0b11, 2),
        PauliTerm(0.5, 0b00, 0b10, 0),
    ]
    encoded = encode_candidate(terms)
    assert len(encoded) == 3
    assert encoded[0] == (0, 0b01, 0b00)  # 1.0 is index 0
    assert encoded[1] == (1, 0b11, 0b11)  # -1.0 is index 1
    assert encoded[2] == (2, 0b00, 0b10)  # 0.5 is index 2

    decoded = decode_candidate(encoded, n_qubits=2)
    assert decoded == terms


def test_codec_bounds_validation():
    # Negative mask
    with pytest.raises(ValueError, match="masks must be non-negative"):
        decode_candidate([(0, -1, 0)], n_qubits=2)

    # Mask exceeds width
    with pytest.raises(ValueError, match="mask exceeds n_qubits=2 width"):
        decode_candidate([(0, 4, 0)], n_qubits=2)

    # Invalid coeff_id
    with pytest.raises(ValueError, match="coeff_id"):
        decode_candidate([(len(COEFF_BANK), 1, 0)], n_qubits=2)


def test_sample_candidate_n_terms_validation():
    rng = np.random.default_rng(0)
    for valid_n in (1, 2, 4, 8, 16):
        cand = sample_candidate(rng, 4, valid_n)
        assert len(cand) == valid_n

    for invalid_n in (0, 3, 5, 7, 9):
        with pytest.raises(ValueError, match="n_terms must be in"):
            sample_candidate(rng, 4, invalid_n)


def test_pure_vs_structured_sampling():
    rng = np.random.default_rng(42)
    n = 6

    # Structured terms on N=6 must have locality <= 2
    for _ in range(50):
        t_struct = sample_structured_term(rng, n)
        weight = (t_struct.x_mask | t_struct.z_mask).bit_count()
        assert 1 <= weight <= 2
        assert t_struct.x_mask < (1 << n)
        assert t_struct.z_mask < (1 << n)
        # Phase correctly tracks Y singles
        expected_phase = (t_struct.x_mask & t_struct.z_mask).bit_count() % 4
        assert t_struct.phase == expected_phase

    # Pure terms explore up to full weight
    weights = [
        (sample_pure_term(rng, n).x_mask | sample_pure_term(rng, n).z_mask).bit_count()
        for _ in range(100)
    ]
    assert max(weights) >= 4


def test_seeded_reproducibility():
    h = heisenberg(2)
    run1 = random_conserved_search(h, 2, budget=500, n_terms=1, seed=123, structured=True)
    run2 = random_conserved_search(h, 2, budget=500, n_terms=1, seed=123, structured=True)

    assert run1["commutator_error"] == run2["commutator_error"]
    assert run1["candidate"] == run2["candidate"]
    assert run1["fitness"] == run2["fitness"]

    # Different seeds differ
    run3 = random_conserved_search(h, 2, budget=500, n_terms=1, seed=999, structured=False)
    assert run1["seed"] != run3["seed"]


def test_random_search_finds_commuting_term_on_heisenberg():
    h = heisenberg(2)
    # Heisenberg bond XX + YY + ZZ commutes with XX, YY, ZZ
    out = random_conserved_search(h, 2, budget=1000, n_terms=1, seed=0, structured=True)
    assert out["commutator_error"] < 1e-9


def test_fitness_and_complexity():
    h = ising(2)
    cand1 = [PauliTerm(1.0, 1, 0, 0)]
    cand2 = [PauliTerm(1.0, 1, 0, 0), PauliTerm(1.0, 2, 0, 0)]
    f1 = fitness(h, cand1, 2)
    f2 = fitness(h, cand2, 2)
    assert f1["complexity"] < f2["complexity"]
    assert "fitness" in f1
    assert "commutator_error" in f1


def test_evolution_genetic_operators():
    from evobyte.quantum.evolution_q import (
        crossover_candidates,
        mutate_candidate,
        mutate_term,
        tournament_select,
    )

    rng = np.random.default_rng(100)
    term = PauliTerm(1.0, 0b01, 0b00, 0)
    mutated = mutate_term(term, n_qubits=2, rng=rng, p_bit=1.0)
    assert isinstance(mutated, PauliTerm)

    parent_a = [PauliTerm(1.0, 1, 0, 0), PauliTerm(1.0, 2, 0, 0)]
    parent_b = [PauliTerm(-1.0, 0, 1, 0), PauliTerm(-1.0, 0, 2, 0)]
    child_a, child_b = crossover_candidates(parent_a, parent_b, rng)
    assert len(child_a) == 2
    assert len(child_b) == 2

    # Tournament selection chooses lowest fitness
    pop = [parent_a, parent_b]
    scores = [10.0, 1.0]
    winner = tournament_select(pop, scores, rng, k=2)
    assert winner == parent_b


def test_evolution_random_injection_and_repeatability():
    from evobyte.quantum.evolution_q import evolve_conserved_operator

    h = heisenberg(2)

    # 1. Seeded repeatability
    run1 = evolve_conserved_operator(h, n_qubits=2, pop_size=20, generations=10, n_terms=2, seed=42)
    run2 = evolve_conserved_operator(h, n_qubits=2, pop_size=20, generations=10, n_terms=2, seed=42)

    assert run1["commutator_error"] == run2["commutator_error"]
    assert run1["fitness"] == run2["fitness"]
    assert run1["generations_run"] == run2["generations_run"]
    assert run1["best_candidate"] == run2["best_candidate"]

    # 2. Random injection floor
    # Running with injection_ratio=0.3 injects fresh candidates
    run_inj = evolve_conserved_operator(
        h, n_qubits=2, pop_size=30, generations=5, n_terms=2, seed=1, injection_ratio=0.3
    )
    assert run_inj["archive_size"] >= 1
    assert run_inj["evaluations"] >= 30
