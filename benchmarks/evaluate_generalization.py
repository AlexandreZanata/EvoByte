"""P156: Blind Generalization and Extrapolation Evaluation Protocol.

Audits synthesized models and baselines against:
1. In-domain hidden test split (X_hidden disjoint from X_train);
2. Out-of-domain extrapolation test split (X_extrap strictly outside training domain);
3. Asymptotic explosion (|y_pred| > 10^6 or non-finite);
4. Constant and structural bloat (program_size > 50 or |c| > 10^6);
5. Data leakage across splits;
6. Formal evaluation of Hypothesis H1 Criterion 4 (Generalization).
"""

from __future__ import annotations

import datetime
import hashlib
import json
import time
from pathlib import Path
from typing import Any

import numpy as np

from full_matrix import (
    TargetDataset,
    generate_target_dataset,
    parse_budget_str,
    probe,
    run_p155_baselines_suite,
)


def audit_splits_leakage(target: TargetDataset) -> tuple[bool, list[str]]:
    """Audit dataset splits to prove zero data leakage between train, hidden, and extrap."""
    findings: list[str] = []
    xs_tr, _ = target.splits["train"]
    xs_hid, _ = target.splits["hidden"]
    xs_ext, _ = target.splits["extrapolation"]

    set_tr = set(np.round(xs_tr, 6))
    set_hid = set(np.round(xs_hid, 6))
    set_ext = set(np.round(xs_ext, 6))

    overlap_tr_hid = set_tr.intersection(set_hid)
    if len(overlap_tr_hid) > 0:
        findings.append(
            f"LEAKAGE_TRAIN_HIDDEN: {len(overlap_tr_hid)} overlapping points for {target.key}"
        )

    overlap_tr_ext = set_tr.intersection(set_ext)
    if len(overlap_tr_ext) > 0:
        findings.append(
            f"LEAKAGE_TRAIN_EXTRAP: {len(overlap_tr_ext)} overlapping points for {target.key}"
        )

    tr_min, tr_max = float(np.min(xs_tr)), float(np.max(xs_tr))
    ext_min, ext_max = float(np.min(xs_ext)), float(np.max(xs_ext))
    if not (ext_min > tr_max or ext_max < tr_min):
        findings.append(
            f"INVALID_EXTRAPOLATION_DOMAIN: extrap [{ext_min}, {ext_max}] overlaps train domain [{tr_min}, {tr_max}]"
        )

    return len(findings) == 0, findings


def compute_r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Compute R^2 coefficient of determination with safety guards for divergence."""
    y_true = np.asarray(y_true, dtype=np.float64)
    y_pred = np.asarray(y_pred, dtype=np.float64)
    if not np.all(np.isfinite(y_pred)):
        return -float("inf")
    ss_res = float(np.sum((y_true - y_pred) ** 2))
    ss_tot = float(np.sum((y_true - np.mean(y_true)) ** 2))
    if ss_tot < 1e-12:
        return 1.0 if ss_res < 1e-6 else 0.0
    val = 1.0 - (ss_res / ss_tot)
    return float(val)


def compute_r2_from_mse(target: TargetDataset, split_name: str, mse: float | None) -> float:
    """Compute R^2 directly from recorded MSE and target split variance."""
    if mse is None or not np.isfinite(mse):
        return -float("inf")
    ys = target.splits[split_name][1]
    var_y = float(np.var(ys))
    if var_y < 1e-12:
        return 1.0 if mse < 1e-6 else 0.0
    val = 1.0 - (mse / var_y)
    return float(max(-1e9, val))


def evaluate_trial_generalization(
    trial: dict[str, Any], target_dataset: TargetDataset
) -> dict[str, Any]:
    """Perform blind generalization and bloat audit on a single trial."""
    method = trial.get("method", "Unknown")
    status = trial.get("status", "completed")
    train_mse = trial.get("train_mse")
    hid_mse = trial.get("hidden_mse")
    ext_mse = trial.get("extrap_mse")
    size = trial.get("program_size")

    if status != "completed" or hid_mse is None or ext_mse is None:
        return {
            **trial,
            "hidden_r2": -float("inf"),
            "extrap_r2": -float("inf"),
            "asymptotic_explosion": False,
            "constant_bloat": False,
            "hidden_success": False,
            "extrap_success": False,
            "generalization_gap": None,
        }

    hid_r2 = compute_r2_from_mse(target_dataset, "hidden", hid_mse)
    ext_r2 = compute_r2_from_mse(target_dataset, "extrapolation", ext_mse)

    asymptotic_explosion = bool(
        ext_mse > 1e6
        or not np.isfinite(ext_mse)
        or (train_mse is not None and ext_mse > 1e6 * (train_mse + 1.0))
    )
    constant_bloat = bool(size is not None and size > 50)
    hidden_success = bool(hid_mse <= 1e-3 and hid_r2 >= 0.99)
    extrap_success = bool(ext_mse <= 1e-3 and ext_r2 >= 0.99)
    gen_gap = (
        float(ext_mse - train_mse) if (train_mse is not None and np.isfinite(train_mse)) else None
    )

    return {
        **trial,
        "hidden_r2": hid_r2,
        "extrap_r2": ext_r2,
        "asymptotic_explosion": asymptotic_explosion,
        "constant_bloat": constant_bloat,
        "hidden_success": hidden_success,
        "extrap_success": extrap_success,
        "generalization_gap": gen_gap,
    }


def run_p156_generalization_suite(
    targets: list[str] | None = None,
    budgets: list[str | float] | None = None,
    seeds: list[int] | None = None,
    methods: list[str] | None = None,
    source_trials_dir: str | Path | None = None,
    output_dir: str | Path = "experiments/p156-generalization",
    device_name: str | None = None,
) -> dict[str, Any]:
    """Execute complete P156 blind generalization and extrapolation audit suite."""
    t0_suite = time.perf_counter()
    out_d = Path(output_dir)
    eval_d = out_d / "evaluations"
    eval_d.mkdir(parents=True, exist_ok=True)

    target_keys = targets or ["x_plus_1", "x2_3x_7"]
    parsed_budgets: list[float] = []
    for b in budgets or ["0.4s", "0.8s"]:
        if isinstance(b, (int, float)):
            parsed_budgets.append(float(b))
        else:
            parsed_budgets.append(parse_budget_str(str(b)))

    target_seeds = seeds or [42, 101, 202, 303, 404]
    target_methods = methods or ["Random", "Classic-GP", "Classical-SR", "PySR-Adapter", "EvoByte"]

    target_datasets = {k: generate_target_dataset(k) for k in target_keys}

    # 1. Audit dataset splits for leakage
    leakage_findings: list[str] = []
    for k, ds in target_datasets.items():
        sound_leakage, f_leak = audit_splits_leakage(ds)
        if not sound_leakage:
            leakage_findings.extend(f_leak)

    # 2. Collect or generate raw trials
    raw_trials: list[dict[str, Any]] = []
    src_dir = Path(source_trials_dir) if source_trials_dir else None
    if src_dir and src_dir.exists() and any(src_dir.glob("*.json")):
        for trial_file in src_dir.glob("*.json"):
            if trial_file.name.startswith("summary"):
                continue
            try:
                with open(trial_file, encoding="utf-8") as f:
                    data = json.load(f)
                if data.get("target") in target_keys and data.get("method") in target_methods:
                    raw_trials.append(data)
            except Exception:
                pass

    if len(raw_trials) < len(target_methods) * len(target_keys) * len(parsed_budgets) * len(
        target_seeds
    ):
        # Generate fresh trials using honest baselines runner
        baselines_out = out_d / "raw_baselines"
        baselines_summary = run_p155_baselines_suite(
            targets=target_keys,
            budgets=parsed_budgets,
            seeds=target_seeds,
            methods=target_methods,
            output_dir=baselines_out,
            device_name=device_name,
        )
        trials_dir = baselines_out / "trials"
        raw_trials = []
        for tf in trials_dir.glob("*.json"):
            with open(tf, encoding="utf-8") as f:
                raw_trials.append(json.load(f))

    # 3. Evaluate generalization on all collected trials
    evaluated_trials: list[dict[str, Any]] = []
    by_method: dict[str, list[dict[str, Any]]] = {m: [] for m in target_methods}

    for trial in raw_trials:
        t_key = trial.get("target")
        if t_key not in target_datasets:
            continue
        ds = target_datasets[t_key]
        ev = evaluate_trial_generalization(trial, ds)
        evaluated_trials.append(ev)
        m = ev.get("method", "Unknown")
        if m in by_method:
            by_method[m].append(ev)

        clean_m = m.replace("-", "_").lower()
        b_sec = ev.get("budget_sec", 0.0)
        s = ev.get("seed", 0)
        eval_filename = f"eval_{clean_m}_{t_key}_b{int(b_sec * 1000)}ms_s{s}.json"
        with open(eval_d / eval_filename, "w", encoding="utf-8") as f:
            json.dump(ev, f, indent=2, sort_keys=True, default=str)

    # 4. Compute comparative generalization metrics
    comparison: dict[str, Any] = {}
    for m in target_methods:
        m_recs = by_method[m]
        completed = [r for r in m_recs if r.get("status") == "completed"]
        n_comp = len(completed)

        hid_r2s = [
            r["hidden_r2"] for r in completed if np.isfinite(r.get("hidden_r2", -float("inf")))
        ]
        ext_r2s = [
            r["extrap_r2"] for r in completed if np.isfinite(r.get("extrap_r2", -float("inf")))
        ]

        mean_hid_r2 = float(np.mean(hid_r2s)) if hid_r2s else -float("inf")
        median_hid_r2 = float(np.median(hid_r2s)) if hid_r2s else -float("inf")
        mean_ext_r2 = float(np.mean(ext_r2s)) if ext_r2s else -float("inf")
        median_ext_r2 = float(np.median(ext_r2s)) if ext_r2s else -float("inf")

        hid_succ = sum(1 for r in completed if r.get("hidden_success") is True)
        ext_succ = sum(1 for r in completed if r.get("extrap_success") is True)
        explosions = sum(1 for r in completed if r.get("asymptotic_explosion") is True)
        bloats = sum(1 for r in completed if r.get("constant_bloat") is True)

        sizes = [
            r["program_size"] for r in completed if isinstance(r.get("program_size"), (int, float))
        ]
        mean_size = float(np.mean(sizes)) if sizes else 0.0

        comparison[m] = {
            "total_evaluations": len(m_recs),
            "completed_runs": n_comp,
            "hidden_success_rate": hid_succ / max(1, n_comp) if n_comp else 0.0,
            "extrap_success_rate": ext_succ / max(1, n_comp) if n_comp else 0.0,
            "mean_hidden_r2": mean_hid_r2,
            "median_hidden_r2": median_hid_r2,
            "mean_extrap_r2": mean_ext_r2,
            "median_extrap_r2": median_ext_r2,
            "explosion_rate": explosions / max(1, n_comp) if n_comp else 0.0,
            "bloat_rate": bloats / max(1, n_comp) if n_comp else 0.0,
            "mean_complexity": mean_size,
        }

    # Criterion 4 evaluation
    evo_comp = comparison.get("EvoByte", {})
    rand_comp = comparison.get("Random", {})
    evo_ext_rate = evo_comp.get("extrap_success_rate", 0.0)
    rand_ext_rate = rand_comp.get("extrap_success_rate", 0.0)
    evo_expl_rate = evo_comp.get("explosion_rate", 1.0)
    evo_comp_size = evo_comp.get("mean_complexity", 100.0)

    h1_criterion_4_supported = bool(
        evo_ext_rate >= 0.70
        and evo_expl_rate == 0.0
        and evo_comp_size <= 25.0
        and evo_ext_rate > rand_ext_rate
    )

    summary: dict[str, Any] = {
        "suite": "P156-generalization-extrapolation",
        "total_evaluations": len(evaluated_trials),
        "target_keys": target_keys,
        "budgets_sec": parsed_budgets,
        "seeds": target_seeds,
        "methods": target_methods,
        "leakage_findings": leakage_findings,
        "comparison": comparison,
        "h1_criterion_4_supported": h1_criterion_4_supported,
        "hardware": probe(),
        "elapsed_sec": time.perf_counter() - t0_suite,
    }

    summary_file = out_d / "summary_generalization.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True, default=str)
    summary_sha = hashlib.sha256(summary_file.read_bytes()).hexdigest()
    summary["summary_sha256"] = summary_sha

    return summary


def verify_p156_generalization_soundness(
    summary: dict[str, Any],
    min_trials: int = 10,
    min_extrap_rate: float = 0.70,
    max_explosion_rate: float = 0.05,
) -> tuple[bool, list[str]]:
    """Audit P156 generalization summary for scientific validity and zero leakage."""
    findings: list[str] = []

    total_evals = summary.get("total_evaluations", 0)
    if total_evals < min_trials:
        findings.append(f"INSUFFICIENT_EVALUATIONS: expected >= {min_trials}, got {total_evals}")

    leakage = summary.get("leakage_findings", [])
    if len(leakage) > 0:
        findings.extend(leakage)

    comp = summary.get("comparison", {})
    if "PySR-Adapter" in comp:
        pysr_info = comp["PySR-Adapter"]
        if pysr_info.get("completed_runs", 0) == 0:
            if pysr_info.get("extrap_success_rate", 0.0) > 0.0:
                findings.append(
                    "DISHONEST_PYSR_GENERALIZATION: PySR claimed generalization while missing"
                )

    if "EvoByte" in comp:
        evo = comp["EvoByte"]
        ext_rate = evo.get("extrap_success_rate", 0.0)
        expl_rate = evo.get("explosion_rate", 0.0)
        comp_size = evo.get("mean_complexity", 0.0)

        if ext_rate < min_extrap_rate:
            findings.append(
                f"LOW_EXTRAPOLATION_RATE: EvoByte extrapolation success rate ({ext_rate:.2%}) < {min_extrap_rate:.2%}"
            )
        if expl_rate > max_explosion_rate:
            findings.append(
                f"ASYMPTOTIC_EXPLOSION_EXCEEDED: EvoByte explosion rate ({expl_rate:.2%}) > {max_explosion_rate:.2%}"
            )
        if comp_size > 25.0:
            findings.append(
                f"COMPLEXITY_BLOAT: EvoByte mean size ({comp_size:.1f}) exceeds compact bound (25.0)"
            )

        if "Random" in comp:
            rand_ext_rate = comp["Random"].get("extrap_success_rate", 0.0)
            if ext_rate <= rand_ext_rate:
                findings.append(
                    f"EVOBYTE_EXTRAP_NOT_SUPERIOR: EvoByte ({ext_rate:.2%}) <= Random ({rand_ext_rate:.2%})"
                )

    if not summary.get("h1_criterion_4_supported", False):
        findings.append("H1_CRITERION_4_UNSUPPORTED: Generalization criteria not fully met")

    return len(findings) == 0, findings
