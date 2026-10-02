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
    assert ACCEPTANCE_PHASES == ("P40", "P41", "P42", "P43", "P44")
    import subprocess as _sp

    proc = _sp.run(
        [
            sys.executable,
            "benchmarks/science_matrix.py",
            "--acceptance-phase",
            "P45",
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
    assert "Unknown acceptance phase 'P45'" in (proc.stdout + proc.stderr)


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


def test_p42_exact_audit_smoke(tmp_path):
    from benchmarks.science_matrix import run_p42_exact_audit

    out_p = tmp_path / "p42-acceptance.json"
    report = run_p42_exact_audit("experiments/p42-config.json", out_p)
    assert out_p.exists()
    assert report["phase"] == "P42"
    assert report["verdict"] in ("ACCEPTED", "MIXED")
    assert len(report["identities"]) == 4
    assert all(
        i["resolution"] in ("exact_accepted", "exact_rejected") for i in report["identities"]
    )
    assert all(c["rejected"] for c in report["controls"])
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
