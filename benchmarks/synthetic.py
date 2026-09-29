"""Synthetic dataset generator + smoke/bench harness (P00 scope)."""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np


def gen_dataset(formula: str, n: int, lo: float, hi: float, seed: int):
    rng = np.random.default_rng(seed)
    xs = rng.uniform(lo, hi, size=(n,)).astype(np.float32)
    if formula == "x2_3x_7":
        ys = (xs * xs + 3 * xs + 7).astype(np.float32)
    elif formula == "sin_x2":
        ys = (np.sin(xs) + xs * xs).astype(np.float32)
    elif formula == "x_plus_1":
        ys = (xs + 1).astype(np.float32)
    else:
        raise ValueError(f"unknown formula: {formula}")
    h = hashlib.sha256(
        np.ascontiguousarray(xs).tobytes() + np.ascontiguousarray(ys).tobytes()
    ).hexdigest()[:16]
    return xs, ys, h


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--benchmark", action="store_true")
    ap.add_argument("--generators", action="store_true")
    ap.add_argument("--cascade", action="store_true")
    args = ap.parse_args()

    if args.smoke or args.benchmark or args.generators or args.cascade:
        xs, ys, h = gen_dataset("x2_3x_7", 256, -10.0, 10.0, seed=0)
        assert xs.shape == (256,) and np.all(np.isfinite(ys))
        print(f"smoke ok: n=256 formula=x^2+3x+7 seed=0 hash={h}")

    if args.generators:
        import time

        from evobyte.bytecode import is_valid
        from evobyte.evolution import sample_pure, sample_structured

        seed = 0
        n_samples = 5000
        rng = np.random.default_rng(seed)

        print(
            f"\nGenerator Benchmark (P03): Pure (A) vs Structured (B) [seed={seed}, n={n_samples}]"
        )
        print("-" * 75)
        print(
            f"{'Generator':<18} | {'Throughput (gen/s)':<20} | {'S0 Pass Rate':<12} | {'Valid / Total'}"
        )
        print("-" * 75)

        for name, label, fn in [
            ("pure", "Pure (A)", sample_pure),
            ("structured", "Structured (B)", sample_structured),
        ]:
            t0 = time.perf_counter()
            progs = [fn(rng) for _ in range(n_samples)]
            dt = time.perf_counter() - t0
            throughput = n_samples / dt if dt > 0 else float("inf")
            valid_count = sum(is_valid(p) for p in progs)
            rate = valid_count / len(progs)
            print(
                f"{label:<18} | {throughput:>18.1f} | {rate:>10.2%} | {valid_count} / {n_samples}"
            )
            print(
                f"generator {name}: S0 pass rate={rate:.2f} ({throughput:.1f} gen/s, n={n_samples}, seed={seed})"
            )
        print("-" * 75)

    if args.cascade:
        from evobyte.bytecode import encode_instr, nop_program
        from evobyte.evolution import sample_pure, sample_structured
        from evobyte.verifier import cascade_evaluate, cascade_evaluate_population

        # Demo single bad program
        bad = nop_program()
        bad[0] = encode_instr(0x05, dst=7, a=0, b=0)
        out = cascade_evaluate(bad, xs, ys, elite_err=1e-6)
        print(f"cascade demo: killed={out['killed']} stage={out['stage']} mse={out['mse']:.4g}")

        # Cascade population benchmark (200 candidates)
        rng = np.random.default_rng(0)
        # Exact elite program
        p_elite = nop_program()
        p_elite[0] = encode_instr(0x0F, dst=3, a=1, b=11)  # r3 = 3.0
        p_elite[1] = encode_instr(0x03, dst=3, a=3, b=0)  # r3 = 3x
        p_elite[2] = encode_instr(0x03, dst=2, a=0, b=0)  # r2 = x^2
        p_elite[3] = encode_instr(0x01, dst=4, a=2, b=3)  # r4 = x^2 + 3x
        p_elite[4] = encode_instr(0x0F, dst=7, a=4, b=10)  # r7 = x^2 + 3x + 7

        pop = []
        # 50 pure random (mostly S0 invalid)
        pop.extend([sample_pure(rng) for _ in range(50)])
        # 140 structured random (S0 valid, mostly killed in S1/S2)
        pop.extend([sample_structured(rng) for _ in range(140)])
        # 10 elite instances
        pop.extend([p_elite.copy() for _ in range(10)])

        xs_casc, ys_casc, _ = gen_dataset("x2_3x_7", 1024, -10.0, 10.0, seed=0)
        stats = cascade_evaluate_population(pop, xs_casc, ys_casc, elite_err=1e-6, k=4.0)

        stage_points = {0: "0 (validity)", 1: "32 pts", 2: "256 pts", 3: "1024 pts (S3)"}
        print(f"\nCascade Benchmark (P04): Population Evaluation [n={stats['total']}, seed=0]")
        print("-" * 75)
        print(
            f"{'Stage':<18} | {'Points':<14} | {'Candidates':<11} | {'Killed':<8} | {'Survivors'}"
        )
        print("-" * 75)
        for s in range(4):
            candidates = stats["stage_survivors"][s]
            killed = stats["stage_kills"][s]
            survivors = max(0, candidates - killed)
            kill_pct = (killed / candidates * 100) if candidates else 0.0
            print(
                f"Stage {s:<12} | {stage_points[s]:<14} | {candidates:<11} | {killed:<4} ({kill_pct:>5.1f}%) | {survivors}"
            )
        print("-" * 75)
        print(
            f"Final Survivors (S3): {stats['survivors']} / {stats['total']} ({stats['survival_rate']:.1%})\n"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
