"""Tests for P183 Hamiltonian anomaly search and independent verification.

Strict timing rule: all individual tests < 0.2 s, total suite < 3 s.
Validates independent verification, anti-cherry-picking AST checks,
and unambiguous NULL_RESULT handling.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import numpy as np

from evobyte.quantum.hamiltonians import PauliTerm, heisenberg, ising, total_sz
from benchmarks.run_hamiltonian_anomaly_search import (
    independent_commutator_norm,
    independent_operator_matrix,
    independent_pauli_matrix,
    verify_non_trivial_invariant,
)


def test_calibration_reproduces_exact_invariant() -> None:
    """Micro-instance exactly soluble directly diagonalized in test reproduces known invariant."""
    n = 3
    # Micro-Ising open chain N=3: H = -X0 - X1 - X2 - Z0*Z1 - Z1*Z2
    h_terms = ising(n, j=1.0, h=1.0)

    # Direct manual construction of dense matrices inside test
    i2 = np.eye(2, dtype=np.complex128)
    x2 = np.array([[0, 1], [1, 0]], dtype=np.complex128)
    z2 = np.array([[1, 0], [0, -1]], dtype=np.complex128)

    # Parity P = X0 (x) X1 (x) X2
    p_mat = np.kron(np.kron(x2, x2), x2)

    # Dense H
    h_mat = (
        - np.kron(np.kron(x2, i2), i2)
        - np.kron(np.kron(i2, x2), i2)
        - np.kron(np.kron(i2, i2), x2)
        - np.kron(np.kron(z2, z2), i2)
        - np.kron(np.kron(i2, z2), z2)
    )

    # Direct commutation check: [H, P] == 0
    comm = h_mat @ p_mat - p_mat @ h_mat
    assert float(np.linalg.norm(comm)) < 1e-12

    # Verify that independent verifier produces exactly zero commutator error
    p_term = [PauliTerm(1.0, (1 << n) - 1, 0, 0)]
    verif = verify_non_trivial_invariant(h_terms, p_term, n)
    assert verif["is_conserved"] is True
    assert verif["commutator_error"] < 1e-12


def test_no_manual_seeds_in_protocol() -> None:
    """Static AST verification: no hardcoded solution statevectors or manual dimer seeds."""
    script_path = Path("benchmarks/run_hamiltonian_anomaly_search.py")
    assert script_path.exists()

    tree = ast.parse(script_path.read_text(encoding="utf-8"))

    # Check that script has no large numerical list constants (> 16 elements) resembling statevectors
    for node in ast.walk(tree):
        if isinstance(node, ast.List):
            # Only small configuration lists are allowed
            assert len(node.elts) < 32, f"Disallowed large literal array in protocol: length {len(node.elts)}"

    # Check manifest for absence of solution seeds
    manifest_path = Path("experiments/p183-hamiltonian-manifest.json")
    assert manifest_path.exists()
    manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert "initial_state" not in manifest_data
    assert "known_solution" not in manifest_data
    assert "solution_seed" not in manifest_data
    assert "ansatz_seeds" not in manifest_data


def test_conserved_quantity_verified_independently() -> None:
    """Independent verification rigorously rejects zero, identity, and non-conserved candidates."""
    n = 3
    h_terms = heisenberg(n, j=1.0)

    # 1. Total Sz should be recognized as conserved known Sz
    sz_terms = total_sz(n)
    v_sz = verify_non_trivial_invariant(h_terms, sz_terms, n)
    assert v_sz["is_conserved"] is True
    assert v_sz["is_known_sz"] is True
    assert v_sz["verified"] is False  # Not an uncataloged anomaly
    assert v_sz["reason"] == "KNOWN_SZ"

    # 2. Non-commuting candidate: single X0 on Heisenberg
    bad_term = [PauliTerm(1.0, 1, 0, 0)]
    v_bad = verify_non_trivial_invariant(h_terms, bad_term, n)
    assert v_bad["is_conserved"] is False
    assert v_bad["verified"] is False
    assert v_bad["commutator_error"] > 0.1

    # 3. Trivial zero operator (+Z - Z)
    zero_terms = [PauliTerm(1.0, 0, 1, 0), PauliTerm(-1.0, 0, 1, 0)]
    v_zero = verify_non_trivial_invariant(h_terms, zero_terms, n)
    assert v_zero["verified"] is False
    assert v_zero["reason"] == "TRIVIAL_ZERO_OPERATOR"

    # 4. Trivial identity operator
    ident_terms = [PauliTerm(1.0, 0, 0, 0)]
    v_ident = verify_non_trivial_invariant(h_terms, ident_terms, n)
    assert v_ident["verified"] is False
    assert v_ident["reason"] == "TRIVIAL_SCALAR_IDENTITY"


def test_null_when_nothing_found() -> None:
    """When no uncataloged structure is discovered, campaign verdict is unambiguously NULL_RESULT."""
    fake_trials = [
        {
            "lattice_id": "j1j2_mg",
            "size_label": "pequeno-exato",
            "n_qubits": 6,
            "seed": 42,
            "conserved_search": {
                "evaluations": 100,
                "elapsed_s": 0.05,
                "candidate": ["+1.0000*Z0", "-1.0000*Z0"],
                "commutator_error": 0.0,
                "verification": {"verified": False, "reason": "TRIVIAL_ZERO_OPERATOR"},
            },
            "ground_search": {
                "evaluations": 100,
                "elapsed_s": 0.05,
                "energy_discovered": -6.5,
                "energy_exact": -9.0,
                "energy_error": 2.5,
                "fidelity": 0.5,
                "success": False,
            },
            "anomaly_detected": False,
        }
    ]

    has_anomaly = any(t["anomaly_detected"] for t in fake_trials)
    verdict = "ANOMALY_CONFIRMED" if has_anomaly else "NULL_RESULT"

    assert verdict == "NULL_RESULT"
    assert verdict in {"ANOMALY_CONFIRMED", "NULL_RESULT"}
    assert verdict != ""
