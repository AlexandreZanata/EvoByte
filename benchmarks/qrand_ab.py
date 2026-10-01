"""P27 — Quantum-inspired randomness hypotheses (one per cycle, falsifiable).

Tests whether quantum-inspired sampling improves relevant exploration or solution rate
over uniform sampling, a simple learned distribution, and genetic evolution — under the
same wall-clock budget, same verifier, and same problems.

Inspiration is a claim about search distribution dynamics, not quantum execution.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import math
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "src"))

from evobyte.bytecode import (
    N_INSTR,
    N_REGS,
    decode_human,
)
from evobyte.evolution import EvolutionConfig
from evobyte.provenance import (
    MonotonicDeadline,
    collect_provenance,
    resolve_device,
    seed_all,
    synchronize,
    write_manifest,
)
from evobyte.resident import (
    gpu_crossover_single_point,
    gpu_mutate,
    gpu_sample_structured,
    gpu_tournament_selection,
)
from evobyte.vm_torch import execute_population_torch

PREREGISTRATION_SPEC = """
HYPOTHESIS: amplitude-distribution
PREREGISTRATION DATE: 2026-10-01
EQUATIONS:
1. Q-bit State: |psi_jk> = alpha_jk |0> + beta_jk |1>, with alpha_jk^2 + beta_jk^2 = 1.
   Parametrization: alpha_jk = cos(theta_jk), beta_jk = sin(theta_jk), theta_jk in [0.01*pi, 0.49*pi].
2. Selection Probability: P(opcode=k at slot j) = sin^2(theta_jk) / sum_m sin^2(theta_jm).
3. Quantum Rotation Gate:
   For best candidate opcode k*:
   theta_jk* <- min(theta_jk* + Delta_theta, 0.49*pi)
   theta_jk  <- max(theta_jk - Delta_theta / (N_ops - 1), 0.01*pi) for k != k*
   where Delta_theta = 0.05*pi.
MECHANISM: GPU-resident theta tensor updated via elite feedback; batched multinomial sampling.
PREDICTION: Under equal wall-clock budget and identical problem sets, amplitude-distribution
sampling discovers lower held-out MSE (or >= 15% higher distinct behavioral expressions)
relative to uniform random search, while remaining competitive with classical crossover-based genetic evolution.
FALSIFICATION THRESHOLD:
Delta_MSE_vs_uniform <= 0.0 and distinct_expression_ratio < 1.15.
CONTROLS: uniform, learned-dist, genetic.
EVALUATION: 5 independent seeds, train/held-out split on x^2 + 3x + 7.
"""

PREREGISTRATION_HASH = hashlib.sha256(PREREGISTRATION_SPEC.strip().encode("utf-8")).hexdigest()

LITERATURE_NOTE = {
    "prior_art": [
        {
            "citation": (
                "Han & Kim (2002), Quantum-inspired Evolutionary Algorithm with a New Termination "
                "Criterion, H-epsilon Gate, and Two-Phase Scheme, IEEE TEVC 6(6): 527-535"
            ),
            "mechanism": "Q-bit angle representation and rotation gate update",
        },
        {
            "citation": (
                "arXiv:quant-ph/0610105, Quantum-inspired evolutionary algorithm for solving "
                "combinatorial problems"
            ),
            "mechanism": "Theoretical analysis of classical sampling distributions parameterized by quantum state amplitudes",
        },
    ],
    "novelty_boundary": (
        "Application of Q-bit rotation to linear register bytecode instruction-slot distributions "
        "under fixed V0 interpreter constraints; inspiration is classical distribution dynamics, "
        "not quantum execution or quantum speedup."
    ),
}

PROBE_POINTS = np.array([-5.0, -2.0, -1.0, 0.0, 1.0, 2.0, 5.0, 10.0], dtype=np.float32)


# ==============================================================================
# Helper Functions: Encoders & Evaluators
# ==============================================================================


def encode_program_tensor(ops: torch.Tensor, device: torch.device) -> torch.Tensor:
    """Vectorized operand assignment and encoding from opcode tensor (n, N_INSTR)."""
    n = ops.shape[0]
    dst = torch.randint(0, N_REGS, (n, N_INSTR), device=device)
    a = torch.randint(0, N_REGS, (n, N_INSTR), device=device)
    b_reg = torch.randint(0, N_REGS, (n, N_INSTR), device=device)
    b_const = torch.randint(0, 16, (n, N_INSTR), device=device)
    b = torch.where(ops == 0x0F, b_const, b_reg)

    # Guarantee at least one write to r7
    has_r7 = ((dst == 7) & (ops != 0)).any(dim=1)
    if not has_r7.all():
        need = torch.nonzero(~has_r7).squeeze(1)
        dst[need, N_INSTR - 1] = 7
        ops[need, N_INSTR - 1] = 0x01  # ADD r7

    words = (ops & 0xFF) | ((dst & 0xFF) << 8) | ((a & 0xFF) << 16) | ((b & 0xFF) << 24)
    words = torch.where(ops != 0, words, torch.zeros_like(words))
    return words


def compute_expression_signatures(
    population: torch.Tensor,
    probe_xs: torch.Tensor,
    device: torch.device,
) -> set[str]:
    """Compute behavioral output hashes for a population on fixed probe points."""
    with torch.no_grad():
        preds, flags = execute_population_torch(population, probe_xs, device=device)
    vals = preds.cpu().numpy()
    flag_mask = flags.any(dim=1).cpu().numpy()

    sigs: set[str] = set()
    for i in range(len(vals)):
        row = vals[i]
        if flag_mask[i] or np.any(np.isnan(row)) or np.any(np.isinf(row)):
            continue
        rounded = np.round(row, 4)
        sig = hashlib.sha256(rounded.tobytes()).hexdigest()[:16]
        sigs.add(sig)
    return sigs


# ==============================================================================
# Search Arms: Equal-Budget Implementation
# ==============================================================================


def run_uniform_arm(
    *,
    xs_train: torch.Tensor,
    ys_train: torch.Tensor,
    xs_test: torch.Tensor,
    ys_test: torch.Tensor,
    probe_xs: torch.Tensor,
    device: torch.device,
    budget_sec: float,
    pop_size: int = 100,
) -> dict[str, Any]:
    """Arm 1: Pure uniform random sampling over opcode space."""
    t0 = time.perf_counter()
    iterations = 0
    total_evals = 0
    best_fit = float("inf")
    best_prog_cpu: np.ndarray | None = None
    all_byte_hashes: set[str] = set()
    all_expr_sigs: set[str] = set()

    while time.perf_counter() - t0 < budget_sec:
        # Uniform sampling across opcodes [0..15]
        ops = torch.randint(0, 16, (pop_size, N_INSTR), device=device)
        population = encode_program_tensor(ops, device)

        preds, flags = execute_population_torch(population, xs_train, device=device)
        diff = preds - ys_train.unsqueeze(0)
        mse = (diff**2).mean(dim=1)
        invalid = flags.any(dim=1) | torch.isnan(mse) | torch.isinf(mse)
        fit = torch.where(invalid, mse + 1e6, mse)

        min_val, min_idx = torch.min(fit, dim=0)
        if float(min_val.item()) < best_fit:
            best_fit = float(min_val.item())
            best_prog_cpu = population[min_idx].cpu().numpy().astype(np.uint32)

        pop_cpu = population.cpu().numpy().astype(np.uint32)
        for p in pop_cpu:
            all_byte_hashes.add(hashlib.sha256(p.tobytes()).hexdigest())

        sigs = compute_expression_signatures(population, probe_xs, device)
        all_expr_sigs.update(sigs)

        iterations += 1
        total_evals += pop_size
        synchronize(device)

    elapsed = max(1e-6, time.perf_counter() - t0)

    # Evaluate best candidate on held-out test split
    if best_prog_cpu is not None:
        best_t = torch.from_numpy(best_prog_cpu.astype(np.int64)).unsqueeze(0).to(device)
        t_preds, _ = execute_population_torch(best_t, xs_test, device=device)
        held_out_mse = float(((t_preds[0] - ys_test) ** 2).mean().item())
        disasm = decode_human(best_prog_cpu)
        b_hex = best_prog_cpu.tobytes().hex()
    else:
        held_out_mse = float("inf")
        disasm = "NOP"
        b_hex = ""

    return {
        "arm": "uniform",
        "wall_clock_sec": elapsed,
        "iterations": iterations,
        "candidates_evaluated": total_evals,
        "evals_per_sec": total_evals / elapsed,
        "best_train_mse": best_fit,
        "held_out_mse": held_out_mse,
        "distinct_byte_programs": len(all_byte_hashes),
        "distinct_expressions": len(all_expr_sigs),
        "best_disassembly": disasm,
        "best_bytecode_hex": b_hex,
    }


def run_learned_arm(
    *,
    xs_train: torch.Tensor,
    ys_train: torch.Tensor,
    xs_test: torch.Tensor,
    ys_test: torch.Tensor,
    probe_xs: torch.Tensor,
    device: torch.device,
    budget_sec: float,
    pop_size: int = 100,
) -> dict[str, Any]:
    """Arm 2: Simple learned distribution (categorical frequency model with Dirichlet smoothing)."""
    t0 = time.perf_counter()
    iterations = 0
    total_evals = 0
    best_fit = float("inf")
    best_prog_cpu: np.ndarray | None = None
    all_byte_hashes: set[str] = set()
    all_expr_sigs: set[str] = set()

    # Prior counts: Dirichlet smoothing alpha = 1.0
    counts = torch.ones((N_INSTR, 16), dtype=torch.float32, device=device)

    while time.perf_counter() - t0 < budget_sec:
        probs = counts / counts.sum(dim=-1, keepdim=True)
        # Sample opcodes per slot
        ops_by_slot = [
            torch.multinomial(probs[j], pop_size, replacement=True) for j in range(N_INSTR)
        ]
        ops = torch.stack(ops_by_slot, dim=1)
        population = encode_program_tensor(ops, device)

        preds, flags = execute_population_torch(population, xs_train, device=device)
        diff = preds - ys_train.unsqueeze(0)
        mse = (diff**2).mean(dim=1)
        invalid = flags.any(dim=1) | torch.isnan(mse) | torch.isinf(mse)
        fit = torch.where(invalid, mse + 1e6, mse)

        sorted_fit, sorted_idx = torch.sort(fit)
        if float(sorted_fit[0].item()) < best_fit:
            best_fit = float(sorted_fit[0].item())
            best_prog_cpu = population[sorted_idx[0]].cpu().numpy().astype(np.uint32)

        # Update distribution using top 10%
        top_k = max(2, int(0.10 * pop_size))
        top_ops = ops[sorted_idx[:top_k]]
        new_counts = torch.zeros_like(counts)
        for j in range(N_INSTR):
            new_counts[j] = torch.bincount(top_ops[:, j], minlength=16).float()

        counts = 0.85 * counts + 0.15 * (new_counts + 1.0)

        pop_cpu = population.cpu().numpy().astype(np.uint32)
        for p in pop_cpu:
            all_byte_hashes.add(hashlib.sha256(p.tobytes()).hexdigest())

        sigs = compute_expression_signatures(population, probe_xs, device)
        all_expr_sigs.update(sigs)

        iterations += 1
        total_evals += pop_size
        synchronize(device)

    elapsed = max(1e-6, time.perf_counter() - t0)

    if best_prog_cpu is not None:
        best_t = torch.from_numpy(best_prog_cpu.astype(np.int64)).unsqueeze(0).to(device)
        t_preds, _ = execute_population_torch(best_t, xs_test, device=device)
        held_out_mse = float(((t_preds[0] - ys_test) ** 2).mean().item())
        disasm = decode_human(best_prog_cpu)
        b_hex = best_prog_cpu.tobytes().hex()
    else:
        held_out_mse = float("inf")
        disasm = "NOP"
        b_hex = ""

    return {
        "arm": "learned-dist",
        "wall_clock_sec": elapsed,
        "iterations": iterations,
        "candidates_evaluated": total_evals,
        "evals_per_sec": total_evals / elapsed,
        "best_train_mse": best_fit,
        "held_out_mse": held_out_mse,
        "distinct_byte_programs": len(all_byte_hashes),
        "distinct_expressions": len(all_expr_sigs),
        "best_disassembly": disasm,
        "best_bytecode_hex": b_hex,
    }


def run_genetic_arm(
    *,
    xs_train: torch.Tensor,
    ys_train: torch.Tensor,
    xs_test: torch.Tensor,
    ys_test: torch.Tensor,
    probe_xs: torch.Tensor,
    device: torch.device,
    budget_sec: float,
    pop_size: int = 100,
) -> dict[str, Any]:
    """Arm 3: Classical genetic evolution (tournament selection + crossover + mutation)."""
    t0 = time.perf_counter()
    iterations = 0
    total_evals = 0
    best_fit = float("inf")
    best_prog_cpu: np.ndarray | None = None
    all_byte_hashes: set[str] = set()
    all_expr_sigs: set[str] = set()

    cfg = EvolutionConfig(pop_size=pop_size, crossover_p=0.4, elite_k=max(1, int(0.05 * pop_size)))
    population = gpu_sample_structured(pop_size, device=device)

    while time.perf_counter() - t0 < budget_sec:
        preds, flags = execute_population_torch(population, xs_train, device=device)
        diff = preds - ys_train.unsqueeze(0)
        mse = (diff**2).mean(dim=1)
        invalid = flags.any(dim=1) | torch.isnan(mse) | torch.isinf(mse)
        fit = torch.where(invalid, mse + 1e6, mse)

        sorted_fit, sorted_idx = torch.sort(fit)
        sorted_pop = population[sorted_idx]
        if float(sorted_fit[0].item()) < best_fit:
            best_fit = float(sorted_fit[0].item())
            best_prog_cpu = sorted_pop[0].cpu().numpy().astype(np.uint32)

        pop_cpu = population.cpu().numpy().astype(np.uint32)
        for p in pop_cpu:
            all_byte_hashes.add(hashlib.sha256(p.tobytes()).hexdigest())

        sigs = compute_expression_signatures(population, probe_xs, device)
        all_expr_sigs.update(sigs)

        # Breeding for next step
        k_elites = cfg.elite_k
        elites = sorted_pop[:k_elites]
        n_inject = max(2, int(0.10 * pop_size))
        n_offspring = pop_size - k_elites - n_inject
        n_pairs = (n_offspring + 1) // 2

        parents_1 = gpu_tournament_selection(
            sorted_pop, sorted_fit, n_winners=n_pairs, tournament_size=cfg.tournament_size
        )
        parents_2 = gpu_tournament_selection(
            sorted_pop, sorted_fit, n_winners=n_pairs, tournament_size=cfg.tournament_size
        )
        c1, c2 = gpu_crossover_single_point(parents_1, parents_2, crossover_p=cfg.crossover_p)
        offspring = torch.cat([c1, c2], dim=0)[:n_offspring]
        mutated = gpu_mutate(offspring)

        injected = gpu_sample_structured(n_inject, device=device)
        population = torch.cat([elites, mutated, injected], dim=0)[:pop_size]

        iterations += 1
        total_evals += pop_size
        synchronize(device)

    elapsed = max(1e-6, time.perf_counter() - t0)

    if best_prog_cpu is not None:
        best_t = torch.from_numpy(best_prog_cpu.astype(np.int64)).unsqueeze(0).to(device)
        t_preds, _ = execute_population_torch(best_t, xs_test, device=device)
        held_out_mse = float(((t_preds[0] - ys_test) ** 2).mean().item())
        disasm = decode_human(best_prog_cpu)
        b_hex = best_prog_cpu.tobytes().hex()
    else:
        held_out_mse = float("inf")
        disasm = "NOP"
        b_hex = ""

    return {
        "arm": "genetic",
        "wall_clock_sec": elapsed,
        "iterations": iterations,
        "candidates_evaluated": total_evals,
        "evals_per_sec": total_evals / elapsed,
        "best_train_mse": best_fit,
        "held_out_mse": held_out_mse,
        "distinct_byte_programs": len(all_byte_hashes),
        "distinct_expressions": len(all_expr_sigs),
        "best_disassembly": disasm,
        "best_bytecode_hex": b_hex,
    }


def run_amplitude_arm(
    *,
    xs_train: torch.Tensor,
    ys_train: torch.Tensor,
    xs_test: torch.Tensor,
    ys_test: torch.Tensor,
    probe_xs: torch.Tensor,
    device: torch.device,
    budget_sec: float,
    pop_size: int = 100,
) -> dict[str, Any]:
    """Arm 4: Quantum-inspired amplitude-distribution sampling with Q-bit rotation gate."""
    t0 = time.perf_counter()
    iterations = 0
    total_evals = 0
    best_fit = float("inf")
    best_prog_cpu: np.ndarray | None = None
    all_byte_hashes: set[str] = set()
    all_expr_sigs: set[str] = set()

    # Initial Q-bit angles: theta = pi/4 for equal initial amplitudes
    theta = torch.full((N_INSTR, 16), float(math.pi / 4.0), dtype=torch.float32, device=device)
    delta_theta = float(0.05 * math.pi)
    min_theta = float(0.01 * math.pi)
    max_theta = float(0.49 * math.pi)

    while time.perf_counter() - t0 < budget_sec:
        # Sampling probability from quantum amplitude: P = sin^2(theta)
        probs = torch.sin(theta) ** 2
        probs = probs / probs.sum(dim=-1, keepdim=True)

        ops_by_slot = [
            torch.multinomial(probs[j], pop_size, replacement=True) for j in range(N_INSTR)
        ]
        ops = torch.stack(ops_by_slot, dim=1)
        population = encode_program_tensor(ops, device)

        preds, flags = execute_population_torch(population, xs_train, device=device)
        diff = preds - ys_train.unsqueeze(0)
        mse = (diff**2).mean(dim=1)
        invalid = flags.any(dim=1) | torch.isnan(mse) | torch.isinf(mse)
        fit = torch.where(invalid, mse + 1e6, mse)

        sorted_fit, sorted_idx = torch.sort(fit)
        best_candidate_ops = ops[sorted_idx[0]]

        if float(sorted_fit[0].item()) < best_fit:
            best_fit = float(sorted_fit[0].item())
            best_prog_cpu = population[sorted_idx[0]].cpu().numpy().astype(np.uint32)

        # Quantum Rotation Gate update towards best candidate's opcodes
        # For winning opcode k*: theta_jk* += delta_theta
        # For other opcodes: theta_jk -= delta_theta / 15
        for j in range(N_INSTR):
            k_star = int(best_candidate_ops[j].item())
            theta[j] = torch.clamp(theta[j] - (delta_theta / 15.0), min=min_theta, max=max_theta)
            theta[j, k_star] = min(max_theta, float(theta[j, k_star].item() + delta_theta))

        pop_cpu = population.cpu().numpy().astype(np.uint32)
        for p in pop_cpu:
            all_byte_hashes.add(hashlib.sha256(p.tobytes()).hexdigest())

        sigs = compute_expression_signatures(population, probe_xs, device)
        all_expr_sigs.update(sigs)

        iterations += 1
        total_evals += pop_size
        synchronize(device)

    elapsed = max(1e-6, time.perf_counter() - t0)

    if best_prog_cpu is not None:
        best_t = torch.from_numpy(best_prog_cpu.astype(np.int64)).unsqueeze(0).to(device)
        t_preds, _ = execute_population_torch(best_t, xs_test, device=device)
        held_out_mse = float(((t_preds[0] - ys_test) ** 2).mean().item())
        disasm = decode_human(best_prog_cpu)
        b_hex = best_prog_cpu.tobytes().hex()
    else:
        held_out_mse = float("inf")
        disasm = "NOP"
        b_hex = ""

    return {
        "arm": "amplitude-distribution",
        "wall_clock_sec": elapsed,
        "iterations": iterations,
        "candidates_evaluated": total_evals,
        "evals_per_sec": total_evals / elapsed,
        "best_train_mse": best_fit,
        "held_out_mse": held_out_mse,
        "distinct_byte_programs": len(all_byte_hashes),
        "distinct_expressions": len(all_expr_sigs),
        "best_disassembly": disasm,
        "best_bytecode_hex": b_hex,
    }


# ==============================================================================
# Full Multi-Seed A/B Experiment & Statistical Verdict
# ==============================================================================


def run_qrand_experiment(
    *,
    hypothesis_name: str,
    seeds_count: int = 5,
    budget_sec: float = 0.5,
    pop_size: int = 100,
    device_name: str | None = None,
    formula: str = "x2_3x_7",
    output_path: Path,
) -> dict[str, Any]:
    """Execute complete 4-arm A/B comparison across seeds with statistical falsification test."""
    t_start = time.monotonic()
    device = resolve_device(device_name)
    deadline = MonotonicDeadline(budget_sec=600.0)
    deadline.mark_setup_done()

    print(
        f"\nStarting P27 Q-Rand Experiment: hypothesis={hypothesis_name} "
        f"seeds={seeds_count} budget={budget_sec}s/arm device={device}..."
    )

    per_seed_runs: list[dict[str, Any]] = []
    seeds = [42 + i * 17 for i in range(seeds_count)]

    probe_xs = torch.from_numpy(PROBE_POINTS).to(device)

    for seed in seeds:
        print(f"  --- Running Seed {seed} ---")
        seed_all(seed)
        rng = np.random.default_rng(seed)

        # 128 train points, 128 strictly held-out points
        xs_all = rng.uniform(-10.0, 10.0, size=(256,)).astype(np.float32)
        if formula == "x2_3x_7":
            ys_all = (xs_all**2 + 3.0 * xs_all + 7.0).astype(np.float32)
        else:
            ys_all = (xs_all + 1.0).astype(np.float32)

        xs_tr = torch.from_numpy(xs_all[:128]).to(device)
        ys_tr = torch.from_numpy(ys_all[:128]).to(device)
        xs_te = torch.from_numpy(xs_all[128:]).to(device)
        ys_te = torch.from_numpy(ys_all[128:]).to(device)

        # Run 4 arms with exact same budget
        res_uniform = run_uniform_arm(
            xs_train=xs_tr,
            ys_train=ys_tr,
            xs_test=xs_te,
            ys_test=ys_te,
            probe_xs=probe_xs,
            device=device,
            budget_sec=budget_sec,
            pop_size=pop_size,
        )

        res_learned = run_learned_arm(
            xs_train=xs_tr,
            ys_train=ys_tr,
            xs_test=xs_te,
            ys_test=ys_te,
            probe_xs=probe_xs,
            device=device,
            budget_sec=budget_sec,
            pop_size=pop_size,
        )

        res_genetic = run_genetic_arm(
            xs_train=xs_tr,
            ys_train=ys_tr,
            xs_test=xs_te,
            ys_test=ys_te,
            probe_xs=probe_xs,
            device=device,
            budget_sec=budget_sec,
            pop_size=pop_size,
        )

        res_amplitude = run_amplitude_arm(
            xs_train=xs_tr,
            ys_train=ys_tr,
            xs_test=xs_te,
            ys_test=ys_te,
            probe_xs=probe_xs,
            device=device,
            budget_sec=budget_sec,
            pop_size=pop_size,
        )

        per_seed_runs.append(
            {
                "seed": seed,
                "uniform": res_uniform,
                "learned-dist": res_learned,
                "genetic": res_genetic,
                "amplitude-distribution": res_amplitude,
            }
        )

    deadline.mark_warmup_done()

    # Aggregate metrics across seeds
    arms = ["uniform", "learned-dist", "genetic", "amplitude-distribution"]
    aggregates: dict[str, Any] = {}
    for arm in arms:
        held_out_list = [r[arm]["held_out_mse"] for r in per_seed_runs]
        distinct_expr_list = [r[arm]["distinct_expressions"] for r in per_seed_runs]
        cvps_list = [r[arm]["evals_per_sec"] for r in per_seed_runs]

        aggregates[arm] = {
            "mean_held_out_mse": float(np.mean(held_out_list)),
            "std_held_out_mse": float(np.std(held_out_list)),
            "mean_distinct_expressions": float(np.mean(distinct_expr_list)),
            "std_distinct_expressions": float(np.std(distinct_expr_list)),
            "mean_cvps": float(np.mean(cvps_list)),
            "std_cvps": float(np.std(cvps_list)),
        }

    # Hypothesis comparisons vs controls
    q_mse = aggregates["amplitude-distribution"]["mean_held_out_mse"]
    u_mse = aggregates["uniform"]["mean_held_out_mse"]
    l_mse = aggregates["learned-dist"]["mean_held_out_mse"]
    g_mse = aggregates["genetic"]["mean_held_out_mse"]

    q_expr = aggregates["amplitude-distribution"]["mean_distinct_expressions"]
    u_expr = aggregates["uniform"]["mean_distinct_expressions"]
    l_expr = aggregates["learned-dist"]["mean_distinct_expressions"]
    g_expr = aggregates["genetic"]["mean_distinct_expressions"]

    mse_improvement_vs_uniform = (u_mse - q_mse) / max(1e-6, u_mse)
    distinct_expr_ratio_vs_uniform = q_expr / max(1.0, u_expr)

    # Determine falsification verdict against preregistered threshold
    # Prediction: lower held-out MSE (improvement > 0) OR distinct expressions >= 1.15x
    if mse_improvement_vs_uniform > 0.05 and distinct_expr_ratio_vs_uniform >= 1.15:
        verdict = "CONFIRMED"
        verdict_summary = (
            "Amplitude-distribution sampling met both MSE improvement (>5%) "
            "and distinct expression exploration (>=15%) thresholds over uniform search."
        )
    elif distinct_expr_ratio_vs_uniform >= 1.15:
        verdict = "PARTIAL"
        verdict_summary = (
            "Amplitude-distribution significantly expanded distinct expression exploration (>=15%), "
            "but held-out MSE improvement did not reach the primary discovery threshold."
        )
    else:
        verdict = "FALSIFIED_NULL"
        verdict_summary = (
            "Amplitude-distribution sampling did not exceed the preregistered falsification threshold "
            "(MSE gain <= 0 or distinct expression ratio < 1.15). Null result recorded."
        )

    deadline.mark_compute_done()
    timing = deadline.finish()
    elapsed = max(1e-6, time.monotonic() - t_start)

    prov = collect_provenance(
        seed=seeds[0],
        device=device,
        config={
            "hypothesis": hypothesis_name,
            "seeds_count": seeds_count,
            "budget_sec": budget_sec,
            "pop_size": pop_size,
        },
    )

    manifest_data = {
        "phase": "p27-qrand-hypotheses",
        "status": "complete",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        "elapsed_sec": elapsed,
        "hypothesis": {
            "name": hypothesis_name,
            "preregistration_spec": PREREGISTRATION_SPEC.strip(),
            "preregistration_hash": PREREGISTRATION_HASH,
            "literature_check": LITERATURE_NOTE,
        },
        "verdict": verdict,
        "verdict_summary": verdict_summary,
        "comparisons": {
            "mse_improvement_vs_uniform_pct": mse_improvement_vs_uniform * 100.0,
            "distinct_expressions_ratio_vs_uniform": distinct_expr_ratio_vs_uniform,
            "mean_held_out_mse": {
                "amplitude": q_mse,
                "uniform": u_mse,
                "learned": l_mse,
                "genetic": g_mse,
            },
            "mean_distinct_expressions": {
                "amplitude": q_expr,
                "uniform": u_expr,
                "learned": l_expr,
                "genetic": g_expr,
            },
        },
        "aggregates_by_arm": aggregates,
        "per_seed_runs": per_seed_runs,
        "timing": timing,
        "provenance": prov,
    }

    written = write_manifest(output_path, manifest_data, {})
    return written


def main() -> int:
    parser = argparse.ArgumentParser(
        description="P27 Quantum-Inspired Randomness Hypotheses A/B Testing Harness"
    )
    parser.add_argument(
        "--hypothesis",
        type=str,
        default="amplitude-distribution",
        help="Single hypothesis to test (e.g. amplitude-distribution)",
    )
    parser.add_argument(
        "--seeds",
        type=int,
        default=5,
        help="Number of independent seeds to evaluate",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="experiments/p27-qrand-amplitude-distribution.json",
        help="Path to write the checksummed artifact manifest",
    )
    parser.add_argument(
        "--budget-sec",
        type=float,
        default=0.5,
        help="Equal wall-clock budget in seconds per arm per seed",
    )
    parser.add_argument(
        "--pop-size",
        type=int,
        default=100,
        help="Candidate population size per batch",
    )
    parser.add_argument(
        "--device",
        type=str,
        default=None,
        help="Compute device (cuda / cpu)",
    )
    args = parser.parse_args()

    out_path = _REPO_ROOT / args.output
    manifest = run_qrand_experiment(
        hypothesis_name=args.hypothesis,
        seeds_count=args.seeds,
        budget_sec=args.budget_sec,
        pop_size=args.pop_size,
        device_name=args.device,
        output_path=out_path,
    )

    print("\n=== P27 Q-Rand Experiment Completed ===")
    print(f"Manifest: {out_path} (sha256={manifest['manifest_sha256'][:16]}...)")
    print(f"Hypothesis: {manifest['hypothesis']['name']}")
    print(f"Preregistration Hash: {manifest['hypothesis']['preregistration_hash'][:16]}...")
    print(f"Verdict: {manifest['verdict']}")
    print(f"Verdict Summary: {manifest['verdict_summary']}")
    print(
        f"Held-Out MSE: Amplitude={manifest['comparisons']['mean_held_out_mse']['amplitude']:.4f} | "
        f"Uniform={manifest['comparisons']['mean_held_out_mse']['uniform']:.4f} | "
        f"Genetic={manifest['comparisons']['mean_held_out_mse']['genetic']:.4f}"
    )
    print(
        f"Distinct Expressions: Amplitude={manifest['comparisons']['mean_distinct_expressions']['amplitude']:.1f} | "
        f"Uniform={manifest['comparisons']['mean_distinct_expressions']['uniform']:.1f} "
        f"(Ratio: {manifest['comparisons']['distinct_expressions_ratio_vs_uniform']:.2f}x)"
    )
    print(f"Elapsed: {manifest['elapsed_sec']:.2f} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
