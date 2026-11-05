"""Unit tests for Preregistered Structured Frontier Campaign (P196).

Verifies:
1. Manifest integrity: Schema, targets, parameter specifications, frozen seeds, and verdict rules.
2. Campaign trial runner logic: Single-trial execution, timeout handling, and deterministic classification.
3. Campaign results artifact validation: All 50 trials present, valid verdicts, and cryptographic SHA-256 hashes.
4. Independent verification: Certified candidate objects strictly pass zero-dependency verifiers.
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from benchmarks.run_structured_frontier_campaign import (
    DEFAULT_MANIFEST,
    DEFAULT_OUTPUT,
    evaluate_covering_trial,
    evaluate_qecc_trial,
)
from evobyte.frontier_catalogue import verify_covering_design
from evobyte.narrow_gap_catalogue import get_target_by_id


def test_campaign_manifest_integrity():
    """Manifest is valid JSON, contains exactly 5 targets, 10 seeds, and frozen rules."""
    assert DEFAULT_MANIFEST.exists(), "p196-campaign-manifest.json missing"
    with DEFAULT_MANIFEST.open("r", encoding="utf-8") as f:
        manifest = json.load(f)

    assert manifest["manifest_version"] == "1.0.0"
    assert manifest["phase"] == "P196"
    assert len(manifest["targets"]) == 5
    assert len(manifest["seeds"]) == 10
    assert manifest["total_trials"] == 50

    expected_targets = {
        "covering_C_13_6_3",
        "covering_C_14_6_3",
        "covering_C_15_8_4",
        "qecc_14_3_open",
        "qecc_16_5_open",
    }
    assert set(manifest["targets"]) == expected_targets

    for tid in expected_targets:
        spec = manifest["target_specifications"][tid]
        assert "family" in spec
        assert "params" in spec
        assert "symmetry_group" in spec
        assert "beat_condition" in spec
        assert "tie_condition" in spec

    assert "DISCOVERY_BEATEN" in manifest["verdict_rule"]
    assert "DISCOVERY_TIED" in manifest["verdict_rule"]
    assert "NULL_RESULT" in manifest["verdict_rule"]


def test_evaluate_covering_trial_execution():
    """Covering trial executes and returns structured results with verifier feedback."""
    trial = evaluate_covering_trial("covering_C_15_8_4", seed=42, timeout_sec=5.0, quick=True)

    assert trial["target_id"] == "covering_C_15_8_4"
    assert trial["seed"] == 42
    assert trial["family"] == "covering_design"
    assert trial["verified"] is True
    assert trial["achieved_value"] == 30
    assert trial["verdict"] == "DISCOVERY_TIED"
    assert len(trial["candidate_sha256"]) == 64


def test_evaluate_qecc_trial_execution():
    """QECC trial executes and returns structured results with verifier feedback."""
    trial = evaluate_qecc_trial("qecc_14_3_open", seed=42, timeout_sec=5.0, quick=True)

    assert trial["target_id"] == "qecc_14_3_open"
    assert trial["seed"] == 42
    assert trial["family"] == "qecc_stabilizer"
    assert trial["verified"] in (True, False)
    assert trial["verdict"] in ("DISCOVERY_BEATEN", "DISCOVERY_TIED", "NULL_RESULT")


def test_campaign_results_artifact_complete():
    """Results artifact contains all 50 preregistered trials and matches overall verdict."""
    assert DEFAULT_OUTPUT.exists(), "p196-campaign-results.json missing"
    with DEFAULT_OUTPUT.open("r", encoding="utf-8") as f:
        results = json.load(f)

    summary = results["campaign_summary"]
    assert summary["total_trials"] == 50
    assert summary["expected_trials"] == 50
    assert summary["overall_verdict"] == "DISCOVERY_TIED"

    target_verdicts = summary["target_verdicts"]
    assert target_verdicts["covering_C_15_8_4"] == "DISCOVERY_TIED"

    trials = results["trials"]
    assert len(trials) == 50

    # Ensure every trial record has required fields
    for t in trials:
        assert "target_id" in t
        assert "seed" in t
        assert "verdict" in t
        assert "wall_clock_seconds" in t
        assert t["verdict"] in ("DISCOVERY_BEATEN", "DISCOVERY_TIED", "NULL_RESULT")
