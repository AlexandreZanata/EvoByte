"""Tests for P169 statistical evaluation and Holm-Bonferroni FWER control."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from evobyte.statistical_evaluation import (
    compute_paired_wilcoxon_holm,
    consolidate_campaign_verdicts,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_wilcoxon_holm_identical_samples():
    """Identical samples must yield p_raw == 1.0 and direction == 'no_difference'."""
    a = [1.0, 2.0, 3.0, 4.0, 5.0]
    b = [1.0, 2.0, 3.0, 4.0, 5.0]

    verdict = compute_paired_wilcoxon_holm(a, b, comparison_name="test_identical")
    assert verdict.p_value_raw == 1.0
    assert verdict.p_value_holm == 1.0
    assert verdict.direction == "no_difference"
    assert verdict.is_significant is False
    assert verdict.verdict == "INCONCLUSIVE_IDENTICAL"


def test_wilcoxon_holm_significant_difference():
    """Strongly separated samples must yield p_holm <= 0.01 and is_significant == True."""
    # 25 pairs with constant positive difference of 10.0
    a = [10.0 + i for i in range(25)]
    b = [float(i) for i in range(25)]

    verdict = compute_paired_wilcoxon_holm(
        a, b, comparison_name="test_significant", family_size=1, alpha=0.01
    )
    assert verdict.p_value_holm <= 0.01
    assert verdict.is_significant is True
    assert verdict.direction == "method_a_superior"
    assert verdict.verdict == "SUPPORTED_METHOD_A_SUPERIOR"


def test_sample_size_mismatch_raises():
    """Mismatched sample lengths must raise ValueError."""
    a = [1.0, 2.0, 3.0]
    b = [1.0, 2.0]

    with pytest.raises(ValueError, match="sample sizes must match"):
        compute_paired_wilcoxon_holm(a, b, comparison_name="test_mismatch")


def test_alpha_strict_threshold_guard():
    """Borderline or non-significant p-values must strictly reject false positives."""
    # Subtle differences with high variance -> should not reach p <= 0.01
    rng = np.random.default_rng(42)
    a = rng.normal(0.0, 1.0, size=10)
    b = rng.normal(0.0, 1.0, size=10)

    verdict = compute_paired_wilcoxon_holm(a, b, comparison_name="test_null", alpha=0.01)
    if verdict.p_value_holm > 0.01:
        assert verdict.is_significant is False
        assert verdict.verdict == "NOT_SUPPORTED_NULL"


def test_consolidate_campaign_verdicts_empty(tmp_path: Path):
    """Consolidation must succeed gracefully on minimal or empty payload."""
    dummy_summary = tmp_path / "empty_summary.json"
    dummy_out = tmp_path / "verdict_out.json"

    with open(dummy_summary, "w", encoding="utf-8") as f:
        json.dump({"trials": [], "algorithms": [], "verdicts": {}}, f)

    res = consolidate_campaign_verdicts(str(dummy_summary), str(dummy_out))
    assert res["status"] == "EVALUATED"
    assert res["family_alpha"] == 0.01
    assert res["mathematical_record_discovery"] == "NULL_RESULT"
    assert res["bytecode_evolutionary_advantage"] == "NOT_SUPPORTED"
    assert res["hypotheses"] == []
    assert dummy_out.exists()


def test_consolidate_campaign_verdicts_on_p166(tmp_path: Path):
    """Consolidate real P166 campaign summary and verify paired Wilcoxon batteries."""
    p166_path = REPO_ROOT / "experiments" / "p166-campaign" / "summary.json"
    assert p166_path.exists(), "p166 summary.json must exist"

    out_path = tmp_path / "p169_test_verdict.json"
    res = consolidate_campaign_verdicts(str(p166_path), str(out_path))

    assert res["status"] == "EVALUATED"
    assert res["family_alpha"] == 0.01
    assert res["mathematical_record_discovery"] == "NULL_RESULT"
    assert res["bytecode_evolutionary_advantage"] == "NOT_SUPPORTED"

    # We expect 6 subset comparisons and 1 pooled comparison
    assert len(res["hypotheses"]) >= 7

    # Validate that every hypothesis strictly respects alpha=0.01
    for hyp in res["hypotheses"]:
        if hyp["p_value_holm"] > 0.01:
            assert hyp["is_significant"] is False
            assert hyp["verdict"] == "NOT_SUPPORTED_NULL"
        else:
            assert hyp["is_significant"] is True
            assert hyp["verdict"].startswith("SUPPORTED_")


def test_p169_artifacts_and_report_integrity():
    """Verify that committed P169 artifacts exist and follow strict honesty requirements."""
    artifact_path = REPO_ROOT / "experiments" / "p169-statistical-verdict.json"
    report_path = REPO_ROOT / "docs" / "research" / "p169-statistical-verdict.md"

    assert artifact_path.exists(), "experiments/p169-statistical-verdict.json must exist"
    assert report_path.exists(), "docs/research/p169-statistical-verdict.md must exist"

    with open(artifact_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data.get("phase") == "P169"
    assert data.get("status") == "EVALUATED"
    assert data.get("family_alpha") == 0.01
    assert data.get("mathematical_record_discovery") == "NULL_RESULT"
    assert data.get("bytecode_evolutionary_advantage") == "NOT_SUPPORTED"

    report_content = report_path.read_text(encoding="utf-8")
    assert (
        "A hipótese de superioridade estrita de busca evolutiva em bytecode é REJECTED"
        in report_content
    )
    assert (
        "A hipótese de descoberta de novos recordes matemáticos na campanha pré-registrada é NULL RESULT"
        in report_content
    )
