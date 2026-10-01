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
import json
import math
import os
import sys
import time
import zlib
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


P37_HYPOTHESIS = "dependency-correlated"

P37_PREREGISTRATION_SPEC = """
HYPOTHESIS: dependency-correlated
PREREGISTRATION DATE: 2026-10-01
MECHANISM (exactly one per cycle): opcode bigram sampling. Slot 0 opcode is drawn
from a start distribution; slot j>0 opcode is drawn conditioned on the opcode
sampled at slot j-1 through a per-slot 16x16 transition law. Same parameter
count, update cadence and wall-clock budget as the matched classical control.
EQUATIONS (proposed arm):
1. Phase state: start angles psi[k], transition angles Phi_j[a,k],
   psi, Phi in [0.01*pi, 0.49*pi].
2. Sampling law: P(k | slot j, prev a) = sin^2(Phi_j[a,k]) / sum_m sin^2(Phi_j[a,m]);
   slot 0 uses psi analogously. Classical implementation on GPU/CPU; no quantum hardware.
3. Rotation-gate update toward elite bigrams (top 10% by train fitness, same as control):
   Phi_j[a,k*] <- min(Phi_j[a,k*] + Delta, 0.49*pi) for each elite pair (a -> k*);
   Phi_j[a,k]  <- max(Phi_j[a,k]  - Delta/15, 0.01*pi) for k != k*;
   Delta = 0.05*pi. Start vector updated analogously toward elite slot-0 opcodes.
MATCHED CLASSICAL CONTROL (same expressive capacity and update budget):
per-slot bigram frequency table with Laplace smoothing (alpha = 1.0):
P(k | j, a) = C_j[a,k] / sum_m C_j[a,m]; update C <- 0.85*C + 0.15*(elite bigram
counts + 1.0) each iteration. Only the update rule differs from the proposed arm.
BASELINE: classical genetic evolution (tournament + crossover + mutation).
PREDICTION: dependency-correlated sampling yields >= 15% higher verified
solutions/sec than the matched classical control on development polynomial tasks.
FALSIFICATION / VERDICT RULE (single frozen rule, no post-hoc OR/AND):
paired differences (proposed minus control) of verified solutions/sec over paired
(task, seed, budget) trials; deterministic percentile bootstrap (2000 resamples,
seed 0) for the 95% CI of the paired mean difference.
GAIN iff relative gain >= 15% AND CI lower bound > 0. LOSS iff relative gain
<= -15% AND CI upper bound < 0. Otherwise NULL. Genetic comparison is descriptive
only and cannot award the verdict.
UNCERTAINTY: paired bootstrap 95% CI as above; means alone never imply significance.
CONTROLS: matched-classical bigram (verdict control), genetic (descriptive baseline).
EVALUATION: paired (task, seed, budget) trials; >= 5 seeds; nominal budgets
10s/1m/10m wall-clock-enforced per arm (effective budgets disclosed via scale factor);
3 development polynomial tasks; independent RNG streams per arm; rotated arm order;
matched warmup; sampling/update/tracing costs billed; final test untouched.
PRIMARY OUTCOMES: verified solutions/sec, censored time-to-certified-solution.
SECONDARY: distinct behavioral expressions (finite probe signatures = behaviors).
"""

P37_PREREGISTRATION_HASH = hashlib.sha256(
    P37_PREREGISTRATION_SPEC.strip().encode("utf-8")
).hexdigest()

P37_LITERATURE_NOTE = {
    "prior_art": [
        {
            "citation": (
                "Han & Kim (2002), Quantum-inspired Evolutionary Algorithm, IEEE TEVC 6(6)"
            ),
            "mechanism": "Q-bit angle representation and rotation-gate update of sampling distributions",
        },
        {
            "citation": (
                "Manning & Schutze (1999), Foundations of Statistical NLP, MIT Press (n-gram "
                "models with Laplace/Lidstone smoothing)"
            ),
            "mechanism": "Classical bigram frequency tables with additive smoothing (matched control)",
        },
        {
            "citation": "EvoByte P27 amplitude-distribution pilot (FALSIFIED_NULL)",
            "mechanism": "Independent per-slot Q-bit rotation showed no gain; motivates testing "
            "dependency (bigram) structure instead of slot independence",
        },
    ],
    "novelty_boundary": (
        "Bigram transition laws with rotation-gate updates applied to register-bytecode "
        "opcode sequences under fixed V0 interpreter constraints. Quantum inspiration is "
        "classical distribution dynamics, not quantum execution, hardware, or advantage."
    ),
}

P37_TASKS = (
    ("quad_offset", "x**2+3*x+7"),
    ("affine", "2*x+5"),
    ("quad_square", "x**2-2*x+1"),
)

P37_ARMS = ("genetic", "matched-classical", "dependency-correlated")

P37_EFFECT_PCT = 15.0
P37_BOOTSTRAP_RESAMPLES = 2000


def _p37_task_grids(formula: str) -> dict[str, Any]:
    """Deterministic train/test/extrapolation grids for a development polynomial task."""
    import sympy as _sympy

    x = _sympy.Symbol("x")
    fn = _sympy.lambdify(x, _sympy.sympify(formula), modules=["numpy"])
    train_xs = np.linspace(-3.0, 3.0, 48, dtype=np.float64)
    test_xs = np.linspace(-2.9, 2.9, 32, dtype=np.float64)
    extrap_xs = np.concatenate([np.linspace(-6.0, -3.5, 16), np.linspace(3.5, 6.0, 16)]).astype(
        np.float64
    )
    return {
        "train_xs": train_xs,
        "train_ys": np.asarray(fn(train_xs), dtype=np.float64),
        "test_xs": test_xs,
        "test_ys": np.asarray(fn(test_xs), dtype=np.float64),
        "extrap_xs": extrap_xs,
        "extrap_ys": np.asarray(fn(extrap_xs), dtype=np.float64),
    }


def _p37_certify_best(
    best_prog: np.ndarray | None, formula: str, grids: dict[str, Any]
) -> dict[str, Any]:
    """P31-style L2 certificate for one candidate program (valid certificates only)."""
    from evobyte.verifier import verify_l2

    if best_prog is None:
        return {"verified": False, "decision": "NO_CANDIDATE", "test_mse": float("inf")}
    prog = np.asarray(best_prog, dtype=np.uint32)
    res = verify_l2(
        prog,
        grids["train_xs"],
        grids["train_ys"],
        grids["test_xs"],
        grids["test_ys"],
        val_xs=grids["test_xs"],
        val_ys=grids["test_ys"],
        extrap_xs=grids["extrap_xs"],
        extrap_ys=grids["extrap_ys"],
        adversarial_xs=grids["extrap_xs"],
        ground_truth_formula=formula,
        error_threshold=1e-4,
        extrap_threshold=1.0,
        domain_str="[-3, 3] train; [-6, -3.5]U[3.5, 6] extrap",
    )
    return {"verified": bool(res.passed), "decision": res.decision, "test_mse": res.f64_test_mse}


def _p37_sample_bigram(
    start_p: torch.Tensor, trans_p: list[torch.Tensor], pop_size: int, device: torch.device
) -> torch.Tensor:
    """Sample opcode sequences from start + per-slot transition laws."""
    ops = torch.empty((pop_size, N_INSTR), dtype=torch.int64, device=device)
    ops[:, 0] = torch.multinomial(start_p, pop_size, replacement=True)
    for j in range(1, N_INSTR):
        rows = trans_p[j - 1][ops[:, j - 1]]
        ops[:, j] = torch.multinomial(rows, 1, replacement=True).squeeze(1)
    return ops


def _p37_elite_bigrams(
    ops: torch.Tensor, sorted_idx: torch.Tensor, pop_size: int
) -> tuple[torch.Tensor, torch.Tensor]:
    """Slot-0 opcodes and (prev, next) pairs of the elite top 10% sequences."""
    top_k = max(2, int(0.10 * pop_size))
    top = ops[sorted_idx[:top_k]]
    pairs = torch.stack([top[:, :-1].reshape(-1), top[:, 1:].reshape(-1)], dim=1)
    return top[:, 0], pairs


def run_bigram_arm(
    *,
    arm: str,
    xs_train: torch.Tensor,
    ys_train: torch.Tensor,
    probe_xs: torch.Tensor,
    device: torch.device,
    budget_sec: float,
    pop_size: int = 100,
    gt_formula: str = "x**2+3*x+7",
    grids: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """One controlled bigram arm: matched-classical (Laplace) or dependency-correlated.

    Identical loop, parameter count, update cadence and billing; only the
    representation and update rule differ (the single-mechanism intervention).
    """
    assert arm in ("matched-classical", "dependency-correlated"), arm
    quantum = arm == "dependency-correlated"
    t0 = time.perf_counter()
    sample_sec = 0.0
    eval_sec = 0.0
    update_sec = 0.0
    trace_sec = 0.0
    iterations = 0
    total_evals = 0
    best_fit = float("inf")
    best_prog_cpu: np.ndarray | None = None
    first_sub_sec: float | None = None
    all_byte_hashes: set[str] = set()
    all_expr_sigs: set[str] = set()

    delta = float(0.05 * math.pi)
    lo = float(0.01 * math.pi)
    hi = float(0.49 * math.pi)
    if quantum:
        start = torch.full((16,), float(math.pi / 4.0), dtype=torch.float32, device=device)
        trans = [
            torch.full((16, 16), float(math.pi / 4.0), dtype=torch.float32, device=device)
            for _ in range(N_INSTR - 1)
        ]
    else:
        start = torch.ones((16,), dtype=torch.float32, device=device)
        trans = [
            torch.ones((16, 16), dtype=torch.float32, device=device) for _ in range(N_INSTR - 1)
        ]

    # Matched warmup: one untimed-setup evaluation billed separately, identical code.
    t_warm_0 = time.perf_counter()
    with torch.no_grad():
        _w_ops = torch.randint(0, 16, (pop_size, N_INSTR), device=device)
        _w_pop = encode_program_tensor(_w_ops, device)
        _w_preds, _ = execute_population_torch(_w_pop, xs_train, device=device)
        synchronize(device)
    warmup_sec = time.perf_counter() - t_warm_0

    while time.perf_counter() - t0 < budget_sec:
        t_s_0 = time.perf_counter()
        if quantum:
            start_p = torch.sin(start) ** 2
            start_p = start_p / start_p.sum()
            trans_p = []
            for mat in trans:
                sq = torch.sin(mat) ** 2
                trans_p.append(sq / sq.sum(dim=-1, keepdim=True))
        else:
            start_p = start / start.sum()
            trans_p = [mat / mat.sum(dim=-1, keepdim=True) for mat in trans]
        ops = _p37_sample_bigram(start_p, trans_p, pop_size, device)
        population = encode_program_tensor(ops, device)
        sample_sec += time.perf_counter() - t_s_0

        t_e_0 = time.perf_counter()
        preds, flags = execute_population_torch(population, xs_train, device=device)
        diff = preds - ys_train.unsqueeze(0)
        mse = (diff**2).mean(dim=1)
        invalid = flags.any(dim=1) | torch.isnan(mse) | torch.isinf(mse)
        fit = torch.where(invalid, mse + 1e6, mse)
        sorted_fit, sorted_idx = torch.sort(fit)
        eval_sec += time.perf_counter() - t_e_0

        if float(sorted_fit[0].item()) < best_fit:
            best_fit = float(sorted_fit[0].item())
            best_prog_cpu = population[sorted_idx[0]].cpu().numpy().astype(np.uint32)
        if first_sub_sec is None and best_fit <= 1e-4:
            first_sub_sec = time.perf_counter() - t0

        t_u_0 = time.perf_counter()
        slot0, pairs = _p37_elite_bigrams(ops, sorted_idx, pop_size)
        if quantum:
            start = torch.clamp(start - (delta / 15.0), min=lo, max=hi)
            start[slot0] = torch.clamp(start[slot0] + delta, min=lo, max=hi)
            for j in range(N_INSTR - 1):
                mat = trans[j]
                mat = torch.clamp(mat - (delta / 15.0), min=lo, max=hi)
                for a, k in pairs.tolist():
                    mat[a, k] = min(hi, float(mat[a, k].item()) + delta)
                trans[j] = mat
        else:
            new_start = torch.bincount(slot0, minlength=16).float()
            start = 0.85 * start + 0.15 * (new_start + 1.0)
            for j in range(N_INSTR - 1):
                new_mat = torch.zeros_like(trans[j])
                for a, k in pairs.tolist():
                    new_mat[a, k] += 1.0
                trans[j] = 0.85 * trans[j] + 0.15 * (new_mat + 1.0)
        update_sec += time.perf_counter() - t_u_0

        t_t_0 = time.perf_counter()
        pop_cpu = population.cpu().numpy().astype(np.uint32)
        for p in pop_cpu:
            all_byte_hashes.add(hashlib.sha256(p.tobytes()).hexdigest())
        all_expr_sigs.update(compute_expression_signatures(population, probe_xs, device))
        trace_sec += time.perf_counter() - t_t_0

        iterations += 1
        total_evals += pop_size
        synchronize(device)

    elapsed = max(1e-6, time.perf_counter() - t0)
    cert = _p37_certify_best(best_prog_cpu, gt_formula, grids or _p37_task_grids(gt_formula))
    time_to_cert = first_sub_sec if (cert["verified"] and first_sub_sec is not None) else None
    return {
        "arm": arm,
        "wall_clock_sec": elapsed,
        "warmup_sec": warmup_sec,
        "sample_sec": sample_sec,
        "eval_sec": eval_sec,
        "update_sec": update_sec,
        "trace_sec": trace_sec,
        "iterations": iterations,
        "candidates_evaluated": total_evals,
        "evals_per_sec": total_evals / elapsed,
        "best_train_mse": best_fit,
        "distinct_byte_programs": len(all_byte_hashes),
        "distinct_expressions": len(all_expr_sigs),
        "certificate": cert["decision"],
        "verified": cert["verified"],
        "verified_per_sec": (1.0 if cert["verified"] else 0.0) / elapsed,
        "time_to_certified_sec": time_to_cert,
        "censored": cert["verified"] is False,
        "best_disassembly": decode_human(best_prog_cpu) if best_prog_cpu is not None else "NOP",
    }


def run_p37_genetic_arm(
    *,
    xs_train: torch.Tensor,
    ys_train: torch.Tensor,
    probe_xs: torch.Tensor,
    device: torch.device,
    budget_sec: float,
    pop_size: int = 100,
    gt_formula: str = "x**2+3*x+7",
    grids: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """P37 descriptive genetic baseline with the same scaffolding, billing and certificate."""
    t0 = time.perf_counter()
    sample_sec = 0.0
    eval_sec = 0.0
    update_sec = 0.0
    trace_sec = 0.0
    iterations = 0
    total_evals = 0
    best_fit = float("inf")
    best_prog_cpu: np.ndarray | None = None
    first_sub_sec: float | None = None
    all_byte_hashes: set[str] = set()
    all_expr_sigs: set[str] = set()

    cfg = EvolutionConfig(pop_size=pop_size, crossover_p=0.4, elite_k=max(1, int(0.05 * pop_size)))

    t_warm_0 = time.perf_counter()
    with torch.no_grad():
        _w_pop = gpu_sample_structured(pop_size, device=device)
        _w_preds, _ = execute_population_torch(_w_pop, xs_train, device=device)
        synchronize(device)
    warmup_sec = time.perf_counter() - t_warm_0

    population = gpu_sample_structured(pop_size, device=device)
    while time.perf_counter() - t0 < budget_sec:
        t_e_0 = time.perf_counter()
        preds, flags = execute_population_torch(population, xs_train, device=device)
        diff = preds - ys_train.unsqueeze(0)
        mse = (diff**2).mean(dim=1)
        invalid = flags.any(dim=1) | torch.isnan(mse) | torch.isinf(mse)
        fit = torch.where(invalid, mse + 1e6, mse)
        sorted_fit, sorted_idx = torch.sort(fit)
        sorted_pop = population[sorted_idx]
        eval_sec += time.perf_counter() - t_e_0

        if float(sorted_fit[0].item()) < best_fit:
            best_fit = float(sorted_fit[0].item())
            best_prog_cpu = sorted_pop[0].cpu().numpy().astype(np.uint32)
        if first_sub_sec is None and best_fit <= 1e-4:
            first_sub_sec = time.perf_counter() - t0

        t_u_0 = time.perf_counter()
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
        t_s_0 = time.perf_counter()
        injected = gpu_sample_structured(n_inject, device=device)
        sample_sec += time.perf_counter() - t_s_0
        population = torch.cat([elites, mutated, injected], dim=0)[:pop_size]
        update_sec += time.perf_counter() - t_u_0

        t_t_0 = time.perf_counter()
        pop_cpu = population.cpu().numpy().astype(np.uint32)
        for p in pop_cpu:
            all_byte_hashes.add(hashlib.sha256(p.tobytes()).hexdigest())
        all_expr_sigs.update(compute_expression_signatures(population, probe_xs, device))
        trace_sec += time.perf_counter() - t_t_0

        iterations += 1
        total_evals += pop_size
        synchronize(device)

    elapsed = max(1e-6, time.perf_counter() - t0)
    cert = _p37_certify_best(best_prog_cpu, gt_formula, grids or _p37_task_grids(gt_formula))
    time_to_cert = first_sub_sec if (cert["verified"] and first_sub_sec is not None) else None
    return {
        "arm": "genetic",
        "wall_clock_sec": elapsed,
        "warmup_sec": warmup_sec,
        "sample_sec": sample_sec,
        "eval_sec": eval_sec,
        "update_sec": update_sec,
        "trace_sec": trace_sec,
        "iterations": iterations,
        "candidates_evaluated": total_evals,
        "evals_per_sec": total_evals / elapsed,
        "best_train_mse": best_fit,
        "distinct_byte_programs": len(all_byte_hashes),
        "distinct_expressions": len(all_expr_sigs),
        "certificate": cert["decision"],
        "verified": cert["verified"],
        "verified_per_sec": (1.0 if cert["verified"] else 0.0) / elapsed,
        "time_to_certified_sec": time_to_cert,
        "censored": cert["verified"] is False,
        "best_disassembly": decode_human(best_prog_cpu) if best_prog_cpu is not None else "NOP",
    }


def _p37_bootstrap_ci(diffs: np.ndarray, resamples: int = 2000) -> tuple[float, float]:
    """Deterministic percentile bootstrap 95% CI of the paired mean difference."""
    rng = np.random.default_rng(0)
    n = len(diffs)
    means = np.empty(resamples, dtype=np.float64)
    for i in range(resamples):
        means[i] = float(np.mean(rng.choice(diffs, size=n, replace=True)))
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def run_controlled_qrand(
    *,
    hypothesis: str = P37_HYPOTHESIS,
    budgets_str: str = "10s,1m,10m",
    seeds_count: int = 5,
    scale_factor: float = 0.05,
    device_name: str | None = None,
    output_path: Path,
    smoke: bool = False,
    pop_size: int = 100,
) -> dict[str, Any]:
    """Execute the P37 controlled single-mechanism experiment with matched control."""
    if hypothesis != P37_HYPOTHESIS:
        raise ValueError(
            f"Unsupported P37 hypothesis {hypothesis!r}; exactly one mechanism per cycle: "
            f"{P37_HYPOTHESIS!r} (new mechanisms require a new preregistration and branch)."
        )
    from evobyte.provenance import parse_budget_duration

    t_start = time.monotonic()
    device = resolve_device(device_name)
    torch.set_num_threads(8)

    print(
        f"\nStarting P37 Controlled Q-Rand: hypothesis={hypothesis} "
        f"budgets={budgets_str} (scale={scale_factor}) seeds={seeds_count} device={device}..."
    )

    if smoke:
        parsed_budgets: list[tuple[str, float]] = [("smoke", 0.3)]
        tasks = P37_TASKS[:1]
        seeds = [42]
        pop_size = 32
    else:
        parsed_budgets = [
            (b.strip(), max(0.2, parse_budget_duration(b.strip()) * scale_factor))
            for b in budgets_str.split(",")
            if b.strip()
        ]
        tasks = P37_TASKS
        seeds = [42 + i * 17 for i in range(seeds_count)]

    probe_xs = torch.from_numpy(PROBE_POINTS).to(device)
    trials: list[dict[str, Any]] = []

    for b_label, b_sec in parsed_budgets:
        for t_idx, (task_key, formula) in enumerate(tasks):
            grids = _p37_task_grids(formula)
            xs_tr = torch.from_numpy(grids["train_xs"].astype(np.float32)).to(device)
            ys_tr = torch.from_numpy(grids["train_ys"].astype(np.float32)).to(device)
            for s_idx, seed in enumerate(seeds):
                # Rotated arm order; independent RNG streams per arm.
                order = ["genetic", "matched-classical", "dependency-correlated"]
                rot = (t_idx + s_idx) % len(order)
                order = order[rot:] + order[:rot]
                results: dict[str, Any] = {}
                for a_idx, arm in enumerate(order):
                    stream = (
                        seed * 131
                        + a_idx * 7919
                        + t_idx * 104729
                        + zlib.crc32(b_label.encode("utf-8")) % 1000
                    )
                    seed_all(stream % (2**32))
                    torch.manual_seed(stream % (2**32))
                    if arm == "genetic":
                        results[arm] = run_p37_genetic_arm(
                            xs_train=xs_tr,
                            ys_train=ys_tr,
                            probe_xs=probe_xs,
                            device=device,
                            budget_sec=b_sec,
                            pop_size=pop_size,
                            gt_formula=formula,
                            grids=grids,
                        )
                    else:
                        results[arm] = run_bigram_arm(
                            arm=arm,
                            xs_train=xs_tr,
                            ys_train=ys_tr,
                            probe_xs=probe_xs,
                            device=device,
                            budget_sec=b_sec,
                            pop_size=pop_size,
                            gt_formula=formula,
                            grids=grids,
                        )
                trials.append(
                    {
                        "budget_label": b_label,
                        "budget_sec": b_sec,
                        "task": task_key,
                        "formula": formula,
                        "seed": seed,
                        "arm_order": order,
                        **{f"{a}": results[a] for a in P37_ARMS},
                    }
                )
                print(
                    f"  [{b_label}] {task_key} seed={seed}: "
                    + " | ".join(
                        f"{a}={'CERT' if results[a]['verified'] else 'miss'}" for a in P37_ARMS
                    )
                )

    # Paired analysis: proposed minus matched-classical verified/sec per trial.
    diffs = np.array(
        [
            t["dependency-correlated"]["verified_per_sec"]
            - t["matched-classical"]["verified_per_sec"]
            for t in trials
        ],
        dtype=np.float64,
    )
    ctrl_mean = float(np.mean([t["matched-classical"]["verified_per_sec"] for t in trials]))
    prop_mean = float(np.mean([t["dependency-correlated"]["verified_per_sec"] for t in trials]))
    rel_gain = (prop_mean - ctrl_mean) / max(ctrl_mean, 1e-12) * 100.0
    ci_lo, ci_hi = _p37_bootstrap_ci(diffs, P37_BOOTSTRAP_RESAMPLES)

    if rel_gain >= P37_EFFECT_PCT and ci_lo > 0.0:
        verdict = "GAIN"
        verdict_summary = (
            f"Dependency-correlated bigram sampling gains {rel_gain:.1f}% verified "
            f"solutions/sec over the matched classical bigram (95% CI [{ci_lo:.4f}, "
            f"{ci_hi:.4f}] excludes 0). Nominated for independent confirmation in P38."
        )
    elif rel_gain <= -P37_EFFECT_PCT and ci_hi < 0.0:
        verdict = "LOSS"
        verdict_summary = (
            f"Dependency-correlated sampling loses {abs(rel_gain):.1f}% verified "
            f"solutions/sec vs the matched control (95% CI [{ci_lo:.4f}, {ci_hi:.4f}] "
            "excludes 0). Mechanism rejected; baseline selected."
        )
    else:
        verdict = "NULL"
        verdict_summary = (
            f"No preregistered effect: relative gain {rel_gain:.1f}% with 95% CI "
            f"[{ci_lo:.4f}, {ci_hi:.4f}]. Sound null completes the cycle; baseline selected."
        )

    def _arm_agg(arm: str) -> dict[str, Any]:
        recs = [t[arm] for t in trials]
        ttcs = [r["time_to_certified_sec"] for r in recs if r["time_to_certified_sec"] is not None]
        return {
            "trials": len(recs),
            "cert_fraction": float(np.mean([1.0 if r["verified"] else 0.0 for r in recs])),
            "mean_verified_per_sec": float(np.mean([r["verified_per_sec"] for r in recs])),
            "median_time_to_certified_sec": float(np.median(ttcs)) if ttcs else None,
            "censored_trials": sum(1 for r in recs if r["censored"]),
            "mean_distinct_expressions": float(np.mean([r["distinct_expressions"] for r in recs])),
            "mean_update_sec": float(np.mean([r["update_sec"] for r in recs])),
            "mean_sample_sec": float(np.mean([r["sample_sec"] for r in recs])),
            "mean_trace_sec": float(np.mean([r["trace_sec"] for r in recs])),
            "mean_warmup_sec": float(np.mean([r["warmup_sec"] for r in recs])),
        }

    elapsed = max(1e-6, time.monotonic() - t_start)
    prov = collect_provenance(
        seed=seeds[0],
        device=device,
        dataset_hashes={"p37_tasks": hashlib.sha256(str(P37_TASKS).encode()).hexdigest()[:16]},
        config={
            "hypothesis": hypothesis,
            "budgets": budgets_str,
            "scale": scale_factor,
            "seeds": seeds,
            "tasks": [k for k, _ in tasks],
        },
    )
    manifest_data = {
        "phase": "p37-controlled-qrand",
        "status": "complete",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        "elapsed_sec": elapsed,
        "hypothesis": {
            "name": hypothesis,
            "preregistration_spec": P37_PREREGISTRATION_SPEC.strip(),
            "preregistration_hash": P37_PREREGISTRATION_HASH,
            "literature_check": P37_LITERATURE_NOTE,
        },
        "preregistration": {
            "effect_pct": P37_EFFECT_PCT,
            "uncertainty": f"paired percentile bootstrap 95% CI, {P37_BOOTSTRAP_RESAMPLES} resamples, seed 0",
            "budgets_nominal": budgets_str,
            "budgets_effective_sec": [[b, s] for b, s in parsed_budgets],
            "seeds": seeds,
            "tasks": [{"key": k, "formula": f} for k, f in tasks],
            "arms": list(P37_ARMS),
            "rng": "independent per-arm streams; rotated arm order; matched warmup/pop/verify",
        },
        "verdict": verdict,
        "verdict_summary": verdict_summary,
        "comparisons": {
            "relative_gain_vs_matched_pct": rel_gain,
            "paired_diff_ci95": [ci_lo, ci_hi],
            "mean_verified_per_sec": {
                "proposed": prop_mean,
                "matched_classical": ctrl_mean,
            },
        },
        "aggregates_by_arm": {a: _arm_agg(a) for a in P37_ARMS},
        "provenance": prov,
    }

    raw_path = output_path.parent / (output_path.stem + "-raw.json")
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(trials, f, indent=2, sort_keys=True, default=str)
    raw_hash = hashlib.sha256(raw_path.read_bytes()).hexdigest()
    try:
        raw_ref = str(raw_path.relative_to(_REPO_ROOT))
    except ValueError:
        raw_ref = str(raw_path)
    written = write_manifest(output_path, manifest_data, {raw_ref: raw_hash})
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
        "--controlled",
        action="store_true",
        help="Run the P37 controlled single-mechanism protocol with matched control",
    )
    parser.add_argument(
        "--budgets",
        type=str,
        default="10s,1m,10m",
        help="Comma-separated nominal wall-clock budgets per arm (P37 controlled mode)",
    )
    parser.add_argument(
        "--scale-budgets",
        type=float,
        default=float(os.environ.get("EVOBYTE_SUSTAINED_SCALE", "1.0")),
        help="Scale factor applied to nominal budgets (P37 controlled mode)",
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

    if args.controlled:
        scale = (
            0.05
            if (args.scale_budgets == 1.0 and not os.environ.get("EVOBYTE_SUSTAINED_SCALE"))
            else args.scale_budgets
        )
        out_path = _REPO_ROOT / args.output
        if out_path.name.startswith("p27"):
            out_path = out_path.parent / "p37-qrand-dependency-correlated.json"
        manifest = run_controlled_qrand(
            hypothesis=args.hypothesis,
            budgets_str=args.budgets,
            seeds_count=args.seeds,
            scale_factor=scale,
            device_name=args.device,
            output_path=out_path,
            smoke=False,
            pop_size=args.pop_size,
        )
        print("\n=== P37 Controlled Q-Rand Completed ===")
        print(f"Manifest: {out_path} (sha256={manifest['manifest_sha256'][:16]}...)")
        print(f"Hypothesis: {manifest['hypothesis']['name']}")
        print(f"Preregistration Hash: {manifest['hypothesis']['preregistration_hash'][:16]}...")
        print(f"Verdict: {manifest['verdict']}")
        print(f"Verdict Summary: {manifest['verdict_summary']}")
        print(f"Elapsed: {manifest['elapsed_sec']:.2f} s")
        return 0

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
