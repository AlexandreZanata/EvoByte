"""Weak-Schur campaign logic: verdict, symmetry, manifest, break size (P177)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "benchmarks"))

from run_weak_schur_campaign import (  # noqa: E402
    break_size,
    is_p_periodic,
    load_checkpoint,
    random_symmetric_coloring,
    save_checkpoint,
    trial_key,
    verdict_for_target,
)


def test_verdict_rule_beaten_vs_null() -> None:
    assert verdict_for_target(207, [{"size": 208, "sha256": "abc"}]) == "DISCOVERY_BEATEN"
    assert verdict_for_target(207, [{"size": 207, "sha256": "abc"}]) == "NULL_RESULT"
    assert verdict_for_target(207, []) == "NULL_RESULT"
    assert verdict_for_target(207, [{"size": "xx"}]) == "NULL_RESULT"


def test_symmetric_mode_restricts_space() -> None:
    rng = np.random.default_rng(0)
    sym = random_symmetric_coloring(50, 5, 3, rng)
    assert is_p_periodic(sym, 3) is True
    # A free random coloring is (with overwhelming probability) not 3-periodic.
    free = [int(x) + 1 for x in rng.integers(0, 5, size=50)]
    assert is_p_periodic(free, 3) is False
    assert (
        trial_key("weak_schur_5", 208, "SimulatedAnnealing", 42, "free")
        == "weak_schur_5|m208|SimulatedAnnealing|seed42|free"
    )


def test_manifest_schema() -> None:
    manifest = json.loads(
        (REPO / "experiments" / "p177-weak-schur-manifest.json").read_text(encoding="utf-8")
    )
    for field in (
        "phase",
        "targets",
        "targets_source",
        "attempt_sizes",
        "symmetry",
        "budget_sec_per_seed",
        "seeds",
        "algorithms",
        "verifier",
        "verdict_rule",
    ):
        assert field in manifest, f"missing manifest field: {field}"
    assert manifest["phase"] == "P177"
    assert manifest["targets"] == ["weak_schur_5", "weak_schur_6", "weak_schur_7"]
    assert manifest["attempt_sizes"] == ["best_known_value + 1"]
    assert manifest["verifier"] == "frontier_catalogue.verify_weak_schur_partition"
    assert set(manifest["verdict_rule"]) == {"DISCOVERY_BEATEN", "NULL_RESULT"}
    assert manifest["symmetry"]["kind"] == "cyclic_shift_period_p"
    catalogue = json.loads((REPO / manifest["targets_source"]).read_text(encoding="utf-8"))
    by_id = {t["target_id"]: t for t in catalogue["targets"]}
    for tid in manifest["targets"]:
        assert tid in by_id and by_id[tid]["role"] == "record"


def test_break_size_is_best_plus_one() -> None:
    catalogue = json.loads(
        (REPO / "docs/research/targets/frontier_targets_v2.json").read_text(encoding="utf-8")
    )
    by_id = {t["target_id"]: t for t in catalogue["targets"]}
    for tid in ("weak_schur_5", "weak_schur_6", "weak_schur_7"):
        assert (
            break_size(int(by_id[tid]["best_known_value"]))
            == int(by_id[tid]["best_known_value"]) + 1
        )
    assert "123456789" not in json.dumps(
        json.loads(
            (REPO / "experiments" / "p177-weak-schur-manifest.json").read_text(encoding="utf-8")
        )
    )


def test_checkpoint_roundtrip(tmp_path: Path) -> None:
    ckpt = tmp_path / "ckpt.json"
    save_checkpoint(ckpt, {"manifest_sha256": "abc", "completed": {"k1": {"result": "UNBEATEN"}}})
    back = load_checkpoint(ckpt)
    assert back["completed"]["k1"]["result"] == "UNBEATEN"
    assert load_checkpoint(tmp_path / "missing.json") == {"completed": {}}
