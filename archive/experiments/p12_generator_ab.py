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


# -----------------------------------------------------------------------------
# P22 — Cross-task transfer protocol (disjoint families, billed costs)
# -----------------------------------------------------------------------------

P22_PREREG = {
    "train_families": ["quad"],
    "val_families": ["cubic"],
    "test_families": ["sinlin"],
    "success_hidden_mse": 1e-3,
    "success_extrap_mse": 1e-3,
    "min_ttq_benefit": 0.15,
    "max_throughput_penalty": 0.30,
    "n_new_tasks": 2,
    "note": "Split by structure/family, not by points. Held-out solutions and "
    "test trajectories never enter archives or training inputs; hidden splits "
    "are scoring-only. Neural training is offline on train elites and billed.",
}


def p22_family_function(name: str, x: np.ndarray) -> np.ndarray:
    if name == "quad":
        return x * x + 3.0 * x + 7.0
    if name == "cubic":
        return x * x * x - 2.0 * x + 1.0
    if name == "sinlin":
        return np.sin(x) + 2.0 * x + 1.0
    raise ValueError(f"unknown P22 family {name!r}")


def p22_family_splits() -> dict[str, dict[str, Any]]:
    import hashlib as _hashlib

    specs: dict[str, tuple[str, float, float, float, float]] = {
        # name -> (family, train_lo, train_hi, extrap_lo, extrap_hi)
        "quad": ("quad", -5.0, 5.0, 6.0, 12.0),
        "cubic": ("cubic", -2.0, 2.0, 2.6, 4.0),
        "sinlin": ("sinlin", -5.0, 5.0, 6.0, 10.0),
    }
    out: dict[str, dict[str, Any]] = {}
    for task, (fam, lo, hi, elo, ehi) in specs.items():
        xs_train = np.linspace(lo, hi, 64, dtype=np.float32)
        # Interleaved holdout: shifted grid, never used for selection.
        xs_hidden = np.linspace(lo + 0.05, hi - 0.05, 64, dtype=np.float32)
        xs_extrap = np.linspace(elo, ehi, 64, dtype=np.float32)
        f = lambda v, _fam=fam: p22_family_function(_fam, v.astype(np.float64)).astype(np.float32)
        ys_train, ys_hidden, ys_extrap = f(xs_train), f(xs_hidden), f(xs_extrap)
        h = _hashlib.sha256(
            f"{task}|{fam}|".encode() + xs_train.tobytes() + ys_train.tobytes()
        ).hexdigest()[:16]
        out[task] = {
            "family": fam,
            "train": (xs_train, ys_train),
            "hidden": (xs_hidden, ys_hidden),
            "extrapolation": (xs_extrap, ys_extrap),
            "sha16": h,
        }
    return out


def p22_build_opcode_distribution(elites: list[np.ndarray]) -> np.ndarray:
    """Simple learned prior: normalized opcode frequencies over train elites."""
    from evobyte.bytecode import decode_instr

    counts = np.ones(16, dtype=np.float64)  # Laplace smoothing
    for prog in elites:
        for w in np.asarray(prog, dtype=np.uint32):
            op, _, _, _ = decode_instr(w)
            counts[int(op) & 0x0F] += 1.0
    probs = counts / counts.sum()
    return probs


def p22_sample_from_opcode_dist(
    rng: np.random.Generator, probs: np.ndarray, n: int
) -> np.ndarray:
    """Sample programs from the learned opcode prior, preserving S0 validity.

    Starts from structured samples (valid skeletons) and resamples each
    non-NOP opcode from the learned distribution. Operands are kept from the
    skeleton, so operand-range validity is inherited.
    """
    from evobyte.bytecode import decode_instr, encode_instr

    pops = [sample_structured(rng) for _ in range(n)]
    out = []
    for prog in pops:
        prog = np.asarray(prog, dtype=np.uint32).copy()
        for i, w in enumerate(prog):
            op, dst, a, b = decode_instr(w)
            if int(op) == 0x00:
                continue
            new_op = int(rng.choice(16, p=probs))
            if new_op == 0x00:
                continue  # keep skeleton non-NOP structure
            prog[i] = encode_instr(new_op, dst, a, b)
        # S0-validity guard on the output register (mirror generator.py).
        from evobyte.bytecode import RISKY_OPS

        op, _, a, b = decode_instr(prog[-1])
        if int(op) == 0x00 or int(op) in RISKY_OPS:
            prog[-1] = encode_instr(0x01, 7, int(a) % 8, int(b) % 8)
        out.append(prog)
    return np.stack(out)


def p22_final_eval_f64(program: np.ndarray, xs: np.ndarray, ys: np.ndarray) -> float | None:
    """P19-style strict float64 MSE for a promoted program; None if unavailable."""
    try:
        from evobyte.vm import execute_batch_f64
    except (ImportError, AttributeError):
        return None
    try:
        pred, invalid = execute_batch_f64(
            np.asarray(program), np.asarray(xs, dtype=np.float64)
        )
        pred = np.asarray(pred, dtype=np.float64)
        target = np.asarray(ys, dtype=np.float64)
        mse = float(np.mean((pred - target) ** 2))
        if invalid.size and bool(np.asarray(invalid).any()):
            mse += 1e6
        return mse
    except (ValueError, RuntimeError, TypeError):
        return None


def run_method_learned_dist(
    xs_train: np.ndarray,
    ys_train: np.ndarray,
    budget_sec: float,
    seed: int,
    opcode_probs: np.ndarray,
    batch_size: int = 250,
) -> dict[str, Any]:
    rng = np.random.default_rng(seed ^ 0x22C3)
    ys_t = torch.from_numpy(ys_train)
    best_prog = p22_sample_from_opcode_dist(rng, opcode_probs, 1)[0]
    best_mse = float("inf")
    best_fitness = float("inf")
    total_evaluated = 0
    ttq = budget_sec  # censored default
    t0 = time.perf_counter()
    while time.perf_counter() - t0 < budget_sec:
        pop = p22_sample_from_opcode_dist(rng, opcode_probs, batch_size)
        raw_mse, fitnesses = evaluate_batch_fitness(pop, xs_train, ys_t)
        total_evaluated += len(pop)
        elapsed = time.perf_counter() - t0
        min_idx = int(np.argmin(fitnesses))
        if fitnesses[min_idx] < best_fitness:
            best_fitness = float(fitnesses[min_idx])
            best_mse = float(raw_mse[min_idx])
            best_prog = pop[min_idx].copy()
            if best_mse <= 1e-3 and ttq >= budget_sec:
                ttq = elapsed
            if best_mse <= 1e-5:
                break
    elapsed = time.perf_counter() - t0
    return {
        "method": "learned-dist",
        "best_program": best_prog,
        "best_mse": best_mse,
        "best_fitness": best_fitness,
        "total_evaluated": total_evaluated,
        "time_sec": elapsed,
        "ttq_sec": float(min(ttq, elapsed)),
        "cvps": total_evaluated / max(elapsed, 1e-6),
    }


def run_method_neural_frozen(
    xs_train: np.ndarray,
    ys_train: np.ndarray,
    budget_sec: float,
    seed: int,
    generator: MicroGenerator,
    batch_size: int = 128,
) -> dict[str, Any]:
    ys_t = torch.from_numpy(ys_train)
    generator.model.eval()
    # Cold start on the new task: a small random elite pool for scoring only.
    # The generator itself stays frozen (train-family prior); no fitting here.
    rng = np.random.default_rng(seed ^ 0xF207)
    init_pop = np.stack([sample_structured(rng) for _ in range(batch_size)])
    raw_mse, fitnesses = evaluate_batch_fitness(init_pop, xs_train, ys_t)
    total_evaluated = len(init_pop)
    best_idx = int(np.argmin(fitnesses))
    best_prog = init_pop[best_idx].copy()
    best_fitness = float(fitnesses[best_idx])
    best_mse = float(raw_mse[best_idx])
    ttq = budget_sec
    if best_mse <= 1e-3:
        ttq = 0.0
    t0 = time.perf_counter()
    with torch.no_grad():
        while time.perf_counter() - t0 < budget_sec:
            candidates = generator.sample_candidates(batch_size, elites=None, p_prefix_condition=0.0)
            raw_mse, fitnesses = evaluate_batch_fitness(candidates, xs_train, ys_t)
            total_evaluated += len(candidates)
            elapsed = time.perf_counter() - t0
            min_idx = int(np.argmin(fitnesses))
            if fitnesses[min_idx] < best_fitness:
                best_fitness = float(fitnesses[min_idx])
                best_mse = float(raw_mse[min_idx])
                best_prog = candidates[min_idx].copy()
                if best_mse <= 1e-3 and ttq >= budget_sec:
                    ttq = elapsed
                if best_mse <= 1e-5:
                    break
    elapsed = time.perf_counter() - t0
    return {
        "method": "neural-frozen",
        "best_program": best_prog,
        "best_mse": best_mse,
        "best_fitness": best_fitness,
        "total_evaluated": total_evaluated,
        "time_sec": elapsed,
        "ttq_sec": float(min(ttq, elapsed)),
        "cvps": total_evaluated / max(elapsed, 1e-6),
    }


def run_method_hybrid_frozen(
    xs_train: np.ndarray,
    ys_train: np.ndarray,
    budget_sec: float,
    seed: int,
    generator: MicroGenerator,
    pop_size: int = 500,
) -> dict[str, Any]:
    rng = np.random.default_rng(seed ^ 0x71B)
    ys_t = torch.from_numpy(ys_train)
    generator.model.eval()
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
    ttq = budget_sec
    t0 = time.perf_counter()
    with torch.no_grad():
        while time.perf_counter() - t0 < budget_sec:
            raw_mse, fitnesses = evaluate_batch_fitness(pop, xs_train, ys_t)
            total_evaluated += len(pop)
            elapsed = time.perf_counter() - t0
            min_idx = int(np.argmin(fitnesses))
            if fitnesses[min_idx] < best_fitness:
                best_fitness = float(fitnesses[min_idx])
                best_mse = float(raw_mse[min_idx])
                best_prog = pop[min_idx].copy()
                if best_mse <= 1e-3 and ttq >= budget_sec:
                    ttq = elapsed
                if best_mse <= 1e-5:
                    break
            next_pop = step_generation(pop, fitnesses, cfg_evo, rng)
            n_neural = int(pop_size * 0.25)
            neural_candidates = generator.sample_candidates(
                n_neural, elites=None, p_prefix_condition=0.0
            )
            next_pop[-n_neural:] = neural_candidates
            pop = next_pop
    elapsed = time.perf_counter() - t0
    return {
        "method": "hybrid-frozen",
        "best_program": best_prog,
        "best_mse": best_mse,
        "best_fitness": best_fitness,
        "total_evaluated": total_evaluated,
        "time_sec": elapsed,
        "ttq_sec": float(min(ttq, elapsed)),
        "cvps": total_evaluated / max(elapsed, 1e-6),
    }


def run_cross_task_benchmark(
    seeds: list[int],
    total_budget_sec: float = 600.0,
    output_path: str = "experiments/p22-transfer.json",
    train_budget_sec: float = 30.0,
    neural_epochs: int = 5,
) -> tuple[bool, dict[str, Any]]:
    import json as _json
    import subprocess as _subprocess
    from pathlib import Path as _Path

    families = p22_family_splits()
    train_tasks = list(P22_PREREG["train_families"])
    heldout_tasks = list(P22_PREREG["val_families"]) + list(P22_PREREG["test_families"])
    methods = ["genetic", "learned-dist", "neural-frozen", "hybrid-frozen"]
    n_evals = len(seeds) * len(heldout_tasks) * len(methods)
    budget_per_eval = total_budget_sec / max(1, n_evals)

    print("================================================================================")
    print("P22 Cross-Task Transfer: genetic control vs learned priors on held-out families")
    print(f"Train: {train_tasks} | Held-out: {heldout_tasks} | Seeds: {len(seeds)}")
    print(f"Transfer budget total: {total_budget_sec:.0f}s | per-method-per-task-per-seed: {budget_per_eval:.1f}s")
    print(f"Prereg: TTQ benefit>={P22_PREREG['min_ttq_benefit']*100:.0f}% + CVPS>=70% on BOTH held-out families")
    print("================================================================================\n")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    per_seed: list[dict[str, Any]] = []
    train_costs: list[dict[str, Any]] = []
    neural_costs: list[dict[str, Any]] = []

    for s in seeds:
        xs_tr, ys_tr = families["quad"]["train"]
        # 1. Train-family genetic run to build the elite archive (billed).
        t_arch0 = time.perf_counter()
        arch_res = run_method_genetic(xs_tr, ys_tr, train_budget_sec, s)
        arch_time = time.perf_counter() - t_arch0
        # Reconstruct a small elite archive from a fresh scored pool (held-out
        # trajectories never enter here; only train-family points are used).
        rng_arch = np.random.default_rng(s ^ 0xA9C4)
        ys_t = torch.from_numpy(ys_tr)
        pool = np.stack([sample_structured(rng_arch) for _ in range(256)])
        _, fitnesses = evaluate_batch_fitness(pool, xs_tr, ys_t)
        elite_idx = np.argsort(fitnesses)[:32]
        train_elites = [pool[i].copy() for i in elite_idx]
        train_costs.append({
            "seed": s,
            "archive_time_sec": arch_time,
            "archive_evals": int(arch_res["total_evaluated"] + len(pool)),
            "train_best_mse": float(arch_res["best_mse"]),
        })

        # 2. Offline neural training on train elites only (explicitly billed).
        cfg_gen = GeneratorConfig(d_model=128, nhead=4, num_layers=3, dim_feedforward=256)
        generator = MicroGenerator(config=cfg_gen, device=device)
        n_params = int(sum(p.numel() for p in generator.model.parameters()))
        assert n_params <= 5_000_000, f"neural exceeds 5M cap: {n_params}"
        t_nn0 = time.perf_counter()
        train_stats = generator.train_on_elites(train_elites, epochs=neural_epochs)
        nn_time = time.perf_counter() - t_nn0
        if torch.cuda.is_available():
            try:
                vram_mb = float(torch.cuda.memory_allocated() / 1e6)
            except RuntimeError:
                vram_mb = float(n_params * 4 / 1e6)
        else:
            vram_mb = float(n_params * 4 / 1e6)
        neural_costs.append({
            "seed": s,
            "n_params": n_params,
            "train_time_sec": nn_time,
            "train_loss": float(train_stats.get("loss", 0.0)),
            "train_steps": int(train_stats.get("steps", 0)),
            "vram_mb": vram_mb,
        })

        # 3. Learned opcode prior from train elites only.
        opcode_probs = p22_build_opcode_distribution(train_elites)

        for task in heldout_tasks:
            xs_t, ys_t_arr = families[task]["train"]
            xs_h, ys_h = families[task]["hidden"]
            xs_e, ys_e = families[task]["extrapolation"]
            # Genetic control from scratch on the new task.
            g = run_method_genetic(xs_t, ys_t_arr, budget_per_eval, s)
            ld = run_method_learned_dist(xs_t, ys_t_arr, budget_per_eval, s, opcode_probs)
            nf = run_method_neural_frozen(xs_t, ys_t_arr, budget_per_eval, s, generator)
            hf = run_method_hybrid_frozen(xs_t, ys_t_arr, budget_per_eval, s, generator)
            for res in (g, ld, nf, hf):
                ev_h = evaluate(res["best_program"], xs_h, ys_h)
                ev_e = evaluate(res["best_program"], xs_e, ys_e)
                f64_h = p22_final_eval_f64(res["best_program"], xs_h, ys_h)
                success = (ev_h["mse"] <= 1e-3) and (ev_e["mse"] <= 1e-3)
                per_seed.append({
                    "seed": s,
                    "task": task,
                    "family": families[task]["family"],
                    "method": res["method"],
                    "train_mse": float(res["best_mse"]),
                    "hidden_mse": float(ev_h["mse"]),
                    "extrap_mse": float(ev_e["mse"]),
                    "hidden_mse_f64": (None if f64_h is None else float(f64_h)),
                    "success": bool(success),
                    "ttq_sec": float(res.get("ttq_sec", res["time_sec"])),
                    "time_sec": float(res["time_sec"]),
                    "total_evaluated": int(res["total_evaluated"]),
                    "cvps": float(res["cvps"]),
                    "expression": decode_human(res["best_program"]),
                })
            print(f"  [seed {s} task {task}] " + " | ".join(
                f"{r['method']} hid={r['hidden_mse']:.2e} ttq={r['ttq_sec']:.1f}s"
                for r in per_seed[-4:]
            ))

    # Summary per held-out task x method.
    summary: dict[str, dict[str, dict[str, float]]] = {}
    for task in heldout_tasks:
        summary[task] = {}
        for m in methods:
            recs = [r for r in per_seed if r["task"] == task and r["method"] == m]
            summary[task][m] = {
                "success_rate": float(np.mean([1.0 if r["success"] else 0.0 for r in recs])),
                "mean_hidden_mse": float(np.mean([r["hidden_mse"] for r in recs])),
                "mean_extrap_mse": float(np.mean([r["extrap_mse"] for r in recs])),
                "mean_ttq_sec": float(np.mean([r["ttq_sec"] for r in recs])),
                "mean_cvps": float(np.mean([r["cvps"] for r in recs])),
                "mean_time_sec": float(np.mean([r["time_sec"] for r in recs])),
            }

    # Preregistered KEEP/DROP verdict: best learned config must beat genetic
    # TTQ by >=15% AND keep CVPS >=70% on BOTH held-out families.
    learned = ["learned-dist", "neural-frozen", "hybrid-frozen"]
    per_task_pass: dict[str, dict[str, Any]] = {}
    for task in heldout_tasks:
        g_ttq = summary[task]["genetic"]["mean_ttq_sec"]
        g_cvps = summary[task]["genetic"]["mean_cvps"]
        best: dict[str, Any] = {"method": None, "benefit": -1.0, "cvps_ratio": 0.0}
        for m in learned:
            ttq = summary[task][m]["mean_ttq_sec"]
            cvps = summary[task][m]["mean_cvps"]
            benefit = (g_ttq - ttq) / max(g_ttq, 1e-9)
            ratio = cvps / max(g_cvps, 1e-9)
            if benefit > best["benefit"]:
                best = {"method": m, "benefit": float(benefit), "cvps_ratio": float(ratio)}
        pas = (best["benefit"] >= P22_PREREG["min_ttq_benefit"]) and (
            best["cvps_ratio"] >= 1.0 - P22_PREREG["max_throughput_penalty"]
        )
        per_task_pass[task] = {"pass": bool(pas), **best}
    keep = bool(all(v["pass"] for v in per_task_pass.values()))
    verdict = "KEEP" if keep else "DROP"

    mean_train_time = float(np.mean([c["archive_time_sec"] for c in train_costs]))
    mean_nn_time = float(np.mean([c["train_time_sec"] for c in neural_costs]))
    mean_transfer_time = float(np.mean([r["time_sec"] for r in per_seed]))
    amortized = (mean_train_time + mean_nn_time + len(per_seed) / len(seeds) * mean_transfer_time) / P22_PREREG["n_new_tasks"]

    try:
        commit = _subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5, check=False,
        ).stdout.strip() or "unknown"
    except (OSError, _subprocess.SubprocessError):
        commit = "unknown"
    payload = {
        "phase": "P22",
        "preregistration": P22_PREREG,
        "families": {k: {"family": v["family"], "sha16": v["sha16"]} for k, v in families.items()},
        "thresholds": {"success_hidden_mse": 1e-3, "success_extrap_mse": 1e-3},
        "budgets": {
            "total_transfer_budget_sec": total_budget_sec,
            "budget_per_eval_sec": budget_per_eval,
            "train_budget_sec": train_budget_sec,
            "neural_epochs": neural_epochs,
        },
        "costs": {
            "train": train_costs,
            "neural_offline": neural_costs,
            "mean_archive_time_sec": mean_train_time,
            "mean_neural_train_time_sec": mean_nn_time,
            "mean_transfer_time_sec": mean_transfer_time,
            "amortized_sec_per_new_task": amortized,
        },
        "summary": summary,
        "per_task_verdict": per_task_pass,
        "verdict": verdict,
        "decision": "D010 stands (genetic default)" if verdict == "DROP" else "Requires ADR superseding D010",
        "details": per_seed,
        "provenance": {
            "commit": commit,
            "device": device,
            "torch": torch.__version__,
            "cuda_available": bool(torch.cuda.is_available()),
        },
    }
    out_p = _Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(_json.dumps(payload, indent=2), encoding="utf-8")

    print("\n--------------------------------------------------------------------------------")
    print(f"P22 verdict: {verdict} "
          f"({'D010 stands' if verdict == 'DROP' else 'needs ADR superseding D010'})")
    for task in heldout_tasks:
        v = per_task_pass[task]
        print(f"  {task}: best-learned={v['method']} benefit={v['benefit']*100:.1f}% "
              f"cvps_ratio={v['cvps_ratio']*100:.1f}% -> {'PASS' if v['pass'] else 'FAIL'}")
    print(f"Amortized cost per new task: {amortized:.1f}s "
          f"(archive {mean_train_time:.1f}s + neural {mean_nn_time:.1f}s billed)")
    print(f"Artifact: {out_p}")
    print("--------------------------------------------------------------------------------\n")
    return True, payload


def main() -> int:
    parser = argparse.ArgumentParser(description="P12 4-Way Neural Generator Benchmark (+ P22 cross-task)")
    parser.add_argument("--budget", type=str, default="10min", help="Total time budget (default: 10min)")
    parser.add_argument("--seeds", type=int, default=5, help="Number of seeds (default: 5)")
    parser.add_argument("--cross-task", action="store_true", help="Run P22 cross-task transfer protocol")
    parser.add_argument("--output", type=str, default="", help="Output JSON path for --cross-task (default: experiments/p22-transfer.json)")
    args = parser.parse_args()

    default_seeds = [42, 101, 202, 303, 404]
    if args.seeds == 5:
        seeds = default_seeds
    else:
        seeds = [100 + i for i in range(args.seeds)]

    budget_sec = parse_budget(args.budget)
    if args.cross_task:
        out_path = args.output or "experiments/p22-transfer.json"
        passed, _ = run_cross_task_benchmark(seeds=seeds, total_budget_sec=budget_sec, output_path=out_path)
        return 0 if passed else 1
    passed, _ = run_4way_benchmark(seeds=seeds, total_budget_sec=budget_sec)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
