"""Hamiltonian builders + oracle + conserved-operator tests (Q02/Q03 gate)."""

import numpy as np

from evobyte.quantum.hamiltonians import (
    PauliTerm,
    commutator_norm,
    energy,
    exact,
    fidelity,
    hamiltonian_hash,
    heisenberg,
    ising,
    ising_parity,
    j1j2,
    total_sz,
)
from evobyte.quantum.pauli import Pauli
from evobyte.quantum.search import random_conserved_search


def test_ising_two_qubit_golden_energies():
    # H = -ZZ (J=1, h=0): eigenvalues -1 (x2: 00, 11), +1 (x2: 01, 10).
    out = exact(ising(2, j=1.0, h=0.0), 2)
    np.testing.assert_allclose(sorted(out["energies"]), [-1.0, -1.0, 1.0, 1.0], atol=1e-12)


def test_heisenberg_bond_golden_energies():
    # XX+YY+ZZ on 2 qubits: singlet -3, triplet +1 (x3).
    out = exact(heisenberg(2, j=1.0), 2)
    np.testing.assert_allclose(sorted(out["energies"]), [-3.0, 1.0, 1.0, 1.0], atol=1e-12)


def test_term_counts():
    assert len(ising(4)) == 4 + 3
    assert len(heisenberg(4)) == 3 * 3
    assert len(j1j2(4)) == 3 * 3 + 3 * 2


def test_total_sz_commutes_with_heisenberg():
    assert commutator_norm(heisenberg(3), total_sz(3), 3) < 1e-9


def test_parity_commutes_with_ising():
    n = 3
    p = ising_parity(n)
    assert commutator_norm(ising(n), [PauliTerm(1.0, p.x_mask, 0)], n) < 1e-9


def test_ground_energy_matches_expectation():
    h = heisenberg(3)
    out = exact(h, 3)
    assert abs(energy(h, 3, out["psi_exact"]) - out["E_exact"]) < 1e-9
    assert abs(fidelity(out["psi_exact"], out["psi_exact"]) - 1.0) < 1e-12


def test_hash_stable():
    assert hamiltonian_hash(heisenberg(3)) == hamiltonian_hash(heisenberg(3))
    assert hamiltonian_hash(heisenberg(3)) != hamiltonian_hash(ising(3))


def test_random_search_finds_commuting_term():
    # 2-qubit Heisenberg bond: XX, YY, ZZ commute -> seeded 1-term search must hit norm 0.
    h = heisenberg(2)
    out = random_conserved_search(h, 2, budget=2000, n_terms=1, seed=0)
    assert out["commutator_error"] < 1e-9
