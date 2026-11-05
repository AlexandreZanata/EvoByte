"""Consolidated statistical verdicts for frontier campaigns (P178)."""

from __future__ import annotations

import datetime
import hashlib
import json
from pathlib import Path
from typing import Any

from scipy import stats


def paired_wilcoxon_holm(
    scores_a: list[float],
    scores_b: list[float],
    comparison_name: str,
    family_size: int = 1,
    alpha: float = 0.01,
) -> dict[str, Any]:
    """Two-sided paired Wilcoxon + conservative single-step Bonferroni-Holm.

    Pairing is strict by position (caller aligns by target/size/seed); samples
    of different sizes raise ValueError. p_holm = min(1, p_raw * family_size)
    (single-step, conservative; documented, not step-down Holm).
    All-zero differences short-circuit to p_raw == 1.0 (scipy is undefined
    there). Direction follows the mean of (a - b).
    """
    a = [float(x) for x in scores_a]
    b = [float(x) for x in scores_b]
    if len(a) != len(b):
        raise ValueError(f"paired samples differ in size: {len(a)} != {len(b)} ({comparison_name})")
    if len(a) == 0:
        raise ValueError(f"empty paired samples ({comparison_name})")
    m = max(1, int(family_size))
    diffs = [x - y for x, y in zip(a, b)]
    mean_diff = sum(diffs) / len(diffs)
    if all(d == 0.0 for d in diffs):
        p_raw = 1.0
        w = 0.0
        direction = "no_difference"
    else:
        res = stats.wilcoxon(a, b, alternative="two-sided")
        w = float(res.statistic)
        p_raw = float(res.pvalue)
        direction = (
            "a_greater" if mean_diff > 0 else ("b_greater" if mean_diff < 0 else "no_difference")
        )
    p_holm = min(1.0, p_raw * m)
    if direction == "no_difference":
        verdict = "INCONCLUSIVE_IDENTICAL"
    elif p_holm <= float(alpha):
        verdict = "SUPPORTED_A_GREATER" if direction == "a_greater" else "SUPPORTED_B_GREATER"
    else:
        verdict = "NOT_SUPPORTED_NULL"
    return {
        "comparison": comparison_name,
        "n": len(a),
        "W": w,
        "p_raw": p_raw,
        "p_holm": p_holm,
        "family_size": m,
        "alpha": float(alpha),
        "direction": direction,
        "verdict": verdict,
        "is_significant": bool(p_holm <= float(alpha)) and direction != "no_difference",
    }


def _trial_pairs(
    results: dict, algo_a: str, algo_b: str, mode: str | None = None
) -> dict[tuple, tuple[list[float], list[float]]]:
    """Group paired scores by (target_id, attempt_size): {key: (scores_a, scores_b)}.

    Pairs align by seed; trials missing on either side are dropped pair-wise.
    Lower scores are better (uncovered counts / violation counts).
    """
    by_key: dict[tuple, dict[int, dict[str, float]]] = {}
    for tr in results.get("trials", []):
        if mode is not None and tr.get("mode", "free") != mode:
            continue
        if tr.get("algorithm") not in (algo_a, algo_b):
            continue
        metric = tr.get("best_uncovered", tr.get("best_violations"))
        if metric is None:
            continue
        key = (tr.get("target_id"), tr.get("attempt_size"))
        by_key.setdefault(key, {}).setdefault(int(tr.get("seed")), {})[tr["algorithm"]] = float(
            metric
        )
    out: dict[tuple, tuple[list[float], list[float]]] = {}
    for key, per_seed in by_key.items():
        sa = [v[algo_a] for _, v in sorted(per_seed.items()) if algo_a in v and algo_b in v]
        sb = [v[algo_b] for _, v in sorted(per_seed.items()) if algo_a in v and algo_b in v]
        if sa:
            out[key] = (sa, sb)
    return out


def consolidate_frontier_verdicts(
    p176_path: str | Path, p177_path: str | Path, output_path: str | Path, alpha: float = 0.01
) -> dict[str, Any]:
    """Consolidate P176/P177 campaign results into a preregistered verdict.

    Battery: one SA-vs-HillClimbing paired test per (campaign, target, size
    [and mode for P177]), seeds strictly paired. One pooled (grouped) test
    per campaign, family_size = 1, labeled exploratory (units differ across
    campaigns, so no cross-campaign pooling). Family-wise correction is
    single-step (conservative) over the battery.
    """
    p176 = json.loads(Path(p176_path).read_text(encoding="utf-8"))
    p177 = json.loads(Path(p177_path).read_text(encoding="utf-8"))

    batteries: list[tuple[str, dict[tuple, tuple[list[float], list[float]]]]] = []
    batteries.append(("P176", _trial_pairs(p176, "SimulatedAnnealing", "HillClimbing")))
    for mode in ("free", "symmetric_p3"):
        batteries.append(
            (f"P177/{mode}", _trial_pairs(p177, "SimulatedAnnealing", "HillClimbing", mode=mode))
        )

    n_battery = sum(len(pairs) for _, pairs in batteries)
    family_size = max(1, n_battery)
    hypotheses: list[dict[str, Any]] = []
    for scope, pairs in batteries:
        for (target_id, attempt), (sa, hc) in sorted(pairs.items(), key=lambda kv: str(kv[0])):
            hypotheses.append(
                paired_wilcoxon_holm(
                    sa,
                    hc,
                    f"{scope}:{target_id}|B{attempt}|SA-vs-HC",
                    family_size=family_size,
                    alpha=alpha,
                )
            )

    grouped: list[dict[str, Any]] = []
    for scope, pairs in batteries:
        all_a: list[float] = []
        all_b: list[float] = []
        for _, (sa, hc) in pairs.items():
            all_a.extend(sa)
            all_b.extend(hc)
        if all_a:
            g = paired_wilcoxon_holm(
                all_a,
                all_b,
                f"{scope}:grouped:SA-vs-HC:exploratory",
                family_size=1,
                alpha=alpha,
            )
            g["exploratory"] = True
            grouped.append(g)

    discoveries: list[dict[str, Any]] = []
    for res in (p176, p177):
        for e in res.get("targets", []):
            if e.get("verdict") == "DISCOVERY_BEATEN" and e.get("certificate"):
                discoveries.append(
                    {"target_id": e.get("target_id"), "certificate": e["certificate"]}
                )
    mathematical_record_discovery = "CONFIRMED" if discoveries else "NULL_RESULT"

    targets_summary = []
    for res, phase in ((p176, "P176"), (p177, "P177")):
        for e in res.get("targets", []):
            targets_summary.append(
                {"phase": phase, "target_id": e.get("target_id"), "verdict": e.get("verdict")}
            )

    payload = {
        "status": "COMPLETE",
        "alpha": float(alpha),
        "family_size_battery": family_size,
        "correction": "single-step Bonferroni (conservative; documented, not step-down Holm)",
        "n_hypotheses_battery": len(hypotheses),
        "hypotheses": hypotheses,
        "grouped_exploratory": grouped,
        "mathematical_record_discovery": mathematical_record_discovery,
        "discoveries": discoveries,
        "targets_summary": targets_summary,
        "custody": {
            "p176_results_sha256": hashlib.sha256(Path(p176_path).read_bytes()).hexdigest(),
            "p177_results_sha256": hashlib.sha256(Path(p177_path).read_bytes()).hexdigest(),
        },
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    payload["custody"]["output_sha256"] = hashlib.sha256(out_p.read_bytes()).hexdigest()
    return payload
