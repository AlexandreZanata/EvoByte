"""Tests for quaternion algebra sieve and norm factorization (P99)."""

from evobyte.quaternion_sieve import (
    Quaternion,
    decompose_four_squares,
    evaluate_quaternion_sieve_coverage,
    quaternion_sieve_conic_point,
)


def test_quaternion_basic_properties():
    q = Quaternion(1, 2, 3, 4, alpha=-1, beta=-1)
    assert q.x0 == 1
    assert q.x1 == 2
    assert q.x2 == 3
    assert q.x3 == 4
    # Nrd(q) = 1^2 + 2^2 + 3^2 + 4^2 = 1 + 4 + 9 + 16 = 30
    assert q.reduced_norm() == 30

    q_conj = q.conjugate()
    assert q_conj.x0 == 1
    assert q_conj.x1 == -2
    assert q_conj.x2 == -3
    assert q_conj.x3 == -4


def test_quaternion_norm_multiplicativity():
    # Test standard Hamilton quaternions
    q1 = Quaternion(2, 3, 5, 7, alpha=-1, beta=-1)
    q2 = Quaternion(1, -2, 4, -3, alpha=-1, beta=-1)
    q_prod = q1 * q2
    assert q_prod.reduced_norm() == q1.reduced_norm() * q2.reduced_norm()

    # Test generalized quaternion algebra H(alpha, beta)
    g1 = Quaternion(3, 1, -2, 4, alpha=2, beta=5)
    g2 = Quaternion(-1, 4, 2, -1, alpha=2, beta=5)
    g_prod = g1 * g2
    assert g_prod.reduced_norm() == g1.reduced_norm() * g2.reduced_norm()


def test_decompose_four_squares():
    test_cases = [0, 1, 2, 3, 4, 7, 15, 25, 42, 1009, 10007]
    for n in test_cases:
        a, b, c, d = decompose_four_squares(n)
        assert a**2 + b**2 + c**2 + d**2 == n


def test_quaternion_sieve_conic_point():
    res = quaternion_sieve_conic_point(4, 1009, 253)
    assert res["verified"] is True
    assert res["norm_multiplicative"] is True
    assert res["nrd_prod"] == res["nrd_u"] * res["nrd_v"]


def test_quaternion_sieve_coverage():
    cov = evaluate_quaternion_sieve_coverage(instances=[1009, 841, 121], a_values=[4, 5])
    assert cov["all_verified"] is True
    assert cov["success_rate"] == 1.0
    assert cov["total_verified"] == cov["total_evaluated"]
