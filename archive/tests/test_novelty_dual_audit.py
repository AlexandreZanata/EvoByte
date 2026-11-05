"""Tests for P186 World Literature Novelty & Priority Dual-Audit."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import pytest

from scripts.novelty_dual_audit import (
    AuditClaimRecord,
    SourceSnapshot,
    audit_claim,
    run_novelty_dual_audit,
)


def test_audit_confirms_clear_record(tmp_path: Path) -> None:
    """Test that a valid object strictly beating frozen and literature bounds is CONFIRMED."""
    # Synthetic target with frozen best known value = 10, objective maximize
    # Candidate object achieves metric = 12
    # Local dated snapshot confirms literature bound is still 10
    local_snap_path = tmp_path / "test_source.snapshot"
    local_snap_path.write_text("Mock OEIS entry: highest known bound is 10.")

    snap = SourceSnapshot(
        source_id="mock-oeis-record",
        url="https://oeis.org/search?q=id:A999999&fmt=text",
        accessed_at="2026-10-25T14:00:00Z",
        sha256="abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        status="offline_cached",
        notes="Local test snapshot with bound 10",
        local_path=str(local_snap_path),
        literature_bound=10,
    )

    # Valid candidate object (e.g. cap set in F3^2 of size 4; for mock family generic pass)
    candidate_obj = [[0, 0], [0, 1], [1, 0], [1, 2]]

    claim = audit_claim(
        target_id="mock_frontier_target_1",
        family="generic_mock",
        objective="maximize",
        frozen_best_known=10,
        candidate_metric=12,
        candidate_object=candidate_obj,
        claim_type="discovery_beaten",
        target_params={"n": 2},
        snapshot=snap,
        literature_current_bound=10,
        machine_signature="EvoByte-FrontierVerifier-v2",
        human_signature="human:Alexandre",
    )

    assert claim.verdict == "CONFIRMED"
    assert claim.audit_a_passed is True
    assert claim.audit_b_passed is True
    assert "CONFIRMED" in claim.reason
    assert claim.signatures["human_signature"] == "human:Alexandre"
    assert claim.evidence["snapshot_sha256"] == snap.sha256
    assert claim.evidence["literature_bound"] == 10


def test_audit_downgrades_stale_claim(tmp_path: Path) -> None:
    """Test that a claim beating frozen bound but superseded by literature is DOWNGRADED."""
    # Frozen catalog had bound = 10. Candidate achieves metric = 12.
    # But new dated literature snapshot shows an external paper achieved bound = 14.
    local_snap_path = tmp_path / "test_stale.snapshot"
    local_snap_path.write_text("Mock paper: achieved bound 14.")

    snap = SourceSnapshot(
        source_id="mock-arxiv-new-paper",
        url="https://arxiv.org/abs/2610.99999",
        accessed_at="2026-10-25T14:00:00Z",
        sha256="1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        status="offline_cached",
        notes="Literature updated bound to 14",
        local_path=str(local_snap_path),
        literature_bound=14,
    )

    candidate_obj = [[0, 0], [0, 1], [1, 0], [1, 2]]

    claim = audit_claim(
        target_id="mock_frontier_target_stale",
        family="generic_mock",
        objective="maximize",
        frozen_best_known=10,
        candidate_metric=12,
        candidate_object=candidate_obj,
        claim_type="discovery_beaten",
        target_params={},
        snapshot=snap,
        literature_current_bound=14,  # Literature already achieved 14 >= 12
        machine_signature="EvoByte-FrontierVerifier-v2",
        human_signature="human:Alexandre",
    )

    assert claim.verdict == "DOWNGRADED"
    assert claim.audit_a_passed is True  # Beat frozen 10
    assert claim.audit_b_passed is False  # Superseded by 14
    assert "DOWNGRADED: Failed Audit B" in claim.reason
    assert "SUPERSEDED by literature" in claim.audit_b_details


def test_null_when_no_beaten(tmp_path: Path) -> None:
    """Test that campaigns without DISCOVERY_BEATEN yield 0 confirmed and all NOT_APPLICABLE."""
    inputs = [
        "experiments/p176-covering-results.json",
        "experiments/p177-weak-schur-results.json",
        "experiments/p182-qecc-results.json",
    ]
    out_file = tmp_path / "audit_test.json"
    sn_dir = tmp_path / "snapshots"

    report = run_novelty_dual_audit(
        inputs=inputs,
        out_path=out_file,
        snapshots_dir=sn_dir,
        offline=True,  # STRICTLY OFFLINE FOR TESTS
        human_reviewer="human:Alexandre",
    )

    summary = report["summary"]
    assert summary["total_claims_audited"] > 0
    assert summary["confirmed"] == 0
    assert summary["downgraded"] == 0
    assert summary["not_applicable"] == summary["total_claims_audited"]
    assert report["overall_verdict"] == "NO_ACTIVE_DISCOVERY_CLAIMS"

    # Confirm no claim was marked CONFIRMED
    for c in report["claims"]:
        assert c["verdict"] != "CONFIRMED"
        assert c["verdict"] == "NOT_APPLICABLE"


def test_every_claim_has_dated_evidence(tmp_path: Path) -> None:
    """Test that all claims in audit report contain dated snapshot evidence with URL and SHA."""
    # Run audit on calibration samples and inputs offline
    inputs = [
        "dist/external-validation/frontier_sample_covering.json",
        "dist/external-validation/frontier_sample_weak_schur.json",
    ]
    out_file = tmp_path / "evidence_audit.json"
    sn_dir = tmp_path / "snapshots"

    report = run_novelty_dual_audit(
        inputs=inputs,
        out_path=out_file,
        snapshots_dir=sn_dir,
        offline=True,
        human_reviewer="human:Alexandre",
    )

    for claim in report["claims"]:
        evidence = claim["evidence"]
        assert "accessed_at" in evidence
        assert len(evidence["accessed_at"]) > 0
        assert "snapshot_url" in evidence
        assert len(evidence["snapshot_url"]) > 0
        assert "snapshot_sha256" in evidence
        assert len(evidence["snapshot_sha256"]) > 0

    for src in report["sources_reconsulted"]:
        assert len(src["url"]) > 0
        assert len(src["accessed_at"]) > 0
        assert len(src["sha256"]) > 0


def test_missing_human_signature_prevents_confirmed(tmp_path: Path) -> None:
    """Test that missing human reviewer signature prevents CONFIRMED verdict."""
    snap = SourceSnapshot(
        source_id="mock-source",
        url="https://example.org/table",
        accessed_at="2026-10-25T14:00:00Z",
        sha256="abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        status="offline_cached",
        notes="Mock snapshot",
        literature_bound=10,
    )

    claim = audit_claim(
        target_id="mock_frontier_target_unsigned",
        family="generic_mock",
        objective="maximize",
        frozen_best_known=10,
        candidate_metric=12,
        candidate_object=[[0, 0]],
        claim_type="discovery_beaten",
        target_params={},
        snapshot=snap,
        literature_current_bound=10,
        machine_signature="EvoByte-FrontierVerifier-v2",
        human_signature=None,  # MISSING HUMAN SIGNATURE
    )

    assert claim.verdict == "DOWNGRADED"
    assert "mandatory human reviewer signature" in claim.reason


def test_invalid_candidate_object_downgraded() -> None:
    """Test that a candidate failing independent verifier is DOWNGRADED in Audit A."""
    snap = SourceSnapshot(
        source_id="mock-source",
        url="https://example.org/covering",
        accessed_at="2026-10-25T14:00:00Z",
        sha256="abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        status="offline_cached",
        notes="Mock snapshot",
        literature_bound=7,
    )

    # Incomplete covering design for C(7, 3, 2): only 2 blocks leaves pairs uncovered
    bad_blocks = [[1, 2, 3], [4, 5, 6]]

    claim = audit_claim(
        target_id="covering_C_7_3_2",
        family="covering_design",
        objective="minimize",
        frozen_best_known=7,
        candidate_metric=2,  # Claims size 2 < 7
        candidate_object=bad_blocks,
        claim_type="discovery_beaten",
        target_params={"v": 7, "k": 3, "t": 2},
        snapshot=snap,
        literature_current_bound=7,
        machine_signature="EvoByte-FrontierVerifier-v2",
        human_signature="human:Alexandre",
    )

    assert claim.verdict == "DOWNGRADED"
    assert claim.audit_a_passed is False
    assert "Failed Audit A" in claim.reason


def test_cli_execution(tmp_path: Path) -> None:
    """Test CLI execution in offline mode via subprocess."""
    out_file = tmp_path / "cli_audit.json"
    sn_dir = tmp_path / "cli_snapshots"
    cmd = [
        sys.executable,
        "scripts/novelty_dual_audit.py",
        "--inputs",
        "experiments/p176-covering-results.json",
        "experiments/p177-weak-schur-results.json",
        "--out",
        str(out_file),
        "--snapshots",
        str(sn_dir),
        "--offline",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert result.returncode == 0
    assert out_file.exists()
    data = json.loads(out_file.read_text())
    assert data["phase"] == "P186"
    assert data["summary"]["total_claims_audited"] > 0
