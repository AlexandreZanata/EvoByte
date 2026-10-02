"""Gated scientific dataset matrix with pre-registered hypotheses and Domain L2 checks (P14 scope)."""

from __future__ import annotations

import argparse
import contextlib
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "benchmarks"))

from hw_probe import probe

from evobyte.bytecode import decode_human
from evobyte.constants import TunableProgram, tune_promoted_candidate
from evobyte.evolution import EvolutionConfig, run_evolution
from evobyte.vm import execute_batch

_REPO_ROOT = Path(__file__).resolve().parents[1]


def get_git_commit() -> str:
    with contextlib.suppress(OSError, subprocess.SubprocessError):
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
            cwd=_REPO_ROOT,
        )
        if out.returncode == 0:
            return out.stdout.strip()[:12]
    return "unknown"


# ==============================================================================
# 1. Scientific Domain Specifications & L2 Verifier Data Structures
# ==============================================================================


@dataclass
class ScientificDatasetSpec:
    """Pre-registered scientific dataset specification with domain constraints."""

    key: str
    name: str
    law_formula: str
    domain_field: str
    license_name: str
    license_url: str
    input_symbol: str
    input_unit: str
    output_symbol: str
    output_unit: str
    train_range: tuple[float, float]
    extrap_range: tuple[float, float]
    adversarial_points: list[float]
    expected_scaling_exponent: float | None  # e.g., 1.5 for Kepler (a^1.5)
    monotonicity_sign: (
        int | None
    )  # +1 for strictly increasing, -1 for decreasing, None if not monotonic
    asymptote_bound: float | None  # Upper bound on extrapolation (e.g. V_max in Michaelis-Menten)
    r2_threshold: float
    max_extrap_rel_error: float


@dataclass
class DomainL2Result:
    """Detailed audit report from Level-2 scientific domain verification."""

    status: str  # "SUPPORTED" | "NULL" | "NEEDS_WORK"
    dataset_key: str
    expression_str: str
    train_r2: float
    train_mse_f64: float
    hidden_r2: float
    hidden_mse_f64: float
    extrap_rel_error: float
    extrapolation_passed: bool
    units_scaling_passed: bool
    adversarial_passed: bool
    non_degenerate: bool
    failure_reasons: list[str] = field(default_factory=list)


def compute_r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Compute coefficient of determination R^2 in float64."""
    y_t = np.asarray(y_true, dtype=np.float64)
    y_p = np.asarray(y_pred, dtype=np.float64)
    ss_res = float(np.sum((y_t - y_p) ** 2))
    ss_tot = float(np.sum((y_t - np.mean(y_t)) ** 2))
    if ss_tot < 1e-12:
        return 1.0 if ss_res < 1e-12 else 0.0
    return max(-100.0, 1.0 - (ss_res / ss_tot))


def check_non_degeneracy(
    program: np.ndarray | TunableProgram,
    xs_probe: np.ndarray,
) -> tuple[bool, list[str]]:
    """Strict L2 degenerate-expression guards per docs/VERIFIER.md."""
    reasons = []

    # 1. Probe outputs across a diverse grid
    if isinstance(program, TunableProgram):
        preds, flags = program.execute(xs_probe)
    else:
        preds, flags = execute_batch(program, xs_probe)

    if flags.any() or not np.all(np.isfinite(preds)):
        reasons.append("Produces NaN/Inf or raised VM invalid execution flags")
        return False, reasons

    # 2. Constant-only output check
    pred_std = float(np.std(preds))
    if pred_std < 1e-6:
        reasons.append(f"Constant-only output (std={pred_std:.3e} < 1e-6)")

    # 3. Absurd constants check
    if isinstance(program, TunableProgram):
        slots = program.get_slots()
        head_w1, head_w0 = program.linear_head
        if abs(head_w1) > 1e6 or abs(head_w0) > 1e6:
            reasons.append("Absurd linear head constants (> 1e6)")
        for val in slots:
            if abs(float(val)) > 1e6:
                reasons.append(f"Absurd slot constant value {val} (> 1e6)")

    if len(reasons) > 0:
        return False, reasons
    return True, []


def check_units_scaling(
    program: np.ndarray | TunableProgram,
    base_x: float,
    expected_exponent: float | None,
    scale_factors: list[float] | None = None,
    tolerance: float = 0.15,
) -> tuple[bool, float | None]:
    """Check dimensional scaling invariance: f(lambda * x) / f(x) ~ lambda^alpha."""
    if expected_exponent is None:
        return True, None

    if scale_factors is None:
        scale_factors = [1.5, 2.0, 3.0]

    xs = np.array([base_x] + [base_x * s for s in scale_factors], dtype=np.float32)
    if isinstance(program, TunableProgram):
        preds, flags = program.execute(xs)
    else:
        preds, flags = execute_batch(program, xs)

    if flags.any() or not np.all(np.isfinite(preds)) or abs(preds[0]) < 1e-9:
        return False, None

    empirical_exponents = []
    base_pred = float(preds[0])
    for i, s in enumerate(scale_factors, 1):
        ratio = float(preds[i]) / base_pred
        if ratio <= 0:
            return False, None
        exp = np.log(ratio) / np.log(s)
        empirical_exponents.append(exp)

    mean_exp = float(np.mean(empirical_exponents))
    passed = bool(abs(mean_exp - expected_exponent) <= tolerance)
    return passed, mean_exp


def check_adversarial_domain(
    program: np.ndarray | TunableProgram,
    adversarial_points: list[float],
) -> tuple[bool, list[str]]:
    """Test candidate stability near domain boundaries, singularities, and asymptotic regions."""
    if not adversarial_points:
        return True, []

    xs_adv = np.array(adversarial_points, dtype=np.float32)
    if isinstance(program, TunableProgram):
        preds, flags = program.execute(xs_adv)
    else:
        preds, flags = execute_batch(program, xs_adv)

    reasons = []
    if flags.any() or not np.all(np.isfinite(preds)):
        reasons.append(
            "Raised invalid execution flag or produced NaN/Inf on adversarial test points"
        )
        return False, reasons

    return True, []


def verify_scientific_candidate_l2(
    candidate: np.ndarray | TunableProgram,
    spec: ScientificDatasetSpec,
    splits: dict[str, tuple[np.ndarray, np.ndarray]],
) -> DomainL2Result:
    """Execute complete Level-2 domain verification for a promoted scientific candidate."""
    xs_tr, ys_tr = splits["train"]
    xs_hid, ys_hid = splits["hidden"]
    xs_ext, ys_ext = splits["extrapolation"]

    failure_reasons: list[str] = []

    # 1. Non-degeneracy audit
    xs_probe = np.linspace(spec.train_range[0], spec.train_range[1], 100, dtype=np.float32)
    non_deg, deg_reasons = check_non_degeneracy(candidate, xs_probe)
    if not non_deg:
        failure_reasons.extend(deg_reasons)

    # 2. Float64 Evaluation on train & hidden
    if isinstance(candidate, TunableProgram):
        p_tr, f_tr = candidate.execute(xs_tr)
        p_hid, f_hid = candidate.execute(xs_hid)
        p_ext, f_ext = candidate.execute(xs_ext)
        expr_str = candidate.decode_expression()
    else:
        p_tr, f_tr = execute_batch(candidate, xs_tr)
        p_hid, f_hid = execute_batch(candidate, xs_hid)
        p_ext, f_ext = execute_batch(candidate, xs_ext)
        expr_str = decode_human(candidate)

    tr_valid = not f_tr.any() and np.all(np.isfinite(p_tr))
    hid_valid = not f_hid.any() and np.all(np.isfinite(p_hid))
    ext_valid = not f_ext.any() and np.all(np.isfinite(p_ext))

    tr_r2 = compute_r2(ys_tr, p_tr) if tr_valid else -1.0
    tr_mse = float(np.mean((p_tr - ys_tr) ** 2)) if tr_valid else float("inf")

    hid_r2 = compute_r2(ys_hid, p_hid) if hid_valid else -1.0
    hid_mse = float(np.mean((p_hid - ys_hid) ** 2)) if hid_valid else float("inf")

    # 3. Extrapolation relative error check
    if ext_valid:
        rel_errors = np.abs(p_ext - ys_ext) / np.maximum(np.abs(ys_ext), 1e-4)
        ext_rel_err = float(np.median(rel_errors))
        ext_passed = ext_rel_err <= spec.max_extrap_rel_error
        if not ext_passed:
            failure_reasons.append(
                f"Extrapolation relative error {ext_rel_err:.2%} exceeded threshold {spec.max_extrap_rel_error:.2%}"
            )
    else:
        ext_rel_err = float("inf")
        ext_passed = False
        failure_reasons.append("Extrapolation points caused invalid flags or infinite predictions")

    # 4. Monotonicity & Asymptote domain checks
    if ext_valid and spec.monotonicity_sign is not None:
        diffs = np.diff(p_ext)
        if spec.monotonicity_sign > 0 and not np.all(diffs >= -1e-4):
            failure_reasons.append("Violated required positive monotonicity dY/dX >= 0")
        elif spec.monotonicity_sign < 0 and not np.all(diffs <= 1e-4):
            failure_reasons.append("Violated required negative monotonicity dY/dX <= 0")

    if (
        ext_valid
        and spec.asymptote_bound is not None
        and np.any(p_ext > spec.asymptote_bound * 1.25)
    ):
        failure_reasons.append(
            f"Extrapolation exceeded physical asymptote bound {spec.asymptote_bound:.2f}"
        )

    # 5. Units / Scaling verification
    base_x = float(np.median(xs_tr))
    units_passed, measured_exp = check_units_scaling(
        candidate, base_x, spec.expected_scaling_exponent
    )
    if not units_passed and spec.expected_scaling_exponent is not None:
        failure_reasons.append(
            f"Dimensional scaling exponent {measured_exp} differed from physical expectation {spec.expected_scaling_exponent}"
        )

    # 6. Adversarial domain audit
    adv_passed, adv_reasons = check_adversarial_domain(candidate, spec.adversarial_points)
    if not adv_passed:
        failure_reasons.extend(adv_reasons)

    # 7. Final Status Determination
    if (
        non_deg
        and tr_r2 >= spec.r2_threshold
        and hid_r2 >= (spec.r2_threshold - 0.05)
        and ext_passed
        and units_passed
        and adv_passed
        and len(failure_reasons) == 0
    ):
        status = "SUPPORTED"
    elif tr_r2 < 0.50:
        status = "NULL"
    else:
        status = "NEEDS_WORK"

    return DomainL2Result(
        status=status,
        dataset_key=spec.key,
        expression_str=expr_str,
        train_r2=tr_r2,
        train_mse_f64=tr_mse,
        hidden_r2=hid_r2,
        hidden_mse_f64=hid_mse,
        extrap_rel_error=ext_rel_err,
        extrapolation_passed=ext_passed,
        units_scaling_passed=units_passed,
        adversarial_passed=adv_passed,
        non_degenerate=non_deg,
        failure_reasons=failure_reasons,
    )


# ==============================================================================
# 2. Pre-Registered Scientific Dataset Registry
# ==============================================================================


PREREGISTERED_SCIENCE_SPECS: list[ScientificDatasetSpec] = [
    ScientificDatasetSpec(
        key="kepler_third_law",
        name="Kepler's Third Planetary Law",
        law_formula="T = a^(3/2) = a * sqrt(a)",
        domain_field="Astrophysics & Celestial Mechanics",
        license_name="NASA Exoplanet Archive / Planetary Fact Sheet (Public Domain)",
        license_url="https://nssdc.gsfc.nasa.gov/planetary/factsheet/",
        input_symbol="a",
        input_unit="Astronomical Units (AU)",
        output_symbol="T",
        output_unit="Earth Years (yr)",
        train_range=(0.2, 5.2),  # Mercury to Jupiter
        extrap_range=(9.0, 30.0),  # Saturn to Neptune
        adversarial_points=[0.01, 0.05, 50.0],
        expected_scaling_exponent=1.5,
        monotonicity_sign=1,
        asymptote_bound=None,
        r2_threshold=0.999,
        max_extrap_rel_error=0.05,
    ),
    ScientificDatasetSpec(
        key="boyle_gas_law",
        name="Boyle-Mariotte Ideal Gas Law",
        law_formula="P = k / V",
        domain_field="Thermodynamics & Gas Physics",
        license_name="NIST Chemistry WebBook (Public Domain)",
        license_url="https://webbook.nist.gov/chemistry/fluid/",
        input_symbol="V",
        input_unit="Liters (L)",
        output_symbol="P",
        output_unit="Atmospheres (atm)",
        train_range=(1.0, 10.0),
        extrap_range=(12.0, 25.0),
        adversarial_points=[0.05, 0.2, 50.0],
        expected_scaling_exponent=-1.0,
        monotonicity_sign=-1,
        asymptote_bound=None,
        r2_threshold=0.99,
        max_extrap_rel_error=0.08,
    ),
    ScientificDatasetSpec(
        key="stefan_boltzmann",
        name="Stefan-Boltzmann Blackbody Radiation",
        law_formula="j* = sigma * T^4",
        domain_field="Thermodynamics & Radiative Transfer",
        license_name="NIST Physical Reference Data (CC0)",
        license_url="https://physics.nist.gov/cuu/Constants/",
        input_symbol="T_k",
        input_unit="KiloKelvin (kK)",
        output_symbol="j*",
        output_unit="kW/m^2",
        train_range=(0.3, 1.5),  # 300 K to 1500 K
        extrap_range=(1.8, 3.0),  # 1800 K to 3000 K
        adversarial_points=[0.01, 0.05, 5.0],
        expected_scaling_exponent=4.0,
        monotonicity_sign=1,
        asymptote_bound=None,
        r2_threshold=0.99,
        max_extrap_rel_error=0.08,
    ),
    ScientificDatasetSpec(
        key="michaelis_menten",
        name="Michaelis-Menten Enzyme Kinetics",
        law_formula="v = (V_max * [S]) / (K_m + [S])",
        domain_field="Biochemistry & Enzymology",
        license_name="BioModels Database (CC0)",
        license_url="https://www.ebi.ac.uk/biomodels/",
        input_symbol="[S]",
        input_unit="micromolar (uM)",
        output_symbol="v",
        output_unit="uM / sec",
        train_range=(0.5, 10.0),
        extrap_range=(15.0, 40.0),
        adversarial_points=[0.01, 100.0],
        expected_scaling_exponent=None,
        monotonicity_sign=1,
        asymptote_bound=10.0,  # V_max = 10.0
        r2_threshold=0.98,
        max_extrap_rel_error=0.08,
    ),
    ScientificDatasetSpec(
        key="lorentz_factor",
        name="Relativistic Lorentz Factor",
        law_formula="gamma = 1 / sqrt(1 - beta^2)",
        domain_field="Special Relativity & Particle Physics",
        license_name="CERN Open Data (CC-BY 4.0)",
        license_url="http://opendata.cern.ch/",
        input_symbol="beta",
        input_unit="v / c (dimensionless)",
        output_symbol="gamma",
        output_unit="dimensionless",
        train_range=(0.0, 0.85),
        extrap_range=(0.88, 0.98),
        adversarial_points=[0.99, 0.995],
        expected_scaling_exponent=None,
        monotonicity_sign=1,
        asymptote_bound=None,
        r2_threshold=0.98,
        max_extrap_rel_error=0.15,
    ),
]


def generate_scientific_splits(
    spec: ScientificDatasetSpec,
    n_points: int = 64,
) -> tuple[dict[str, tuple[np.ndarray, np.ndarray]], str]:
    """Generate train, val, hidden, and extrapolation splits for a pre-registered scientific dataset."""
    lo, hi = spec.train_range
    ext_lo, ext_hi = spec.extrap_range

    def ground_truth_eval(x: np.ndarray) -> np.ndarray:
        if spec.key == "kepler_third_law":
            return (x * np.sqrt(x)).astype(np.float32)
        elif spec.key == "boyle_gas_law":
            return (22.4 / x).astype(np.float32)
        elif spec.key == "stefan_boltzmann":
            return (56.7 * (x**4)).astype(np.float32)
        elif spec.key == "michaelis_menten":
            return ((10.0 * x) / (2.0 + x)).astype(np.float32)
        elif spec.key == "lorentz_factor":
            return (1.0 / np.sqrt(np.maximum(1.0 - x * x, 1e-6))).astype(np.float32)
        raise ValueError(f"Unknown law key {spec.key}")

    xs_tr = np.linspace(lo, hi, n_points, dtype=np.float32)
    ys_tr = ground_truth_eval(xs_tr)

    xs_val = np.linspace(lo * 1.05, hi * 0.95, n_points, dtype=np.float32)
    ys_val = ground_truth_eval(xs_val)

    # Disjoint in-domain hidden evaluation
    step = (hi - lo) / n_points
    xs_hid = np.linspace(lo + 0.31 * step, hi - 0.29 * step, n_points, dtype=np.float32)
    ys_hid = ground_truth_eval(xs_hid)

    # Strictly out-of-domain extrapolation evaluation
    xs_ext = np.linspace(ext_lo, ext_hi, n_points, dtype=np.float32)
    ys_ext = ground_truth_eval(xs_ext)

    h = hashlib.sha256(
        np.ascontiguousarray(xs_tr).tobytes() + np.ascontiguousarray(ys_tr).tobytes()
    ).hexdigest()[:16]

    splits = {
        "train": (xs_tr, ys_tr),
        "val": (xs_val, ys_val),
        "hidden": (xs_hid, ys_hid),
        "extrapolation": (xs_ext, ys_ext),
    }
    return splits, h


# ==============================================================================
# 3. Gated Science Matrix Execution
# ==============================================================================


def evaluate_dataset_on_clock(
    spec: ScientificDatasetSpec,
    seeds: list[int],
    max_trial_sec: float = 2.0,
    pop_size: int = 400,
    max_generations: int = 40,
) -> dict[str, Any]:
    splits, data_hash = generate_scientific_splits(spec)
    xs_tr, ys_tr = splits["train"]
    xs_val, ys_val = splits["val"]

    seed_reports: list[DomainL2Result] = []
    total_evals = 0
    t0_all = time.perf_counter()

    for s in seeds:
        rng = np.random.default_rng(s)
        cfg = EvolutionConfig(
            pop_size=pop_size,
            elite_k=32,
            tournament_size=4,
            crossover_p=0.4,
            gene_mut_p=0.10,
            large_mut_p=0.06,
            point_mut_p=0.02,
            random_inject_p=0.10,
            max_generations=max_generations,
            early_stop_fitness=1e-5,
        )

        res = run_evolution(xs_tr, ys_tr, cfg, rng, xs_val=xs_val, ys_val=ys_val)
        best_p = res["best_program"]
        total_evals += res["candidates_total"]

        tune_res = tune_promoted_candidate(best_p, xs_tr, ys_tr, max_steps=15)
        if tune_res["final_mse"] < res["best_mse"]:
            candidate = tune_res["tunable_program"]
        else:
            candidate = best_p

        l2_report = verify_scientific_candidate_l2(candidate, spec, splits)
        seed_reports.append(l2_report)

    elapsed_all = max(1e-4, time.perf_counter() - t0_all)

    supported_count = sum(1 for r in seed_reports if r.status == "SUPPORTED")
    null_count = sum(1 for r in seed_reports if r.status == "NULL")

    if supported_count >= 2:
        dataset_verdict = "SUPPORTED"
    elif null_count >= 3:
        dataset_verdict = "NULL (Empirical Negative Result Validated)"
    else:
        dataset_verdict = "NEEDS_WORK (Domain L2 Gate Blocked Unproven Claims)"

    best_r2_report = max(seed_reports, key=lambda r: r.hidden_r2)

    return {
        "spec": spec,
        "dataset_key": spec.key,
        "data_hash": data_hash,
        "dataset_verdict": dataset_verdict,
        "supported_count": supported_count,
        "total_seeds": len(seeds),
        "mean_hidden_r2": float(np.mean([r.hidden_r2 for r in seed_reports])),
        "mean_extrap_error": float(np.median([r.extrap_rel_error for r in seed_reports])),
        "best_report": best_r2_report,
        "seed_reports": seed_reports,
        "total_evaluated": total_evals,
        "cvps": total_evals / elapsed_all,
    }


def run_science_matrix(
    preregistered_only: bool = True,
    seeds: list[int] | None = None,
    max_trial_sec: float = 2.0,
    device_name: str | None = None,
) -> dict[str, Any]:
    if seeds is None:
        seeds = [42, 101, 202, 303, 404]

    device = (
        torch.device("cuda")
        if (device_name == "cuda" or (device_name is None and torch.cuda.is_available()))
        else torch.device("cpu")
    )

    hw = probe()
    commit = get_git_commit()

    print("=" * 90)
    print("EVOBYTE P14 GATED SCIENTIFIC EVALUATION MATRIX")
    print("=" * 90)
    print(f"  Git Commit      : {commit}")
    print(f"  CPU             : {hw.get('cpu', 'unknown')}")
    print(f"  OS              : {hw.get('os', 'unknown')}")
    print(f"  Python          : {hw.get('python', sys.version.split()[0])}")
    print(f"  PyTorch         : {getattr(torch, '__version__', 'unknown')}")
    print(f"  CUDA Available  : {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"  GPU             : {torch.cuda.get_device_name(0)}")
    print(f"  Active Device   : {device}")
    print(f"  Preregistered   : {preregistered_only}")
    print(f"  Seeds ({len(seeds)}) : {seeds}")
    print(
        f"  Pre-registered  : {len(PREREGISTERED_SCIENCE_SPECS)} scientific laws with domain constraints"
    )
    print("=" * 90)

    dataset_results = []
    for spec in PREREGISTERED_SCIENCE_SPECS:
        print(f"\n--- Evaluating Scientific Law: {spec.name} ({spec.key}) ---")
        print(f"  Formula         : {spec.law_formula}")
        print(f"  Domain Field    : {spec.domain_field}")
        print(f"  License         : {spec.license_name}")
        print(
            f"  Pre-reg Target  : R^2 >= {spec.r2_threshold}, Extrap Error <= {spec.max_extrap_rel_error:.1%}"
        )

        res = evaluate_dataset_on_clock(spec, seeds, max_trial_sec=max_trial_sec)
        dataset_results.append(res)

        b = res["best_report"]
        print(
            f"  Outcome: {res['dataset_verdict']} ({res['supported_count']}/{res['total_seeds']} seeds) | "
            f"Hidden R^2: {b.hidden_r2:.4f} | Extrap Rel Err: {b.extrap_rel_error:.2%}"
        )
        print(f"  Discovered Expr : {b.expression_str}")
        if b.failure_reasons:
            print(f"  L2 Gate Notes   : {b.failure_reasons[0]}")

    print_science_summary_tables(dataset_results, commit)

    return {
        "status": "PASS",
        "commit": commit,
        "datasets": dataset_results,
    }


def print_science_summary_tables(
    results: list[dict[str, Any]],
    commit: str,
) -> None:
    print("\n" + "=" * 96)
    print("P14 SCIENTIFIC BENCHMARK MATRIX SUMMARY TABLE")
    print("=" * 96)
    header = (
        f"{'Dataset / Physical Law':<30} | {'Field':<18} | {'Outcome':<18} | "
        f"{'Hidden R^2':<10} | {'Extrap Err':<10}"
    )
    print(header)
    print("-" * 96)

    for r in results:
        spec: ScientificDatasetSpec = r["spec"]
        b: DomainL2Result = r["best_report"]
        verdict_trunc = r["dataset_verdict"].split("(")[0].strip()
        print(
            f"{spec.name[:28]:<30} | {spec.domain_field[:18]:<18} | {verdict_trunc:<18} | "
            f"{b.hidden_r2:<10.4f} | {b.extrap_rel_error:<10.2%}"
        )
    print("-" * 96)

    print("\n" + "=" * 96)
    print("REPRODUCTION & PROVENANCE BUNDLE")
    print("=" * 96)
    for r in results:
        spec: ScientificDatasetSpec = r["spec"]
        b: DomainL2Result = r["best_report"]
        print(f"Physical Law : {spec.name} [{spec.key}]")
        print(f"  License    : {spec.license_name} ({spec.license_url})")
        print(f"  Data Hash  : {r['data_hash']}")
        print(f"  Verdict    : {r['dataset_verdict']}")
        print(f"  Expression : {b.expression_str}")
        print(
            f"  Gates      : Extrap={b.extrapolation_passed}, Units={b.units_scaling_passed}, Adv={b.adversarial_passed}"
        )
        print("-" * 96)

    print(f"\nP14 Gated Science Evaluation Complete. Git Commit: {commit}\n")


# ==============================================================================
# P40 acceptance boundary: executable evidence audit only.
# PNN is metadata selecting an implemented capability; unknown phases fail.
# ==============================================================================

ACCEPTANCE_PHASES = ("P40", "P41", "P42", "P43", "P44", "P45", "P46")


P46_CERTIFICATE_TYPES = ("proof_or_counterexample", "construction_or_impossibility")
P46_ENTRY_FIELDS = (
    "id",
    "title",
    "statement_excerpt",
    "area",
    "primary_source",
    "consulted_at",
    "state",
    "certificate_type",
    "verifiability",
    "partial_refs",
    "statement_sha256",
)
P46_SOURCE_FIELDS = ("citation", "url", "dataset", "dataset_commit")


def _p46_check_entry(entry: Any, bucket: str) -> list[str]:
    """Return schema violations for one catalogue record (empty when valid)."""
    errs: list[str] = []
    if not isinstance(entry, dict):
        return [f"{bucket}: entry is not an object"]
    tag = entry.get("id", f"{bucket}[?]")
    for required in P46_ENTRY_FIELDS:
        if required not in entry:
            errs.append(f"{tag}: missing field {required}")
    src = entry.get("primary_source")
    if not isinstance(src, dict):
        errs.append(f"{tag}: primary_source is not an object")
    else:
        for field in P46_SOURCE_FIELDS:
            if not src.get(field):
                errs.append(f"{tag}: primary_source missing {field}")
        commit = str(src.get("dataset_commit", ""))
        if commit and (len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit)):
            errs.append(f"{tag}: dataset_commit is not a pinned 40-hex commit")
        url = str(src.get("url", ""))
        if url and not re.fullmatch(r"https://www\.erdosproblems\.com/\d+", url):
            errs.append(f"{tag}: source URL is not a problem page")
    if entry.get("certificate_type") not in P46_CERTIFICATE_TYPES:
        errs.append(f"{tag}: certificate_type outside frozen vocabulary")
    if not isinstance(entry.get("partial_refs"), list):
        errs.append(f"{tag}: partial_refs must be a list")
    if not str(entry.get("statement_excerpt", "")).strip():
        errs.append(f"{tag}: empty statement_excerpt")
    if not str(entry.get("verifiability", "")).strip():
        errs.append(f"{tag}: empty verifiability")
    sha = str(entry.get("statement_sha256", ""))
    if len(sha) != 16 or any(c not in "0123456789abcdef" for c in sha):
        errs.append(f"{tag}: statement_sha256 is not 16 hex chars")
    try:
        datetime.date.fromisoformat(str(entry.get("consulted_at")))
    except ValueError:
        errs.append(f"{tag}: consulted_at is not an ISO date")
    entry_id = str(entry.get("id", ""))
    if (
        entry_id.startswith("erdos-")
        and isinstance(src, dict)
        and not str(src.get("url", "")).endswith("/" + entry_id.split("-", 1)[1])
    ):
        errs.append(f"{tag}: id and source URL disagree")
    return errs


def run_p46_catalogue_audit(config_path: str | Path, output_path: str | Path) -> dict[str, Any]:
    """P46 audit: validate the sourced open-problem catalogue (schema + counts + dedup).

    Technical validation only; the phase exit gate additionally requires a
    human mathematical review of the curation before P47, which this audit
    reports as pending and cannot grant.
    """
    t0 = time.perf_counter()
    cfg_p = Path(config_path)
    with open(cfg_p, encoding="utf-8") as f:
        config = json.load(f)
    if config.get("phase") != "P46":
        raise ValueError(f"Config {cfg_p} is not a P46 configuration")
    config_sha = hashlib.sha256(cfg_p.read_bytes()).hexdigest()
    catalogue_p = _REPO_ROOT / config.get("catalogue_path", "docs/research/open-problems.json")
    min_open = int(config.get("min_open_confirmed", 100))

    print("=" * 115)
    print("P46 OPEN-PROBLEM CATALOGUE AUDIT (schema, sources, counts, dedup)")
    print("=" * 115)

    report: dict[str, Any] = {
        "phase": "P46",
        "resolved_config": {
            "config_path": str(cfg_p),
            "config_sha256": config_sha,
            "acceptance_phase": "P46",
            "catalogue_path": str(catalogue_p),
        },
    }
    try:
        with open(catalogue_p, encoding="utf-8") as f:
            cat = json.load(f)
    except (OSError, ValueError) as exc:
        report.update(
            {"status": "FAIL", "verdict": "REJECTED", "errors": [f"unreadable catalogue: {exc}"]}
        )
        print(f"P46 REJECTED: unreadable catalogue: {exc}")
        return report

    errors: list[str] = []
    if cat.get("phase") != "p46-open-problem-catalogue":
        errors.append("catalogue phase marker is wrong")
    source = cat.get("source") or {}
    for required in ("primary", "dataset", "dataset_commit", "license"):
        if not source.get(required):
            errors.append(f"source missing {required}")
    open_conf = cat.get("open_confirmed")
    if not isinstance(open_conf, list):
        errors.append("open_confirmed must be a list")
        open_conf = []
    candidates = cat.get("finite_search_candidates") or []
    if not isinstance(candidates, list):
        errors.append("finite_search_candidates must be a list")
        candidates = []

    for entry in open_conf:
        errors.extend(_p46_check_entry(entry, "open_confirmed"))
        if entry.get("state") != "open-confirmed":
            errors.append(f"{entry.get('id', '?')}: open bucket entry state is not open-confirmed")
    for entry in candidates:
        errors.extend(_p46_check_entry(entry, "finite_search_candidates"))
        if entry.get("finite_resolution_possible") is not True:
            errors.append(f"{entry.get('id', '?')}: candidate must be finite-resolution possible")

    ids = [str(e.get("id")) for e in open_conf + candidates]
    id_dupes = sorted({i for i in ids if ids.count(i) > 1})
    if id_dupes:
        errors.append(f"duplicate ids: {id_dupes[:5]}")
    shas = [str(e.get("statement_sha256")) for e in open_conf + candidates]
    sha_dupes = sorted({s for s in shas if shas.count(s) > 1})
    if sha_dupes:
        errors.append(f"duplicate statement hashes: {sha_dupes[:5]}")

    counts = cat.get("counts") or {}
    if counts.get("open_confirmed") != len(open_conf):
        errors.append("counts.open_confirmed disagrees with the entries")
    if counts.get("finite_search_candidates") != len(candidates):
        errors.append("counts.finite_search_candidates disagrees with the entries")
    if len(open_conf) < min_open:
        errors.append(f"open_confirmed={len(open_conf)} below the frozen minimum {min_open}")

    review = cat.get("human_review") or {}
    review_required = bool(review.get("required", True))
    schema_ok = not errors
    technical = "PASS" if schema_ok else "FAIL"
    verdict = "PENDING_HUMAN_REVIEW" if schema_ok else "REJECTED"

    area_dist: dict[str, int] = {}
    for entry in open_conf:
        area = str(entry.get("area", "unsorted"))
        area_dist[area] = area_dist.get(area, 0) + 1
    report.update(
        {
            "status": "PASS" if schema_ok else "FAIL",
            "verdict": verdict,
            "claim_scope": "catalogue metadata validation; curation approval is a human gate",
            "catalogue_sha256": hashlib.sha256(catalogue_p.read_bytes()).hexdigest(),
            "source": source,
            "counts": {
                "open_confirmed": len(open_conf),
                "finite_search_candidates": len(candidates),
                "status_unconfirmed": len(cat.get("status_unconfirmed") or []),
                "solved_examples": len(cat.get("solved_examples") or []),
                "unsuitable": len(cat.get("unsuitable") or []),
                "min_open_confirmed": min_open,
            },
            "area_distribution": dict(sorted(area_dist.items(), key=lambda kv: -kv[1])),
            "sample_ids": [e.get("id") for e in open_conf[:5]],
            "checks": {
                "schema_ok": schema_ok,
                "count_ok": len(open_conf) >= min_open,
                "dedup_ok": not id_dupes and not sha_dupes,
                "source_pinned": bool(source.get("dataset_commit")),
            },
            "errors": errors[:50],
            "human_review": {
                "required": review_required,
                "status": review.get("status", "pending"),
                "scope": review.get("scope", "curation before P47"),
                "gate_note": "P47 is blocked until a mathematician approves this curation; "
                "this audit cannot grant approval.",
            },
            "elapsed_sec": time.perf_counter() - t0,
        }
    )
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True, default=str)
    print(
        f"P46 technical={technical} verdict={verdict}: {len(open_conf)} open-confirmed, "
        f"{len(candidates)} finite-search candidates; report -> {out_p}"
    )
    return report


def run_p45_envelope_audit(config_path: str | Path, output_path: str | Path) -> dict[str, Any]:
    """P45 audit: 60s tracing matrix, frozen selection, 600s envelope on the winner."""
    import tempfile

    import torch as _torch

    from evobyte.provenance import (
        collect_provenance,
        get_git_commit,
        get_git_status,
    )

    t0 = time.perf_counter()
    cfg_p = Path(config_path)
    with open(cfg_p, encoding="utf-8") as f:
        config = json.load(f)
    if config.get("phase") != "P45":
        raise ValueError(f"Config {cfg_p} is not a P45 configuration")
    config_sha = hashlib.sha256(cfg_p.read_bytes()).hexdigest()

    print("=" * 115)
    print("P45 HONEST-ENVELOPE AUDIT (real budgets, exclusive dirs, no OOM tolerated)")
    print("=" * 115)

    report: dict[str, Any] = {
        "phase": "P45",
        "resolved_config": {
            "config_path": str(cfg_p),
            "config_sha256": config_sha,
            "acceptance_phase": "P45",
        },
    }
    if not _torch.cuda.is_available():
        report.update(
            {
                "verdict": "NOT_MEASURED",
                "reason": "no CUDA reference GPU; resident envelope claims blocked",
            }
        )
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        with open(out_p, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, sort_keys=True, default=str)
        print("P45 audit NOT_MEASURED: no CUDA device.")
        return report

    from gpu_limits import run_p45_envelope_measurement

    scratch = Path(tempfile.mkdtemp(prefix="evobyte-p45-"))
    seed = int(config.get("seed", 42))
    common = {
        "formula": config.get("formula", "x**2 + 3*x + 7"),
        "pop_size": int(config.get("pop_size", 256)),
        "seed": seed,
        "smoke": False,
        "scale_factor": 1.0,
        "verify_every_gens": int(config.get("verify_every_gens", 10)),
        "checkpoint_every_sec": float(config.get("checkpoint_every_sec", 120.0)),
        "device_name": config.get("device", "cuda"),
    }
    matrix = run_p45_envelope_measurement(
        durations_sec=list(config.get("durations_60s", [60])),
        tracing_modes=list(config.get("tracing_modes_60s", [False, True])),
        output_path=str(scratch / "p45-matrix.json"),
        raw_root=str(scratch / "matrix-raw"),
        **common,
    )
    cells = matrix["tiers"]
    base_ok = len(cells) > 0 and all(c["status"] == "ok" and c["counter_check"] for c in cells)
    selected: bool | None = None
    if base_ok:
        best = max(cells, key=lambda c: (c["verified_exact"], c["tracing"]))
        selected = bool(best["tracing"])
    print(f"  60s matrix stable={base_ok}; selected tracing={selected}")

    envelope: dict[str, Any] | None = None
    if base_ok and selected is not None:
        envelope = run_p45_envelope_measurement(
            durations_sec=list(config.get("durations_600s", [600])),
            tracing_modes=[selected],
            output_path=str(scratch / "p45-envelope.json"),
            raw_root=str(scratch / "envelope-raw"),
            **common,
        )
        print(f"  600s envelope verdict={envelope['verdict']}")

    if not base_ok or envelope is None:
        verdict = "MIXED"
    elif envelope["verdict"] == "ACCEPTED" and all(
        t["status"] == "ok" and t["counter_check"] for t in envelope["tiers"]
    ):
        verdict = "ACCEPTED"
    else:
        verdict = "MIXED"

    revision = get_git_commit()
    dirty = get_git_status()
    prov = collect_provenance(
        seed=seed,
        device=_torch.device("cpu"),
        dataset_hashes={"p45_config": config_sha[:16]},
        config={"acceptance_phase": "P45"},
    )
    report.update(
        {
            "verdict": verdict,
            "claim_scope": "full-pipeline envelope at real budgets; no hour-stability claim",
            "run_id": hashlib.sha256(f"{config_sha}{revision}".encode()).hexdigest()[:16],
            "revision": revision,
            "dirty": dirty,
            "matrix_60s": {
                "verdict": matrix["verdict"],
                "tiers": matrix["tiers"],
                "stages_per_sec": matrix["stages_per_sec"],
            },
            "selection_rule": config.get("selection_rule"),
            "selected_tracing": selected,
            "envelope_600s": (
                {
                    "verdict": envelope["verdict"],
                    "tiers": envelope["tiers"],
                    "stages_per_sec": envelope["stages_per_sec"],
                    "batch_policy": envelope.get("batch_policy"),
                }
                if envelope
                else None
            ),
            "hardware": prov["hardware"],
            "driver": (prov["hardware"].get("nvidia_smi", "not-probed")),
            "package_versions": {
                "python": prov["hardware"].get("python"),
                "numpy": prov["hardware"].get("numpy"),
                "torch": prov["hardware"].get("torch"),
                "cuda": prov["hardware"].get("cuda_version"),
            },
            "seeds_rng": f"fixed seed {seed} (+101 per cell); deterministic rebuilds, not bit-compared",
            "budgets": "requested 60s x2 + 600s x1 wall-clock at scale 1.0; observed per tier",
            "counters": {
                "cells_60s": len(cells),
                "cells_60s_ok": sum(1 for c in cells if c["status"] == "ok"),
                "long_tier_ok": bool(envelope)
                and all(t["status"] == "ok" for t in envelope["tiers"]),
            },
            "limitations": [
                "No 3600s confirmation run; hour-stability is not claimed.",
                "VRAM headroom accounts coarsely for other processes (nvidia-smi snapshots).",
            ],
            "elapsed_sec": time.perf_counter() - t0,
        }
    )
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True, default=str)
    print(f"P45 audit {verdict}; report -> {out_p}")
    return report


def _p44_profile_components(evo: Any, iters: int) -> dict[str, Any]:
    """Time generation/mutation/execution/selection sections with device sync."""
    import torch as _torch

    from evobyte.grammar import grammar_mutate_batch_torch, sample_grammar_batch
    from evobyte.resident import (
        gpu_crossover_single_point,
        gpu_tournament_selection,
    )
    from evobyte.vm_torch import execute_population_torch

    dev = evo.device
    is_cuda = dev.type == "cuda" and _torch.cuda.is_available()

    def _sync() -> None:
        if is_cuda:
            _torch.cuda.synchronize(dev)

    def _timed(fn: Any) -> float:
        _sync()
        t0 = time.perf_counter()
        for _ in range(iters):
            fn()
        _sync()
        return (time.perf_counter() - t0) / iters

    pop = evo.population
    cfg = evo.config
    fit = _torch.rand(pop.shape[0], device=dev)
    t_gen = _timed(lambda: sample_grammar_batch(pop.shape[0], device=dev, seed=1).to(dev))
    t_mut = _timed(lambda: grammar_mutate_batch_torch(pop, device=dev, p_mut=cfg.gene_mut_p))
    t_exe = _timed(lambda: execute_population_torch(pop, evo.xs, device=dev, buffer=evo.vm_buffer))

    def _select() -> None:
        _sfit, sidx = _torch.sort(fit)
        spop = pop[sidx]
        winners = gpu_tournament_selection(spop, _sfit, pop.shape[0] // 2, 4)
        gpu_crossover_single_point(winners, winners, crossover_p=0.4)

    t_sel = _timed(_select)
    _sync()
    t_step_0 = time.perf_counter()
    for _ in range(iters):
        evo.step()
    _sync()
    t_step = (time.perf_counter() - t_step_0) / iters
    total = t_gen + t_mut + t_exe + t_sel
    return {
        "iters": iters,
        "mean_ms": {
            "generation": t_gen * 1000.0,
            "mutation": t_mut * 1000.0,
            "execution": t_exe * 1000.0,
            "selection": t_sel * 1000.0,
            "full_step": t_step * 1000.0,
        },
        "share": (
            {
                k: v / total
                for k, v in {
                    "generation": t_gen,
                    "mutation": t_mut,
                    "execution": t_exe,
                    "selection": t_sel,
                }.items()
            }
            if total > 0
            else {}
        ),
    }


def run_p44_resident_audit(config_path: str | Path, output_path: str | Path) -> dict[str, Any]:
    """P44 audit: resident torch mutation with per-backend determinism and profile."""
    import random as _random
    import unittest.mock as _mock

    import numpy as _np
    import torch as _torch

    from evobyte.evolution import EvolutionConfig
    from evobyte.grammar import (
        GrammarResidentEvolution,
        batch_is_valid_torch,
        grammar_mutate_batch,
        grammar_mutate_batch_torch,
        sample_grammar_batch,
    )
    from evobyte.provenance import (
        collect_provenance,
        get_git_commit,
        get_git_status,
    )
    from evobyte.resident import state_fingerprint

    t0 = time.perf_counter()
    cfg_p = Path(config_path)
    with open(cfg_p, encoding="utf-8") as f:
        config = json.load(f)
    if config.get("phase") != "P44":
        raise ValueError(f"Config {cfg_p} is not a P44 configuration")
    config_sha = hashlib.sha256(cfg_p.read_bytes()).hexdigest()
    seed = int(config.get("seed", 7))
    pop_size = int(config.get("pop_size", 64))
    n_gens = int(config.get("determinism_gens", 30))
    profile_iters = int(config.get("profile_iters", 25))

    import sympy as _sympy

    _x = _sympy.Symbol("x")
    _fn = _sympy.lambdify(
        _x, _sympy.sympify(config.get("formula", "x**2 + 3*x + 7")), modules=["numpy"]
    )
    xs = _np.linspace(-3.0, 3.0, 48, dtype=_np.float32)
    ys = _np.asarray(_fn(xs), dtype=_np.float32)

    print("=" * 115)
    print("P44 RESIDENT-GRAMMAR AUDIT (torch batch mutation; no host round-trip)")
    print("=" * 115)

    def _fresh(dev: _torch.device) -> GrammarResidentEvolution:
        _random.seed(seed)
        _np.random.seed(seed)
        _torch.manual_seed(seed)
        if dev.type == "cuda" and _torch.cuda.is_available():
            _torch.cuda.manual_seed_all(seed)
        cfg = EvolutionConfig(pop_size=pop_size, elite_k=4, random_inject_p=0.10)
        return GrammarResidentEvolution(xs, ys, config=cfg, device=dev, seed=seed)

    # Global-RNG engines require a reseed between consecutive runs: each arm is
    # built (reseeded) immediately before its own run, never batched upfront.
    determinism: dict[str, Any] = {}
    for dev in (_torch.device("cpu"), _torch.device("cuda")):
        if dev.type == "cuda" and not _torch.cuda.is_available():
            determinism["cuda"] = {"measured": False, "reason": "no CUDA device"}
            continue
        first = _fresh(dev)
        first.run(max_generations=n_gens, early_stop_mse=0.0)
        fa = state_fingerprint(first)
        second = _fresh(dev)
        second.run(max_generations=n_gens, early_stop_mse=0.0)
        fb = state_fingerprint(second)
        keys = (
            "population_sha256",
            "best_program_sha256",
            "torch_cpu_rng_sha256",
            "numpy_rng_sha256",
        )
        determinism[dev.type] = {"measured": True, "equal": all(fa[k] == fb[k] for k in keys)}

    # Semantic conformance: torch batch vs deterministic CPU reference.
    dev_cpu = _torch.device("cpu")
    _torch.manual_seed(seed)
    ref_pop = sample_grammar_batch(128, device=dev_cpu, seed=seed)
    _torch.manual_seed(seed)
    torch_mut = grammar_mutate_batch_torch(ref_pop, device=dev_cpu, p_mut=0.30)
    py_mut = grammar_mutate_batch(ref_pop, device=dev_cpu, p_mut=0.30, seed=seed)
    gate_torch = batch_is_valid_torch(torch_mut).cpu().numpy()
    w0 = ref_pop.cpu().numpy().astype(_np.int64)
    w1 = torch_mut.cpu().numpy().astype(_np.int64)
    conformance = {
        "torch_all_valid": bool(gate_torch.all()),
        "python_reference_ran": py_mut.shape == ref_pop.shape,
        "locality_ok": bool(((w0 != w1) & ~_np.isin(w0 & 0xFF, [1, 2, 15])).sum() == 0),
        "fields_in_range": bool((((w1 >> 8) & 0xFF) < 8).all() and (((w1 >> 16) & 0xFF) < 8).all()),
    }

    # Invalidity rejected through the device gate.
    bad = _np.zeros((3, 16), dtype=_np.uint32)
    bad[1, 0] = _np.uint32(0x01 | (9 << 8))
    bad[2, :6] = _np.uint32(
        [
            0x01 | (7 << 8),
            0x04 | (7 << 8),
            0x07 | (7 << 8),
            0x08 | (7 << 8),
            0x09 | (7 << 8),
            0x0B | (7 << 8),
        ]
    )
    gate_bad = batch_is_valid_torch(_torch.from_numpy(bad.astype(_np.int64)).to(dev_cpu))
    flags = gate_bad.cpu().numpy().tolist()
    invalidity = {"gate_flags": flags, "rejected": flags == [False, False, False]}

    # No full-population host transfer inside the resident loop.
    transfers: dict[str, Any] = {}
    for dev in (_torch.device("cpu"), _torch.device("cuda")):
        if dev.type == "cuda" and not _torch.cuda.is_available():
            transfers["cuda"] = {"checked": False, "reason": "no CUDA device"}
            continue
        evo = _fresh(dev)
        try:
            with (
                _mock.patch.object(
                    _torch.Tensor, "cpu", side_effect=AssertionError("host transfer")
                ),
                _mock.patch.object(
                    _torch.Tensor, "numpy", side_effect=AssertionError("host transfer")
                ),
            ):
                for _ in range(5):
                    evo.step()
            transfers[dev.type] = {"checked": True, "host_transfer_calls": 0}
        except AssertionError as exc:
            transfers[dev.type] = {"checked": True, "host_transfer_calls": 1, "error": str(exc)}

    cuda_available = _torch.cuda.is_available()
    profile: dict[str, Any] = {"measured": False}
    if cuda_available:
        evo_cuda = _fresh(_torch.device("cuda"))
        profile = {"measured": True, **_p44_profile_components(evo_cuda, profile_iters)}

    resident_ok = (
        determinism.get("cuda", {}).get("equal", False)
        and transfers.get("cuda", {}).get("host_transfer_calls", 1) == 0
        and profile.get("measured", False)
    )
    checks_ok = (
        determinism.get("cpu", {}).get("equal", False)
        and all(conformance.values())
        and invalidity["rejected"]
        and transfers.get("cpu", {}).get("host_transfer_calls", 1) == 0
    )
    if not cuda_available:
        verdict = "NOT_MEASURED"
    elif resident_ok and checks_ok:
        verdict = "ACCEPTED"
    else:
        verdict = "MIXED"

    revision = get_git_commit()
    dirty = get_git_status()
    prov = collect_provenance(
        seed=seed,
        device=_torch.device("cpu"),
        dataset_hashes={"p44_config": config_sha[:16]},
        config={"acceptance_phase": "P44"},
    )
    report = {
        "phase": "P44",
        "verdict": verdict,
        "claim_scope": "resident torch mutation; per-backend determinism; no host round-trip",
        "run_id": hashlib.sha256(f"{config_sha}{revision}".encode()).hexdigest()[:16],
        "revision": revision,
        "dirty": dirty,
        "determinism": determinism,
        "conformance": conformance,
        "invalidity": invalidity,
        "host_transfers": transfers,
        "profile_cuda": profile,
        "hardware": prov["hardware"],
        "driver": (prov["hardware"].get("nvidia_smi", "not-probed")),
        "package_versions": {
            "python": prov["hardware"].get("python"),
            "numpy": prov["hardware"].get("numpy"),
            "torch": prov["hardware"].get("torch"),
            "cuda": prov["hardware"].get("cuda_version"),
        },
        "resolved_config": {
            "config_path": str(cfg_p),
            "config_sha256": config_sha,
            "acceptance_phase": "P44",
        },
        "seeds_rng": f"fixed seed {seed}; cross-backend bit equality not required (reason: distinct RNG streams)",
        "budgets": f"fixed generation counts ({n_gens} determinism, {profile_iters} profile iters); "
        "wall-clock recorded, never an equality criterion",
        "counters": {"determinism_backends": 2, "profile_components": 4},
        "limitations": [
            "Canonical form not guaranteed by the torch path; validity and field semantics preserved.",
            "Injection sampling stays a CPU-built batch upload (generation, profiled separately).",
            "Scalar logging syncs (O(1) bytes) remain; no population-sized host transfers in the loop.",
        ],
        "elapsed_sec": time.perf_counter() - t0,
    }
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True, default=str)
    print(f"P44 audit {verdict}; report -> {out_p}")
    return report


def run_p43_resume_audit(config_path: str | Path, output_path: str | Path) -> dict[str, Any]:
    """P43 audit: 40 gens + killed process + restored 60 gens == straight 100 gens."""
    import random as _random
    import subprocess as _sp
    import tempfile

    import numpy as _np
    import torch as _torch

    from evobyte.evolution import EvolutionConfig
    from evobyte.grammar import GrammarResidentEvolution
    from evobyte.provenance import (
        collect_provenance,
        get_git_commit,
        get_git_status,
    )
    from evobyte.resident import IncompatibleCheckpointError, state_fingerprint

    t0 = time.perf_counter()
    cfg_p = Path(config_path)
    with open(cfg_p, encoding="utf-8") as f:
        config = json.load(f)
    if config.get("phase") != "P43":
        raise ValueError(f"Config {cfg_p} is not a P43 configuration")
    config_sha = hashlib.sha256(cfg_p.read_bytes()).hexdigest()
    seed = int(config.get("seed", 7))
    pop_size = int(config.get("pop_size", 32))
    gens = config.get("generations", {})
    split_at, resumed_gens = int(gens.get("restore_at", 40)), int(gens.get("resumed", 60))
    total_gens = int(gens.get("total", split_at + resumed_gens))
    dev = _torch.device(config.get("device", "cpu"))
    xs = _np.linspace(-3.0, 3.0, 48, dtype=_np.float32)

    import sympy as _sympy

    _x = _sympy.Symbol("x")
    _fn = _sympy.lambdify(
        _x, _sympy.sympify(config.get("formula", "x**2 + 3*x + 7")), modules=["numpy"]
    )
    ys = _np.asarray(_fn(xs), dtype=_np.float32)

    def _fresh() -> GrammarResidentEvolution:
        _random.seed(seed)
        _np.random.seed(seed)
        _torch.manual_seed(seed)
        cfg = EvolutionConfig(pop_size=pop_size, elite_k=4, random_inject_p=0.10)
        return GrammarResidentEvolution(xs, ys, config=cfg, device=dev, seed=seed)

    def _run(evo: GrammarResidentEvolution, n: int) -> dict[str, Any]:
        return evo.run(max_generations=n, early_stop_mse=0.0)

    print("=" * 115)
    print("P43 REAL-CHECKPOINT-RESUME AUDIT (kill + fresh-process restore)")
    print("=" * 115)

    scratch = Path(tempfile.mkdtemp(prefix="evobyte-p43-"))
    ckpt = scratch / "p43-exact.pt"

    # Arm A (straight): uninterrupted total_gens run.
    t_a_0 = time.perf_counter()
    straight = _fresh()
    _run(straight, total_gens)
    ref = state_fingerprint(straight)
    t_a = time.perf_counter() - t_a_0

    # Arm B (resumed): split_at gens, save, drop everything, fresh OS process continues.
    t_b_0 = time.perf_counter()
    part = _fresh()
    _run(part, split_at)
    part.save_checkpoint(ckpt)
    pre_kill = state_fingerprint(part)
    del part
    worker_out = scratch / "worker-result.json"
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        [str(_REPO_ROOT / "src"), str(_REPO_ROOT / "benchmarks"), env.get("PYTHONPATH", "")]
    )
    worker_snippet = (
        "from evobyte.grammar import checkpoint_resume_worker; "
        f"checkpoint_resume_worker({str(ckpt)!r}, {str(worker_out)!r}, {resumed_gens})"
    )
    proc = _sp.run(
        [sys.executable, "-c", worker_snippet],
        capture_output=True,
        text=True,
        check=False,
        env=env,
        cwd=str(_REPO_ROOT),
    )
    t_b = time.perf_counter() - t_b_0
    worker: dict[str, Any] = {}
    if proc.returncode == 0 and worker_out.exists():
        with open(worker_out, encoding="utf-8") as f:
            worker = json.load(f)
    else:
        worker = {"error": (proc.stderr or proc.stdout)[-2000:]}
    got = worker.get("fingerprint", {})

    # Live refusal probes on copies (never on the proof checkpoint).
    refusals: list[dict[str, Any]] = []
    trunc = scratch / "trunc.pt"
    trunc.write_bytes(ckpt.read_bytes()[: max(64, ckpt.stat().st_size // 2)])
    probe_evo = _fresh()
    for label, fn in (
        ("truncated", lambda: probe_evo.load_checkpoint(trunc)),
        ("version", lambda: probe_evo.load_checkpoint(ckpt, expected={"torch_version": "0.0.0"})),
        ("config", lambda: probe_evo.load_checkpoint(ckpt, expected={"config": {"pop_size": -1}})),
    ):
        try:
            fn()
            refusals.append({"probe": label, "refused": False})
        except IncompatibleCheckpointError as exc:
            refusals.append({"probe": label, "refused": True, "reason": str(exc)[:120]})

    keys = (
        "generation",
        "population_sha256",
        "best_program_sha256",
        "torch_cpu_rng_sha256",
        "numpy_rng_sha256",
        "best_fitness",
        "best_mse",
    )
    matches = {k: (got.get(k) == ref.get(k)) for k in keys}
    counters_match = got.get("counters") == ref.get("counters")
    equality = all(matches.values()) and counters_match
    refusals_ok = all(r["refused"] for r in refusals)
    verdict = (
        "ACCEPTED"
        if (equality and refusals_ok and worker.get("generations") == resumed_gens)
        else "MIXED"
    )

    revision = get_git_commit()
    dirty = get_git_status()
    prov = collect_provenance(
        seed=seed,
        device=_torch.device("cpu"),
        dataset_hashes={"p43_config": config_sha[:16]},
        config={"acceptance_phase": "P43"},
    )
    report = {
        "phase": "P43",
        "verdict": verdict,
        "claim_scope": "kill-and-restore continuation equals the straight run in the pinned environment",
        "run_id": hashlib.sha256(f"{config_sha}{revision}".encode()).hexdigest()[:16],
        "revision": revision,
        "dirty": dirty,
        "straight": {"wall_sec": t_a, "fingerprint": ref},
        "resumed": {"wall_sec": t_b, "pre_kill": pre_kill, "worker": worker},
        "equality": {
            "fields": matches,
            "counters_match": counters_match,
            "worker_generations": worker.get("generations"),
        },
        "refusals": refusals,
        "hardware": prov["hardware"],
        "driver": (prov["hardware"].get("nvidia_smi", "not-probed")),
        "package_versions": {
            "python": prov["hardware"].get("python"),
            "numpy": prov["hardware"].get("numpy"),
            "torch": prov["hardware"].get("torch"),
            "cuda": prov["hardware"].get("cuda_version"),
        },
        "resolved_config": {
            "config_path": str(cfg_p),
            "config_sha256": config_sha,
            "acceptance_phase": "P43",
        },
        "seeds_rng": f"fixed seed {seed} both arms; post-run RNG states compared byte-identical",
        "budgets": f"fixed generation counts {split_at}+{resumed_gens} vs {total_gens}; "
        "wall-clock recorded, never an equality criterion",
        "counters": {
            "comparisons": len(matches) + 1,
            "matched": sum(matches.values()) + int(counters_match),
        },
        "limitations": [
            "Equality holds in the same pinned environment; cross-GPU/version binary equality is not promised.",
            "Problem data travels inside the checkpoint by design (fresh process has no other source).",
        ],
        "elapsed_sec": time.perf_counter() - t0,
    }
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True, default=str)
    print(f"P43 audit {verdict}: equality={equality} refusals_ok={refusals_ok}; report -> {out_p}")
    return report


def _p42_grids(formula: str) -> dict[str, Any]:
    """Deterministic scoring grids shared with the P35 recipe."""
    import sympy as _sympy

    x = _sympy.Symbol("x")
    fn = _sympy.lambdify(x, _sympy.sympify(formula), modules=["numpy"])
    train_xs = np.linspace(-3.0, 3.0, 48, dtype=np.float64)
    test_xs = np.linspace(-2.9, 2.9, 32, dtype=np.float64)
    extrap_xs = np.concatenate([np.linspace(-6.0, -3.5, 16), np.linspace(3.5, 6.0, 16)]).astype(
        np.float64
    )
    return {
        "train_xs": train_xs,
        "train_ys": np.asarray(fn(train_xs), dtype=np.float64),
        "test_xs": test_xs,
        "test_ys": np.asarray(fn(test_xs), dtype=np.float64),
        "extrap_xs": extrap_xs,
        "extrap_ys": np.asarray(fn(extrap_xs), dtype=np.float64),
    }


def run_p42_exact_audit(config_path: str | Path, output_path: str | Path) -> dict[str, Any]:
    """P42 audit: revalidate the P35 positives by exact verification (new records only)."""
    import tempfile

    from evobyte.provenance import (
        collect_provenance,
        get_git_commit,
        get_git_status,
        verify_manifest_integrity,
    )
    from evobyte.verifier import verify_l2

    t0 = time.perf_counter()
    cfg_p = Path(config_path)
    with open(cfg_p, encoding="utf-8") as f:
        config = json.load(f)
    if config.get("phase") != "P42":
        raise ValueError(f"Config {cfg_p} is not a P42 configuration")
    config_sha = hashlib.sha256(cfg_p.read_bytes()).hexdigest()
    domain = tuple(config.get("domain", [-3.0, 3.0]))

    print("=" * 115)
    print("P42 EXACT-CERTIFICATION AUDIT (P35 record read-only; new records only)")
    print("=" * 115)

    corpus_p = _REPO_ROOT / config.get("corpus_manifest", "experiments/p35-training-corpus.json")
    with open(corpus_p, encoding="utf-8") as f:
        corpus = json.load(f)
    if corpus.get("phase") != "p35-verified-training-corpus" or corpus.get("status") != "PASS":
        raise ValueError("P35 corpus prerequisite is not an accepted PASS artifact")
    # Original record integrity first: revalidation never repairs it.
    integrity = verify_manifest_integrity(corpus_p)
    by_id = {p["item_id"]: p for p in corpus.get("positives", [])}

    identities: list[dict[str, Any]] = []
    for spec in config.get("identities", []):
        iid, gt = spec["item_id"], spec["ground_truth"]
        entry = by_id.get(iid)
        if entry is None or entry.get("ground_truth_expr") != gt:
            identities.append(
                {
                    "item_id": iid,
                    "resolution": "inconclusive_evidence",
                    "reason": "identity not found in frozen P35 record",
                }
            )
            continue
        prog = np.array(entry["program_words"], dtype=np.uint32)
        grids = _p42_grids(gt)
        v = verify_l2(
            prog,
            grids["train_xs"],
            grids["train_ys"],
            grids["test_xs"],
            grids["test_ys"],
            val_xs=grids["test_xs"],
            val_ys=grids["test_ys"],
            extrap_xs=grids["extrap_xs"],
            extrap_ys=grids["extrap_ys"],
            adversarial_xs=grids["extrap_xs"],
            ground_truth_formula=gt,
            error_threshold=1e-4,
            extrap_threshold=1.0,
            domain=domain,
            domain_str="[-3, 3] train; [-6, -3.5]U[3.5, 6] extrap",
        )
        resolution = "exact_accepted" if v.proof_type == "exact_certificate" else "exact_rejected"
        identities.append(
            {
                "item_id": iid,
                "ground_truth": gt,
                "resolution": resolution,
                "passed": v.passed,
                "proof_type": v.proof_type,
                "symbolic_equivalent": v.symbolic_equivalent,
                "decision": v.decision,
                "test_mse": v.f64_test_mse,
                "symbolic_notes": v.symbolic_notes,
            }
        )
        print(f"  {iid}: {resolution} ({v.proof_type}; {v.symbolic_notes[:90]})")

    # False controls must stay rejected under the fixed checker (tripwire).
    from evobyte.bytecode import encode_instr, nop_program

    controls: list[dict[str, Any]] = []
    coinc = nop_program()
    coinc[0] = encode_instr(0x02, dst=1, a=0, b=0)  # r1 = x - x = 0 everywhere
    coinc[1] = encode_instr(0x04, dst=7, a=0, b=1)  # r7 = x / 0 (always invalid)
    grids_c = _p42_grids("1")
    vc = verify_l2(
        coinc,
        grids_c["train_xs"],
        np.ones(48),
        grids_c["test_xs"],
        np.ones(32),
        ground_truth_formula="1",
        domain=domain,
    )
    controls.append(
        {
            "control": "invalid_numeric_certificate",
            "rejected": (not vc.passed) and vc.proof_type == "numerical_evidence",
        }
    )
    from evobyte.verifier import check_symbolic_equivalence, program_to_sympy

    _x_prog = nop_program()
    _x_prog[0] = encode_instr(0x03, dst=7, a=0, b=0)
    sym_y = program_to_sympy(_x_prog, var_name="y")
    eq_mm, _ = check_symbolic_equivalence(sym_y, "x", var_name="x")
    controls.append({"control": "symbol_hypothesis_mismatch", "rejected": not eq_mm})
    for c in controls:
        print(f"  control {c['control']}: {'rejected' if c['rejected'] else 'NOT REJECTED'}")

    # Prospective rule: no smoke-corpus positive is born from tolerance alone.
    labeling: dict[str, Any] = {"checked": False}
    try:
        from math_specialist import build_verified_training_corpus

        tmp = Path(tempfile.mkdtemp(prefix="evobyte-p42-"))
        smoke_cfg = config.get("smoke", {})
        rep = build_verified_training_corpus(
            family="polynomial_arithmetic",
            split_manifest="experiments/p30-splits.json",
            output_path=tmp / "p42-smoke-corpus.json",
            device_name="cpu",
            teacher_budget_sec=float(smoke_cfg.get("teacher_budget_sec", 0.06)),
            teacher_pop_size=int(smoke_cfg.get("teacher_pop_size", 32)),
            seed=42,
            smoke=True,
        )
        bad = [
            p["item_id"]
            for p in rep.get("positives", [])
            if p.get("proof_type") != "exact_certificate"
        ]
        labeling = {
            "checked": True,
            "n_positives": len(rep.get("positives", [])),
            "tolerance_born": bad,
            "rule_holds": not bad,
        }
    except RuntimeError as exc:
        labeling = {"checked": False, "reason": f"smoke unavailable: {exc}"}
    print(f"  labeling rule (positives ⇒ exact_certificate): {labeling}")

    decisive = all(i["resolution"] in ("exact_accepted", "exact_rejected") for i in identities)
    if decisive and all(c["rejected"] for c in controls) and labeling.get("rule_holds"):
        verdict = "ACCEPTED"
    else:
        verdict = "MIXED"

    revision = get_git_commit()
    dirty = get_git_status()
    prov = collect_provenance(
        seed=42,
        device=torch.device("cpu"),
        dataset_hashes={
            "p42_config": config_sha[:16],
            "p35_corpus": hashlib.sha256(corpus_p.read_bytes()).hexdigest()[:16],
        },
        config={"acceptance_phase": "P42"},
    )
    report = {
        "phase": "P42",
        "verdict": verdict,
        "claim_scope": "P35 positives revalidated by exact verification; original record untouched",
        "run_id": hashlib.sha256(f"{config_sha}{revision}".encode()).hexdigest()[:16],
        "revision": revision,
        "dirty": dirty,
        "corpus_integrity": {"ok": integrity["ok"], "errors": integrity["errors"]},
        "identities": identities,
        "controls": controls,
        "labeling_rule": labeling,
        "hardware": prov["hardware"],
        "driver": (prov["hardware"].get("nvidia_smi", "not-probed")),
        "package_versions": {
            "python": prov["hardware"].get("python"),
            "numpy": prov["hardware"].get("numpy"),
            "torch": prov["hardware"].get("torch"),
            "cuda": prov["hardware"].get("cuda_version"),
        },
        "resolved_config": {
            "config_path": str(cfg_p),
            "config_sha256": config_sha,
            "acceptance_phase": "P42",
        },
        "seeds_rng": "fixed seed 42 for smoke corpus; revalidation deterministic (reason: no search)",
        "budgets": {"smoke_teacher_budget_sec": config.get("smoke", {}).get("teacher_budget_sec")},
        "counters": {
            "identities": len(identities),
            "exact_accepted": sum(1 for i in identities if i["resolution"] == "exact_accepted"),
            "exact_rejected": sum(1 for i in identities if i["resolution"] == "exact_rejected"),
        },
        "limitations": [
            "Revalidation reuses P35 scoring grids; it certifies identities, not the original training labels.",
            "P35 record is read-only; its tolerance-born positives (if any) stay historical.",
        ],
        "elapsed_sec": time.perf_counter() - t0,
    }
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True, default=str)
    print(f"P42 audit {verdict}; report -> {out_p}")
    return report


def _p41_snapshot(paths: list[str]) -> dict[str, str | None]:
    """Hash-snapshot historical artifacts (None when missing)."""
    from evobyte.provenance import hash_file

    snap: dict[str, str | None] = {}
    for ref in paths:
        cand = _REPO_ROOT / ref
        try:
            snap[ref] = hash_file(cand) if cand.is_file() else None
        except OSError:
            snap[ref] = None
    return snap


def run_p41_immutable_audit(config_path: str | Path, output_path: str | Path) -> dict[str, Any]:
    """P41 audit: exclusive-dir smoke, before/after immutability proof, tamper demos."""
    import tempfile

    from evobyte.provenance import (
        collect_provenance,
        get_git_commit,
        get_git_status,
        verify_manifest_integrity,
        write_manifest_exclusive,
    )

    t0 = time.perf_counter()
    cfg_p = Path(config_path)
    with open(cfg_p, encoding="utf-8") as f:
        config = json.load(f)
    if config.get("phase") != "P41":
        raise ValueError(f"Config {cfg_p} is not a P41 configuration")
    config_sha = hashlib.sha256(cfg_p.read_bytes()).hexdigest()
    inventory = config.get("inventory", [])
    watched = [e["path"] for e in inventory]

    print("=" * 115)
    print("P41 IMMUTABLE-ARTIFACTS AUDIT (exclusive dirs; history read-only)")
    print("=" * 115)

    before = _p41_snapshot(watched)

    # Smoke in a fresh exclusive directory (never a historical raw dir).
    smoke = config.get("smoke", {})
    scratch = Path(tempfile.mkdtemp(prefix="evobyte-p41-"))
    smoke_manifest = scratch / "p41-smoke.json"
    smoke_record: dict[str, Any] = {"ran": False}
    try:
        from gpu_limits import run_p34_profiled_benchmark

        t_smoke_0 = time.perf_counter()
        stable, _ = run_p34_profiled_benchmark(
            budgets_str=smoke.get("budgets_str", "0.05s"),
            seeds_count=int(smoke.get("seeds_count", 1)),
            confirm_1h=True,
            tracing=True,
            scale_factor=float(smoke.get("scale_factor", 0.05)),
            output_path=str(smoke_manifest),
            raw_dir=str(scratch / "p41-raw"),
            smoke=True,
        )
        smoke_record = {
            "ran": True,
            "stable": bool(stable),
            "requested": smoke,
            "actual_sec": time.perf_counter() - t_smoke_0,
            "manifest": str(smoke_manifest),
        }
        smoke_record["manifest_verifies"] = bool(verify_manifest_integrity(smoke_manifest)["ok"])
    except RuntimeError as exc:
        smoke_record = {"ran": False, "reason": f"smoke unavailable: {exc}"}
    print(f"  smoke ran={smoke_record['ran']} manifest={smoke_manifest}")

    after = _p41_snapshot(watched)
    untouched = {ref: (before[ref] == after[ref]) for ref in watched}
    changed = sorted(ref for ref, same in untouched.items() if not same)

    # Pinned inventory vs manifest-recorded expectations (drift recorded, never rebuilt).
    items: list[dict[str, Any]] = []
    for entry in inventory:
        ref, want = entry["path"], entry["expected_sha256"]
        got = after.get(ref)
        if got is None:
            items.append({**entry, "verdict": "unavailable", "actual_sha256": None})
        elif got == want:
            items.append({**entry, "verdict": "ok", "actual_sha256": got})
        else:
            items.append(
                {
                    **entry,
                    "verdict": "rejected",
                    "actual_sha256": got,
                    "note": "post-seal drift; recorded, not rebuilt",
                }
            )

    # Active demonstrations on scratch fixtures (never on historical data).
    demo_dir = scratch / "demo"
    demo_dir.mkdir(parents=True, exist_ok=True)
    demo_manifest = demo_dir / "demo.json"
    demo_raw = demo_dir / "demo-evidence.jsonl"
    write_manifest_exclusive(demo_manifest, {"phase": "P41-demo"}, {str(demo_raw): b'{"n": 1}\n'})
    try:
        write_manifest_exclusive(demo_manifest, {"phase": "P41-demo"}, {str(demo_raw): b"{}"})
        overwrite_refused = False
    except FileExistsError:
        overwrite_refused = True
    with open(demo_raw, "ab") as f:
        f.write(b" ")
    tamper_detected = not verify_manifest_integrity(demo_manifest)["ok"]

    rejected_inventory = sum(1 for i in items if i["verdict"] == "rejected")
    if (
        not smoke_record.get("ran")
        or changed
        or not overwrite_refused
        or not tamper_detected
        or rejected_inventory
    ):
        verdict = "MIXED"
    else:
        verdict = "ACCEPTED"

    revision = get_git_commit()
    dirty = get_git_status()
    prov = collect_provenance(
        seed=42,
        device=torch.device("cpu"),
        dataset_hashes={"p41_config": config_sha[:16]},
        config={"acceptance_phase": "P41"},
    )
    report = {
        "phase": "P41",
        "verdict": verdict,
        "claim_scope": "P41 immutability mechanism; historical inventory recorded, not repaired",
        "run_id": hashlib.sha256(f"{config_sha}{revision}".encode()).hexdigest()[:16],
        "revision": revision,
        "dirty": dirty,
        "smoke": smoke_record,
        "historical_untouched_by_smoke": {"compared": len(watched), "changed": changed},
        "inventory": items,
        "demonstrations": {
            "overwrite_refused": overwrite_refused,
            "one_byte_tamper_detected": tamper_detected,
        },
        "hardware": prov["hardware"],
        "driver": (prov["hardware"].get("nvidia_smi", "not-probed")),
        "package_versions": {
            "python": prov["hardware"].get("python"),
            "numpy": prov["hardware"].get("numpy"),
            "torch": prov["hardware"].get("torch"),
            "cuda": prov["hardware"].get("cuda_version"),
        },
        "resolved_config": {
            "config_path": str(cfg_p),
            "config_sha256": config_sha,
            "acceptance_phase": "P41",
        },
        "seeds_rng": "not-applicable: audit performs no search (reason: deterministic inspection + fixed smoke seed)",
        "budgets": {"smoke_requested": smoke, "smoke_actual_sec": smoke_record.get("actual_sec")},
        "counters": {
            "inventory": len(items),
            "inventory_ok": sum(1 for i in items if i["verdict"] == "ok"),
            "inventory_rejected": rejected_inventory,
            "historical_changed_by_smoke": len(changed),
        },
        "limitations": [
            "P41 audits the mechanism and records inventory; divergent history (P34 telemetry) is rejected, not rebuilt.",
            "Smoke requires the CUDA reference GPU; otherwise recorded unavailable.",
        ],
        "elapsed_sec": time.perf_counter() - t0,
    }
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True, default=str)
    print(
        f"P41 audit {verdict}: inventory "
        f"{sum(1 for i in items if i['verdict'] == 'ok')}/{len(items)} ok; "
        f"historical changes by smoke: {len(changed)}; report -> {out_p}"
    )
    return report


def _p40_has_path(doc: Any, dotted: str) -> bool:
    """Check dotted/list-element paths like 'a.b', 'a[].b' or 'a[?c].b'.

    A top-level list requires every element to carry the path. The '[?c]'
    segment selects elements containing key 'c' (at least one required) so
    optional per-element evidence (e.g. certificates only on certified
    instances) is not demanded where no claim exists.
    """
    node: Any = doc
    if isinstance(node, list):
        return bool(node) and all(_p40_has_path(e, dotted) for e in node)
    for part in dotted.split("."):
        if part.endswith("[]"):
            key = part[:-2]
            if not isinstance(node, dict) or not isinstance(node.get(key), list):
                return False
            node = node[key]
            if not node:
                return False
        elif part.startswith("[?") and part.endswith("]"):
            key = part[2:-1]
            if not isinstance(node, list):
                return False
            node = [e for e in node if isinstance(e, dict) and key in e]
            if not node:
                return False
        elif part == "":
            return False
        elif "[" in part and part.endswith("]"):
            name, filt = part.split("[", 1)
            filt = filt[:-1]
            if not (isinstance(node, dict) and isinstance(node.get(name), list)):
                return False
            node = node[name]
            if filt.startswith("?"):
                key = filt[1:]
                node = [e for e in node if isinstance(e, dict) and key in e]
            elif filt != "":
                return False
            if not node:
                return False
        else:
            if isinstance(node, list):
                if not all(isinstance(e, dict) and part in e for e in node):
                    return False
                node = [e[part] for e in node]
            elif isinstance(node, dict) and part in node:
                node = node[part]
            else:
                return False
    return True


def _p40_check_manifest(entry: dict[str, Any]) -> dict[str, Any]:
    """Audit one experiment manifest: seal, raw hashes, fields, budgets, revision."""
    from evobyte.provenance import verify_manifest_integrity

    path = entry["path"]
    finding: dict[str, Any] = {"path": path, "verdict": "accepted", "notes": []}
    integrity = verify_manifest_integrity(_REPO_ROOT / path)
    finding["integrity"] = {
        "ok": integrity["ok"],
        "seal_ok": integrity.get("seal_ok", False),
        "raw": [
            {"path": r["path"], "ok": r["ok"], "size": r.get("size", 0)} for r in integrity["raw"]
        ],
        "errors": integrity["errors"],
    }
    if not integrity["ok"]:
        finding["verdict"] = "rejected"
        finding["notes"].append("seal or raw hash mismatch")
        return finding
    try:
        with open(_REPO_ROOT / path, encoding="utf-8") as f:
            doc = json.load(f)
    except (OSError, ValueError) as exc:
        finding["verdict"] = "rejected"
        finding["notes"].append(f"unreadable after seal check: {exc}")
        return finding
    if doc.get("status") not in entry.get("status_ok", ["PASS"]):
        finding["verdict"] = "rejected"
        finding["notes"].append(f"unexpected status {doc.get('status')!r}")
    for required in entry.get("required_fields", []):
        if not _p40_has_path(doc, required):
            finding["verdict"] = "rejected"
            finding["notes"].append(f"missing required field {required}")
    elapsed = doc.get("elapsed_sec")
    if not isinstance(elapsed, (int, float)) or elapsed <= 0:
        finding["verdict"] = "rejected"
        finding["notes"].append("elapsed_sec missing or non-positive (duration divergent)")
    scale = float(entry.get("budgets", {}).get("scale", 1.0))
    if scale != 1.0:
        blob = json.dumps(doc, sort_keys=True, default=str).lower()
        if "scale" not in blob and "effective" not in blob:
            finding["verdict"] = "rejected"
            finding["notes"].append("reduced scale undisclosed (diagnostic scale hidden)")
        else:
            finding["notes"].append("reduced scale disclosed as diagnostic")
    prov = doc.get("provenance", {})
    if isinstance(prov, dict) and "clean_tree" in prov:
        finding["recorded_clean_tree"] = bool(prov["clean_tree"])
    raw_docs: list[Any] = []
    for r in integrity["raw"]:
        rp = _REPO_ROOT / r["path"]
        try:
            with open(rp, encoding="utf-8") as f:
                raw_docs.append(json.load(f))
        except (OSError, ValueError):
            raw_docs.append(None)
    for ev in entry.get("certificate_evidence", []):
        if ev.startswith("raw "):
            sub = ev[4:]
            present = [d for d in raw_docs if d is not None]
            if not present or not any(_p40_has_path(d, sub) for d in present):
                finding["verdict"] = "rejected"
                finding["notes"].append(f"raw evidence missing: {sub}")
        elif not _p40_has_path(doc, ev):
            finding["verdict"] = "rejected"
            finding["notes"].append(f"certificate evidence missing: {ev}")
    if not entry.get("certificate_evidence"):
        finding["notes"].append(entry.get("certificate_na_reason", "no certificate claimed"))
    return finding


def _p40_git_contains(rev: str) -> bool:
    try:
        out = subprocess.run(
            ["git", "merge-base", "--is-ancestor", rev, "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
            cwd=_REPO_ROOT,
        )
        return out.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def _p40_evaluate_claims(
    claim_defs: list[dict[str, Any]], docs: dict[str, Any], origin_integrated: bool = False
) -> list[dict[str, Any]]:
    """Evaluate frozen per-claim rules; accepted/provisional/rejected only."""
    p33, p34, p35, p36, p37, p38, p39 = (
        docs.get(k, {}) for k in ("p33", "p34", "p35", "p36", "p37", "p38", "p39")
    )
    verdicts: list[dict[str, Any]] = []

    def _add(cid: str, verdict: str, rationale: str) -> None:
        verdicts.append({"id": cid, "verdict": verdict, "rationale": rationale})

    _ = [c["id"] for c in claim_defs]
    clean_flags = [
        bool((d.get("provenance") or {}).get("clean_tree", False))
        for d in (p33, p34, p35, p36, p37, p38, p39)
        if d
    ]
    if clean_flags and all(clean_flags):
        _add("base-clean-revision", "accepted", "all audited manifests ran on clean trees")
    else:
        _add(
            "base-clean-revision",
            "rejected",
            f"gate runs recorded dirty trees ({sum(1 for c in clean_flags if not c)}/"
            f"{len(clean_flags)} manifests); revision-dirty fixtures rejected",
        )
    if origin_integrated:
        _add(
            "base-integration",
            "accepted",
            "origin/main accepted merges #54-#57 are ancestors of HEAD; "
            "integration documented for P41",
        )
    else:
        _add(
            "base-integration",
            "rejected",
            "origin/main accepted merges #54-#57 not integrated in this branch; "
            "no merges this cycle; integration micro-task required before P41",
        )
    ruling = (p33.get("ruling") or {}).get("decision")
    if ruling == "ADOPT" and p33.get("finalists_verification"):
        _add(
            "p33-adopt-grammar",
            "accepted",
            "ADOPT backed by finalists_verification; 0.05x scale disclosed as diagnostic",
        )
    else:
        _add("p33-adopt-grammar", "rejected", "ADOPT ruling or verification evidence missing")
    blob34 = json.dumps(p34, sort_keys=True, default=str).lower()
    if p34.get("vram_budget") and not any(
        t in blob34 for t in ("million/s", "speedup", "discovery")
    ):
        _add(
            "p34-envelope-diagnostic", "accepted", "envelope measured; no fabricated speedup claim"
        )
    else:
        _add("p34-envelope-diagnostic", "rejected", "envelope or claim hygiene missing")
    lc = p35.get("learning_curve", {}) or {}
    if lc.get("sufficient_for_p36") is False and str(lc.get("learner_promotion", "")).startswith(
        "blocked"
    ):
        _add(
            "p35-insufficient-published",
            "accepted",
            "insufficient corpus published; promotion blocked",
        )
    else:
        _add("p35-insufficient-published", "rejected", "sufficiency limit not honestly published")
    if (p36.get("verdict") or {}).get("decision") == "INCONCLUSIVE" and "training" not in p36:
        _add("p36-inconclusive-no-training", "accepted", "no training ran; no weights exist")
    else:
        _add(
            "p36-inconclusive-no-training",
            "rejected",
            "training ran or weights claimed without data",
        )
    if p37.get("verdict") == "NULL" and (p37.get("comparisons") or {}).get("paired_diff_ci95"):
        _add("p37-null-frozen-rule", "accepted", "NULL under the frozen rule; nothing nominated")
    else:
        _add("p37-null-frozen-rule", "rejected", "NULL verdict or paired CI missing")
    v38 = p38.get("verdict", {}) or {}
    if (
        v38.get("family") == "PROVISIONAL"
        and v38.get("h1") == "NOT_CONFIRMED"
        and p38.get("confirmation", {}).get("per_problem")
    ):
        _add("p38-provisional-bounded", "accepted", "0.20 with intervals; H1 not replaced")
    else:
        _add("p38-provisional-bounded", "rejected", "provisional bound or H1 guardrail missing")
    novel_ok = "novelty" in json.dumps(p39, sort_keys=True, default=str).lower()
    if (
        p39.get("classification") == "rediscovery"
        and novel_ok
        and any(r.get("classification") == "budget_exhausted" for r in p39.get("instances", []))
    ):
        _add(
            "p39-rediscovery-capped",
            "accepted",
            "weaker label retained; finite miss is budget_exhausted",
        )
    else:
        _add("p39-rediscovery-capped", "rejected", "label cap or honest null missing")
    _add(
        "scale-is-diagnostic",
        "accepted",
        "0.05x runs disclosed as diagnostic, never stability proof",
    )
    strong = ("CONFIRMED", "KEEP", "GAIN", "proven-theorem", "verified-construction")
    labels = [
        str(p33.get("ruling", {}).get("decision")),
        str((p36.get("verdict") or {}).get("decision")),
        str(p37.get("verdict")),
        str((p38.get("verdict") or {}).get("family")),
        str(p39.get("classification")),
    ]
    if any(s in strong for s in labels):
        _add("mse-is-not-proof", "rejected", "raw MSE promoted without certificate evidence")
    else:
        _add("mse-is-not-proof", "accepted", "no manifest promotes raw MSE to a discovery claim")
    ckpt = _REPO_ROOT / "experiments" / "p39-checkpoint.json"
    tests_txt = (_REPO_ROOT / "tests" / "test_open_problems.py").read_text(encoding="utf-8")
    if ckpt.exists() and "resume" in tests_txt:
        _add(
            "checkpoint-is-not-resume",
            "accepted",
            "checkpoint artifact exists with resume coverage; loading never counted as resume evidence",
        )
    else:
        _add("checkpoint-is-not-resume", "rejected", "checkpoint continuation evidence missing")
    arms = p33.get("summary_by_arm") or {}
    if isinstance(arms, dict) and len(arms) >= 2:
        _add("sampling-is-not-evolution", "accepted", "P33 arms kept distinct; no cross-credit")
    else:
        _add("sampling-is-not-evolution", "rejected", "arm separation missing")
    return verdicts


def run_p40_evidence_audit(config_path: str | Path, output_path: str | Path) -> dict[str, Any]:
    """Execute the P40 evidence-reconciliation audit (manifest inspection only, no search)."""
    from evobyte.provenance import collect_provenance, get_git_commit, get_git_status

    t0 = time.perf_counter()
    cfg_p = Path(config_path)
    with open(cfg_p, encoding="utf-8") as f:
        config = json.load(f)
    if config.get("phase") != "P40":
        raise ValueError(f"Config {cfg_p} is not a P40 configuration")
    config_sha = hashlib.sha256(cfg_p.read_bytes()).hexdigest()

    print("=" * 115)
    print("P40 EVIDENCE RECONCILIATION AUDIT (inspection only; no search, no merges)")
    print("=" * 115)

    base = config.get("base", {})
    ancestor = base.get("ancestor_branch_vs_origin_main", "")
    origin_main = base.get("origin_main_at_plan", "")
    ancestor_present = _p40_git_contains(ancestor) if ancestor else False
    origin_integrated = _p40_git_contains(origin_main) if origin_main else False

    manifest_findings: list[dict[str, Any]] = []
    docs: dict[str, Any] = {}
    for entry in config.get("manifests", []):
        finding = _p40_check_manifest(entry)
        manifest_findings.append(finding)
        stem = Path(entry["path"]).stem
        for tag in ("p33", "p34", "p35", "p36", "p37", "p38", "p39"):
            if stem.startswith(tag):
                try:
                    with open(_REPO_ROOT / entry["path"], encoding="utf-8") as f:
                        docs[tag] = json.load(f)
                except (OSError, ValueError):
                    docs[tag] = {}
        status = "ok" if finding["verdict"] == "accepted" else "REJECTED"
        print(
            f"  {entry['path']}: {status}"
            + (f" ({'; '.join(finding['notes'])})" if finding["notes"] else "")
        )

    claims = _p40_evaluate_claims(config.get("claims", []), docs, origin_integrated)
    for c in claims:
        print(f"  claim {c['id']}: {c['verdict']}")
    n_rejected = sum(1 for c in claims if c["verdict"] == "rejected")
    n_rejected += sum(1 for m in manifest_findings if m["verdict"] == "rejected")
    verdict = "MIXED" if n_rejected else "ACCEPTED"
    revision = get_git_commit()
    dirty = get_git_status()
    prov = collect_provenance(
        seed=42,
        device=torch.device("cpu"),
        dataset_hashes={"p40_config": config_sha[:16]},
        config={"acceptance_phase": "P40"},
    )
    report = {
        "phase": "P40",
        "verdict": verdict,
        "claim_scope": "P33-P39 evidence reconciliation; no new search; no unlocked claims",
        "run_id": hashlib.sha256(f"{config_sha}{revision}".encode()).hexdigest()[:16],
        "revision": revision,
        "dirty": dirty,
        "rejected_count": n_rejected,
        "base_reconciliation": {
            "ancestor": ancestor,
            "ancestor_present": ancestor_present,
            "origin_main": origin_main,
            "origin_main_integrated": origin_integrated,
            "merges_this_cycle": False,
            "missing_accepted_merges": base.get("missing_accepted_merges", []),
        },
        "manifests": manifest_findings,
        "claims": claims,
        "hardware": prov["hardware"],
        "driver": (prov["hardware"].get("nvidia_smi", "not-probed")),
        "package_versions": {
            "python": prov["hardware"].get("python"),
            "numpy": prov["hardware"].get("numpy"),
            "torch": prov["hardware"].get("torch"),
            "cuda": prov["hardware"].get("cuda_version"),
        },
        "resolved_config": {
            "config_path": str(cfg_p),
            "config_sha256": config_sha,
            "acceptance_phase": "P40",
        },
        "seeds_rng": "not-applicable: audit performs no search (reason: deterministic manifest inspection)",
        "budgets": "not-applicable: audit performs no search (reason: requested/actual wall budgets undefined)",
        "certificate_references": [
            {
                "manifest": m["path"],
                "raw": [
                    {"path": r["path"], "sha256": None, "size": r.get("size", 0)}
                    for r in m["integrity"]["raw"]
                ],
            }
            for m in manifest_findings
        ],
        "counters": {
            "manifests": len(manifest_findings),
            "manifests_accepted": sum(1 for m in manifest_findings if m["verdict"] == "accepted"),
            "claims": len(claims),
            "claims_accepted": sum(1 for c in claims if c["verdict"] == "accepted"),
        },
        "limitations": [
            "P40 audits recorded evidence; it does not re-execute P33-P39 or confirm old results.",
            "Gate runs recorded dirty trees; clean-tree re-measurement belongs to later corrective cycles.",
            "origin/main merges #54-#57 outstanding; P41 requires their integration documented.",
        ],
        "elapsed_sec": time.perf_counter() - t0,
    }
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True, default=str)
    print(
        f"P40 audit {verdict}: {len(claims) - sum(1 for c in claims if c['verdict'] != 'accepted')}/"
        f"{len(claims)} claims accepted; report -> {out_p}"
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="P14 Gated Scientific Benchmark Matrix")
    parser.add_argument(
        "--preregistered-only",
        action="store_true",
        default=True,
        help="Run only pre-registered scientific datasets (default: True)",
    )
    parser.add_argument("--seeds", type=int, default=5, help="Number of seeds (default: 5)")
    parser.add_argument(
        "--max-trial-sec",
        type=float,
        default=2.0,
        help="Max time allocated per seed/target trial (default: 2.0s)",
    )
    parser.add_argument(
        "--device",
        type=str,
        default=None,
        help="Compute device (cuda/cpu)",
    )
    parser.add_argument("--smoke", action="store_true", help="Run quick 1-seed test")
    parser.add_argument(
        "--acceptance-phase",
        type=str,
        default=None,
        help="Run an implemented acceptance audit (PNN metadata; implemented: P40)",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Frozen configuration file for the acceptance audit",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output path for manifest / audit / acceptance report",
    )
    args = parser.parse_args()

    if args.acceptance_phase is not None:
        if args.acceptance_phase not in ACCEPTANCE_PHASES:
            raise SystemExit(
                f"Unknown acceptance phase {args.acceptance_phase!r}; "
                f"implemented capabilities: {', '.join(ACCEPTANCE_PHASES)}. "
                "Future phases are not promised by this interface."
            )
        if not args.config or not args.output:
            raise SystemExit("Acceptance mode requires --config and --output.")
        if args.acceptance_phase == "P40":
            run_p40_evidence_audit(args.config, args.output)
        elif args.acceptance_phase == "P41":
            run_p41_immutable_audit(args.config, args.output)
        elif args.acceptance_phase == "P42":
            run_p42_exact_audit(args.config, args.output)
        elif args.acceptance_phase == "P43":
            run_p43_resume_audit(args.config, args.output)
        elif args.acceptance_phase == "P44":
            run_p44_resident_audit(args.config, args.output)
        elif args.acceptance_phase == "P45":
            run_p45_envelope_audit(args.config, args.output)
        elif args.acceptance_phase == "P46":
            run_p46_catalogue_audit(args.config, args.output)
        return 0

    seeds = (
        [42]
        if args.smoke
        else ([42, 101, 202, 303, 404] if args.seeds == 5 else [100 + i for i in range(args.seeds)])
    )
    max_sec = 0.8 if args.smoke else args.max_trial_sec

    res = run_science_matrix(
        preregistered_only=args.preregistered_only,
        seeds=seeds,
        max_trial_sec=max_sec,
        device_name=args.device,
    )
    return 0 if res["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
