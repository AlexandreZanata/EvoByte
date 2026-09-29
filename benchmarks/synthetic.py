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
    h = hashlib.sha256(np.ascontiguousarray(xs).tobytes() + np.ascontiguousarray(ys).tobytes()).hexdigest()[:16]
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
        from evobyte.evolution import sample_pure, sample_structured
        from evobyte.bytecode import is_valid

        rng = np.random.default_rng(0)
        for name, fn in [("pure", sample_pure), ("structured", sample_structured)]:
            progs = [fn(rng) for _ in range(200)]
            rate = sum(is_valid(p) for p in progs) / len(progs)
            print(f"generator {name}: S0 pass rate={rate:.2f} (n=200, seed=0)")

    if args.cascade:
        from evobyte.bytecode import encode_instr, nop_program
        from evobyte.verifier import cascade_evaluate

        bad = nop_program()
        bad[0] = encode_instr(0x05, dst=7, a=0, b=0)
        out = cascade_evaluate(bad, xs, ys, elite_err=1e-6)
        print(f"cascade demo: killed={out['killed']} stage={out['stage']} mse={out['mse']:.4g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
