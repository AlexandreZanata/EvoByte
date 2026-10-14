"""Unit and integration tests for Lean 4 formal proof bridge (P77)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from evobyte.verifier import is_lean_available

needs_lean = pytest.mark.skipif(not is_lean_available(), reason="requires Lean 4 toolchain")

from evobyte.algebraic import Poly1D, get_algebraic_identity_for_residue
from evobyte.bytecode import encode_instr
from evobyte.formal_bridge import (
    algebraic_identity_to_lean_theorem,
    bytecode_to_lean_definition,
    bytecode_to_lean_theorem,
    compile_lean_file,
    erdos_straus_instance_to_lean_theorem,
    export_formal_proof_catalog,
    generate_lean_proof_module,
    poly1d_to_lean,
    verify_proof_catalog_soundness,
)


def test_poly1d_to_lean():
    p0 = Poly1D.constant(0)
    assert poly1d_to_lean(p0) == "(0 : ℚ)"

    p1 = Poly1D.linear(4, 1)  # 4k + 1
    lean_str = poly1d_to_lean(p1, "k")
    assert "k" in lean_str
    assert "4" in lean_str and "1" in lean_str

    p2 = Poly1D([5, 3, 2])  # 2k^2 + 3k + 5
    lean_str2 = poly1d_to_lean(p2, "k")
    assert "k ^ 2" in lean_str2


def test_algebraic_identity_to_lean_theorem():
    ident = get_algebraic_identity_for_residue(24, 5)
    assert ident is not None
    thm = algebraic_identity_to_lean_theorem(ident)
    assert "theorem erdos_straus_ident_m24_r5" in thm
    assert "ring" in thm
    assert "∀ k : ℚ," in thm


def test_erdos_straus_instance_to_lean_theorem():
    thm = erdos_straus_instance_to_lean_theorem(1009, 253, 85100, 944524900)
    assert "theorem erdos_straus_cert_n1009" in thm
    assert "(4 : ℚ) / 1009 = 1 / 253 + 1 / 85100 + 1 / 944524900" in thm
    assert "norm_num" in thm


def test_bytecode_to_lean_definition():
    # Program: r7 = r0 + 1 (CSEL r7, r0, b=1)
    words = [encode_instr(0x0F, dst=7, a=0, b=1)] + [0] * 15
    prog = np.array(words, dtype=np.uint32)

    lean_def, ret_reg = bytecode_to_lean_definition(prog, func_name="my_prog")
    assert "def my_prog (x : ℚ) : ℚ :=" in lean_def
    assert "let r7 := r0 + (1 : ℚ)" in lean_def
    assert ret_reg == "r7"


def test_bytecode_to_lean_theorem():
    # Program: r7 = r0 + 1
    words = [encode_instr(0x0F, dst=7, a=0, b=1)] + [0] * 15
    prog = np.array(words, dtype=np.uint32)

    thm = bytecode_to_lean_theorem(prog, "my_prog", "x + 1", "my_prog_spec")
    assert "theorem my_prog_spec : ∀ x : ℚ, my_prog x = x + 1 := by" in thm
    assert "dsimp [my_prog]" in thm
    assert "ring" in thm


def test_generate_lean_proof_module():
    thm = "theorem dummy : (1 : ℚ) + 1 = 2 := by norm_num\n"
    module_src = generate_lean_proof_module([thm], "Dummy module doc")
    assert "Dummy module doc" in module_src
    assert "import Mathlib.Tactic.NormNum" in module_src
    assert "theorem dummy" in module_src


@needs_lean
def test_compile_lean_file_valid(tmp_path: Path):
    proj = Path("lean_proofs").resolve()
    test_src = """import Mathlib.Tactic.Ring
import Mathlib.Data.Rat.Defs

theorem test_square : ∀ x : ℚ, (x + 1) * (x - 1) = x ^ 2 - 1 := by
  intro x
  ring
"""
    test_file = proj / "TestValidSquare.lean"
    test_file.write_text(test_src, encoding="utf-8")
    try:
        res = compile_lean_file(test_file, project_dir=proj)
        assert res["accepted"] is True
        assert res["reasons"] == []
    finally:
        test_file.unlink(missing_ok=True)


@needs_lean
def test_compile_lean_file_rejects_sorry(tmp_path: Path):
    proj = Path("lean_proofs").resolve()
    test_src = """import Mathlib.Data.Rat.Defs

theorem unproven_claim : ∀ x : ℚ, x = x + 1 := by
  intro x
  sorry
"""
    test_file = proj / "TestSorry.lean"
    test_file.write_text(test_src, encoding="utf-8")
    try:
        res = compile_lean_file(test_file, project_dir=proj)
        assert res["accepted"] is False
        assert any("sorry" in r for r in res["reasons"])
    finally:
        test_file.unlink(missing_ok=True)


@needs_lean
def test_compile_lean_file_rejects_unsound():
    proj = Path("lean_proofs").resolve()
    test_src = """import Mathlib.Tactic.NormNum
import Mathlib.Data.Rat.Defs

theorem false_equality : (4 : ℚ) / 5 = 1 / 2 := by
  norm_num
"""
    test_file = proj / "TestFalse.lean"
    test_file.write_text(test_src, encoding="utf-8")
    try:
        res = compile_lean_file(test_file, project_dir=proj)
        assert res["accepted"] is False
        assert any("compile_rejected" in r for r in res["reasons"])
    finally:
        test_file.unlink(missing_ok=True)


@needs_lean
def test_export_formal_proof_catalog_and_soundness():
    cat = export_formal_proof_catalog()
    assert cat["all_passed"] is True
    assert cat["has_sorry"] is False
    assert cat["total_theorems"] >= 35
    assert cat["counts"]["polynomial_identities"] >= 20
    assert cat["counts"]["diophantine_certificates"] >= 10
    assert cat["counts"]["bytecode_specifications"] >= 3

    sound, findings = verify_proof_catalog_soundness(cat)
    assert sound is True
    assert findings == []


@needs_lean
def test_p77_acceptance_smoke(tmp_path: Path):
    from benchmarks.science_matrix import run_p77_formal_audit

    cfg = {
        "phase": "P77",
        "seed": 42,
        "allow_dirty": True,
    }
    cfg_p = tmp_path / "p77-smoke-config.json"
    cfg_p.write_text(json.dumps(cfg))
    out_p = tmp_path / "p77-out.json"

    report = run_p77_formal_audit(cfg_p, out_p)
    assert out_p.exists()
    assert report["phase"] == "P77"
    assert report["verdict"] == "ACCEPTED"
    assert report["total_theorems"] >= 35
    assert report["has_sorry"] is False


def test_p77_acceptance_rejects_wrong_phase(tmp_path: Path):
    from benchmarks.science_matrix import run_p77_formal_audit

    cfg_p = tmp_path / "bad.json"
    cfg_p.write_text(json.dumps({"phase": "INVALID"}))
    with pytest.raises(ValueError, match="not a P77 configuration"):
        run_p77_formal_audit(cfg_p, tmp_path / "out.json")


@needs_lean
def test_p80_acceptance_smoke(tmp_path: Path):
    from benchmarks.science_matrix import run_p80_formal_campaign_audit

    cfg = {
        "phase": "P80",
        "budget_sec": 3600.0,
        "max_coord": 10**9,
        "seed": 42,
        "require_clean_tree": False,
        "allow_missing_dossier": True,
    }
    cfg_p = tmp_path / "p80-smoke-config.json"
    cfg_p.write_text(json.dumps(cfg))
    out_p = tmp_path / "p80-out.json"

    report = run_p80_formal_campaign_audit(cfg_p, out_p)
    assert out_p.exists()
    assert report["phase"] == "P80"
    assert report["verdict"] == "ACCEPTED"
    assert report["total_theorems"] >= 100
    assert report["has_sorry"] is False
    assert report["campaign_targets"]["erdos_straus_primes_solved"] == 10
    assert report["campaign_targets"]["sierpinski_primes_solved"] == 10


def test_p80_acceptance_rejects_wrong_phase(tmp_path: Path):
    from benchmarks.science_matrix import run_p80_formal_campaign_audit

    cfg_p = tmp_path / "bad.json"
    cfg_p.write_text(json.dumps({"phase": "INVALID"}))
    with pytest.raises(ValueError, match="not a P80 configuration"):
        run_p80_formal_campaign_audit(cfg_p, tmp_path / "out.json")


@needs_lean
def test_inductive_lemmas_catalog_generation():
    from evobyte.formal_bridge import (
        export_inductive_lemmas_catalog,
        verify_inductive_catalog_soundness,
    )

    cat = export_inductive_lemmas_catalog()
    assert cat["accepted"] is True
    assert cat["has_sorry"] is False
    assert cat["total_lemmas"] >= 20
    assert len(cat["sha256"]) == 64

    sound, findings = verify_inductive_catalog_soundness(cat)
    assert sound is True
    assert findings == []


@needs_lean
def test_p81_acceptance_smoke(tmp_path: Path):
    from benchmarks.science_matrix import run_p81_inductive_baseline_audit

    cfg = {
        "phase": "P81",
        "output_dir": "lean_proofs/Generated",
        "project_dir": "lean_proofs",
        "min_lemmas": 20,
        "seed": 42,
        "require_clean_tree": False,
    }
    cfg_p = tmp_path / "p81-smoke-config.json"
    cfg_p.write_text(json.dumps(cfg))
    out_p = tmp_path / "p81-out.json"

    report = run_p81_inductive_baseline_audit(cfg_p, out_p)
    assert out_p.exists()
    assert report["phase"] == "P81"
    assert report["verdict"] == "ACCEPTED"
    assert report["total_lemmas"] >= 20
    assert report["has_sorry"] is False
    assert report["file"] is not None


def test_p81_acceptance_rejects_wrong_phase(tmp_path: Path):
    from benchmarks.science_matrix import run_p81_inductive_baseline_audit

    cfg_p = tmp_path / "bad.json"
    cfg_p.write_text(json.dumps({"phase": "INVALID"}))
    with pytest.raises(ValueError, match="not a P81 configuration"):
        run_p81_inductive_baseline_audit(cfg_p, tmp_path / "out.json")


def test_divisibility_lemmas_catalog_generation():
    from evobyte.formal_bridge import (
        DIVISIBILITY_NAT_LEMMAS,
        generate_divisibility_lemmas_source,
    )

    assert len(DIVISIBILITY_NAT_LEMMAS) >= 15
    src = generate_divisibility_lemmas_source()
    assert "import Mathlib.Tactic.Ring" in src
    assert "theorem erdos_div_cross_m24_r0" in src
    assert "theorem erdos_div_z_m24_r0" in src
    assert "theorem sierpinski_div_cross_m24_r0" in src
    assert "theorem sierpinski_div_z_m24_r0" in src
    assert "sorry" not in src
    assert src.count("theorem ") >= 50


@needs_lean
def test_p82_acceptance_smoke(tmp_path: Path):
    from benchmarks.science_matrix import run_p82_divisibility_synthesis_audit

    cfg = {
        "phase": "P82",
        "output_dir": "lean_proofs/Generated",
        "project_dir": "lean_proofs",
        "min_lemmas": 50,
        "seed": 42,
        "require_clean_tree": False,
    }
    cfg_p = tmp_path / "p82-smoke-config.json"
    cfg_p.write_text(json.dumps(cfg))
    out_p = tmp_path / "p82-out.json"

    report = run_p82_divisibility_synthesis_audit(cfg_p, out_p)
    assert out_p.exists()
    assert report["phase"] == "P82"
    assert report["verdict"] == "ACCEPTED"
    assert report["total_lemmas"] >= 50
    assert report["has_sorry"] is False
    assert report["file"] is not None


def test_p82_acceptance_rejects_wrong_phase(tmp_path: Path):
    from benchmarks.science_matrix import run_p82_divisibility_synthesis_audit

    cfg_p = tmp_path / "bad.json"
    cfg_p.write_text(json.dumps({"phase": "INVALID"}))
    with pytest.raises(ValueError, match="not a P82 configuration"):
        run_p82_divisibility_synthesis_audit(cfg_p, tmp_path / "out.json")


@needs_lean
def test_try_prove_lemma_with_tactics():
    from evobyte.formal_bridge import try_prove_lemma_with_tactics

    # 1. Omega test
    res_omega = try_prove_lemma_with_tactics(
        "test_omega_sub", "∀ (n : Nat), n ≥ 2 → n + 1 ≥ 3", ["n", "hn"]
    )
    assert res_omega["success"] is True
    assert res_omega["winning_tactic"] == "omega"

    # 2. Linarith test
    res_lin = try_prove_lemma_with_tactics(
        "test_lin_sub", "∀ (x y : ℚ), x ≤ y → y ≤ x + 2 → 2 * x ≤ 2 * y", ["x", "y", "h1", "h2"]
    )
    assert res_lin["success"] is True
    assert res_lin["winning_tactic"] == "linarith"

    # 3. Aesop test
    res_aesop = try_prove_lemma_with_tactics("test_aesop_sub", "∀ (p q : Prop), p ∧ q → q ∧ p", [])
    assert res_aesop["success"] is True
    assert res_aesop["winning_tactic"] == "aesop"


@needs_lean
def test_benchmark_tactic_dispatch_suite():
    from evobyte.formal_bridge import benchmark_tactic_dispatch

    bench = benchmark_tactic_dispatch()
    assert bench["total_lemmas"] == 30
    assert bench["solved_count"] == 30
    assert bench["success_rate"] == 1.0
    dist = bench["tactic_distribution"]
    assert "omega" in dist
    assert "linarith" in dist
    assert "aesop" in dist


@needs_lean
def test_export_automated_theorems_catalog_soundness():
    from evobyte.formal_bridge import (
        export_automated_theorems_catalog,
        verify_automated_catalog_soundness,
    )

    cat = export_automated_theorems_catalog()
    assert cat["accepted"] is True
    assert cat["has_sorry"] is False
    assert cat["total_theorems"] == 30

    sound, findings = verify_automated_catalog_soundness(cat, min_theorems=30)
    assert sound is True
    assert findings == []


@needs_lean
def test_p85_acceptance_smoke(tmp_path: Path):
    from benchmarks.science_matrix import run_p85_tactic_dispatch_audit

    cfg = {
        "phase": "P85",
        "output_dir": "lean_proofs/Generated",
        "project_dir": "lean_proofs",
        "min_theorems": 30,
        "min_success_rate": 1.0,
        "seed": 42,
        "require_clean_tree": False,
    }
    cfg_p = tmp_path / "p85-smoke-config.json"
    cfg_p.write_text(json.dumps(cfg))
    out_p = tmp_path / "p85-out.json"

    report = run_p85_tactic_dispatch_audit(cfg_p, out_p)
    assert out_p.exists()
    assert report["phase"] == "P85"
    assert report["verdict"] == "ACCEPTED"
    assert report["total_theorems"] == 30
    assert report["success_rate"] == 1.0
    assert report["has_sorry"] is False
    assert report["file"] is not None


def test_p85_acceptance_rejects_wrong_phase(tmp_path: Path):
    from benchmarks.science_matrix import run_p85_tactic_dispatch_audit

    cfg_p = tmp_path / "bad.json"
    cfg_p.write_text(json.dumps({"phase": "INVALID"}))
    with pytest.raises(ValueError, match="not a P85 configuration"):
        run_p85_tactic_dispatch_audit(cfg_p, tmp_path / "out.json")


@needs_lean
def test_multiterm_theorems_catalog_export():
    from evobyte.formal_bridge import (
        export_multiterm_theorems_catalog,
        verify_multiterm_catalog_soundness,
    )

    catalog = export_multiterm_theorems_catalog()
    assert catalog["accepted"] is True
    assert catalog["total_theorems"] >= 24
    assert catalog["has_sorry"] is False
    assert len(catalog["sha256"]) == 64

    sound, findings = verify_multiterm_catalog_soundness(catalog, min_theorems=24)
    assert sound is True
    assert len(findings) == 0


def test_p89_tactic_diophantine_file_exists():
    tactic_p = Path("lean_proofs/Tactic/Diophantine.lean")
    assert tactic_p.exists()
    content = tactic_p.read_text(encoding="utf-8")
    assert 'syntax "evobyte_solve"' in content
    assert 'syntax "evobyte_diophantine"' in content
    assert "macro_rules" in content


def test_p89_acceptance_rejects_wrong_phase(tmp_path: Path):
    from benchmarks.science_matrix import run_p89_custom_tactic_audit

    cfg_p = tmp_path / "bad.json"
    cfg_p.write_text(json.dumps({"phase": "INVALID"}))
    with pytest.raises(ValueError, match="not a P89 configuration"):
        run_p89_custom_tactic_audit(cfg_p, tmp_path / "out.json")


@needs_lean
def test_p89_custom_tactic_catalog_export():
    from evobyte.formal_bridge import (
        export_custom_tactic_theorems_catalog,
        verify_custom_tactic_catalog_soundness,
    )

    catalog = export_custom_tactic_theorems_catalog()
    assert catalog["accepted"] is True
    assert catalog["total_theorems"] >= 30
    assert catalog["success_rate"] == 1.0
    assert catalog["has_sorry"] is False
    assert len(catalog["sha256"]) == 64

    sound, findings = verify_custom_tactic_catalog_soundness(catalog, min_theorems=30)
    assert sound is True
    assert len(findings) == 0


def test_p90_schinzel_identities_and_certificates_generation():
    from evobyte.algebraic import (
        generate_schinzel_instance_certificates,
        generate_schinzel_parametric_identities,
    )

    idents = generate_schinzel_parametric_identities([4, 5, 6, 7, 8], modulus=24, max_c=10)
    assert len(idents) >= 80
    for ident in idents:
        assert ident.a in [4, 5, 6, 7, 8]
        assert ident.verify_exact()

    certs = generate_schinzel_instance_certificates([4, 5, 6, 7, 8])
    assert len(certs) >= 40
    for cert in certs:
        assert cert["verified"] is True
        assert len(cert["sol"]) == 3


def test_p90_acceptance_rejects_wrong_phase(tmp_path: Path):
    from benchmarks.science_matrix import run_p90_schinzel_generalization_audit

    cfg_p = tmp_path / "bad.json"
    cfg_p.write_text(json.dumps({"phase": "INVALID"}))
    with pytest.raises(ValueError, match="not a P90 configuration"):
        run_p90_schinzel_generalization_audit(cfg_p, tmp_path / "out.json")


@needs_lean
def test_p90_schinzel_catalog_export():
    from evobyte.formal_bridge import (
        export_schinzel_theorems_catalog,
        verify_schinzel_catalog_soundness,
    )

    catalog = export_schinzel_theorems_catalog()
    assert catalog["accepted"] is True
    assert catalog["total_theorems"] >= 100
    assert catalog["has_sorry"] is False
    assert len(catalog["sha256"]) == 64

    sound, findings = verify_schinzel_catalog_soundness(catalog, min_theorems=100)
    assert sound is True
    assert len(findings) == 0


def test_p91_quadratic_norm_decomposition():
    from evobyte.algebraic import find_quadratic_norm_decomposition

    # delta = 29 = 7^2 - 5*2^2 = |49 - 20|
    norm29 = find_quadratic_norm_decomposition(29)
    assert norm29 is not None
    d, u, v = norm29
    assert abs(u * u - d * v * v) == 29

    # delta = 23 = 5^2 - 2*1^2 = 25 - 2
    norm23 = find_quadratic_norm_decomposition(23)
    assert norm23 is not None
    d, u, v = norm23
    assert abs(u * u - d * v * v) == 23


def test_p91_quadratic_ring_sieve_coverage():
    from evobyte.algebraic import evaluate_quadratic_ring_sieve_coverage

    cov = evaluate_quadratic_ring_sieve_coverage(modulus=840, k_count=3)
    assert cov["total_tested"] >= 15
    assert cov["success_rate"] == 1.0
    assert cov["norm_rate"] == 1.0
    assert cov["all_certified"] is True


def test_p91_acceptance_rejects_wrong_phase(tmp_path: Path):
    from benchmarks.science_matrix import run_p91_quadratic_ring_audit

    cfg_p = tmp_path / "bad.json"
    cfg_p.write_text(json.dumps({"phase": "INVALID"}))
    with pytest.raises(ValueError, match="not a P91 configuration"):
        run_p91_quadratic_ring_audit(cfg_p, tmp_path / "out.json")


@needs_lean
def test_p91_quadratic_ring_catalog_export():
    from evobyte.formal_bridge import (
        export_quadratic_ring_theorems_catalog,
        verify_quadratic_ring_catalog_soundness,
    )

    catalog = export_quadratic_ring_theorems_catalog(modulus=840, k_count=5)
    assert catalog["accepted"] is True
    assert catalog["total_theorems"] >= 50
    assert catalog["has_sorry"] is False
    assert len(catalog["sha256"]) == 64

    sound, findings = verify_quadratic_ring_catalog_soundness(catalog, min_theorems=50)
    assert sound is True
    assert len(findings) == 0


def test_p92_extremal_coordinate_bounds_metrics():
    from evobyte.algebraic import compute_coordinate_bounds

    # 4/73 = 1/20 + 1/292 + 1/730
    metrics = compute_coordinate_bounds(73, (20, 292, 730), a=4)
    assert metrics["max_coord"] == 730
    assert metrics["is_subcubic"] is True
    assert metrics["is_exact"] is True
    assert metrics["quadratic_ratio"] < 1.0


def test_p92_extremal_coordinate_bounds_coverage():
    from evobyte.algebraic import evaluate_extremal_coordinate_bounds_coverage

    cov = evaluate_extremal_coordinate_bounds_coverage(instances=[73, 97, 193], a_values=[4, 5])
    assert cov["total_tested"] == 6
    assert cov["coverage"] == 1.0
    assert cov["subcubic_rate"] == 1.0
    assert cov["quadratic_rate"] == 1.0
    assert cov["all_subcubic"] is True
    assert cov["all_quadratic_bounded"] is True


def test_p92_acceptance_rejects_wrong_phase(tmp_path: Path):
    from benchmarks.science_matrix import run_p92_extremal_bounds_audit

    cfg_p = tmp_path / "bad.json"
    cfg_p.write_text(json.dumps({"phase": "INVALID"}))
    with pytest.raises(ValueError, match="not a P92 configuration"):
        run_p92_extremal_bounds_audit(cfg_p, tmp_path / "out.json")


@needs_lean
def test_p92_extremal_bounds_catalog_export():
    from evobyte.formal_bridge import (
        export_extremal_bounds_theorems_catalog,
        verify_extremal_bounds_catalog_soundness,
    )

    catalog = export_extremal_bounds_theorems_catalog()
    assert catalog["accepted"] is True
    assert catalog["total_theorems"] >= 60
    assert catalog["has_sorry"] is False
    assert len(catalog["sha256"]) == 64

    sound, findings = verify_extremal_bounds_catalog_soundness(catalog, min_theorems=60)
    assert sound is True
    assert len(findings) == 0


def test_p93_modular_asymptotic_density():
    from evobyte.algebraic import compute_modular_asymptotic_density

    # M=24: 1 resistant residue (1), density 23/24
    d24 = compute_modular_asymptotic_density(24)
    assert d24["resistant_count"] == 1
    assert d24["density_str"] == "23/24"
    assert d24["is_high_density"] is True

    # M=840: 6 resistant residues, density 139/140
    d840 = compute_modular_asymptotic_density(840)
    assert d840["resistant_count"] == 6
    assert d840["density_str"] == "139/140"
    assert d840["density"] > 0.99


def test_p93_asymptotic_density_convergence():
    from evobyte.algebraic import evaluate_asymptotic_density_convergence

    conv = evaluate_asymptotic_density_convergence([24, 120, 840, 27720, 720720])
    assert conv["is_monotone"] is True
    assert conv["converges_to_one"] is True
    assert conv["terminal_density"] > 0.998


def test_p93_empirical_sample_verification():
    from evobyte.algebraic import empirical_density_sample_verification

    emp = empirical_density_sample_verification(modulus=840, sample_size=5000, seed=42)
    assert emp["consistent_within_error"] is True
    assert abs(emp["empirical_density"] - emp["theoretical_density"]) < 0.01


def test_p93_acceptance_rejects_wrong_phase(tmp_path: Path):
    from benchmarks.science_matrix import run_p93_asymptotic_density_audit

    cfg_p = tmp_path / "bad.json"
    cfg_p.write_text(json.dumps({"phase": "INVALID"}))
    with pytest.raises(ValueError, match="not a P93 configuration"):
        run_p93_asymptotic_density_audit(cfg_p, tmp_path / "out.json")


@needs_lean
def test_p93_asymptotic_density_catalog_export():
    from evobyte.formal_bridge import (
        export_asymptotic_density_theorems_catalog,
        verify_asymptotic_density_catalog_soundness,
    )

    catalog = export_asymptotic_density_theorems_catalog()
    assert catalog["accepted"] is True
    assert catalog["total_theorems"] >= 40
    assert catalog["has_sorry"] is False
    assert len(catalog["sha256"]) == 64

    sound, findings = verify_asymptotic_density_catalog_soundness(catalog, min_theorems=40)
    assert sound is True
    assert len(findings) == 0


def test_p94_pairwise_coprime_decomposition():
    from evobyte.algebraic import verify_pairwise_coprime_decomposition

    # 1/2 + 1/3 + 1/5 + 1/7 + 1/11 = 2927/2310
    v5, det5 = verify_pairwise_coprime_decomposition((2, 3, 5, 7, 11))
    assert v5 is True
    assert det5["is_pairwise_coprime"] is True
    assert det5["is_increasing"] is True
    assert det5["is_reduced"] is True
    assert det5["numerator"] == 2927
    assert det5["denominator"] == 2310

    # Non-coprime tuple should be rejected
    v_bad, det_bad = verify_pairwise_coprime_decomposition((2, 4, 5, 7, 11))
    assert v_bad is False
    assert det_bad["is_pairwise_coprime"] is False

    # Non-increasing tuple should be rejected
    v_inc, det_inc = verify_pairwise_coprime_decomposition((3, 2, 5, 7, 11))
    assert v_inc is False
    assert det_inc["is_increasing"] is False


def test_p94_universal_multiterm_coverage():
    from evobyte.algebraic import (
        evaluate_universal_multiterm_coprimality_coverage,
        generate_pairwise_coprime_multiterm_decompositions,
    )

    decomps = generate_pairwise_coprime_multiterm_decompositions()
    assert len(decomps) == 34
    assert all(d["is_pairwise_coprime"] for d in decomps)
    assert all(d["is_increasing"] for d in decomps)
    assert all(d["is_reduced"] for d in decomps)

    cov = evaluate_universal_multiterm_coprimality_coverage()
    assert cov["all_certified"] is True
    assert cov["total_decompositions"] >= 30
    assert cov["min_k"] == 5
    assert cov["max_k"] == 8
    assert set(cov["k_counts"].keys()) == {5, 6, 7, 8}


def test_p94_acceptance_rejects_wrong_phase(tmp_path: Path):
    from benchmarks.science_matrix import run_p94_multiterm_coprimality_audit

    cfg_p = tmp_path / "bad.json"
    cfg_p.write_text(json.dumps({"phase": "INVALID"}))
    with pytest.raises(ValueError, match="not a P94 configuration"):
        run_p94_multiterm_coprimality_audit(cfg_p, tmp_path / "out.json")


@needs_lean
def test_p94_universal_multiterm_catalog_export():
    from evobyte.formal_bridge import (
        export_universal_multiterm_theorems_catalog,
        verify_universal_multiterm_catalog_soundness,
    )

    catalog = export_universal_multiterm_theorems_catalog()
    assert catalog["accepted"] is True
    assert catalog["total_theorems"] >= 100
    assert catalog["fraction_equality_count"] >= 30
    assert catalog["coprimality_conjunction_count"] >= 30
    assert catalog["ordering_count"] >= 30
    assert catalog["has_sorry"] is False
    assert len(catalog["sha256"]) == 64

    sound, findings = verify_universal_multiterm_catalog_soundness(catalog, min_theorems=100)
    assert sound is True
    assert len(findings) == 0


def test_p96_audit_grand_formal_library():
    from evobyte.formal_bridge import (
        audit_grand_formal_library,
        verify_grand_formal_campaign_soundness,
    )

    res = audit_grand_formal_library(verify_lake=False)
    assert res["total_modules"] == 16
    assert res["total_theorems"] >= 500
    assert res["total_theorems"] == 965
    assert res["has_sorry"] is False
    assert len(res["missing_modules"]) == 0
    assert len(res["hash_chain"]) == 16
    assert (
        res["final_chain_hash"]
        == "5de47dc7b3987ef724e685d2bac5a944ee1cd4ade4a8178f2d74ae0c9471878c"
    )

    # Verify soundness check
    # Lake flag set to true for soundness verification test
    res_copy = dict(res, lake_passed=True)
    sound, findings = verify_grand_formal_campaign_soundness(res_copy, min_theorems=500)
    assert sound is True
    assert len(findings) == 0


def test_p96_dossier_integrity():
    dossier_p = Path("docs/research/p96-grand-formal-dossier.md")
    assert dossier_p.exists()
    content = dossier_p.read_text(encoding="utf-8")
    assert "965" in content
    assert "16" in content
    assert "5de47dc7b3987ef724e685d2bac5a944ee1cd4ade4a8178f2d74ae0c9471878c" in content
    assert "P96" in content


def test_p96_acceptance_rejects_wrong_phase(tmp_path: Path):
    from benchmarks.science_matrix import run_p96_grand_campaign_audit

    cfg_p = tmp_path / "bad.json"
    cfg_p.write_text(json.dumps({"phase": "INVALID"}))
    with pytest.raises(ValueError, match="not a P96 configuration"):
        run_p96_grand_campaign_audit(cfg_p, tmp_path / "out.json")


@needs_lean
def test_p96_grand_campaign_audit_smoke(tmp_path: Path):
    from benchmarks.science_matrix import run_p96_grand_campaign_audit

    cfg = {
        "phase": "P96",
        "min_theorems": 500,
        "budget_sec": 3600.0,
        "project_dir": "lean_proofs",
        "dossier_path": "docs/research/p96-grand-formal-dossier.md",
        "allow_dirty": True,
        "require_clean_tree": False,
        "seed": 42,
    }
    cfg_p = tmp_path / "p96-smoke-config.json"
    cfg_p.write_text(json.dumps(cfg))
    out_p = tmp_path / "p96-out.json"

    report = run_p96_grand_campaign_audit(cfg_p, out_p)
    assert out_p.exists()
    assert report["phase"] == "P96"
    assert report["verdict"] == "ACCEPTED"
    assert report["total_modules"] == 16
    assert report["total_formal_theorems"] >= 500
    assert report["has_sorry"] is False
    assert (
        report["final_chain_hash"]
        == "5de47dc7b3987ef724e685d2bac5a944ee1cd4ade4a8178f2d74ae0c9471878c"
    )
