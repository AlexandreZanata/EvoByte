"""Tests for QECC blind rediscovery and campaign protocol (P182)."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import unittest.mock

from benchmarks.run_qecc_campaign import (
    DEFAULT_MANIFEST,
    evaluate_campaign_verdict,
    evaluate_target_verdict,
    evaluate_trial_verdict,
    execute_campaign,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
CATALOGUE_PATH = REPO_ROOT / "docs" / "research" / "targets" / "qecc_frontier_v1.json"


def test_verdict_rule_beaten_vs_null() -> None:
    """Test 1: Static fixture tests for trial, target, and campaign verdicts."""
    # Trial level
    assert evaluate_trial_verdict(best_d=7, best_known=6, role="record") == "DISCOVERY_BEATEN"
    assert evaluate_trial_verdict(best_d=6, best_known=6, role="record") == "NULL_RESULT"
    assert evaluate_trial_verdict(best_d=5, best_known=6, role="record") == "NULL_RESULT"
    assert evaluate_trial_verdict(best_d=3, best_known=3, role="calibration") == "REDISCOVERY_OK"
    assert evaluate_trial_verdict(best_d=2, best_known=3, role="calibration") == "NULL_RESULT"

    # Target level
    assert (
        evaluate_target_verdict(["NULL_RESULT", "DISCOVERY_BEATEN", "NULL_RESULT"])
        == "DISCOVERY_BEATEN"
    )
    assert evaluate_target_verdict(["NULL_RESULT", "NULL_RESULT"]) == "NULL_RESULT"
    assert evaluate_target_verdict(["REDISCOVERY_OK", "NULL_RESULT"]) == "REDISCOVERY_OK"

    # Campaign level
    assert evaluate_campaign_verdict({"t1": "NULL_RESULT", "t2": "NULL_RESULT"}) == "NULL_RESULT"
    assert (
        evaluate_campaign_verdict({"t1": "DISCOVERY_BEATEN", "t2": "NULL_RESULT"})
        == "DISCOVERY_BEATEN"
    )


def test_no_manual_seeds_in_campaign_config() -> None:
    """Test 2: Manifest and runner reject manual solution seeds; init path is strictly random."""
    manifest = json.loads(DEFAULT_MANIFEST.read_text(encoding="utf-8"))
    assert "manual_seeds" not in manifest
    assert "generators" not in manifest.get("calibration", {})
    assert "generators" not in manifest.get("campaign", {})

    # Static AST check on run_qecc_campaign.py: no hardcoded Steane / Shor strings
    script_text = (REPO_ROOT / "benchmarks" / "run_qecc_campaign.py").read_text(encoding="utf-8")
    forbidden_solution_tokens = ["IIIXXXX", "IXXIIXX", "XIXIXIX", "ZZIIIIIII", "XXXXXXIII"]
    for token in forbidden_solution_tokens:
        assert token not in script_text, (
            f"Forbidden hardcoded solution token found in script: {token}"
        )


def test_checkpoint_resume_roundtrip(tmp_path: Path) -> None:
    """Test 3: Fake partial checkpoint resumes without repeating completed trials."""
    manifest_bytes = DEFAULT_MANIFEST.read_bytes()
    manifest_sha = hashlib.sha256(manifest_bytes).hexdigest()

    # Construct checkpoint where steane_7_1_3 seed 42 is already done
    fake_checkpoint = {
        "phase": "P182",
        "manifest_sha256": manifest_sha,
        "completed_trials": {
            "calib_steane_7_1_3_42": {
                "target_id": "steane_7_1_3",
                "role": "calibration",
                "n": 7,
                "k": 1,
                "best_known": 3,
                "seed": 42,
                "elapsed_seconds": 0.05,
                "evaluations": 10,
                "generations": 1,
                "best_d": 3,
                "verdict": "REDISCOVERY_OK",
                "best_candidate_generators": ["IIIXXXX"],
                "records_count": 0,
                "records": [],
            }
        },
        "calibration_runs": [],
        "campaign_runs": [],
    }

    ckpt_file = tmp_path / "test_checkpoint.json"
    ckpt_file.write_text(json.dumps(fake_checkpoint), encoding="utf-8")
    out_file = tmp_path / "test_out.json"

    with unittest.mock.patch("benchmarks.run_qecc_campaign.run_trial") as mock_run:
        mock_run.return_value = {
            "target_id": "mock_target",
            "role": "calibration",
            "n": 7,
            "k": 1,
            "best_known": 3,
            "seed": 999,
            "elapsed_seconds": 0.01,
            "evaluations": 5,
            "generations": 1,
            "best_d": 3,
            "verdict": "REDISCOVERY_OK",
            "best_candidate_generators": [],
            "records_count": 0,
            "records": [],
        }

        execute_campaign(
            manifest_path=DEFAULT_MANIFEST,
            output_path=out_file,
            checkpoint_path=ckpt_file,
            resume=True,
            budget_scale=0.01,
        )

        # Confirm steane_7_1_3 with seed 42 was NOT invoked in mock_run
        for call_args in mock_run.call_args_list:
            called_target = call_args.kwargs["target_info"]["target_id"]
            called_seed = call_args.kwargs["seed"]
            assert not (called_target == "steane_7_1_3" and called_seed == 42), (
                "Completed trial from checkpoint was re-run!"
            )


def test_manifest_schema() -> None:
    """Test 4: Manifest schema contains all required keys and all targets exist in P180 catalogue."""
    manifest = json.loads(DEFAULT_MANIFEST.read_text(encoding="utf-8"))
    assert manifest["phase"] == "P182"
    assert "calibration" in manifest
    assert "campaign" in manifest
    assert "algorithms" in manifest
    assert "verifier" in manifest
    assert "verdict_rule" in manifest

    cat_data = json.loads(CATALOGUE_PATH.read_text(encoding="utf-8"))
    cat_ids = {t["target_id"] for t in cat_data["targets"]}

    for tid in manifest["calibration"]["targets"]:
        assert tid in cat_ids, f"Calibration target {tid} not in catalogue"
    for tid in manifest["campaign"]["targets"]:
        assert tid in cat_ids, f"Campaign target {tid} not in catalogue"

    assert len(manifest["calibration"]["seeds"]) >= 2
    assert len(manifest["campaign"]["seeds"]) >= 3
    assert manifest["calibration"]["budget_sec_per_seed"] > 0
    assert manifest["campaign"]["budget_sec_per_seed"] > 0
