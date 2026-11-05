"""Tests for QECC Frontier Target Catalogue v1 (P180)."""

from __future__ import annotations

import ast
import json
from pathlib import Path
import re
import sys
import time

from evobyte.qecc_verifier import check_stabilizer, code_distance
from scripts.build_qecc_catalogue import build_catalogue

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGETS_DIR = REPO_ROOT / "docs" / "research" / "targets"
CAT_PATH = TARGETS_DIR / "qecc_frontier_v1.json"
SOURCES_PATH = TARGETS_DIR / "qecc_sources_v1.json"


def test_catalogue_schema() -> None:
    """Test 1: Every record target has d_lo < d_hi and source with valid SHA-256 and date;
    calibration role only for locally verified certificates."""
    assert CAT_PATH.exists(), f"Missing catalogue: {CAT_PATH}"
    assert SOURCES_PATH.exists(), f"Missing sources: {SOURCES_PATH}"

    with CAT_PATH.open("r", encoding="utf-8") as f:
        cat_data = json.load(f)
    with SOURCES_PATH.open("r", encoding="utf-8") as f:
        sources = json.load(f)

    assert "targets" in cat_data
    targets = cat_data["targets"]
    assert len(targets) >= 10

    mandatory_fields = {
        "target_id",
        "family",
        "n",
        "k",
        "d_lo",
        "d_hi",
        "objective",
        "role",
        "best_known_value",
        "source_convention",
        "claimed_values",
        "verifier",
        "certificate_status",
        "certificate_object",
    }

    cal_count = 0
    rec_count = 0

    for t in targets:
        assert mandatory_fields.issubset(set(t.keys()))
        assert t["family"] == "qecc_stabilizer"
        assert t["verifier"] == "qecc_verifier.code_distance"
        assert isinstance(t["n"], int) and t["n"] > 0
        assert isinstance(t["k"], int) and t["k"] >= 0
        assert isinstance(t["d_lo"], int) and t["d_lo"] > 0
        assert isinstance(t["d_hi"], int) and t["d_hi"] >= t["d_lo"]

        claimed = t["claimed_values"]
        assert isinstance(claimed, list) and len(claimed) >= 1
        for c in claimed:
            assert "source_id" in c and c["source_id"] in sources
            src = sources[c["source_id"]]
            assert "sha256" in src
            assert len(src["sha256"]) == 64
            assert re.fullmatch(r"[0-9a-f]{64}", src["sha256"])
            assert "accessed_at" in src

        if t["role"] == "record":
            rec_count += 1
            assert t["d_lo"] < t["d_hi"], f"Record target {t['target_id']} must have d_lo < d_hi"
            assert t["best_known_value"] == t["d_lo"]
        elif t["role"] == "calibration":
            cal_count += 1
            assert t["certificate_status"] == "constructed_calibration"
            assert t["d_lo"] == t["d_hi"]
            assert t["best_known_value"] == t["d_lo"]
            assert isinstance(t["certificate_object"], list)
            assert len(t["certificate_object"]) > 0
        else:
            raise AssertionError(f"Unknown role {t['role']} in target {t['target_id']}")

    assert rec_count >= 5, f"Expected at least 5 record targets, got {rec_count}"
    assert cal_count >= 5, f"Expected at least 5 calibration targets, got {cal_count}"


def test_no_exact_proven_targets() -> None:
    """Test 2: No record target has lower == upper bound (anti-wall rule from AGENTS.md)."""
    with CAT_PATH.open("r", encoding="utf-8") as f:
        targets = json.load(f)["targets"]

    for t in targets:
        if t["role"] == "record":
            assert t["d_lo"] < t["d_hi"], (
                f"Forbidden exact record target {t['target_id']}: d_lo={t['d_lo']}, d_hi={t['d_hi']}"
            )


def test_sources_have_provenance() -> None:
    """Test 3: Every source_id has URL, date, and valid sha256 or documented status."""
    with SOURCES_PATH.open("r", encoding="utf-8") as f:
        sources = json.load(f)

    for sid, src in sources.items():
        assert src["source_id"] == sid
        assert "url" in src and len(src["url"]) > 0
        assert "accessed_at" in src and len(src["accessed_at"]) > 0
        assert "status" in src and len(src["status"]) > 0
        assert "sha256" in src
        if src["status"] != "not_obtained_dynamic_site":
            assert len(src["sha256"]) == 64
            assert re.fullmatch(r"[0-9a-f]{64}", src["sha256"])


def test_build_is_deterministic() -> None:
    """Test 4: Running build_catalogue twice generates identical JSON byte-by-byte."""
    first = build_catalogue()
    second = build_catalogue()
    first_json = json.dumps(first, indent=2, sort_keys=True) + "\n"
    second_json = json.dumps(second, indent=2, sort_keys=True) + "\n"
    assert first_json == second_json


def test_calibration_certificates_verify() -> None:
    """Test 5: Embedded calibration certificates verify with P179 verifier in < 0.2 s per code."""
    with CAT_PATH.open("r", encoding="utf-8") as f:
        targets = json.load(f)["targets"]

    for t in targets:
        if t["role"] == "calibration":
            gens = t["certificate_object"]
            t0 = time.perf_counter()
            ok_stab, stab_res = check_stabilizer(gens)
            elapsed_stab = time.perf_counter() - t0
            assert ok_stab is True, f"Stabilizer check failed for {t['target_id']}: {stab_res}"
            assert stab_res["n"] == t["n"]
            assert stab_res["k"] == t["k"]
            assert elapsed_stab < 0.1

            t1 = time.perf_counter()
            ok_dist, dist_res = code_distance(gens)
            elapsed_dist = time.perf_counter() - t1
            assert ok_dist is True, f"Distance check failed for {t['target_id']}: {dist_res}"
            assert dist_res["d"] == t["d_lo"]
            assert dist_res["k"] == t["k"]
            assert dist_res["n"] == t["n"]
            assert elapsed_dist < 0.2


def test_record_targets_stabilizers_commute() -> None:
    """Test 6: Published stabilizer matrices for record targets pass mutual commutation and rank."""
    with CAT_PATH.open("r", encoding="utf-8") as f:
        targets = json.load(f)["targets"]

    for t in targets:
        if t["role"] == "record":
            gens = t["certificate_object"]
            assert isinstance(gens, list) and len(gens) == t["n"] - t["k"]
            ok, payload = check_stabilizer(gens)
            assert ok is True, f"Check stabilizer failed for record {t['target_id']}: {payload}"
            assert payload["n"] == t["n"]
            assert payload["k"] == t["k"]
            assert payload["rank"] == t["n"] - t["k"]


def test_module_is_stdlib_plus_numpy() -> None:
    """Test 7: AST of scripts/build_qecc_catalogue.py imports only stdlib modules."""
    path = REPO_ROOT / "scripts" / "build_qecc_catalogue.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    stdlib = set(sys.stdlib_module_names) | {"__future__"}
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported.add(node.module.split(".")[0])
    for mod in imported:
        assert mod in stdlib, f"Non-stdlib import in build script: {mod}"
