"""Unit and integration tests for Lean 4 formal proof bridge (P77)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

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
