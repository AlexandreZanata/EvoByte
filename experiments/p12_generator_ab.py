"""Experiment script for P12: 4-Way Comparison (Random vs Genetic vs Neural vs Neural+Genetic)."""

from __future__ import annotations

import argparse
import sys
import time
from typing import Any

import numpy as np
import torch

from evobyte.batching import execute_chunked
from evobyte.bytecode import decode_human
from evobyte.evolution import EvolutionConfig, sample_structured, step_generation
from evobyte.generator import GeneratorConfig, MicroGenerator
from evobyte.verifier import evaluate


def parse_budget(budget_str: str) -> float:
    s = budget_str.strip().lower()
    if s.endswith("h"):
        return float(s[:-1]) * 3600.0
    if s.endswith("m") or s.endswith("min"):
        num = s.replace("min", "").replace("m", "")
        return float(num) * 60.0
    if s.endswith("s"):
        return float(s[:-1])
    return float(s)


def generate_target_splits(n_points: int = 64) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    def f(x: np.ndarray) -> np.ndarray:
        return x * x + 3.0 * x + 7.0

    xs_train = np.linspace(-5.0, 5.0, n_points, dtype=np.float32)
    ys_train = f(xs_train)

    xs_val = np.linspace(-7.0, 7.0, n_points, dtype=np.float32)
    ys_val = f(xs_val)

    xs_hidden = np.linspace(-4.95, 4.95, n_points, dtype=np.float32)
    ys_hidden = f(xs_hidden)

    xs_extrap = np.linspace(6.0, 12.0, n_points, dtype=np.float32)
    ys_extrap = f(xs_extrap)

    return {
        "train": (xs_train, ys_train),
        "val": (xs_val, ys_val),
        "hidden": (xs_hidden, ys_hidden),
        "extrapolation": (xs_extrap, ys_extrap),
    }


def evaluate_batch_fitness(
    pop: np.ndarray,
    xs: np.ndarray,
    ys_t: torch.Tensor,
    complexity_weight: float = 0.001,
) -> tuple[np.ndarray, np.ndarray]:
    """Vectorized batch evaluation returning (raw_mse, fitnesses)."""
    preds, flags = execute_chunked(pop, xs)
    diff = preds - ys_t.unsqueeze(0).to(preds.device)
    mse = (diff ** 2).mean(dim=1)
    mse[flags.any(dim=1)] += 1e6
    raw_mse = mse.cpu().numpy()

    complexity = np.array(
        [sum((int(w) & 0xFF) != 0 for w in p) for p in pop], dtype=np.float32
    )
    fitnesses = raw_mse + complexity_weight * complexity
    return raw_mse, fitnesses


def run_method_random(
    xs_train: np.ndarray,
    ys_train: np.ndarray,
    budget_sec: float,
    seed: int,
    batch_size: int = 250,
) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    ys_t = torch.from_numpy(ys_train)

    best_prog = sample_structured(rng)
    best_mse = float("inf")
    best_fitness = float("inf")
    total_evaluated = 0

    t0 = time.perf_counter()
    while time.perf_counter() - t0 < budget_sec:
        pop = np.stack([sample_structured(rng) for _ in range(batch_size)])
        raw_mse, fitnesses = evaluate_batch_fitness(pop, xs_train, ys_t)
        total_evaluated += len(pop)

        min_idx = int(np.argmin(fitnesses))
        if fitnesses[min_idx] < best_fitness:
            best_fitness = float(fitnesses[min_idx])
            best_mse = float(raw_mse[min_idx])
            best_prog = pop[min_idx].copy()
            if best_mse <= 1e-5:
                break

    elapsed = time.perf_counter() - t0
    return {
        "method": "random",
        "best_program": best_prog,
        "best_mse": best_mse,
        "best_fitness": best_fitness,
        "total_evaluated": total_evaluated,
        "time_sec": elapsed,
        "cvps": total_evaluated / max(elapsed, 1e-6),
    }


def run_method_genetic(
    xs_train: np.ndarray,
    ys_train: np.ndarray,
    budget_sec: float,
    seed: int,
    pop_size: int = 500,
) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    ys_t = torch.from_numpy(ys_train)
    cfg = EvolutionConfig(
        pop_size=pop_size,
        elite_k=32,
        tournament_size=4,
        crossover_p=0.4,
        gene_mut_p=0.10,
        large_mut_p=0.08,
        point_mut_p=0.02,
        random_inject_p=0.10,
        max_generations=10000,
        early_stop_fitness=1e-5,
    )

    pop = np.stack([sample_structured(rng) for _ in range(cfg.pop_size)])
    best_prog = pop[0].copy()
    best_mse = float("inf")
    best_fitness = float("inf")
    total_evaluated = 0

    t0 = time.perf_counter()
    while time.perf_counter() - t0 < budget_sec:
        raw_mse, fitnesses = evaluate_batch_fitness(pop, xs_train, ys_t)
        total_evaluated += len(pop)

        min_idx = int(np.argmin(fitnesses))
        if fitnesses[min_idx] < best_fitness:
            best_fitness = float(fitnesses[min_idx])
            best_mse = float(raw_mse[min_idx])
            best_prog = pop[min_idx].copy()
            if best_mse <= 1e-5:
                break

        pop = step_generation(pop, fitnesses, cfg, rng)

    elapsed = time.perf_counter() - t0
    return {
        "method": "genetic",
        "best_program": best_prog,
        "best_mse": best_mse,
        "best_fitness": best_fitness,
        "total_evaluated": total_evaluated,
        "time_sec": elapsed,
        "cvps": total_evaluated / max(elapsed, 1e-6),
    }


def run_method_neural(
    xs_train: np.ndarray,
    ys_train: np.ndarray,
    budget_sec: float,
    seed: int,
    batch_size: int = 128,
) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    ys_t = torch.from_numpy(ys_train)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    cfg_gen = GeneratorConfig(d_model=128, nhead=4, num_layers=3, dim_feedforward=256)
    generator = MicroGenerator(config=cfg_gen, device=device)

    # Seed initial elites from random structured programs
    initial_pop = np.stack([sample_structured(rng) for _ in range(batch_size)])
    raw_mse, fitnesses = evaluate_batch_fitness(initial_pop, xs_train, ys_t)
    total_evaluated = len(initial_pop)

    elite_indices = np.argsort(fitnesses)[:32]
    elites = [initial_pop[i].copy() for i in elite_indices]

    best_prog = initial_pop[elite_indices[0]].copy()
    best_fitness = float(fitnesses[elite_indices[0]])
    best_mse = float(raw_mse[elite_indices[0]])

    t0 = time.perf_counter()
    cycle = 0
    while time.perf_counter() - t0 < budget_sec:
        cycle += 1
        # Train on current elites for 2 epochs
        generator.train_on_elites(elites, epochs=2)

        # Sample new candidates (50% conditioned on elite prefixes, 50% unconditional)
        candidates = generator.sample_candidates(
            batch_size, elites=elites, p_prefix_condition=0.5
        )

        raw_mse, fitnesses = evaluate_batch_fitness(candidates, xs_train, ys_t)
        total_evaluated += len(candidates)

        min_idx = int(np.argmin(fitnesses))
        if fitnesses[min_idx] < best_fitness:
            best_fitness = float(fitnesses[min_idx])
            best_mse = float(raw_mse[min_idx])
            best_prog = candidates[min_idx].copy()
            if best_mse <= 1e-5:
                break

        # Incorporate top candidates into elite pool
        top_k_idx = np.argsort(fitnesses)[:8]
        for idx in top_k_idx:
            elites.append(candidates[idx].copy())
        # Keep top 32 elites
        if len(elites) > 64:
            elites = elites[-64:]

    elapsed = time.perf_counter() - t0
    return {
        "method": "neural",
        "best_program": best_prog,
        "best_mse": best_mse,
        "best_fitness": best_fitness,
        "total_evaluated": total_evaluated,
        "time_sec": elapsed,
        "cvps": total_evaluated / max(elapsed, 1e-6),
    }


def run_method_neural_genetic(
    xs_train: np.ndarray,
    ys_train: np.ndarray,
    budget_sec: float,
    seed: int,
    pop_size: int = 500,
) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    ys_t = torch.from_numpy(ys_train)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    cfg_gen = GeneratorConfig(d_model=128, nhead=4, num_layers=3, dim_feedforward=256)
    generator = MicroGenerator(config=cfg_gen, device=device)

    cfg_evo = EvolutionConfig(
        pop_size=pop_size,
        elite_k=32,
        tournament_size=4,
        crossover_p=0.4,
        gene_mut_p=0.10,
        large_mut_p=0.08,
        point_mut_p=0.02,
        random_inject_p=0.10,
    )

    pop = np.stack([sample_structured(rng) for _ in range(pop_size)])
    best_prog = pop[0].copy()
    best_mse = float("inf")
    best_fitness = float("inf")
    total_evaluated = 0
    elites: list[np.ndarray] = []

    t0 = time.perf_counter()
    gen = 0
    while time.perf_counter() - t0 < budget_sec:
        gen += 1
        raw_mse, fitnesses = evaluate_batch_fitness(pop, xs_train, ys_t)
        total_evaluated += len(pop)

        min_idx = int(np.argmin(fitnesses))
        if fitnesses[min_idx] < best_fitness:
            best_fitness = float(fitnesses[min_idx])
            best_mse = float(raw_mse[min_idx])
            best_prog = pop[min_idx].copy()
            if best_mse <= 1e-5:
                break

        # Collect elites for neural generator
        top_idx = np.argsort(fitnesses)[:cfg_evo.elite_k]
        elites = [pop[i].copy() for i in top_idx]

        # Standard genetic step
        next_pop = step_generation(pop, fitnesses, cfg_evo, rng)

        # Neural injection: replace 25% of offspring with neural samples
        n_neural = int(pop_size * 0.25)
        if gen % 3 == 0:
            generator.train_on_elites(elites, epochs=1)

        neural_candidates = generator.sample_candidates(
            n_neural, elites=elites, p_prefix_condition=0.6
        )
        next_pop[-n_neural:] = neural_candidates
        pop = next_pop

    elapsed = time.perf_counter() - t0
    return {
        "method": "neural+genetic",
        "best_program": best_prog,
        "best_mse": best_mse,
        "best_fitness": best_fitness,
        "total_evaluated": total_evaluated,
        "time_sec": elapsed,
        "cvps": total_evaluated / max(elapsed, 1e-6),
    }


def run_4way_benchmark(
    seeds: list[int],
    total_budget_sec: float = 600.0,
) -> tuple[bool, dict[str, Any]]:
    splits = generate_target_splits()
    xs_train, ys_train = splits["train"]
    xs_hidden, ys_hidden = splits["hidden"]
    xs_extrap, ys_extrap = splits["extrapolation"]

    budget_per_seed = total_budget_sec / len(seeds)
    budget_per_method = budget_per_seed / 4.0

    print("================================================================================")
    print("P12 4-Way Benchmark: Random vs Genetic vs Neural vs Neural+Genetic")
    print(f"Target: y = x^2 + 3x + 7 | Total Budget: {total_budget_sec:.0f}s | Budget/Method/Seed: {budget_per_method:.1f}s")
    print("================================================================================\n")

    methods = ["random", "genetic", "neural", "neural+genetic"]
    runners = {
        "random": run_method_random,
        "genetic": run_method_genetic,
        "neural": run_method_neural,
        "neural+genetic": run_method_neural_genetic,
    }

    results_by_method: dict[str, list[dict[str, Any]]] = {m: [] for m in methods}

    for s_idx, s in enumerate(seeds, 1):
        print(f"--- Seed {s} ({s_idx}/{len(seeds)}) ---")
        for m in methods:
            runner = runners[m]
            t_start = time.perf_counter()
            res = runner(xs_train, ys_train, budget_per_method, s)

            best_p = res["best_program"]
            ev_hid = evaluate(best_p, xs_hidden, ys_hidden)
            ev_ext = evaluate(best_p, xs_extrap, ys_extrap)

            success = (ev_hid["mse"] <= 1e-3) and (ev_ext["mse"] <= 1e-3)
            rec = {
                "seed": s,
                "train_mse": res["best_mse"],
                "hidden_mse": ev_hid["mse"],
                "extrap_mse": ev_ext["mse"],
                "total_evaluated": res["total_evaluated"],
                "time_sec": res["time_sec"],
                "cvps": res["cvps"],
                "success": success,
                "expression": decode_human(best_p),
            }
            results_by_method[m].append(rec)
            succ_str = "SUCCESS" if success else "FAIL"
            print(
                f"  [{m:<14}] Train MSE: {rec['train_mse']:<9.5f} | "
                f"Extrap MSE: {rec['extrap_mse']:<9.5f} | "
                f"CVPS: {rec['cvps']:<7.1f} | {succ_str}"
            )

    # 4-way Summary Table
    print("\n" + "=" * 90)
    print("P12 4-Way Benchmark Summary Table (Equal Wall-Clock Budget)")
    print("=" * 90)
    header = (
        f"{'Method':<16} | {'Success Rate':<12} | {'Mean Train MSE':<15} | "
        f"{'Mean Hidden MSE':<15} | {'Mean Extrap MSE':<15} | {'Mean CVPS':<10}"
    )
    print(header)
    print("-" * len(header))

    summary_stats = {}
    for m in methods:
        recs = results_by_method[m]
        succ_rate = np.mean([1.0 if r["success"] else 0.0 for r in recs])
        mean_tr = np.mean([r["train_mse"] for r in recs])
        mean_hid = np.mean([r["hidden_mse"] for r in recs])
        mean_ext = np.mean([r["extrap_mse"] for r in recs])
        mean_cvps = np.mean([r["cvps"] for r in recs])

        summary_stats[m] = {
            "success_rate": float(succ_rate),
            "mean_train_mse": float(mean_tr),
            "mean_hidden_mse": float(mean_hid),
            "mean_extrap_mse": float(mean_ext),
            "mean_cvps": float(mean_cvps),
        }

        print(
            f"{m:<16} | {succ_rate*100:>5.1f}% ({sum(1 for r in recs if r['success'])}/{len(recs)}) | "
            f"{mean_tr:<15.5f} | {mean_hid:<15.5f} | {mean_ext:<15.5f} | {mean_cvps:<10.1f}"
        )
    print("-" * len(header))

    # Keep-or-Drop Decision Analysis
    gen_succ = summary_stats["genetic"]["success_rate"]
    gen_cvps = summary_stats["genetic"]["mean_cvps"]

    neural_succ = summary_stats["neural"]["success_rate"]
    neural_gen_succ = summary_stats["neural+genetic"]["success_rate"]

    neural_cvps = summary_stats["neural"]["mean_cvps"]
    neural_gen_cvps = summary_stats["neural+genetic"]["mean_cvps"]

    # Rule: "generator stays only if it beats genetic per wall-clock second without hurting CVPS beyond its cap. Negative results are valid and recorded."
    neural_wins = (neural_succ > gen_succ or neural_gen_succ > gen_succ)
    cvps_preserved = (neural_gen_cvps >= gen_cvps * 0.70)

    decision_keep = neural_wins and cvps_preserved
    verdict_str = "KEEP" if decision_keep else "DROP (Negative Result Validated)"

    print("\n--------------------------------------------------------------------------------")
    print(f"ADR Keep-or-Drop Ruling: {verdict_str}")
    print(f"Genetic Success Rate: {gen_succ*100:.1f}% | CVPS: {gen_cvps:.1f}")
    print(f"Neural Standalone Success Rate: {neural_succ*100:.1f}% | CVPS: {neural_cvps:.1f}")
    print(f"Neural+Genetic Hybrid Success Rate: {neural_gen_succ*100:.1f}% | CVPS: {neural_gen_cvps:.1f}")
    print(f"P12 Exit Gate: PASS (Empirical 4-way comparison complete and measured)")
    print("--------------------------------------------------------------------------------\n")

    return True, {"summary": summary_stats, "details": results_by_method, "decision_keep": decision_keep}


def main() -> int:
    parser = argparse.ArgumentParser(description="P12 4-Way Neural Generator Benchmark")
    parser.add_argument("--budget", type=str, default="10min", help="Total time budget (default: 10min)")
    parser.add_argument("--seeds", type=int, default=5, help="Number of seeds (default: 5)")
    args = parser.parse_args()

    default_seeds = [42, 101, 202, 303, 404]
    if args.seeds == 5:
        seeds = default_seeds
    else:
        seeds = [100 + i for i in range(args.seeds)]

    budget_sec = parse_budget(args.budget)
    passed, _ = run_4way_benchmark(seeds=seeds, total_budget_sec=budget_sec)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
