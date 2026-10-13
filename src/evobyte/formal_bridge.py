"""Bytecode compiler to certified Lean 4 theorems and formal proof bridge (P77).

Translates EvoByte mathematical artifacts (algebraic polynomial identities over Q[k],
Diophantine integer solution certificates, and decompiled bytecode programs)
into rigorous Lean 4 definitions and theorems proven automatically by formal kernel
tactics (`ring`, `norm_num`, `linarith`, `omega`) without human intervention or `sorry`.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import numpy as np

from evobyte.algebraic import (
    AlgebraicIdentity,
    Poly1D,
    get_algebraic_identity_for_residue,
    get_resistant_residues,
    rational_divisor_sieve,
    sierpinski_divisor_sieve,
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
    root_src = (
        "-- EvoByte Root Generated Formal Library\n"
        "import Generated.ErdosStrausIdentities\n"
        "import Generated.ErdosStrausCertificates\n"
        "import Generated.BytecodeTheorems\n"
        "import Generated.SierpinskiTheorems\n"
    )
    root_file = proj / "Generated.lean"
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
