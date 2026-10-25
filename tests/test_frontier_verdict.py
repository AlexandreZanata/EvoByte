"""Consolidated frontier verdict statistics (P178)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from evobyte.frontier_verdict import consolidate_frontier_verdicts, paired_wilcoxon_holm

REPO = Path(__file__).resolve().parents[1]


def test_wilcoxon_identical_samples() -> None:
    r = paired_wilcoxon_holm([4.0] * 10, [4.0] * 10, "identical")
    assert r["p_raw"] == 1.0
    assert r["direction"] == "no_difference"
    assert r["verdict"] == "INCONCLUSIVE_IDENTICAL"
    assert r["is_significant"] is False


def test_wilcoxon_separated_samples() -> None:
    a = [float(x) for x in range(25)]
    b = [float(x) + 5.0 for x in range(25)]
    r = paired_wilcoxon_holm(a, b, "separated", family_size=3)
    assert r["p_holm"] <= 0.01
    assert r["is_significant"] is True
    assert r["verdict"] == "SUPPORTED_B_GREATER"


def test_sample_size_mismatch_raises() -> None:
    with pytest.raises(ValueError):
        paired_wilcoxon_holm([1.0, 2.0], [1.0], "mismatch")


def test_consolidate_empty_graceful(tmp_path: Path) -> None:
    p176 = tmp_path / "empty176.json"
    p177 = tmp_path / "empty177.json"
    p176.write_text(json.dumps({"trials": [], "targets": []}), encoding="utf-8")
    p177.write_text(json.dumps({"trials": [], "targets": []}), encoding="utf-8")
    out = tmp_path / "verdict.json"
    payload = consolidate_frontier_verdicts(p176, p177, out)
    assert payload["status"] == "COMPLETE"
    assert payload["hypotheses"] == []
    assert payload["mathematical_record_discovery"] == "NULL_RESULT"
    assert json.loads(out.read_text(encoding="utf-8"))["status"] == "COMPLETE"


def test_consolidate_on_p176_p177() -> None:
    out = REPO / "experiments" / "p178-frontier-verdict.json"
    assert out.exists(), "consolidation artifact must exist"
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["status"] == "COMPLETE"
    assert payload["hypotheses"], "battery must not be empty on real data"
    for h in payload["hypotheses"]:
        if h["p_holm"] > 0.01:
            # Anti-p-hacking: no significance claim without p_holm <= alpha.
            # Identical samples yield INCONCLUSIVE_IDENTICAL (never SUPPORTED_*).
            assert h["verdict"] in ("NOT_SUPPORTED_NULL", "INCONCLUSIVE_IDENTICAL"), h["comparison"]
        else:
            assert h["verdict"] in ("SUPPORTED_A_GREATER", "SUPPORTED_B_GREATER")
    assert payload["mathematical_record_discovery"] in ("CONFIRMED", "NULL_RESULT")


def test_no_unadjusted_significance_claim() -> None:
    report = (REPO / "docs" / "research" / "p178-frontier-verdict-report.md").read_text(
        encoding="utf-8"
    )
    for line in report.splitlines():
        low = line.lower()
        if "significant" in low and "not significant" not in low and "non-significant" not in low:
            assert "p_holm" in low or "p-holm" in low or "holm" in low, line
