"""Ground-state search and variational ansatz tests (Q06 gate).

Verifies ansatz codec, variational principle bounds (E(psi) >= E_exact),
energy of known eigenstates, and evolutionary convergence with TTS/TTE.
"""

import numpy as np
import pytest

from evobyte.quantum.ground import (
    AnsatzTerm,
    decode_ansatz,
    encode_ansatz,
    energy_fitness,
    evolve_ground_state,
    sample_ansatz,
    to_statevector,
)
from evobyte.quantum.hamiltonians import heisenberg, ising, to_hamiltonian_matrix
from evobyte.quantum.oracle import energy, exact, fidelity


def test_known_eigenstate_energy_equals_e_exact():
    # 1. 2-qubit Heisenberg singlet state: (|01> - |10>) / sqrt(2)
    h_heis = heisenberg(2, j=1.0)
    owe_heis = exact(h_heis, 2)
    e_exact_heis = float(owe_heis["E_exact"])

    psi_singlet = np.zeros(4, dtype=np.complex128)
    psi_singlet[1] = 1.0 / np.sqrt(2)
    psi_singlet[2] = -1.0 / np.sqrt(2)

    e_singlet = energy(h_heis, 2, psi_singlet)
    assert abs(e_singlet - e_exact_heis) < 1e-12
    assert abs(fidelity(psi_singlet, owe_heis["psi_exact"]) - 1.0) < 1e-12

    # 2. 2-qubit Ising pure coupling (J=1, h=0): |00> has energy -1.0
    h_is_c = ising(2, j=1.0, h=0.0)
    owe_is_c = exact(h_is_c, 2)
    psi_00 = np.zeros(4, dtype=np.complex128)
    psi_00[0] = 1.0
    assert abs(energy(h_is_c, 2, psi_00) - float(owe_is_c["E_exact"])) < 1e-12

    # 3. 2-qubit Ising pure field (J=0, h=1): |++> has energy -2.0
    h_is_f = ising(2, j=0.0, h=1.0)
    owe_is_f = exact(h_is_f, 2)
    psi_plus = np.ones(4, dtype=np.complex128) / 2.0
    assert abs(energy(h_is_f, 2, psi_plus) - float(owe_is_f["E_exact"])) < 1e-12


def test_variational_principle_lower_bound():
    rng = np.random.default_rng(42)
    for n in (2, 3, 4):
        for h_terms in (heisenberg(n), ising(n)):
            owe = exact(h_terms, n)
            e_exact = float(owe["E_exact"])
            h_dense = to_hamiltonian_matrix(h_terms, n)

            for _ in range(10):
                cand = sample_ansatz(rng, n, n_terms=min(4, 1 << n))
                psi = to_statevector(cand, n)
                e_trial = energy_fitness(h_dense, psi)
                # Variational theorem: E(psi) >= E_exact
                assert e_trial >= e_exact - 1e-12, f"Variational violation: {e_trial} < {e_exact}"


def test_ansatz_codec_and_statevector():
    n = 3
    terms = [AnsatzTerm(1.0, 0, 0), AnsatzTerm(-0.5, 3, 2), AnsatzTerm(0.7071, 7, 1)]
    encoded = encode_ansatz(terms)
    decoded = decode_ansatz(encoded, n)
    assert decoded == terms

    # Mask exceeding dimension
    with pytest.raises(ValueError, match="basis_mask"):
        decode_ansatz([(1.0, 8, 0)], n_qubits=3)

    # Unit norm verification
    psi = to_statevector(terms, n)
    assert abs(np.linalg.norm(psi) - 1.0) < 1e-12


def test_ground_state_evolution_2qubit():
    h = heisenberg(2, j=1.0)
    owe = exact(h, 2)
    res = evolve_ground_state(
        h, n_qubits=2, pop_size=30, generations=20, n_terms=2, seed=0, target_energy_tol=1e-4, oracle_truth=owe
    )

    assert res["success"]
    assert abs(res["energy_candidate"] - (-3.0)) < 1e-4
    assert res["fidelity"] > 0.99
    assert res["tts_s"] is not None
    assert res["tte_evals"] is not None
    assert res["tte_evals"] >= 1
    assert res["qvps"] > 0
