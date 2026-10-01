"""GPU-resident evolutionary cycle (P17 scope).

Executes generation, evaluation, mutation, crossover, fitness reduction,
and selection directly on GPU tensors without per-candidate host round-trips.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np
import torch

from evobyte.bytecode import N_INSTR, N_REGS, decode_human
from evobyte.evolution import STRUCTURED_OP_RATIOS, EvolutionConfig
from evobyte.vm_torch import PopulationVMBuffer, execute_population_torch, get_default_device


def gpu_sample_pure(
    n: int,
    device: torch.device | str | None = None,
) -> torch.Tensor:
    """Sample uniform random program bytecodes directly on device."""
    dev = torch.device(device) if device is not None else get_default_device()
    # 32-bit unsigned integers stored in int64 to avoid overflow issues
    return torch.randint(0, 0x100000000, (n, N_INSTR), dtype=torch.int64, device=dev)


def gpu_sample_structured(
    n: int,
    device: torch.device | str | None = None,
    p_nop: float = 0.35,
) -> torch.Tensor:
    """Sample opcode-aware structured programs directly on device."""
    dev = torch.device(device) if device is not None else get_default_device()
    op_weights = torch.tensor(STRUCTURED_OP_RATIOS, dtype=torch.float32, device=dev)

    # 1. Opcode selection per slot
    op_samples = torch.multinomial(op_weights, n * N_INSTR, replacement=True).view(n, N_INSTR)

    # 2. Active instruction length per candidate (between 2 and N_INSTR inclusive)
    n_active = torch.randint(2, N_INSTR + 1, (n, 1), device=dev)
    step_idx = torch.arange(N_INSTR, device=dev).unsqueeze(0).expand(n, -1)
    active_mask = step_idx < n_active

    # 3. NOP padding
    nop_mask = (torch.rand((n, N_INSTR), device=dev) < p_nop) | (op_samples == 0)
    valid_mask = active_mask & (~nop_mask)
    ops = torch.where(valid_mask, op_samples, torch.zeros_like(op_samples))

    # 4. Operands
    dst = torch.randint(0, N_REGS, (n, N_INSTR), device=dev)
    a = torch.randint(0, N_REGS, (n, N_INSTR), device=dev)
    b_reg = torch.randint(0, N_REGS, (n, N_INSTR), device=dev)
    b_const = torch.randint(0, 16, (n, N_INSTR), device=dev)
    b = torch.where(ops == 0x0F, b_const, b_reg)

    # 5. Guarantee at least one write to r7 for candidates lacking it
    has_r7 = (valid_mask & (dst == 7) & (ops != 0)).any(dim=1)
    if not has_r7.all():
        need_fix = torch.nonzero(~has_r7).squeeze(1)
        if need_fix.numel() > 0:
            target_pos = (n_active[need_fix, 0] - 1).clamp(0, N_INSTR - 1)
            fb_ops_tensor = torch.tensor([0x01, 0x02, 0x03, 0x0F], device=dev, dtype=torch.int64)
            fb_pick = torch.randint(0, 4, (need_fix.shape[0],), device=dev)
            fb_op = fb_ops_tensor[fb_pick]
            fb_dst = torch.full_like(fb_op, 7)
            fb_a = torch.randint(0, N_REGS, (need_fix.shape[0],), device=dev)
            fb_b_reg = torch.randint(0, N_REGS, (need_fix.shape[0],), device=dev)
            fb_b_const = torch.randint(0, 16, (need_fix.shape[0],), device=dev)
            fb_b = torch.where(fb_op == 0x0F, fb_b_const, fb_b_reg)

            ops[need_fix, target_pos] = fb_op
            dst[need_fix, target_pos] = fb_dst
            a[need_fix, target_pos] = fb_a
            b[need_fix, target_pos] = fb_b

    # 6. Encode 32-bit instructions
    words = (ops & 0xFF) | ((dst & 0xFF) << 8) | ((a & 0xFF) << 16) | ((b & 0xFF) << 24)
    words = torch.where(ops != 0, words, torch.zeros_like(words))
    return words


def gpu_tournament_selection(
    sorted_population: torch.Tensor,
    sorted_fitness: torch.Tensor,
    n_winners: int,
    tournament_size: int,
    pool_size: int | None = None,
) -> torch.Tensor:
    """Vectorized tournament selection over population directly on device."""
    dev = sorted_population.device
    p_len = sorted_population.shape[0]
    p_pool = pool_size if pool_size is not None else p_len
    p_pool = max(1, min(p_len, p_pool))

    competitors = torch.randint(0, p_pool, (n_winners, tournament_size), device=dev)
    comp_fit = sorted_fitness[competitors]
    best_pos = torch.argmin(comp_fit, dim=1)
    winner_idx = competitors.gather(1, best_pos.unsqueeze(1)).squeeze(1)
    return sorted_population[winner_idx]


def gpu_crossover_single_point(
    p1: torch.Tensor,
    p2: torch.Tensor,
    crossover_p: float = 0.3,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Vectorized single-point crossover over 16 instruction slots on device."""
    dev = p1.device
    n = p1.shape[0]

    do_cross = torch.rand(n, device=dev) < crossover_p
    pts = torch.randint(1, N_INSTR, (n, 1), device=dev)
    cols = torch.arange(N_INSTR, device=dev).unsqueeze(0).expand(n, -1)
    left_mask = cols < pts

    c1 = torch.where(left_mask, p1, p2)
    c2 = torch.where(left_mask, p2, p1)

    c1 = torch.where(do_cross.unsqueeze(1), c1, p1)
    c2 = torch.where(do_cross.unsqueeze(1), c2, p2)
    return c1, c2


def gpu_mutate(
    progs: torch.Tensor,
    p_gene: float = 0.08,
    p_block: float = 0.05,
    p_byte: float = 0.02,
) -> torch.Tensor:
    """Vectorized mutation combining block, gene, and byte-level point flips on device."""
    dev = progs.device
    k = progs.shape[0]
    out = progs.clone()

    # 1. Block mutation
    if p_block > 0.0:
        do_block = torch.rand(k, device=dev) < p_block
        if do_block.any():
            block_lens = torch.randint(1, 4, (k, 1), device=dev)
            max_starts = (N_INSTR - block_lens).clamp(min=0)
            starts = (torch.rand(k, 1, device=dev) * (max_starts.float() + 1.0)).long()
            cols = torch.arange(N_INSTR, device=dev).unsqueeze(0).expand(k, -1)
            block_mask = do_block.unsqueeze(1) & (cols >= starts) & (cols < starts + block_lens)

            fresh_blocks = gpu_sample_structured(k, device=dev)
            out = torch.where(block_mask, fresh_blocks, out)

    # 2. Gene-level mutation (replacing instruction with newly sampled structured word)
    if p_gene > 0.0:
        gene_mask = torch.rand((k, N_INSTR), device=dev) < p_gene
        if gene_mask.any():
            fresh_genes = gpu_sample_structured(k, device=dev)
            out = torch.where(gene_mask, fresh_genes, out)

    # 3. Byte-level point mutation
    if p_byte > 0.0:
        byte_mask = torch.rand((k, N_INSTR, 4), device=dev) < p_byte
        if byte_mask.any():
            b0 = out & 0xFF
            b1 = (out >> 8) & 0xFF
            b2 = (out >> 16) & 0xFF
            b3 = (out >> 24) & 0xFF

            r0 = torch.randint(0, 256, (k, N_INSTR), device=dev, dtype=torch.int64)
            r1 = torch.randint(0, 256, (k, N_INSTR), device=dev, dtype=torch.int64)
            r2 = torch.randint(0, 256, (k, N_INSTR), device=dev, dtype=torch.int64)
            r3 = torch.randint(0, 256, (k, N_INSTR), device=dev, dtype=torch.int64)

            new_b0 = torch.where(byte_mask[..., 0], r0, b0)
            # Clamp opcodes into valid [0x00..0x0F] table
            new_b0 = torch.where(new_b0 > 15, torch.zeros_like(new_b0), new_b0)
            new_b1 = torch.where(byte_mask[..., 1], r1, b1)
            new_b2 = torch.where(byte_mask[..., 2], r2, b2)
            new_b3 = torch.where(byte_mask[..., 3], r3, b3)

            out = (
                (new_b0 & 0xFF)
                | ((new_b1 & 0xFF) << 8)
                | ((new_b2 & 0xFF) << 16)
                | ((new_b3 & 0xFF) << 24)
            )

    return out


class GPUResidentEvolution:
    """Closed evolutionary search cycle resident entirely in GPU memory."""

    def __init__(
        self,
        xs: np.ndarray | torch.Tensor,
        ys: np.ndarray | torch.Tensor,
        config: EvolutionConfig | None = None,
        x1s: np.ndarray | torch.Tensor | None = None,
        device: torch.device | str | None = None,
        initial_population: np.ndarray | torch.Tensor | None = None,
        cascade: Any | None = None,
    ) -> None:
        self.device = torch.device(device) if device is not None else get_default_device()
        self.config = config if config is not None else EvolutionConfig()
        self.cascade = cascade

        if isinstance(xs, np.ndarray):
            self.xs = torch.from_numpy(xs.astype(np.float32)).to(self.device)
        else:
            self.xs = xs.to(dtype=torch.float32, device=self.device)
        self.xs = self.xs.ravel()

        if isinstance(ys, np.ndarray):
            self.ys = torch.from_numpy(ys.astype(np.float32)).to(self.device)
        else:
            self.ys = ys.to(dtype=torch.float32, device=self.device)
        self.ys = self.ys.ravel()

        if x1s is not None:
            if isinstance(x1s, np.ndarray):
                self.x1s = torch.from_numpy(x1s.astype(np.float32)).to(self.device)
            else:
                self.x1s = x1s.to(dtype=torch.float32, device=self.device)
            self.x1s = self.x1s.ravel()
        else:
            self.x1s = None

        pop_size = self.config.pop_size
        b_points = self.xs.shape[0]

        # Allocate reusable VM buffer
        self.vm_buffer = PopulationVMBuffer(
            max_pop=pop_size,
            max_points=b_points,
            device=self.device,
        )

        # Initialize resident population
        if initial_population is not None:
            if isinstance(initial_population, np.ndarray):
                self.population = torch.from_numpy(initial_population.astype(np.int64)).to(
                    self.device
                )
            else:
                self.population = initial_population.to(dtype=torch.int64, device=self.device)
        else:
            self.population = gpu_sample_structured(pop_size, device=self.device)

        self.generation = 0
        self.best_fitness = float("inf")
        self.best_mse = float("inf")
        self.best_program = self.population[0].cpu().numpy().astype(np.uint32)

    def _sync(self) -> None:
        if self.device.type == "cuda":
            torch.cuda.synchronize(self.device)

    def step(self) -> dict[str, Any]:
        """Execute one generation cycle resident on GPU."""
        self.generation += 1
        t_start = time.perf_counter()

        # 1. EVALUATION on GPU
        t_eval_0 = time.perf_counter()
        if self.cascade is not None:
            elite_sc = self.best_fitness if self.best_fitness < 1e5 else None
            fitness, mse, counters = self.cascade.evaluate(
                self.population,
                self.xs,
                self.ys,
                elite_score=elite_sc,
                x1s=self.x1s,
            )
            invalid = fitness >= 1e5
        else:
            preds, flags = execute_population_torch(
                self.population,
                self.xs,
                x1s=self.x1s,
                device=self.device,
                buffer=self.vm_buffer,
            )
            diff = preds - self.ys.unsqueeze(0)
            mse = (diff**2).mean(dim=1)

            # Invalidity penalty
            invalid = flags.any(dim=1)
            penalized_mse = torch.where(invalid, mse + 1e6, mse)

            # Complexity penalty
            ops = self.population & 0xFF
            complexity = (ops != 0).sum(dim=1).to(dtype=torch.float32)
            fitness = penalized_mse + self.config.complexity_weight * complexity
            counters = None

        self._sync()
        t_eval = time.perf_counter() - t_eval_0

        # 2. SELECTION & ELITISM on GPU
        t_sel_0 = time.perf_counter()
        sorted_fit, sorted_idx = torch.sort(fitness)
        sorted_pop = self.population[sorted_idx]
        sorted_mse = mse[sorted_idx]

        # Update best tracked elite
        gen_best_fit = float(sorted_fit[0].item())
        gen_best_mse = float(sorted_mse[0].item())
        if gen_best_fit < self.best_fitness:
            self.best_fitness = gen_best_fit
            self.best_mse = gen_best_mse
            self.best_program = sorted_pop[0].cpu().numpy().astype(np.uint32)

        pop_size = self.config.pop_size
        k_elites = min(self.config.elite_k, pop_size)
        elites = sorted_pop[:k_elites]

        # Random injection floor (at least 10% pure random/structured, always)
        n_inject = max(
            int(np.ceil(self.config.random_inject_p * pop_size)),
            int(np.ceil(0.10 * pop_size)),
        )
        n_pure = n_inject // 2
        n_struct = n_inject - n_pure

        n_offspring = pop_size - k_elites - n_inject
        pool_size = max(4, min(pop_size, max(20, int(0.25 * pop_size))))

        # Select parents
        n_pairs = (n_offspring + 1) // 2
        parents_1 = gpu_tournament_selection(
            sorted_pop,
            sorted_fit,
            n_winners=n_pairs,
            tournament_size=self.config.tournament_size,
            pool_size=pool_size,
        )
        parents_2 = gpu_tournament_selection(
            sorted_pop,
            sorted_fit,
            n_winners=n_pairs,
            tournament_size=self.config.tournament_size,
            pool_size=pool_size,
        )
        self._sync()
        t_sel = time.perf_counter() - t_sel_0

        # 3. REPRODUCTION & INJECTION on GPU
        t_rep_0 = time.perf_counter()
        # Crossover
        c1, c2 = gpu_crossover_single_point(
            parents_1, parents_2, crossover_p=self.config.crossover_p
        )
        offspring = torch.cat([c1, c2], dim=0)[:n_offspring]

        # Mutation
        mutated_offspring = gpu_mutate(
            offspring,
            p_gene=self.config.gene_mut_p,
            p_block=self.config.large_mut_p,
            p_byte=self.config.point_mut_p,
        )

        # Injections
        pure_injected = gpu_sample_pure(n_pure, device=self.device)
        struct_injected = gpu_sample_structured(n_struct, device=self.device)
        injected = torch.cat([pure_injected, struct_injected], dim=0)

        # Reassemble resident population
        parts = [elites, mutated_offspring, injected]
        self.population = torch.cat(parts, dim=0)[:pop_size]

        self._sync()
        t_rep = time.perf_counter() - t_rep_0
        t_step = time.perf_counter() - t_start

        # Compute light telemetry
        valid_count = int((~invalid).sum().item())
        valid_rate = float(valid_count / pop_size)
        unique_count = int(torch.unique(sorted_pop[: min(pop_size, 500)], dim=0).shape[0])
        dup_rate = float(1.0 - (unique_count / min(pop_size, 500)))

        stat_dict = {
            "generation": self.generation,
            "best_fitness": self.best_fitness,
            "best_mse": self.best_mse,
            "gen_best_fit": gen_best_fit,
            "gen_best_mse": gen_best_mse,
            "mean_fitness": float(sorted_fit.mean().item()),
            "valid_rate": valid_rate,
            "duplicate_rate": dup_rate,
            "eval_time_s": t_eval,
            "select_time_s": t_sel,
            "reproduce_time_s": t_rep,
            "step_time_s": t_step,
            "candidates_per_sec": pop_size / max(t_step, 1e-6),
        }
        if counters is not None:
            stat_dict["cascade_counters"] = counters.to_dict()
        return stat_dict

    def run(
        self,
        max_generations: int | None = None,
        early_stop_mse: float | None = None,
        on_generation: Callable[[dict[str, Any]], None] | None = None,
        time_budget_sec: float | None = None,
    ) -> dict[str, Any]:
        """Run evolutionary loop resident on GPU."""
        if time_budget_sec is not None and max_generations is None:
            max_gen = None
        else:
            max_gen = (
                max_generations if max_generations is not None else self.config.max_generations
            )
        target_mse = (
            early_stop_mse if early_stop_mse is not None else self.config.early_stop_fitness
        )

        t_total_0 = time.perf_counter()
        history = []
        converged = False

        gen_counter = 0
        while True:
            if max_gen is not None and gen_counter >= max_gen:
                break
            if time_budget_sec is not None and (time.perf_counter() - t_total_0) >= time_budget_sec:
                break

            stats = self.step()
            stats["elapsed_total_s"] = time.perf_counter() - t_total_0
            history.append(stats)
            gen_counter += 1

            if on_generation is not None:
                on_generation(stats)

            if stats["best_mse"] <= target_mse:
                converged = True
                break

        total_time = time.perf_counter() - t_total_0
        total_evals = len(history) * self.config.pop_size

        return {
            "best_program": self.best_program,
            "best_fitness": self.best_fitness,
            "best_mse": self.best_mse,
            "best_expression": decode_human(self.best_program),
            "generations": len(history),
            "candidates_total": total_evals,
            "time_sec": total_time,
            "search_cvps": total_evals / max(total_time, 1e-6),
            "converged": converged,
            "history": history,
        }

    def save_checkpoint(self, path: str | Path) -> None:
        """Save GPU-resident population and RNG states to checkpoint."""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        state = {
            "generation": self.generation,
            "population": self.population.cpu().clone(),
            "best_fitness": self.best_fitness,
            "best_mse": self.best_mse,
            "best_program": torch.from_numpy(self.best_program.astype(np.int64)),
            "torch_cpu_rng": torch.get_rng_state(),
            "torch_cuda_rng": (
                torch.cuda.get_rng_state_all() if torch.cuda.is_available() else None
            ),
            "numpy_rng": np.random.get_state(),
        }
        torch.save(state, p)

    def load_checkpoint(self, path: str | Path) -> None:
        """Restore GPU-resident population and RNG states from checkpoint."""
        state = torch.load(path, map_location=self.device, weights_only=False)
        self.generation = int(state["generation"])
        self.population = state["population"].to(self.device)
        self.best_fitness = float(state["best_fitness"])
        self.best_mse = float(state["best_mse"])
        self.best_program = state["best_program"].cpu().numpy().astype(np.uint32)
        torch.set_rng_state(state["torch_cpu_rng"].cpu())
        if torch.cuda.is_available() and state["torch_cuda_rng"] is not None:
            cuda_states = [
                s.cpu() if isinstance(s, torch.Tensor) else s for s in state["torch_cuda_rng"]
            ]
            torch.cuda.set_rng_state_all(cuda_states)
        if "numpy_rng" in state and state["numpy_rng"] is not None:
            np.random.set_state(state["numpy_rng"])
