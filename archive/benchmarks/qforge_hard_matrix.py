"""Hard-System Matrix Benchmark across scaling verifier ladder (spec: Q13, docs/quantum/VERIFIER.md).

Executes pre-registered quantum systems (larger N at the exact-verification bottleneck,
J1-J2 frustrated chains, critical Ising, Heisenberg) across scaling verifier tiers
(sparse CSR Lanczos, symmetry-reduced subspace diagonalization).
Mandatory negative-result reporting: outcomes are classified into SUPPORTED, NULL,
and NEEDS_WORK, ensuring unproven claims fail and null results uphold scientific integrity.
"""

from __future__ import annotations

import argparse
import datetime
import math
import subprocess
import sys
import time
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "benchmarks"))

from hw_probe import probe

from evobyte.quantum.scaling import (
    PREREGISTERED_TARGETS,
    OutcomeClass,
    TargetEvaluationResult,
    run_hard_target_search,
)


def get_git_commit() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=5, check=False
        )
        if out.returncode == 0:
            return out.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return "unknown"
    return "unknown"


def report_passes(results: list[TargetEvaluationResult]) -> bool:
    """Check report consistency; this is not a scientific discovery acceptance gate."""
    if not results:
        return False
    for result in results:
        target = PREREGISTERED_TARGETS.get(result.target_id)
        if target is None or result.outcome == OutcomeClass.NEEDS_WORK:
            return False
        if not all(
            math.isfinite(value)
            for value in (
                result.discovered_energy,
                result.reference_energy,
                result.energy_error,
                result.wall_clock_sec,
            )
        ):
            return False
        if not (0 < result.evaluations <= target.max_evaluations) or result.wall_clock_sec <= 0:
            return False
        if result.energy_error < 0:
            return False
        if result.fidelity is not None and (
            not math.isfinite(result.fidelity) or not 0 <= result.fidelity <= 1.0 + 1e-12
        ):
            return False
        if not math.isclose(
            result.energy_error,
            abs(result.discovered_energy - result.reference_energy),
            rel_tol=1e-9,
            abs_tol=1e-12,
        ):
            return False
        fidelity_ok = target.fidelity_threshold <= 0 or (
            result.fidelity is not None
            and math.isfinite(result.fidelity)
            and target.fidelity_threshold <= result.fidelity <= 1.0 + 1e-12
        )
        meets_thresholds = result.energy_error <= target.energy_tolerance and fidelity_ok
        budget_exhausted = (
            result.evaluations >= target.max_evaluations
            or result.wall_clock_sec >= target.wall_clock_timeout_sec
        )
        if result.outcome == OutcomeClass.SUPPORTED:
            if not meets_thresholds:
                return False
        elif result.outcome == OutcomeClass.NULL:
            if meets_thresholds or not budget_exhausted:
                return False
        else:
            return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Q-Forge Hard-System Matrix Benchmark (Q13)")
    parser.add_argument(
        "--preregistered-only",
        action="store_true",
        default=True,
        help="Run all pre-registered hard targets exclusively",
    )
    parser.add_argument(
        "--targets",
        type=str,
        default="",
        help="Comma-separated target IDs (default: all pre-registered targets)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for search reproducibility",
    )
    args = parser.parse_args()

    hw_info = probe()
    git_hash = get_git_commit()
    timestamp = datetime.datetime.now(datetime.UTC).isoformat()

    if args.targets:
        target_keys = [t.strip() for t in args.targets.split(",") if t.strip()]
    else:
        target_keys = list(PREREGISTERED_TARGETS.keys())

    print("=" * 135)
    print("Q-FORGE HARD-SYSTEM MATRIX BENCHMARK (SCALING VERIFIERS & PRE-REGISTERED TARGETS)")
    print("=" * 135)
    print(f"  Timestamp            : {timestamp}")
    print(f"  Git Commit           : {git_hash}")
    print(f"  CPU                  : {hw_info.get('cpu', 'unknown')}")
    print(f"  OS                   : {hw_info.get('os', 'unknown')}")
    print(f"  Pre-registered Targets: {', '.join(target_keys)}")
    print(f"  Random Seed          : {args.seed}")
    print("-" * 135)
    print(
        f"{'Target ID':<23} | {'Model':<10} | {'N':<3} | {'Dim':<6} | {'Outcome':<10} | "
        f"{'Evals':<6} | {'Time (s)':<8} | {'E_found':<10} | {'E_ref':<10} | {'Delta E':<10} | "
        f"{'Fidelity':<8} | {'Verifier Tier'}"
    )
    print("-" * 135)

    results: list[TargetEvaluationResult] = []
    t_start = time.perf_counter()

    for tid in target_keys:
        if tid not in PREREGISTERED_TARGETS:
            print(f"ERROR: Target '{tid}' is not in pre-registered catalog!")
            return 1

        target = PREREGISTERED_TARGETS[tid]
        res = run_hard_target_search(target, seed=args.seed)
        results.append(res)

        fid_str = f"{res.fidelity:<8.4f}" if res.fidelity is not None else "N/A     "
        outcome_color = res.outcome.value

        print(
            f"{res.target_id:<23} | {res.model:<10} | {res.n_qubits:<3} | {res.hilbert_dim:<6} | {outcome_color:<10} | "
            f"{res.evaluations:<6} | {res.wall_clock_sec:<8.4f} | {res.discovered_energy:<10.4f} | "
            f"{res.reference_energy:<10.4f} | {res.energy_error:<10.2e} | {fid_str} | {res.verifier_tier.value}"
        )

    t_total = time.perf_counter() - t_start
    print("-" * 135)

    # Outcome Summary & Negative Result Integrity Audit
    supported_count = sum(1 for r in results if r.outcome == OutcomeClass.SUPPORTED)
    null_count = sum(1 for r in results if r.outcome == OutcomeClass.NULL)
    needs_work_count = sum(1 for r in results if r.outcome == OutcomeClass.NEEDS_WORK)

    print("\nPre-Registered Target Outcomes:")
    print(f"  SUPPORTED  : {supported_count} / {len(results)}")
    print(f"  NULL       : {null_count} / {len(results)} (mandatory negative results upheld)")
    print(f"  NEEDS_WORK : {needs_work_count} / {len(results)}")
    print(f"  Total Time : {t_total:.2f} s")

    print("\nReproduction Bundles:")
    for r in results:
        print(f"  [{r.outcome.value:<9}] {r.target_id}: {r.reproduction_cmd}")

    passed = report_passes(results)

    print("\n" + "=" * 135)
    print(f"EXIT GATE VERDICT: {'PASS' if passed else 'FAIL'} (report consistency only)")
    print("RESEARCH ACCEPTANCE: PROVISIONAL; known seeds and reference-based stopping are used")
    print("=" * 135)

    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
