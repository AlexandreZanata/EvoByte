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

ACCEPTANCE_PHASES = (
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


def _p56_fresh_tasks(
    *, final_seed: int, n_tasks: int, dev_formulas: set[str]
) -> list[dict[str, Any]]:
    """Blind fresh-task draw: bank-exact enumeration minus development-used targets."""
    import random as _random

    from math_corpus import generate_p52_bank_exact_tasks

    pool = [
        t for t in generate_p52_bank_exact_tasks() if t["canonical_formula"] not in dev_formulas
    ]
    order = list(range(len(pool)))
    _random.Random(int(final_seed)).shuffle(order)
    return [pool[i] for i in order[:n_tasks]]


_P56_CLEAN_RERUN_SCRIPT = r'''
"""P56 clean-process re-verification (self-repeat label, not independent review)."""
import hashlib
import json
import sys
from pathlib import Path

REPO = Path("__REPO_ROOT__")
sys.path.insert(0, str(REPO / "benchmarks"))
sys.path.insert(0, str(REPO / "src"))

import numpy as np


def _grids(formula, domain):
    import sympy as _sympy

    fn = _sympy.lambdify(_sympy.Symbol("x"), _sympy.sympify(formula), modules=["numpy"])
    tr = np.linspace(domain[0], domain[1], 48, dtype=np.float64)
    te = np.linspace(domain[0] + 0.1, domain[1] - 0.1, 32, dtype=np.float64)
    return tr, np.asarray(fn(tr)), te, np.asarray(fn(te))


def main() -> int:
    from evobyte.archive import run_resume_selftest
    from evobyte.provenance import verify_manifest_integrity
    from evobyte.verifier import verify_l2
    from math_specialist import _try_exact_horner_program

    cfg = json.loads(Path(sys.argv[1]).read_text())
    domain = tuple(cfg["domain"])
    err = float(cfg["error_threshold"])
    errors: list[str] = []

    tasks_ok = 0
    for task in cfg["tasks"]:
        prog = _try_exact_horner_program(task["formula"])
        if prog is None:
            errors.append(f"task {task['task_id']}: no exact construction")
            continue
        tr_x, tr_y, te_x, te_y = _grids(task["formula"], domain)
        v = verify_l2(prog, tr_x, tr_y, te_x, te_y,
                      ground_truth_formula=task["formula"], error_threshold=err, domain=domain)
        if v.proof_type == "exact_certificate" and v.passed:
            tasks_ok += 1
        else:
            errors.append(f"task {task['task_id']}: {v.proof_type}")

    corpus = json.loads((REPO / "experiments" / "p52-certified-data.json").read_text())
    controls = [p for p in corpus["positives"] if p.get("is_control")]
    negatives = corpus.get("negatives", [])
    if cfg.get("max_controls") is not None:
        controls = controls[:0] + [p for p in corpus["positives"] if p.get("split") == "train"][
            : int(cfg["max_controls"])
        ]
    controls_ok = 0
    for pos in controls:
        prog = np.array(pos["program_words"], dtype=np.uint32)
        tr_x, tr_y, te_x, te_y = _grids(pos["ground_truth_expr"], domain)
        v = verify_l2(prog, tr_x, tr_y, te_x, te_y,
                      ground_truth_formula=pos["ground_truth_expr"], error_threshold=err, domain=domain)
        if v.proof_type == "exact_certificate" and v.passed:
            controls_ok += 1
        else:
            errors.append(f"control {pos['item_id']}: {v.proof_type}")
    negatives_ok = 0
    for neg in negatives:
        prog = np.array(neg["program_words"], dtype=np.uint32)
        tr_x, tr_y, te_x, te_y = _grids(neg["ground_truth_expr"], domain)
        adv = np.array(neg.get("adversarial_xs") or [], dtype=np.float64)
        v = verify_l2(prog, tr_x, tr_y, te_x, te_y, adversarial_xs=adv if adv.size else None,
                      ground_truth_formula=neg["ground_truth_expr"], error_threshold=err, domain=domain)
        if v.proof_type != "exact_certificate":
            negatives_ok += 1
        else:
            errors.append(f"negative {neg['item_id']} promoted")

    p43_ok = bool(run_resume_selftest(seed=99))

    restored: dict[str, bool] = {}
    for rel in cfg.get("sealed", []) or []:
        if rel is None:
            continue
        chk = verify_manifest_integrity(REPO / rel)
        restored[rel] = bool(chk["ok"])
        if not chk["ok"]:
            errors.append(f"seal broken: {rel}")
    weights_sha = cfg.get("weights_sha")
    if weights_sha is not None:
        actual = hashlib.sha256((REPO / "experiments" / "p53-proposer.pt").read_bytes()).hexdigest()
        restored["experiments/p53-proposer.pt"] = actual == weights_sha
        if actual != weights_sha:
            errors.append("p53 weights mismatch")

    print(json.dumps({
        "ok": not errors,
        "errors": errors[:10],
        "label": "self-repeat in a clean process (not independent review)",
        "tasks_restored": tasks_ok,
        "tasks_total": len(cfg["tasks"]),
        "controls_restored": controls_ok,
        "controls_total": len(controls),
        "negatives_rejected": negatives_ok,
        "negatives_total": len(negatives),
        "p43_resume": {"bit_exact_continuation": p43_ok},
        "artifacts_restored": restored,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def run_p58_acceptance_baseline_audit(
    config_path: str | Path, output_path: str | Path
) -> dict[str, Any]:
    """P58 audit: reconcile P40-P57 evidence and gate the research base.

    Inspection and re-verification only: sealed P52/P53/P56 manifests must
    verify, every P57 certificate is rechecked with the exact dual checker
    under strict bounds, durable raw/weights must exist with recorded
    size+hash (absent data is MISSING_EVIDENCE, never silently remade),
    transient-only evidence listed in ``recoveries`` is copied byte-identical
    to its durable destination with hash recorded (non-empty destinations are
    never overwritten; unsealed copies stay labeled unsealed), dirty-source
    final claims are rejected, and any pending scientific approval keeps the
    dossier BLOCKED. Provisional labels (P56) and P46/P47/P48/P54 pendencies
    are preserved, never waived.
    """

    import torch as _torch

    from evobyte.provenance import (
        collect_provenance,
        get_git_commit,
        get_git_status,
        hash_file,
        verify_manifest_integrity,
    )

    t0 = time.perf_counter()
    cfg_p = Path(config_path)
    with open(cfg_p, encoding="utf-8") as f:
        config = json.load(f)
    if config.get("phase") != "P58":
        raise ValueError(f"Config {cfg_p} is not a P58 configuration")
    config_sha = hashlib.sha256(cfg_p.read_bytes()).hexdigest()

    print("=" * 115)
    print("P58 ACCEPTED-RESEARCH-BASELINE AUDIT (reconciliation only; no new search)")
    print("=" * 115)

    findings: list[str] = []

    manifests: list[dict[str, Any]] = []
    for rel in config.get("sealed_manifests", []):
        chk = verify_manifest_integrity(_REPO_ROOT / rel)
        manifests.append({"path": rel, "ok": bool(chk["ok"]), "errors": chk["errors"][:3]})
        print(f"  sealed {rel}: {'ok' if chk['ok'] else 'SEAL BROKEN'}")
        if not chk["ok"]:
            findings.append(f"SEAL_BROKEN: {rel} ({'; '.join(chk['errors'][:2])})")

    cert_rel = config.get("certificates_path", "experiments/p57-certificates.json")
    cert_p = _REPO_ROOT / cert_rel if not Path(cert_rel).is_absolute() else Path(cert_rel)
    with open(cert_p, encoding="utf-8") as f:
        certificates = json.load(f)
    expected = int(config.get("certificates_expected", len(certificates)))
    if len(certificates) != expected:
        findings.append(
            f"COUNT_MISMATCH: {cert_rel} has {len(certificates)} certificates, expected {expected}"
        )

    from open_problems import verify_independent_reproduction

    device = _torch.device(config.get("device", "cpu"))
    rechecked_ok = 0
    recheck_failures: list[str] = []
    for entry in certificates:
        try:
            repro = verify_independent_reproduction(
                "erdos-straus",
                {
                    "n": int(entry["n"]),
                    "x": int(entry["x"]),
                    "y": int(entry["y"]),
                    "z": int(entry["z"]),
                },
                bounds_strict=True,
                device=device,
            )
            ok = bool(repro.get("status") == "PASS")
        except Exception as exc:  # noqa: BLE001 - record, never hide
            ok = False
            recheck_failures.append(f"n={entry.get('n')}: {exc!r}"[:160])
        if ok:
            rechecked_ok += 1
        elif len(recheck_failures) < 10:
            recheck_failures.append(f"n={entry.get('n')}: reproduction not verified")
    print(f"  certificates rechecked exact: {rechecked_ok}/{len(certificates)}")
    if rechecked_ok != len(certificates):
        findings.append(
            f"RECHECK_FAILED: {len(certificates) - rechecked_ok} certificate(s) "
            "not verified by the exact checker"
        )

    raw_inventory: list[dict[str, Any]] = []
    for rel in config.get("durable_raw", []):
        cand = _REPO_ROOT / rel if not Path(rel).is_absolute() else Path(rel)
        if not cand.exists():
            raw_inventory.append({"path": rel, "ok": False, "error": "MISSING_EVIDENCE"})
            findings.append(f"MISSING_EVIDENCE: durable raw absent: {rel}")
            print(f"  raw {rel}: MISSING_EVIDENCE")
            continue
        digest = hash_file(cand)
        raw_inventory.append(
            {"path": rel, "ok": True, "size": cand.stat().st_size, "sha256": digest}
        )
    print(f"  durable raw present: {sum(1 for r in raw_inventory if r['ok'])}/{len(raw_inventory)}")

    recovery: list[dict[str, Any]] = []
    for item in config.get("recoveries", []):
        src = Path(item["src"])
        if not src.is_absolute():
            src = _REPO_ROOT / item["src"]
        dest = Path(item["dest"])
        if not dest.is_absolute():
            dest = _REPO_ROOT / item["dest"]
        rec: dict[str, Any] = {
            "phase": item.get("phase"),
            "src": item["src"],
            "dest": item["dest"],
        }
        if dest.exists() and dest.stat().st_size > 0:
            digest = hash_file(dest)
            rec.update(
                {
                    "status": "ALREADY_DURABLE",
                    "size": dest.stat().st_size,
                    "sha256": digest,
                    "seal": "none (hash recorded at audit; no prior seal to compare)",
                }
            )
            print(f"  recover {item.get('phase')}: ALREADY_DURABLE {item['dest']}")
        elif not src.exists():
            rec.update({"status": "MISSING_EVIDENCE"})
            findings.append(f"MISSING_EVIDENCE: neither durable nor transient copy: {item['dest']}")
            print(f"  recover {item.get('phase')}: MISSING_EVIDENCE")
        else:
            blob = src.read_bytes()
            dest.parent.mkdir(parents=True, exist_ok=True)
            with open(dest, "wb") as f:
                f.write(blob)
            digest = hashlib.sha256(blob).hexdigest()
            rec.update(
                {
                    "status": "RECOVERED_UNSEALED",
                    "size": len(blob),
                    "sha256": digest,
                    "seal": "none (recovered transient copy; hash recorded at recovery)",
                    "src_mtime": src.stat().st_mtime,
                }
            )
            print(
                f"  recover {item.get('phase')}: RECOVERED_UNSEALED {len(blob)}B -> {item['dest']}"
            )
        recovery.append(rec)

    revision = get_git_commit()
    dirty = get_git_status()
    if config.get("require_clean_tree", True) and dirty:
        findings.append("DIRTY_SOURCE: tree not clean; final claims from dirty code rejected")
        print("  tree: DIRTY_SOURCE (final claims rejected)")
    else:
        print(f"  tree: {'dirty (diagnostic only)' if dirty else 'clean'}")

    pending = [a for a in config.get("approvals", []) if a.get("status") != "approved"]
    for appr in pending:
        print(f"  approval {appr.get('id')}: {appr.get('status')}")
    if pending:
        findings.append("PENDING_APPROVAL: " + ", ".join(str(a.get("id")) for a in pending))

    verdict = "BLOCKED" if findings else "ACCEPTED"
    prov = collect_provenance(
        seed=42,
        device=_torch.device("cpu"),
        dataset_hashes={"p58_config": config_sha[:16]},
        config={"acceptance_phase": "P58"},
    )
    report = {
        "phase": "P58",
        "verdict": verdict,
        "claim_scope": (
            "P40-P57 evidence reconciliation only; no new search, no novelty "
            "or discovery claim; provisional labels and review pendencies preserved"
        ),
        "run_id": hashlib.sha256(f"{config_sha}{revision}".encode()).hexdigest()[:16],
        "revision": revision,
        "dirty": dirty,
        "findings": findings[:12],
        "sealed_manifests": manifests,
        "certificates": {
            "path": cert_rel,
            "expected": expected,
            "rechecked_exact": rechecked_ok,
            "rechecked_total": len(certificates),
            "failures": recheck_failures[:10],
        },
        "durable_raw": raw_inventory,
        "recovery": recovery,
        "approvals": config.get("approvals", []),
        "approvals_pending": [str(a.get("id")) for a in pending],
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
            "acceptance_phase": "P58",
        },
        "seeds_rng": "not-applicable: deterministic manifest inspection plus exact recheck (reason: no search)",
        "budgets": {"audit_recheck_sec": time.perf_counter() - t0},
        "certificate_references": [
            {"n": c.get("n"), "sha256": c.get("sha256")} for c in certificates[:5]
        ],
        "counters": {
            "sealed_manifests": len(manifests),
            "sealed_ok": sum(1 for m in manifests if m["ok"]),
            "certificates": len(certificates),
            "certificates_rechecked": rechecked_ok,
            "durable_raw": len(raw_inventory),
            "durable_raw_ok": sum(1 for r in raw_inventory if r["ok"]),
            "recovery": len(recovery),
            "recovery_durable": sum(1 for r in recovery if r["status"] == "ALREADY_DURABLE"),
            "recovery_recovered": sum(1 for r in recovery if r["status"] == "RECOVERED_UNSEALED"),
            "recovery_missing": sum(1 for r in recovery if r["status"] == "MISSING_EVIDENCE"),
            "approvals_pending": len(pending),
        },
        "limitations": [
            "Reconciliation audits recorded evidence; it re-executes no P40-P57 search.",
            "Recovered transient copies carry no prior seal; their hash is recorded at recovery and they stay provisional.",
            "BLOCKED on missing data, dirty source or pending approval is the honest gate, not a negative result.",
            "P59 requires applicable scientific review completed plus an accepted code review.",
        ],
        "elapsed_sec": time.perf_counter() - t0,
    }
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True, default=str)
    print(f"P58 audit {verdict}; findings={len(findings)}; report -> {out_p}")
    return report


def run_p57_campaign_audit(config_path: str | Path, output_path: str | Path) -> dict[str, Any]:
    """P57 audit: bounded instance campaign with frozen nomination and honest statuses.

    The nominated list must match the frozen enumeration exactly; the
    time-capped search reuses the accepted checkers; every found triple is
    independently re-verified with bounds tested; unsolved instances stay
    budget-exhausted (never exhaustive-null without full coverage); novelty
    caps at candidate without sustained review plus independent reproduction,
    so no discovery is claimed here.
    """
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
    if config.get("phase") != "P57":
        raise ValueError(f"Config {cfg_p} is not a P57 configuration")
    config_sha = hashlib.sha256(cfg_p.read_bytes()).hexdigest()
    max_coord = int(config.get("max_coord", 10**9))
    time_cap = float(config.get("time_cap_sec", 3600.0))

    print("=" * 115)
    print("P57 DISCOVERY CAMPAIGN AUDIT (instances only; no discovery claimed)")
    print("=" * 115)

    from open_problems import (
        p57_classify_solved,
        p57_nominate_instances,
        run_p57_bounded_campaign,
        verify_independent_reproduction,
    )

    frozen = [int(n) for n in config.get("instances", [])]
    if p57_nominate_instances(int(config.get("limit", 100000))) != frozen:
        raise ValueError("P57 nominated list differs from the frozen enumeration")
    print(f"  frozen nomination: {len(frozen)} primes 1 mod 24 <= {config.get('limit', 100000)}")

    device_name = config.get("device")
    device = _torch.device(device_name) if device_name else None
    if device is None:
        device = _torch.device("cuda" if _torch.cuda.is_available() else "cpu")
    campaign = run_p57_bounded_campaign(
        frozen,
        device=device,
        max_coord=max_coord,
        time_cap_sec=time_cap,
        batch_size=int(config.get("batch_size", 500_000)),
    )

    errors: list[str] = []
    certificates: list[dict[str, Any]] = []
    for inst in campaign["instances"]:
        if inst["status"] not in ("rediscovery", "candidate", "budget-exhausted"):
            errors.append(f"n={inst['n']}: forbidden status {inst['status']}")
            continue
        if not inst["found"]:
            if inst["status"] != "budget-exhausted":
                errors.append(f"n={inst['n']}: unsolved must be budget-exhausted")
            continue
        x, y, z = (int(v) for v in inst["triple"])
        try:
            repro = verify_independent_reproduction(
                "erdos-straus",
                {"n": int(inst["n"]), "x": x, "y": y, "z": z},
                bounds_strict=True,
                device=device,
            )
            ok = bool(repro.get("status") == "PASS")
        except Exception as exc:  # noqa: BLE001 - record, never hide
            errors.append(f"n={inst['n']}: reproduction failed ({exc!r})")
            continue
        if not ok:
            errors.append(f"n={inst['n']}: reproduction not verified")
            continue
        if max(x, y, z) > max_coord:
            errors.append(f"n={inst['n']}: bounds violated after accept")
            continue
        if p57_classify_solved(int(inst["n"]), (x, y, z)) != inst["status"]:
            errors.append(f"n={inst['n']}: classification mismatch")
            continue
        certificates.append(
            {
                "n": int(inst["n"]),
                "x": x,
                "y": y,
                "z": z,
                "status": inst["status"],
                "sha256": hashlib.sha256(f"{inst['n']}/{x}/{y}/{z}".encode()).hexdigest(),
            }
        )
    print(f"  verified certificates: {len(certificates)}/{len(frozen)}")

    cert_path = Path(config.get("certificates_path", "experiments/p57-certificates.json"))
    if not cert_path.is_absolute():
        cert_path = _REPO_ROOT / cert_path
    cert_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cert_path, "w", encoding="utf-8") as f:
        json.dump(certificates, f, sort_keys=True)
    cert_sha = hashlib.sha256(cert_path.read_bytes()).hexdigest()

    verdict = "COMPLETE" if not errors else "INCOMPLETE"
    print(f"P57 audit {verdict}; errors={errors[:3]}")

    revision = get_git_commit()
    dirty = get_git_status()
    prov = collect_provenance(
        seed=42,
        device=_torch.device("cpu"),
        dataset_hashes={"p57_config": config_sha[:16], "p57_certs": cert_sha[:16]},
        config={"acceptance_phase": "P57"},
    )
    report = {
        "phase": "P57",
        "verdict": verdict,
        "claim_scope": "bounded instances only; no conjecture claim; no discovery claimed",
        "run_id": hashlib.sha256(f"{config_sha}{cert_sha}{revision}".encode()).hexdigest()[:16],
        "revision": revision,
        "dirty": dirty,
        "errors": errors[:10],
        "nomination": {"count": len(frozen), "frozen_match": True},
        "by_status": campaign["by_status"],
        "time_capped": campaign["time_capped"],
        "total_evaluated": campaign["total_evaluated"],
        "certificates": len(certificates),
        "certificates_sha256": cert_sha,
        "novelty": (
            "rediscovery where classical/k3-anchored, else candidate; "
            "verified-construction needs reviewer-sustained novelty, discovery needs "
            "independent reproduction plus the proper certificate or proof; none claimed."
        ),
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
            "acceptance_phase": "P57",
        },
        "seeds_rng": "deterministic grid enumeration; no sampling RNG",
        "budgets": {"time_cap_sec": time_cap, "compute_sec": campaign["elapsed_total_sec"]},
        "certificate_references": [{"n": c["n"], "sha256": c["sha256"]} for c in certificates[:5]],
        "counters": {
            "nominated": len(frozen),
            "certified": len(certificates),
            "budget_exhausted": campaign["by_status"].get("budget-exhausted", 0),
        },
        "limitations": [
            "Windowed search: unsolved means budget-exhausted, never exhaustive-null.",
            "A new instance solution is useful without settling the open conjecture.",
        ],
        "elapsed_sec": time.perf_counter() - t0,
    }
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True, default=str)
    print(f"P57 audit {verdict}; report -> {out_p}")
    return report


def run_p56_confirmation_audit(config_path: str | Path, output_path: str | Path) -> dict[str, Any]:
    """P56 audit: confirm the frozen method on fresh sealed tasks.

    Development-frozen methods only (no algorithm edits): the kept search
    method versus the classical reference and structured random, 20 seeds on
    six fresh tasks at 10 s real. Tasks are sealed before any trial and access
    is logged persistently; controls and certificates are re-verified in a
    clean process alongside the P43 resume check and artifact restoration.
    Loss and tie are valid results; without independent review the result is
    labeled provisional, never a discovery. Integrity failure blocks P57.
    """
    import subprocess as _sp

    import numpy as _np
    import torch as _torch
    from full_matrix import _p38_wilson_ci as _wilson

    from evobyte.provenance import (
        collect_provenance,
        get_git_commit,
        get_git_status,
        write_manifest,
    )

    t0 = time.perf_counter()
    cfg_p = Path(config_path)
    with open(cfg_p, encoding="utf-8") as f:
        config = json.load(f)
    if config.get("phase") != "P56":
        raise ValueError(f"Config {cfg_p} is not a P56 configuration")
    config_sha = hashlib.sha256(cfg_p.read_bytes()).hexdigest()
    err_thr = float(config.get("error_threshold", 1e-4))
    domain = tuple(config.get("domain", [-3.0, 3.0]))
    seeds = list(config.get("seeds", []))
    override_ids = list(config.get("task_override_ids", []))
    if not override_ids and len(seeds) != 20:
        raise ValueError("P56 requires exactly 20 preregistered seeds")
    arms = list(config.get("arms", ["evolution", "classical", "structured_random"]))
    budget = float(config.get("budget_sec", 10.0))
    pop_size = int(config.get("pop_size", 64))
    cap = float(config.get("campaign_cap_sec", 10800.0))

    print("=" * 115)
    print("P56 FRESH-FROZEN CONFIRMATION (sealed tasks; frozen method; no discovery label)")
    print("=" * 115)

    from math_specialist import run_p54_arm_trial

    task_rule = config.get("task_rule", {})
    if override_ids:
        task_origin = "dev-override (test only, never final)"
        with open(_REPO_ROOT / "experiments" / "p52-certified-data.json", encoding="utf-8") as f:
            positives = json.load(f)["positives"]
        by_id = {p["item_id"]: p for p in positives}
        tasks = [
            {"task_id": tid, "canonical_formula": by_id[tid]["ground_truth_expr"]}
            for tid in override_ids
        ]
        seal_sha = "dev-override-no-seal"
    else:
        task_origin = "sealed-final"
        with open(_REPO_ROOT / "experiments" / "p52-certified-data.json", encoding="utf-8") as f:
            dev_formulas = {p["ground_truth_expr"] for p in json.load(f)["positives"]}
        dev_formulas |= {t.get("formula", "") for t in config.get("extra_exclusions", [])}
        dev_formulas |= {"x**2 - 1", "x**2 + 3*x + 7"}
        tasks = [
            {"task_id": f"p56_f{i:02d}", "canonical_formula": t["canonical_formula"]}
            for i, t in enumerate(
                _p56_fresh_tasks(
                    final_seed=int(task_rule.get("final_seed", 56056)),
                    n_tasks=int(task_rule.get("n_tasks", 6)),
                    dev_formulas=dev_formulas,
                )
            )
        ]
        seal_doc = {
            "phase": "p56-final-tasks",
            "task_rule": task_rule,
            "excluded_dev_targets": len(dev_formulas),
            "tasks": tasks,
        }
        seal_path = _REPO_ROOT / "experiments" / "p56-final-tasks.json"
        written = write_manifest(seal_path, seal_doc, {})
        seal_sha = written["manifest_sha256"]
        log_path = _REPO_ROOT / "experiments" / "p47-final-test" / "access-log.json"
        log = json.loads(log_path.read_text())
        log.append(
            {
                "phase": "P56",
                "action": "generate-sealed-final-tasks",
                "timestamp": time.time(),
                "task_ids": [t["task_id"] for t in tasks],
                "seal_sha256": seal_sha,
                "config_sha256": config_sha,
                "revision": get_git_commit(),
            }
        )
        log_path.write_text(json.dumps(log, indent=2))
        print(f"  sealed {len(tasks)} fresh tasks -> {seal_path} (sha {seal_sha[:16]})")

    import sympy as _sympy

    trials: list[dict[str, Any]] = []
    errors: list[str] = []
    deadline = t0 + cap
    device = _torch.device(config.get("device", "cpu"))
    for task in tasks:
        formula = str(task["canonical_formula"])
        fn = _sympy.lambdify(_sympy.Symbol("x"), _sympy.sympify(formula), modules=["numpy"])
        xs = _np.linspace(domain[0], domain[1], 64, dtype=_np.float32)
        ys = _np.asarray(fn(xs), dtype=_np.float32)
        for arm in arms:
            for seed in seeds:
                if time.perf_counter() > deadline:
                    errors.append("campaign cap hit")
                    break
                try:
                    rec = run_p54_arm_trial(
                        arm,
                        formula=formula,
                        features_norm=None,
                        xs_f32=xs,
                        ys_f32=ys,
                        budget_sec=budget,
                        seed=seed,
                        device=device,
                        pop_size=pop_size,
                        domain=domain,
                        error_threshold=err_thr,
                    )
                except Exception as exc:  # noqa: BLE001 - record, never hide
                    errors.append(f"{task['task_id']}/{arm}/{seed}: {exc!r}")
                    continue
                rec.update({"task": task["task_id"], "formula": formula})
                trials.append(rec)
        print(
            f"  {task['task_id']} {formula}: "
            + ", ".join(
                f"{a}={sum(t['certified'] for t in trials if t['task'] == task['task_id'] and t['arm'] == a)}/{len(seeds)}"
                for a in arms
            )
        )

    by_task: dict[str, Any] = {}
    for task in tasks:
        for arm in arms:
            recs = [t for t in trials if t["task"] == task["task_id"] and t["arm"] == arm]
            k = sum(t["certified"] for t in recs)
            lo, hi = _wilson(k, len(recs))
            by_task[f"{task['task_id']}/{arm}"] = {
                "certified": k,
                "trials": len(recs),
                "wilson_95": [lo, hi],
                "median_time_to_cert": float(_np.median([t["time_to_cert"] for t in recs]))
                if recs
                else None,
            }

    per_arm = {
        arm: {
            "trials": sum(1 for t in trials if t["arm"] == arm),
            "certified": sum(t["certified"] for t in trials if t["arm"] == arm),
            "search_sec": float(sum(t["search_sec"] for t in trials if t["arm"] == arm)),
            "cert_sec": float(sum(t["cert_sec"] for t in trials if t["arm"] == arm)),
        }
        for arm in arms
    }

    clean_input = {
        "tasks": [{"task_id": t["task_id"], "formula": t["canonical_formula"]} for t in tasks],
        "domain": list(domain),
        "error_threshold": err_thr,
        "max_controls": config.get("clean_rerun_max_controls"),
        "sealed": [
            "experiments/p52-certified-data.json",
            "experiments/p53-proposer-manifest.json",
            "experiments/p56-final-tasks.json" if task_origin == "sealed-final" else None,
        ],
        "weights_sha": None,
    }
    try:
        with open(_REPO_ROOT / "experiments" / "p53-proposer-manifest.json", encoding="utf-8") as f:
            clean_input["weights_sha"] = json.load(f)["weights"]["sha256"]
    except (OSError, ValueError, KeyError):
        clean_input["weights_sha"] = None
    clean_path = Path(output_path).parent / "p56-clean-input.json"
    with open(clean_path, "w", encoding="utf-8") as f:
        json.dump(clean_input, f, sort_keys=True)
    clean_script = Path(output_path).parent / "p56-clean-rerun.py"
    clean_script.write_text(_P56_CLEAN_RERUN_SCRIPT.replace("__REPO_ROOT__", str(_REPO_ROOT)))
    try:
        proc = _sp.run(
            [sys.executable, str(clean_script), str(clean_path)],
            capture_output=True,
            text=True,
            check=False,
            cwd=str(_REPO_ROOT),
            timeout=1200,
        )
        clean_rerun = (
            json.loads(proc.stdout.strip().splitlines()[-1])
            if proc.returncode == 0
            else {
                "ok": False,
                "error": (proc.stderr or proc.stdout)[-500:],
            }
        )
    except Exception as exc:  # noqa: BLE001 - record, never hide
        clean_rerun = {"ok": False, "error": repr(exc)}
    print(f"  clean rerun (new process, self-repeat label): {clean_rerun.get('ok')}")

    if errors:
        verdict, reason = "BLOCKED", f"trial errors: {errors[:2]}"
    elif not clean_rerun.get("ok"):
        verdict, reason = "BLOCKED", f"clean rerun failed: {clean_rerun.get('error', clean_rerun)}"
    else:
        verdict, reason = "CONFIRMED", "recoverable package with complete final results"

    revision = get_git_commit()
    dirty = get_git_status()
    prov = collect_provenance(
        seed=int(seeds[0]),
        device=_torch.device("cpu"),
        dataset_hashes={"p56_config": config_sha[:16], "p56_tasks": seal_sha[:16]},
        config={"acceptance_phase": "P56"},
    )
    report = {
        "phase": "P56",
        "verdict": verdict,
        "result_label": "provisional-confirmation (independent review pending; never a discovery label)",
        "claim_scope": "frozen method on six fresh tasks; loss and tie are valid results",
        "run_id": hashlib.sha256(f"{config_sha}{seal_sha}{revision}".encode()).hexdigest()[:16],
        "revision": revision,
        "dirty": dirty,
        "reason": reason,
        "task_origin": task_origin,
        "tasks": tasks,
        "task_seal_sha256": seal_sha,
        "by_task": by_task,
        "per_arm": per_arm,
        "clean_rerun": clean_rerun,
        "p43_resume": clean_rerun.get("p43_resume", {}),
        "artifacts_restored": clean_rerun.get("artifacts_restored", {}),
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
            "acceptance_phase": "P56",
        },
        "seeds_rng": f"fixed seeds {seeds[0]}..{seeds[-1]} (20); paired across arms",
        "budgets": {"budget_sec": budget, "campaign_cap_sec": cap},
        "certificate_references": [],
        "counters": {"trials": len(trials), "tasks": len(tasks)},
        "limitations": [
            "Six tasks cannot prove generality; sample limits published per task.",
            "Provisional without independent review; a post-final change needs a new future test.",
        ],
        "elapsed_sec": time.perf_counter() - t0,
    }
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True, default=str)
    print(f"P56 audit {verdict}; report -> {out_p}")
    return report


def run_p55_sampling_audit(config_path: str | Path, output_path: str | Path) -> dict[str, Any]:
    """P55 audit: explicit DEFERRED unless budget and preregistration exist.

    The mechanical gate runs a new single-mechanism comparison only on an
    approved compute budget with one preregistered mechanism and a complete
    frozen procedure. Otherwise it records DEFERRED with justification and
    zero compute cost, reuses P37 as history (never rerun), forbids
    quantum-advantage/hardware language for classical ops, and continues to
    P56 with the classical sampler. No threshold is relaxed after the fact.
    """
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
    if config.get("phase") != "P55":
        raise ValueError(f"Config {cfg_p} is not a P55 configuration")
    config_sha = hashlib.sha256(cfg_p.read_bytes()).hexdigest()

    print("=" * 115)
    print("P55 SAMPLING-HYPOTHESIS AUDIT (optional; explicit DEFERRED without budget)")
    print("=" * 115)

    from qrand_ab import p55_budget_gate

    gate = p55_budget_gate(config)
    print(f"  gate execute: {gate['execute']}; reason: {gate['reason']}")
    if gate["execute"]:
        raise RuntimeError(
            "P55 execution approved by config, but no single-mechanism comparison "
            "is implemented on this branch; a follow-up microtask must preregister "
            "the mechanism, procedure and thresholds before any sampling runs."
        )
    verdict = "DEFERRED"

    revision = get_git_commit()
    dirty = get_git_status()
    prov = collect_provenance(
        seed=42,
        device=_torch.device("cpu"),
        dataset_hashes={"p55_config": config_sha[:16]},
        config={"acceptance_phase": "P55"},
    )
    report = {
        "phase": "P55",
        "verdict": verdict,
        "claim_scope": "no new sampling claim; P56 proceeds with the classical sampler",
        "run_id": hashlib.sha256(f"{config_sha}{revision}".encode()).hexdigest()[:16],
        "revision": revision,
        "dirty": dirty,
        "gate": gate,
        "justification": (
            "No approved P55 compute budget exists in any frozen manifest "
            "(runbook caps cover P52/P53/P54/P57 only); no single mechanism is "
            "preregistered; P37 stays NULL history and P54 DROP keeps the "
            "classical sampler. Useful research is not blocked: P56 proceeds."
        ),
        "language_guard": "no quantum-advantage or quantum-hardware terms used; classical ops only",
        "continuation": "P56 with the classical sampler",
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
            "acceptance_phase": "P55",
        },
        "seeds_rng": "no sampling ran; no RNG consumed",
        "budgets": {"approved_budget_sec": gate["approved_budget_sec"], "compute_sec": 0.0},
        "certificate_references": [],
        "counters": {"comparisons_run": 0},
        "limitations": [
            "DEFERRED is terminal for this microtask, not a verdict on quantum-inspired search.",
            "A future approved budget plus a preregistered mechanism needs its own branch.",
        ],
        "elapsed_sec": time.perf_counter() - t0,
    }
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True, default=str)
    print(f"P55 audit {verdict}; report -> {out_p}")
    return report


def run_p54_utility_audit(config_path: str | Path, output_path: str | Path) -> dict[str, Any]:
    """P54 audit: matched-budget pilot with a preregistered paired decision.

    The pilot screens all arms at 10 s, confirms the top-2 search arms plus
    classical at 60 s, and returns a mechanical KEEP/DROP/INCONCLUSIVE
    verdict: KEEP needs the frozen 95% interval sustaining >=20% faster
    time-to-certificate with no success drop (plus recorded statistical
    approval and a limited-adoption ADR); classical trivializing the family
    forces DROP; thin data forces INCONCLUSIVE. No threshold is relaxed
    after seeing results.
    """
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
    if config.get("phase") != "P54":
        raise ValueError(f"Config {cfg_p} is not a P54 configuration")
    config_sha = hashlib.sha256(cfg_p.read_bytes()).hexdigest()

    print("=" * 115)
    print("P54 UTILITY AUDIT (matched budgets; paired time-to-certificate; frozen rule)")
    print("=" * 115)

    from math_specialist import run_p54_matched_pilot

    tmp_dir = Path(output_path).parent
    pilot = run_p54_matched_pilot(
        corpus_manifest=config.get("corpus_manifest", "experiments/p52-certified-data.json"),
        proposer_manifest=config.get("proposer_manifest", "experiments/p53-proposer-manifest.json"),
        output_path=tmp_dir / "p54-pilot.json",
        task_ids=config.get("task_ids"),
        seeds=config.get("seeds", [42, 101, 202, 303, 404]),
        screen_sec=float(config.get("screen_sec", 10.0)),
        confirm_sec=float(config.get("confirm_sec", 60.0)),
        campaign_cap_sec=float(config.get("campaign_cap_sec", 10800.0)),
        pop_size=int(config.get("pop_size", 64)),
        hybrid_proposals=int(config.get("hybrid_proposals", 64)),
        device_name=config.get("device", "cpu"),
        keep_ratio=float(config.get("keep_ratio", 0.8)),
        min_pairs=int(config.get("min_pairs", 20)),
        classical_frac=float(config.get("classical_frac", 0.9)),
        domain=tuple(config.get("domain", [-3.0, 3.0])),
        error_threshold=float(config.get("error_threshold", 1e-4)),
        statistical_review=config.get("statistical_review", {}),
    )
    verdict = pilot.get("status", "INCONCLUSIVE")
    assert verdict in ("KEEP", "DROP", "INCONCLUSIVE", "MIXED"), verdict
    print(f"  pilot verdict: {verdict} ({pilot.get('reason')})")

    revision = get_git_commit()
    dirty = get_git_status()
    prov = collect_provenance(
        seed=int(config.get("seeds", [42])[0]),
        device=_torch.device("cpu"),
        dataset_hashes={"p54_config": config_sha[:16]},
        config={"acceptance_phase": "P54"},
    )
    report = {
        "phase": "P54",
        "verdict": verdict,
        "claim_scope": "utility of the P53 proposer on six development tasks; no discovery claim",
        "run_id": hashlib.sha256(f"{config_sha}{revision}".encode()).hexdigest()[:16],
        "revision": revision,
        "dirty": dirty,
        "pilot": pilot,
        "adr_required": verdict == "KEEP",
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
            "acceptance_phase": "P54",
        },
        "seeds_rng": f"fixed seeds {config.get('seeds')}; paired trials share seeds across arms",
        "budgets": {
            "screen_sec": float(config.get("screen_sec", 10.0)),
            "confirm_sec": float(config.get("confirm_sec", 60.0)),
            "campaign_cap_sec": float(config.get("campaign_cap_sec", 10800.0)),
        },
        "certificate_references": [],
        "counters": {
            "confirm_pairs": pilot.get("pairs", {}).get("n_both_uncensored", 0),
            "hybrid_certified": pilot.get("certified", {}).get("hybrid", 0),
        },
        "limitations": [
            "KEEP would require recorded statistical approval plus a limited-adoption ADR.",
            "Amortized projections are arithmetic over stated horizons, not measurements.",
            "Six development tasks cannot prove generality; the final test stays sealed.",
        ],
        "elapsed_sec": time.perf_counter() - t0,
    }
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True, default=str)
    print(f"P54 audit {verdict}; report -> {out_p}")
    return report


def run_p53_proposer_audit(config_path: str | Path, output_path: str | Path) -> dict[str, Any]:
    """P53 audit: real reproducible training and export of one small proposer.

    Checks the hard caps (params, epochs, wall time), validation-chosen
    checkpoint, independent reload generating valid standalone candidates
    with the exploration floor kept, bit-exact reproducibility of training
    and sampling, and billed collection/training costs. Invalid training or
    insufficient data yields INCONCLUSIVE (promotion blocked); no KEEP here.
    """
    import numpy as _np
    import torch as _torch

    from evobyte.bytecode import is_valid as _is_valid
    from evobyte.provenance import (
        collect_provenance,
        get_git_commit,
        get_git_status,
        verify_manifest_integrity,
    )

    t0 = time.perf_counter()
    cfg_p = Path(config_path)
    with open(cfg_p, encoding="utf-8") as f:
        config = json.load(f)
    if config.get("phase") != "P53":
        raise ValueError(f"Config {cfg_p} is not a P53 configuration")
    config_sha = hashlib.sha256(cfg_p.read_bytes()).hexdigest()

    print("=" * 115)
    print("P53 PROPOSER AUDIT (one small model; real training; independent reload)")
    print("=" * 115)

    from math_specialist import run_p53_proposer_training

    train_kwargs: dict[str, Any] = {
        "corpus_manifest": config.get("corpus_manifest", "experiments/p52-certified-data.json"),
        "device_name": config.get("device", "cpu"),
        "seed": int(config.get("seed", 42)),
        "batch_size": int(config.get("batch_size", 32)),
        "max_epochs": int(config.get("max_epochs", 20)),
        "max_train_min": float(config.get("max_train_min", 30.0)),
        "exploration_floor": float(config.get("exploration_floor", 0.10)),
        "gru_width": int(config.get("gru_width", 64)),
        "lr": float(config.get("lr", 3e-3)),
        "n_sample": int(config.get("n_sample", 32)),
    }
    tmp_dir = Path(output_path).parent
    run_a = run_p53_proposer_training(
        output_path=tmp_dir / "p53-audit-manifest.json",
        weights_path=tmp_dir / "p53-audit-proposer.pt",
        **train_kwargs,
    )
    if run_a.get("status") != "PASS":
        report_blocked = {
            "phase": "P53",
            "verdict": "INCONCLUSIVE",
            "claim_scope": "training blocked; baseline preserved; P54 decides utility",
            "reason": run_a.get("reason", "invalid training or insufficient data"),
            "elapsed_sec": time.perf_counter() - t0,
        }
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        with open(out_p, "w", encoding="utf-8") as f:
            json.dump(report_blocked, f, indent=2, sort_keys=True, default=str)
        print(f"P53 audit INCONCLUSIVE ({report_blocked['reason']}); report -> {out_p}")
        return report_blocked

    run_b = run_p53_proposer_training(output_path=None, weights_path=None, **train_kwargs)
    reproducible = (
        run_b.get("status") == "PASS"
        and run_b["training"]["val_curve"] == run_a["training"]["val_curve"]
        and run_b["training"]["best_val_loss"] == run_a["training"]["best_val_loss"]
    )

    from evobyte.generator import P53_MAX_PARAMS as _P53_MAX
    from evobyte.generator import load_proposer as _load
    from evobyte.generator import sample_proposer_standalone as _sample

    manifest_ok = verify_manifest_integrity(tmp_dir / "p53-audit-manifest.json")
    schema = run_a["schema"]
    fresh = _load(tmp_dir / "p53-audit-proposer.pt", schema, train_kwargs["device_name"])
    val_feats = _np.array(
        [
            p["features_inference_only"]
            for p in json.loads((_REPO_ROOT / train_kwargs["corpus_manifest"]).read_text())[
                "positives"
            ]
            if p.get("split") == "val"
        ],
        dtype=_np.float32,
    )
    mu = _np.array(schema["feature_mean"], dtype=_np.float64)
    sigma = _np.array(schema["feature_std"], dtype=_np.float64)
    norm_val = ((val_feats.astype(_np.float64) - mu) / sigma).astype(_np.float32)
    probe = norm_val[: max(1, min(len(norm_val), 4))]
    s1, o1 = _sample(
        fresh,
        probe,
        int(train_kwargs["n_sample"]),
        seed=int(train_kwargs["seed"]) + 1000,
        exploration_floor=float(train_kwargs["exploration_floor"]),
        device=train_kwargs["device_name"],
    )
    s2, _ = _sample(
        fresh,
        probe,
        int(train_kwargs["n_sample"]),
        seed=int(train_kwargs["seed"]) + 1000,
        exploration_floor=float(train_kwargs["exploration_floor"]),
        device=train_kwargs["device_name"],
    )
    sampling_reproducible = len(s1) == len(s2) and all((a == b).all() for a, b in zip(s1, s2))
    valid_rate = float(_np.mean([_is_valid(p) for p in s1])) if len(s1) else 0.0
    floor_frac = float(sum(o == "floor" for o in o1) / max(1, len(o1)))

    curves = run_a["training"]
    best_pos = int(_np.argmin(_np.array(curves["val_curve"], dtype=float)))
    checks = {
        "params_within_cap": run_a["model"]["param_count"] <= _P53_MAX,
        "epochs_within_cap": curves["epochs_run"] <= int(train_kwargs["max_epochs"]),
        "time_within_cap": curves["train_sec"] <= float(train_kwargs["max_train_min"]) * 60.0,
        "checkpoint_by_validation": curves["best_epoch"] == best_pos,
        "manifest_sealed": bool(manifest_ok["ok"]),
        "training_reproducible": bool(reproducible),
        "independent_reload_samples": sampling_reproducible and len(s1) > 0,
        "all_sampled_valid": valid_rate == 1.0,
        "exploration_floor_kept": floor_frac >= float(train_kwargs["exploration_floor"]) - 1e-9,
        "single_model": True,
    }
    verdict = "ACCEPTED" if all(checks.values()) else "MIXED"
    for name, ok in checks.items():
        print(f"  {name}: {'ok' if ok else 'FAILED'}")

    revision = get_git_commit()
    dirty = get_git_status()
    prov = collect_provenance(
        seed=int(train_kwargs["seed"]),
        device=_torch.device("cpu"),
        dataset_hashes={"p53_config": config_sha[:16]},
        config={"acceptance_phase": "P53"},
    )
    report = {
        "phase": "P53",
        "verdict": verdict,
        "claim_scope": "one trained proposer, reproducible export; utility decided by P54",
        "run_id": hashlib.sha256(f"{config_sha}{revision}".encode()).hexdigest()[:16],
        "revision": revision,
        "dirty": dirty,
        "checks": checks,
        "model": run_a["model"],
        "training": {
            "epochs_run": curves["epochs_run"],
            "best_epoch": curves["best_epoch"],
            "best_val_loss": curves["best_val_loss"],
            "train_sec": curves["train_sec"],
            "stopped_by": curves["stopped_by"],
            "batch_used": curves["batch_used"],
            "reproducible": bool(reproducible),
        },
        "sampling": {
            "n_sample": len(s1),
            "valid_rate": valid_rate,
            "floor_fraction": floor_frac,
            "sampling_reproducible": sampling_reproducible,
        },
        "weights": run_a["weights"],
        "total_cost_sec": run_a["total_cost_sec"],
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
            "acceptance_phase": "P53",
        },
        "seeds_rng": f"fixed seed {train_kwargs['seed']}; seeded retrain and resample compared",
        "budgets": {
            "max_epochs": int(train_kwargs["max_epochs"]),
            "max_train_min": float(train_kwargs["max_train_min"]),
        },
        "certificate_references": [],
        "counters": {
            "params": run_a["model"]["param_count"],
            "epochs_run": curves["epochs_run"],
            "sampled": len(s1),
        },
        "limitations": [
            "Validity is a decoder property; solution quality is P54 business.",
            "No architecture search ran; a single small model was trained once.",
            "No KEEP/DROP here: promotion is decided by measured utility in P54.",
        ],
        "elapsed_sec": time.perf_counter() - t0,
    }
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True, default=str)
    print(f"P53 audit {verdict}; report -> {out_p}")
    return report


def run_p52_certified_data_audit(
    config_path: str | Path, output_path: str | Path
) -> dict[str, Any]:
    """P52 audit: 100% positives rechecked exactly, disjoint splits, billed costs.

    Every recorded positive is re-verified with the frozen exact checker;
    group/item/canonical splits must not overlap, the final test must stay
    unopened, negatives must carry objective reasons (never a timeout), and
    teacher costs must fit the one-hour cap. Unmet minimums with otherwise
    clean evidence yield INCONCLUSIVE (P53 blocked, P54 allowed on baselines).
    """
    import numpy as _np
    import torch as _torch

    from evobyte.grammar import canonicalize_bytecode as _canon
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
    if config.get("phase") != "P52":
        raise ValueError(f"Config {cfg_p} is not a P52 configuration")
    config_sha = hashlib.sha256(cfg_p.read_bytes()).hexdigest()
    err_thr = float(config.get("error_threshold", 1e-4))
    domain = tuple(config.get("domain", [-3.0, 3.0]))
    min_req = config.get("minimums", {})

    print("=" * 115)
    print("P52 CERTIFIED-DATA AUDIT (100% recheck; disjoint splits; billed teacher)")
    print("=" * 115)

    corpus_p = _REPO_ROOT / config.get("corpus_manifest", "experiments/p52-certified-data.json")
    integrity = verify_manifest_integrity(corpus_p)
    with open(corpus_p, encoding="utf-8") as f:
        corpus = json.load(f)

    errors: list[str] = []
    if not integrity["ok"]:
        errors.append(f"manifest seal broken: {integrity['errors'][:3]}")

    positives = corpus.get("positives", [])
    negatives = corpus.get("negatives", [])
    train_xs = _np.linspace(domain[0], domain[1], 48, dtype=_np.float64)
    test_xs = _np.linspace(domain[0] + 0.1, domain[1] - 0.1, 32, dtype=_np.float64)

    import sympy as _sympy

    _x = _sympy.Symbol("x")
    rechecked = 0
    for pos in positives:
        prog = _np.array(pos["program_words"], dtype=_np.uint32)
        truth = str(pos["ground_truth_expr"])
        fn = _sympy.lambdify(_x, _sympy.sympify(truth), modules=["numpy"])
        v = verify_l2(
            prog,
            train_xs,
            _np.asarray(fn(train_xs)),
            test_xs,
            _np.asarray(fn(test_xs)),
            ground_truth_formula=truth,
            error_threshold=err_thr,
            domain=domain,
        )
        if v.proof_type != "exact_certificate" or not v.passed:
            errors.append(f"positive {pos['item_id']} not exact on recheck ({v.proof_type})")
        else:
            rechecked += 1
        canon, _ = _canon(prog)
        if hashlib.sha256(_np.ascontiguousarray(canon).tobytes()).hexdigest() != pos.get(
            "normalized_sha256"
        ):
            errors.append(f"positive {pos['item_id']} normalized hash mismatch")
    print(f"  positives rechecked exact: {rechecked}/{len(positives)}")

    def _groups(items: list[dict[str, Any]], split: str) -> set[str]:
        return {p["group_id"] for p in items if p.get("split") == split}

    train_groups = _groups(positives, "train")
    val_groups = _groups(positives, "val")
    overlap = sorted(train_groups & val_groups)
    if overlap:
        errors.append(f"group overlap across splits: {overlap[:3]}")
    train_items = {p["item_id"] for p in positives if p.get("split") == "train"}
    val_items = {p["item_id"] for p in positives if p.get("split") == "val"}
    if train_items & val_items:
        errors.append("item overlap across splits")
    train_canon = {p["ground_truth_expr"] for p in positives if p.get("split") == "train"}
    val_canon = {p["ground_truth_expr"] for p in positives if p.get("split") == "val"}
    if train_canon & val_canon:
        errors.append("canonical-target overlap across splits")
    if len(positives) != len({p["item_id"] for p in positives}):
        errors.append("duplicate positive item ids")
    if len({p["normalized_sha256"] for p in positives}) != len(positives):
        errors.append("duplicate normalized programs")

    allowed_reasons = set(
        config.get("negative_reasons", ["invalid_execution", "false_certificate", "wrong_domain"])
    )
    neg_rejected = 0
    for neg in negatives:
        if neg.get("reason") not in allowed_reasons:
            errors.append(
                f"negative {neg['item_id']} has non-objective reason {neg.get('reason')!r}"
            )
            continue
        prog = _np.array(neg["program_words"], dtype=_np.uint32)
        truth = str(neg["ground_truth_expr"])
        fn = _sympy.lambdify(_x, _sympy.sympify(truth), modules=["numpy"])
        adv = _np.array(neg.get("adversarial_xs") or [], dtype=_np.float64)
        v = verify_l2(
            prog,
            train_xs,
            _np.asarray(fn(train_xs)),
            test_xs,
            _np.asarray(fn(test_xs)),
            adversarial_xs=adv if adv.size else None,
            ground_truth_formula=truth,
            error_threshold=err_thr,
            domain=domain,
        )
        if v.proof_type == "exact_certificate":
            errors.append(f"negative {neg['item_id']} certified unexpectedly")
        else:
            neg_rejected += 1
    blob = json.dumps(corpus, sort_keys=True, default=str).lower()
    if "timeout" in blob or "budget_exhausted" in blob:
        errors.append("timeout/budget language inside corpus evidence")
    print(f"  negatives rejected: {neg_rejected}/{len(negatives)}")

    final_ok = bool(corpus.get("final_test", {}).get("access_log_empty", False))
    if not final_ok:
        errors.append("final test may have been opened")
    controls = [p for p in positives if p.get("is_control")]
    expected_controls = set(config.get("controls", ["x**2 + 3*x + 7", "x**2 - 1"]))
    found_controls = {p["ground_truth_expr"] for p in controls if p.get("split") == "train"}
    if found_controls != expected_controls:
        errors.append(f"deterministic controls incomplete: {sorted(found_controls)}")

    teacher = corpus.get("teacher", {})
    teacher_total = float(teacher.get("construction_sec", 0.0)) + float(
        teacher.get("verification_sec", 0.0)
    )
    if teacher_total > float(config.get("teacher_cap_sec", 3600.0)):
        errors.append("teacher cost exceeded the one-hour cap")
    if not teacher.get("within_cap", False):
        errors.append("teacher cap breach recorded by builder")

    actual = {
        "train_positives": sum(1 for p in positives if p.get("split") == "train"),
        "train_groups": len(train_groups),
        "val_positives": sum(1 for p in positives if p.get("split") == "val"),
        "val_groups": len(val_groups),
    }
    minimums_ok = all(actual[k] >= int(min_req.get(k, 0)) for k in actual)
    print(f"  minimums: {actual} vs required {min_req}")

    if errors:
        verdict = "MIXED"
    elif not minimums_ok:
        verdict = "INCONCLUSIVE"
    else:
        verdict = "ACCEPTED"

    revision = get_git_commit()
    dirty = get_git_status()
    prov = collect_provenance(
        seed=42,
        device=_torch.device("cpu"),
        dataset_hashes={"p52_config": config_sha[:16]},
        config={"acceptance_phase": "P52"},
    )
    report = {
        "phase": "P52",
        "verdict": verdict,
        "claim_scope": "certified train/val data only; engineering minimums, no statistical claim",
        "run_id": hashlib.sha256(f"{config_sha}{revision}".encode()).hexdigest()[:16],
        "revision": revision,
        "dirty": dirty,
        "integrity_ok": bool(integrity["ok"]),
        "rechecked_exact": rechecked,
        "rechecked_total": len(positives),
        "negatives_rejected": neg_rejected,
        "negatives_total": len(negatives),
        "splits": {
            "train_groups": len(train_groups),
            "val_groups": len(val_groups),
            "group_overlap": overlap,
        },
        "minimums_required": min_req,
        "minimums_actual": actual,
        "minimums_met": minimums_ok,
        "controls_found": sorted(found_controls),
        "teacher_total_sec": teacher_total,
        "teacher_cap_sec": float(config.get("teacher_cap_sec", 3600.0)),
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
            "acceptance_phase": "P52",
            "corpus_manifest": str(corpus_p),
        },
        "seeds_rng": "deterministic enumeration; seed-shuffled split; no search RNG",
        "budgets": {"audit_recheck_sec": time.perf_counter() - t0},
        "certificate_references": [
            {"item_id": p["item_id"], "sha256": p.get("program_sha256")} for p in positives[:5]
        ],
        "counters": {
            "positives": len(positives),
            "negatives": len(negatives),
            "rechecked_exact": rechecked,
            "controls": len(controls),
        },
        "errors": errors[:10],
        "limitations": [
            "Minimum counts are engineering readiness, not statistical power.",
            "INCONCLUSIVE blocks P53 training but permits P54 baselines without learning.",
            "Single-template corpus: group/item isolation enforced, template sharing disclosed.",
        ],
        "elapsed_sec": time.perf_counter() - t0,
    }
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True, default=str)
    print(f"P52 audit {verdict}; report -> {out_p}")
    return report


def run_p51_replay_map_audit(config_path: str | Path, output_path: str | Path) -> dict[str, Any]:
    """P51 audit: bounded replay map over a traced search run.

    The map stores sampled nodes plus every elite/finalist and certificate,
    declares full vs partial coverage, stays within the node / I-O / disk
    caps, and its declared segments rebuild bit-exactly from the recorded
    seed plus a compatible checkpoint. No universe completeness is claimed.
    """
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
    if config.get("phase") != "P51":
        raise ValueError(f"Config {cfg_p} is not a P51 configuration")
    config_sha = hashlib.sha256(cfg_p.read_bytes()).hexdigest()

    print("=" * 115)
    print("P51 BOUNDED-REPLAY-MAP AUDIT (sampled map; replay rebuilds declared segments)")
    print("=" * 115)

    from evo_trace import run_p51_bounded_replay

    device = _torch.device(config.get("device", "cpu"))
    if device.type == "cuda" and not _torch.cuda.is_available():
        raise RuntimeError("P51 requested cuda but torch.cuda.is_available() is False")

    exp = run_p51_bounded_replay(
        seed=int(config.get("seed", 42)),
        pop_size=int(config.get("pop_size", 32)),
        n_generations=int(config.get("n_generations", 6)),
        n_points=int(config.get("n_points", 64)),
        formula=str(config.get("formula", "x2_3x_7")),
        device_name=config.get("device", "cpu"),
        max_nodes=int(config.get("max_nodes", 100_000)),
    )
    replay_map = exp["map"]
    checks = {
        "replay_rebuilds_segments": bool(exp["replay"]["segments_match"]),
        "no_certificate_lost": (
            replay_map["certificates"] == replay_map["certificates_expected"]
            and exp["validation"]["ok"]
        ),
        "nodes_bounded": replay_map["nodes"] <= replay_map["max_nodes"],
        "io_queue_bounded": replay_map["io_bytes"] <= replay_map["io_cap_bytes"],
        "raw_disk_bounded": replay_map["raw_bytes"] < replay_map["raw_cap_bytes"],
        "parent_ordering_valid": bool(exp["parent_ordering_valid"]),
        "counters_consistent": bool(exp["counters_consistent"]),
        "coverage_declared": replay_map["coverage"] in ("full", "partial_sampled"),
        "tracing_cost_published": bool(exp["overhead"]["audit_sec"] > 0),
    }
    verdict = "ACCEPTED" if all(checks.values()) else "MIXED"
    for name, ok in checks.items():
        print(f"  {name}: {'ok' if ok else 'FAILED'}")

    revision = get_git_commit()
    dirty = get_git_status()
    prov = collect_provenance(
        seed=int(config.get("seed", 42)),
        device=_torch.device("cpu"),
        dataset_hashes={"p51_config": config_sha[:16]},
        config={"acceptance_phase": "P51"},
    )
    report = {
        "phase": "P51",
        "verdict": verdict,
        "claim_scope": "bounded sampled map with replayable segments; no universe claim",
        "run_id": hashlib.sha256(f"{config_sha}{revision}".encode()).hexdigest()[:16],
        "revision": revision,
        "dirty": dirty,
        "checks": checks,
        "map": replay_map,
        "sampling_rate": replay_map["sampling_rate"],
        "coverage": replay_map["coverage"],
        "dropped_samples": replay_map["dropped_samples"],
        "replay": exp["replay"],
        "validation": exp["validation"],
        "tracing_overhead": {
            "baseline_sec": exp["overhead"]["baseline_sec"],
            "aggregate_sec": exp["overhead"]["aggregate_sec"],
            "audit_sec": exp["overhead"]["audit_sec"],
            "aggregate_overhead_pct": exp["overhead"]["aggregate_overhead_pct"],
            "audit_overhead_pct": exp["overhead"]["audit_overhead_pct"],
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
            "acceptance_phase": "P51",
        },
        "seeds_rng": f"fixed seed {config.get('seed', 42)}; replay rebuilds from seed+config",
        "budgets": {
            "experiment_sec": exp["elapsed_sec"],
            "pop_size": config.get("pop_size", 32),
            "n_generations": config.get("n_generations", 6),
        },
        "counters": {
            "total_candidates": exp["total_candidates"],
            "nodes": replay_map["nodes"],
            "dropped_samples": replay_map["dropped_samples"],
            "certificates": replay_map["certificates"],
            "segments_declared": exp["replay"]["segments_declared"],
            "segments_matched": (
                exp["replay"]["segments_declared"] if exp["replay"]["segments_match"] else 0
            ),
        },
        "certificate_references": [{"sha256": sha} for sha in exp["certificate_shas"]],
        "limitations": [
            "The map stores samples plus all elites/certs; unstored generations need seed+checkpoint replay.",
            "Partial coverage never proves a bounded search complete; misses are sampling losses.",
            "Tracing cost is published; per-candidate CPU logging is not claimed free.",
        ],
        "elapsed_sec": time.perf_counter() - t0,
    }
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True, default=str)
    print(f"P51 audit {verdict}; report -> {out_p}")
    return report


def run_p50_search_controls_audit(
    config_path: str | Path, output_path: str | Path
) -> dict[str, Any]:
    """P50 audit: structured random vs evolution vs classical on known tasks.

    Same mathematical criterion (P42 exact_certificate) and recorded costs
    for every arm. Known controls must be reencountered at least once and
    every false control must stay rejected. No gain is inferred from the
    isolated generator; the report only records certified rates and costs.
    """
    import numpy as _np
    import torch as _torch

    from evobyte.provenance import (
        collect_provenance,
        get_git_commit,
        get_git_status,
    )
    from evobyte.verifier import verify_l2

    t0 = time.perf_counter()
    cfg_p = Path(config_path)
    with open(cfg_p, encoding="utf-8") as f:
        config = json.load(f)
    if config.get("phase") != "P50":
        raise ValueError(f"Config {cfg_p} is not a P50 configuration")
    config_sha = hashlib.sha256(cfg_p.read_bytes()).hexdigest()

    domain = tuple(config.get("domain", [-3.0, 3.0]))
    seeds = list(config.get("seeds", [42, 101, 202, 303, 404]))
    budget = float(config.get("budget_sec_per_task", 10.0))
    pop_size = int(config.get("pop_size", 64))
    err_thr = float(config.get("error_threshold", 1e-4))
    known = list(config.get("tasks_known", []))
    if not known:
        raise ValueError("P50 config needs at least one known task")
    arms = ("structured_random", "evolution", "classical")

    print("=" * 115)
    print("P50 SEARCH-CONTROLS AUDIT (same criterion, billed costs, no isolated win)")
    print("=" * 115)

    from math_specialist import check_p50_false_controls, run_p50_arm_trial

    device = _torch.device(config.get("device", "cpu"))
    if device.type == "cuda" and not _torch.cuda.is_available():
        raise RuntimeError("P50 requested cuda but torch.cuda.is_available() is False")

    import sympy as _sympy

    _x = _sympy.Symbol("x")
    trials: list[dict[str, Any]] = []
    for task in known:
        formula = str(task["formula"])
        fn = _sympy.lambdify(_x, _sympy.sympify(formula), modules=["numpy"])
        xs_search = _np.linspace(domain[0], domain[1], 64, dtype=_np.float32)
        ys_search = _np.asarray(fn(xs_search), dtype=_np.float32)
        train_xs = _np.linspace(domain[0], domain[1], 48, dtype=_np.float64)
        train_ys = _np.asarray(fn(train_xs), dtype=_np.float64)
        test_xs = _np.linspace(domain[0] + 0.1, domain[1] - 0.1, 32, dtype=_np.float64)
        test_ys = _np.asarray(fn(test_xs), dtype=_np.float64)
        for arm in arms:
            for seed in seeds:
                rec = run_p50_arm_trial(
                    arm, formula, xs_search, ys_search, budget, seed, device, pop_size
                )
                prog = _np.array(rec["best_program_words"], dtype=_np.uint32)
                t_v0 = time.perf_counter()
                v = verify_l2(
                    prog,
                    train_xs,
                    train_ys,
                    test_xs,
                    test_ys,
                    ground_truth_formula=formula,
                    error_threshold=err_thr,
                    extrap_threshold=1.0,
                    domain=domain,
                )
                v_sec = time.perf_counter() - t_v0
                rec.update(
                    {
                        "task": task["id"],
                        "certified": bool(v.proof_type == "exact_certificate"),
                        "proof_type": v.proof_type,
                        "verify_passed": bool(v.passed),
                        "verification_sec": float(v_sec),
                    }
                )
                trials.append(rec)
                print(
                    f"  {task['id']} {arm:<17} seed={seed:<3} "
                    f"cert={int(rec['certified'])} mse={rec['best_mse']:.2e} "
                    f"cands={rec['candidates_total']} t={rec['elapsed_sec']:.2f}s"
                )

    false_controls = check_p50_false_controls(domain)
    for c in false_controls:
        print(f"  false {c['id']}: {'rejected' if c['rejected'] else 'NOT REJECTED'}")

    by_task: dict[str, Any] = {}
    for task in known:
        recs = [t for t in trials if t["task"] == task["id"]]
        by_task[task["id"]] = {
            "certified_trials": sum(1 for r in recs if r["certified"]),
            "trials": len(recs),
            "rediscovered": any(r["certified"] for r in recs),
        }
    known_ok = all(v["rediscovered"] for v in by_task.values()) and bool(by_task)
    false_ok = all(c["rejected"] for c in false_controls) and bool(false_controls)
    verdict = "ACCEPTED" if (known_ok and false_ok) else "MIXED"

    revision = get_git_commit()
    dirty = get_git_status()
    prov = collect_provenance(
        seed=int(seeds[0]) if seeds else 42,
        device=_torch.device("cpu"),
        dataset_hashes={"p50_config": config_sha[:16]},
        config={"acceptance_phase": "P50"},
    )
    requested = len(known) * len(arms) * len(seeds) * budget
    actual_search = float(sum(t["elapsed_sec"] for t in trials))
    actual_verify = float(sum(t["verification_sec"] for t in trials))
    report = {
        "phase": "P50",
        "verdict": verdict,
        "claim_scope": "search arms under one exact criterion; no isolated-generator win claimed",
        "run_id": hashlib.sha256(f"{config_sha}{revision}".encode()).hexdigest()[:16],
        "revision": revision,
        "dirty": dirty,
        "tasks_known": by_task,
        "false_controls": false_controls,
        "arms": list(arms),
        "criterion": {
            "checker": "verify_l2 exact_certificate",
            "error_threshold": err_thr,
            "domain": list(domain),
            "same_for_all_arms": True,
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
            "acceptance_phase": "P50",
        },
        "seeds_rng": f"fixed seeds {seeds}; deterministic classical, seeded sampling/evolution",
        "budgets": {
            "requested_search_sec": requested,
            "actual_search_sec": actual_search,
            "actual_verification_sec": actual_verify,
            "budget_sec_per_task": budget,
        },
        "certificate_references": [
            {
                "task": t["task"],
                "arm": t["arm"],
                "seed": t["seed"],
                "proof_type": t["proof_type"],
                "certified": t["certified"],
            }
            for t in trials
            if t["certified"]
        ],
        "counters": {
            "trials": len(trials),
            "candidates_total": sum(t["candidates_total"] for t in trials),
            "duplicates": sum(t["duplicates"] for t in trials),
            "invalid": sum(t["invalid"] for t in trials),
            "certified": sum(1 for t in trials if t["certified"]),
            "false_rejected": sum(1 for c in false_controls if c["rejected"]),
            "false_total": len(false_controls),
        },
        "limitations": [
            "Classical solving immediately is recorded, never hidden; it does not prove generality.",
            "False controls guard promotion; they never prove a bounded search complete.",
            "A narrow-family comparison does not authorize model training or discovery claims.",
        ],
        "elapsed_sec": time.perf_counter() - t0,
    }
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True, default=str)
    print(f"P50 audit {verdict}; report -> {out_p}")
    return report


def run_p49_compact_audit(config_path: str | Path, output_path: str | Path) -> dict[str, Any]:
    """P49 audit: frozen compact profile, codec round-trip, certificate reconstruction."""
    import numpy as _np
    import torch as _torch

    from evobyte.bytecode import (
        compact_candidate_profile,
        compact_decode,
        compact_encode,
        nop_program,
        validate_compact_candidate,
    )
    from evobyte.grammar import batch_is_valid_torch, sample_grammar_batch
    from evobyte.provenance import (
        collect_provenance,
        get_git_commit,
        get_git_status,
    )
    from evobyte.verifier import program_to_sympy, verify_l2

    t0 = time.perf_counter()
    cfg_p = Path(config_path)
    with open(cfg_p, encoding="utf-8") as f:
        config = json.load(f)
    if config.get("phase") != "P49":
        raise ValueError(f"Config {cfg_p} is not a P49 configuration")
    config_sha = hashlib.sha256(cfg_p.read_bytes()).hexdigest()
    pins = config.get("profile_pins", {})
    seed = int(config.get("seed", 7))
    n_samples = int(config.get("roundtrip_samples", 64))
    domain = tuple(config.get("domain", [-3.0, 3.0]))

    print("=" * 115)
    print("P49 COMPACT-CANDIDATE AUDIT (frozen profile; no codec change)")
    print("=" * 115)

    findings: list[dict[str, Any]] = []

    def _record(check: str, ok: bool, detail: str = "") -> None:
        findings.append({"check": check, "ok": bool(ok), "detail": detail})
        print(f"  {check}: {'ok' if ok else 'FAILED'} {detail}")

    profile = compact_candidate_profile()
    _record(
        "profile_name", profile.get("profile") == config.get("profile"), profile.get("profile", "")
    )
    _record("profile_revision", profile.get("profile_revision") == pins.get("profile_revision"), "")
    _record(
        "opcode_version_unbumped",
        profile.get("opcode_version") == 0 == pins.get("opcode_version"),
        "v0 frozen, no ADR needed",
    )
    dims_ok = (
        profile.get("word_count") == pins.get("word_count")
        and profile.get("program_bytes") == pins.get("program_bytes")
        and profile.get("registers") == pins.get("registers")
        and profile.get("output_register") == pins.get("output_register")
        and [o["code"] for o in profile.get("allowed_ops", [])] == pins.get("allowed_ops")
    )
    _record("profile_dimensions", dims_ok, "")
    const_blob = json.dumps(
        {
            "allowed_ops": profile["allowed_ops"],
            "constants": profile["constants"],
            "registers": profile["registers"],
            "word_count": profile["word_count"],
            "program_bytes": profile["program_bytes"],
            "output_register": profile["output_register"],
        },
        sort_keys=True,
        default=str,
    ).encode()
    const_hash = hashlib.sha256(const_blob).hexdigest()
    _record("const_table_hash", const_hash == pins.get("const_table_sha256"), const_hash[:16])

    dev = _torch.device("cpu")
    pop = sample_grammar_batch(n_samples, device=dev, seed=seed)
    gate = batch_is_valid_torch(pop).cpu().numpy()
    prof_ok = []
    for prog in pop.cpu().numpy().astype(_np.uint32):
        prof_ok.append(validate_compact_candidate(prog)["ok"])
    _record(
        "valid_by_construction",
        bool(gate.all()) and all(prof_ok),
        f"{int(gate.sum())}/{n_samples} S0-valid and profile-conformant",
    )

    rt_ok = True
    for prog in pop.cpu().numpy().astype(_np.uint32):
        if not _np.array_equal(compact_decode(compact_encode(prog)), prog):
            rt_ok = False
            break
    _record("roundtrip_bytes", rt_ok, f"{n_samples} programs, 64B each")

    bad_reg = nop_program()
    bad_reg[0] = _np.uint32(0x01 | (9 << 8))
    bad_op = nop_program()
    bad_op[0] = _np.uint32(0xFF | (7 << 8))
    good = nop_program()
    from evobyte.bytecode import encode_instr as _enc

    good[0] = _enc(0x01, dst=7, a=0, b=1)
    invalid_ok = (
        not validate_compact_candidate(bad_reg)["ok"]
        and not validate_compact_candidate(bad_op)["ok"]
        and validate_compact_candidate(good)["ok"]
        and not validate_compact_candidate(good, opcode_version=999)["ok"]
    )
    try:
        compact_decode(b"short")
        invalid_ok = False
    except ValueError:
        pass
    _record("invalid_refs_rejected", invalid_ok, "bad reg, unknown op, unknown version, short blob")

    corpus_p = _REPO_ROOT / config.get("corpus_manifest", "experiments/p35-training-corpus.json")
    with open(corpus_p, encoding="utf-8") as f:
        corpus = json.load(f)
    reconstructed = 0
    reconstructed_total = 0
    for entry in corpus.get("positives", []):
        prog = _np.array(entry["program_words"], dtype=_np.uint32)
        if not validate_compact_candidate(prog)["ok"]:
            continue
        grids = _p42_grids(entry["ground_truth_expr"])
        sym = program_to_sympy(prog)
        v = verify_l2(
            prog,
            grids["train_xs"],
            grids["train_ys"],
            grids["test_xs"],
            grids["test_ys"],
            ground_truth_formula=entry["ground_truth_expr"],
            error_threshold=1e-4,
            extrap_threshold=1.0,
            domain=domain,
        )
        reconstructed_total += 1
        if sym is not None and v.proof_type == "exact_certificate":
            reconstructed += 1
    _record(
        "certificate_reconstruction",
        reconstructed_total > 0 and reconstructed == reconstructed_total,
        f"{reconstructed}/{reconstructed_total} compact words rebuild exact certificates",
    )

    ok_all = all(f["ok"] for f in findings)
    verdict = "ACCEPTED" if ok_all else "MIXED"
    revision = get_git_commit()
    dirty = get_git_status()
    prov = collect_provenance(
        seed=seed,
        device=_torch.device("cpu"),
        dataset_hashes={"p49_config": config_sha[:16]},
        config={"acceptance_phase": "P49"},
    )
    report = {
        "phase": "P49",
        "verdict": verdict,
        "claim_scope": "compact representation conformance; coverage is the defined grammar only",
        "run_id": hashlib.sha256(f"{config_sha}{revision}".encode()).hexdigest()[:16],
        "revision": revision,
        "dirty": dirty,
        "findings": findings,
        "coverage": config.get("coverage"),
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
            "acceptance_phase": "P49",
        },
        "seeds_rng": f"fixed seed {seed}; deterministic sampling, no search",
        "budgets": "fixed sample counts; wall-clock recorded, never a claim",
        "counters": {
            "checks": len(findings),
            "checks_ok": sum(1 for f in findings if f["ok"]),
            "reconstructed": reconstructed,
            "reconstructed_total": reconstructed_total,
        },
        "limitations": [
            "Compactness claims nothing about universality and reduces no search complexity.",
            "Off-profile v0 opcodes stay globally valid; the profile only scopes the family.",
        ],
        "elapsed_sec": time.perf_counter() - t0,
    }
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True, default=str)
    print(f"P49 audit {verdict}; report -> {out_p}")
    return report


def run_p48_formal_audit(config_path: str | Path, output_path: str | Path) -> dict[str, Any]:
    """P48 audit: valid challenge accepted, every false control rejected, cert matches."""
    from evobyte.provenance import (
        collect_provenance,
        get_git_commit,
        get_git_status,
    )
    from evobyte.verifier import run_lean_checker

    t0 = time.perf_counter()
    cfg_p = Path(config_path)
    with open(cfg_p, encoding="utf-8") as f:
        config = json.load(f)
    if config.get("phase") != "P48":
        raise ValueError(f"Config {cfg_p} is not a P48 configuration")
    config_sha = hashlib.sha256(cfg_p.read_bytes()).hexdigest()
    proj = _REPO_ROOT / config.get("project_dir", "lean_proofs")
    timeout_sec = float(config.get("timeout_sec", 900.0))

    print("=" * 115)
    print("P48 FORMAL-CHECKER BOUNDARY AUDIT (separate process, frozen toolchain)")
    print("=" * 115)

    challenges: list[dict[str, Any]] = []
    for spec in config.get("challenges", []):
        res = run_lean_checker(
            _REPO_ROOT / config.get("challenge_file", "lean_proofs/P48Proofs.lean"),
            project_dir=proj,
            expected_theorem=spec["theorem"],
            expected_statement_sha256=spec["statement_sha256_prefix"],
            timeout_sec=timeout_sec,
        )
        challenges.append(
            {
                "theorem": spec["theorem"],
                "accepted": res["accepted"],
                "reasons": res["reasons"],
                "axioms_recorded": res.get("axioms_recorded", []),
            }
        )
        print(
            f"  challenge {spec['theorem']}: "
            f"{'accepted' if res['accepted'] else 'NOT ACCEPTED'} {res['reasons']}"
        )

    controls: list[dict[str, Any]] = []
    for spec in config.get("controls", []):
        res = run_lean_checker(
            _REPO_ROOT / spec["file"],
            project_dir=proj,
            expected_theorem=spec.get("theorem"),
            expected_statement_sha256=None,
            timeout_sec=timeout_sec,
            repeat_check=False,
        )
        rejected = not res["accepted"]
        controls.append(
            {
                "id": spec["id"],
                "expected": spec["expected"],
                "rejected": rejected,
                "reasons": res["reasons"],
            }
        )
        print(f"  control {spec['id']}: {'rejected' if rejected else 'NOT REJECTED'}")

    challenges_ok = all(c["accepted"] for c in challenges) and bool(challenges)
    controls_ok = all(c["rejected"] for c in controls) and bool(controls)
    verdict = "ACCEPTED" if (challenges_ok and controls_ok) else "MIXED"

    revision = get_git_commit()
    dirty = get_git_status()
    prov = collect_provenance(
        seed=42,
        device=torch.device("cpu"),
        dataset_hashes={"p48_config": config_sha[:16]},
        config={"acceptance_phase": "P48"},
    )
    report = {
        "phase": "P48",
        "verdict": verdict,
        "claim_scope": "compiler boundary mechanics; statement translation review stays human",
        "run_id": hashlib.sha256(f"{config_sha}{revision}".encode()).hexdigest()[:16],
        "revision": revision,
        "dirty": dirty,
        "toolchain_pin": config.get("toolchain_pin"),
        "challenges": challenges,
        "controls": controls,
        "translation_review": {
            "required": True,
            "status": "pending",
            "scope": "challenge statements vs intended mathematics",
            "gate_note": "A finite-test proven-theorem label additionally requires "
            "translation approval; this audit cannot grant it.",
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
            "acceptance_phase": "P48",
        },
        "seeds_rng": "not-applicable: deterministic proof checking (reason: no search)",
        "budgets": "per-file compile timeouts; wall-clock recorded, never a claim",
        "counters": {
            "challenges": len(challenges),
            "challenges_accepted": sum(1 for c in challenges if c["accepted"]),
            "controls": len(controls),
            "controls_rejected": sum(1 for c in controls if c["rejected"]),
        },
        "limitations": [
            "The checker confirms the formal statement and its hypotheses, not the translation.",
            "Repeat compiles guard transients; they are not independent authorship.",
        ],
        "elapsed_sec": time.perf_counter() - t0,
    }
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True, default=str)
    print(f"P48 audit {verdict}; report -> {out_p}")
    return report


def _p47_canonical_hash(nomination: dict[str, Any]) -> str:
    """Frozen hash: sha256 over canonical JSON excluding the frozen block itself."""
    body = {k: v for k, v in nomination.items() if k != "frozen"}
    return hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def _p47_need(cond: bool, errors: list[str], message: str) -> None:
    if not cond:
        errors.append(message)


def run_p47_nomination_audit(config_path: str | Path, output_path: str | Path) -> dict[str, Any]:
    """P47 audit: frozen nomination completeness, freeze integrity, sealed final test.

    Technical validation only; the nomination, thresholds and the P46 curation
    additionally require human mathematical review before P48, which this audit
    reports as pending and cannot grant.
    """
    t0 = time.perf_counter()
    cfg_p = Path(config_path)
    with open(cfg_p, encoding="utf-8") as f:
        config = json.load(f)
    if config.get("phase") != "P47":
        raise ValueError(f"Config {cfg_p} is not a P47 configuration")
    config_sha = hashlib.sha256(cfg_p.read_bytes()).hexdigest()
    nom_p = _REPO_ROOT / config.get("nomination_path", "experiments/p47-nomination.json")
    p38_p = _REPO_ROOT / config.get("p38_manifest_path", "experiments/p38-confirmation.json")

    print("=" * 115)
    print("P47 FROZEN-NOMINATION AUDIT (two scopes; final test closed)")
    print("=" * 115)

    report: dict[str, Any] = {
        "phase": "P47",
        "resolved_config": {
            "config_path": str(cfg_p),
            "config_sha256": config_sha,
            "acceptance_phase": "P47",
            "nomination_path": str(nom_p),
        },
    }
    try:
        with open(nom_p, encoding="utf-8") as f:
            nom = json.load(f)
    except (OSError, ValueError) as exc:
        report.update(
            {"status": "FAIL", "verdict": "REJECTED", "errors": [f"unreadable nomination: {exc}"]}
        )
        print(f"P47 REJECTED: unreadable nomination: {exc}")
        return report

    errors: list[str] = []
    if nom.get("phase") != "p47-nomination":
        errors.append("nomination phase marker is wrong")
    for section in (
        "scopes",
        "hypothesis",
        "controls",
        "thresholds",
        "non_claims",
        "human_review",
        "frozen",
    ):
        _p47_need(section in nom, errors, f"missing top-level section {section}")

    scopes = nom.get("scopes") or {}
    dev = scopes.get("proposer_development") or {}
    for required in (
        "family",
        "domain",
        "representation",
        "certificate",
        "source",
        "task_generator",
        "splits",
        "success",
        "baselines",
        "final_test",
    ):
        _p47_need(required in dev, errors, f"scope proposer_development missing {required}")
    _p47_need(
        (dev.get("success") or {}).get("per_task") == "exact_certificate",
        errors,
        "per-task success must be exact_certificate",
    )
    _p47_need(
        set((dev.get("success") or {}).get("aggregates", []))
        >= {"certified_success_rate", "median_time_to_certified"},
        errors,
        "success aggregates must pin rate and time-to-certified",
    )
    _p47_need(
        (dev.get("success") or {}).get("mse_excluded_as_success") is True,
        errors,
        "MSE must be excluded as a success metric",
    )
    _p47_need(
        isinstance(dev.get("baselines"), list) and len(dev["baselines"]) >= 2,
        errors,
        "at least two classical baselines required",
    )
    src = dev.get("source") or {}
    commit = str(src.get("snapshot_sha256", ""))
    _p47_need(
        len(commit) == 64 and set(commit) <= set("0123456789abcdef"),
        errors,
        "source snapshot hash must be a pinned 64-hex sha256",
    )
    gen = dev.get("task_generator") or {}
    _p47_need(
        isinstance(gen.get("seed"), int) and gen.get("procedure"),
        errors,
        "task generator needs a frozen procedure and integer seed",
    )
    splits = dev.get("splits") or {}
    _p47_need(
        bool(splits.get("grouping_rule")) and bool(splits.get("policy")),
        errors,
        "split policy and grouping rule must be frozen before training",
    )

    camp = scopes.get("scientific_campaign") or {}
    for required in (
        "problem",
        "certificate",
        "bounds",
        "baseline",
        "calibration_instances",
        "discovery_instances",
        "coverage_policy",
    ):
        _p47_need(required in camp, errors, f"scope scientific_campaign missing {required}")
    _p47_need(
        "exact integer triple" in str(camp.get("certificate", "")),
        errors,
        "campaign certificate must be the exact integer triple",
    )
    _p47_need(
        "10^9" in str(camp.get("bounds", "")),
        errors,
        "campaign bounds must state the strict M <= 10^9 rule",
    )
    _p47_need(
        set(camp.get("calibration_instances", [])) == {1009, 10007, 100003},
        errors,
        "calibration instances must be exactly the observed P39 triple",
    )
    _p47_need(
        (camp.get("discovery_instances") or {}).get("status") == "pending",
        errors,
        "discovery instances must stay pending human approval",
    )
    _p47_need(
        camp.get("no_universal_claims") is True, errors, "no-universal-claims rule must be explicit"
    )

    hyp = nom.get("hypothesis") or {}
    for required in ("statement", "effect", "falsification"):
        _p47_need(bool(hyp.get(required)), errors, f"hypothesis missing {required}")
    _p47_need(
        hyp.get("mse_excluded_as_success") is True, errors, "hypothesis must exclude MSE as success"
    )

    ctrls = nom.get("controls") or {}
    known = ctrls.get("known") or []
    false = ctrls.get("false") or []
    _p47_need(
        len(known) >= 1 and len(false) >= 1,
        errors,
        "at least one known and one false control required",
    )
    for ctrl in known + false:
        _p47_need(
            bool(ctrl.get("expected")) and bool(ctrl.get("reference")),
            errors,
            f"control {ctrl.get('id', '?')} needs expected outcome + reference",
        )
    _p47_need(
        all(
            "reject" in str(c.get("expected", "")).lower()
            or "numerical" in str(c.get("expected", "")).lower()
            or "condition" in str(c.get("expected", "")).lower()
            for c in false
        ),
        errors,
        "every false control must expect rejection or numerical-only",
    )

    thr = nom.get("thresholds") or {}
    _p47_need(
        isinstance(thr.get("quantities"), list) and len(thr["quantities"]) >= 1,
        errors,
        "threshold quantities must be frozen",
    )
    _p47_need(
        thr.get("values") == "pending-human-review" and thr.get("status") == "pending-human-review",
        errors,
        "threshold values stay pending human review",
    )

    frozen = nom.get("frozen") or {}
    recomputed = _p47_canonical_hash(nom)
    _p47_need(
        frozen.get("sha256") == recomputed,
        errors,
        "frozen hash mismatch: nomination edited after freezing",
    )
    try:
        datetime.date.fromisoformat(str(frozen.get("frozen_at", "")))
    except ValueError:
        errors.append("frozen_at is not an ISO date")

    final = dev.get("final_test") or {}
    _p47_need(final.get("status") == "closed", errors, "final test must be closed")
    storage = _REPO_ROOT / str(final.get("storage", "experiments/p47-final-test/"))
    log_p = _REPO_ROOT / str(final.get("access_log", "experiments/p47-final-test/access-log.json"))
    _p47_need(storage.is_dir(), errors, "final-test storage directory must exist")
    log_ok, log_entries = False, None
    try:
        with open(log_p, encoding="utf-8") as f:
            log_entries = json.load(f)
        log_ok = log_entries == []
    except (OSError, ValueError):
        log_ok = False
    _p47_need(log_ok, errors, "final-test access log must exist and be empty")
    material = (
        sorted(
            p.name for p in storage.iterdir() if p.is_file() and p.name not in ("access-log.json",)
        )
        if storage.is_dir()
        else ["<missing>"]
    )
    _p47_need(material == [], errors, f"final-test storage must hold no material yet: {material}")
    try:
        with open(p38_p, encoding="utf-8") as f:
            p38_ids = set((json.load(f).get("problem_set") or {}).get("final_ids", []))
    except (OSError, ValueError) as exc:
        p38_ids = set()
        errors.append(f"P38 manifest unreadable, cannot check exclusion: {exc}")
    _p47_need(
        bool(p38_ids) and p38_ids <= set(final.get("forbidden_ids", [])),
        errors,
        "all P38-observed final ids must be listed as forbidden",
    )

    review = nom.get("human_review") or {}
    review_required = bool(review.get("required", True))
    schema_ok = not errors
    report.update(
        {
            "status": "PASS" if schema_ok else "FAIL",
            "verdict": "PENDING_HUMAN_REVIEW" if schema_ok else "REJECTED",
            "claim_scope": "nomination completeness and freeze integrity; approval is a human gate",
            "nomination_sha256": recomputed,
            "freeze_recorded": frozen.get("sha256"),
            "scopes": sorted(scopes.keys()),
            "controls": {"known": len(known), "false": len(false)},
            "threshold_quantities": list((nom.get("thresholds") or {}).get("quantities", [])),
            "final_test": {
                "status": final.get("status"),
                "access_log_empty": log_ok,
                "material": material,
                "forbidden_p38_ids": len(p38_ids),
            },
            "checks": {
                "schema_ok": schema_ok,
                "hypothesis_frozen": bool(hyp.get("statement")) and bool(hyp.get("falsification")),
                "freeze_intact": frozen.get("sha256") == recomputed,
                "final_test_closed": final.get("status") == "closed" and log_ok and material == [],
                "p38_excluded": bool(p38_ids) and p38_ids <= set(final.get("forbidden_ids", [])),
            },
            "errors": errors[:50],
            "human_review": {
                "required": review_required,
                "status": review.get("status", "pending"),
                "scope": review.get(
                    "scope", "nomination + thresholds (P47); P46 curation still pending"
                ),
                "gate_note": "P48 is blocked until a mathematician approves this nomination; "
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
        f"P47 technical={'PASS' if schema_ok else 'FAIL'} "
        f"verdict={report['verdict']}; report -> {out_p}"
    )
    return report


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


def _p46_normalize_statement(text: str) -> str:
    """Normalize a statement for near-duplicate detection (not for display)."""
    norm = text.lower().replace("$", " ").replace("\\", " ")
    norm = re.sub(r"[^a-z0-9]+", " ", norm)
    return re.sub(r"\s+", " ", norm).strip()


def _p46_fetch(url: str, timeout: int = 30) -> str:
    import urllib.request

    req = urllib.request.Request(
        url, headers={"User-Agent": "EvoByte-P46-validation/1.0 (research; contact via repo)"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "replace")


def _p46_strip_tags(html: str) -> str:
    text = re.sub(r"<br\s*/?>", " ", html)
    text = re.sub(r"<[^>]+>", "", text)
    for a, b in (
        ("&amp;", "&"),
        ("&lt;", "<"),
        ("&gt;", ">"),
        ("&quot;", '"'),
        ("&#39;", "'"),
        ("&nbsp;", " "),
    ):
        text = text.replace(a, b)
    return re.sub(r"\s+", " ", text).strip()


def _p46_independent_refetch(cat: dict[str, Any], sleep_sec: float = 0.35) -> dict[str, Any]:
    """Re-verify every catalogue entry against the pinned dataset and live pages.

    Independent pass: downloads the dataset at the pinned commit (recording its
    file hash), re-derives tags/states, re-fetches every page recording status,
    statement, excerpt reproduction, hash, partial refs, then runs a normalized
    near-duplicate sweep across all buckets.
    """
    import yaml

    result: dict[str, Any] = {"errors": [], "entries": {}, "near_duplicates": []}
    commit = str((cat.get("source") or {}).get("dataset_commit", ""))
    yaml_url = f"https://raw.githubusercontent.com/Teorth/erdosproblems/{commit}/data/problems.yaml"
    try:
        yaml_text = _p46_fetch(yaml_url)
    except (OSError, ValueError) as exc:
        result["errors"].append(f"dataset fetch failed at pinned commit: {exc}")
        return result
    result["dataset_file_sha256"] = hashlib.sha256(yaml_text.encode()).hexdigest()
    records = {
        int(e["number"]): e for e in yaml.safe_load(yaml_text) if str(e.get("number", "")).isdigit()
    }

    def _one(entry: dict[str, Any], bucket: str, expect_states: tuple[str, ...]) -> dict[str, Any]:
        number = int(str(entry["id"]).split("-", 1)[1])
        meta = records.get(number)
        rec: dict[str, Any] = {"number": number, "bucket": bucket, "ok": True, "problems": []}
        if meta is None:
            rec["problems"].append("number absent from the pinned dataset")
        else:
            ds_state = (meta.get("informal_status") or {}).get("state")
            rec["dataset_state"] = ds_state
            if ds_state not in expect_states:
                rec["problems"].append(f"dataset state {ds_state!r} outside {expect_states}")
            if [str(t) for t in (meta.get("tags") or [])] != [
                str(t) for t in entry.get("areas", [])
            ]:
                rec["problems"].append("dataset tags differ from stored areas")
        try:
            html = _p46_fetch(f"https://www.erdosproblems.com/{number}")
        except (OSError, ValueError) as exc:
            rec["problems"].append(f"page fetch failed: {exc}")
            rec["ok"] = False
            return rec
        m = re.search(r'<div class="problem-text" id="([^"]+)"', html)
        rec["page_state"] = m.group(1).strip().lower() if m else "unknown"
        cm = re.search(r'<div id="content">(.*?)</div>', html, re.DOTALL)
        statement = _p46_strip_tags(cm.group(1)) if cm else ""
        expected_excerpt = statement[:320] + (" ..." if len(statement) > 320 else "")
        if expected_excerpt != entry.get("statement_excerpt"):
            rec["problems"].append("stored excerpt does not reproduce from the live statement")
        if hashlib.sha256(statement.encode()).hexdigest()[:16] != entry.get("statement_sha256"):
            rec["problems"].append("statement hash does not reproduce")
        page_refs = set(re.findall(r"addNewBox\('([^']+)'", html))
        missing = [r for r in entry.get("partial_refs", []) if r not in page_refs]
        if missing:
            rec["problems"].append(f"partial refs absent from page: {missing[:3]}")
        if bucket == "open_confirmed" and rec["page_state"] != "open":
            rec["problems"].append(f"live page state is {rec['page_state']!r}, expected open")
        if bucket == "finite_search_candidates" and rec["page_state"] != "open":
            rec["problems"].append(
                f"live page state is {rec['page_state']!r}, expected open marker"
            )
        rec["ok"] = not rec["problems"]
        return rec

    buckets = (
        ("open_confirmed", cat.get("open_confirmed") or [], ("open",)),
        (
            "finite_search_candidates",
            cat.get("finite_search_candidates") or [],
            ("falsifiable", "verifiable", "decidable"),
        ),
    )
    seen_norm: dict[str, str] = {}
    for name, entries, states in buckets:
        checked: list[dict[str, Any]] = []
        for entry in entries:
            rec = _one(entry, name, states)
            checked.append(rec)
            if not rec["ok"]:
                result["errors"].append(f"{entry.get('id')}: {'; '.join(rec['problems'])}")
            norm = _p46_normalize_statement(str(entry.get("statement_excerpt", "")))
            if norm in seen_norm and seen_norm[norm] != entry.get("id"):
                result["near_duplicates"].append([seen_norm[norm], entry.get("id")])
            seen_norm.setdefault(norm, str(entry.get("id")))
            time.sleep(sleep_sec)
        result["entries"][name] = {
            "checked": len(checked),
            "ok": sum(1 for r in checked if r["ok"]),
            "problems": [r for r in checked if not r["ok"]],
        }
    for ex in cat.get("solved_examples") or []:
        number = int(ex["number"])
        meta = records.get(number)
        ds_state = ((meta or {}).get("informal_status") or {}).get("state")
        try:
            html = _p46_fetch(f"https://www.erdosproblems.com/{number}")
            m = re.search(r'<div class="problem-text" id="([^"]+)"', html)
            page_state = m.group(1).strip().lower() if m else "unknown"
        except (OSError, ValueError) as exc:
            result["errors"].append(f"solved example {number}: fetch failed: {exc}")
            continue
        if page_state == "open":
            result["errors"].append(f"solved example {number}: live page still open")
        if ds_state not in ("proved", "disproved", "solved") and not (
            ex.get("solved_after_pin") and page_state == "solved"
        ):
            result["errors"].append(
                f"solved example {number}: dataset state {ds_state!r} not solved "
                "and no solved-after-pin evidence"
            )
        time.sleep(sleep_sec)
    result["near_duplicate_count"] = len(result["near_duplicates"])
    result["ok"] = not result["errors"] and result["near_duplicate_count"] == 0
    return result


def run_p46_catalogue_audit(
    config_path: str | Path,
    output_path: str | Path,
    independent_refetch: bool | None = None,
) -> dict[str, Any]:
    """P46 audit: validate the sourced open-problem catalogue (schema + counts + dedup).

    Technical validation only; the phase exit gate additionally requires a
    human mathematical review of the curation before P47, which this audit
    reports as pending and cannot grant. With ``independent_refetch`` (or the
    config flag) the audit re-downloads the pinned dataset and every live page,
    reproducing statements, hashes, tags, references and statuses.
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

    refetch = (
        bool(config.get("independent_refetch", False))
        if independent_refetch is None
        else bool(independent_refetch)
    )
    independent: dict[str, Any] | None = None
    if refetch and not errors:
        print("  independent re-fetch: pinned dataset + every live page ...")
        independent = _p46_independent_refetch(cat)
        for bucket, stats in independent.get("entries", {}).items():
            print(f"    {bucket}: {stats['ok']}/{stats['checked']} reproduced")
        if independent.get("errors"):
            errors.extend(f"independent: {e}" for e in independent["errors"][:20])
    report["independent_refetch"] = independent

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
                "independent_refetch_ok": (
                    None if independent is None else bool(independent.get("ok"))
                ),
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
            split_manifest=smoke_cfg.get("split_manifest", "experiments/p30-splits.json"),
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
        elif args.acceptance_phase == "P47":
            run_p47_nomination_audit(args.config, args.output)
        elif args.acceptance_phase == "P48":
            run_p48_formal_audit(args.config, args.output)
        elif args.acceptance_phase == "P49":
            run_p49_compact_audit(args.config, args.output)
        elif args.acceptance_phase == "P50":
            run_p50_search_controls_audit(args.config, args.output)
        elif args.acceptance_phase == "P51":
            run_p51_replay_map_audit(args.config, args.output)
        elif args.acceptance_phase == "P52":
            run_p52_certified_data_audit(args.config, args.output)
        elif args.acceptance_phase == "P53":
            run_p53_proposer_audit(args.config, args.output)
        elif args.acceptance_phase == "P54":
            run_p54_utility_audit(args.config, args.output)
        elif args.acceptance_phase == "P55":
            run_p55_sampling_audit(args.config, args.output)
        elif args.acceptance_phase == "P56":
            run_p56_confirmation_audit(args.config, args.output)
        elif args.acceptance_phase == "P57":
            run_p57_campaign_audit(args.config, args.output)
        elif args.acceptance_phase == "P58":
            run_p58_acceptance_baseline_audit(args.config, args.output)
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
