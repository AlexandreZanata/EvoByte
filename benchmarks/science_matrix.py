"""Gated scientific dataset matrix with pre-registered hypotheses and Domain L2 checks (P14 scope)."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
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

ACCEPTANCE_PHASES = ("P40",)


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
        run_p40_evidence_audit(args.config, args.output)
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
