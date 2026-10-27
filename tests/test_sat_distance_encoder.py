"""Unit tests for Exact SAT Distance and Symplectic Encoder (P204).

Validates:
1. Exact SAT verification of Steane code [[7, 1, 3]] (UNSAT for w=1, 2; SAT for w=3).
2. Exact SAT verification of Shor code [[9, 1, 3]] (UNSAT for w=1, 2; SAT for w=3).
3. Exact SAT verification of [[16, 2, 4]] code (UNSAT for w=1, 2, 3; SAT for w=4).
4. Honest refutation of false claims (e.g. verifying d >= 4 on a d=3 code returns False).
5. Exact SAT covering design search under AGL(1, 9) and AGL(1, 13).
6. Strict time budget verification (< 5 seconds per query).
"""

from __future__ import annotations

import numpy as np

from evobyte.generalized_symmetry import AffineGroup1D
from evobyte.quasi_cyclic_qecc import BicirculantQECCEngine
from evobyte.sat_distance_encoder import SATCoveringEncoder, SATDistanceEncoder


def test_sat_distance_steane_7_1_3() -> None:
    """Verify Steane [[7, 1, 3]] code distance d >= 3 via SAT."""
    HX = np.array(
        [
            [0, 0, 0, 1, 1, 1, 1],
            [0, 1, 1, 0, 0, 1, 1],
            [1, 0, 1, 0, 1, 0, 1],
        ],
        dtype=np.uint8,
    )
    HZ = np.copy(HX)

    # 1. Verification of lower bound d >= 3
    res_bound = SATDistanceEncoder.verify_distance_bound((HX, HZ), target_distance=3)
    assert res_bound.distance_verified is True
    assert res_bound.proven_distance_lower_bound == 3
    assert res_bound.solve_time_seconds < 1.0

    # 2. Exact distance search
    res_exact = SATDistanceEncoder.find_exact_distance((HX, HZ), max_search=4)
    assert res_exact.exact_distance == 3
    assert res_exact.solve_time_seconds < 1.0


def test_sat_distance_shor_9_1_3() -> None:
    """Verify Shor [[9, 1, 3]] code distance d >= 3 via SAT."""
    HX = np.array(
        [
            [1, 1, 1, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 1, 1, 1, 1, 1, 1],
        ],
        dtype=np.uint8,
    )
    HZ = np.array(
        [
            [1, 1, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 1, 1],
        ],
        dtype=np.uint8,
    )

    res_bound = SATDistanceEncoder.verify_distance_bound((HX, HZ), target_distance=3)
    assert res_bound.distance_verified is True
    assert res_bound.proven_distance_lower_bound == 3
    assert res_bound.solve_time_seconds < 1.0

    res_exact = SATDistanceEncoder.find_exact_distance((HX, HZ), max_search=4)
    assert res_exact.exact_distance == 3


def test_sat_distance_bicirculant_16_2_4() -> None:
    """Verify [[16, 2, 4]] code distance d >= 4 via SAT."""
    engine = BicirculantQECCEngine(8)
    ra = [0, 0, 0, 0, 0, 0, 1, 1]
    rb = [0, 1, 0, 0, 1, 0, 0, 0]
    code = engine.generate_code(ra, rb)

    # Prove d >= 4
    res_bound = SATDistanceEncoder.verify_distance_bound(code, target_distance=4)
    assert res_bound.distance_verified is True
    assert res_bound.proven_distance_lower_bound == 4
    assert res_bound.solve_time_seconds < 2.0

    # Search exact distance
    res_exact = SATDistanceEncoder.find_exact_distance(code, max_search=5)
    assert res_exact.exact_distance == 4
    assert res_exact.solve_time_seconds < 2.0


def test_sat_distance_refutes_false_bound() -> None:
    """Verify that verify_distance_bound refutes d >= 4 on Steane [[7, 1, 3]]."""
    HX = np.array(
        [
            [0, 0, 0, 1, 1, 1, 1],
            [0, 1, 1, 0, 0, 1, 1],
            [1, 0, 1, 0, 1, 0, 1],
        ],
        dtype=np.uint8,
    )
    HZ = np.copy(HX)

    # Claiming d >= 4 on a d=3 code MUST fail honestly
    res = SATDistanceEncoder.verify_distance_bound((HX, HZ), target_distance=4)
    assert res.distance_verified is False
    assert res.exact_distance == 3  # Detected weight 3 logical operator


def test_sat_covering_agl_9_3_2() -> None:
    """Verify SAT covering formulation on C(9, 3, 2) under AGL(1, 9)."""
    group = AffineGroup1D(9)
    res = SATCoveringEncoder.encode_and_solve(
        v=9,
        k=3,
        t=2,
        group=group,
        max_base_blocks=2,
    )
    assert res.is_sat is True
    assert res.num_base_blocks <= 2
    assert res.solve_time_seconds < 1.0


def test_sat_covering_agl_13_5_3() -> None:
    """Verify SAT covering formulation on C(13, 5, 3) under AGL(1, 13)."""
    group = AffineGroup1D(13)
    res = SATCoveringEncoder.encode_and_solve(
        v=13,
        k=5,
        t=3,
        group=group,
        max_base_blocks=2,
    )
    assert res.is_sat is True
    assert res.num_base_blocks >= 1
    assert res.solve_time_seconds < 2.0
