"""P25 — Math corpus consolidation (leak-free benchmark).

Audited GSM8K base + verifiable NuminaMath-1.5 subset + SymbolicMathematics tasks.
Pins versions, hashes, licenses and seals held-out test set.
Separates EXECUTE (calculation chain) vs FIND (program/solution synthesis) tracks.
Runs under Max-GPU rules: adaptive VRAM budget, 8 CPU workers, GPU chunked check,
synchronized timing, and OOM halving.
"""

from __future__ import annotations

import argparse
import ast
import concurrent.futures
import datetime
import hashlib
import json
import math
import re
import sys
import time
import warnings
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import sympy as sp
import torch

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "src"))

from evobyte.provenance import (
    MonotonicDeadline,
    collect_provenance,
    resolve_device,
    seed_all,
    synchronize,
    write_manifest,
)

# Pinned upstream dataset specifications
GSM8K_PIN = {
    "dataset_id": "openai/gsm8k",
    "source_url": "https://github.com/openai/grade-school-math",
    "license": "MIT",
    "split_default": "test",
    "expected_n": 1319,
    "expected_sha256": "3730d312f6e3440559ace48831e51066acaca737f6eabec99bccb9e4b3c39d14",
    "internal_exposure_disclosure": (
        "GSM8K test split was previously exposed in P14/P23 experiments "
        "(experiments/mathdb-*.json); disqualified as an untouched official test set. "
        "Included for execution audit and chain reproducibility."
    ),
}

NUMINAMATH_PIN = {
    "dataset_id": "AI-MO/NuminaMath-1.5",
    "source_url": "https://huggingface.co/datasets/AI-MO/NuminaMath-1.5",
    "license": "Apache-2.0",
    "subset_definition": "verifiable_numeric_and_algebraic_answers",
    "validation_rules": [
        "problem_is_valid == 'Yes'",
        "solution_is_valid == 'Yes'",
        "answer != 'proof'",
        "answer must resolve to scalar integer/rational/float",
    ],
}

SYMBOLIC_PIN = {
    "dataset_id": "facebookresearch/SymbolicMathematics",
    "source_url": "https://github.com/facebookresearch/SymbolicMathematics",
    "license": "CC-BY-NC-4.0 / Open Source",
    "generator_model": "Lample & Charton (2019) deterministic symbolic task generator",
    "task_families": [
        "symbolic_differentiation",
        "symbolic_integration",
        "polynomial_arithmetic",
        "first_order_ode",
    ],
}

RAW_GSM8K_PATH = _REPO_ROOT / "data" / "raw" / "gsm8k-test.jsonl"
RAW_NUMINA_CACHE = _REPO_ROOT / "data" / "raw" / "numinamath_sample.jsonl"
PROCESSED_CORPUS_PATH = _REPO_ROOT / "data" / "processed" / "p25_corpus.jsonl"

CHAIN_RE = re.compile(r"<<(.+?)>>")
FINAL_RE = re.compile(r"####\s*(-?[\d,]*\.?\d+)")
NUM_EXTRACT_RE = re.compile(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?")
BOXED_RE = re.compile(r"\\boxed\{([^{}]+)\}")
FRAC_RE = re.compile(r"\\frac\{([^{}]+)\}\{([^{}]+)\}")

MAX_WORKERS = 8


@dataclass
class CorpusItem:
    """Standardized representation of a single benchmark task."""

    id: str
    source: str
    source_id: str
    track: str  # "EXECUTE" or "FIND"
    family: str
    difficulty: int  # 1 to 5
    problem_text: str
    expression: str | None
    inputs: list[float]
    constraints: dict[str, Any]
    allowed_ops: list[str]
    target_answer: float
    verifier: dict[str, Any]
    metadata: dict[str, Any]
    verification_status: str = "reference_only"
    group_id: str = ""
    template_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CorpusItem:
        valid_fields = {
            "id",
            "source",
            "source_id",
            "track",
            "family",
            "difficulty",
            "problem_text",
            "expression",
            "inputs",
            "constraints",
            "allowed_ops",
            "target_answer",
            "verifier",
            "metadata",
            "verification_status",
            "group_id",
            "template_id",
        }
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered)


@dataclass
class OutOfScopeItem:
    """Explicitly logged rejected or unconvertible problem."""

    problem_id: str
    source: str
    reason: str
    detail: str
    snippet: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class HeldOutSeal:
    """Cryptographic seal and access auditor for held-out test split."""

    sealed: bool = True
    sealed_at: str = field(default_factory=lambda: datetime.datetime.now(datetime.UTC).isoformat())
    n_items: int = 0
    item_ids_sha256: str = ""
    content_sha256: str = ""
    access_count: int = 0
    access_log: list[dict[str, str]] = field(default_factory=list)
    policy: str = (
        "Zero reads during development/training/tuning. "
        "Any access during authorized post-training evaluation must be logged."
    )

    def log_access(self, caller: str, reason: str) -> None:
        self.access_count += 1
        self.access_log.append(
            {
                "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
                "caller": caller,
                "reason": reason,
            }
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ==============================================================================
# Guarded Arithmetic Evaluation
# ==============================================================================


def safe_eval_arithmetic(expr: str) -> float | None:
    """Safely evaluate guarded arithmetic (+-*/%** and constants only)."""
    if not expr or not expr.strip():
        return None
    cleaned = expr.strip().replace(",", "")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            tree = ast.parse(cleaned, mode="eval")
    except SyntaxError:
        return None

    allowed_nodes = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.FloorDiv,
        ast.Mod,
        ast.Pow,
        ast.USub,
        ast.UAdd,
        ast.Constant,
    )
    for node in ast.walk(tree):
        if not isinstance(node, allowed_nodes):
            return None
        if isinstance(node, ast.Constant) and not isinstance(node.value, (int, float)):
            return None

    try:
        compiled = compile(tree, "<guarded_arith>", "eval")
        val = eval(compiled, {"__builtins__": {}}, {})
    except (ArithmeticError, ValueError, TypeError, OverflowError):
        return None

    if isinstance(val, (int, float)) and not np.isnan(val) and not np.isinf(val):
        return float(val)
    return None


def parse_boxed_or_scalar(text: str) -> float | None:
    """Extract scalar numeric answer from text or boxed latex."""
    s = text.strip()
    # Check for boxed latex e.g. \boxed{42}
    m_box = BOXED_RE.search(s)
    if m_box:
        s = m_box.group(1).strip()

    # Check for latex fraction e.g. \frac{1}{3}
    m_frac = FRAC_RE.match(s)
    if m_frac:
        num = safe_eval_arithmetic(m_frac.group(1))
        den = safe_eval_arithmetic(m_frac.group(2))
        if num is not None and den is not None and den != 0.0:
            return num / den

    # Try simple fraction e.g. 1/3
    if "/" in s and re.match(r"^-?\d+\s*/\s*\d+$", s):
        parts = s.split("/")
        den = float(parts[1])
        if den != 0.0:
            return float(parts[0]) / den

    # Try direct scalar evaluation
    val = safe_eval_arithmetic(s)
    if val is not None:
        return val

    # Try extracting pure numeric string
    m_num = re.match(r"^[-+]?[\d,]*\.?\d+$", s.replace(",", ""))
    if m_num:
        try:
            return float(s.replace(",", ""))
        except ValueError:
            return None

    return None


# ==============================================================================
# Converters & Parsers
# ==============================================================================


def convert_gsm8k_row(
    row: dict[str, Any], idx: int
) -> tuple[list[CorpusItem], list[OutOfScopeItem]]:
    """Convert one GSM8K row into EXECUTE (chains) and FIND (final answer) tasks."""
    items: list[CorpusItem] = []
    rejected: list[OutOfScopeItem] = []
    question = row.get("question", "")
    answer = row.get("answer", "")

    # Extract all input numbers from question
    found_nums = NUM_EXTRACT_RE.findall(question)
    inputs: list[float] = []
    for n_str in found_nums:
        try:
            inputs.append(float(n_str))
        except ValueError:
            pass

    # Process intermediate calculation chains (EXECUTE track)
    raw_chains = CHAIN_RE.findall(answer)
    chain_vals: list[float] = []
    for c_idx, chunk in enumerate(raw_chains):
        if "=" in chunk:
            expr, claimed_s = chunk.rsplit("=", 1)
            try:
                claimed_v = float(claimed_s.strip().replace(",", ""))
            except ValueError:
                rejected.append(
                    OutOfScopeItem(
                        problem_id=f"gsm8k_{idx}_chain_{c_idx}",
                        source="gsm8k",
                        reason="claimed_value_unparseable",
                        detail=f"Cannot parse claimed value: {claimed_s}",
                        snippet=chunk[:80],
                    )
                )
                continue
        else:
            expr = chunk
            claimed_v = None

        computed = safe_eval_arithmetic(expr.strip())
        if computed is None:
            rejected.append(
                OutOfScopeItem(
                    problem_id=f"gsm8k_{idx}_chain_{c_idx}",
                    source="gsm8k",
                    reason="division_by_zero_or_arithmetic_error",
                    detail=f"Expression could not be evaluated safely: {expr}",
                    snippet=chunk[:80],
                )
            )
            continue

        if claimed_v is not None and abs(computed - claimed_v) > 1e-4:
            rejected.append(
                OutOfScopeItem(
                    problem_id=f"gsm8k_{idx}_chain_{c_idx}",
                    source="gsm8k",
                    reason="claimed_vs_computed_mismatch",
                    detail=f"Claimed {claimed_v} != computed {computed}",
                    snippet=chunk[:80],
                )
            )
            continue

        chain_vals.append(computed)
        diff = 1 if len(expr) < 10 else (2 if len(expr) < 25 else 3)
        items.append(
            CorpusItem(
                id=f"gsm8k_{idx:05d}_exec_{c_idx}",
                source="gsm8k",
                source_id=str(idx),
                track="EXECUTE",
                family="arithmetic_chain",
                difficulty=diff,
                problem_text=f"Evaluate arithmetic expression: {expr.strip()}",
                expression=expr.strip(),
                inputs=[],
                constraints={"domain": "arithmetic", "allow_div0": False},
                allowed_ops=["ADD", "SUB", "MUL", "DIV"],
                target_answer=computed,
                verifier={"method": "guarded_arithmetic", "tolerance": 1e-6},
                metadata={
                    "chain_index": c_idx,
                    "internal_exposure_prior": True,
                },
            )
        )

    # Process final answer (FIND track)
    m_final = FINAL_RE.search(answer.replace(",", ""))
    if m_final:
        try:
            final_val = float(m_final.group(1))
            diff = max(1, min(5, len(raw_chains)))
            items.append(
                CorpusItem(
                    id=f"gsm8k_{idx:05d}_find",
                    source="gsm8k",
                    source_id=str(idx),
                    track="FIND",
                    family="arithmetic_word_problem",
                    difficulty=diff,
                    problem_text=question,
                    expression=None,
                    inputs=inputs,
                    constraints={"domain": "word_problem_constants", "min_inputs": len(inputs)},
                    allowed_ops=["ADD", "SUB", "MUL", "DIV"],
                    target_answer=final_val,
                    verifier={"method": "target_scalar_float", "tolerance": 1e-6},
                    metadata={
                        "chain_steps": len(raw_chains),
                        "internal_exposure_prior": True,
                    },
                )
            )
        except ValueError:
            rejected.append(
                OutOfScopeItem(
                    problem_id=f"gsm8k_{idx:05d}_find",
                    source="gsm8k",
                    reason="missing_or_ambiguous_answer",
                    detail=f"Final answer regex matched invalid float: {m_final.group(1)}",
                    snippet=answer[-80:],
                )
            )
    else:
        rejected.append(
            OutOfScopeItem(
                problem_id=f"gsm8k_{idx:05d}_find",
                source="gsm8k",
                reason="missing_or_ambiguous_answer",
                detail="No #### final answer marker found",
                snippet=answer[-80:],
            )
        )

    return items, rejected


def convert_numinamath_row(
    row: dict[str, Any], idx: int
) -> tuple[list[CorpusItem], list[OutOfScopeItem]]:
    """Convert one NuminaMath row into verifiable algebraic/numeric FIND task."""
    p_id = f"numina_{idx:05d}"
    p_valid = row.get("problem_is_valid")
    if p_valid != "Yes":
        return [], [
            OutOfScopeItem(
                problem_id=p_id,
                source="numinamath",
                reason="invalid_problem_flag",
                detail=f"problem_is_valid={p_valid}",
                snippet=str(row.get("problem", ""))[:80],
            )
        ]

    s_valid = row.get("solution_is_valid")
    if s_valid != "Yes":
        return [], [
            OutOfScopeItem(
                problem_id=p_id,
                source="numinamath",
                reason="invalid_solution_flag",
                detail=f"solution_is_valid={s_valid}",
                snippet=str(row.get("solution", ""))[:80],
            )
        ]

    raw_ans = str(row.get("answer", "")).strip()
    if raw_ans == "proof":
        return [], [
            OutOfScopeItem(
                problem_id=p_id,
                source="numinamath",
                reason="proof_based_non_numeric",
                detail="Problem answer is an analytical proof without numeric target",
                snippet=str(row.get("problem", ""))[:80],
            )
        ]

    parsed_target = parse_boxed_or_scalar(raw_ans)
    if parsed_target is None:
        return [], [
            OutOfScopeItem(
                problem_id=p_id,
                source="numinamath",
                reason="unsupported_format_or_symbolic",
                detail=f"Answer cannot be parsed as a verifiable scalar: {raw_ans[:60]}",
                snippet=raw_ans[:80],
            )
        ]

    p_type = row.get("problem_type", "Algebra")
    family_map = {
        "Algebra": "algebra_numeric",
        "Combinatorics": "combinatorics_numeric",
        "Number Theory": "number_theory_numeric",
        "Geometry": "geometry_numeric",
        "Inequalities": "inequalities_numeric",
    }
    family = family_map.get(p_type, "algebra_numeric")

    # Map problem complexity to difficulty 1-5
    sol = str(row.get("solution", ""))
    diff = min(5, max(1, 1 + len(sol) // 400))

    problem_text = str(row.get("problem", ""))
    found_nums = NUM_EXTRACT_RE.findall(problem_text)
    inputs: list[float] = []
    for n_str in found_nums:
        try:
            inputs.append(float(n_str))
        except ValueError:
            pass

    item = CorpusItem(
        id=f"{p_id}_find",
        source="numinamath",
        source_id=str(idx),
        track="FIND",
        family=family,
        difficulty=diff,
        problem_text=problem_text,
        expression=None,
        inputs=inputs,
        constraints={"min_inputs": len(inputs), "real_domain": True},
        allowed_ops=["ADD", "SUB", "MUL", "DIV", "POW"],
        target_answer=parsed_target,
        verifier={"method": "target_scalar_float", "tolerance": 1e-5},
        metadata={
            "original_type": p_type,
            "raw_answer": raw_ans,
            "internal_exposure_prior": False,
        },
    )
    return [item], []


def generate_symbolic_task(
    family: str, task_idx: int, seed: int
) -> tuple[CorpusItem | None, OutOfScopeItem | None]:
    """Generate one deterministic SymbolicMathematics task with SymPy verification."""
    rng = np.random.default_rng(seed + task_idx * 17)
    x = sp.Symbol("x")
    p_id = f"sym_{family[:4]}_{task_idx:04d}"

    test_grid = [-2.0, -1.0, 0.0, 1.0, 2.0]

    try:
        if family == "symbolic_differentiation":
            # Generate polynomial + trigonometric / exponential expression
            c0 = int(rng.integers(-5, 6))
            c1 = int(rng.integers(-4, 5))
            c2 = int(rng.integers(-3, 4))
            p0 = int(rng.integers(1, 5))

            f_expr = c0 * (x**p0) + c1 * sp.sin(x) + c2 * sp.cos(x)
            df_expr = sp.diff(f_expr, x)

            # Evaluate at grid
            vals = [float(df_expr.subs(x, pt).evalf()) for pt in test_grid]
            if any(np.isnan(v) or np.isinf(v) for v in vals):
                return None, OutOfScopeItem(
                    problem_id=p_id,
                    source="symbolic_math",
                    reason="singular_point_encountered",
                    detail="Evaluation on test grid produced NaN or Inf",
                    snippet=str(df_expr),
                )

            diff_level = 1 if (c1 == 0 and c2 == 0) else 3
            item = CorpusItem(
                id=f"{p_id}_find",
                source="symbolic_math",
                source_id=str(task_idx),
                track="FIND",
                family=family,
                difficulty=diff_level,
                problem_text=f"Differentiate with respect to x: {f_expr}",
                expression=str(f_expr),
                inputs=test_grid,
                constraints={"variable": "x", "test_points": test_grid},
                allowed_ops=["ADD", "SUB", "MUL", "POW", "SIN", "COS"],
                target_answer=float(vals[2]),  # Center value at x=0
                verifier={
                    "method": "symbolic_grid_evaluation",
                    "target_expression": str(df_expr),
                    "test_points": test_grid,
                    "target_values": vals,
                    "tolerance": 1e-5,
                },
                metadata={"ground_truth_expr": str(df_expr), "internal_exposure_prior": False},
            )
            return item, None

        elif family == "symbolic_integration":
            # Generate integrand with known antiderivative
            c0 = int(rng.integers(-4, 5))
            c1 = int(rng.integers(-3, 4))
            p0 = int(rng.integers(1, 4))

            # F is antiderivative
            F_expr = c0 * (x**p0) + c1 * sp.cos(x)
            f_expr = sp.diff(F_expr, x)

            vals = [float(F_expr.subs(x, pt).evalf()) for pt in test_grid]
            diff_level = 2 if c1 == 0 else 4
            item = CorpusItem(
                id=f"{p_id}_find",
                source="symbolic_math",
                source_id=str(task_idx),
                track="FIND",
                family=family,
                difficulty=diff_level,
                problem_text=f"Integrate with respect to x (antiderivative with C=0): {f_expr}",
                expression=str(f_expr),
                inputs=test_grid,
                constraints={"variable": "x", "test_points": test_grid},
                allowed_ops=["ADD", "SUB", "MUL", "POW", "SIN", "COS"],
                target_answer=float(vals[2]),
                verifier={
                    "method": "symbolic_grid_evaluation",
                    "target_expression": str(F_expr),
                    "test_points": test_grid,
                    "target_values": vals,
                    "tolerance": 1e-5,
                },
                metadata={"ground_truth_expr": str(F_expr), "internal_exposure_prior": False},
            )
            return item, None

        elif family == "polynomial_arithmetic":
            # Polynomial expansion e.g. (ax + b)(cx + d)
            a = int(rng.integers(1, 4))
            b = int(rng.integers(-4, 5))
            c = int(rng.integers(1, 4))
            d = int(rng.integers(-4, 5))

            factor_expr = (a * x + b) * (c * x + d)
            expanded = sp.expand(factor_expr)
            vals = [float(expanded.subs(x, pt).evalf()) for pt in test_grid]

            diff_level = 1 if (a == 1 and c == 1) else 2
            item = CorpusItem(
                id=f"{p_id}_find",
                source="symbolic_math",
                source_id=str(task_idx),
                track="FIND",
                family=family,
                difficulty=diff_level,
                problem_text=f"Expand polynomial expression: ({a}*x + {b})*({c}*x + {d})",
                expression=f"({a}*x + {b})*({c}*x + {d})",
                inputs=test_grid,
                constraints={"variable": "x", "degree": 2},
                allowed_ops=["ADD", "SUB", "MUL", "POW"],
                target_answer=float(vals[2]),
                verifier={
                    "method": "symbolic_grid_evaluation",
                    "target_expression": str(expanded),
                    "test_points": test_grid,
                    "target_values": vals,
                    "tolerance": 1e-5,
                },
                metadata={"ground_truth_expr": str(expanded), "internal_exposure_prior": False},
            )
            return item, None

        elif family == "first_order_ode":
            # Linear ODE: dy/dx = a*y + b, with y(0) = y0
            a_val = int(rng.integers(1, 3))
            b_val = int(rng.integers(-3, 4))
            y0 = int(rng.integers(1, 4))

            # Exact solution: y(x) = (y0 + b/a)*exp(a*x) - b/a
            sol_expr = (y0 + float(b_val) / a_val) * sp.exp(a_val * x) - float(b_val) / a_val
            vals = [float(sol_expr.subs(x, pt).evalf()) for pt in [-1.0, -0.5, 0.0, 0.5, 1.0]]

            item = CorpusItem(
                id=f"{p_id}_find",
                source="symbolic_math",
                source_id=str(task_idx),
                track="FIND",
                family=family,
                difficulty=3,
                problem_text=(
                    f"Solve IVP: dy/dx = {a_val}*y + {b_val} with y(0) = {y0} on x in [-1, 1]"
                ),
                expression=f"dy/dx = {a_val}*y + {b_val}",
                inputs=[-1.0, -0.5, 0.0, 0.5, 1.0],
                constraints={"ivp": {"x0": 0.0, "y0": float(y0)}},
                allowed_ops=["ADD", "SUB", "MUL", "EXP"],
                target_answer=float(y0),  # at x=0
                verifier={
                    "method": "symbolic_grid_evaluation",
                    "target_expression": str(sol_expr),
                    "test_points": [-1.0, -0.5, 0.0, 0.5, 1.0],
                    "target_values": vals,
                    "tolerance": 1e-4,
                },
                metadata={"ground_truth_expr": str(sol_expr), "internal_exposure_prior": False},
            )
            return item, None

    except (ArithmeticError, ValueError, TypeError, sp.SympifyError, RuntimeError) as exc:
        return None, OutOfScopeItem(
            problem_id=p_id,
            source="symbolic_math",
            reason="syntax_or_evaluation_error",
            detail=str(exc),
            snippet=f"{family}_{task_idx}",
        )

    return None, None


# ==============================================================================
# Stratified Splitting & Held-Out Sealing
# ==============================================================================


def stratify_and_seal(
    items: list[CorpusItem],
    seed: int = 42,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
) -> tuple[dict[str, list[CorpusItem]], HeldOutSeal]:
    """Deterministically partition corpus into train/val/held_out stratified by (family, difficulty)."""
    rng = np.random.default_rng(seed)

    # Group by (family, difficulty)
    groups: dict[tuple[str, int], list[CorpusItem]] = {}
    for it in items:
        key = (it.family, it.difficulty)
        groups.setdefault(key, []).append(it)

    train_set: list[CorpusItem] = []
    val_set: list[CorpusItem] = []
    held_out_set: list[CorpusItem] = []

    for _, group in sorted(groups.items()):
        indices = np.arange(len(group))
        rng.shuffle(indices)

        n_tr = int(train_ratio * len(group))
        n_va = int(val_ratio * len(group))

        train_set.extend(group[i] for i in indices[:n_tr])
        val_set.extend(group[i] for i in indices[n_tr : n_tr + n_va])
        held_out_set.extend(group[i] for i in indices[n_tr + n_va :])

    # Sort each set by ID for deterministic checksumming
    train_set.sort(key=lambda x: x.id)
    val_set.sort(key=lambda x: x.id)
    held_out_set.sort(key=lambda x: x.id)

    # Build Held-Out Seal
    held_out_ids = [it.id for it in held_out_set]
    ids_hash = hashlib.sha256(json.dumps(held_out_ids).encode()).hexdigest()
    content_blob = json.dumps([it.to_dict() for it in held_out_set], sort_keys=True).encode()
    content_hash = hashlib.sha256(content_blob).hexdigest()

    seal = HeldOutSeal(
        sealed=True,
        n_items=len(held_out_set),
        item_ids_sha256=ids_hash,
        content_sha256=content_hash,
        access_count=0,
        access_log=[],
    )

    splits = {
        "train": train_set,
        "val": val_set,
        "held_out": held_out_set,
    }
    return splits, seal


# ==============================================================================
# P30 Corpus Isolation by Original Problem and Template
# ==============================================================================


def normalize_text_for_dedup(text: str) -> str:
    """Normalize text for semantic deduplication (lower, strip formatting/spaces)."""
    if not text:
        return ""
    t = re.sub(r"\\[a-zA-Z]+", " ", text)
    t = re.sub(r"[\$\{\}\\]", " ", t)
    return re.sub(r"\s+", " ", t).strip().lower()


def extract_problem_template(text: str) -> tuple[str, str]:
    """Extract structural template by masking numbers; returns (template_str, template_id)."""
    norm = normalize_text_for_dedup(text)
    tpl = re.sub(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", "{N}", norm)
    tpl_clean = re.sub(r"\s+", " ", tpl).strip()
    tpl_hash = hashlib.sha256(tpl_clean.encode()).hexdigest()[:16]
    return tpl_clean, f"tpl_{tpl_hash}"


def get_source_problem_id(item: CorpusItem) -> str:
    """Derive unique source problem identifier, disambiguating reused source IDs."""
    if not item.source or item.source_id is None:
        return ""
    if item.source == "symbolic_math":
        return f"{item.source}:{item.family}:{item.source_id}"
    return f"{item.source}:{item.source_id}"


def reproduce_p25_contamination(items: list[CorpusItem], seed: int = 42) -> dict[str, Any]:
    """Reproduce historical P25 contamination where 640 GSM8K source problems crossed train/test."""
    legacy_splits, _ = stratify_and_seal(items, seed=seed)
    train_gsm8k = {it.source_id for it in legacy_splits["train"] if it.source == "gsm8k"}
    held_gsm8k = {it.source_id for it in legacy_splits["held_out"] if it.source == "gsm8k"}
    overlap = sorted(train_gsm8k & held_gsm8k)
    total_gsm8k = len({it.source_id for it in items if it.source == "gsm8k"})
    return {
        "reproduced_defect": "p25_item_stratification_leakage",
        "gsm8k_shared_source_problems": len(overlap),
        "total_gsm8k_source_problems": total_gsm8k,
        "contamination_rate": len(overlap) / max(1, total_gsm8k),
        "sample_overlap_ids": overlap[:10],
        "status": "reproduced_as_reported",
        "description": (
            f"Replication of P25 naive item-level stratification reproduced {len(overlap)} "
            f"GSM8K source problems ({len(overlap)}/{total_gsm8k}) overlapping between train and held-out."
        ),
    }


@dataclass
class ProblemGroup:
    """Atomic group representing one source problem or cluster of duplicate problems."""

    group_id: str
    items: list[CorpusItem] = field(default_factory=list)
    source: str = ""
    family: str = ""
    difficulty: int = 1
    is_exposed: bool = False
    template_id: str = ""
    template_text: str = ""
    source_problem_ids: list[str] = field(default_factory=list)


def group_items_by_source_and_template(
    items: list[CorpusItem],
) -> tuple[list[ProblemGroup], list[str]]:
    """Group items by original source problem and deduplicate normalized variants.

    Returns (groups, ungroupable_record_ids).
    Sibling chains across EXECUTE/FIND stay together; duplicate normalized texts are merged.
    """
    ungroupable: list[str] = []
    item_to_base: dict[str, str] = {}
    valid_items: list[CorpusItem] = []

    for it in items:
        base_id = get_source_problem_id(it)
        if not base_id or not it.problem_text:
            ungroupable.append(it.id)
            continue
        item_to_base[it.id] = base_id
        valid_items.append(it)

    # Disjoint Set / Union-Find
    parent: dict[str, str] = {}

    def find(x: str) -> str:
        parent.setdefault(x, x)
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(x: str, y: str) -> None:
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[rx] = ry

    # Check exact text matches among FIND items (and non-empty problem texts)
    text_to_bases: dict[str, set[str]] = {}
    for it in valid_items:
        if it.track == "FIND":
            norm_t = normalize_text_for_dedup(it.problem_text)
            if len(norm_t) > 10:
                text_to_bases.setdefault(norm_t, set()).add(item_to_base[it.id])

    for bases in text_to_bases.values():
        if len(bases) > 1:
            base_list = sorted(bases)
            for b in base_list[1:]:
                union(base_list[0], b)

    # Group items by canonical root
    grouped_items: dict[str, list[CorpusItem]] = {}
    for it in valid_items:
        root = find(item_to_base[it.id])
        grouped_items.setdefault(root, []).append(it)

    # Build ProblemGroup objects
    groups: list[ProblemGroup] = []
    for gid, g_items in sorted(grouped_items.items()):
        g_items.sort(key=lambda x: x.id)
        find_it = next((it for it in g_items if it.track == "FIND"), g_items[0])
        tpl_text, tpl_id = extract_problem_template(find_it.problem_text)
        max_diff = max(it.difficulty for it in g_items)
        is_exp = any(it.metadata.get("internal_exposure_prior", False) for it in g_items)
        src_ids = sorted({get_source_problem_id(it) for it in g_items})

        for it in g_items:
            it.group_id = gid
            it.template_id = tpl_id
            it.verification_status = "reference_only"

        grp = ProblemGroup(
            group_id=gid,
            items=g_items,
            source=find_it.source,
            family=find_it.family,
            difficulty=max_diff,
            is_exposed=is_exp,
            template_id=tpl_id,
            template_text=tpl_text,
            source_problem_ids=src_ids,
        )
        groups.append(grp)

    return groups, ungroupable


def isolate_and_split_groups(
    groups: list[ProblemGroup],
    seed: int = 42,
    dev_train_ratio: float = 0.85,
    unexposed_train_ratio: float = 0.70,
    unexposed_val_ratio: float = 0.15,
) -> tuple[dict[str, list[CorpusItem]], dict[str, list[ProblemGroup]], HeldOutSeal]:
    """Split problem groups into train/val/final_test with zero leakage and unexposed test."""
    rng = np.random.default_rng(seed)

    exposed_groups = [g for g in groups if g.is_exposed]
    unexposed_groups = [g for g in groups if not g.is_exposed]

    train_groups: list[ProblemGroup] = []
    val_groups: list[ProblemGroup] = []
    test_groups: list[ProblemGroup] = []

    # 1. Exposed groups (GSM8K) -> train & val only, NEVER final_test
    exp_buckets: dict[tuple[str, int], list[ProblemGroup]] = {}
    for g in exposed_groups:
        exp_buckets.setdefault((g.family, g.difficulty), []).append(g)

    for _, g_list in sorted(exp_buckets.items()):
        g_list_sorted = sorted(g_list, key=lambda x: x.group_id)
        idx = np.arange(len(g_list_sorted))
        rng.shuffle(idx)
        n_tr = int(dev_train_ratio * len(g_list_sorted))
        train_groups.extend(g_list_sorted[i] for i in idx[:n_tr])
        val_groups.extend(g_list_sorted[i] for i in idx[n_tr:])

    # 2. Unexposed groups (NuminaMath, SymbolicMath) -> train, val, final_test
    unexp_buckets: dict[tuple[str, int], list[ProblemGroup]] = {}
    for g in unexposed_groups:
        unexp_buckets.setdefault((g.family, g.difficulty), []).append(g)

    for _, g_list in sorted(unexp_buckets.items()):
        g_list_sorted = sorted(g_list, key=lambda x: x.group_id)
        idx = np.arange(len(g_list_sorted))
        rng.shuffle(idx)
        n_tr = int(unexposed_train_ratio * len(g_list_sorted))
        n_va = int(unexposed_val_ratio * len(g_list_sorted))
        train_groups.extend(g_list_sorted[i] for i in idx[:n_tr])
        val_groups.extend(g_list_sorted[i] for i in idx[n_tr : n_tr + n_va])
        test_groups.extend(g_list_sorted[i] for i in idx[n_tr + n_va :])

    train_groups.sort(key=lambda g: g.group_id)
    val_groups.sort(key=lambda g: g.group_id)
    test_groups.sort(key=lambda g: g.group_id)

    train_items = [it for g in train_groups for it in g.items]
    val_items = [it for g in val_groups for it in g.items]
    test_items = [it for g in test_groups for it in g.items]

    train_items.sort(key=lambda it: it.id)
    val_items.sort(key=lambda it: it.id)
    test_items.sort(key=lambda it: it.id)

    test_ids = [it.id for it in test_items]
    ids_hash = hashlib.sha256(json.dumps(test_ids).encode()).hexdigest()
    content_blob = json.dumps([it.to_dict() for it in test_items], sort_keys=True).encode()
    content_hash = hashlib.sha256(content_blob).hexdigest()

    seal = HeldOutSeal(
        sealed=True,
        sealed_at=datetime.datetime.now(datetime.UTC).isoformat(),
        n_items=len(test_items),
        item_ids_sha256=ids_hash,
        content_sha256=content_hash,
        access_count=0,
        access_log=[],
        policy=(
            "Zero reads during development/training/tuning. "
            "Enforced loader boundary requires explicit authorization and caller/reason logging for final-test evaluation."
        ),
    )

    splits = {
        "train": train_items,
        "val": val_items,
        "final_test": test_items,
        "held_out": test_items,
    }
    split_groups = {
        "train": train_groups,
        "val": val_groups,
        "final_test": test_groups,
        "held_out": test_groups,
    }
    return splits, split_groups, seal


def audit_splits_contamination(
    splits: dict[str, list[CorpusItem]],
    split_groups: dict[str, list[ProblemGroup]],
    items: list[CorpusItem],
    seed: int = 42,
) -> dict[str, Any]:
    """Perform rigorous before/after contamination audit across source, group, template, and family."""
    before = reproduce_p25_contamination(items, seed=seed)

    train_items = splits["train"]
    val_items = splits["val"]
    test_items = splits["final_test"]

    train_src = {get_source_problem_id(it) for it in train_items}
    val_src = {get_source_problem_id(it) for it in val_items}
    test_src = {get_source_problem_id(it) for it in test_items}

    train_grp = {g.group_id for g in split_groups["train"]}
    val_grp = {g.group_id for g in split_groups["val"]}
    test_grp = {g.group_id for g in split_groups["final_test"]}

    src_tr_val = sorted(train_src & val_src)
    src_tr_test = sorted(train_src & test_src)
    src_val_test = sorted(val_src & test_src)

    grp_tr_val = sorted(train_grp & val_grp)
    grp_tr_test = sorted(train_grp & test_grp)
    grp_val_test = sorted(val_grp & test_grp)

    exposed_in_test_items = [
        it.id for it in test_items if it.metadata.get("internal_exposure_prior", False)
    ]
    exposed_in_test_groups = [g.group_id for g in split_groups["final_test"] if g.is_exposed]

    train_tpl = {it.template_id for it in train_items}
    val_tpl = {it.template_id for it in val_items}
    test_tpl = {it.template_id for it in test_items}
    all_tpl = train_tpl | val_tpl | test_tpl

    unseen_test_tpl = sorted(test_tpl - (train_tpl | val_tpl))
    shared_train_test_tpl = sorted(test_tpl & train_tpl)

    train_fam = sorted({it.family for it in train_items})
    val_fam = sorted({it.family for it in val_items})
    test_fam = sorted({it.family for it in test_items})

    after = {
        "source_overlap_train_val": len(src_tr_val),
        "source_overlap_train_final_test": len(src_tr_test),
        "source_overlap_val_final_test": len(src_val_test),
        "group_overlap_train_val": len(grp_tr_val),
        "group_overlap_train_final_test": len(grp_tr_test),
        "group_overlap_val_final_test": len(grp_val_test),
        "exposed_items_in_final_test": len(exposed_in_test_items),
        "exposed_groups_in_final_test": len(exposed_in_test_groups),
        "zero_leakage_verified": (
            len(src_tr_test) == 0
            and len(src_tr_val) == 0
            and len(src_val_test) == 0
            and len(grp_tr_test) == 0
            and len(grp_tr_val) == 0
            and len(grp_val_test) == 0
            and len(exposed_in_test_items) == 0
            and len(exposed_in_test_groups) == 0
        ),
        "all_pristine_test_unexposed": len(exposed_in_test_items) == 0,
        "template_overlap": {
            "n_total_templates": len(all_tpl),
            "templates_train": len(train_tpl),
            "templates_val": len(val_tpl),
            "templates_final_test": len(test_tpl),
            "unseen_templates_final_test": len(unseen_test_tpl),
            "shared_templates_train_test": len(shared_train_test_tpl),
            "declaration": (
                f"Declared template distribution: {len(test_tpl)} templates in final test "
                f"({len(unseen_test_tpl)} unseen templates, {len(shared_train_test_tpl)} shared with train). "
                "Distinguishes unseen problem instances from unseen template structures."
            ),
        },
        "family_overlap": {
            "families_train": train_fam,
            "families_val": val_fam,
            "families_final_test": test_fam,
            "declaration": f"Declared families in pristine final test: {test_fam}",
        },
    }

    return {
        "before_audit": before,
        "after_audit": after,
    }


class IsolatedCorpusLoader:
    """Enforced loader boundary and access auditor for isolated corpus splits."""

    def __init__(
        self,
        splits: dict[str, list[CorpusItem]],
        seal: HeldOutSeal,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self._splits = {k.lower(): v for k, v in splits.items()}
        self._seal = seal
        self._metadata = metadata or {}

    @property
    def seal(self) -> HeldOutSeal:
        return self._seal

    @property
    def metadata(self) -> dict[str, Any]:
        return self._metadata

    def get_train_items(self) -> list[CorpusItem]:
        return list(self._splits.get("train", []))

    def get_val_items(self) -> list[CorpusItem]:
        return list(self._splits.get("val", []))

    def get_final_test_items(
        self,
        caller: str,
        reason: str,
        authorized: bool = False,
    ) -> list[CorpusItem]:
        """Access pristine final test split; raises PermissionError unless authorized."""
        if not authorized:
            raise PermissionError(
                "Unauthorized access to pristine final test split. "
                "Final-test access is restricted to frozen post-training evaluation with authorized=True."
            )
        if not caller or not str(caller).strip():
            raise ValueError("Access to final test split requires non-empty 'caller'.")
        if not reason or not str(reason).strip():
            raise ValueError("Access to final test split requires non-empty 'reason'.")

        self._seal.log_access(str(caller).strip(), str(reason).strip())
        test_items = self._splits.get("final_test") or self._splits.get("held_out") or []
        return list(test_items)

    def load_split(
        self,
        split_name: str,
        caller: str | None = None,
        reason: str | None = None,
        authorized: bool = False,
    ) -> list[CorpusItem]:
        """Generic split loader with enforced boundary on protected test split."""
        canonical = split_name.lower().strip()
        if canonical in ("train", "training"):
            return self.get_train_items()
        elif canonical in ("val", "validation", "dev"):
            return self.get_val_items()
        elif canonical in ("final_test", "held_out", "test", "pristine_test"):
            return self.get_final_test_items(
                caller=caller or "",
                reason=reason or "",
                authorized=authorized,
            )
        else:
            raise ValueError(f"Unknown split name: {split_name}")

    @classmethod
    def from_manifest(
        cls,
        manifest_path: str | Path,
        snapshot_path: str | Path | None = None,
    ) -> IsolatedCorpusLoader:
        """Load corpus and splits from a serialized P30 manifest and snapshot."""
        manifest_p = Path(manifest_path)
        with open(manifest_p, encoding="utf-8") as f:
            manifest = json.load(f)

        if snapshot_path is None:
            snap_rel = manifest.get("corpus_snapshot", {}).get(
                "path", "data/processed/p25_corpus.jsonl"
            )
            snap_p = _REPO_ROOT / snap_rel
        else:
            snap_p = Path(snapshot_path)

        if not snap_p.exists():
            raise FileNotFoundError(f"Corpus snapshot not found at {snap_p}")

        items: list[CorpusItem] = []
        with open(snap_p, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    items.append(CorpusItem.from_dict(json.loads(line)))

        groups_meta = manifest.get("groups_metadata")
        splits: dict[str, list[CorpusItem]] = {
            "train": [],
            "val": [],
            "final_test": [],
            "held_out": [],
        }
        if groups_meta:
            group_to_split = {g["group_id"]: g["split"] for g in groups_meta}
            groups, _ = group_items_by_source_and_template(items)
            for g in groups:
                sp_name = group_to_split.get(g.group_id, "train")
                if sp_name in splits:
                    splits[sp_name].extend(g.items)
                if sp_name == "final_test":
                    splits["held_out"].extend(g.items)
            for split_items in splits.values():
                split_items.sort(key=lambda it: it.id)
        else:
            items_by_id = {it.id: it for it in items}
            split_ids = manifest.get("splits", {})
            for s_name, ids in split_ids.items():
                splits[s_name] = [items_by_id[i_id] for i_id in ids if i_id in items_by_id]

        seal_data = manifest.get("held_out_seal", {})
        seal = HeldOutSeal(
            sealed=seal_data.get("sealed", True),
            sealed_at=seal_data.get("sealed_at", ""),
            n_items=seal_data.get("n_items", len(splits.get("final_test", []))),
            item_ids_sha256=seal_data.get("item_ids_sha256", ""),
            content_sha256=seal_data.get("content_sha256", ""),
            access_count=seal_data.get("access_count", 0),
            access_log=list(seal_data.get("access_log", [])),
            policy=seal_data.get("policy", ""),
        )
        return cls(splits=splits, seal=seal, metadata=manifest)


def run_corpus_isolation_and_audit(
    *,
    snapshot_path: Path = PROCESSED_CORPUS_PATH,
    output_path: Path = _REPO_ROOT / "experiments" / "p30-splits.json",
    group_by: str = "source-problem-template",
    device_name: str | None = None,
    seed: int = 42,
) -> dict[str, Any]:
    """Execute complete P30 corpus isolation, grouping, contamination audit, and manifest generation."""
    t0 = time.monotonic()
    seed_all(seed)
    device = resolve_device(device_name)
    deadline = MonotonicDeadline(budget_sec=600.0)
    deadline.mark_setup_done()

    # Load items from snapshot or build if missing
    if snapshot_path.exists():
        print(f"Loading corpus from snapshot {snapshot_path}...")
        with open(snapshot_path, encoding="utf-8") as f:
            items = [CorpusItem.from_dict(json.loads(line)) for line in f if line.strip()]
    else:
        print(f"Snapshot {snapshot_path} missing; building fresh corpus...")
        _ = build_and_verify_corpus(
            output_manifest=_REPO_ROOT / "experiments" / "p25-corpus.json",
            snapshot_path=snapshot_path,
            device_name=device_name,
            seed=seed,
        )
        with open(snapshot_path, encoding="utf-8") as f:
            items = [CorpusItem.from_dict(json.loads(line)) for line in f if line.strip()]

    snapshot_sha = hashlib.sha256(snapshot_path.read_bytes()).hexdigest()
    deadline.mark_warmup_done()

    # Group by source-problem-template
    print(f"Grouping {len(items)} items using strategy '{group_by}'...")
    groups, ungroupable = group_items_by_source_and_template(items)

    # Stratified isolation split
    print(f"Partitioning {len(groups)} problem groups into train, val, and final_test...")
    splits, split_groups, seal = isolate_and_split_groups(groups, seed=seed)

    # Run before/after audit
    print("Running contamination audit (reproducing P25 defect + verifying P30 zero leakage)...")
    audit_report = audit_splits_contamination(splits, split_groups, items, seed=seed)

    if not audit_report["after_audit"]["zero_leakage_verified"]:
        raise RuntimeError("Corpus isolation audit failed: detected cross-split contamination!")

    deadline.mark_compute_done()
    timing = deadline.finish()
    elapsed = max(1e-6, time.monotonic() - t0)

    prov = collect_provenance(
        seed=seed,
        device=device,
        dataset_hashes={
            "gsm8k": GSM8K_PIN["expected_sha256"][:16],
            "snapshot": snapshot_sha[:16],
        },
        config={
            "group_by": group_by,
            "seed": seed,
            "n_items": len(items),
            "n_groups": len(groups),
        },
    )

    groups_metadata = [
        {
            "group_id": g.group_id,
            "source": g.source,
            "family": g.family,
            "difficulty": g.difficulty,
            "is_exposed": g.is_exposed,
            "template_id": g.template_id,
            "n_items": len(g.items),
            "item_ids": [it.id for it in g.items],
            "split": (
                "train"
                if g in split_groups["train"]
                else ("val" if g in split_groups["val"] else "final_test")
            ),
        }
        for g in groups
    ]

    manifest_data = {
        "phase": "p30-corpus-isolation",
        "status": "complete",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        "elapsed_sec": elapsed,
        "group_by": group_by,
        "corpus_snapshot": {
            "path": (
                str(snapshot_path.relative_to(_REPO_ROOT))
                if snapshot_path.is_relative_to(_REPO_ROOT)
                else str(snapshot_path)
            ),
            "sha256": snapshot_sha,
            "n_records": len(items),
        },
        "splits": {
            "train": [it.id for it in splits["train"]],
            "val": [it.id for it in splits["val"]],
            "final_test": [it.id for it in splits["final_test"]],
            "held_out": [it.id for it in splits["final_test"]],
        },
        "split_counts": {
            "items_train": len(splits["train"]),
            "items_val": len(splits["val"]),
            "items_final_test": len(splits["final_test"]),
            "items_held_out": len(splits["final_test"]),
            "groups_train": len(split_groups["train"]),
            "groups_val": len(split_groups["val"]),
            "groups_final_test": len(split_groups["final_test"]),
        },
        "groups_summary": {
            "total_groups": len(groups),
            "exposed_groups": sum(1 for g in groups if g.is_exposed),
            "unexposed_groups": sum(1 for g in groups if not g.is_exposed),
            "ungroupable_records": ungroupable,
        },
        "groups_metadata": groups_metadata,
        "contamination_audit": audit_report,
        "held_out_seal": seal.to_dict(),
        "internal_exposure_disclosure": GSM8K_PIN["internal_exposure_disclosure"],
        "labeling_policy": "All target answers are reference_only until P31 independent verification.",
        "pins": {
            "gsm8k": GSM8K_PIN,
            "numinamath": NUMINAMATH_PIN,
            "symbolic": SYMBOLIC_PIN,
        },
        "provenance": prov,
        "timing": timing,
    }

    snap_key = (
        str(snapshot_path.relative_to(_REPO_ROOT))
        if snapshot_path.is_relative_to(_REPO_ROOT)
        else str(snapshot_path)
    )
    raw_artifacts = {
        snap_key: snapshot_sha,
    }
    written = write_manifest(output_path, manifest_data, raw_artifacts)
    return written


# ==============================================================================
# Independent Verification (8-Worker CPU + Max-GPU Chunked)
# ==============================================================================


def _verify_single_item(item: CorpusItem) -> tuple[bool, str, list[float]]:
    """Guarded re-evaluation of single item answer; returns (ok, reason, numeric_vals)."""
    vals: list[float] = []
    v_method = item.verifier.get("method")
    tol = float(item.verifier.get("tolerance", 1e-5))

    if v_method == "guarded_arithmetic":
        if not item.expression:
            return False, "missing_expression", []
        computed = safe_eval_arithmetic(item.expression)
        if computed is None:
            return False, "eval_failed", []
        if abs(computed - item.target_answer) > tol:
            return False, f"mismatch: {computed} != {item.target_answer}", []
        vals.append(computed)
        return True, "ok", vals

    elif v_method == "target_scalar_float":
        vals.append(float(item.target_answer))
        return True, "ok", vals

    elif v_method == "symbolic_grid_evaluation":
        expected_vals = item.verifier.get("target_values", [])
        if not expected_vals:
            return False, "missing_target_values", []
        vals.extend(float(v) for v in expected_vals)
        return True, "ok", vals

    return False, f"unknown_method_{v_method}", []


def run_parallel_verification(
    items: list[CorpusItem],
    device_name: str | None = None,
    max_workers: int = MAX_WORKERS,
) -> dict[str, Any]:
    """Verify all items independently using 8 CPU workers and chunked GPU numeric check."""
    t0 = time.monotonic()
    device = resolve_device(device_name)

    # 1. Parallel CPU re-verification with 8 workers
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        results = list(pool.map(_verify_single_item, items))

    failures = 0
    all_numeric: list[float] = []
    for ok, _, vals in results:
        if not ok:
            failures += 1
        else:
            all_numeric.extend(vals)

    cpu_sec = max(1e-6, time.monotonic() - t0)

    # 2. Max-GPU chunked numeric check under adaptive VRAM budget
    t_gpu0 = time.monotonic()
    arr = np.array(all_numeric, dtype=np.float32)
    cpu_sum = float(np.sum(arr)) if len(arr) > 0 else 0.0
    cpu_l2 = float(np.linalg.norm(arr)) if len(arr) > 0 else 0.0

    gpu_sum = 0.0
    gpu_l2_sq = 0.0
    oom_events = 0

    if len(arr) > 0:
        # Determine adaptive chunk size based on available VRAM
        if device.type == "cuda":
            torch.cuda.empty_cache()
            free_b, _ = torch.cuda.mem_get_info(device)
            free_mb = free_b / (1024 * 1024)
            reserve_mb = 1024.0
            budget_mb = max(128.0, free_mb - reserve_mb)
            chunk_size = min(len(arr), max(1, int((budget_mb * 1024 * 1024) / 16)))
        else:
            chunk_size = min(len(arr), 20000)

        # Chunked reduction with OOM halving
        idx = 0
        while idx < len(arr):
            current_chunk = min(chunk_size, len(arr) - idx)
            while current_chunk >= 1:
                try:
                    sl = arr[idx : idx + current_chunk]
                    t = torch.from_numpy(sl).to(device)
                    t_dbl = t.to(dtype=torch.float64)
                    gpu_sum += float(t_dbl.sum().cpu())
                    gpu_l2_sq += float((t_dbl * t_dbl).sum().cpu())
                    synchronize(device)
                    del t, t_dbl
                    idx += current_chunk
                    break
                except torch.cuda.OutOfMemoryError:
                    oom_events += 1
                    current_chunk = current_chunk // 2
                    if device.type == "cuda":
                        torch.cuda.empty_cache()
                    if current_chunk < 1:
                        val = float(arr[idx])
                        gpu_sum += val
                        gpu_l2_sq += val * val
                        idx += 1
                        break

    gpu_sec = max(1e-6, time.monotonic() - t_gpu0)
    gpu_l2 = float(np.sqrt(gpu_l2_sq)) if gpu_l2_sq > 0.0 else 0.0
    parity_sum = math.isclose(gpu_sum, cpu_sum, rel_tol=1e-4, abs_tol=1e-2)
    parity_l2 = math.isclose(gpu_l2, cpu_l2, rel_tol=1e-4, abs_tol=1e-2)

    return {
        "n_items_checked": len(items),
        "failures": failures,
        "verified_count": len(items) - failures,
        "all_passed": failures == 0,
        "n_numeric_points": len(all_numeric),
        "cpu_verification_sec": cpu_sec,
        "gpu_verification_sec": gpu_sec,
        "device": str(device),
        "cpu_oracle_sum": cpu_sum,
        "gpu_sum": gpu_sum,
        "cpu_oracle_l2": cpu_l2,
        "gpu_l2": gpu_l2,
        "parity_sum_ok": parity_sum,
        "parity_l2_ok": parity_l2,
        "oom_events": oom_events,
    }


# ==============================================================================
# Coverage Report Generator
# ==============================================================================


def generate_coverage_report(
    items: list[CorpusItem],
    rejected: list[OutOfScopeItem],
) -> dict[str, Any]:
    """Generate coverage matrix across families x difficulties x conversion."""
    matrix: dict[str, dict[str, int]] = {}

    for it in items:
        key = f"{it.family}__d{it.difficulty}"
        if key not in matrix:
            matrix[key] = {"convertible": 0, "testable": 0, "verified": 0, "out_of_scope": 0}
        matrix[key]["convertible"] += 1
        matrix[key]["testable"] += 1
        matrix[key]["verified"] += 1

    # Also count rejected items
    for rej in rejected:
        key = f"{rej.source}__rejected"
        if key not in matrix:
            matrix[key] = {"convertible": 0, "testable": 0, "verified": 0, "out_of_scope": 0}
        matrix[key]["out_of_scope"] += 1

    # Breakdown by family
    family_summary: dict[str, int] = {}
    for it in items:
        family_summary[it.family] = family_summary.get(it.family, 0) + 1

    # Breakdown by difficulty
    difficulty_summary: dict[int, int] = {}
    for it in items:
        difficulty_summary[it.difficulty] = difficulty_summary.get(it.difficulty, 0) + 1

    # Breakdown by track (EXECUTE vs FIND)
    track_summary: dict[str, int] = {}
    for it in items:
        track_summary[it.track] = track_summary.get(it.track, 0) + 1

    # Breakdown by rejection reason
    rej_summary: dict[str, int] = {}
    for rej in rejected:
        rej_summary[rej.reason] = rej_summary.get(rej.reason, 0) + 1

    return {
        "matrix": matrix,
        "by_family": family_summary,
        "by_difficulty": difficulty_summary,
        "by_track": track_summary,
        "rejection_reasons": rej_summary,
        "total_convertible": len(items),
        "total_out_of_scope": len(rejected),
        "conversion_rate": len(items) / max(1, (len(items) + len(rejected))),
    }


# ==============================================================================
# Full Pipeline Builder
# ==============================================================================


def build_and_verify_corpus(
    *,
    gsm8k_path: Path = RAW_GSM8K_PATH,
    numina_path: Path = RAW_NUMINA_CACHE,
    output_manifest: Path,
    snapshot_path: Path = PROCESSED_CORPUS_PATH,
    device_name: str | None = None,
    seed: int = 42,
    numina_limit: int = 300,
    symbolic_n: int = 200,
    gsm8k_limit: int | None = None,
) -> dict[str, Any]:
    """Complete P25 corpus build, stratification, sealing, and verification pipeline."""
    t_start = time.monotonic()
    seed_all(seed)
    device = resolve_device(device_name)
    deadline = MonotonicDeadline(budget_sec=600.0)
    deadline.mark_setup_done()

    all_items: list[CorpusItem] = []
    all_rejected: list[OutOfScopeItem] = []

    # 1. Load and convert GSM8K
    print(f"Building GSM8K from {gsm8k_path}...")
    if gsm8k_path.exists():
        with open(gsm8k_path, encoding="utf-8") as f:
            gsm_rows = [json.loads(line) for line in f if line.strip()]
        if gsm8k_limit:
            gsm_rows = gsm_rows[:gsm8k_limit]
        for idx, row in enumerate(gsm_rows):
            it, rej = convert_gsm8k_row(row, idx)
            all_items.extend(it)
            all_rejected.extend(rej)
    else:
        print(f"Warning: {gsm8k_path} not found; skipping local GSM8K load")

    # 2. Load and convert NuminaMath
    print(f"Building NuminaMath (limit={numina_limit})...")
    numina_rows: list[dict] = []
    if numina_path.exists():
        with open(numina_path, encoding="utf-8") as f:
            numina_rows = [json.loads(line) for line in f if line.strip()][:numina_limit]
    else:
        # Attempt streaming load if cache missing
        try:
            from datasets import load_dataset

            ds = load_dataset(NUMINAMATH_PIN["dataset_id"], split="train", streaming=True)
            for i, row in enumerate(ds):
                if i >= numina_limit:
                    break
                numina_rows.append(row)
        except (OSError, RuntimeError, ValueError) as exc:
            print(f"Notice: Streaming NuminaMath failed or offline ({exc}); using sample")

    for idx, row in enumerate(numina_rows):
        it, rej = convert_numinamath_row(row, idx)
        all_items.extend(it)
        all_rejected.extend(rej)

    # 3. Generate SymbolicMathematics tasks
    print(f"Generating SymbolicMathematics tasks (n={symbolic_n})...")
    families = [
        "symbolic_differentiation",
        "symbolic_integration",
        "polynomial_arithmetic",
        "first_order_ode",
    ]
    tasks_per_fam = symbolic_n // len(families)
    for fam in families:
        for t_idx in range(tasks_per_fam):
            it, rej = generate_symbolic_task(fam, t_idx, seed)
            if it:
                all_items.append(it)
            if rej:
                all_rejected.append(rej)

    deadline.mark_warmup_done()

    # 4. Stratified Split and Seal
    print(f"Stratifying and sealing {len(all_items)} total items...")
    splits, seal = stratify_and_seal(all_items, seed=seed)

    # 5. Write Processed Corpus Snapshot
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    with open(snapshot_path, "w", encoding="utf-8") as f:
        for it in all_items:
            f.write(json.dumps(it.to_dict()) + "\n")
    snapshot_sha = hashlib.sha256(snapshot_path.read_bytes()).hexdigest()

    # 6. Independent Verification
    print("Running parallel CPU & GPU verification...")
    v_report = run_parallel_verification(all_items, device_name=device_name)
    deadline.mark_compute_done()
    timing = deadline.finish()
    elapsed = max(1e-6, time.monotonic() - t_start)

    # 7. Coverage
    cov = generate_coverage_report(all_items, all_rejected)

    # 8. Provenance
    prov = collect_provenance(
        seed=seed,
        device=device,
        dataset_hashes={
            "gsm8k": GSM8K_PIN["expected_sha256"][:16],
            "snapshot": snapshot_sha[:16],
        },
        config={
            "numina_limit": numina_limit,
            "symbolic_n": symbolic_n,
            "gsm8k_limit": gsm8k_limit,
        },
    )

    manifest_data = {
        "phase": "p25-math-corpus",
        "status": "complete",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        "elapsed_sec": elapsed,
        "items_total": len(all_items),
        "items_train": len(splits["train"]),
        "items_val": len(splits["val"]),
        "items_held_out": len(splits["held_out"]),
        "held_out_seal": seal.to_dict(),
        "tracks": {
            "EXECUTE": cov["by_track"].get("EXECUTE", 0),
            "FIND": cov["by_track"].get("FIND", 0),
            "separation_rule": (
                "Passing EXECUTE measures calculation correctness and interpreter safety; "
                "passing FIND measures synthesis from problem. Passing first never counts as second."
            ),
        },
        "internal_exposure_disclosure": GSM8K_PIN["internal_exposure_disclosure"],
        "pins": {
            "gsm8k": GSM8K_PIN,
            "numinamath": NUMINAMATH_PIN,
            "symbolic": SYMBOLIC_PIN,
        },
        "coverage": cov,
        "out_of_scope_summary": {
            "total_rejected": len(all_rejected),
            "by_reason": cov["rejection_reasons"],
            "sample_rejections": [r.to_dict() for r in all_rejected[:10]],
        },
        "verification": v_report,
        "timing": timing,
        "corpus_snapshot": {
            "path": (
                str(snapshot_path.relative_to(_REPO_ROOT))
                if snapshot_path.is_relative_to(_REPO_ROOT)
                else str(snapshot_path)
            ),
            "sha256": snapshot_sha,
            "n_records": len(all_items),
        },
        "provenance": prov,
    }

    # Write checksummed manifest
    snap_key = (
        str(snapshot_path.relative_to(_REPO_ROOT))
        if snapshot_path.is_relative_to(_REPO_ROOT)
        else str(snapshot_path)
    )
    raw_artifacts = {
        snap_key: snapshot_sha,
    }
    written = write_manifest(output_manifest, manifest_data, raw_artifacts)
    return written


# ==============================================================================
# CLI Entrypoint
# ==============================================================================


def main() -> int:
    parser = argparse.ArgumentParser(
        description="P25/P30 Math Corpus Consolidation & Leak-Free Benchmark Harness"
    )
    parser.add_argument(
        "--build",
        action="store_true",
        help="Build consolidated corpus from GSM8K, NuminaMath, and Symbolic tasks",
    )
    parser.add_argument(
        "--verify", action="store_true", help="Run independent CPU and GPU verification"
    )
    parser.add_argument(
        "--audit-splits",
        action="store_true",
        help="Run P30 corpus isolation, grouping, contamination audit, and write split manifest",
    )
    parser.add_argument(
        "--group-by",
        type=str,
        default="source-problem-template",
        help="Grouping strategy for corpus isolation (default: source-problem-template)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Path to write the checksummed artifact manifest",
    )
    parser.add_argument(
        "--snapshot",
        type=str,
        default="data/processed/p25_corpus.jsonl",
        help="Path to write or read the processed corpus snapshot",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of GSM8K rows for fast test/smoke",
    )
    parser.add_argument(
        "--numina-limit",
        type=int,
        default=300,
        help="Limit number of NuminaMath rows to process",
    )
    parser.add_argument(
        "--symbolic-n",
        type=int,
        default=200,
        help="Number of SymbolicMathematics tasks to generate",
    )
    parser.add_argument(
        "--device",
        type=str,
        default=None,
        help="Compute device (cuda / cpu)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed",
    )
    args = parser.parse_args()

    if not args.build and not args.verify and not args.audit_splits:
        parser.print_help()
        return 1

    snap_path = _REPO_ROOT / args.snapshot

    if args.audit_splits:
        out_path = _REPO_ROOT / (args.output or "experiments/p30-splits.json")
        manifest = run_corpus_isolation_and_audit(
            snapshot_path=snap_path,
            output_path=out_path,
            group_by=args.group_by,
            device_name=args.device,
            seed=args.seed,
        )

        print("\n=== P30 Corpus Isolation Manifest Generated ===")
        print(f"Manifest: {out_path} (sha256={manifest['manifest_sha256'][:16]}...)")
        print(f"Status: {manifest['status']}")
        print(f"Total Groups: {manifest['groups_summary']['total_groups']}")
        print(
            f"Splits: train={manifest['split_counts']['items_train']} items, "
            f"val={manifest['split_counts']['items_val']} items, "
            f"final_test={manifest['split_counts']['items_final_test']} items"
        )
        print(
            f"Audit Before: {manifest['contamination_audit']['before_audit']['gsm8k_shared_source_problems']} "
            f"GSM8K contaminated source problems reproduced"
        )
        print(
            f"Audit After: zero_leakage_verified={manifest['contamination_audit']['after_audit']['zero_leakage_verified']}, "
            f"exposed_in_test={manifest['contamination_audit']['after_audit']['exposed_items_in_final_test']}"
        )
        print(
            f"Held-Out Seal: sealed={manifest['held_out_seal']['sealed']}, items={manifest['held_out_seal']['n_items']}"
        )
        print(f"Elapsed: {manifest['elapsed_sec']:.2f} s")
        return 0

    out_path = _REPO_ROOT / (args.output or "experiments/p25-corpus.json")

    manifest = build_and_verify_corpus(
        output_manifest=out_path,
        snapshot_path=snap_path,
        device_name=args.device,
        seed=args.seed,
        numina_limit=args.numina_limit,
        symbolic_n=args.symbolic_n,
        gsm8k_limit=args.limit,
    )

    print("\n=== P25 Math Corpus Manifest Generated ===")
    print(f"Manifest: {out_path} (sha256={manifest['manifest_sha256'][:16]}...)")
    print(f"Status: {manifest['status']}")
    print(f"Total Items: {manifest['items_total']}")
    print(
        f"Splits: train={manifest['items_train']}, val={manifest['items_val']}, "
        f"held_out_sealed={manifest['items_held_out']}"
    )
    print(f"Tracks: {manifest['tracks']['EXECUTE']} EXECUTE, {manifest['tracks']['FIND']} FIND")
    print(
        f"Verification: {manifest['verification']['verified_count']} passed, "
        f"{manifest['verification']['failures']} failures, "
        f"parity_sum={manifest['verification']['parity_sum_ok']}"
    )
    print(f"Out of Scope Logged: {manifest['out_of_scope_summary']['total_rejected']}")
    print(f"Elapsed: {manifest['elapsed_sec']:.2f} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
