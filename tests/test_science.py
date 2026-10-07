"""Unit tests for P14 scientific dataset specifications and Domain L2 verification."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "benchmarks"))

from benchmarks.science_matrix import (
    ACCEPTANCE_PHASES,
    PREREGISTERED_SCIENCE_SPECS,
    _p40_check_manifest,
    _p40_has_path,
    check_adversarial_domain,
    check_non_degeneracy,
    check_units_scaling,
    compute_r2,
    generate_scientific_splits,
    run_p40_evidence_audit,
    run_p58_acceptance_baseline_audit,
    run_p59_equal_information_audit,
    run_p60_workbench_audit,
    run_p61_shadow_audit,
    run_p62_repair_audit,
    run_p63_feedback_audit,
    run_p64_obstruction_audit,
    run_science_matrix,
    verify_scientific_candidate_l2,
)
from evobyte.bytecode import encode_instr, nop_program
from evobyte.provenance import verify_manifest_integrity, write_manifest


def test_preregistered_specs():
    assert len(PREREGISTERED_SCIENCE_SPECS) >= 5
    keys = [s.key for s in PREREGISTERED_SCIENCE_SPECS]
    assert "kepler_third_law" in keys
    assert "boyle_gas_law" in keys
    assert "stefan_boltzmann" in keys
    assert "michaelis_menten" in keys
    assert "lorentz_factor" in keys

    for s in PREREGISTERED_SCIENCE_SPECS:
        assert len(s.name) > 0
        assert len(s.license_name) > 0
        assert len(s.input_unit) > 0
        assert len(s.output_unit) > 0
        assert s.train_range[0] < s.train_range[1]
        assert s.extrap_range[0] < s.extrap_range[1]
        assert s.r2_threshold > 0.90


def test_generate_scientific_splits():
    spec = PREREGISTERED_SCIENCE_SPECS[0]
    splits, h = generate_scientific_splits(spec, n_points=32)
    assert len(h) == 16
    for k in ("train", "val", "hidden", "extrapolation"):
        xs, ys = splits[k]
        assert len(xs) == 32
        assert len(ys) == 32
        assert np.all(np.isfinite(xs))
        assert np.all(np.isfinite(ys))

    # Verify deterministic hash
    _, h2 = generate_scientific_splits(spec, n_points=32)
    assert h == h2


def test_compute_r2():
    y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0], dtype=np.float64)
    assert abs(compute_r2(y_true, y_true) - 1.0) < 1e-9

    y_pred_bad = np.array([10.0, 10.0, 10.0, 10.0, 10.0], dtype=np.float64)
    assert compute_r2(y_true, y_pred_bad) < 0.1


def test_check_non_degeneracy_constant_guard():
    # Program that outputs a constant (e.g. always 5.0 in r7 from r2=0 + bank[12]=5.0)
    prog = nop_program()
    prog[0] = encode_instr(0x0F, dst=7, a=2, b=12)  # CSEL r7 = r2(0.0) + const[12](5.0)

    xs_probe = np.linspace(1.0, 10.0, 50, dtype=np.float32)
    ok, reasons = check_non_degeneracy(prog, xs_probe)
    assert ok is False
    assert any("Constant-only" in r for r in reasons)


def test_check_units_scaling():
    # Construct candidate that computes y = x^1.5 = x * sqrt(x)
    prog = nop_program()
    prog[0] = encode_instr(0x0B, dst=1, a=0, b=0)  # SQRT r1 = sqrt(x)
    prog[1] = encode_instr(0x03, dst=7, a=0, b=1)  # MUL r7 = x * sqrt(x)

    ok, exp = check_units_scaling(prog, base_x=4.0, expected_exponent=1.5)
    assert ok is True
    assert exp is not None
    assert abs(exp - 1.5) < 0.05

    # Fail check if expected exponent doesn't match
    ok_fail, _ = check_units_scaling(prog, base_x=4.0, expected_exponent=2.0)
    assert ok_fail is False


def test_check_adversarial_domain():
    prog = nop_program()
    prog[0] = encode_instr(0x04, dst=7, a=0, b=0)  # DIV r7 = x / x

    ok, _ = check_adversarial_domain(prog, [0.01, 1.0, 100.0])
    assert ok is True


def test_verify_scientific_candidate_l2_kepler():
    spec = next(s for s in PREREGISTERED_SCIENCE_SPECS if s.key == "kepler_third_law")
    splits, _ = generate_scientific_splits(spec, n_points=64)

    # Exact Kepler program: r1 = sqrt(x), r7 = x * r1
    prog = nop_program()
    prog[0] = encode_instr(0x0B, dst=1, a=0, b=0)  # SQRT r1 = sqrt(x)
    prog[1] = encode_instr(0x03, dst=7, a=0, b=1)  # MUL r7 = x * sqrt(x)

    res = verify_scientific_candidate_l2(prog, spec, splits)
    assert res.status == "SUPPORTED"
    assert res.train_r2 > 0.999
    assert res.hidden_r2 > 0.999
    assert res.extrapolation_passed is True
    assert res.units_scaling_passed is True
    assert res.adversarial_passed is True
    assert res.non_degenerate is True
    assert len(res.failure_reasons) == 0


def test_science_matrix_smoke():
    res = run_science_matrix(preregistered_only=True, seeds=[42], max_trial_sec=0.5)
    assert res["status"] == "PASS"
    assert len(res["datasets"]) >= 5


def test_p40_acceptance_registry_rejects_unknown_phases():
    assert ACCEPTANCE_PHASES == (
        "P40",
        "P41",
        "P42",
        "P43",
        "P44",
        "P45",
        "P46",
        "P47",
        "P48",
        "P49",
        "P50",
        "P51",
        "P52",
        "P53",
        "P54",
        "P55",
        "P56",
        "P57",
        "P58",
    )
    import subprocess as _sp

    proc = _sp.run(
        [
            sys.executable,
            "benchmarks/science_matrix.py",
            "--acceptance-phase",
            "P59",
            "--config",
            "experiments/p40-config.json",
            "--output",
            "/tmp/evobyte-p40-unknown.json",
        ],
        capture_output=True,
        text=True,
        check=False,
        cwd=str(Path(__file__).resolve().parents[1]),
    )
    assert proc.returncode != 0
    assert "Unknown acceptance phase 'P59'" in (proc.stdout + proc.stderr)


def test_p40_path_helper_quantifiers():
    doc = {"instances": [{"certificate": {"h": 1}}, {"note": "miss"}]}
    assert _p40_has_path(doc, "instances[?certificate].certificate.h") is True
    assert _p40_has_path(doc, "instances[].certificate.h") is False
    assert _p40_has_path([{"a": 1}], "a") is True
    assert _p40_has_path([], "a") is False


def test_p40_manifest_integrity_detects_tampering(tmp_path):
    raw = tmp_path / "raw.json"
    raw.write_text('{"trials": []}')
    manifest_p = tmp_path / "m.json"
    write_manifest(manifest_p, {"phase": "P40-test", "elapsed_sec": 1.0}, {str(raw): "x"})
    # Fix the recorded hash to the true value, then tamper the raw file.
    import hashlib as _hl
    import json as _json

    doc = _json.loads(manifest_p.read_text())
    doc["raw_artifacts"] = [{"path": str(raw), "sha256": _hl.sha256(raw.read_bytes()).hexdigest()}]
    blob = _json.dumps(
        {k: v for k, v in doc.items() if k != "manifest_sha256"}, sort_keys=True, default=str
    ).encode()
    doc["manifest_sha256"] = _hl.sha256(blob).hexdigest()
    manifest_p.write_text(_json.dumps(doc, indent=2, sort_keys=True))
    assert verify_manifest_integrity(manifest_p)["ok"] is True
    with open(raw, "a", encoding="utf-8") as f:
        f.write(" ")
    tampered = verify_manifest_integrity(manifest_p)
    assert tampered["ok"] is False
    assert any("raw_hash_mismatch" in e for e in tampered["errors"])
    # Tampered seal is also rejected.
    doc["elapsed_sec"] = 2.0
    manifest_p.write_text(_json.dumps(doc, indent=2, sort_keys=True))
    resealed = verify_manifest_integrity(manifest_p)
    assert resealed["ok"] is False
    assert "manifest_seal_mismatch" in resealed["errors"]


def test_p40_manifest_check_rejects_duration_divergence(tmp_path):
    import json as _json

    raw = tmp_path / "raw.json"
    raw.write_text("{}")
    manifest_p = tmp_path / "m.json"
    import hashlib as _hl

    doc = {
        "phase": "P40-test",
        "status": "PASS",
        "elapsed_sec": 0.0,
        "provenance": {"clean_tree": True},
        "raw_artifacts": [{"path": str(raw), "sha256": _hl.sha256(raw.read_bytes()).hexdigest()}],
    }
    blob = _json.dumps(
        {k: v for k, v in doc.items() if k != "manifest_sha256"}, sort_keys=True, default=str
    ).encode()
    doc["manifest_sha256"] = _hl.sha256(blob).hexdigest()
    manifest_p.write_text(_json.dumps(doc, indent=2, sort_keys=True))
    finding = _p40_check_manifest(
        {
            "path": str(manifest_p),
            "status_ok": ["PASS"],
            "required_fields": ["provenance"],
            "certificate_evidence": [],
            "budgets": {"scale": 1.0},
        }
    )
    assert finding["verdict"] == "rejected"
    assert any("elapsed_sec" in n for n in finding["notes"])


def test_p40_evidence_audit_smoke(tmp_path):
    out_p = tmp_path / "p40-acceptance.json"
    report = run_p40_evidence_audit("experiments/p40-config.json", out_p)
    assert out_p.exists()
    assert report["phase"] == "P40"
    assert report["verdict"] in ("ACCEPTED", "MIXED")
    assert report["claim_scope"].startswith("P33-P39")
    assert len(report["manifests"]) == 7
    assert len(report["claims"]) == 13
    assert report["base_reconciliation"]["merges_this_cycle"] is False
    assert report["resolved_config"]["config_path"] == "experiments/p40-config.json"
    assert "deterministic manifest inspection" in report["seeds_rng"]


def test_p41_immutable_audit_smoke(tmp_path):
    from benchmarks.science_matrix import run_p41_immutable_audit

    out_p = tmp_path / "p41-acceptance.json"
    report = run_p41_immutable_audit("experiments/p41-config.json", out_p)
    assert out_p.exists()
    assert report["phase"] == "P41"
    assert report["verdict"] in ("ACCEPTED", "MIXED")
    assert report["demonstrations"]["overwrite_refused"] is True
    assert report["demonstrations"]["one_byte_tamper_detected"] is True
    assert report["historical_untouched_by_smoke"]["changed"] == []
    assert len(report["inventory"]) == 9
    assert "deterministic inspection" in report["seeds_rng"]


def test_p42_exact_audit_smoke(tmp_path, p30_split_manifest):
    from benchmarks.science_matrix import run_p42_exact_audit

    out_p = tmp_path / "p42-acceptance.json"
    import json

    config = json.loads(
        (Path(__file__).resolve().parents[1] / "experiments" / "p42-config.json").read_text()
    )
    config["smoke"]["split_manifest"] = str(p30_split_manifest)
    config_path = tmp_path / "p42-test-config.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    report = run_p42_exact_audit(config_path, out_p)
    assert out_p.exists()
    assert report["phase"] == "P42"
    assert report["verdict"] in ("ACCEPTED", "MIXED")
    assert len(report["identities"]) == 4
    assert all(
        i["resolution"] in ("exact_accepted", "exact_rejected") for i in report["identities"]
    )
    assert all(c["rejected"] for c in report["controls"])
    assert report["labeling_rule"]["n_positives"] > 0
    assert report["labeling_rule"].get("rule_holds") is True
    assert report["corpus_integrity"]["ok"] is True


def test_p43_resume_audit_smoke(tmp_path):
    from benchmarks.science_matrix import run_p43_resume_audit

    out_p = tmp_path / "p43-acceptance.json"
    report = run_p43_resume_audit("experiments/p43-config.json", out_p)
    assert out_p.exists()
    assert report["phase"] == "P43"
    assert report["verdict"] in ("ACCEPTED", "MIXED")
    assert report["equality"]["counters_match"] is True
    assert all(report["equality"]["fields"].values())
    assert all(r["refused"] for r in report["refusals"])
    assert report["resumed"]["worker"].get("generations") == 60


def test_p44_resident_audit_smoke(tmp_path):
    import torch as _torch

    from benchmarks.science_matrix import run_p44_resident_audit

    out_p = tmp_path / "p44-acceptance.json"
    report = run_p44_resident_audit("experiments/p44-config.json", out_p)
    assert out_p.exists()
    assert report["phase"] == "P44"
    assert report["verdict"] in ("ACCEPTED", "MIXED", "NOT_MEASURED")
    assert report["determinism"]["cpu"]["equal"] is True
    assert all(report["conformance"].values())
    assert report["invalidity"]["rejected"] is True
    if _torch.cuda.is_available():
        assert report["verdict"] == "ACCEPTED"
        assert report["profile_cuda"]["measured"] is True


def test_p45_envelope_audit_smoke(tmp_path):
    import json as _json

    import torch as _torch

    from benchmarks.science_matrix import run_p45_envelope_audit

    if not _torch.cuda.is_available():
        return
    cfg = {
        "phase": "P45",
        "formula": "x**2 + 3*x + 7",
        "pop_size": 32,
        "durations_60s": [3],
        "durations_600s": [4],
        "tracing_modes_60s": [True],
        "seed": 42,
        "verify_every_gens": 5,
        "checkpoint_every_sec": 2,
        "device": "cuda",
        "selection_rule": "smoke rule",
    }
    cfg_p = tmp_path / "p45-smoke-config.json"
    cfg_p.write_text(_json.dumps(cfg))
    out_p = tmp_path / "p45-acceptance.json"
    report = run_p45_envelope_audit(cfg_p, out_p)
    assert out_p.exists()
    assert report["phase"] == "P45"
    assert report["verdict"] in ("ACCEPTED", "MIXED")
    assert len(report["matrix_60s"]["tiers"]) == 1
    assert report["envelope_600s"] is not None
    assert all(t["counter_check"] for t in report["envelope_600s"]["tiers"])


def test_p46_catalogue_audit_smoke(tmp_path):
    import json as _json

    from benchmarks.science_matrix import run_p46_catalogue_audit

    cfg = _json.loads(
        (Path(__file__).resolve().parents[1] / "experiments" / "p46-config.json").read_text()
    )
    cfg["independent_refetch"] = False  # offline smoke; the frozen run re-fetches sources
    cfg_p = tmp_path / "p46-offline-config.json"
    cfg_p.write_text(_json.dumps(cfg))
    out_p = tmp_path / "p46-acceptance.json"
    report = run_p46_catalogue_audit(cfg_p, out_p)
    assert out_p.exists()
    assert report["independent_refetch"] is None
    checks = {k: v for k, v in report["checks"].items() if v is not None}
    assert report["status"] == "PASS"
    assert report["verdict"] == "PENDING_HUMAN_REVIEW"
    assert report["counts"]["open_confirmed"] >= 100
    assert report["counts"]["finite_search_candidates"] == 34
    assert all(checks.values())
    assert report["errors"] == []
    assert report["human_review"]["required"] is True
    assert report["human_review"]["status"] == "pending"


def test_p46_catalogue_rejects_bad_entries(tmp_path):
    import json as _json

    from benchmarks.science_matrix import run_p46_catalogue_audit

    cat_dir = tmp_path / "docs"
    cat_dir.mkdir()
    cat_p = cat_dir / "open-problems.json"
    entry = {
        "id": "erdos-3",
        "title": "Erdos Problem #3",
        "statement_excerpt": "excerpt",
        "area": "number theory",
        "primary_source": {
            "citation": "c",
            "url": "https://www.erdosproblems.com/3",
            "dataset": "d",
            "dataset_commit": "6754c649e41328f461412eb1d08ea72f1d4bb5d1",
        },
        "consulted_at": "2026-10-02",
        "state": "open-confirmed",
        "certificate_type": "proof_or_counterexample",
        "verifiability": "exact_statement_checkable",
        "partial_refs": [],
        "statement_sha256": "0" * 16,
    }
    bad = _json.loads(_json.dumps(entry))
    del bad["consulted_at"]
    dup = _json.loads(_json.dumps(entry))
    dup["statement_sha256"] = "0" * 16
    cat = {
        "phase": "p46-open-problem-catalogue",
        "source": {
            "primary": "p",
            "dataset": "d",
            "dataset_commit": "6754c649e41328f461412eb1d08ea72f1d4bb5d1",
            "license": "Apache-2.0",
        },
        "counts": {"open_confirmed": 2, "finite_search_candidates": 0},
        "open_confirmed": [bad, dup],
        "finite_search_candidates": [],
        "human_review": {"required": True, "status": "pending"},
    }
    cat_p.write_text(_json.dumps(cat))
    cfg_p = tmp_path / "cfg.json"
    cfg_p.write_text(_json.dumps({"phase": "P46", "catalogue_path": str(cat_p)}))
    report = run_p46_catalogue_audit(cfg_p, tmp_path / "out.json")
    assert report["status"] == "FAIL"
    assert report["verdict"] == "REJECTED"
    assert any("missing field consulted_at" in e for e in report["errors"])
    assert any("duplicate statement hashes" in e for e in report["errors"])
    assert any("below the frozen minimum" in e for e in report["errors"])


def test_p46_normalized_statement_dedup():
    from benchmarks.science_matrix import _p46_normalize_statement

    a = _p46_normalize_statement("If $A\\subseteq \\mathbb{N}$ then must ...")
    b = _p46_normalize_statement("if a subseteq mathbb n then must")
    assert a == b == "if a subseteq mathbb n then must"
    c = _p46_normalize_statement("Is there an odd covering system?")
    assert c != a


def test_p47_nomination_audit_smoke(tmp_path):
    from benchmarks.science_matrix import run_p47_nomination_audit

    out_p = tmp_path / "p47-acceptance.json"
    report = run_p47_nomination_audit("experiments/p47-config.json", out_p)
    assert out_p.exists()
    import json as _json

    _log = _json.loads(
        (
            Path(__file__).resolve().parents[1]
            / "experiments"
            / "p47-final-test"
            / "access-log.json"
        ).read_text()
    )
    if not _log:
        assert report["status"] == "PASS"
        assert report["final_test"]["access_log_empty"] is True
    else:
        # Post-P56 the final is open: the gate must keep firing on exactly
        # the emptiness condition, and every opening must be the authorized one.
        assert report["status"] == "FAIL"
        assert report["errors"] == ["final-test access log must exist and be empty"]
        assert report["final_test"]["access_log_empty"] is False
        assert all(
            e.get("phase") == "P56" and e.get("action") == "generate-sealed-final-tasks"
            for e in _log
        )
    assert report["freeze_recorded"] == report["nomination_sha256"]
    assert report["final_test"]["material"] == []
    assert report["final_test"]["forbidden_p38_ids"] == 10
    assert report["controls"] == {"known": 3, "false": 4}
    assert report["human_review"]["required"] is True


def test_p47_nomination_rejects_tampering_and_open_test(tmp_path):
    import copy as _copy
    import json as _json

    from benchmarks.science_matrix import run_p47_nomination_audit

    base = _json.loads(
        (Path(__file__).resolve().parents[1] / "experiments" / "p47-nomination.json").read_text()
    )
    tampered = _copy.deepcopy(base)
    tampered["hypothesis"]["mse_excluded_as_success"] = True
    tampered["thresholds"]["values"] = {"min_seeds": 3}
    tampered_p = tmp_path / "p47-tampered.json"
    tampered_p.write_text(_json.dumps(tampered))
    cfg_p = tmp_path / "cfg.json"
    cfg_p.write_text(
        _json.dumps(
            {
                "phase": "P47",
                "nomination_path": str(tampered_p),
                "p38_manifest_path": "experiments/p38-confirmation.json",
            }
        )
    )
    report = run_p47_nomination_audit(cfg_p, tmp_path / "out.json")
    assert report["status"] == "FAIL"
    assert report["verdict"] == "REJECTED"
    assert any("frozen hash mismatch" in e for e in report["errors"])
    assert any("pending human review" in e for e in report["errors"])


def test_p49_compact_audit_smoke(tmp_path):
    from benchmarks.science_matrix import run_p49_compact_audit

    out_p = tmp_path / "p49-acceptance.json"
    report = run_p49_compact_audit("experiments/p49-config.json", out_p)
    assert out_p.exists()
    assert report["phase"] == "P49"
    assert report["verdict"] in ("ACCEPTED", "MIXED")
    assert all(f["ok"] for f in report["findings"])
    assert report["counters"]["reconstructed"] == report["counters"]["reconstructed_total"] > 0
    assert "grammar-defined only" in report["coverage"]


def test_p50_search_controls_audit_smoke(tmp_path):
    import json as _json

    from benchmarks.science_matrix import run_p50_search_controls_audit

    cfg = _json.loads(
        (Path(__file__).resolve().parents[1] / "experiments" / "p50-config.json").read_text()
    )
    cfg["seeds"] = [42, 101]
    cfg["budget_sec_per_task"] = 0.3
    cfg["pop_size"] = 32
    cfg_p = tmp_path / "p50-smoke-config.json"
    cfg_p.write_text(_json.dumps(cfg))
    out_p = tmp_path / "p50-acceptance.json"
    report = run_p50_search_controls_audit(cfg_p, out_p)
    assert out_p.exists()
    assert report["phase"] == "P50"
    assert report["verdict"] == "ACCEPTED"
    assert report["criterion"]["same_for_all_arms"] is True
    assert all(v["rediscovered"] for v in report["tasks_known"].values())
    assert all(c["rejected"] for c in report["false_controls"])
    assert report["counters"]["certified"] >= len(report["tasks_known"])
    assert report["counters"]["false_rejected"] == report["counters"]["false_total"] == 4
    assert report["budgets"]["actual_search_sec"] > 0
    assert report["budgets"]["actual_verification_sec"] >= 0


def test_p50_classical_baseline_is_deterministic():
    import numpy as _np
    import torch as _torch

    from benchmarks.math_specialist import check_p50_false_controls, run_p50_arm_trial
    from evobyte.grammar import classical_interpolate_program, count_batch_stats

    xs = _np.linspace(-3.0, 3.0, 64, dtype=_np.float32)
    ys = (xs**2 + 3.0 * xs + 7.0).astype(_np.float32)
    rec = run_p50_arm_trial(
        "classical", "x**2 + 3*x + 7", xs, ys, 0.3, 42, _torch.device("cpu"), 32
    )
    assert rec["candidates_total"] >= 1
    assert rec["elapsed_sec"] < 0.3
    assert rec["best_mse"] == 0.0
    prog, _info = classical_interpolate_program(xs, ys, max_degree=2)
    assert prog is not None
    stats = count_batch_stats([prog, prog])
    assert stats == {"n": 2, "duplicates": 1, "invalid": 0}
    false = check_p50_false_controls()
    assert len(false) == 4
    assert all(c["rejected"] for c in false)


def _p59_dev_samples():
    import numpy as _np

    xs = _np.linspace(-3.0, 3.0, 24, dtype=_np.float32)
    ys = (xs**2 + 3.0 * xs + 7.0).astype(_np.float32)
    return xs, ys


def test_p59_leakage_sentinel_passes_structured_random():
    from benchmarks.math_specialist import run_p59_leakage_sentinel

    xs, ys = _p59_dev_samples()
    rep = run_p59_leakage_sentinel(
        "structured_random", xs, ys, "x**2 + 3*x + 10", "x**2 - 1", seed=7
    )
    assert rep["passed"] is True
    assert rep["proposals_sha256"] == rep["swapped_sha256"]
    assert rep["proposals_bytes"] > 0


def test_p59_leakage_sentinel_passes_evolution():
    from benchmarks.math_specialist import run_p59_leakage_sentinel

    xs, ys = _p59_dev_samples()
    rep = run_p59_leakage_sentinel(
        "evolution",
        xs,
        ys,
        "x**2 + 3*x + 10",
        "x**2 - 1",
        seed=7,
        pop_size=8,
        max_generations=2,
    )
    assert rep["passed"] is True
    assert rep["proposals_sha256"] == rep["swapped_sha256"]


def test_p59_compilation_control_depends_on_private_formula():
    from benchmarks.math_specialist import run_p59_compilation_control

    xs, ys = _p59_dev_samples()
    ctl_a = run_p59_compilation_control("x**2 + 3*x + 10", xs, ys)
    ctl_b = run_p59_compilation_control("x**2 - 1", xs, ys)
    assert ctl_a["control_kind"].startswith("compilation")
    assert ctl_a["construction_sec"] >= 0.0
    assert ctl_a["program_sha256"] != ctl_b["program_sha256"]


def test_p59_rejects_unknown_arm_and_vacuous_swap():
    import pytest as _pytest

    from benchmarks.math_specialist import p59_public_proposals, run_p59_leakage_sentinel

    xs, ys = _p59_dev_samples()
    with _pytest.raises(ValueError, match="Unknown P59 public arm"):
        p59_public_proposals("classical", xs, ys, seed=7)
    with _pytest.raises(ValueError, match="different private formulas"):
        run_p59_leakage_sentinel("structured_random", xs, ys, "x**2", "x**2", seed=7)


def test_p59_matched_es_same_inputs_both_arms():
    from benchmarks.open_problems import p59_es_public_inputs, run_p59_matched_es_trial

    inputs = p59_es_public_inputs(4)
    cpu = run_p59_matched_es_trial("cpu_enumeration", inputs)
    cls = run_p59_matched_es_trial("classical_construction", inputs)
    assert cpu["inputs_hash"] == cls["inputs_hash"]
    assert cpu["status"] == "certified" and cls["status"] == "certified"
    assert cpu["triple"] == [2, 3, 6] and cls["triple"] == [2, 3, 6]
    for rec in (cpu, cls):
        parts = rec["ledger"]["parts"]
        assert set(parts) == {"train", "generation", "inference", "filters", "checkers", "tracking"}
        assert rec["ledger"]["total_sec"] == sum(parts.values())


def test_p59_warm_start_origin_is_reported():
    from benchmarks.open_problems import p59_es_public_inputs, run_p59_matched_es_trial

    warm = p59_es_public_inputs(4, warm_start=[(2, 3, 6)])
    assert run_p59_matched_es_trial("classical_construction", warm)["origin"] == "warm-start"
    assert run_p59_matched_es_trial("cpu_enumeration", warm)["origin"] == "warm-start"
    cold = p59_es_public_inputs(4)
    assert run_p59_matched_es_trial("classical_construction", cold)["origin"] == ("classical-even")


def test_p59_cost_ledger_guards():
    import pytest as _pytest

    from benchmarks.open_problems import p59_cost_ledger

    good = p59_cost_ledger(
        train=0.0, generation=1.5, inference=0.0, filters=0.0, checkers=0.5, tracking=0.0
    )
    assert good["total_sec"] == 2.0
    with _pytest.raises(ValueError, match="exactly"):
        p59_cost_ledger(train=0.0, generation=1.0)
    with _pytest.raises(ValueError, match="must not be negative"):
        p59_cost_ledger(
            train=-1.0, generation=0.0, inference=0.0, filters=0.0, checkers=0.0, tracking=0.0
        )


def test_p59_comparison_scope_restricts_families():
    import pytest as _pytest

    from benchmarks.open_problems import (
        p59_comparison_scope,
        p59_es_public_inputs,
        run_p59_matched_es_trial,
    )

    scope = p59_comparison_scope("erdos-straus")
    assert scope["comparable"] is True
    assert set(scope["arms"]) == {"cpu_enumeration", "classical_construction"}
    for family in ("taxicab", "diophantine-quintuple", "no-such-family"):
        restricted = p59_comparison_scope(family)
        assert restricted["comparable"] is False
        assert restricted["reason"]
    with _pytest.raises(ValueError, match="Unknown P59 ES arm"):
        run_p59_matched_es_trial("gpu_search", p59_es_public_inputs(4))


def test_p60_workbench_manifest_is_complete():
    import json as _json

    repo = Path(__file__).resolve().parents[1]
    man = _json.loads((repo / "experiments" / "p60-workbench-manifest.json").read_text())
    assert man["phase"] == "P60" and man["version"] == 1
    assert len(man["development_tasks"]) == 6
    assert len({t["task_id"] for t in man["development_tasks"]}) == 6
    assert man["seeds"] == [7, 42, 101]
    budgets = man["budgets"]
    assert budgets["search_cert_per_attempt_sec"] == 10
    assert budgets["per_hypothesis_ceiling_min"] == 30
    assert budgets["model_reserve_params"] == 100000
    assert budgets["model_absolute_cap_params"] == 1000000
    assert all(v > 0 for v in budgets.values())
    assert set(man["screening"]) == {"PROMISING", "NULL", "INCONCLUSIVE", "BLOCKED"}
    assert len(man["mechanisms"]) == 10
    assert [m["id"] for m in man["mechanisms"]] == [f"H{i:02d}" for i in range(1, 11)]
    for mech in man["mechanisms"]:
        assert mech["hypothesis"] and mech["literature_overlap"] and mech["phase_file"]
        assert (repo / mech["phase_file"]).exists()
    blob = _json.dumps(man, sort_keys=True)
    assert "TBD" not in blob and "TODO" not in blob


def test_p60_frozen_config_matches_reviewed_manifest():
    import json as _json

    repo = Path(__file__).resolve().parents[1]
    man = _json.loads((repo / "experiments" / "p60-workbench-manifest.json").read_text())
    cfg = _json.loads((repo / "experiments" / "p60-config.json").read_text())
    assert cfg["phase"] == "P60"
    assert cfg["manifest_version"] == man["version"] == 1
    assert cfg["manifest_path"] == "experiments/p60-workbench-manifest.json"
    import hashlib as _hashlib

    assert (
        cfg["manifest_sha256"]
        == _hashlib.sha256((repo / cfg["manifest_path"]).read_bytes()).hexdigest()
    )
    assert [t["task_id"] for t in cfg["development_tasks"]] == [
        t["task_id"] for t in man["development_tasks"]
    ]
    assert cfg["seeds"] == man["seeds"]
    assert cfg["review"]["status"] == "accepted"
    assert (repo / cfg["review"]["record"]).exists()
    from benchmarks.science_matrix import _p60_final_tokens

    assert _p60_final_tokens(cfg) == []
    assert _p60_final_tokens({"ref": "experiments/p56-final-tasks.json"}) == ["p56-final"]
    assert _p60_final_tokens({"budgets": {"p71_per_method_h": 2}}) == []


def _p60_smoke_config(tmp_path):
    import json as _json

    repo = Path(__file__).resolve().parents[1]
    cfg = _json.loads((repo / "experiments" / "p60-config.json").read_text())
    cfg["require_clean_tree"] = False
    cfg_p = tmp_path / "p60-smoke-config.json"
    cfg_p.write_text(_json.dumps(cfg))
    return cfg_p


def test_p60_acceptance_smoke(tmp_path):
    out_p = tmp_path / "p60-acceptance.json"
    report = run_p60_workbench_audit(_p60_smoke_config(tmp_path), out_p)
    assert out_p.exists()
    assert report["phase"] == "P60"
    assert report["verdict"] == "ACCEPTED"
    assert report["counters"]["dev_tasks"] == 6
    assert report["counters"]["dev_certified"] == report["counters"]["dev_trials"] == 12
    by_task: dict[str, set[str]] = {}
    for entry in report["dev_trials"]:
        by_task.setdefault(entry["task"], set()).add(entry["inputs_hash"])
    assert all(hashes == {next(iter(hashes))} for hashes in by_task.values())
    assert report["budgets"]["measured_sec"] <= report["budgets"]["ceiling_sec"]


def test_p60_acceptance_blocks_manifest_mismatch(tmp_path):
    import json as _json

    cfg_p = _p60_smoke_config(tmp_path)
    cfg = _json.loads(cfg_p.read_text())
    cfg["manifest_sha256"] = "0" * 64
    cfg_p.write_text(_json.dumps(cfg))
    report = run_p60_workbench_audit(cfg_p, tmp_path / "p60-out.json")
    assert report["verdict"] == "BLOCKED"
    assert any("MANIFEST_MISMATCH" in f for f in report["findings"])


def test_p60_acceptance_blocks_final_reference(tmp_path):
    import json as _json

    cfg_p = _p60_smoke_config(tmp_path)
    cfg = _json.loads(cfg_p.read_text())
    cfg["notes_path"] = "experiments/p56-final-tasks.json"
    cfg_p.write_text(_json.dumps(cfg))
    report = run_p60_workbench_audit(cfg_p, tmp_path / "p60-out.json")
    assert report["verdict"] == "BLOCKED"
    assert any("FINAL_ACCESS" in f for f in report["findings"])


def _p61_smoke_config(tmp_path):
    import json as _json

    repo = Path(__file__).resolve().parents[1]
    cfg = _json.loads((repo / "experiments" / "p61-config.json").read_text())
    cfg["instances"] = [
        {
            "n": 4,
            "seed": 11,
            "must_include": [[2, 3, 6]],
            "random_count": 50,
            "random_bound": 100,
            "boxes": [[1, 10]],
        }
    ]
    cfg["require_clean_tree"] = False
    cfg_p = tmp_path / "p61-smoke-config.json"
    cfg_p.write_text(_json.dumps(cfg))
    return cfg_p


def test_p61_acceptance_smoke(tmp_path):
    out_p = tmp_path / "p61-acceptance.json"
    report = run_p61_shadow_audit(_p61_smoke_config(tmp_path), out_p)
    assert out_p.exists()
    assert report["phase"] == "P61"
    assert report["verdict"] == "ACCEPTED"
    assert report["hypothesis_outcome"] in ("PROMISING", "NULL")
    assert report["counters"]["certificates"] >= 1
    assert report["counters"]["instances"] == 1


def test_p61_acceptance_blocks_final_reference(tmp_path):
    import json as _json

    cfg_p = _p61_smoke_config(tmp_path)
    cfg = _json.loads(cfg_p.read_text())
    cfg["notes_path"] = "experiments/p56-final-tasks.json"
    cfg_p.write_text(_json.dumps(cfg))
    report = run_p61_shadow_audit(cfg_p, tmp_path / "p61-out.json")
    assert report["verdict"] == "BLOCKED"
    assert any("FINAL_ACCESS" in f for f in report["findings"])


def test_p61_acceptance_blocks_empty_candidates(tmp_path):
    import json as _json

    cfg_p = _p61_smoke_config(tmp_path)
    cfg = _json.loads(cfg_p.read_text())
    cfg["instances"] = [
        {
            "n": 4,
            "seed": 11,
            "must_include": [],
            "random_count": 0,
            "random_bound": 100,
            "boxes": [],
        }
    ]
    cfg_p.write_text(_json.dumps(cfg))
    report = run_p61_shadow_audit(cfg_p, tmp_path / "p61-out.json")
    assert report["verdict"] == "BLOCKED"
    assert any("CONFIG_INVALID" in f for f in report["findings"])


def _p62_smoke_config(tmp_path):
    import json as _json

    repo = Path(__file__).resolve().parents[1]
    cfg = _json.loads((repo / "experiments" / "p62-config.json").read_text())
    cfg["require_clean_tree"] = False
    cfg_p = tmp_path / "p62-smoke-config.json"
    cfg_p.write_text(_json.dumps(cfg))
    return cfg_p


def test_p62_acceptance_smoke(tmp_path):
    out_p = tmp_path / "p62-acceptance.json"
    report = run_p62_repair_audit(_p62_smoke_config(tmp_path), out_p)
    assert out_p.exists()
    assert report["phase"] == "P62"
    assert report["verdict"] == "ACCEPTED"
    assert report["hypothesis_outcome"] in ("PROMISING", "NULL")
    assert set(report["comparison"]) == {"classical", "random", "learned"}
    assert report["training"]["n_params"] <= 100000


def test_p62_acceptance_blocks_split_leak(tmp_path):
    import json as _json

    cfg_p = _p62_smoke_config(tmp_path)
    cfg = _json.loads(cfg_p.read_text())
    cfg["dev_starts"] = [[4, [2, 4, 6]]]
    cfg_p.write_text(_json.dumps(cfg))
    report = run_p62_repair_audit(cfg_p, tmp_path / "p62-out.json")
    assert report["verdict"] == "BLOCKED"
    assert any("SPLIT_LEAK" in f for f in report["findings"])


def test_p62_acceptance_blocks_final_reference(tmp_path):
    import json as _json

    cfg_p = _p62_smoke_config(tmp_path)
    cfg = _json.loads(cfg_p.read_text())
    cfg["notes_path"] = "experiments/p56-final-tasks.json"
    cfg_p.write_text(_json.dumps(cfg))
    report = run_p62_repair_audit(cfg_p, tmp_path / "p62-out.json")
    assert report["verdict"] == "BLOCKED"
    assert any("FINAL_ACCESS" in f for f in report["findings"])


def _p63_smoke_config(tmp_path):
    import json as _json

    repo = Path(__file__).resolve().parents[1]
    cfg = _json.loads((repo / "experiments" / "p63-config.json").read_text())
    cfg["require_clean_tree"] = False
    cfg_p = tmp_path / "p63-smoke-config.json"
    cfg_p.write_text(_json.dumps(cfg))
    return cfg_p


def test_p63_acceptance_smoke(tmp_path):
    out_p = tmp_path / "p63-acceptance.json"
    report = run_p63_feedback_audit(_p63_smoke_config(tmp_path), out_p)
    assert out_p.exists()
    assert report["phase"] == "P63"
    assert report["verdict"] == "ACCEPTED"
    assert report["hypothesis_outcome"] in ("PROMISING", "NULL")
    assert set(report["comparison"]) == {"real", "shuffled", "scalar"}
    assert report["training"]["n_params"] <= 100000


def test_p63_acceptance_blocks_split_leak(tmp_path):
    import json as _json

    cfg_p = _p63_smoke_config(tmp_path)
    cfg = _json.loads(cfg_p.read_text())
    cfg["dev_starts"] = [[4, [2, 4, 6]]]
    cfg_p.write_text(_json.dumps(cfg))
    report = run_p63_feedback_audit(cfg_p, tmp_path / "p63-out.json")
    assert report["verdict"] == "BLOCKED"
    assert any("SPLIT_LEAK" in f for f in report["findings"])


def test_p63_acceptance_blocks_final_reference(tmp_path):
    import json as _json

    cfg_p = _p63_smoke_config(tmp_path)
    cfg = _json.loads(cfg_p.read_text())
    cfg["notes_path"] = "experiments/p56-final-tasks.json"
    cfg_p.write_text(_json.dumps(cfg))
    report = run_p63_feedback_audit(cfg_p, tmp_path / "p63-out.json")
    assert report["verdict"] == "BLOCKED"
    assert any("FINAL_ACCESS" in f for f in report["findings"])


def _p64_smoke_config(tmp_path):
    import json as _json

    repo = Path(__file__).resolve().parents[1]
    cfg = _json.loads((repo / "experiments" / "p64-config.json").read_text())
    cfg["require_clean_tree"] = False
    cfg_p = tmp_path / "p64-smoke-config.json"
    cfg_p.write_text(_json.dumps(cfg))
    return cfg_p


def test_p64_acceptance_smoke(tmp_path):
    out_p = tmp_path / "p64-acceptance.json"
    report = run_p64_obstruction_audit(_p64_smoke_config(tmp_path), out_p)
    assert out_p.exists()
    assert report["phase"] == "P64"
    assert report["verdict"] == "ACCEPTED"
    assert report["hypothesis_outcome"] in ("PROMISING", "NULL")
    assert {r["status"] for r in report["rules"]} == {"PROVEN", "REFUTED"}
    assert report["known_valid_kept"] == 3
    assert report["scan_unfiltered_fraction"] >= 0.1


def test_p64_acceptance_blocks_empty_rules(tmp_path):
    import json as _json

    cfg_p = _p64_smoke_config(tmp_path)
    cfg = _json.loads(cfg_p.read_text())
    cfg["rules"] = []
    cfg_p.write_text(_json.dumps(cfg))
    report = run_p64_obstruction_audit(cfg_p, tmp_path / "p64-out.json")
    assert report["verdict"] == "BLOCKED"
    assert any("CONFIG_INVALID" in f for f in report["findings"])


def test_p64_acceptance_blocks_final_reference(tmp_path):
    import json as _json

    cfg_p = _p64_smoke_config(tmp_path)
    cfg = _json.loads(cfg_p.read_text())
    cfg["notes_path"] = "experiments/p56-final-tasks.json"
    cfg_p.write_text(_json.dumps(cfg))
    report = run_p64_obstruction_audit(cfg_p, tmp_path / "p64-out.json")
    assert report["verdict"] == "BLOCKED"
    assert any("FINAL_ACCESS" in f for f in report["findings"])


def _p59_smoke_config(tmp_path):
    import json as _json

    repo = Path(__file__).resolve().parents[1]
    cfg = _json.loads((repo / "experiments" / "p59-config.json").read_text())
    cfg["es_instances"] = [4]
    cfg["require_clean_tree"] = False
    cfg_p = tmp_path / "p59-smoke-config.json"
    cfg_p.write_text(_json.dumps(cfg))
    return cfg_p


def test_p59_acceptance_smoke(tmp_path):
    out_p = tmp_path / "p59-acceptance.json"
    report = run_p59_equal_information_audit(_p59_smoke_config(tmp_path), out_p)
    assert out_p.exists()
    assert report["phase"] == "P59"
    assert report["verdict"] == "ACCEPTED"
    assert {t["inputs_hash"] for t in report["es_trials"]} == {
        report["es_trials"][0]["inputs_hash"]
    }
    assert report["counters"]["es_certified"] == 2
    assert report["counters"]["sentinels_passed"] == report["counters"]["sentinels"] == 2
    assert report["counters"]["compilations"] == 1
    assert "no statistical gain claimed" in report["claim_scope"]


def test_p59_acceptance_blocks_final_reference(tmp_path):
    import json as _json

    cfg_p = _p59_smoke_config(tmp_path)
    cfg = _json.loads(cfg_p.read_text())
    cfg["final_tasks_path"] = "experiments/p56-final-tasks.json"
    cfg_p.write_text(_json.dumps(cfg))
    report = run_p59_equal_information_audit(cfg_p, tmp_path / "p59-out.json")
    assert report["verdict"] == "BLOCKED"
    assert any("FINAL_ACCESS" in f for f in report["findings"])


def test_p59_acceptance_blocks_uncomparable_family(tmp_path):
    import json as _json

    cfg_p = _p59_smoke_config(tmp_path)
    cfg = _json.loads(cfg_p.read_text())
    cfg["families"] = ["taxicab"]
    cfg_p.write_text(_json.dumps(cfg))
    report = run_p59_equal_information_audit(cfg_p, tmp_path / "p59-out.json")
    assert report["verdict"] == "BLOCKED"
    assert any("SCOPE_RESTRICTED" in f for f in report["findings"])


def test_p51_replay_map_audit_smoke(tmp_path):
    import json as _json

    from benchmarks.science_matrix import run_p51_replay_map_audit

    cfg = _json.loads(
        (Path(__file__).resolve().parents[1] / "experiments" / "p51-config.json").read_text()
    )
    cfg["seed"] = 7
    cfg["pop_size"] = 16
    cfg["n_generations"] = 3
    cfg["max_nodes"] = 20
    cfg_p = tmp_path / "p51-smoke-config.json"
    cfg_p.write_text(_json.dumps(cfg))
    out_p = tmp_path / "p51-acceptance.json"
    report = run_p51_replay_map_audit(cfg_p, out_p)
    assert out_p.exists()
    assert report["phase"] == "P51"
    assert report["verdict"] == "ACCEPTED"
    assert all(report["checks"].values())
    assert report["coverage"] == "partial_sampled"
    assert report["map"]["nodes"] <= 20
    assert report["counters"]["segments_matched"] == report["counters"]["segments_declared"] > 0
    assert report["counters"]["certificates"] == len(report["certificate_references"]) > 0


def test_p52_certified_data_audit_smoke(tmp_path):
    import json as _json

    from benchmarks.science_matrix import run_p52_certified_data_audit

    repo = Path(__file__).resolve().parents[1]
    cfg = _json.loads((repo / "experiments" / "p52-config.json").read_text())
    cfg["corpus_manifest"] = "experiments/p52-certified-data.json"
    cfg["minimums"] = {
        "train_positives": 6,
        "train_groups": 2,
        "val_positives": 2,
        "val_groups": 1,
    }
    cfg_p = tmp_path / "p52-smoke-config.json"
    cfg_p.write_text(_json.dumps(cfg))
    out_p = tmp_path / "p52-acceptance.json"
    report = run_p52_certified_data_audit(cfg_p, out_p)
    assert out_p.exists()
    assert report["phase"] == "P52"
    assert report["verdict"] == "ACCEPTED"
    assert report["rechecked_exact"] == report["rechecked_total"] > 0
    assert report["negatives_rejected"] == report["negatives_total"] == 6
    assert report["minimums_met"] is True
    assert report["splits"]["group_overlap"] == []


def test_p53_proposer_audit_smoke(tmp_path):
    import json as _json

    from benchmarks.science_matrix import run_p53_proposer_audit

    cfg = _json.loads(
        (Path(__file__).resolve().parents[1] / "experiments" / "p53-config.json").read_text()
    )
    cfg["max_epochs"] = 2
    cfg["n_sample"] = 8
    cfg_p = tmp_path / "p53-smoke-config.json"
    cfg_p.write_text(_json.dumps(cfg))
    out_p = tmp_path / "p53-acceptance.json"
    report = run_p53_proposer_audit(cfg_p, out_p)
    assert out_p.exists()
    assert report["phase"] == "P53"
    assert report["verdict"] == "ACCEPTED"
    assert all(report["checks"].values())
    assert report["model"]["param_count"] <= 1_000_000
    assert report["sampling"]["valid_rate"] == 1.0
    assert report["sampling"]["floor_fraction"] >= 0.10


def test_p54_utility_audit_smoke(tmp_path):
    import json as _json

    from benchmarks.science_matrix import run_p54_utility_audit

    cfg = _json.loads(
        (Path(__file__).resolve().parents[1] / "experiments" / "p54-config.json").read_text()
    )
    cfg["task_ids"] = ["p52_va_0000"]
    cfg["seeds"] = [42, 101]
    cfg["screen_sec"] = 0.3
    cfg["confirm_sec"] = 0.5
    cfg["pop_size"] = 16
    cfg["hybrid_proposals"] = 8
    cfg_p = tmp_path / "p54-smoke-config.json"
    cfg_p.write_text(_json.dumps(cfg))
    out_p = tmp_path / "p54-acceptance.json"
    report = run_p54_utility_audit(cfg_p, out_p)
    assert out_p.exists()
    assert report["phase"] == "P54"
    assert report["verdict"] in ("KEEP", "DROP", "INCONCLUSIVE", "MIXED")
    assert report["pilot"]["screen_ok"] is True
    assert set(report["pilot"]["arms"]) == {"structured_random", "evolution", "classical", "hybrid"}
    assert report["pilot"]["thresholds_frozen"]["keep_ratio"] == 0.8
    assert report["pilot"]["negatives_ok"] is True


def test_p55_sampling_audit_deferred(tmp_path):
    from benchmarks.science_matrix import run_p55_sampling_audit

    out_p = tmp_path / "p55-acceptance.json"
    report = run_p55_sampling_audit("experiments/p55-config.json", out_p)
    assert out_p.exists()
    assert report["phase"] == "P55"
    assert report["verdict"] == "DEFERRED"
    assert report["gate"]["execute"] is False
    assert report["budgets"]["compute_sec"] == 0.0
    assert report["counters"]["comparisons_run"] == 0
    assert report["gate"]["historical"]["result"] == "NULL"
    assert "P56" in report["continuation"]
    blob = out_p.read_text().lower()
    assert "quantum advantage" not in blob
    assert "quantum hardware" not in blob


def test_p56_fresh_tasks_exclude_development_targets():
    import json as _json

    from benchmarks.science_matrix import _p56_fresh_tasks

    corpus = _json.loads(
        (
            Path(__file__).resolve().parents[1] / "experiments" / "p52-certified-data.json"
        ).read_text()
    )
    dev = {p["ground_truth_expr"] for p in corpus["positives"]}
    tasks = _p56_fresh_tasks(final_seed=56056, n_tasks=6, dev_formulas=dev)
    assert len(tasks) == 6
    assert len({t["group_id"] for t in tasks}) == 6
    assert not ({t["canonical_formula"] for t in tasks} & dev)
    again = _p56_fresh_tasks(final_seed=56056, n_tasks=6, dev_formulas=dev)
    assert [t["group_id"] for t in again] == [t["group_id"] for t in tasks]


def test_p56_confirmation_audit_smoke_dev_override(tmp_path):
    import json as _json

    from benchmarks.science_matrix import run_p56_confirmation_audit

    repo = Path(__file__).resolve().parents[1]
    seal_path = repo / "experiments" / "p56-final-tasks.json"
    log_path = repo / "experiments" / "p47-final-test" / "access-log.json"
    log_before = log_path.read_text()
    seal_before = seal_path.read_bytes() if seal_path.exists() else None
    cfg = _json.loads((repo / "experiments" / "p56-config.json").read_text())
    cfg["task_override_ids"] = ["p52_va_0000", "p52_va_0001"]
    cfg["seeds"] = [900, 901]
    cfg["budget_sec"] = 0.3
    cfg["pop_size"] = 16
    cfg["clean_rerun_max_controls"] = 4
    cfg_p = tmp_path / "p56-smoke-config.json"
    cfg_p.write_text(_json.dumps(cfg))
    out_p = tmp_path / "p56-acceptance.json"
    report = run_p56_confirmation_audit(cfg_p, out_p)
    assert out_p.exists()
    assert report["phase"] == "P56"
    assert report["verdict"] == "CONFIRMED"
    assert report["task_origin"] == "dev-override (test only, never final)"
    assert report["result_label"].startswith("provisional-confirmation")
    assert "discovery" in report["result_label"] and "never" in report["result_label"]
    assert report["clean_rerun"]["ok"] is True
    seal_after = seal_path.read_bytes() if seal_path.exists() else None
    assert seal_after == seal_before
    assert log_path.read_text() == log_before


def test_p57_campaign_audit_smoke(tmp_path):
    import json as _json

    from benchmarks.science_matrix import run_p57_campaign_audit

    repo = Path(__file__).resolve().parents[1]
    cfg = _json.loads((repo / "experiments" / "p57-config.json").read_text())
    cfg["instances"] = [73, 97, 193]
    cfg["limit"] = 200
    cfg["device"] = "cpu"
    cfg["batch_size"] = 50000
    cfg["time_cap_sec"] = 120.0
    cfg["certificates_path"] = str(tmp_path / "p57-smoke-certs.json")
    cfg_p = tmp_path / "p57-smoke-config.json"
    cfg_p.write_text(_json.dumps(cfg))
    out_p = tmp_path / "p57-acceptance.json"
    report = run_p57_campaign_audit(cfg_p, out_p)
    assert out_p.exists()
    assert report["phase"] == "P57"
    assert report["verdict"] in ("COMPLETE", "INCOMPLETE")
    assert report["counters"]["nominated"] == 3
    assert report["counters"]["certified"] + report["counters"]["budget_exhausted"] == 3
    assert "exhaustive-null" not in report["by_status"]
    blob = out_p.read_text().lower()
    assert "discovery claimed" not in blob or "no discovery claimed" in blob


_P58_R1_IDS = [
    "p46-catalogue-review",
    "p47-nomination-review",
    "p48-translation-review",
    "p54-statistical-review",
    "p56-independent-review",
    "p58-scope-review",
]


def _p58_valid_decisions(tmp_path, *, disposition="reference_only", scientific_approval="pending"):
    import hashlib as _hashlib
    import json as _json

    decisions = []
    for did in _P58_R1_IDS:
        ev = tmp_path / f"evidence-{did}.json"
        ev.write_text(_json.dumps({"id": did, "opinion": "restricted reference only"}))
        sha = _hashlib.sha256(ev.read_bytes()).hexdigest()
        decisions.append(
            {
                "id": did,
                "owner": "alexandre",
                "executor": "executor-agent",
                "date": "2026-10-07",
                "scope": "p58 technical base only",
                "justification": "preserve pendency with restriction",
                "authorization_origin": "D019 delegated review 2026-10-06",
                "reviewed_review": "phase file plus acceptance artifact",
                "evidence_path": str(ev),
                "evidence_sha256": sha,
                "disposition": disposition,
                "allowed_uses": ["reconciliation-audit"],
                "prohibited_uses": ["novelty-claim", "final-test", "superiority-claim"],
                "scientific_approval": scientific_approval,
            }
        )
    code_review = {
        "status": "accepted",
        "reviewer": "test-reviewer",
        "review_id": "p58-r1-test-review-001",
        "date": "2026-10-07",
        "scope": "R1 decision contract",
    }
    return decisions, code_review


def _p58_smoke_config(
    tmp_path,
    repo,
    *,
    approvals,
    require_clean_tree,
    n_certs=3,
    durable_raw=None,
    recoveries=None,
    decisions="valid",
    code_review="valid",
):
    import json as _json

    certs = _json.loads((repo / "experiments" / "p57-certificates.json").read_text())[:n_certs]
    cert_path = tmp_path / "p58-smoke-certs.json"
    cert_path.write_text(_json.dumps(certs))
    cfg = {
        "phase": "P58",
        "sealed_manifests": ["experiments/p56-final-tasks.json"],
        "certificates_path": str(cert_path),
        "certificates_expected": n_certs,
        "durable_raw": durable_raw
        if durable_raw is not None
        else [
            "experiments/p52-certified-data-raw.json",
            "experiments/no-such-raw.json",
        ],
        "device": "cpu",
        "require_clean_tree": require_clean_tree,
        "approvals": approvals,
        "recoveries": recoveries if recoveries is not None else [],
    }
    if decisions == "valid":
        valid_decisions, valid_review = _p58_valid_decisions(tmp_path)
        cfg["decisions"] = valid_decisions
        if code_review == "valid":
            cfg["code_review"] = valid_review
        elif code_review != "omit":
            cfg["code_review"] = code_review
    elif decisions != "omit":
        cfg["decisions"] = decisions
        if code_review == "valid":
            _, valid_review = _p58_valid_decisions(tmp_path)
            cfg["code_review"] = valid_review
        elif code_review != "omit":
            cfg["code_review"] = code_review
    else:
        if code_review == "valid":
            _, valid_review = _p58_valid_decisions(tmp_path)
            cfg["code_review"] = valid_review
        elif code_review != "omit":
            cfg["code_review"] = code_review
    cfg_p = tmp_path / "p58-smoke-config.json"
    cfg_p.write_text(_json.dumps(cfg))
    return cfg_p


def test_p58_blocks_on_pending_approval_and_missing_raw(tmp_path):
    repo = Path(__file__).resolve().parents[1]
    cfg_p = _p58_smoke_config(
        tmp_path,
        repo,
        approvals=[{"id": "p58-scope-review", "status": "pending"}],
        require_clean_tree=False,
    )
    out_p = tmp_path / "p58-acceptance.json"
    report = run_p58_acceptance_baseline_audit(cfg_p, out_p)
    assert out_p.exists()
    assert report["phase"] == "P58"
    assert report["verdict"] == "BLOCKED"
    assert report["certificates"]["rechecked_exact"] == 3
    assert any("MISSING_EVIDENCE" in f for f in report["findings"])
    # R3 waiver: the valid restrictive decision excuses the pending approval
    # for the technical-base scope, so raw absence alone blocks here.
    assert "p58-scope-review" in report["approvals_excused"]
    assert report["approvals_pending"] == []


def test_p58_r3_pending_without_decision_still_blocks(tmp_path):
    repo = Path(__file__).resolve().parents[1]
    cfg_p = _p58_smoke_config(
        tmp_path,
        repo,
        approvals=[{"id": "p58-scope-review", "status": "pending"}],
        require_clean_tree=False,
        durable_raw=["experiments/p52-certified-data-raw.json"],
        decisions="omit",
    )
    report = run_p58_acceptance_baseline_audit(cfg_p, tmp_path / "p58-out.json")
    assert report["verdict"] == "BLOCKED"
    assert any("PENDING_APPROVAL" in f for f in report["findings"])
    assert "p58-scope-review" in report["approvals_pending"]
    assert report["approvals_excused"] == []


def test_p58_r3_broken_decision_never_excuses(tmp_path):
    repo = Path(__file__).resolve().parents[1]
    decisions, _ = _p58_valid_decisions(tmp_path)
    decisions = [
        dict(d, disposition="approved_for_current_use", scientific_approval="pending")
        if d["id"] == "p58-scope-review"
        else d
        for d in decisions
    ]
    cfg_p = _p58_smoke_config(
        tmp_path,
        repo,
        approvals=[{"id": "p58-scope-review", "status": "pending"}],
        require_clean_tree=False,
        durable_raw=["experiments/p52-certified-data-raw.json"],
        decisions=decisions,
    )
    report = run_p58_acceptance_baseline_audit(cfg_p, tmp_path / "p58-out.json")
    assert report["verdict"] == "BLOCKED"
    assert any("PENDING_APPROVAL" in f for f in report["findings"])
    assert any("approved_for_current_use" in f for f in report["findings"])
    assert "p58-scope-review" in report["approvals_pending"]


def test_p58_r3_frozen_config_decisions_are_valid():
    import hashlib as _hashlib
    import json as _json

    repo = Path(__file__).resolve().parents[1]
    cfg = _json.loads((repo / "experiments" / "p58-config.json").read_text())
    assert cfg["phase"] == "P58"
    assert {d["id"] for d in cfg["decisions"]} == set(_P58_R1_IDS)
    for dec in cfg["decisions"]:
        blob = (repo / dec["evidence_path"]).read_bytes()
        assert dec["evidence_sha256"] == _hashlib.sha256(blob).hexdigest()
        assert dec["disposition"] in (
            "reference_only",
            "excluded_from_claims",
            "approved_for_current_use",
        )
        assert dec["prohibited_uses"]
        assert set(map(str, dec["allowed_uses"])).isdisjoint(dec["prohibited_uses"])
    assert cfg["code_review"]["status"] == "accepted"
    assert cfg["code_review"]["reviewer"]
    assert cfg["code_review"]["review_id"]


def test_p58_accepts_when_evidence_complete_and_approved(tmp_path):
    repo = Path(__file__).resolve().parents[1]
    cfg_p = _p58_smoke_config(
        tmp_path,
        repo,
        approvals=[{"id": "p58-scope-review", "status": "approved"}],
        require_clean_tree=False,
    )
    import json as _json

    cfg = _json.loads(cfg_p.read_text())
    cfg["durable_raw"] = ["experiments/p52-certified-data-raw.json"]
    cfg_p.write_text(_json.dumps(cfg))
    out_p = tmp_path / "p58-acceptance.json"
    report = run_p58_acceptance_baseline_audit(cfg_p, out_p)
    assert report["verdict"] == "ACCEPTED"
    assert report["counters"]["sealed_ok"] == 1
    assert report["counters"]["certificates_rechecked"] == 3


def test_p58_rejects_wrong_phase_config(tmp_path):
    import json as _json

    import pytest as _pytest

    cfg_p = tmp_path / "p58-wrong-config.json"
    cfg_p.write_text(_json.dumps({"phase": "P57"}))
    with _pytest.raises(ValueError, match="not a P58 configuration"):
        run_p58_acceptance_baseline_audit(cfg_p, tmp_path / "p58-out.json")


def test_p58_recovery_copies_absent_dest_with_hash(tmp_path):
    import hashlib as _hashlib
    import json as _json

    repo = Path(__file__).resolve().parents[1]
    src = tmp_path / "transient-evidence.json"
    src.write_text(_json.dumps({"phase": "PX", "verdict": "COMPLETE"}))
    cfg_p = _p58_smoke_config(
        tmp_path,
        repo,
        approvals=[{"id": "p58-scope-review", "status": "approved"}],
        require_clean_tree=False,
        durable_raw=["experiments/p52-certified-data-raw.json"],
        recoveries=[{"phase": "PX", "src": str(src), "dest": str(tmp_path / "durable-px.json")}],
    )
    out_p = tmp_path / "p58-acceptance.json"
    report = run_p58_acceptance_baseline_audit(cfg_p, out_p)
    assert report["verdict"] == "ACCEPTED"
    assert report["counters"]["recovery_recovered"] == 1
    rec = report["recovery"][0]
    assert rec["status"] == "RECOVERED_UNSEALED"
    assert rec["size"] == src.stat().st_size
    assert rec["sha256"] == _hashlib.sha256(src.read_bytes()).hexdigest()
    assert (tmp_path / "durable-px.json").read_bytes() == src.read_bytes()


def test_p58_recovery_refuses_to_overwrite_durable(tmp_path):
    repo = Path(__file__).resolve().parents[1]
    src = tmp_path / "transient-evidence.json"
    src.write_text('{"new": true}')
    dest = tmp_path / "durable-px.json"
    dest.write_text('{"sealed": true}')
    cfg_p = _p58_smoke_config(
        tmp_path,
        repo,
        approvals=[{"id": "p58-scope-review", "status": "approved"}],
        require_clean_tree=False,
        durable_raw=["experiments/p52-certified-data-raw.json"],
        recoveries=[{"phase": "PX", "src": str(src), "dest": str(dest)}],
    )
    out_p = tmp_path / "p58-acceptance.json"
    report = run_p58_acceptance_baseline_audit(cfg_p, out_p)
    assert report["verdict"] == "ACCEPTED"
    assert report["recovery"][0]["status"] == "ALREADY_DURABLE"
    assert dest.read_text() == '{"sealed": true}'


def test_p58_recovery_missing_both_is_blocked(tmp_path):
    repo = Path(__file__).resolve().parents[1]
    cfg_p = _p58_smoke_config(
        tmp_path,
        repo,
        approvals=[{"id": "p58-scope-review", "status": "approved"}],
        require_clean_tree=False,
        durable_raw=["experiments/p52-certified-data-raw.json"],
        recoveries=[
            {
                "phase": "PX",
                "src": str(tmp_path / "no-transient.json"),
                "dest": str(tmp_path / "no-durable.json"),
            }
        ],
    )
    out_p = tmp_path / "p58-acceptance.json"
    report = run_p58_acceptance_baseline_audit(cfg_p, out_p)
    assert report["verdict"] == "BLOCKED"
    assert report["counters"]["recovery_missing"] == 1
    assert any("MISSING_EVIDENCE" in f for f in report["findings"])


def test_p58_r1_rejects_absent_decisions(tmp_path):
    repo = Path(__file__).resolve().parents[1]
    cfg_p = _p58_smoke_config(
        tmp_path,
        repo,
        approvals=[{"id": "p58-scope-review", "status": "approved"}],
        require_clean_tree=False,
        durable_raw=["experiments/p52-certified-data-raw.json"],
        decisions="omit",
    )
    report = run_p58_acceptance_baseline_audit(cfg_p, tmp_path / "p58-out.json")
    assert report["verdict"] == "BLOCKED"
    assert any("DECISION_CONTRACT" in f for f in report["findings"])


def test_p58_r1_rejects_duplicate_decision_id(tmp_path):
    import json as _json

    repo = Path(__file__).resolve().parents[1]
    decisions, _ = _p58_valid_decisions(tmp_path)
    decisions = decisions + [dict(decisions[0])]
    cfg_p = _p58_smoke_config(
        tmp_path,
        repo,
        approvals=[{"id": "p58-scope-review", "status": "approved"}],
        require_clean_tree=False,
        durable_raw=["experiments/p52-certified-data-raw.json"],
        decisions=decisions,
    )
    cfg = _json.loads(cfg_p.read_text())
    assert len(cfg["decisions"]) == 7
    report = run_p58_acceptance_baseline_audit(cfg_p, tmp_path / "p58-out.json")
    assert report["verdict"] == "BLOCKED"
    assert any("duplicated" in f for f in report["findings"])


def test_p58_r1_rejects_evidence_hash_mismatch(tmp_path):
    repo = Path(__file__).resolve().parents[1]
    decisions, _ = _p58_valid_decisions(tmp_path)
    decisions[0] = dict(decisions[0], evidence_sha256="0" * 64)
    cfg_p = _p58_smoke_config(
        tmp_path,
        repo,
        approvals=[{"id": "p58-scope-review", "status": "approved"}],
        require_clean_tree=False,
        durable_raw=["experiments/p52-certified-data-raw.json"],
        decisions=decisions,
    )
    report = run_p58_acceptance_baseline_audit(cfg_p, tmp_path / "p58-out.json")
    assert report["verdict"] == "BLOCKED"
    assert any("hash mismatch" in f for f in report["findings"])


def test_p58_r1_rejects_missing_code_review(tmp_path):
    repo = Path(__file__).resolve().parents[1]
    cfg_p = _p58_smoke_config(
        tmp_path,
        repo,
        approvals=[{"id": "p58-scope-review", "status": "approved"}],
        require_clean_tree=False,
        durable_raw=["experiments/p52-certified-data-raw.json"],
        code_review="omit",
    )
    report = run_p58_acceptance_baseline_audit(cfg_p, tmp_path / "p58-out.json")
    assert report["verdict"] == "BLOCKED"
    assert any("CODE_REVIEW" in f for f in report["findings"])


def test_p58_r1_rejects_approved_use_without_scientific_approval(tmp_path):
    repo = Path(__file__).resolve().parents[1]
    decisions, _ = _p58_valid_decisions(tmp_path)
    decisions[0] = dict(
        decisions[0], disposition="approved_for_current_use", scientific_approval="pending"
    )
    cfg_p = _p58_smoke_config(
        tmp_path,
        repo,
        approvals=[{"id": "p58-scope-review", "status": "approved"}],
        require_clean_tree=False,
        durable_raw=["experiments/p52-certified-data-raw.json"],
        decisions=decisions,
    )
    report = run_p58_acceptance_baseline_audit(cfg_p, tmp_path / "p58-out.json")
    assert report["verdict"] == "BLOCKED"
    assert any("approved_for_current_use" in f for f in report["findings"])


def test_p58_r1_accepts_restricted_base_with_valid_contract(tmp_path):
    repo = Path(__file__).resolve().parents[1]
    cfg_p = _p58_smoke_config(
        tmp_path,
        repo,
        approvals=[{"id": "p58-scope-review", "status": "approved"}],
        require_clean_tree=False,
        durable_raw=["experiments/p52-certified-data-raw.json"],
    )
    report = run_p58_acceptance_baseline_audit(cfg_p, tmp_path / "p58-out.json")
    assert report["verdict"] == "ACCEPTED"
    assert report["counters"]["decision_findings"] == 0
    assert report["counters"]["code_review_findings"] == 0
    assert len(report["decisions"]) == 6


def test_p58_durable_manifest_matches_files():
    import hashlib as _hashlib
    import json as _json

    repo = Path(__file__).resolve().parents[1]
    man = _json.loads((repo / "experiments" / "p58-durable-manifest.json").read_text())
    assert man["phase"] == "P58"
    assert man["n_entries"] == len(man["entries"]) == 25
    paths = {e["path"] for e in man["entries"]}
    assert {
        "experiments/p52-certified-data.json",
        "experiments/p53-proposer-manifest.json",
        "experiments/p56-final-tasks.json",
        "experiments/p57-certificates.json",
        "experiments/p52-certified-data-raw.json",
        "experiments/p53-proposer.pt",
        "experiments/p53-proposer-raw.json",
    } <= paths
    for entry in man["entries"]:
        blob = (repo / entry["path"]).read_bytes()
        assert entry["size"] == len(blob)
        assert entry["sha256"] == _hashlib.sha256(blob).hexdigest()
        assert entry["git_tracked"] is True
