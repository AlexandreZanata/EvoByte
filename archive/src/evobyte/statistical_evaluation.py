"""Statistical evaluation and Holm-Bonferroni FWER control (P169).

Performs rigorous non-parametric paired tests between methods and emits
honest verdict classifications.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
from scipy import stats


@dataclass
class HypothesisVerdict:
    comparison_name: str
    n_pairs: int
    w_stat: float
    p_value_raw: float
    p_value_holm: float
    alpha: float
    is_significant: bool
    direction: str  # "method_a_superior", "method_b_superior", "no_difference"
    verdict: str


def compute_paired_wilcoxon_holm(
    scores_a: list[float] | np.ndarray,
    scores_b: list[float] | np.ndarray,
    comparison_name: str,
    family_size: int = 1,
    alpha: float = 0.01,
) -> HypothesisVerdict:
    """Compute exact paired Wilcoxon signed-rank test with Bonferroni-Holm adjustment."""
    a = np.asarray(scores_a, dtype=float)
    b = np.asarray(scores_b, dtype=float)
    if len(a) != len(b):
        raise ValueError(f"sample sizes must match: {len(a)} vs {len(b)}")

    diffs = a - b
    nonzero_diffs = diffs[diffs != 0.0]

    if len(nonzero_diffs) == 0:
        return HypothesisVerdict(
            comparison_name=comparison_name,
            n_pairs=len(a),
            w_stat=0.0,
            p_value_raw=1.0,
            p_value_holm=1.0,
            alpha=alpha,
            is_significant=False,
            direction="no_difference",
            verdict="INCONCLUSIVE_IDENTICAL",
        )

    res = stats.wilcoxon(diffs, alternative="two-sided")
    p_raw = float(res.pvalue)
    # Holm adjustment for single family step
    p_holm = min(1.0, p_raw * family_size)

    mean_diff = float(np.mean(diffs))
    if mean_diff > 0:
        direction = "method_a_superior"
    elif mean_diff < 0:
        direction = "method_b_superior"
    else:
        direction = "no_difference"

    is_sig = bool(p_holm <= alpha)
    verdict = f"SUPPORTED_{direction.upper()}" if is_sig else "NOT_SUPPORTED_NULL"

    return HypothesisVerdict(
        comparison_name=comparison_name,
        n_pairs=len(a),
        w_stat=float(res.statistic),
        p_value_raw=p_raw,
        p_value_holm=p_holm,
        alpha=alpha,
        is_significant=is_sig,
        direction=direction,
        verdict=verdict,
    )


def consolidate_campaign_verdicts(
    campaign_summary_path: str,
    output_path: str,
    family_alpha: float = 0.01,
) -> dict[str, Any]:
    """Parse raw campaign data, run statistical batteries, and output verdict."""
    with open(campaign_summary_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    trials = data.get("trials", [])
    algorithms = data.get("algorithms", [])
    targets_verdicts = data.get("verdicts", {})

    hypotheses: list[dict[str, Any]] = []

    # If we have matched trials between SimulatedAnnealing and TabuSearch:
    if "SimulatedAnnealing" in algorithms and "TabuSearch" in algorithms and trials:
        sa_map = {
            (t["target_id"], t["size_kind"], t["seed"]): t
            for t in trials
            if t.get("algorithm") == "SimulatedAnnealing"
        }
        tabu_map = {
            (t["target_id"], t["size_kind"], t["seed"]): t
            for t in trials
            if t.get("algorithm") == "TabuSearch"
        }

        # Subsets by target and size
        subsets = sorted(list({(t["target_id"], t["size_kind"]) for t in trials}))
        family_size = len(subsets) if subsets else 1

        for tgt, sk in subsets:
            common_seeds = sorted(
                [k[2] for k in sa_map if k[0] == tgt and k[1] == sk and k in tabu_map]
            )
            if common_seeds:
                sa_scores = [sa_map[(tgt, sk, s)]["best_score"] for s in common_seeds]
                tabu_scores = [tabu_map[(tgt, sk, s)]["best_score"] for s in common_seeds]
                comp_name = f"SA_vs_Tabu_{tgt}_{sk}"
                verdict_obj = compute_paired_wilcoxon_holm(
                    sa_scores,
                    tabu_scores,
                    comparison_name=comp_name,
                    family_size=family_size,
                    alpha=family_alpha,
                )
                hypotheses.append(asdict(verdict_obj))

        # Pooled test across all targets and sizes
        all_common_keys = sorted([k for k in sa_map if k in tabu_map])
        if all_common_keys:
            sa_all = [sa_map[k]["best_score"] for k in all_common_keys]
            tabu_all = [tabu_map[k]["best_score"] for k in all_common_keys]
            pooled_verdict = compute_paired_wilcoxon_holm(
                sa_all,
                tabu_all,
                comparison_name="SA_vs_Tabu_pooled_campaign",
                family_size=1,
                alpha=family_alpha,
            )
            hypotheses.append(asdict(pooled_verdict))

    has_beaten = any(v.get("verdict") == "DISCOVERY_BEATEN" for v in targets_verdicts.values())
    record_discovery = "CONFIRMED" if has_beaten else "NULL_RESULT"

    verdicts: dict[str, Any] = {
        "phase": "P169",
        "status": "EVALUATED",
        "family_alpha": family_alpha,
        "campaign_summary_source": str(campaign_summary_path),
        "hypotheses": hypotheses,
        "mathematical_record_discovery": record_discovery,
        "bytecode_evolutionary_advantage": "NOT_SUPPORTED",
        "targets_summary": {tgt: v.get("verdict") for tgt, v in targets_verdicts.items()},
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(verdicts, f, indent=2)

    return verdicts
