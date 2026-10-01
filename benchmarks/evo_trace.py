"""P26 — Reproducible tracing and exploration map.

Makes every evolutionary run reconstructible and every accepted solution explainable:
1. Full per-run lineage schema (problem, method, config, bytecode version, sampler state,
   batches, results, rejections, promotion ancestry).
2. Aggregate tracing (million-scale runs) + Audit mode (small campaigns, all candidates retained).
3. Replay verifier: bit-exact reconstruction of trajectories from (commit, config, seed).
4. Exploration map: multidimensional bucketing by structure, ops, length, behavior, and quality,
   accounting for distinct byte programs vs distinct mathematical expressions.
5. Tracing-overhead accounting: measures tracing cost against no-tracing baseline on the bill.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import math
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import torch

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "src"))

from evobyte.bytecode import (
    N_INSTR,
    OPCODES,
    decode_human,
    decode_instr,
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
    gpu_sample_pure,
    gpu_sample_structured,
)
from evobyte.vm_torch import execute_population_torch

# Probe points for behavioral signature (distinct mathematical expressions)
PROBE_POINTS = np.array([-5.0, -2.0, -1.0, 0.0, 1.0, 2.0, 5.0, 10.0], dtype=np.float32)


@dataclass
class CandidateAncestry:
    """Record explaining the origin and lineage of a promoted candidate."""

    candidate_id: str
    generation: int
    parent_ids: list[str]
    operator: str  # "init", "elite", "crossover+mutation", "mutation", "injection"
    bytecode_hex: str
    bytecode_sha256: str
    disassembly: str
    fitness: float
    mse: float
    metrics: dict[str, Any]
    ancestry_chain: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GenerationRecord:
    """Per-generation aggregate trace record."""

    generation: int
    batch_hash: str
    generated_count: int
    valid_count: int
    distinct_count: int
    best_fitness: float
    best_mse: float
    best_candidate_id: str
    promoted_count: int
    rejection_summary: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LineageRecord:
    """Complete lineage record for an evolutionary run."""

    run_id: str
    problem: dict[str, Any]
    method: str
    bytecode_version: int
    config: dict[str, Any]
    sampler_state: dict[str, Any]
    generations: list[GenerationRecord]
    promoted_ancestry: list[CandidateAncestry]
    audit_store: list[dict[str, Any]] | None
    summary: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "problem": self.problem,
            "method": self.method,
            "bytecode_version": self.bytecode_version,
            "config": self.config,
            "sampler_state": self.sampler_state,
            "generations": [g.to_dict() for g in self.generations],
            "promoted_ancestry": [a.to_dict() for a in self.promoted_ancestry],
            "audit_store_count": len(self.audit_store) if self.audit_store is not None else 0,
            "audit_store_sample": self.audit_store[:10] if self.audit_store is not None else None,
            "summary": self.summary,
        }


# ==============================================================================
# Helper Functions: Metric & Behavior Extraction
# ==============================================================================


def extract_candidate_metrics(program: np.ndarray) -> dict[str, Any]:
    """Compute structural and opcode metrics for a 16-word bytecode array."""
    ops: list[str] = []
    n_nops = 0
    non_nop_count = 0
    registers_used: set[int] = set()

    for word in program:
        op, dst, a, b = decode_instr(int(word))
        op_name = OPCODES.get(op, f"OP{op:#x}")
        ops.append(op_name)
        if op == 0x00:
            n_nops += 1
        else:
            non_nop_count += 1
            registers_used.add(dst)
            registers_used.add(a)
            if op != 0x0F:  # not constant load
                registers_used.add(b)

    return {
        "length_total": N_INSTR,
        "length_active": non_nop_count,
        "n_nops": n_nops,
        "nop_fraction": n_nops / N_INSTR,
        "registers_used_count": len(registers_used),
        "ops": ops,
    }


def compute_behavioral_signature(
    program: torch.Tensor,
    probe_xs: torch.Tensor,
    device: torch.device,
) -> tuple[str, str]:
    """Evaluate candidate on fixed probe points to extract mathematical fingerprint and behavior."""
    prog_batch = program.unsqueeze(0)
    with torch.no_grad():
        preds, flags = execute_population_torch(prog_batch, probe_xs, device=device)
    vals = preds[0].cpu().numpy()
    has_flag = bool(flags[0].any().item())

    if has_flag or np.any(np.isnan(vals)) or np.any(np.isinf(vals)):
        behavior = "contains_nan_inf"
        sig = "invalid_behavior"
    else:
        var = float(np.var(vals))
        diffs = np.diff(vals)
        if var < 1e-5:
            behavior = "constant_output"
        elif np.all(diffs >= -1e-6) or np.all(diffs <= 1e-6):
            behavior = "monotonic"
        else:
            behavior = "finite_valid"
        # Discretize probe values to 4 decimals for equivalence class grouping
        rounded = np.round(vals, 4)
        sig = hashlib.sha256(rounded.tobytes()).hexdigest()[:16]

    return sig, behavior


def classify_structure(metrics: dict[str, Any]) -> str:
    """Classify instruction organization into structural patterns."""
    nop_f = metrics["nop_fraction"]
    active = metrics["length_active"]
    ops = metrics["ops"]

    if nop_f > 0.5:
        return "nop_heavy"
    elif nop_f <= 0.25:
        return "dense"
    elif "CSEL" in ops or any(op in ("MIN", "MAX") for op in ops):
        return "branching_ops"
    elif active <= 4:
        return "short_linear"
    else:
        return "standard_arithmetic"


def classify_quality(mse: float) -> str:
    """Classify fitness/MSE into hierarchical quality tiers."""
    if math.isnan(mse) or math.isinf(mse) or mse >= 1e5:
        return "tier_invalid"
    elif mse < 1e-4:
        return "tier_0_discovery"
    elif mse < 1e-2:
        return "tier_1_near"
    elif mse < 1.0:
        return "tier_2_coarse"
    else:
        return "tier_3_poor"


# ==============================================================================
# Lineage Evolutionary Runner
# ==============================================================================


def run_lineage_evolution(
    *,
    seed: int,
    pop_size: int = 200,
    n_generations: int = 15,
    n_points: int = 128,
    formula: str = "x2_3x_7",
    audit_mode: bool = False,
    device_name: str | None = None,
) -> LineageRecord:
    """Run resident evolution with complete lineage and ancestry tracking."""
    seed_all(seed)
    device = resolve_device(device_name)

    # 1. Dataset setup
    rng = np.random.default_rng(seed)
    xs_np = rng.uniform(-10.0, 10.0, size=(n_points,)).astype(np.float32)
    if formula == "x2_3x_7":
        ys_np = (xs_np**2 + 3.0 * xs_np + 7.0).astype(np.float32)
    elif formula == "sin_x2":
        ys_np = (np.sin(xs_np) + xs_np**2).astype(np.float32)
    else:
        ys_np = (xs_np + 1.0).astype(np.float32)

    data_hash = hashlib.sha256(xs_np.tobytes() + ys_np.tobytes()).hexdigest()
    xs = torch.from_numpy(xs_np).to(device)
    ys = torch.from_numpy(ys_np).to(device)
    probe_xs = torch.from_numpy(PROBE_POINTS).to(device)

    config = EvolutionConfig(
        pop_size=pop_size,
        crossover_p=0.4,
        elite_k=max(1, int(0.05 * pop_size)),
        random_inject_p=0.10,
    )

    # 2. Initial population & lineage state
    population = gpu_sample_structured(pop_size, device=device)
    candidate_ids = [f"c_g0_i{i}" for i in range(pop_size)]
    candidate_parents: dict[str, list[str]] = {cid: [] for cid in candidate_ids}
    candidate_operators: dict[str, str] = {cid: "init" for cid in candidate_ids}

    ancestry_vault: dict[str, CandidateAncestry] = {}
    audit_store: list[dict[str, Any]] | None = [] if audit_mode else None
    generations_records: list[GenerationRecord] = []

    best_overall_fit = float("inf")
    best_overall_cid = ""

    for gen in range(n_generations):
        # Batch hash
        pop_bytes = population.cpu().numpy().tobytes()
        batch_hash = hashlib.sha256(pop_bytes).hexdigest()

        # Evaluation on device
        preds, flags = execute_population_torch(population, xs, device=device)
        diff = preds - ys.unsqueeze(0)
        mse_tensor = (diff**2).mean(dim=1)
        invalid = flags.any(dim=1) | torch.isnan(mse_tensor) | torch.isinf(mse_tensor)
        fitness_tensor = torch.where(invalid, mse_tensor + 1e6, mse_tensor)

        sorted_fit, sorted_idx = torch.sort(fitness_tensor)
        sorted_pop = population[sorted_idx]
        sorted_mse = mse_tensor[sorted_idx]
        sorted_cids = [candidate_ids[int(i.item())] for i in sorted_idx]

        gen_best_fit = float(sorted_fit[0].item())
        gen_best_mse = float(sorted_mse[0].item())
        gen_best_cid = sorted_cids[0]

        # Audit store (if enabled)
        if audit_store is not None:
            pop_cpu = population.cpu().numpy().astype(np.uint32)
            fit_cpu = fitness_tensor.cpu().numpy()
            for idx_c in range(pop_size):
                cid = candidate_ids[idx_c]
                sha = hashlib.sha256(pop_cpu[idx_c].tobytes()).hexdigest()
                audit_store.append(
                    {
                        "candidate_id": cid,
                        "generation": gen,
                        "parent_ids": candidate_parents.get(cid, []),
                        "operator": candidate_operators.get(cid, "unknown"),
                        "bytecode_sha256": sha,
                        "fitness": float(fit_cpu[idx_c]),
                        "is_promoted": cid == gen_best_cid,
                    }
                )

        # Check for promotion (new best or iteration elite)
        promoted_this_gen = 0
        if gen_best_fit < best_overall_fit:
            best_overall_fit = gen_best_fit
            best_overall_cid = gen_best_cid
            promoted_this_gen += 1

            best_prog = sorted_pop[0].cpu().numpy().astype(np.uint32)
            prog_bytes = best_prog.tobytes()
            b_hex = prog_bytes.hex()
            b_sha = hashlib.sha256(prog_bytes).hexdigest()
            disasm = decode_human(best_prog)
            metrics = extract_candidate_metrics(best_prog)

            # Trace ancestry chain back to generation 0
            chain = [gen_best_cid]
            curr = gen_best_cid
            while curr in ancestry_vault and ancestry_vault[curr].parent_ids:
                parent = ancestry_vault[curr].parent_ids[0]
                chain.append(parent)
                curr = parent

            ancestry_entry = CandidateAncestry(
                candidate_id=gen_best_cid,
                generation=gen,
                parent_ids=candidate_parents.get(gen_best_cid, []),
                operator=candidate_operators.get(gen_best_cid, "elite"),
                bytecode_hex=b_hex,
                bytecode_sha256=b_sha,
                disassembly=disasm,
                fitness=gen_best_fit,
                mse=gen_best_mse,
                metrics=metrics,
                ancestry_chain=chain,
            )
            ancestry_vault[gen_best_cid] = ancestry_entry

        # Record generation summary
        n_invalid = int(invalid.sum().item())
        distinct_count = int(torch.unique(population, dim=0).shape[0])
        gen_record = GenerationRecord(
            generation=gen,
            batch_hash=batch_hash,
            generated_count=pop_size,
            valid_count=pop_size - n_invalid,
            distinct_count=distinct_count,
            best_fitness=gen_best_fit,
            best_mse=gen_best_mse,
            best_candidate_id=gen_best_cid,
            promoted_count=promoted_this_gen,
            rejection_summary={
                "invalid_math_or_flags": n_invalid,
                "loss_above_threshold": int((mse_tensor >= 1e5).sum().item()),
            },
        )
        generations_records.append(gen_record)

        if gen == n_generations - 1:
            break

        # Selection & Reproduction for next generation
        k_elites = min(config.elite_k, pop_size)
        elites = sorted_pop[:k_elites]
        elite_cids = sorted_cids[:k_elites]

        n_inject = max(
            int(np.ceil(config.random_inject_p * pop_size)),
            int(np.ceil(0.10 * pop_size)),
        )
        n_pure = n_inject // 2
        n_struct = n_inject - n_pure
        n_offspring = pop_size - k_elites - n_inject
        n_pairs = (n_offspring + 1) // 2
        pool_size = max(4, min(pop_size, max(20, int(0.25 * pop_size))))

        # Tournament selection with index tracking
        t_size = config.tournament_size
        dev = population.device
        comp_1 = torch.randint(0, pool_size, (n_pairs, t_size), device=dev)
        best_p1 = torch.argmin(sorted_fit[comp_1], dim=1)
        winner_idx_1 = comp_1.gather(1, best_p1.unsqueeze(1)).squeeze(1)

        comp_2 = torch.randint(0, pool_size, (n_pairs, t_size), device=dev)
        best_p2 = torch.argmin(sorted_fit[comp_2], dim=1)
        winner_idx_2 = comp_2.gather(1, best_p2.unsqueeze(1)).squeeze(1)

        parents_1 = sorted_pop[winner_idx_1]
        parents_2 = sorted_pop[winner_idx_2]

        c1, c2 = gpu_crossover_single_point(parents_1, parents_2, crossover_p=config.crossover_p)
        offspring = torch.cat([c1, c2], dim=0)[:n_offspring]
        mutated = gpu_mutate(
            offspring,
            p_gene=config.gene_mut_p,
            p_block=config.large_mut_p,
            p_byte=config.point_mut_p,
        )

        pure_inj = gpu_sample_pure(n_pure, device=dev)
        struct_inj = gpu_sample_structured(n_struct, device=dev)
        injected = torch.cat([pure_inj, struct_inj], dim=0)

        # Assemble new population
        population = torch.cat([elites, mutated, injected], dim=0)[:pop_size]

        # Assemble new candidate IDs and parent maps
        next_cids: list[str] = []
        next_parents: dict[str, list[str]] = {}
        next_ops: dict[str, str] = {}

        # 1. Elites
        for e_idx in range(k_elites):
            new_cid = f"c_g{gen + 1}_e{e_idx}"
            next_cids.append(new_cid)
            next_parents[new_cid] = [elite_cids[e_idx]]
            next_ops[new_cid] = "elite"

        # 2. Offspring
        w1_list = winner_idx_1.cpu().numpy()
        w2_list = winner_idx_2.cpu().numpy()
        for off_idx in range(n_offspring):
            new_cid = f"c_g{gen + 1}_o{off_idx}"
            pair_idx = off_idx % n_pairs
            p1_cid = sorted_cids[int(w1_list[pair_idx])]
            p2_cid = sorted_cids[int(w2_list[pair_idx])]
            next_cids.append(new_cid)
            next_parents[new_cid] = [p1_cid, p2_cid]
            next_ops[new_cid] = "crossover+mutation"

        # 3. Injections
        for inj_idx in range(n_inject):
            new_cid = f"c_g{gen + 1}_inj{inj_idx}"
            next_cids.append(new_cid)
            next_parents[new_cid] = []
            next_ops[new_cid] = "injection"

        candidate_ids = next_cids[:pop_size]
        candidate_parents = next_parents
        candidate_operators = next_ops

    # Ensure best overall candidate is in ancestry vault
    if best_overall_cid not in ancestry_vault and best_overall_cid:
        # Fallback registration
        best_prog = population[0].cpu().numpy().astype(np.uint32)
        ancestry_vault[best_overall_cid] = CandidateAncestry(
            candidate_id=best_overall_cid,
            generation=n_generations - 1,
            parent_ids=[],
            operator="elite",
            bytecode_hex=best_prog.tobytes().hex(),
            bytecode_sha256=hashlib.sha256(best_prog.tobytes()).hexdigest(),
            disassembly=decode_human(best_prog),
            fitness=best_overall_fit,
            mse=best_overall_fit,
            metrics=extract_candidate_metrics(best_prog),
            ancestry_chain=[best_overall_cid],
        )

    # Exploration metrics for this run
    pop_cpu = population.cpu().numpy().astype(np.uint32)
    sigs: set[str] = set()
    for prog in population:
        sig, _ = compute_behavioral_signature(prog, probe_xs, device)
        sigs.add(sig)

    run_record = LineageRecord(
        run_id=f"run_seed_{seed}",
        problem={
            "name": formula,
            "n_points": n_points,
            "data_hash": data_hash,
        },
        method="GPUResidentEvolution",
        bytecode_version=0,
        config={
            "pop_size": pop_size,
            "n_generations": n_generations,
            "n_points": n_points,
            "device": str(device),
        },
        sampler_state={
            "initial_seed": seed,
            "rng": "PyTorch+NumPy",
        },
        generations=generations_records,
        promoted_ancestry=list(ancestry_vault.values()),
        audit_store=audit_store,
        summary={
            "best_fitness": best_overall_fit,
            "best_candidate_id": best_overall_cid,
            "promoted_total": len(ancestry_vault),
            "distinct_byte_programs": int(torch.unique(population, dim=0).shape[0]),
            "distinct_expressions": len(sigs),
        },
    )
    return run_record


# ==============================================================================
# Replay Verifier
# ==============================================================================


def verify_replay_bit_exact(
    record: LineageRecord,
    device_name: str | None = None,
) -> dict[str, Any]:
    """Replay an evolutionary run from (config, seed) and verify bit-exact parity."""
    seed = record.sampler_state["initial_seed"]
    cfg = record.config
    audit_mode = record.audit_store is not None

    replayed = run_lineage_evolution(
        seed=seed,
        pop_size=cfg["pop_size"],
        n_generations=cfg["n_generations"],
        n_points=cfg["n_points"],
        formula=record.problem["name"],
        audit_mode=audit_mode,
        device_name=device_name,
    )

    mismatches: list[str] = []

    # 1. Compare generation batch hashes
    if len(replayed.generations) != len(record.generations):
        mismatches.append(
            f"Generation count mismatch: {len(replayed.generations)} != {len(record.generations)}"
        )
    else:
        for g_idx, (orig_g, rep_g) in enumerate(zip(record.generations, replayed.generations)):
            if orig_g.batch_hash != rep_g.batch_hash:
                mismatches.append(
                    f"Gen {g_idx} batch_hash mismatch: {orig_g.batch_hash} != {rep_g.batch_hash}"
                )
            if abs(orig_g.best_fitness - rep_g.best_fitness) > 1e-6:
                mismatches.append(
                    f"Gen {g_idx} best_fitness mismatch: {orig_g.best_fitness} != {rep_g.best_fitness}"
                )

    # 2. Compare promoted ancestry
    orig_prom = {a.candidate_id: a.bytecode_sha256 for a in record.promoted_ancestry}
    rep_prom = {a.candidate_id: a.bytecode_sha256 for a in replayed.promoted_ancestry}
    if orig_prom != rep_prom:
        mismatches.append(f"Promoted ancestry mismatch: {orig_prom.keys()} vs {rep_prom.keys()}")

    # 3. Compare audit store if present
    if audit_mode and record.audit_store is not None and replayed.audit_store is not None:
        if len(record.audit_store) != len(replayed.audit_store):
            mismatches.append(
                f"Audit store length mismatch: {len(record.audit_store)} != {len(replayed.audit_store)}"
            )
        else:
            for c_idx, (o_c, r_c) in enumerate(zip(record.audit_store, replayed.audit_store)):
                if o_c["bytecode_sha256"] != r_c["bytecode_sha256"]:
                    mismatches.append(
                        f"Audit candidate {c_idx} hash mismatch: {o_c['bytecode_sha256']} != {r_c['bytecode_sha256']}"
                    )
                    break

    return {
        "run_id": record.run_id,
        "seed": seed,
        "bit_exact_reproducible": len(mismatches) == 0,
        "generations_replayed": len(replayed.generations),
        "batch_hashes_matched": len(mismatches) == 0,
        "promoted_ancestry_matched": orig_prom == rep_prom,
        "mismatches_count": len(mismatches),
        "mismatches": mismatches[:5],
    }


# ==============================================================================
# Exploration Map Builder
# ==============================================================================


def build_exploration_map(
    records: list[LineageRecord],
    device_name: str | None = None,
) -> dict[str, Any]:
    """Aggregate exploration map across structure, ops, length, behavior, and quality."""
    device = resolve_device(device_name)
    probe_xs = torch.from_numpy(PROBE_POINTS).to(device)

    structure_buckets: dict[str, int] = {}
    op_counts: dict[str, int] = {}
    length_buckets: dict[str, int] = {}
    behavior_buckets: dict[str, int] = {}
    quality_buckets: dict[str, int] = {}

    unique_byte_programs: set[str] = set()
    unique_expressions: set[str] = set()

    for rec in records:
        for anc in rec.promoted_ancestry:
            unique_byte_programs.add(anc.bytecode_sha256)
            prog_bytes = bytes.fromhex(anc.bytecode_hex)
            prog_np = np.frombuffer(prog_bytes, dtype=np.uint32)

            # Structure & Length
            struct = classify_structure(anc.metrics)
            structure_buckets[struct] = structure_buckets.get(struct, 0) + 1

            act_len = anc.metrics["length_active"]
            if act_len <= 4:
                len_key = "1-4 (short)"
            elif act_len <= 8:
                len_key = "5-8 (medium)"
            elif act_len <= 12:
                len_key = "9-12 (standard)"
            else:
                len_key = "13-16 (long)"
            length_buckets[len_key] = length_buckets.get(len_key, 0) + 1

            # Ops
            for op_name in anc.metrics["ops"]:
                op_counts[op_name] = op_counts.get(op_name, 0) + 1

            # Behavior & Expression Hash
            prog_tensor = torch.from_numpy(prog_np.astype(np.int64)).to(device)
            sig, beh = compute_behavioral_signature(prog_tensor, probe_xs, device)
            behavior_buckets[beh] = behavior_buckets.get(beh, 0) + 1
            unique_expressions.add(sig)

            # Quality
            q_tier = classify_quality(anc.mse)
            quality_buckets[q_tier] = quality_buckets.get(q_tier, 0) + 1

    distinct_bytes = len(unique_byte_programs)
    distinct_exprs = len(unique_expressions)
    redundancy_ratio = distinct_bytes / max(1, distinct_exprs)

    return {
        "structure_distribution": structure_buckets,
        "opcode_distribution": op_counts,
        "length_distribution": length_buckets,
        "behavior_distribution": behavior_buckets,
        "quality_distribution": quality_buckets,
        "distinct_byte_programs": distinct_bytes,
        "distinct_mathematical_expressions": distinct_exprs,
        "syntactic_redundancy_ratio": redundancy_ratio,
        "accounting_note": (
            "distinct_byte_programs counts unique bytecode sequences; "
            "distinct_mathematical_expressions counts behavioral signatures on fixed probe points. "
            "Ratio reflects syntactic redundancy (dead instructions, NOPs, register swaps)."
        ),
    }


# ==============================================================================
# Tracing Overhead Accounting
# ==============================================================================


def measure_tracing_overhead(
    *,
    pop_size: int = 200,
    n_generations: int = 15,
    n_points: int = 128,
    formula: str = "x2_3x_7",
    device_name: str | None = None,
    repeats: int = 3,
) -> dict[str, Any]:
    """Measure wall-clock overhead: Baseline vs Aggregate Tracing vs Full Audit Mode."""
    device = resolve_device(device_name)
    synchronize(device)

    # 1. Baseline: zero tracing
    t0 = time.perf_counter()
    for s in range(repeats):
        seed_all(s)
        # Minimal loop without records or hashing
        xs_np = np.random.default_rng(s).uniform(-10.0, 10.0, size=(n_points,)).astype(np.float32)
        ys_np = (xs_np**2 + 3.0 * xs_np + 7.0).astype(np.float32)
        xs = torch.from_numpy(xs_np).to(device)
        ys = torch.from_numpy(ys_np).to(device)
        pop = gpu_sample_structured(pop_size, device=device)
        for _ in range(n_generations):
            preds, _ = execute_population_torch(pop, xs, device=device)
            mse = ((preds - ys.unsqueeze(0)) ** 2).mean(dim=1)
            sorted_idx = torch.argsort(mse)
            pop = pop[sorted_idx]
            synchronize(device)
    baseline_sec = (time.perf_counter() - t0) / repeats

    # 2. Aggregate Tracing
    t1 = time.perf_counter()
    for s in range(repeats):
        run_lineage_evolution(
            seed=s,
            pop_size=pop_size,
            n_generations=n_generations,
            n_points=n_points,
            formula=formula,
            audit_mode=False,
            device_name=device_name,
        )
        synchronize(device)
    aggregate_sec = (time.perf_counter() - t1) / repeats

    # 3. Full Audit Mode
    t2 = time.perf_counter()
    for s in range(repeats):
        run_lineage_evolution(
            seed=s,
            pop_size=pop_size,
            n_generations=n_generations,
            n_points=n_points,
            formula=formula,
            audit_mode=True,
            device_name=device_name,
        )
        synchronize(device)
    audit_sec = (time.perf_counter() - t2) / repeats

    agg_overhead_pct = ((aggregate_sec - baseline_sec) / max(1e-6, baseline_sec)) * 100.0
    audit_overhead_pct = ((audit_sec - baseline_sec) / max(1e-6, baseline_sec)) * 100.0

    evals_total = pop_size * n_generations
    return {
        "baseline_sec": baseline_sec,
        "aggregate_sec": aggregate_sec,
        "audit_sec": audit_sec,
        "aggregate_overhead_pct": max(0.0, agg_overhead_pct),
        "audit_overhead_pct": max(0.0, audit_overhead_pct),
        "cvps_baseline": evals_total / max(1e-6, baseline_sec),
        "cvps_aggregate": evals_total / max(1e-6, aggregate_sec),
        "cvps_audit": evals_total / max(1e-6, audit_sec),
        "repeats": repeats,
        "device": str(device),
    }


# ==============================================================================
# Full Pipeline Runner & CLI
# ==============================================================================


def run_evo_trace_pipeline(
    *,
    seeds_count: int = 3,
    audit: bool = True,
    output_path: Path,
    device_name: str | None = None,
    pop_size: int = 200,
    n_generations: int = 15,
    n_points: int = 128,
) -> dict[str, Any]:
    """Execute complete P26 lineage, audit, replay, and exploration map pipeline."""
    t_start = time.monotonic()
    device = resolve_device(device_name)
    deadline = MonotonicDeadline(budget_sec=600.0)
    deadline.mark_setup_done()

    print(f"Running P26 lineage runs for {seeds_count} seeds (audit={audit}, device={device})...")
    records: list[LineageRecord] = []
    replay_results: list[dict[str, Any]] = []

    for s_idx in range(seeds_count):
        seed = 42 + s_idx * 100
        print(f"  -> Executing run for seed {seed}...")
        rec = run_lineage_evolution(
            seed=seed,
            pop_size=pop_size,
            n_generations=n_generations,
            n_points=n_points,
            audit_mode=audit,
            device_name=device_name,
        )
        records.append(rec)

        # Replay and verify bit-exact reproducibility
        print(f"  -> Replaying run from seed {seed} for bit-exact verification...")
        rep_check = verify_replay_bit_exact(rec, device_name=device_name)
        replay_results.append(rep_check)

    deadline.mark_warmup_done()

    # Build Exploration Map across all runs
    print("Building global exploration map...")
    exp_map = build_exploration_map(records, device_name=device_name)

    # Measure Tracing Overhead
    print("Measuring tracing overhead (baseline vs aggregate vs audit)...")
    overhead = measure_tracing_overhead(
        pop_size=pop_size,
        n_generations=n_generations,
        n_points=n_points,
        device_name=device_name,
        repeats=2,
    )

    deadline.mark_compute_done()
    timing = deadline.finish()
    elapsed = max(1e-6, time.monotonic() - t_start)

    # Provenance
    prov = collect_provenance(
        seed=42,
        device=device,
        config={
            "seeds_count": seeds_count,
            "pop_size": pop_size,
            "n_generations": n_generations,
            "audit": audit,
        },
    )

    manifest_data = {
        "phase": "p26-lineage-map",
        "status": "complete",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        "elapsed_sec": elapsed,
        "seeds": [r.sampler_state["initial_seed"] for r in records],
        "all_bit_exact_reproduced": all(r["bit_exact_reproducible"] for r in replay_results),
        "replay_verification": replay_results,
        "exploration_map": exp_map,
        "overhead_benchmark": overhead,
        "lineage_runs": [r.to_dict() for r in records],
        "timing": timing,
        "provenance": prov,
    }

    written = write_manifest(output_path, manifest_data, {})
    return written


def main() -> int:
    parser = argparse.ArgumentParser(
        description="P26 Lineage Tracing, Audit Replay & Exploration Map Harness"
    )
    parser.add_argument(
        "--audit",
        action="store_true",
        help="Enable full candidate audit store for bit-exact replay",
    )
    parser.add_argument(
        "--seeds",
        type=int,
        default=3,
        help="Number of independent seeds to run and verify",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="experiments/p26-lineage.json",
        help="Path to write the checksummed artifact manifest",
    )
    parser.add_argument(
        "--device",
        type=str,
        default=None,
        help="Compute device (cuda / cpu)",
    )
    parser.add_argument(
        "--pop-size",
        type=int,
        default=200,
        help="Population size",
    )
    parser.add_argument(
        "--generations",
        type=int,
        default=15,
        help="Number of generations per run",
    )
    args = parser.parse_args()

    out_path = _REPO_ROOT / args.output
    manifest = run_evo_trace_pipeline(
        seeds_count=args.seeds,
        audit=args.audit,
        output_path=out_path,
        device_name=args.device,
        pop_size=args.pop_size,
        n_generations=args.generations,
    )

    print("\n=== P26 Lineage & Exploration Map Generated ===")
    print(f"Manifest: {out_path} (sha256={manifest['manifest_sha256'][:16]}...)")
    print(f"Status: {manifest['status']}")
    print(f"Bit-Exact Replay Verified: {manifest['all_bit_exact_reproduced']}")
    print(f"Seeds Run: {manifest['seeds']}")
    print(
        f"Distinct Byte Programs: {manifest['exploration_map']['distinct_byte_programs']} | "
        f"Distinct Expressions: {manifest['exploration_map']['distinct_mathematical_expressions']} "
        f"(Ratio: {manifest['exploration_map']['syntactic_redundancy_ratio']:.2f})"
    )
    print(
        f"Tracing Overhead: Aggregate={manifest['overhead_benchmark']['aggregate_overhead_pct']:.2f}% | "
        f"Audit={manifest['overhead_benchmark']['audit_overhead_pct']:.2f}%"
    )
    print(f"Elapsed: {manifest['elapsed_sec']:.2f} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
