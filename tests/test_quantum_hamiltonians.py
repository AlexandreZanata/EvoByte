"""Hamiltonian builders + oracle + conserved-operator tests (Q02/Q03 gate)."""

import numpy as np
import pytest

from evobyte.quantum.hamiltonians import (
    PauliTerm,
    commutator_norm,
    decode_hamiltonian,
    decode_term,
    energy,
    exact,
    fidelity,
    hamiltonian_hash,
    heisenberg,
    ising,
    ising_parity,
    j1j2,
    to_hamiltonian_matrix,
    total_sz,
)
from evobyte.quantum.search import random_conserved_search


def test_ising_two_qubit_golden_energies():
    # H = -ZZ (J=1, h=0): eigenvalues -1 (x2: 00, 11), +1 (x2: 01, 10).
    out = exact(ising(2, j=1.0, h=0.0), 2)
    np.testing.assert_allclose(sorted(out["energies"]), [-1.0, -1.0, 1.0, 1.0], atol=1e-12)


def test_heisenberg_bond_golden_energies():
    # XX+YY+ZZ on 2 qubits: singlet -3, triplet +1 (x3).
    out = exact(heisenberg(2, j=1.0), 2)
    np.testing.assert_allclose(sorted(out["energies"]), [-3.0, 1.0, 1.0, 1.0], atol=1e-12)


def test_term_counts_and_mask_shapes_n2_to_n6():
    for n in range(2, 7):
        # 1. Ising open chain: -J Σ ZZ - h Σ X
        # Expected: n single-X terms + (n - 1) ZZ terms = 2n - 1 terms.
        h_ising = ising(n)
        assert len(h_ising) == 2 * n - 1
        x_terms = [t for t in h_ising if t.x_mask != 0]
        zz_terms = [t for t in h_ising if t.x_mask == 0]
        assert len(x_terms) == n
        assert len(zz_terms) == n - 1
        for i, t in enumerate(x_terms):
            assert t.x_mask == (1 << i)
            assert t.z_mask == 0
            assert t.coeff == -1.0
            assert t.phase == 0
        for i, t in enumerate(zz_terms):
            assert t.x_mask == 0
            assert t.z_mask == ((1 << i) | (1 << (i + 1)))
            assert t.coeff == -1.0
            assert t.phase == 0
        for t in h_ising:
            assert t.x_mask < (1 << n)
            assert t.z_mask < (1 << n)

        # 2. Heisenberg XXX open chain: J Σ (XX + YY + ZZ)
        # Expected: 3 * (n - 1) terms.
        h_heis = heisenberg(n)
        assert len(h_heis) == 3 * (n - 1)
        for i in range(n - 1):
            bond_terms = h_heis[3 * i : 3 * (i + 1)]
            # XX term
            assert bond_terms[0].x_mask == ((1 << i) | (1 << (i + 1)))
            assert bond_terms[0].z_mask == 0
            assert bond_terms[0].phase == 0
            # YY term: carries phase 2 (two Y singles: i * i = -1)
            assert bond_terms[1].x_mask == ((1 << i) | (1 << (i + 1)))
            assert bond_terms[1].z_mask == ((1 << i) | (1 << (i + 1)))
            assert bond_terms[1].phase == 2
            # ZZ term
            assert bond_terms[2].x_mask == 0
            assert bond_terms[2].z_mask == ((1 << i) | (1 << (i + 1)))
            assert bond_terms[2].phase == 0
        for t in h_heis:
            assert t.x_mask < (1 << n)
            assert t.z_mask < (1 << n)

        # 3. J1-J2 open chain: J1 NN + J2 NNN (n >= 3)
        if n >= 3:
            h_j1j2 = j1j2(n)
            # Expected: 3 * (n - 1) + 3 * (n - 2) = 6n - 9
            assert len(h_j1j2) == 6 * n - 9
            for t in h_j1j2:
                assert t.x_mask < (1 << n)
                assert t.z_mask < (1 << n)


def test_builder_validation_errors():
    with pytest.raises(ValueError, match="ising needs n >= 2"):
        ising(1)
    with pytest.raises(ValueError, match="ising needs n >= 2"):
        ising(0)
    with pytest.raises(ValueError, match="ising needs n >= 2"):
        ising(-1)

    with pytest.raises(ValueError, match="heisenberg needs n >= 2"):
        heisenberg(1)
    with pytest.raises(ValueError, match="heisenberg needs n >= 2"):
        heisenberg(-2)

    with pytest.raises(ValueError, match="j1j2 needs n >= 3"):
        j1j2(2)
    with pytest.raises(ValueError, match="j1j2 needs n >= 3"):
        j1j2(1)


def test_builder_custom_parameters():
    h_is = ising(3, j=2.5, h=0.75)
    for t in h_is[:3]:
        assert t.coeff == -0.75
    for t in h_is[3:]:
        assert t.coeff == -2.5

    h_he = heisenberg(3, j=-1.5)
    for t in h_he:
        assert t.coeff == -1.5

    h_j = j1j2(4, j1=2.0, j2=0.5)
    nn_terms = h_j[:9]
    nnn_terms = h_j[9:]
    assert all(t.coeff == 2.0 for t in nn_terms)
    assert all(t.coeff == 0.5 for t in nnn_terms)


def test_hamiltonian_hermiticity_n2_to_n6():
    for n in range(2, 7):
        m_is = to_hamiltonian_matrix(ising(n), n)
        np.testing.assert_allclose(m_is, m_is.conj().T, atol=1e-12)

        m_he = to_hamiltonian_matrix(heisenberg(n), n)
        np.testing.assert_allclose(m_he, m_he.conj().T, atol=1e-12)

        if n >= 3:
            m_j = to_hamiltonian_matrix(j1j2(n), n)
            np.testing.assert_allclose(m_j, m_j.conj().T, atol=1e-12)


def test_decode_hamiltonian_and_terms():
    assert decode_hamiltonian([], 2) == "0"
    term = PauliTerm(-1.0, 1, 0, 0)
    assert decode_term(term, 2) == "-1.0000*X0"

    h2 = ising(2)
    dec = decode_hamiltonian(h2, 2)
    assert "-1.0000*X0" in dec
    assert "-1.0000*X1" in dec
    assert "-1.0000*Z0 Z1" in dec


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


def test_known_symmetries_isolated_from_search():
    # 1. Mathematical symmetry verification
    for n in (2, 3, 4):
        # Ising parity Π Xi
        p = ising_parity(n)
        assert commutator_norm(ising(n), [PauliTerm(1.0, p.x_mask, 0)], n) < 1e-9

        # Heisenberg SU(2): Sx, Sy, Sz
        # Sz: Σ Zi
        assert commutator_norm(heisenberg(n), total_sz(n), n) < 1e-9
        # Sx: Σ Xi
        sx = [PauliTerm(1.0, 1 << i, 0) for i in range(n)]
        assert commutator_norm(heisenberg(n), sx, n) < 1e-9
        # Sy: Σ Yi (each Y single carries phase 1)
        sy = [PauliTerm(1.0, 1 << i, 1 << i, 1) for i in range(n)]
        assert commutator_norm(heisenberg(n), sy, n) < 1e-9

    # 2. Review checklist: search code paths must NOT import or leak known symmetries
    import evobyte.quantum.search as search_mod

    with open(search_mod.__file__, "r", encoding="utf-8") as f:
        src = f.read()
    assert "total_sz" not in src
    assert "ising_parity" not in src
