"""Unit tests for Bivariate Bicycle and 2D Lifted Product QECC Engine (P213).

Validates:
1. Exact symplectic orthogonality (HX @ HZ^T == 0 mod 2) across all constructions.
2. Exact rank and logical qubit count k = n - rank(HX) - rank(HZ).
3. Landmark reference codes:
   - Bravyi et al. (2024) [[72, 12, 6]]
   - 2D Toric codes [[8, 2, 2]], [[18, 2, 3]], [[32, 2, 4]]
   - Bivariate [[16, 2, 4]] code over Z_2 x Z_4
4. LiftedProduct2DEngine constructions from classical parity checks.
5. Throughput benchmark verifying < 5 ms per candidate latency gate.
6. Target catalogue compatibility with verify_calibration_candidate.
"""

from __future__ import annotations

import numpy as np
import pytest

from evobyte.bivariate_algebra import BivariateGroupAlgebra
from evobyte.bivariate_bicycle import (
    BivariateBicycleEngine,
    BivariateStabilizerCode,
    LiftedProduct2DEngine,
    bivariate_16_2_4,
    bravyi_72_12_6,
    toric_code_2d,
)
from evobyte.bivariate_target_catalogue import verify_calibration_candidate


def test_bivariate_bicycle_engine_initialization() -> None:
    """Test valid initialization and error handling of BivariateBicycleEngine."""
    engine = BivariateBicycleEngine(3, 4)
    assert engine.l == 3
    assert engine.m == 4
    assert engine.block_dim == 12
    assert engine.n == 24

    with pytest.raises(ValueError, match="positive"):
        BivariateBicycleEngine(0, 5)
    with pytest.raises(ValueError, match="positive"):
        BivariateBicycleEngine(5, -1)


def test_toric_code_family() -> None:
    """Test Kitaev 2D toric code family [[2 L^2, 2, L]] as bivariate bicycle codes."""
    # L = 2: [[8, 2, 2]]
    t2 = toric_code_2d(2, 2, compute_distance=True, max_weight=3)
    assert t2.n == 8
    assert t2.k == 2
    assert t2.d == 2
    assert t2.is_valid
    assert t2.is_symplectic
    assert t2.rank_x == 3
    assert t2.rank_z == 3

    # L = 3: [[18, 2, 3]]
    t3 = toric_code_2d(3, 3, compute_distance=True, max_weight=4)
    assert t3.n == 18
    assert t3.k == 2
    assert t3.d == 3
    assert t3.is_valid
    assert t3.is_symplectic
    assert t3.rank_x == 8
    assert t3.rank_z == 8

    # L = 4: [[32, 2, 4]]
    t4 = toric_code_2d(4, 4, compute_distance=False)
    assert t4.n == 32
    assert t4.k == 2
    assert t4.is_valid
    assert t4.is_symplectic
    assert t4.rank_x == 15
    assert t4.rank_z == 15


def test_bivariate_16_2_4_code() -> None:
    """Test [[16, 2, 4]] bivariate bicycle code over Z_2 x Z_4."""
    code = bivariate_16_2_4()
    assert code.n == 16
    assert code.k == 2
    assert code.d == 4
    assert code.is_valid
    assert code.is_symplectic
    assert code.rank_x == 7
    assert code.rank_z == 7

    # Check generator properties
    paulis = code.to_pauli_strings()
    assert len(paulis) == 14  # 7 X-generators + 7 Z-generators
    for p in paulis:
        assert len(p) == 16


def test_bravyi_72_12_6_reference() -> None:
    """Test Bravyi et al. (2024) [[72, 12, 6]] bivariate bicycle code."""
    code = bravyi_72_12_6(compute_distance=False)
    assert code.n == 72
    assert code.k == 12
    assert code.d == 6
    assert code.rank_x == 30
    assert code.rank_z == 30
    assert code.is_valid
    assert code.is_symplectic

    # Check sparsity and regular LDPC check weights
    assert code.sparsity > 0.90
    assert code.is_ldpc
    # In Bravyi's code, deg(A) = 3 and deg(B) = 3, so each row has weight 6
    for w in code.row_weights_x:
        assert w == 6
    for w in code.row_weights_z:
        assert w == 6

    # Test compatibility with target catalogue verifier
    catalogue_dict = code.to_catalogue_dict()
    ok, payload = verify_calibration_candidate(
        "calib_bravyi_72_12_6",
        catalogue_dict,
    )
    assert ok is True
    assert payload["k"] == 12
    assert payload["n"] == 72
    assert payload["d"] == 6


def test_symplectic_orthogonality_across_rings() -> None:
    """Test that symplectic condition HX @ HZ^T == 0 (mod 2) holds 100% across diverse rings."""
    rng = np.random.default_rng(seed=123)
    ring_configs = [
        (3, 3),  # n = 18
        (5, 2),  # n = 20
        (4, 3),  # n = 24
        (6, 6),  # n = 72
    ]

    for l, m in ring_configs:
        engine = BivariateBicycleEngine(l, m)
        for _ in range(15):
            code = engine.sample_random_code(weight_a=3, weight_b=3, rng=rng)
            assert code.is_symplectic is True
            assert code.is_valid is True
            assert code.n == 2 * l * m
            assert code.k == code.n - code.rank_x - code.rank_z
            assert code.k >= 0


def test_candidate_sampling_and_filtering() -> None:
    """Test sampling with target_k filtering and reproducible seeds."""
    engine = BivariateBicycleEngine(3, 3)  # n = 18
    rng1 = np.random.default_rng(seed=999)
    rng2 = np.random.default_rng(seed=999)

    samples1 = engine.sample_candidates(
        weight_a=2,
        weight_b=2,
        num_samples=20,
        rng=rng1,
        target_k=2,
    )
    samples2 = engine.sample_candidates(
        weight_a=2,
        weight_b=2,
        num_samples=20,
        rng=rng2,
        target_k=2,
    )

    assert len(samples1) > 0
    assert len(samples1) == len(samples2)
    for c1, c2 in zip(samples1, samples2):
        assert c1.terms_a == c2.terms_a
        assert c1.terms_b == c2.terms_b
        assert c1.k == 2


def test_fast_dimension_method() -> None:
    """Test fast_dimension method against generate_code."""
    engine = BivariateBicycleEngine(4, 2)
    terms_a = [(0, 0), (1, 1)]
    terms_b = [(2, 0), (3, 1)]

    code = engine.generate_code(terms_a, terms_b)
    rx, rz, k = engine.fast_dimension(terms_a, terms_b)

    assert rx == code.rank_x
    assert rz == code.rank_z
    assert k == code.k


def test_lifted_product_2d_engine() -> None:
    """Test LiftedProduct2DEngine on classical cyclic repetition matrices."""
    # Cyclic repetition check matrix of size 3 x 3
    H = np.array(
        [
            [1, 1, 0],
            [0, 1, 1],
            [1, 0, 1],
        ],
        dtype=np.uint8,
    )

    code = LiftedProduct2DEngine.generate_from_classical(
        H,
        H,
        compute_distance=True,
        max_weight=4,
    )
    assert code.n == 18
    assert code.k == 2
    assert code.d == 3
    assert code.is_valid
    assert code.is_symplectic
    assert code.code_family == "lifted_product_2d"

    # Test from bivariate chains
    alg = BivariateGroupAlgebra(2, 2)
    p1 = alg.from_terms([(0, 0), (1, 0)])
    p2 = alg.from_terms([(0, 0), (0, 1)])
    lp_code = LiftedProduct2DEngine.generate_from_bivariate_chains(
        p1,
        p2,
        compute_distance=False,
    )
    assert lp_code.is_valid
    assert lp_code.is_symplectic
    assert lp_code.n == 32


def test_benchmark_throughput_latency_gate() -> None:
    """Test that candidate evaluation latency is strictly < 5 ms per candidate."""
    # Test on n = 72 (largest size in scope)
    engine = BivariateBicycleEngine(6, 6)
    bench = engine.benchmark_throughput(num_samples=50)

    assert bench["all_symplectic"] is True
    assert bench["latency_gate_passed"] is True
    assert bench["mean_ms"] < 5.0
    assert bench["throughput_codes_per_sec"] > 200.0


def test_code_summary_and_sparsity() -> None:
    """Test summary dictionary and LDPC sparsity properties."""
    code = toric_code_2d(3, 3, compute_distance=True, max_weight=3)
    s = code.summary()
    assert s["n"] == 18
    assert s["k"] == 2
    assert s["d"] == 3
    assert s["is_valid"] is True
    assert s["is_ldpc"] is True
    assert s["code"] == "[[18, 2, 3]]"
    assert 0.0 < s["sparsity"] < 1.0
