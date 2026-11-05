"""Unit tests for Blind Historical Calibration Protocol (P215).

Validates:
1. Blind rediscovery of Bravyi et al. (2024) [[72, 12, 6]] bivariate bicycle code.
2. Blind rediscovery of Bivariate [[16, 2, 4]] code with exact distance d = 4.
3. Blind rediscovery of Steane [[7, 1, 3]] projective CSS code.
4. Blind rediscovery of affine plane covering design C(9, 3, 2) = 12 blocks.
5. Integrity and validation of the official calibration manifest.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from evobyte.bivariate_calibration import (
    blind_synthesize_affine_covering_c9_3_2,
    blind_synthesize_bivariate_16_2_4,
    blind_synthesize_bravyi_72_12_6,
    blind_synthesize_steane_7_1_3,
    run_p215_calibration_suite,
)


def test_blind_bravyi_72_12_6() -> None:
    """Test blind synthesis of [[72, 12, 6]] bivariate bicycle code."""
    res = blind_synthesize_bravyi_72_12_6(seed=42, timeout_seconds=10.0)
    assert res.verified is True
    assert res.target_id == "calib_bravyi_72_12_6"
    assert res.parameters["n"] == 72
    assert res.parameters["k"] == 12
    assert res.parameters["d"] == 6
    assert res.verification_payload["rank_X"] == 30
    assert res.verification_payload["rank_Z"] == 30
    assert len(res.sha256_hash) == 64
    assert res.wall_clock_seconds < 5.0


def test_blind_bivariate_16_2_4() -> None:
    """Test blind synthesis of [[16, 2, 4]] bivariate code and SAT distance proof."""
    res = blind_synthesize_bivariate_16_2_4(seed=42, timeout_seconds=10.0)
    assert res.verified is True
    assert res.target_id == "calib_bivariate_16_2_4"
    assert res.parameters["n"] == 16
    assert res.parameters["k"] == 2
    assert res.parameters["d"] == 4
    assert res.verification_payload["sat_verified"] is True
    assert res.verification_payload["is_symplectic"] is True
    assert res.wall_clock_seconds < 5.0


def test_blind_steane_7_1_3() -> None:
    """Test blind synthesis of Steane [[7, 1, 3]] projective CSS code."""
    res = blind_synthesize_steane_7_1_3(seed=42, timeout_seconds=10.0)
    assert res.verified is True
    assert res.target_id == "calib_steane_7_1_3"
    assert res.parameters["n"] == 7
    assert res.parameters["k"] == 1
    assert res.parameters["d"] == 3
    assert res.wall_clock_seconds < 5.0


def test_blind_affine_covering_c9_3_2() -> None:
    """Test blind synthesis of C(9, 3, 2) = 12 affine plane design."""
    res = blind_synthesize_affine_covering_c9_3_2(seed=42, timeout_seconds=10.0)
    assert res.verified is True
    assert res.target_id == "calib_covering_C_9_3_2"
    assert res.parameters["v"] == 9
    assert res.parameters["k"] == 3
    assert res.parameters["t"] == 2
    assert res.parameters["b"] == 12
    assert res.wall_clock_seconds < 5.0


def test_calibration_manifest_integrity() -> None:
    """Test that the calibration results manifest exists and records CALIBRATION_REPRODUCED."""
    manifest_path = Path("experiments/p215-bivariate-calibration-results.json")
    if not manifest_path.exists():
        run_p215_calibration_suite(seeds=(42, 43, 44), out_path=manifest_path)

    assert manifest_path.exists()
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    summary = data["summary"]
    assert summary["all_passed"] is True
    assert summary["success_rate"] == 1.0
    assert summary["verdict"] == "CALIBRATION_REPRODUCED"
    assert summary["budget_passed"] is True
    assert summary["total_wall_clock_seconds"] < 90.0

    # Ensure all 12 results are verified
    assert len(data["results"]) == 12
    for r in data["results"]:
        assert r["verified"] is True
        assert len(r["sha256_hash"]) == 64
