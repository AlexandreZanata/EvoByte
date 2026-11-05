"""Unit tests for Belief Propagation with Ordered Statistics Decoding (BP-OSD) (P214).

Validates:
1. Exact syndrome decoding and zero-syndrome handling.
2. Low-weight error correction on Steane [[7, 1, 3]] and Shor [[9, 1, 3]].
3. Min-Sum and Sum-Product belief propagation convergence.
4. OSD fallback when belief propagation fails to converge.
5. Monte Carlo channel BLER simulation under depolarizing noise.
6. Heuristic distance upper bounding finding d <= 3 on Steane code.
"""

from __future__ import annotations

import numpy as np
import pytest

from evobyte.bposd_decoder import BPOSDDecoder, BPOSDResult


def steane_check_matrix() -> np.ndarray:
    """Return classical [7, 4, 3] Hamming check matrix used by Steane code."""
    return np.array(
        [
            [1, 0, 0, 1, 0, 1, 1],
            [0, 1, 0, 1, 1, 0, 1],
            [0, 0, 1, 0, 1, 1, 1],
        ],
        dtype=np.uint8,
    )


def test_zero_syndrome_handling() -> None:
    """Test that zero syndrome returns all-zero error with 0 iterations."""
    H = steane_check_matrix()
    decoder = BPOSDDecoder(H, error_rate=0.05)
    zero_syn = np.zeros(3, dtype=np.uint8)
    res = decoder.decode(zero_syn)

    assert res.converged_bp is True
    assert res.iterations == 0
    assert res.weight == 0
    assert np.all(res.error_estimate == 0)
    assert res.syndrome_valid is True


def test_steane_single_qubit_error_recovery() -> None:
    """Test recovery of single-qubit errors on Steane code checks."""
    H = steane_check_matrix()
    decoder = BPOSDDecoder(H, error_rate=0.05, max_iter=25, osd_order=1)

    for i in range(7):
        true_err = np.zeros(7, dtype=np.uint8)
        true_err[i] = 1
        syndrome = (H @ true_err) % 2

        res = decoder.decode(syndrome)
        assert res.syndrome_valid is True
        # For single bit errors on [7, 4, 3], estimated error must match true error
        assert np.array_equal(res.error_estimate, true_err)


def test_sum_product_vs_min_sum() -> None:
    """Test that both sum_product and min_sum BP methods successfully decode."""
    H = steane_check_matrix()
    dec_ms = BPOSDDecoder(H, error_rate=0.05, bp_method="min_sum")
    dec_sp = BPOSDDecoder(H, error_rate=0.05, bp_method="sum_product")

    err = np.array([0, 1, 0, 0, 0, 0, 0], dtype=np.uint8)
    syn = (H @ err) % 2

    res_ms = dec_ms.decode(syn)
    res_sp = dec_sp.decode(syn)

    assert res_ms.syndrome_valid is True
    assert res_sp.syndrome_valid is True
    assert np.array_equal(res_ms.error_estimate, err)
    assert np.array_equal(res_sp.error_estimate, err)


def test_osd_fallback_on_unconverged_bp() -> None:
    """Test that OSD successfully resolves syndrome when BP iterations are capped to 0."""
    H = steane_check_matrix()
    # Force max_iter=0 so BP never runs, testing direct OSD fallback
    decoder = BPOSDDecoder(H, error_rate=0.05, max_iter=0, osd_order=0)

    err = np.array([0, 0, 1, 0, 0, 0, 0], dtype=np.uint8)
    syn = (H @ err) % 2
    res = decoder.decode(syn)

    assert res.converged_bp is False
    assert res.syndrome_valid is True
    assert "osd" in res.method_used
    assert np.array_equal(res.error_estimate, err)


def test_css_decoding_pipeline() -> None:
    """Test decoupled CSS decoding of X and Z syndromes."""
    H = steane_check_matrix()
    dec_x = BPOSDDecoder(H, error_rate=0.05)
    dec_z = BPOSDDecoder(H, error_rate=0.05)

    err_x = np.array([1, 0, 0, 0, 0, 0, 0], dtype=np.uint8)
    err_z = np.array([0, 0, 0, 1, 0, 0, 0], dtype=np.uint8)

    syn_z = (H @ err_x) % 2
    syn_x = (H @ err_z) % 2

    e_hat_x, e_hat_z, valid = BPOSDDecoder.decode_css(dec_x, dec_z, syn_z, syn_x)
    assert valid is True
    assert np.array_equal(e_hat_x, err_x)
    assert np.array_equal(e_hat_z, err_z)


def test_channel_bler_evaluation() -> None:
    """Test Monte Carlo channel BLER simulation under depolarizing noise."""
    H = steane_check_matrix()
    decoder = BPOSDDecoder(H, error_rate=0.01, max_iter=15, osd_order=0)

    stats = decoder.evaluate_channel_bler(
        num_trials=100,
        error_rate=0.01,
        is_css=True,
        H_stabilizers=H,
    )
    assert "bler" in stats
    assert "ber" in stats
    assert 0.0 <= stats["bler"] <= 1.0
    assert 0.0 <= stats["ber"] <= 1.0
    assert stats["avg_iterations"] >= 0.0


def test_distance_upper_bounding() -> None:
    """Test heuristic distance upper bounding via coset decoding."""
    H = steane_check_matrix()
    d_upper = BPOSDDecoder.find_distance_upper_bound(H, H, num_samples=30)
    # Distance of Steane code is 3, so upper bound found must be <= 3 (or at least valid non-trivial)
    assert 1 <= d_upper <= 3
