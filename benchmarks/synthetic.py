"""Synthetic dataset generator + smoke/bench harness (P00 scope)."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np
import torch

from evobyte.archive import EliteArchive, write_hall_of_fame_entry
from evobyte.bytecode import CONST_BANK, encode_instr, nop_program
from evobyte.verifier import reproduce_candidate, verify_l2


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


def run_strict_verification(seeds: int = 5, output_path: str | None = None) -> dict:
    print("\n================================================================================")
    print(f"Level-2 Strict Verification & Discovery Evidence (P19 Scope) [seeds={seeds}]")
    print("================================================================================\n")

    per_seed_results = []
    all_known_correct_passed = True
    all_overfits_rejected = True
    all_exploits_rejected = True
    all_rounding_rejected = True
    all_reproduced = True
    all_archive_null_ok = True
    all_hof_strict_ok = True

    for s in range(seeds):
        rng = np.random.default_rng(s * 1000 + 42)
        # Disjoint in-domain splits on [-10, 10]
        # Train: 256 points
        train_xs = rng.uniform(-10.0, 10.0, size=(256,)).astype(np.float64)
        train_ys = train_xs**2 + 3.0 * train_xs + 7.0

        # Val: 128 points
        val_xs = rng.uniform(-10.0, 10.0, size=(128,)).astype(np.float64)
        val_ys = val_xs**2 + 3.0 * val_xs + 7.0

        # Hidden test: 256 held-out points (never seen by search)
        test_xs = rng.uniform(-10.0, 10.0, size=(256,)).astype(np.float64)
        test_ys = test_xs**2 + 3.0 * test_xs + 7.0

        # Extrapolation on both domain sides: [-50, -10) and (10, 50]
        extrap_left = rng.uniform(-50.0, -10.0, size=(128,)).astype(np.float64)
        extrap_right = rng.uniform(10.0, 50.0, size=(128,)).astype(np.float64)
        extrap_xs = np.concatenate([extrap_left, extrap_right])
        extrap_ys = extrap_xs**2 + 3.0 * extrap_xs + 7.0

        # Adversarial points near boundaries and singularities
        adv_xs = np.array(
            [-10.0, -9.99999, -5.0, -1e-6, -1e-12, 0.0, 1e-12, 1e-6, 5.0, 9.99999, 10.0],
            dtype=np.float64,
        )

        # Audit Hashes
        h_train = hashlib.sha256(train_xs.tobytes() + train_ys.tobytes()).hexdigest()[:16]
        h_val = hashlib.sha256(val_xs.tobytes() + val_ys.tobytes()).hexdigest()[:16]
        h_test = hashlib.sha256(test_xs.tobytes() + test_ys.tobytes()).hexdigest()[:16]
        h_extrap = hashlib.sha256(extrap_xs.tobytes() + extrap_ys.tobytes()).hexdigest()[:16]

        audit_entry = {
            "seed": s,
            "train_hash": h_train,
            "val_hash": h_val,
            "hidden_test_hash": h_test,
            "extrapolation_hash": h_extrap,
            "search_data_accessed": ["train", "val"],
            "hidden_test_accessed_during_search": False,
        }

        # 1. Known-Correct Program (y = x^2 + 3x + 7)
        p_exact = nop_program()
        p_exact[0] = encode_instr(0x0F, dst=3, a=1, b=11)  # r3 = 3.0
        p_exact[1] = encode_instr(0x03, dst=3, a=3, b=0)  # r3 = 3x
        p_exact[2] = encode_instr(0x03, dst=2, a=0, b=0)  # r2 = x^2
        p_exact[3] = encode_instr(0x01, dst=4, a=2, b=3)  # r4 = x^2 + 3x
        p_exact[4] = encode_instr(0x0F, dst=7, a=4, b=10)  # r7 = x^2 + 3x + 7

        res_exact = verify_l2(
            program=p_exact,
            train_xs=train_xs,
            train_ys=train_ys,
            test_xs=test_xs,
            test_ys=test_ys,
            val_xs=val_xs,
            val_ys=val_ys,
            extrap_xs=extrap_xs,
            extrap_ys=extrap_ys,
            adversarial_xs=adv_xs,
            ground_truth_formula="x2_3x_7",
        )
        if not (res_exact.passed and res_exact.symbolic_equivalent):
            all_known_correct_passed = False

        # Reproduction check
        reproduced = reproduce_candidate(res_exact.exported_candidate, test_xs)
        reprod_err = float(
            np.max(np.abs(reproduced - res_exact.exported_candidate["recorded_predictions"]))
        )
        if reprod_err > 1e-12:
            all_reproduced = False

        # 2. Deliberate Overfit
        # Constant predictor matching train mean but failing extrapolation and test
        p_overfit = nop_program()
        p_overfit[0] = encode_instr(0x0F, dst=7, a=1, b=10)  # r7 = 7.0
        res_overfit = verify_l2(
            program=p_overfit,
            train_xs=train_xs[:4],
            train_ys=train_ys[:4],
            test_xs=test_xs,
            test_ys=test_ys,
            extrap_xs=extrap_xs,
            extrap_ys=extrap_ys,
            ground_truth_formula="x2_3x_7",
        )
        if res_overfit.passed:
            all_overfits_rejected = False

        # 3. Protected-Domain Exploit
        # Program divides by (x - 2.0)
        p_exploit = nop_program()
        p_exploit[0] = encode_instr(0x02, dst=2, a=0, b=1)  # r2 = x - 0
        p_exploit[1] = encode_instr(0x0F, dst=3, a=1, b=3)  # r3 = 2.0 (CONST_BANK[3])
        p_exploit[2] = encode_instr(0x02, dst=4, a=0, b=3)  # r4 = x - 2.0
        p_exploit[3] = encode_instr(0x04, dst=7, a=0, b=4)  # r7 = x / (x - 2.0)
        exploit_test_xs = np.concatenate([np.array([2.0]), test_xs[:16]])
        exploit_test_ys = exploit_test_xs**2 + 3.0 * exploit_test_xs + 7.0
        res_exploit = verify_l2(
            program=p_exploit,
            train_xs=train_xs,
            train_ys=train_ys,
            test_xs=exploit_test_xs,
            test_ys=exploit_test_ys,
            ground_truth_formula="x2_3x_7",
        )
        if res_exploit.passed or "protected_domain_exploit" not in res_exploit.reasons:
            all_exploits_rejected = False

        # 4. Rounding-Sensitive Example (float32 truncation)
        custom_bank = CONST_BANK.copy().astype(np.float64)
        custom_bank[15] = 16777216.0  # 2^24
        p_rounding = p_exact.copy()
        p_rounding[5] = encode_instr(0x0F, dst=2, a=0, b=15)  # r2 = x + 2^24
        p_rounding[6] = encode_instr(0x0F, dst=3, a=1, b=15)  # r3 = 2^24
        p_rounding[7] = encode_instr(0x02, dst=5, a=2, b=3)  # r5 = (x + 2^24) - 2^24
        p_rounding[8] = encode_instr(0x03, dst=5, a=5, b=5)  # r5 = r5^2
        p_rounding[9] = encode_instr(0x01, dst=7, a=7, b=5)  # r7 = r7 + r5
        rounding_xs = np.linspace(-0.4, 0.4, 30, dtype=np.float64)
        rounding_ys = rounding_xs**2 + 3.0 * rounding_xs + 7.0
        res_rounding = verify_l2(
            program=p_rounding,
            train_xs=rounding_xs,
            train_ys=rounding_ys,
            test_xs=rounding_xs,
            test_ys=rounding_ys,
            constants=custom_bank,
            ground_truth_formula="x2_3x_7",
        )
        if res_rounding.passed or "float_precision_divergence" not in res_rounding.reasons:
            all_rounding_rejected = False

        # 5. Archive Null Test & Hall of Fame Gate
        archive = EliteArchive(":memory:")
        sha_exact = res_exact.exported_candidate["sha256"]
        archive.add_elite(
            program=p_exact,
            generation=1,
            fitness=0.01,
            train_error=0.01,
            validation_error=None,
            test_error=None,
            status="provisional",
        )
        row = archive.get_by_hash(sha_exact)
        if row is None or row["validation_error"] is not None or row["test_error"] is not None:
            all_archive_null_ok = False

        # HoF strict test
        tmp_hof = Path(f"/tmp/evobyte_p19_hof_test_{s}.jsonl")
        if tmp_hof.exists():
            tmp_hof.unlink()
        provisional_entry = {
            "rank": 1,
            "fitness": 0.01,
            "expression": "x^2 + 3x + 7",
            "generation": 1,
            "train_error": 0.01,
            "status": "provisional",
        }
        promoted_prov = write_hall_of_fame_entry(
            tmp_hof, provisional_entry, require_strict_evidence=True
        )
        confirmed_entry = {
            "rank": 1,
            "fitness": 0.001,
            "expression": "x^2 + 3x + 7",
            "generation": 10,
            "train_error": 0.0,
            "validation_error": 1e-12,
            "test_error": 1e-12,
            "extrapolation_error": 2e-11,
            "status": "confirmed",
            "verifier_outcome": "verified_discovery",
        }
        promoted_conf = write_hall_of_fame_entry(
            tmp_hof, confirmed_entry, require_strict_evidence=True
        )
        if promoted_prov is not False or promoted_conf is not True:
            all_hof_strict_ok = False
        if tmp_hof.exists():
            tmp_hof.unlink()
        archive.close()

        per_seed_results.append(
            {
                "seed": s,
                "audit": audit_entry,
                "known_correct": {
                    "passed": res_exact.passed,
                    "decision": res_exact.decision,
                    "f64_test_mse": res_exact.f64_test_mse,
                    "f32_test_mse": res_exact.f32_test_mse,
                    "extrap_mse": res_exact.extrap_mse,
                    "symbolic_equivalent": res_exact.symbolic_equivalent,
                    "proof_type": res_exact.proof_type,
                    "reproduction_max_diff": reprod_err,
                },
                "deliberate_overfit": {
                    "passed": res_overfit.passed,
                    "decision": res_overfit.decision,
                    "reasons": res_overfit.reasons,
                    "train_mse": res_overfit.train_mse,
                    "f64_test_mse": res_overfit.f64_test_mse,
                },
                "protected_domain_exploit": {
                    "passed": res_exploit.passed,
                    "decision": res_exploit.decision,
                    "reasons": res_exploit.reasons,
                    "ordinary_math_valid": res_exploit.ordinary_math_valid,
                    "ordinary_math_error": res_exploit.ordinary_math_error,
                },
                "rounding_sensitive": {
                    "passed": res_rounding.passed,
                    "decision": res_rounding.decision,
                    "reasons": res_rounding.reasons,
                    "f32_test_mse": res_rounding.f32_test_mse,
                    "f64_test_mse": res_rounding.f64_test_mse,
                    "divergence": res_rounding.f64_f32_divergence,
                },
            }
        )

    verdict = (
        "PASS"
        if (
            all_known_correct_passed
            and all_overfits_rejected
            and all_exploits_rejected
            and all_rounding_rejected
            and all_reproduced
            and all_archive_null_ok
            and all_hof_strict_ok
        )
        else "FAIL"
    )

    report = {
        "metadata": {
            "suite": "P19 Strict Verification & Discovery Evidence",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "seeds": seeds,
            "platform": platform.platform(),
            "python": platform.python_version(),
            "torch": torch.__version__,
        },
        "summary": {
            "all_known_correct_passed": all_known_correct_passed,
            "all_overfits_rejected": all_overfits_rejected,
            "all_exploits_rejected": all_exploits_rejected,
            "all_rounding_rejected": all_rounding_rejected,
            "all_reproduced": all_reproduced,
            "all_archive_null_ok": all_archive_null_ok,
            "all_hof_strict_ok": all_hof_strict_ok,
            "verdict": verdict,
        },
        "seeds_data": per_seed_results,
    }

    # Print summary table
    print(f"{'Category':<32} | {'Expected':<12} | {'Actual':<12} | {'Status'}")
    print("-" * 75)
    print(
        f"{'Known-Correct Program':<32} | {'PASS':<12} | {'PASS' if all_known_correct_passed else 'FAIL':<12} | {'OK' if all_known_correct_passed else 'FAILED'}"
    )
    print(
        f"{'Deliberate Overfit':<32} | {'REJECT':<12} | {'REJECT' if all_overfits_rejected else 'ACCEPT':<12} | {'OK' if all_overfits_rejected else 'FAILED'}"
    )
    print(
        f"{'Protected-Domain Exploit':<32} | {'REJECT':<12} | {'REJECT' if all_exploits_rejected else 'ACCEPT':<12} | {'OK' if all_exploits_rejected else 'FAILED'}"
    )
    print(
        f"{'Rounding-Sensitive (f32/f64)':<32} | {'REJECT':<12} | {'REJECT' if all_rounding_rejected else 'ACCEPT':<12} | {'OK' if all_rounding_rejected else 'FAILED'}"
    )
    print(
        f"{'Candidate Reproduction':<32} | {'EXACT':<12} | {'EXACT' if all_reproduced else 'MISMATCH':<12} | {'OK' if all_reproduced else 'FAILED'}"
    )
    print(
        f"{'Archive NULL for Unmeasured':<32} | {'NULL':<12} | {'NULL' if all_archive_null_ok else 'NON-NULL':<12} | {'OK' if all_archive_null_ok else 'FAILED'}"
    )
    print(
        f"{'Hall of Fame Strict Gate':<32} | {'ENFORCED':<12} | {'ENFORCED' if all_hof_strict_ok else 'BYPASSED':<12} | {'OK' if all_hof_strict_ok else 'FAILED'}"
    )
    print("-" * 75)
    print(f"Overall Strict Verification Gate: {verdict}\n")

    if output_path is not None:
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"Exported strict verification report to {output_path}")

    return report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--benchmark", action="store_true")
    ap.add_argument("--generators", action="store_true")
    ap.add_argument("--cascade", action="store_true")
    ap.add_argument(
        "--strict-verification",
        action="store_true",
        help="Run Level-2 strict verification suite (P19)",
    )
    ap.add_argument(
        "--seeds",
        type=int,
        default=5,
        help="Number of random seeds for strict verification",
    )
    ap.add_argument(
        "--output",
        type=str,
        default=None,
        help="Path to write JSON benchmark report",
    )
    args = ap.parse_args()

    if args.strict_verification:
        report = run_strict_verification(seeds=args.seeds, output_path=args.output)
        return 0 if report["summary"]["verdict"] == "PASS" else 1

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
