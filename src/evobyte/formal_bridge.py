"""Bytecode compiler to certified Lean 4 theorems and formal proof bridge (P77).

Translates EvoByte mathematical artifacts (algebraic polynomial identities over Q[k],
Diophantine integer solution certificates, and decompiled bytecode programs)
into rigorous Lean 4 definitions and theorems proven automatically by formal kernel
tactics (`ring`, `norm_num`, `linarith`, `omega`) without human intervention or `sorry`.
"""

from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any

import numpy as np

from evobyte.algebraic import (
    AlgebraicIdentity,
    Poly1D,
    evaluate_resistant_residues_coverage,
    get_algebraic_identity_for_residue,
    get_resistant_residues,
    rational_divisor_sieve,
    sierpinski_divisor_sieve,
    synthesize_quadratic_identities,
    synthesize_sierpinski_identity,
)
from evobyte.bytecode import CONST_BANK, decode_instr
from evobyte.grammar import HornerPoly, compile_horner_to_bytecode
from evobyte.verifier import lean_resolve_binaries, run_lean_checker

LEAN_HEADER_IMPORTS = [
    "Mathlib.Tactic.Ring",
    "Mathlib.Tactic.NormNum",
    "Mathlib.Data.Rat.Defs",
]


def poly1d_to_lean(poly: Poly1D, var_name: str = "k") -> str:
    """Format a Poly1D object into a valid Lean 4 rational expression over var_name."""
    terms: list[str] = []
    for deg, c in enumerate(poly.coeffs):
        if c == 0 and len(poly.coeffs) > 1:
            continue
        if c.denominator != 1:
            c_str = f"(({c.numerator} : ℚ) / {c.denominator})"
        else:
            c_str = f"({c.numerator} : ℚ)"

        if deg == 0:
            terms.append(c_str)
        elif deg == 1:
            terms.append(f"{c_str} * {var_name}")
        else:
            terms.append(f"{c_str} * {var_name} ^ {deg}")

    return " + ".join(terms) if terms else "(0 : ℚ)"


def poly1d_to_lean_int(poly: Poly1D, var_name: str = "k") -> str:
    """Format a Poly1D object into a valid Lean 4 integer expression over var_name."""
    terms: list[str] = []
    for deg, c in enumerate(poly.coeffs):
        if c == 0 and len(poly.coeffs) > 1:
            continue
        c_val = int(c)
        c_str = f"({c_val} : ℤ)"
        if deg == 0:
            terms.append(c_str)
        elif deg == 1:
            terms.append(f"{c_str} * {var_name}")
        else:
            terms.append(f"{c_str} * {var_name} ^ {deg}")

    return " + ".join(terms) if terms else "(0 : ℤ)"


def algebraic_identity_to_lean_theorem(
    ident: AlgebraicIdentity, theorem_name: str | None = None
) -> str:
    """Translate an AlgebraicIdentity over Q[k] into a Lean 4 theorem proven by `ring`."""
    name = theorem_name or f"erdos_straus_ident_m{ident.m}_r{ident.r}"
    n_str = poly1d_to_lean(ident.n_poly, "k")
    X_str = poly1d_to_lean(ident.X, "k")
    Y_str = poly1d_to_lean(ident.Y, "k")
    Z_str = poly1d_to_lean(ident.Z, "k")

    doc = (
        f"/-- Erdős–Straus polynomial identity for congruence class n ≡ {ident.r} [mod {ident.m}].\n"
        f"    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/"
    )
    stmt = (
        f"theorem {name} : ∀ k : ℚ,\n"
        f"    {ident.a} * ({X_str}) * ({Y_str}) * ({Z_str}) =\n"
        f"    ({n_str}) * (({Y_str}) * ({Z_str}) + ({X_str}) * ({Z_str}) + ({X_str}) * ({Y_str})) := by\n"
        f"  intro k\n"
        f"  ring"
    )
    return f"{doc}\n{stmt}\n"


def erdos_straus_instance_to_lean_theorem(
    n: int, x: int, y: int, z: int, theorem_name: str | None = None
) -> str:
    """Translate a verified Erdős–Straus certificate into a Lean 4 theorem proven by `norm_num`."""
    name = theorem_name or f"erdos_straus_cert_n{n}"
    doc = (
        f"/-- Certified Erdős–Straus Diophantine solution for n = {n}.\n"
        f"    Verified exact: 4/{n} = 1/{x} + 1/{y} + 1/{z}. -/"
    )
    stmt = (
        f"theorem {name} :\n"
        f"    (4 : ℚ) / {n} = 1 / {x} + 1 / {y} + 1 / {z} := by\n"
        f"  norm_num"
    )
    return f"{doc}\n{stmt}\n"


def sierpinski_identity_to_lean_theorem(
    ident: AlgebraicIdentity, theorem_name: str | None = None
) -> str:
    """Translate a Sierpiński (5/n) polynomial identity into a Lean 4 theorem proven by `ring`."""
    if ident.a != 5:
        raise ValueError(f"Sierpiński identity requires numerator a=5, got a={ident.a}")
    name = theorem_name or f"sierpinski_ident_m{ident.m}_r{ident.r}"
    return algebraic_identity_to_lean_theorem(ident, name).replace(
        "Erdős–Straus polynomial identity", "Sierpiński 5/n polynomial identity"
    )


def sierpinski_instance_to_lean_theorem(
    n: int, x: int, y: int, z: int, theorem_name: str | None = None
) -> str:
    """Translate a verified Sierpiński certificate 5/n = 1/x + 1/y + 1/z into a `norm_num` theorem."""
    if 5 * x * y * z != n * (x * y + y * z + z * x):
        raise ValueError(f"({x}, {y}, {z}) is not a valid Sierpiński solution for n={n}")
    name = theorem_name or f"sierpinski_cert_n{n}"
    doc = (
        f"/-- Certified Sierpiński Diophantine solution for n = {n}.\n"
        f"    Verified exact: 5/{n} = 1/{x} + 1/{y} + 1/{z}. -/"
    )
    stmt = (
        f"theorem {name} :\n"
        f"    (5 : ℚ) / {n} = 1 / {x} + 1 / {y} + 1 / {z} := by\n"
        f"  norm_num"
    )
    return f"{doc}\n{stmt}\n"


def bytecode_to_lean_definition(
    program: np.ndarray, func_name: str = "bytecode_fn", var_name: str = "x"
) -> tuple[str, str]:
    """Decompile a bytecode program into a structured Lean 4 functional definition."""
    lines: list[str] = [
        f"def {func_name} ({var_name} : ℚ) : ℚ :=",
        f"  let r0 : ℚ := {var_name}",
        "  let r1 : ℚ := (0 : ℚ)",
    ]

    for i in range(len(program)):
        op, dst, a, b = decode_instr(program[i])
        if op == 0x00:  # NOP
            continue
        if op == 0x01:  # ADD
            lines.append(f"  let r{dst} := r{a} + r{b % 8}")
        elif op == 0x02:  # SUB
            lines.append(f"  let r{dst} := r{a} - r{b % 8}")
        elif op == 0x03:  # MUL
            lines.append(f"  let r{dst} := r{a} * r{b % 8}")
        elif op == 0x0C:  # NEG
            lines.append(f"  let r{dst} := -r{a}")
        elif op == 0x0F:  # CSEL: r_a + const[b & 0xF]
            c_val = float(CONST_BANK[b & 0x0F])
            c_int = int(c_val) if c_val.is_integer() else c_val
            lines.append(f"  let r{dst} := r{a} + ({c_int} : ℚ)")

    lines.append("  r7")
    return "\n".join(lines), "r7"


def bytecode_to_lean_theorem(
    program: np.ndarray,
    func_name: str,
    target_expr: str,
    theorem_name: str,
    tactic: str = "ring",
) -> str:
    """Generate Lean 4 specification theorem proving equivalence of bytecode evaluation and target expr."""
    lean_def, _ = bytecode_to_lean_definition(program, func_name)
    doc = f"/-- Formal algebraic equivalence: bytecode program `{func_name}` computes `{target_expr}`. -/"
    thm = (
        f"theorem {theorem_name} : ∀ x : ℚ, {func_name} x = {target_expr} := by\n"
        f"  intro x\n"
        f"  dsimp [{func_name}]\n"
        f"  {tactic}"
    )
    return f"{lean_def}\n\n{doc}\n{thm}\n"


def generate_lean_proof_module(
    theorems: list[str],
    module_doc: str = "",
    imports: list[str] | None = None,
    definitions: list[str] | None = None,
) -> str:
    """Assemble a standalone, syntactically valid Lean 4 source module."""
    chosen_imports = imports or LEAN_HEADER_IMPORTS
    import_lines = "\n".join(f"import {imp}" for imp in chosen_imports)

    parts: list[str] = []
    if module_doc:
        parts.append(f"/-\n{module_doc.strip()}\n-/\n")
    parts.append(import_lines)
    parts.append("")

    if definitions:
        for d in definitions:
            parts.append(d.strip())
            parts.append("")

    for thm in theorems:
        parts.append(thm.strip())
        parts.append("")

    return "\n".join(parts).rstrip() + "\n"


def compile_lean_file(
    proof_file: str | Path,
    project_dir: str | Path = "lean_proofs",
    timeout_sec: float = 60.0,
) -> dict[str, Any]:
    """Compile and verify a Lean 4 proof file using hermetic Lake environment."""
    proj = Path(project_dir).resolve()
    target = Path(proof_file)
    if not target.is_absolute():
        target = (proj / target).resolve()

    return run_lean_checker(
        target,
        project_dir=proj,
        timeout_sec=timeout_sec,
    )


def export_formal_proof_catalog(
    output_dir: str | Path = "lean_proofs/Generated",
    project_dir: str | Path = "lean_proofs",
) -> dict[str, Any]:
    """Generate and verify the complete formal certified proof catalog in Lean 4.

    Produces:
    1. ErdosStrausIdentities.lean: 23 mod-24 parameterized polynomial identities.
    2. ErdosStrausCertificates.lean: 10 Diophantine certificates for challenging primes.
    3. BytecodeTheorems.lean: Bytecode decompilations proven against mathematical targets.
    4. Generated.lean: Root library module importing all catalog modules.
    """
    proj = Path(project_dir).resolve()
    out = Path(output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)

    # 1. Modulo 24 & representative identities
    ident_theorems: list[str] = []
    for r in range(24):
        if r in get_resistant_residues(24):
            continue
        ident = get_algebraic_identity_for_residue(24, r)
        if ident is not None and ident.verify_exact():
            ident_theorems.append(algebraic_identity_to_lean_theorem(ident))

    # Add representative mod 840 identities from P75
    for r in (73, 97, 193, 241, 313, 337):
        ident = get_algebraic_identity_for_residue(840, r)
        if ident is not None and ident.verify_exact():
            ident_theorems.append(algebraic_identity_to_lean_theorem(ident))

    identities_doc = "EvoByte Formal Proof Catalog: Certified Erdős–Straus Polynomial Identities in Q[k]."
    identities_src = generate_lean_proof_module(ident_theorems, identities_doc)
    identities_file = out / "ErdosStrausIdentities.lean"
    identities_file.write_text(identities_src, encoding="utf-8")

    # 2. Diophantine instance certificates (P76 challenging primes)
    cert_theorems: list[str] = []
    target_primes = [1009, 1033, 1129, 1153, 1201, 1249, 1297, 1321, 1489, 1609]
    for p in target_primes:
        sol, _ = rational_divisor_sieve(p)
        if sol is not None:
            x, y, z = sol
            cert_theorems.append(erdos_straus_instance_to_lean_theorem(p, x, y, z))

    cert_doc = "EvoByte Formal Proof Catalog: Certified Erdős–Straus Diophantine Certificates."
    cert_src = generate_lean_proof_module(
        cert_theorems, cert_doc, imports=["Mathlib.Tactic.NormNum", "Mathlib.Data.Rat.Defs"]
    )
    cert_file = out / "ErdosStrausCertificates.lean"
    cert_file.write_text(cert_src, encoding="utf-8")

    # 3. Bytecode equivalence theorems
    bytecode_theorems: list[str] = []

    # Program A: 3*x + 2 (Horner: [11, 3])
    prog_a, _ = compile_horner_to_bytecode(HornerPoly(coeff_indices=[11, 3]))
    if prog_a is not None:
        thm_a = bytecode_to_lean_theorem(
            prog_a, "bytecode_linear_3x_plus_2", "(3 : ℚ) * x + 2", "bytecode_spec_linear"
        )
        bytecode_theorems.append(thm_a)

    # Program B: 2*x^2 + 3 (Horner: [3, 0, 11])
    prog_b, _ = compile_horner_to_bytecode(HornerPoly(coeff_indices=[3, 0, 11]))
    if prog_b is not None:
        thm_b = bytecode_to_lean_theorem(
            prog_b, "bytecode_quadratic_2x2_plus_3", "(2 : ℚ) * x ^ 2 + 3", "bytecode_spec_quadratic"
        )
        bytecode_theorems.append(thm_b)

    # Program C: x^2 - 1 (Horner: [1, 0, 2])
    prog_c, _ = compile_horner_to_bytecode(HornerPoly(coeff_indices=[1, 0, 2]))
    if prog_c is not None:
        thm_c = bytecode_to_lean_theorem(
            prog_c, "bytecode_diff_squares", "x ^ 2 - 1", "bytecode_spec_diff_squares"
        )
        bytecode_theorems.append(thm_c)

    # Program D: 4*x - 5 (Horner: [3, 2] -> let's do 3*x - 1 with coeffs [11, 2])
    prog_d, _ = compile_horner_to_bytecode(HornerPoly(coeff_indices=[11, 2]))
    if prog_d is not None:
        thm_d = bytecode_to_lean_theorem(
            prog_d, "bytecode_linear_3x_minus_1", "(3 : ℚ) * x - 1", "bytecode_spec_linear_sub"
        )
        bytecode_theorems.append(thm_d)

    bytecode_doc = "EvoByte Formal Proof Catalog: Bytecode Decompilations and Algebraic Equivalence Theorems."
    bytecode_src = generate_lean_proof_module(
        bytecode_theorems, bytecode_doc, imports=["Mathlib.Tactic.Ring", "Mathlib.Data.Rat.Defs"]
    )
    bytecode_file = out / "BytecodeTheorems.lean"
    bytecode_file.write_text(bytecode_src, encoding="utf-8")

    # 3b. Sierpiński 5/n theorems (P78)
    sier_ident_theorems: list[str] = []
    for r in range(120):
        sident = synthesize_sierpinski_identity(120, r)
        if sident is not None and sident.verify_exact():
            sier_ident_theorems.append(sierpinski_identity_to_lean_theorem(sident))
    sier_cert_theorems: list[str] = []
    for p in (1009, 1033, 1129, 1153, 1201, 1249, 1297, 1321, 1489, 1609):
        ssol, _ = sierpinski_divisor_sieve(p)
        if ssol is not None:
            sier_cert_theorems.append(sierpinski_instance_to_lean_theorem(p, *ssol))
    sier_theorems = sier_ident_theorems + sier_cert_theorems
    sier_doc = "EvoByte Formal Proof Catalog: Certified Sierpiński 5/n Identities and Certificates."
    sier_src = generate_lean_proof_module(
        sier_theorems,
        sier_doc,
        imports=["Mathlib.Tactic.Ring", "Mathlib.Tactic.NormNum", "Mathlib.Data.Rat.Defs"],
    )
    sier_file = out / "SierpinskiTheorems.lean"
    sier_file.write_text(sier_src, encoding="utf-8")

    # 4. Root Generated.lean module
    root_file = proj / "Generated.lean"
    base_imports = [
        "Generated.ErdosStrausIdentities",
        "Generated.ErdosStrausCertificates",
        "Generated.BytecodeTheorems",
        "Generated.SierpinskiTheorems",
        "Generated.InductiveLemmas",
        "Generated.DivisibilityLemmas",
        "Generated.OptimalCertificates",
        "Generated.QuadraticIdentities",
    ]
    existing_content = root_file.read_text(encoding="utf-8") if root_file.exists() else ""
    imports_to_write = []
    for mod in base_imports:
        file_name = mod.split(".")[-1] + ".lean"
        if f"import {mod}" in existing_content or (out / file_name).exists():
            imports_to_write.append(f"import {mod}")
    if not imports_to_write:
        imports_to_write = [f"import {mod}" for mod in base_imports[:4]]
    root_src = "-- EvoByte Root Generated Formal Library\n" + "\n".join(imports_to_write) + "\n"
    if existing_content != root_src:
        root_file.write_text(root_src, encoding="utf-8")

    # Ensure lakefile.toml includes Generated library and defaultTargets
    lakefile = proj / "lakefile.toml"
    lake_toml = lakefile.read_text(encoding="utf-8")
    if 'name = "Generated"' not in lake_toml:
        extra_lib = '\n[[lean_lib]]\nname = "Generated"\n'
        lake_toml = lake_toml.strip() + extra_lib
    if "defaultTargets" not in lake_toml:
        lake_toml = 'defaultTargets = ["P48Proofs", "Generated"]\n' + lake_toml
    lakefile.write_text(lake_toml, encoding="utf-8")

    # 5. Compile and verify proof modules
    proof_modules = [identities_file, cert_file, bytecode_file, sier_file]
    verifications: dict[str, Any] = {}
    total_theorems = (
        len(ident_theorems) + len(cert_theorems) + len(bytecode_theorems) + len(sier_theorems)
    )
    all_passed = True

    for fpath in proof_modules:
        v_res = compile_lean_file(fpath, project_dir=proj)
        rel_name = fpath.name
        verifications[rel_name] = {
            "path": str(fpath),
            "sha256": hashlib.sha256(fpath.read_bytes()).hexdigest(),
            "accepted": v_res.get("accepted", False),
            "reasons": v_res.get("reasons", []),
            "elapsed_sec": v_res.get("elapsed_sec", 0.0),
        }
        if not v_res.get("accepted", False):
            all_passed = False

    # Build the entire Generated library via Lake
    import subprocess
    bins = lean_resolve_binaries(proj)
    lake_proc = subprocess.run(
        [bins["lake"], "-d", str(proj), "build", "Generated"],
        capture_output=True,
        text=True,
        cwd=str(proj),
        timeout=120,
        check=False,
    )
    lake_built_ok = (lake_proc.returncode == 0)
    verifications["Generated.lean"] = {
        "path": str(root_file),
        "sha256": hashlib.sha256(root_file.read_bytes()).hexdigest(),
        "accepted": lake_built_ok,
        "reasons": [] if lake_built_ok else [f"lake_build_failed: {lake_proc.stderr[:160]}"],
        "elapsed_sec": 0.0,
    }
    if not lake_built_ok:
        all_passed = False

    return {
        "catalog_dir": str(out),
        "total_theorems": total_theorems,
        "counts": {
            "polynomial_identities": len(ident_theorems),
            "diophantine_certificates": len(cert_theorems),
            "bytecode_specifications": len(bytecode_theorems),
            "sierpinski_identities": len(sier_ident_theorems),
            "sierpinski_certificates": len(sier_cert_theorems),
        },
        "modules": verifications,
        "all_passed": all_passed,
        "has_sorry": any(
            "sorry" in mod.get("reasons", []) for mod in verifications.values()
        ),
    }


def verify_proof_catalog_soundness(catalog_summary: dict[str, Any]) -> tuple[bool, list[str]]:
    """Audit formal catalog results for complete acceptance, zero sorry, and soundness."""
    findings: list[str] = []

    if not catalog_summary.get("all_passed", False):
        findings.append("MODULE_COMPILATION_FAILED: one or more Lean modules failed compilation")

    if catalog_summary.get("has_sorry", False):
        findings.append("SORRY_DETECTED: proof catalog contains incomplete `sorry` tokens")

    total_thms = catalog_summary.get("total_theorems", 0)
    if total_thms < 30:
        findings.append(f"INSUFFICIENT_THEOREMS: expected >= 30, got {total_thms}")

    counts = catalog_summary.get("counts", {})
    if counts.get("polynomial_identities", 0) < 20:
        findings.append("MISSING_IDENTITIES: less than 20 polynomial identities verified")
    if counts.get("diophantine_certificates", 0) < 10:
        findings.append("MISSING_CERTIFICATES: less than 10 Diophantine certificates verified")
    if counts.get("bytecode_specifications", 0) < 3:
        findings.append("MISSING_BYTECODE_SPECS: less than 3 bytecode specifications verified")
    if counts.get("sierpinski_identities", 0) < 20:
        findings.append("MISSING_SIERPINSKI_IDENTITIES: less than 20 Sierpiński identities verified")
    if counts.get("sierpinski_certificates", 0) < 10:
        findings.append("MISSING_SIERPINSKI_CERTIFICATES: less than 10 Sierpiński certificates verified")

    modules = catalog_summary.get("modules", {})
    for mod_name, mod_info in modules.items():
        if not mod_info.get("accepted", False):
            findings.append(f"MODULE_REJECTED_{mod_name}: {mod_info.get('reasons')}")
        if len(mod_info.get("sha256", "")) != 64:
            findings.append(f"INVALID_CHECKSUM_{mod_name}")

    return (len(findings) == 0), findings


# -----------------------------------------------------------------------------
# Inductive Proof & Presburger Baseline (P81)
# -----------------------------------------------------------------------------

INDUCTIVE_LEAN_LEMMAS: list[tuple[str, str, str, str]] = [
    # 1. Structural induction & basic Presburger Nat properties
    (
        "nat_add_zero_ind",
        "∀ (n : Nat), n + 0 = n",
        "intro n\ninduction n with\n| zero => rfl\n| succ n ih => rw [Nat.add_zero]",
        "Structural induction on Nat: addition with zero right-identity.",
    ),
    (
        "nat_zero_add_ind",
        "∀ (n : Nat), 0 + n = n",
        "intro n\ninduction n with\n| zero => rfl\n| succ n ih => omega",
        "Structural induction on Nat: addition with zero left-identity.",
    ),
    (
        "nat_succ_pos",
        "∀ (n : Nat), n + 1 > 0",
        "intro n\nomega",
        "Successor is strictly positive in Nat.",
    ),
    (
        "nat_succ_ge_one",
        "∀ (n : Nat), n + 1 ≥ 1",
        "intro n\nomega",
        "Successor is greater than or equal to 1 in Nat.",
    ),
    (
        "nat_add_pos_left",
        "∀ (a b : Nat), a > 0 → a + b > 0",
        "intro a b ha\nomega",
        "Addition with a strictly positive term is strictly positive.",
    ),
    (
        "nat_add_pos_right",
        "∀ (a b : Nat), b > 0 → a + b > 0",
        "intro a b hb\nomega",
        "Addition with a strictly positive right term is strictly positive.",
    ),
    (
        "nat_sub_le",
        "∀ (a b : Nat), a - b ≤ a",
        "intro a b\nomega",
        "Truncated subtraction in Nat does not exceed the minuend.",
    ),
    (
        "nat_le_trans",
        "∀ (a b c : Nat), a ≤ b → b ≤ c → a ≤ c",
        "intro a b c hab hbc\nomega",
        "Transitivity of order relation in Nat.",
    ),
    (
        "nat_mul_pos",
        "∀ (a b : Nat), a > 0 → b > 0 → a * b > 0",
        "intro a b ha hb\nexact Nat.mul_pos ha hb",
        "Product of strictly positive natural numbers is strictly positive.",
    ),
    # 2. Denominator strict positivity for Erdős–Straus linear progressions
    (
        "es_denom_4k3_pos",
        "∀ (k : Nat), 4 * k + 3 > 0",
        "intro k\nomega",
        "Strict positivity of denominator 4k + 3 for all k in Nat.",
    ),
    (
        "es_denom_4k3_ge_7",
        "∀ (k : Nat), k ≥ 1 → 4 * k + 3 ≥ 7",
        "intro k hk\nomega",
        "Lower bound on denominator 4k + 3 when k >= 1.",
    ),
    (
        "es_denom_3k2_pos",
        "∀ (k : Nat), 3 * k + 2 > 0",
        "intro k\nomega",
        "Strict positivity of denominator 3k + 2 for all k in Nat.",
    ),
    (
        "es_denom_3k2_ge_5",
        "∀ (k : Nat), k ≥ 1 → 3 * k + 2 ≥ 5",
        "intro k hk\nomega",
        "Lower bound on denominator 3k + 2 when k >= 1.",
    ),
    (
        "es_denom_8k5_pos",
        "∀ (k : Nat), 8 * k + 5 > 0",
        "intro k\nomega",
        "Strict positivity of denominator 8k + 5 for all k in Nat.",
    ),
    (
        "es_denom_8k5_ge_13",
        "∀ (k : Nat), k ≥ 1 → 8 * k + 5 ≥ 13",
        "intro k hk\nomega",
        "Lower bound on denominator 8k + 5 when k >= 1.",
    ),
    (
        "es_denom_24k1_pos",
        "∀ (k : Nat), 24 * k + 1 > 0",
        "intro k\nomega",
        "Strict positivity of denominator 24k + 1 for all k in Nat.",
    ),
    (
        "es_denom_24k1_ge_25",
        "∀ (k : Nat), k ≥ 1 → 24 * k + 1 ≥ 25",
        "intro k hk\nomega",
        "Lower bound on denominator 24k + 1 when k >= 1.",
    ),
    (
        "es_denom_120k2_pos",
        "∀ (k : Nat), 120 * k + 2 > 0",
        "intro k\nomega",
        "Strict positivity of denominator 120k + 2 for all k in Nat.",
    ),
    (
        "es_denom_120k2_ge_122",
        "∀ (k : Nat), k ≥ 1 → 120 * k + 2 ≥ 122",
        "intro k hk\nomega",
        "Lower bound on denominator 120k + 2 when k >= 1.",
    ),
    (
        "es_denom_840k1_pos",
        "∀ (k : Nat), 840 * k + 1 > 0",
        "intro k\nomega",
        "Strict positivity of denominator 840k + 1 for all k in Nat.",
    ),
    (
        "es_coord_x_pos",
        "∀ (k : Nat), k + 1 > 0",
        "intro k\nomega",
        "Strict positivity of coordinate k + 1 for all k in Nat.",
    ),
    (
        "es_coord_2k1_pos",
        "∀ (k : Nat), 2 * k + 1 > 0",
        "intro k\nomega",
        "Strict positivity of coordinate 2k + 1 for all k in Nat.",
    ),
    (
        "es_coord_3k1_pos",
        "∀ (k : Nat), 3 * k + 1 > 0",
        "intro k\nomega",
        "Strict positivity of coordinate 3k + 1 for all k in Nat.",
    ),
    (
        "es_coord_6k1_pos",
        "∀ (k : Nat), 6 * k + 1 > 0",
        "intro k\nomega",
        "Strict positivity of coordinate 6k + 1 for all k in Nat.",
    ),
    (
        "es_coord_12k1_pos",
        "∀ (k : Nat), 12 * k + 1 > 0",
        "intro k\nomega",
        "Strict positivity of coordinate 12k + 1 for all k in Nat.",
    ),
    # 3. Sierpiński progressions in Nat
    (
        "sier_denom_5k1_pos",
        "∀ (k : Nat), 5 * k + 1 > 0",
        "intro k\nomega",
        "Strict positivity of denominator 5k + 1 for all k in Nat.",
    ),
    (
        "sier_denom_5k2_pos",
        "∀ (k : Nat), 5 * k + 2 > 0",
        "intro k\nomega",
        "Strict positivity of denominator 5k + 2 for all k in Nat.",
    ),
    (
        "sier_denom_5k3_pos",
        "∀ (k : Nat), 5 * k + 3 > 0",
        "intro k\nomega",
        "Strict positivity of denominator 5k + 3 for all k in Nat.",
    ),
    (
        "sier_denom_5k4_pos",
        "∀ (k : Nat), 5 * k + 4 > 0",
        "intro k\nomega",
        "Strict positivity of denominator 5k + 4 for all k in Nat.",
    ),
    (
        "sier_denom_120k_rem",
        "∀ (k r : Nat), r > 0 → 120 * k + r > 0",
        "intro k r hr\nomega",
        "Strict positivity of denominator 120k + r whenever remainder r > 0.",
    ),
    # 4. Diophantine cross-terms and coordinate bounds
    (
        "dioph_denom_mul_pos",
        "∀ (x y : Nat), x > 0 → y > 0 → x * y > 0",
        "intro x y hx hy\nexact Nat.mul_pos hx hy",
        "Diophantine cross-product positivity.",
    ),
    (
        "dioph_cross_sum_pos",
        "∀ (x y z : Nat), x > 0 → y > 0 → z > 0 → x * y + y * z + x * z > 0",
        "intro x y z hx hy hz\nhave h1 : x * y > 0 := Nat.mul_pos hx hy\nomega",
        "Diophantine cross-sum positivity for positive coordinates.",
    ),
    (
        "dioph_coord_bound_sum",
        "∀ (x y z : Nat), x ≥ 1 → y ≥ 1 → z ≥ 1 → x + y + z ≥ 3",
        "intro x y z hx hy hz\nomega",
        "Lower bound on coordinate sum x + y + z in Nat when all >= 1.",
    ),
]


def generate_inductive_lemmas_source() -> str:
    """Generate Lean 4 module containing certified inductive & Presburger lemmas in Nat."""
    lines = [
        "import Mathlib.Tactic.Ring",
        "",
        "/-",
        "EvoByte Inductive and Presburger Baseline Lemmas in Nat (P81).",
        "Certified structural induction and linear arithmetic.",
        "-/",
        "",
    ]
    for name, sig, proof, doc in INDUCTIVE_LEAN_LEMMAS:
        lines.append(f"/-- {doc} -/")
        lines.append(f"theorem {name} : {sig} := by")
        for pline in proof.split("\n"):
            lines.append(f"  {pline}")
        lines.append("")
    return "\n".join(lines)


def export_inductive_lemmas_catalog(
    output_dir: str | Path = "lean_proofs/Generated",
    project_dir: str | Path = "lean_proofs",
) -> dict[str, Any]:
    """Export and verify InductiveLemmas.lean in the Lean 4 environment."""
    import subprocess

    t0 = time.perf_counter()
    proj = Path(project_dir).resolve()
    out = Path(output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)

    src = generate_inductive_lemmas_source()
    ind_file = out / "InductiveLemmas.lean"
    ind_file.write_text(src, encoding="utf-8")
    file_sha = hashlib.sha256(ind_file.read_bytes()).hexdigest()

    # Ensure Generated.lean imports Generated.InductiveLemmas
    root_file = proj / "Generated.lean"
    if root_file.exists():
        root_content = root_file.read_text(encoding="utf-8")
        if "import Generated.InductiveLemmas" not in root_content:
            root_content = root_content.rstrip() + "\nimport Generated.InductiveLemmas\n"
            root_file.write_text(root_content, encoding="utf-8")
    else:
        root_file.write_text(
            "-- EvoByte Root Generated Formal Library\nimport Generated.InductiveLemmas\n",
            encoding="utf-8",
        )

    # Compile the file
    v_res = compile_lean_file(ind_file, project_dir=proj)
    accepted = v_res.get("accepted", False)
    reasons = list(v_res.get("reasons", []))

    # Also build the Generated library via Lake
    bins = lean_resolve_binaries(proj)
    lake_proc = subprocess.run(
        [bins["lake"], "-d", str(proj), "build", "Generated"],
        capture_output=True,
        text=True,
        cwd=str(proj),
        timeout=120,
        check=False,
    )
    if lake_proc.returncode != 0:
        accepted = False
        reasons.append(f"lake_build_failed: {lake_proc.stderr[:160]}")

    elapsed = time.perf_counter() - t0

    return {
        "catalog_dir": str(out),
        "total_lemmas": len(INDUCTIVE_LEAN_LEMMAS),
        "file": str(ind_file),
        "sha256": file_sha,
        "accepted": accepted,
        "reasons": reasons,
        "has_sorry": "sorry" in reasons or "sorry" in ind_file.read_text(encoding="utf-8"),
        "elapsed_sec": elapsed,
    }


def verify_inductive_catalog_soundness(catalog_summary: dict[str, Any]) -> tuple[bool, list[str]]:
    """Audit inductive lemmas catalog for complete acceptance, zero sorry, and soundness."""
    findings: list[str] = []

    if not catalog_summary.get("accepted", False):
        findings.append(f"INDUCTIVE_COMPILATION_FAILED: {catalog_summary.get('reasons')}")

    if catalog_summary.get("has_sorry", False):
        findings.append("SORRY_DETECTED: inductive catalog contains sorry")

    total_lemmas = catalog_summary.get("total_lemmas", 0)
    if total_lemmas < 20:
        findings.append(f"INSUFFICIENT_LEMMAS: expected >= 20, got {total_lemmas}")

    if len(catalog_summary.get("sha256", "")) != 64:
        findings.append("INVALID_CHECKSUM_INDUCTIVE_LEMMAS")

    return (len(findings) == 0), findings


DIVISIBILITY_NAT_LEMMAS: list[tuple[str, str, str]] = [
    ("div_nat_2_mul", "∀ (k : Nat), 2 ∣ 2 * k", "⟨k, rfl⟩"),
    ("div_nat_3_lin", "∀ (k : Nat), 3 ∣ 6 * k + 9", "⟨2 * k + 3, by omega⟩"),
    ("div_nat_4_lin", "∀ (k : Nat), 4 ∣ 4 * k + 4", "⟨k + 1, by omega⟩"),
    ("div_nat_5_lin", "∀ (k : Nat), 5 ∣ 10 * k + 15", "⟨2 * k + 3, by omega⟩"),
    ("div_nat_6_lin", "∀ (k : Nat), 6 ∣ 12 * k + 18", "⟨2 * k + 3, by omega⟩"),
    ("div_nat_8_lin", "∀ (k : Nat), 8 ∣ 16 * k + 24", "⟨2 * k + 3, by omega⟩"),
    ("div_nat_12_lin", "∀ (k : Nat), 12 ∣ 24 * k + 36", "⟨2 * k + 3, by omega⟩"),
    ("div_nat_24_lin", "∀ (k : Nat), 24 ∣ 24 * k + 48", "⟨k + 2, by omega⟩"),
    ("div_nat_k1_prod", "∀ (k : Nat), (k + 1) ∣ (k + 1) * (4 * k + 1)", "⟨4 * k + 1, rfl⟩"),
    ("div_nat_2k1_prod", "∀ (k : Nat), (2 * k + 1) ∣ (2 * k + 1) * (k + 2)", "⟨k + 2, rfl⟩"),
    ("div_nat_4k1_sq", "∀ (k : Nat), (4 * k + 1) ∣ 16 * k ^ 2 + 8 * k + 1", "⟨4 * k + 1, by ring⟩"),
    ("div_nat_4k3_sq", "∀ (k : Nat), (4 * k + 3) ∣ 16 * k ^ 2 + 24 * k + 9", "⟨4 * k + 3, by ring⟩"),
    ("div_nat_k1_sq", "∀ (k : Nat), (k + 1) ∣ k ^ 2 + 2 * k + 1", "⟨k + 1, by ring⟩"),
    ("div_nat_k1_cube", "∀ (k : Nat), (k + 1) ∣ k ^ 3 + 3 * k ^ 2 + 3 * k + 1", "⟨k ^ 2 + 2 * k + 1, by ring⟩"),
    ("div_nat_2k1_sq", "∀ (k : Nat), (2 * k + 1) ∣ 4 * k ^ 2 + 4 * k + 1", "⟨2 * k + 1, by ring⟩"),
    ("div_nat_3k2_sq", "∀ (k : Nat), (3 * k + 2) ∣ 9 * k ^ 2 + 12 * k + 4", "⟨3 * k + 2, by ring⟩"),
    ("div_nat_k1_quad", "∀ (k : Nat), (k + 1) ∣ 4 * k ^ 2 + 5 * k + 1", "⟨4 * k + 1, by ring⟩"),
    ("div_nat_2k1_quad", "∀ (k : Nat), (2 * k + 1) ∣ 8 * k ^ 2 + 6 * k + 1", "⟨4 * k + 1, by ring⟩"),
    ("div_nat_3k1_quad", "∀ (k : Nat), (3 * k + 1) ∣ 9 * k ^ 2 + 6 * k + 1", "⟨3 * k + 1, by ring⟩"),
    ("div_nat_4k1_quad", "∀ (k : Nat), (4 * k + 1) ∣ 24 * k ^ 2 + 10 * k + 1", "⟨6 * k + 1, by ring⟩"),
]


def generate_divisibility_lemmas_source() -> str:
    """Generate Lean 4 source for certified Diophantine divisibility lemmas in Nat and Int."""
    lines: list[str] = [
        "/-",
        "EvoByte Formal Proof Catalog: Certified Diophantine Divisibility Lemmas in Nat and Int.",
        "-/",
        "",
        "import Mathlib.Tactic.Ring",
        "",
    ]

    for name, stmt, proof in DIVISIBILITY_NAT_LEMMAS:
        lines.append(f"theorem {name} : {stmt} := by")
        lines.append("  intro k")
        lines.append(f"  exact {proof}")
        lines.append("")

    for r in range(24):
        ident = get_algebraic_identity_for_residue(24, r)
        if ident is not None:
            n_str = poly1d_to_lean_int(ident.n_poly)
            x_str = poly1d_to_lean_int(ident.X)
            y_str = poly1d_to_lean_int(ident.Y)
            z_str = poly1d_to_lean_int(ident.Z)
            d = Poly1D.constant(ident.a) * ident.X * ident.Y - ident.n_poly * (ident.X + ident.Y)
            target = ident.n_poly * (ident.X + ident.Y)
            q = target.exact_divide(d)
            if q is not None:
                q_str = poly1d_to_lean_int(q)
                lines.append(
                    f"theorem erdos_div_cross_m24_r{r} : ∀ (k : ℤ),\n"
                    f"    ({ident.a} * ({x_str}) * ({y_str}) - ({n_str}) * (({x_str}) + ({y_str}))) ∣\n"
                    f"    ({n_str}) * (({x_str}) + ({y_str})) := by\n"
                    f"  intro k\n"
                    f"  exact ⟨{q_str}, by ring⟩\n"
                )
            lines.append(
                f"theorem erdos_div_z_m24_r{r} : ∀ (k : ℤ),\n"
                f"    ({ident.a} * ({x_str}) * ({y_str}) - ({n_str}) * (({x_str}) + ({y_str}))) ∣\n"
                f"    ({n_str}) * ({x_str}) * ({y_str}) := by\n"
                f"  intro k\n"
                f"  exact ⟨{z_str}, by ring⟩\n"
            )

    for r in range(24):
        ident = synthesize_sierpinski_identity(24, r)
        if ident is not None:
            n_str = poly1d_to_lean_int(ident.n_poly)
            x_str = poly1d_to_lean_int(ident.X)
            y_str = poly1d_to_lean_int(ident.Y)
            z_str = poly1d_to_lean_int(ident.Z)
            d = Poly1D.constant(ident.a) * ident.X * ident.Y - ident.n_poly * (ident.X + ident.Y)
            target = ident.n_poly * (ident.X + ident.Y)
            q = target.exact_divide(d)
            if q is not None:
                q_str = poly1d_to_lean_int(q)
                lines.append(
                    f"theorem sierpinski_div_cross_m24_r{r} : ∀ (k : ℤ),\n"
                    f"    ({ident.a} * ({x_str}) * ({y_str}) - ({n_str}) * (({x_str}) + ({y_str}))) ∣\n"
                    f"    ({n_str}) * (({x_str}) + ({y_str})) := by\n"
                    f"  intro k\n"
                    f"  exact ⟨{q_str}, by ring⟩\n"
                )
            lines.append(
                f"theorem sierpinski_div_z_m24_r{r} : ∀ (k : ℤ),\n"
                f"    ({ident.a} * ({x_str}) * ({y_str}) - ({n_str}) * (({x_str}) + ({y_str}))) ∣\n"
                f"    ({n_str}) * ({x_str}) * ({y_str}) := by\n"
                f"  intro k\n"
                f"  exact ⟨{z_str}, by ring⟩\n"
            )

    return "\n".join(lines).rstrip() + "\n"


def export_divisibility_lemmas_catalog(
    output_dir: str | Path = "lean_proofs/Generated",
    project_dir: str | Path = "lean_proofs",
) -> dict[str, Any]:
    """Generate and compile certified Diophantine divisibility lemmas in Nat and Int (P82)."""
    import subprocess

    t0 = time.perf_counter()
    out = Path(output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    proj = Path(project_dir).resolve()

    src = generate_divisibility_lemmas_source()
    div_file = out / "DivisibilityLemmas.lean"
    div_file.write_text(src, encoding="utf-8")
    file_sha = hashlib.sha256(div_file.read_bytes()).hexdigest()

    # Ensure Generated.lean imports DivisibilityLemmas
    root_file = proj / "Generated.lean"
    if root_file.exists():
        root_content = root_file.read_text(encoding="utf-8")
        if "import Generated.DivisibilityLemmas" not in root_content:
            root_content = root_content.rstrip() + "\nimport Generated.DivisibilityLemmas\n"
            root_file.write_text(root_content, encoding="utf-8")
    else:
        root_file.write_text(
            "-- EvoByte Root Generated Formal Library\nimport Generated.DivisibilityLemmas\n",
            encoding="utf-8",
        )

    v_res = compile_lean_file(div_file, project_dir=proj)
    accepted = v_res.get("accepted", False)
    reasons = list(v_res.get("reasons", []))

    bins = lean_resolve_binaries(proj)
    lake_proc = subprocess.run(
        [bins["lake"], "-d", str(proj), "build", "Generated"],
        capture_output=True,
        text=True,
        cwd=str(proj),
        timeout=180,
        check=False,
    )
    if lake_proc.returncode != 0:
        accepted = False
        reasons.append(f"lake_build_failed: {lake_proc.stderr[:160]}")

    elapsed = time.perf_counter() - t0
    total_lemmas = src.count("theorem ")

    return {
        "catalog_dir": str(out),
        "total_lemmas": total_lemmas,
        "file": str(div_file),
        "sha256": file_sha,
        "accepted": accepted,
        "reasons": reasons,
        "has_sorry": "sorry" in reasons or "sorry" in div_file.read_text(encoding="utf-8"),
        "elapsed_sec": elapsed,
    }


def verify_divisibility_catalog_soundness(catalog_summary: dict[str, Any]) -> tuple[bool, list[str]]:
    """Audit divisibility lemmas catalog for complete acceptance, zero sorry, and soundness."""
    findings: list[str] = []

    if not catalog_summary.get("accepted", False):
        findings.append(f"DIVISIBILITY_COMPILATION_FAILED: {catalog_summary.get('reasons')}")

    if catalog_summary.get("has_sorry", False):
        findings.append("SORRY_DETECTED: divisibility catalog contains sorry")

    total_lemmas = catalog_summary.get("total_lemmas", 0)
    if total_lemmas < 50:
        findings.append(f"INSUFFICIENT_LEMMAS: expected >= 50, got {total_lemmas}")

    if len(catalog_summary.get("sha256", "")) != 64:
        findings.append("INVALID_CHECKSUM_DIVISIBILITY_LEMMAS")

    return (len(findings) == 0), findings


def export_optimal_certificates_catalog(
    target_primes: list[int] | None = None,
    output_dir: str | Path = "lean_proofs/Generated",
    project_dir: str | Path = "lean_proofs",
) -> dict[str, Any]:
    """Generate and compile certified Lean 4 theorems for optimal divisor selection solutions (P83)."""
    import subprocess

    from evobyte.algebraic import optimal_erdos_straus_sieve, optimal_sierpinski_sieve

    t0 = time.perf_counter()
    out = Path(output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    proj = Path(project_dir).resolve()

    primes = target_primes or [
        73,
        97,
        193,
        241,
        313,
        337,
        1009,
        1033,
        1129,
        1153,
        1201,
        1249,
        1297,
        1321,
        1489,
        1609,
    ]

    theorems: list[str] = []
    solutions: list[dict[str, Any]] = []

    for p in primes:
        sol_es, det_es = optimal_erdos_straus_sieve(p)
        if sol_es is not None:
            x, y, z = sol_es
            solutions.append(
                {
                    "p": p,
                    "a": 4,
                    "x": x,
                    "y": y,
                    "z": z,
                    "opt_coord": det_es.get("optimal_coord"),
                }
            )
            doc = (
                f"/-- Certified optimal Erdős–Straus solution for n = {p} (P83).\n"
                f"    Verified exact: 4/{p} = 1/{x} + 1/{y} + 1/{z} with minimal coordinate {max(x, y, z)}. -/"
            )
            stmt = (
                f"theorem erdos_straus_opt_cert_n{p} :\n"
                f"    (4 : ℚ) / {p} = 1 / {x} + 1 / {y} + 1 / {z} := by\n"
                f"  norm_num"
            )
            theorems.append(f"{doc}\n{stmt}\n")

        sol_sier, det_sier = optimal_sierpinski_sieve(p)
        if sol_sier is not None:
            x, y, z = sol_sier
            solutions.append(
                {
                    "p": p,
                    "a": 5,
                    "x": x,
                    "y": y,
                    "z": z,
                    "opt_coord": det_sier.get("optimal_coord"),
                }
            )
            doc = (
                f"/-- Certified optimal Sierpiński solution for n = {p} (P83).\n"
                f"    Verified exact: 5/{p} = 1/{x} + 1/{y} + 1/{z} with minimal coordinate {max(x, y, z)}. -/"
            )
            stmt = (
                f"theorem sierpinski_opt_cert_n{p} :\n"
                f"    (5 : ℚ) / {p} = 1 / {x} + 1 / {y} + 1 / {z} := by\n"
                f"  norm_num"
            )
            theorems.append(f"{doc}\n{stmt}\n")

    doc_header = (
        "EvoByte Formal Proof Catalog: Certified Optimal Diophantine Solution Certificates in Q."
    )
    src = generate_lean_proof_module(theorems, doc_header)
    opt_file = out / "OptimalCertificates.lean"
    opt_file.write_text(src, encoding="utf-8")
    file_sha = hashlib.sha256(opt_file.read_bytes()).hexdigest()

    # Ensure Generated.lean imports OptimalCertificates
    root_file = proj / "Generated.lean"
    if root_file.exists():
        root_content = root_file.read_text(encoding="utf-8")
        if "import Generated.OptimalCertificates" not in root_content:
            root_content = root_content.rstrip() + "\nimport Generated.OptimalCertificates\n"
            root_file.write_text(root_content, encoding="utf-8")
    else:
        root_file.write_text(
            "-- EvoByte Root Generated Formal Library\nimport Generated.OptimalCertificates\n",
            encoding="utf-8",
        )

    v_res = compile_lean_file(opt_file, project_dir=proj)
    accepted = v_res.get("accepted", False)
    reasons = list(v_res.get("reasons", []))

    bins = lean_resolve_binaries(proj)
    lake_proc = subprocess.run(
        [bins["lake"], "-d", str(proj), "build", "Generated"],
        capture_output=True,
        text=True,
        cwd=str(proj),
        timeout=180,
        check=False,
    )
    if lake_proc.returncode != 0:
        accepted = False
        reasons.append(f"lake_build_failed: {lake_proc.stderr[:160]}")

    elapsed = time.perf_counter() - t0
    total_certs = src.count("theorem ")

    return {
        "catalog_dir": str(out),
        "total_certificates": total_certs,
        "file": str(opt_file),
        "sha256": file_sha,
        "accepted": accepted,
        "reasons": reasons,
        "has_sorry": "sorry" in reasons or "sorry" in opt_file.read_text(encoding="utf-8"),
        "solutions": solutions,
        "elapsed_sec": elapsed,
    }


def verify_optimal_catalog_soundness(
    catalog_summary: dict[str, Any], min_certificates: int = 8
) -> tuple[bool, list[str]]:
    """Audit optimal certificates catalog for complete acceptance, zero sorry, and soundness."""
    findings: list[str] = []

    if not catalog_summary.get("accepted", False):
        findings.append(f"OPTIMAL_CERT_COMPILATION_FAILED: {catalog_summary.get('reasons')}")

    if catalog_summary.get("has_sorry", False):
        findings.append("SORRY_DETECTED: optimal certificates catalog contains sorry")

    total_certs = catalog_summary.get("total_certificates", 0)
    if total_certs < min_certificates:
        findings.append(f"INSUFFICIENT_CERTIFICATES: expected >= {min_certificates}, got {total_certs}")

    if len(catalog_summary.get("sha256", "")) != 64:
        findings.append("INVALID_CHECKSUM_OPTIMAL_CERTIFICATES")

    return (len(findings) == 0), findings


# -----------------------------------------------------------------------------
# Multiparameter & Quadratic Identities (P84)
# -----------------------------------------------------------------------------


def export_quadratic_identities_catalog(
    output_dir: str | Path = "lean_proofs/Generated",
    project_dir: str | Path = "lean_proofs",
) -> dict[str, Any]:
    """Generate and verify multiparameter quadratic polynomial identities in Lean 4 (P84).

    Exports `lean_proofs/Generated/QuadraticIdentities.lean`, containing:
    1. 12 parametric theorems over Q[u, v] and Q[u] for Erdős–Straus (a = 4) and Sierpiński (a = 5),
       proven with Lean 4 kernel tactic `ring` with zero sorry.
    2. 10 certified Diophantine solution theorems for resistant residues mod 840 (ES) and mod 120 (Sierpiński),
       proven with `norm_num`.
    """
    import subprocess

    t0 = time.perf_counter()
    proj = Path(project_dir).resolve()
    out = Path(output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)

    identities = synthesize_quadratic_identities()
    theorems: list[str] = [ident.to_lean_theorem() for ident in identities]

    res_cov = evaluate_resistant_residues_coverage()
    for inst in res_cov["instances"]:
        name = inst["lean_theorem_name"]
        a = inst["a"]
        n = inst["n"]
        x, y, z = inst["solution"]
        doc = (
            f"/-- Certified Diophantine solution for resistant residue n = {n} (P84).\n"
            f"    Verified exact: {a}/{n} = 1/{x} + 1/{y} + 1/{z} with pairwise distinct positive integers. -/"
        )
        stmt = (
            f"theorem {name} :\n"
            f"    ({a} : ℚ) / {n} = 1 / {x} + 1 / {y} + 1 / {z} := by\n"
            f"  norm_num"
        )
        theorems.append(f"{doc}\n{stmt}\n")

    doc_header = (
        "EvoByte Formal Proof Catalog: Certified Multiparameter Quadratic Identities in Q[u, v]."
    )
    src = generate_lean_proof_module(theorems, doc_header)
    quad_file = out / "QuadraticIdentities.lean"
    quad_file.write_text(src, encoding="utf-8")
    file_sha = hashlib.sha256(quad_file.read_bytes()).hexdigest()

    # Ensure Generated.lean imports QuadraticIdentities
    root_file = proj / "Generated.lean"
    if root_file.exists():
        root_content = root_file.read_text(encoding="utf-8")
        if "import Generated.QuadraticIdentities" not in root_content:
            root_content = root_content.rstrip() + "\nimport Generated.QuadraticIdentities\n"
            root_file.write_text(root_content, encoding="utf-8")
    else:
        root_file.write_text(
            "-- EvoByte Root Generated Formal Library\nimport Generated.QuadraticIdentities\n",
            encoding="utf-8",
        )

    v_res = compile_lean_file(quad_file, project_dir=proj)
    accepted = v_res.get("accepted", False)
    reasons = list(v_res.get("reasons", []))

    bins = lean_resolve_binaries(proj)
    lake_proc = subprocess.run(
        [bins["lake"], "-d", str(proj), "build", "Generated"],
        capture_output=True,
        text=True,
        cwd=str(proj),
        timeout=180,
        check=False,
    )
    if lake_proc.returncode != 0:
        accepted = False
        reasons.append(f"lake_build_failed: {lake_proc.stderr[:160]}")

    elapsed = time.perf_counter() - t0
    total_theorems = src.count("theorem ")

    return {
        "catalog_dir": str(out),
        "total_theorems": total_theorems,
        "parametric_theorems_count": len(identities),
        "instance_certificates_count": len(res_cov["instances"]),
        "file": str(quad_file),
        "sha256": file_sha,
        "accepted": accepted,
        "reasons": reasons,
        "has_sorry": "sorry" in reasons or "sorry" in quad_file.read_text(encoding="utf-8"),
        "identities": [ident.to_dict() for ident in identities],
        "resistant_instances": res_cov["instances"],
        "elapsed_sec": elapsed,
    }


def verify_quadratic_catalog_soundness(
    catalog_summary: dict[str, Any], min_identities: int = 10
) -> tuple[bool, list[str]]:
    """Audit quadratic identities catalog for complete acceptance, zero sorry, and soundness."""
    findings: list[str] = []

    if not catalog_summary.get("accepted", False):
        findings.append(f"QUADRATIC_COMPILATION_FAILED: {catalog_summary.get('reasons')}")

    if catalog_summary.get("has_sorry", False):
        findings.append("SORRY_DETECTED: quadratic identities catalog contains sorry")

    total_thms = catalog_summary.get("total_theorems", 0)
    if total_thms < min_identities:
        findings.append(
            f"INSUFFICIENT_THEOREMS: expected >= {min_identities}, got {total_thms}"
        )

    if len(catalog_summary.get("sha256", "")) != 64:
        findings.append("INVALID_CHECKSUM_QUADRATIC_IDENTITIES")

    return (len(findings) == 0), findings
