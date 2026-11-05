"""Calibration benchmark for frontier combinatorial baselines (P172)."""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
import sys
import time

import numpy as np

from evobyte.frontier_baselines import run_simulated_annealing
from evobyte.frontier_catalogue import verify_covering_design, verify_weak_schur_partition
from evobyte.target_catalogue import verify_schur_partition

HARD_BUDGET_SEC = 3.0
TARGETS_DIR = Path(__file__).resolve().parent.parent / "docs" / "research" / "targets"
CERT_DIR = TARGETS_DIR / "certificates"


def run_verifier_gates() -> None:
    """Step 1: Check verifier fixtures for Fano, AG(2,3), S(3,4,8), and WS(2)."""
    # Fano plane: 7 blocks cover (7,3,2); every single block removal fails
    fano = [(1, 2, 3), (1, 4, 5), (1, 6, 7), (2, 4, 6), (2, 5, 7), (3, 4, 7), (3, 5, 6)]
    ok, msg = verify_covering_design(fano, 7, 3, 2)
    if not ok:
        raise RuntimeError(f"Fano failed covering check: {msg}")

    for i in range(len(fano)):
        sub = fano[:i] + fano[i + 1 :]
        ok_sub, _ = verify_covering_design(sub, 7, 3, 2)
        if ok_sub:
            raise RuntimeError(f"Fano sub-design without block {i} unexpectedly passed!")

    # AG(2,3): 12 lines in F3^2
    ag23_cert = json.loads((CERT_DIR / "covering_C_9_3_2.json").read_text())["blocks"]
    ag23 = [tuple(b) for b in ag23_cert]
    ok_ag, msg_ag = verify_covering_design(ag23, 9, 3, 2)
    if not ok_ag:
        raise RuntimeError(f"AG(2,3) failed covering check: {msg_ag}")
    if verify_covering_design(ag23[:-1], 9, 3, 2)[0]:
        raise RuntimeError("AG(2,3) with 1 removed block unexpectedly passed!")

    # S(3,4,8): 14 planes in F2^3
    s348_cert = json.loads((CERT_DIR / "covering_C_8_4_3.json").read_text())["blocks"]
    s348 = [tuple(b) for b in s348_cert]
    ok_s, msg_s = verify_covering_design(s348, 8, 4, 3)
    if not ok_s:
        raise RuntimeError(f"S(3,4,8) failed covering check: {msg_s}")
    if verify_covering_design(s348[:-1], 8, 4, 3)[0]:
        raise RuntimeError("S(3,4,8) with 1 removed block unexpectedly passed!")

    # WS(2) fixture: valid for weak Schur, invalid for strong Schur
    ws2_fixture = [1, 1, 2, 1, 2, 2, 2, 1]
    ok_ws, msg_ws = verify_weak_schur_partition(ws2_fixture, 2)
    if not ok_ws:
        raise RuntimeError(f"WS(2) fixture rejected by weak Schur verifier: {msg_ws}")

    ok_strong, _ = verify_schur_partition(ws2_fixture, 2)
    if ok_strong:
        raise RuntimeError("WS(2) fixture unexpectedly accepted by strong Schur verifier!")


def run_ws2_search(seed: int = 171, max_seconds: float = 2.0) -> dict:
    """Step 2: WS(2) search by Simulated Annealing from random partition."""

    def init_ws(rng: np.random.Generator) -> tuple[int, ...]:
        return tuple(int(rng.integers(1, 3)) for _ in range(8))

    def neighbor_ws(cand: tuple[int, ...], rng: np.random.Generator) -> tuple[int, ...]:
        idx = int(rng.integers(0, 8))
        cl = list(cand)
        cl[idx] = 3 - cl[idx]
        return tuple(cl)

    def eval_ws(cand: tuple[int, ...]) -> tuple[float, bool]:
        v = 0
        for a in range(1, 8):
            for b in range(a + 1, 9):
                c = a + b
                if c <= 8 and cand[a - 1] == cand[b - 1] == cand[c - 1]:
                    v += 1
        return -float(v), (v == 0)

    res = run_simulated_annealing(
        "WS(2)",
        init_ws,
        neighbor_ws,
        eval_ws,
        max_seconds=max_seconds,
        seed=seed,
    )
    is_valid = bool(res.is_solution and verify_weak_schur_partition(list(res.best_candidate), 2)[0])
    return {
        "hit": is_valid,
        "elapsed_sec": res.elapsed_sec,
        "evaluations": res.evaluations,
        "best_score": res.best_score,
        "best_candidate": list(res.best_candidate) if res.best_candidate else None,
    }


def run_c732_search(seed: int = 171, max_seconds: float = 2.0) -> dict:
    """Step 3: C(7,3,2) search by greedy construction + SA with swaps and restarts."""
    all_triples = list(itertools.combinations(range(1, 8), 3))
    all_pairs = list(itertools.combinations(range(1, 8), 2))

    def init_cov(rng: np.random.Generator) -> tuple[tuple[int, ...], ...]:
        uncovered = set(all_pairs)
        chosen = []
        pool = list(all_triples)
        for _ in range(7):
            scores = [
                sum(1 for p in itertools.combinations(tr, 2) if p in uncovered) for tr in pool
            ]
            max_s = max(scores)
            cands = [pool[i] for i, s in enumerate(scores) if s == max_s]
            pick = cands[rng.integers(0, len(cands))]
            chosen.append(pick)
            pool.remove(pick)
            for p in itertools.combinations(pick, 2):
                uncovered.discard(p)
        return tuple(sorted(chosen))

    def neighbor_cov(
        cand: tuple[tuple[int, ...], ...], rng: np.random.Generator
    ) -> tuple[tuple[int, ...], ...]:
        bl = list(cand)
        idx = int(rng.integers(0, len(bl)))
        rem = [tr for tr in all_triples if tr not in bl]
        new_tr = rem[rng.integers(0, len(rem))]
        bl[idx] = new_tr
        return tuple(sorted(bl))

    def eval_cov(cand: tuple[tuple[int, ...], ...]) -> tuple[float, bool]:
        cov = set()
        for b in cand:
            cov.update(itertools.combinations(b, 2))
        return float(len(cov)), (len(cov) == 21)

    res = run_simulated_annealing(
        "C(7,3,2)",
        init_cov,
        neighbor_cov,
        eval_cov,
        max_seconds=max_seconds,
        seed=seed,
    )
    is_valid = bool(res.is_solution and verify_covering_design(res.best_candidate, 7, 3, 2)[0])
    return {
        "hit": is_valid,
        "elapsed_sec": res.elapsed_sec,
        "evaluations": res.evaluations,
        "best_score": res.best_score,
        "best_candidate": [list(b) for b in res.best_candidate] if res.best_candidate else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Frontier Baseline Calibration (P172)")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("experiments/p172-calibration.json"),
        help="Output path for calibration JSON",
    )
    args = parser.parse_args()

    t_bench_start = time.perf_counter()

    # Step 1: Verifier gates
    run_verifier_gates()

    # Step 2: WS(2) search
    ws_result = run_ws2_search(seed=171, max_seconds=2.0)
    if not ws_result["hit"]:
        print("STOP: WS(2) baseline failed to find solution in budget!", file=sys.stderr)
        return 1

    # Step 3: C(7,3,2) search
    cov_result = run_c732_search(seed=171, max_seconds=2.0)
    if not cov_result["hit"]:
        print("STOP: C(7,3,2) baseline failed to find solution in budget!", file=sys.stderr)
        return 1

    total_elapsed = time.perf_counter() - t_bench_start
    if total_elapsed > HARD_BUDGET_SEC:
        print(
            f"STOP: Calibration exceeded hard budget of {HARD_BUDGET_SEC}s (took {total_elapsed:.3f}s)",
            file=sys.stderr,
        )
        return 1

    output_data = {
        "verifier_gates": "all_pass",
        "hits": {
            "WS(2)": ws_result,
            "C(7,3,2)": cov_result,
        },
        "seeds": {
            "WS(2)": 171,
            "C(7,3,2)": 171,
        },
        "elapsed_sec": round(total_elapsed, 6),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output_data, indent=2))
    print(f"Calibration passed in {total_elapsed:.4f}s. Report saved to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
