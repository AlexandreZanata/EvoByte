"""Hermetic open problems database, dependent typing, and partition orchestration (P105).

Provides formal representation, validation, and hermetic partitioning of the
100 open problems curated from the Erdős Problems dataset (docs/research/open-problems.json).
Generates verified dependent Lean 4 types and signatures in
`lean_proofs/Generated/OpenProblemSignatures.lean`.
"""

from __future__ import annotations

import hashlib
import json
import random
import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from evobyte.verifier import lean_resolve_binaries

DEFAULT_DB_PATH = Path("docs/research/open-problems.json")
GENERATED_LEAN_PATH = Path("lean_proofs/Generated/OpenProblemSignatures.lean")


@dataclass(frozen=True)
class OpenProblemEntry:
    id: str
    title: str
    area: str
    certificate_type: str
    statement_excerpt: str
    statement_sha256: str
    partition: str  # "dev" or "blind"
    finite_resolution_possible: bool = False
    prize: str = "no"


def load_open_problems(db_path: Path | str = DEFAULT_DB_PATH) -> list[dict[str, Any]]:
    """Load and validate the 100 curated open problems from docs/research/open-problems.json."""
    p = Path(db_path)
    if not p.exists():
        raise FileNotFoundError(f"Open problems database not found at {p}")

    with open(p, encoding="utf-8") as f:
        data = json.load(f)

    raw_problems = data.get("open_confirmed", [])
    if len(raw_problems) != 100:
        raise ValueError(f"Expected exactly 100 open_confirmed problems, found {len(raw_problems)}")

    # Validate essential fields for each problem
    for idx, prob in enumerate(raw_problems):
        if not prob.get("id"):
            raise ValueError(f"Problem at index {idx} missing 'id'")
        if not prob.get("statement_sha256"):
            raise ValueError(f"Problem {prob.get('id')} missing 'statement_sha256'")
        if not prob.get("certificate_type"):
            raise ValueError(f"Problem {prob.get('id')} missing 'certificate_type'")

    return raw_problems


def partition_open_problems(
    problems: list[dict[str, Any]],
    blind_ratio: float = 0.30,
    seed: int = 42,
) -> dict[str, Any]:
    """Hermetically partition open problems into development and sealed blind sets.

    Ensures zero leakage, determinism, and full cryptographic commitment of the split.
    """
    total = len(problems)
    if total == 0:
        raise ValueError("Cannot partition empty problems list")

    n_blind = int(total * blind_ratio)
    total - n_blind

    rng = random.Random(seed)
    indices = list(range(total))
    rng.shuffle(indices)

    blind_indices = set(indices[:n_blind])
    dev_indices = set(indices[n_blind:])

    # Strictly disjoint
    assert len(dev_indices & blind_indices) == 0, "Partitions must be disjoint"
    assert len(dev_indices | blind_indices) == total, "Partitions must be exhaustive"

    dev_problems: list[dict[str, Any]] = []
    blind_problems: list[dict[str, Any]] = []
    all_assigned: list[dict[str, Any]] = []

    for idx, p in enumerate(problems):
        p_copy = dict(p)
        if idx in blind_indices:
            p_copy["partition"] = "blind"
            blind_problems.append(p_copy)
        else:
            p_copy["partition"] = "dev"
            dev_problems.append(p_copy)
        all_assigned.append(p_copy)

    # Compute commitment hashes
    dev_hash = hashlib.sha256(",".join(sorted(p["id"] for p in dev_problems)).encode()).hexdigest()
    blind_hash = hashlib.sha256(
        ",".join(sorted(p["id"] for p in blind_problems)).encode()
    ).hexdigest()
    split_payload = ":".join(f"{p['id']}={p['partition']}" for p in all_assigned).encode()
    split_hash = hashlib.sha256(split_payload).hexdigest()

    return {
        "seed": seed,
        "blind_ratio": blind_ratio,
        "total_count": total,
        "dev_count": len(dev_problems),
        "blind_count": len(blind_problems),
        "dev_problems": dev_problems,
        "blind_problems": blind_problems,
        "all_assigned": all_assigned,
        "dev_ids": [p["id"] for p in dev_problems],
        "blind_ids": [p["id"] for p in blind_problems],
        "dev_hash": dev_hash,
        "blind_hash": blind_hash,
        "split_hash": split_hash,
        "leakage_detected": False,
    }


def area_to_lean(area: str) -> str:
    """Map string area name to Lean 4 ProblemArea constructor."""
    norm = area.strip().lower()
    if "number" in norm:
        return "ProblemArea.numberTheory"
    elif "additive" in norm:
        return "ProblemArea.additiveCombinatorics"
    elif "prime" in norm:
        return "ProblemArea.primes"
    elif "geometry" in norm or "distance" in norm:
        return "ProblemArea.geometry"
    elif "graph" in norm:
        return "ProblemArea.graphTheory"
    elif "combinator" in norm or "discrepancy" in norm or "sidon" in norm:
        return "ProblemArea.combinatorics"
    elif "progression" in norm or "primitive" in norm:
        return "ProblemArea.numberTheory"
    elif "group" in norm or "algebra" in norm:
        return "ProblemArea.algebra"
    elif "diophant" in norm:
        return "ProblemArea.diophantine"
    else:
        return "ProblemArea.other"


def cert_type_to_lean(cert: str) -> str:
    """Map string certificate type to Lean 4 CertificateType constructor."""
    if "construction" in cert or "impossibility" in cert:
        return "CertificateType.constructionOrImpossibility"
    else:
        return "CertificateType.proofOrCounterexample"


def safe_id_name(problem_id: str) -> str:
    """Convert problem id like 'erdos-3' into valid Lean identifier 'erdos_3'."""
    return re.sub(r"[^a-zA-Z0-9_]", "_", problem_id)


def generate_open_problems_lean_code(partition_summary: dict[str, Any]) -> str:
    """Generate complete Lean 4 module containing dependent types, signatures, and theorems."""
    lines = [
        (
            "/-\nEvoByte Formal Open Problem Signatures and Dependent Typing (P105).\n\n"
            "Defines dependent types, problem signatures, and formal validation theorems\n"
            "for the 100 open problems curated from the Erdős Problems dataset under\n"
            "hermetic partitioning (dev vs. sealed blind).\n-/"
        ),
        "",
        "import Mathlib.Data.Nat.Basic",
        "import Mathlib.Data.Rat.Defs",
        "import Mathlib.Tactic.Ring",
        "import Mathlib.Tactic.NormNum",
        "",
        "namespace EvoByte.OpenProblems",
        "",
        "/-- Problem mathematical area / classification. -/",
        "inductive ProblemArea where",
        "  | numberTheory : ProblemArea",
        "  | additiveCombinatorics : ProblemArea",
        "  | primes : ProblemArea",
        "  | geometry : ProblemArea",
        "  | graphTheory : ProblemArea",
        "  | combinatorics : ProblemArea",
        "  | algebra : ProblemArea",
        "  | diophantine : ProblemArea",
        "  | other : ProblemArea",
        "  deriving DecidableEq, Repr",
        "",
        "/-- Certificate / expected resolution type. -/",
        "inductive CertificateType where",
        "  | proofOrCounterexample : CertificateType",
        "  | constructionOrImpossibility : CertificateType",
        "  deriving DecidableEq, Repr",
        "",
        "/-- Hermetic dataset partition: development vs. sealed blind. -/",
        "inductive ProblemPartition where",
        "  | dev : ProblemPartition",
        "  | blind : ProblemPartition",
        "  deriving DecidableEq, Repr",
        "",
        "/-- Formal dependent problem signature structure. -/",
        "structure ProblemSignature where",
        "  id : String",
        "  area : ProblemArea",
        "  certType : CertificateType",
        "  partition : ProblemPartition",
        "  statementHash : String",
        "  deriving DecidableEq, Repr",
        "",
        "/-- Helper decidable partition check. -/",
        "def isDev (p : ProblemPartition) : Bool :=",
        "  match p with",
        "  | ProblemPartition.dev => true",
        "  | ProblemPartition.blind => false",
        "",
        "def isBlind (p : ProblemPartition) : Bool :=",
        "  match p with",
        "  | ProblemPartition.dev => false",
        "  | ProblemPartition.blind => true",
        "",
        "/-- Theorem: Dev and Blind partitions are strictly disjoint. -/",
        "theorem partition_disjoint (p : ProblemPartition) : ¬(isDev p = true ∧ isBlind p = true) := by",
        "  cases p <;> decide",
        "",
        "/-- Theorem: Partitions are exhaustive (every problem is either Dev or Blind). -/",
        "theorem partition_exhaustive (p : ProblemPartition) : isDev p = true ∨ isBlind p = true := by",
        "  cases p <;> decide",
        "",
        "/-- Unit fraction representation: a/n = 1/x + 1/y + 1/z. -/",
        "def IsUnitFractionSol (a n x y z : ℕ) : Prop :=",
        "  x > 0 ∧ y > 0 ∧ z > 0 ∧ (a : ℚ) / (n : ℚ) = 1 / (x : ℚ) + 1 / (y : ℚ) + 1 / (z : ℚ)",
        "",
        "/-- Erdős-Graham unit fraction representation: sum of 1/d_i = 1. -/",
        "def IsErdosGrahamUnitSum (denoms : List ℕ) : Prop :=",
        "  (∀ d ∈ denoms, d > 0) ∧ (List.map (fun (d : ℕ) => (1 : ℚ) / (d : ℚ)) denoms).sum = 1",
        "",
        "/-- Pillai exponential Diophantine equation: x^p - y^q = c for x, y, p, q >= 2. -/",
        "def IsPillaiSol (x p y q : ℕ) (c : ℤ) : Prop :=",
        "  x ≥ 2 ∧ y ≥ 2 ∧ p ≥ 2 ∧ q ≥ 2 ∧ ((x : ℤ) ^ p - (y : ℤ) ^ q = c)",
        "",
        "/-- Verified canonical Erdős-Graham unit fraction identity (3 terms). -/",
        "theorem erdos_graham_solution_3 : (1 : ℚ) / 2 + 1 / 3 + 1 / 6 = 1 := by",
        "  norm_num",
        "",
        "/-- Verified canonical Erdős-Graham unit fraction identity (4 terms). -/",
        "theorem erdos_graham_solution_4 : (1 : ℚ) / 2 + 1 / 4 + 1 / 6 + 1 / 12 = 1 := by",
        "  norm_num",
        "",
        "/-- Verified canonical Pillai / Catalan solution 3^2 - 2^3 = 1. -/",
        "theorem catalan_solution : (3 : ℤ) ^ 2 - (2 : ℤ) ^ 3 = 1 := by",
        "  norm_num",
        "",
        "/-- Verified Pillai solution 2^5 - 5^2 = 7. -/",
        "theorem pillai_solution_7 : (2 : ℤ) ^ 5 - (5 : ℤ) ^ 2 = 7 := by",
        "  norm_num",
        "",
        "/-- Verified Pillai solution 2^7 - 11^2 = 7. -/",
        "theorem pillai_solution_128_121 : (2 : ℤ) ^ 7 - (11 : ℤ) ^ 2 = 7 := by",
        "  norm_num",
        "",
        "/-- Verified Pillai solution 3^5 - 2^7 = 115. -/",
        "theorem pillai_solution_243_128 : (3 : ℤ) ^ 5 - (2 : ℤ) ^ 7 = 115 := by",
        "  norm_num",
        "",
    ]

    all_probs = partition_summary["all_assigned"]
    for p in all_probs:
        s_id = safe_id_name(p["id"])
        area_lean = area_to_lean(p.get("area", ""))
        cert_lean = cert_type_to_lean(p.get("certificate_type", ""))
        part_lean = (
            "ProblemPartition.dev" if p.get("partition") == "dev" else "ProblemPartition.blind"
        )
        h_str = p.get("statement_sha256", "")

        lines.append(f"/-- Signature definition for {p['title']} ({p['id']}). -/")
        lines.append(f"def sig_{s_id} : ProblemSignature := {{")
        lines.append(f'  id := "{p["id"]}",')
        lines.append(f"  area := {area_lean},")
        lines.append(f"  certType := {cert_lean},")
        lines.append(f"  partition := {part_lean},")
        lines.append(f'  statementHash := "{h_str}"')
        lines.append("}")
        lines.append("")
        lines.append(
            f"/-- Formal proof that signature for {p['id']} possesses designated partition. -/"
        )
        lines.append(f"theorem sig_{s_id}_partition : sig_{s_id}.partition = {part_lean} := by")
        lines.append("  rfl")
        lines.append("")

    lines.append("end EvoByte.OpenProblems")
    lines.append("")
    return "\n".join(lines)


def export_open_problems_lean_signatures(
    partition_summary: dict[str, Any],
    output_path: Path | str = GENERATED_LEAN_PATH,
) -> Path:
    """Generate and write OpenProblemSignatures.lean to disk."""
    code = generate_open_problems_lean_code(partition_summary)
    out_p = Path(output_path).resolve()
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(code, encoding="utf-8")
    return out_p


def audit_open_problems_database(
    db_path: Path | str = DEFAULT_DB_PATH,
    generated_path: Path | str = GENERATED_LEAN_PATH,
    project_dir: Path | str = "lean_proofs",
    blind_ratio: float = 0.30,
    seed: int = 42,
    verify_lake: bool = True,
) -> dict[str, Any]:
    """Audit the hermetic open problems database and Lean 4 signatures module (P105)."""
    t0 = time.perf_counter()
    db_p = Path(db_path).resolve()
    gen_p = Path(generated_path).resolve()
    proj = Path(project_dir).resolve()

    problems = load_open_problems(db_p)
    partition = partition_open_problems(problems, blind_ratio=blind_ratio, seed=seed)

    # Export or verify Lean signatures
    export_open_problems_lean_signatures(partition, gen_p)

    lean_bytes = gen_p.read_bytes()
    lean_text = lean_bytes.decode("utf-8")
    lean_sha256 = hashlib.sha256(lean_bytes).hexdigest()

    thms_count = len(re.findall(r"^(?:theorem|lemma)\s+", lean_text, flags=re.MULTILINE))
    has_sorry = bool(re.search(r"\bsorry\b", lean_text))

    lake_passed = True
    lake_reasons: list[str] = []
    if verify_lake:
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
            lake_passed = False
            lake_reasons.append(f"lake_build_failed: {lake_proc.stderr[:160]}")

    elapsed = time.perf_counter() - t0

    return {
        "phase": "P105",
        "database_path": str(db_p),
        "database_sha256": hashlib.sha256(db_p.read_bytes()).hexdigest(),
        "total_problems": partition["total_count"],
        "dev_count": partition["dev_count"],
        "blind_count": partition["blind_count"],
        "dev_hash": partition["dev_hash"],
        "blind_hash": partition["blind_hash"],
        "split_hash": partition["split_hash"],
        "leakage_detected": partition["leakage_detected"],
        "generated_lean_path": str(gen_p),
        "generated_lean_sha256": lean_sha256,
        "theorem_count": thms_count,
        "has_sorry": has_sorry,
        "lake_passed": lake_passed,
        "lake_reasons": lake_reasons,
        "elapsed_sec": elapsed,
        "dev_ids": partition["dev_ids"],
        "blind_ids": partition["blind_ids"],
    }


def verify_open_problems_database_soundness(
    audit_summary: dict[str, Any],
    min_problems: int = 100,
    min_theorems: int = 100,
) -> tuple[bool, list[str]]:
    """Verify soundness of the P105 open problems database and Lean 4 compilation."""
    findings: list[str] = []

    total_probs = audit_summary.get("total_problems", 0)
    if total_probs < min_problems:
        findings.append(f"INSUFFICIENT_PROBLEMS: expected >= {min_problems}, got {total_probs}")

    if audit_summary.get("leakage_detected", True):
        findings.append("DATASET_LEAKAGE: overlap detected between dev and blind partitions")

    dev_cnt = audit_summary.get("dev_count", 0)
    blind_cnt = audit_summary.get("blind_count", 0)
    if dev_cnt + blind_cnt != total_probs:
        findings.append(
            f"INCOMPLETE_PARTITION: dev ({dev_cnt}) + blind ({blind_cnt}) != total ({total_probs})"
        )

    if audit_summary.get("has_sorry", False):
        findings.append("SORRY_DETECTED: unproven sorry tokens present in formal signatures")

    thms = audit_summary.get("theorem_count", 0)
    if thms < min_theorems:
        findings.append(f"INSUFFICIENT_THEOREMS: expected >= {min_theorems}, got {thms}")

    if not audit_summary.get("lake_passed", False):
        findings.append(f"LAKE_BUILD_FAILED: {audit_summary.get('lake_reasons')}")

    return len(findings) == 0, findings
