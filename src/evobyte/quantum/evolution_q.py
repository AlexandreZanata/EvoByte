"""Evolutionary conserved-operator search (spec: docs/quantum/ROADMAP.md, Q05 scope).

Genetic operators (mutation, crossover, selection, random injection),
novelty archive tracking, and loop runner for discovering exact conserved
quantities without prior symmetry knowledge.
"""

from __future__ import annotations

import time
from typing import Any

import numpy as np

from evobyte.quantum.hamiltonians import (
    PauliTerm,
    commutes_bitwise,
    hamiltonian_hash,
)
from evobyte.quantum.pauli import Pauli
from evobyte.quantum.search import (
    COEFF_BANK,
    COMPLEXITY_W,
    fitness,
    sample_candidate,
    sample_structured_term,
)

NOVELTY_W = 1e-4


def mutate_term(
    term: PauliTerm, n_qubits: int, rng: np.random.Generator, p_bit: float = 0.25
) -> PauliTerm:
    """Mutate masks and/or coefficient of a single PauliTerm."""
    xm = term.x_mask
    zm = term.z_mask
    coeff = term.coeff

    # 1. Mask mutation: flip or change Pauli on selected qubits
    for q in range(n_qubits):
        if rng.random() < p_bit:
            action = int(rng.integers(0, 4))
            bit = 1 << q
            if action == 0:  # clear to I
                xm &= ~bit
                zm &= ~bit
            elif action == 1:  # set to X
                xm |= bit
                zm &= ~bit
            elif action == 2:  # set to Z
                xm &= ~bit
                zm |= bit
            else:  # set to Y
                xm |= bit
                zm |= bit

    # 2. Coefficient mutation
    if rng.random() < 0.3:
        coeff = COEFF_BANK[int(rng.integers(0, len(COEFF_BANK)))]

    phase = (xm & zm).bit_count() % 4
    return PauliTerm(coeff, int(xm), int(zm), phase)


def mutate_candidate(
    cand: list[PauliTerm],
    n_qubits: int,
    rng: np.random.Generator,
    p_term: float = 0.4,
    p_replace: float = 0.2,
) -> list[PauliTerm]:
    """Mutate candidate terms or replace a term with structured sampling."""
    res = []
    for t in cand:
        if rng.random() < p_replace:
            # Replace with a fresh structured term
            res.append(sample_structured_term(rng, n_qubits))
        elif rng.random() < p_term:
            res.append(mutate_term(t, n_qubits, rng))
        else:
            res.append(t)
    return res


def crossover_candidates(
    parent_a: list[PauliTerm], parent_b: list[PauliTerm], rng: np.random.Generator
) -> tuple[list[PauliTerm], list[PauliTerm]]:
    """Term-level crossover between two candidates of identical length."""
    if len(parent_a) != len(parent_b):
        raise ValueError("parents must have equal length for crossover")
    n_terms = len(parent_a)
    if n_terms <= 1:
        return list(parent_a), list(parent_b)

    pt = int(rng.integers(1, n_terms))
    child_a = list(parent_a[:pt] + parent_b[pt:])
    child_b = list(parent_b[:pt] + parent_a[pt:])
    return child_a, child_b


def tournament_select(
    population: list[list[PauliTerm]],
    fitness_scores: list[float],
    rng: np.random.Generator,
    k: int = 3,
) -> list[PauliTerm]:
    """Select candidate with minimum fitness score among k random tournament contestants."""
    pop_len = len(population)
    contestants = rng.choice(pop_len, size=min(k, pop_len), replace=False)
    best_idx = min(contestants, key=lambda idx: fitness_scores[idx])
    return population[best_idx]


class ConservedArchive:
    """Tracks unique operator topologies and records elite discoveries."""

    def __init__(self, max_size: int = 100) -> None:
        self.max_size = max_size
        self.elites: list[dict[str, Any]] = []
        self._topology_counts: dict[tuple[tuple[int, int], ...], int] = {}

    def get_topology(self, cand: list[PauliTerm]) -> tuple[tuple[int, int], ...]:
        return tuple(sorted((t.x_mask, t.z_mask) for t in cand))

    def novelty_score(self, cand: list[PauliTerm]) -> float:
        top = self.get_topology(cand)
        count = self._topology_counts.get(top, 0)
        return 1.0 / (1.0 + float(count))

    def add(self, cand: list[PauliTerm], error: float, fit: float) -> None:
        top = self.get_topology(cand)
        self._topology_counts[top] = self._topology_counts.get(top, 0) + 1
        entry = {"candidate": cand, "commutator_error": error, "fitness": fit}
        self.elites.append(entry)
        self.elites.sort(key=lambda x: x["fitness"])
        if len(self.elites) > self.max_size:
            self.elites.pop()


def evolve_conserved_operator(
    h_terms: list[PauliTerm],
    n_qubits: int,
    pop_size: int = 60,
    generations: int = 50,
    n_terms: int = 2,
    seed: int = 0,
    p_crossover: float = 0.7,
    p_mutation: float = 0.5,
    injection_ratio: float = 0.15,
    early_stop_tol: float = 1e-7,
) -> dict[str, Any]:
    """Evolve Pauli operator candidate population towards [H, O] = 0."""
    rng = np.random.default_rng(seed)
    archive = ConservedArchive(max_size=100)
    t0 = time.perf_counter()

    # 1. Initialize population (50% structured, 50% pure)
    population: list[list[PauliTerm]] = []
    for i in range(pop_size):
        is_struct = i < (pop_size // 2)
        population.append(sample_candidate(rng, n_qubits, n_terms, structured=is_struct))

    best_ever: dict[str, Any] | None = None
    total_evals = 0

    for gen in range(generations):
        # Evaluate current population
        fitness_scores: list[float] = []
        eval_records: list[dict[str, Any]] = []

        for cand in population:
            # Stage-0 bitwise early exit for single-term candidates
            if n_terms == 1:
                t = cand[0]
                if not commutes_bitwise(h_terms, Pauli(t.x_mask, t.z_mask, t.phase, n_qubits)):
                    # Assign high penalty without dense commutator
                    err = 10.0
                    fit_score = err + COMPLEXITY_W * float(len(cand))
                    fitness_scores.append(fit_score)
                    eval_records.append({"fitness": fit_score, "commutator_error": err})
                    total_evals += 1
                    continue

            out = fitness(h_terms, cand, n_qubits)
            total_evals += 1

            # Incorporate novelty bonus into selection score
            novelty = archive.novelty_score(cand)
            adjusted_fitness = out["fitness"] - NOVELTY_W * novelty

            fitness_scores.append(adjusted_fitness)
            eval_records.append(out)

            # Record in archive
            archive.add(cand, out["commutator_error"], out["fitness"])

            if best_ever is None or out["fitness"] < best_ever["fitness"]:
                best_ever = {
                    "candidate": cand,
                    "commutator_error": out["commutator_error"],
                    "fitness": out["fitness"],
                    "generation": gen,
                }

        # Check early stop
        if best_ever is not None and best_ever["commutator_error"] < early_stop_tol:
            break

        # 2. Reproduction
        # Elitism: carry over top 2 individuals
        sorted_indices = sorted(range(pop_size), key=lambda i: fitness_scores[i])
        new_pop: list[list[PauliTerm]] = [
            population[sorted_indices[0]],
            population[sorted_indices[1]],
        ]

        # Random injection floor
        n_injected = max(1, int(pop_size * injection_ratio))
        for _ in range(n_injected):
            new_pop.append(sample_candidate(rng, n_qubits, n_terms, structured=True))

        # Fill remaining slots via selection, crossover, mutation
        while len(new_pop) < pop_size:
            parent_a = tournament_select(population, fitness_scores, rng, k=3)
            parent_b = tournament_select(population, fitness_scores, rng, k=3)

            if rng.random() < p_crossover:
                child_a, child_b = crossover_candidates(parent_a, parent_b, rng)
            else:
                child_a, child_b = list(parent_a), list(parent_b)

            if rng.random() < p_mutation:
                child_a = mutate_candidate(child_a, n_qubits, rng)
            if rng.random() < p_mutation:
                child_b = mutate_candidate(child_b, n_qubits, rng)

            new_pop.append(child_a)
            if len(new_pop) < pop_size:
                new_pop.append(child_b)

        population = new_pop

    dt = max(time.perf_counter() - t0, 1e-9)
    assert best_ever is not None

    return {
        "best_candidate": best_ever["candidate"],
        "commutator_error": best_ever["commutator_error"],
        "fitness": best_ever["fitness"],
        "generation": best_ever["generation"],
        "generations_run": gen + 1,
        "evaluations": total_evals,
        "qvps": total_evals / dt,
        "elapsed_s": dt,
        "seed": seed,
        "success": best_ever["commutator_error"] < early_stop_tol,
        "archive_size": len(archive.elites),
        "hamiltonian_hash": hamiltonian_hash(h_terms),
    }
