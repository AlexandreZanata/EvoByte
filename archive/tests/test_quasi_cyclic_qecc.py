"""Unit tests for Quasi-Cyclic & Lifted Product Non-Circulant QECC Engine (P203).

Validates:
1. 100% symplectic commutativity rate for bicirculant and lifted product constructions.
2. Exact agreement between fast css_exact_distance and independent qecc_verifier.code_distance.
3. Breaking the circulant barrier: discovery/verification of [[16, 2, 4]] CSS code.
4. Correctness of target_k basis adjustment and generator independence.
5. Lifted product code generation from classical parity check matrices.
"""

from __future__ import annotations

import numpy as np

from evobyte.qecc_verifier import check_stabilizer, code_distance
from evobyte.quasi_cyclic_qecc import (
    BicirculantQECCEngine,
    LiftedProductQECCEngine,
    css_exact_distance,
    gf2_rank,
    verify_symplectic_orthogonality,
)


def test_bicirculant_100_percent_commutativity() -> None:
    """Validate that bicirculant construction achieves 100% commutativity."""
    rng = np.random.default_rng(42)
    for L in [5, 6, 7, 8, 9, 11, 13]:
        engine = BicirculantQECCEngine(L)
        for _ in range(25):
            wa = int(rng.integers(1, L))
            wb = int(rng.integers(1, L))
            ra, rb = engine.sample_random_rows(wa, wb, rng)
            code = engine.generate_code(ra, rb)
            assert code.is_valid, f"Invalid code generated for L={L}"
            assert verify_symplectic_orthogonality(code.HX, code.HZ)


def test_css_distance_matches_verifier_on_calibrations() -> None:
    """Validate that css_exact_distance matches qecc_verifier on Steane [[7, 1, 3]]."""
    # Steane code HX and HZ matrices
    HX = np.array(
        [
            [0, 0, 0, 1, 1, 1, 1],
            [0, 1, 1, 0, 0, 1, 1],
            [1, 0, 1, 0, 1, 0, 1],
        ],
        dtype=np.uint8,
    )
    HZ = np.copy(HX)

    # Fast evaluator
    d_fast, dx_fast, dz_fast = css_exact_distance(HX, HZ, max_weight=5)
    assert d_fast == 3
    assert dx_fast == 3
    assert dz_fast == 3

    # Independent verifier
    gens = [
        "IIIXXXX",
        "IXXIIXX",
        "XIXIXIX",
        "IIIZZZZ",
        "IZZIIZZ",
        "ZIZIZIZ",
    ]
    ok, res = check_stabilizer(gens)
    assert ok
    ok_d, res_d = code_distance(gens)
    assert ok_d
    assert res_d["n"] == 7
    assert res_d["k"] == 1
    assert res_d["d"] == 3


def test_falsifiable_circulant_barrier_broken_16_2_4() -> None:
    """Validate that bicirculant engine finds a [[16, 2, 4]] code breaking d <= 3."""
    engine = BicirculantQECCEngine(8)
    ra = [0, 0, 0, 0, 0, 0, 1, 1]
    rb = [0, 1, 0, 0, 1, 0, 0, 0]

    code = engine.generate_code(ra, rb, compute_d=True, max_weight=4)
    assert code.n == 16
    assert code.k == 2
    assert code.d == 4

    # Double check with independent general qecc_verifier
    pauli_gens = code.to_pauli_strings()
    assert len(pauli_gens) == 14  # 7 X + 7 Z
    ok_stab, stab_info = check_stabilizer(pauli_gens)
    assert ok_stab, f"Stabilizer check failed: {stab_info}"
    assert stab_info["n"] == 16
    assert stab_info["k"] == 2

    ok_d, d_info = code_distance(pauli_gens)
    assert ok_d, f"Distance evaluation failed: {d_info}"
    assert d_info["d"] == 4, f"Expected d=4, got {d_info['d']}"


def test_bicirculant_target_k_basis_adjustment() -> None:
    """Validate target_k adjustment on n=14 and n=16."""
    rng = np.random.default_rng(2026)
    engine14 = BicirculantQECCEngine(7)
    ra, rb = engine14.sample_random_rows(2, 2, rng)

    # Base code has k=2; request k=3
    code_k3 = engine14.generate_code(ra, rb, target_k=3)
    assert code_k3.n == 14
    assert code_k3.k == 3
    assert code_k3.is_valid
    assert len(code_k3.HX) + len(code_k3.HZ) == 11  # 14 - 3 = 11 checks

    # Check stabilizer independence
    paulis = code_k3.to_pauli_strings()
    ok, info = check_stabilizer(paulis)
    assert ok
    assert info["k"] == 3


def test_lifted_product_construction() -> None:
    """Validate LiftedProductQECCEngine on classical codes."""
    # Two classical parity check matrices
    H1 = np.array([[1, 1, 0], [0, 1, 1]], dtype=np.uint8)  # repetition [3, 1]
    H2 = np.array([[1, 0, 1]], dtype=np.uint8)

    code = LiftedProductQECCEngine.generate_code(H1, H2)
    m1, n1 = H1.shape
    m2, n2 = H2.shape
    assert code.n == n1 * m2 + m1 * n2
    assert code.is_valid
    assert verify_symplectic_orthogonality(code.HX, code.HZ)


def test_gf2_rank_and_subspaces() -> None:
    """Verify GF(2) linear algebra utilities."""
    mat = np.array(
        [
            [1, 0, 1, 0],
            [0, 1, 0, 1],
            [1, 1, 1, 1],  # Row 3 = Row 1 + Row 2 (dependent)
        ],
        dtype=np.uint8,
    )
    assert gf2_rank(mat) == 2
