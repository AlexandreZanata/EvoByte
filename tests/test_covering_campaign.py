"""Covering campaign logic: verdict, checkpoint, manifest, break size (P176)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "benchmarks"))

from run_covering_campaign import (  # noqa: E402
    break_size,
    load_checkpoint,
    save_checkpoint,
    trial_key,
    verdict_for_target,
)


def test_verdict_rule_beaten_vs_null() -> None:
    beaten = verdict_for_target(46, [{"n_blocks": 45, "sha256": "abc"}])
    assert beaten == "DISCOVERY_BEATEN"
    equal = verdict_for_target(46, [{"n_blocks": 46, "sha256": "abc"}])
    assert equal == "NULL_RESULT"
    assert verdict_for_target(46, []) == "NULL_RESULT"
    assert verdict_for_target(10, [{"n_blocks": "xx"}]) == "NULL_RESULT"


def test_checkpoint_resume_roundtrip(tmp_path: Path) -> None:
    ckpt = tmp_path / "ckpt.json"
    state = {"manifest_sha256": "deadbeef",
             "completed": {"a|B1|SA|seed1": {"result": "UNBEATEN"}}}
    save_checkpoint(ckpt, state)
    back = load_checkpoint(ckpt)
    assert back["completed"]["a|B1|SA|seed1"]["result"] == "UNBEATEN"
    # Resume filters already-completed trial keys.
    planned = ["a|B1|SA|seed1", "a|B1|SA|seed2"]
    todo = [k for k in planned if k not in back["completed"]]
    assert todo == ["a|B1|SA|seed2"]
    assert load_checkpoint(tmp_path / "missing.json") == {"completed": {}}


def test_manifest_schema() -> None:
    manifest = json.loads((REPO / "experiments" / "p176-covering-manifest.json").read_text(encoding="utf-8"))
    for field in ("phase", "targets", "targets_source", "attempt_sizes", "budget_sec_per_seed",
                  "seeds", "algorithms", "verifier", "verdict_rule"):
        assert field in manifest, f"missing manifest field: {field}"
    assert manifest["phase"] == "P176"
    assert len(manifest["targets"]) == 40
    assert manifest["attempt_sizes"] == ["published_size - 1"]
    assert manifest["verifier"] == "frontier_catalogue.verify_covering_design"
    assert set(manifest["verdict_rule"]) == {"DISCOVERY_BEATEN", "NULL_RESULT"}
    catalogue = json.loads((REPO / manifest["targets_source"]).read_text(encoding="utf-8"))
    by_id = {t["target_id"] for t in catalogue["targets"]}
    assert all(t in by_id for t in manifest["targets"])
    assert "123456789" not in json.dumps(manifest)


def test_break_size_is_published_minus_one() -> None:
    catalogue = json.loads((REPO / "docs/research/targets/frontier_targets_v2.json").read_text(encoding="utf-8"))
    cov = [t for t in catalogue["targets"] if t["target_id"].startswith("covering_")][:3]
    assert len(cov) == 3
    for t in cov:
        assert break_size(int(t["best_known_value"])) == int(t["best_known_value"]) - 1
    assert trial_key("covering_C_7_3_2", 6, "SimulatedAnnealing", 42) == \
        "covering_C_7_3_2|B6|SimulatedAnnealing|seed42"
