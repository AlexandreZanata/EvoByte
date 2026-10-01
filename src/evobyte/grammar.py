"""Grammar-constrained candidate generation and canonicalization (P33 Scope).

Provides typed expression generation, compilation to bytecode v0,
liveness/dead-code analysis, and cheap algebraic canonicalization for the
polynomial_arithmetic family. No strings or AST parsing in the hot loop.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import torch

from evobyte.bytecode import (
    CONST_BANK,
    N_INSTR,
    N_REGS,
    decode_instr,
    encode_instr,
    is_valid,
)
from evobyte.evolution import EvolutionConfig
from evobyte.resident import (
    GPUResidentEvolution,
    gpu_crossover_single_point,
    gpu_tournament_selection,
)
from evobyte.vm_torch import execute_population_torch

# Preregistered rational coefficient indices in CONST_BANK
# 0: 0.0, 1: 1.0, 2: -1.0, 3: 2.0, 4: 0.5, 7: 10.0, 9: -0.5, 10: 7.0, 11: 3.0, 14: -10.0
PREREGISTERED_CONST_INDICES = [0, 1, 2, 3, 4, 7, 9, 10, 11, 14]


@dataclass(frozen=True)
class PolynomialSpec:
    """Preregistered specification for polynomial_arithmetic family (P33)."""

    family: str = "polynomial_arithmetic"
    variable_name: str = "x"
    variable_reg: int = 0  # r0
    zero_reg: int = 1  # r1 holds 0.0
    output_reg: int = 7  # r7
    scratch_regs: tuple[int, ...] = (2, 3, 4, 5, 6)
    max_degree: int = 4
    max_instructions: int = N_INSTR  # 16
    allowed_opcodes: tuple[str, ...] = ("NOP", "ADD", "SUB", "MUL", "CSEL")
    target_mse_threshold: float = 1e-4
    rational_coeff_bounds: tuple[float, float] = (-10.0, 10.0)
    allowed_const_indices: tuple[int, ...] = tuple(PREREGISTERED_CONST_INDICES)
    development_targets: tuple[str, ...] = (
        "3*x + 2",
        "x^2 - x + 1",
        "2*x^2 + 3",
        "x^3 - 2*x",
        "(x - 2)^2",
        "4*x - 5",
    )
    heldout_targets: tuple[str, ...] = (
        "x^2 + 3*x - 2",
        "x^2 - 9",
        "5*x - 7",
        "x^3 + x^2",
    )


# ==============================================================================
# Liveness Analysis & Cheap Canonicalization
# ==============================================================================


def analyze_program_liveness(program: np.ndarray) -> dict[str, Any]:
    """Analyze instruction liveness via backward reachability from r7.

    Separates active/live instructions from padding (NOPs) and dead code
    (computations whose results are never read). Detects constant outputs
    (where r0 is never in the live register dependency chain).
    """
    live_regs: set[int] = {7}
    live_mask = [False] * N_INSTR
    padding_mask = [False] * N_INSTR

    for i in range(N_INSTR - 1, -1, -1):
        op, dst, a, b = decode_instr(program[i])
        if op == 0x00:
            padding_mask[i] = True
            continue
        if dst in live_regs:
            live_mask[i] = True
            # Destination register is now defined; remove from live_regs unless read in same op
            if dst != a and (op == 0x0F or dst != (b % N_REGS)):
                live_regs.remove(dst)
            live_regs.add(a)
            if op != 0x0F:
                live_regs.add(b % N_REGS)

    reads_input = 0 in live_regs

    return {
        "live_count": sum(live_mask),
        "dead_count": N_INSTR - sum(live_mask) - sum(padding_mask),
        "padding_count": sum(padding_mask),
        "is_constant_output": not reads_input,
        "live_mask": live_mask,
    }


def canonicalize_bytecode(program: np.ndarray) -> tuple[np.ndarray, dict[str, Any]]:
    """Canonicalize cheaply justified algebraic identities to reduce syntactic duplication.

    Does NOT claim equivalence from probe points alone.
    Applies:
    1. Dead code elimination (replaces unread instructions with NOPs).
    2. Commutative operand ordering: ensures src_a <= src_b for ADD and MUL.
    3. Padding compaction: live instructions packed forward, NOPs at end.
    """
    liveness = analyze_program_liveness(program)
    live_mask = liveness["live_mask"]

    new_words: list[np.uint32] = []
    reordered_count = 0

    for i in range(N_INSTR):
        if not live_mask[i]:
            continue
        op, dst, a, b = decode_instr(program[i])
        # Commutative canonicalization: for ADD (0x01) and MUL (0x03), order operands
        if op in (0x01, 0x03):
            b_reg = b % N_REGS
            if a > b_reg:
                new_words.append(encode_instr(op, dst=dst, a=b_reg, b=a))
                reordered_count += 1
                continue
        new_words.append(program[i])

    # Pad with NOPs to 16
    while len(new_words) < N_INSTR:
        new_words.append(np.uint32(0))

    canon_prog = np.array(new_words[:N_INSTR], dtype=np.uint32)
    return canon_prog, {
        "live_count": liveness["live_count"],
        "dead_count": liveness["dead_count"],
        "is_constant_output": liveness["is_constant_output"],
        "reordered_count": reordered_count,
    }


# ==============================================================================
# Typed Polynomial Expression AST & Compiler
# ==============================================================================


@dataclass
class Expr:
    """Base class for typed expression AST."""


@dataclass
class Var(Expr):
    """Input variable x (register r0)."""

    name: str = "x"

    def __repr__(self) -> str:
        return "x"


@dataclass
class Const(Expr):
    """Constant value selected from CONST_BANK index."""

    const_idx: int
    val: float = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "val", float(CONST_BANK[self.const_idx & 0x0F]))

    def __repr__(self) -> str:
        return f"{self.val:.2g}"


@dataclass
class BinOp(Expr):
    """Binary operation: '+', '-', or '*'."""

    op: str
    left: Expr
    right: Expr

    def __repr__(self) -> str:
        return f"({self.left} {self.op} {self.right})"


@dataclass
class HornerPoly(Expr):
    """Polynomial in Horner form: P(x) = (...(a_n*x + a_{n-1})*x + ... + a_0)."""

    coeff_indices: list[int]  # [a_n, a_{n-1}, ..., a_0] from highest degree to constant

    def __repr__(self) -> str:
        deg = len(self.coeff_indices) - 1
        terms = []
        for i, c_idx in enumerate(self.coeff_indices):
            p = deg - i
            val = float(CONST_BANK[c_idx & 0x0F])
            if abs(val) < 1e-4 and deg > 0:
                continue
            if p == 0:
                terms.append(f"{val:.2g}")
            elif p == 1:
                terms.append(f"{val:.2g}*x")
            else:
                terms.append(f"{val:.2g}*x^{p}")
        return " + ".join(terms) if terms else "0"


def compile_horner_to_bytecode(
    poly: HornerPoly,
) -> tuple[np.ndarray | None, bool]:
    """Compile a Horner polynomial into 16-word bytecode v0.

    Uses registers r1 (0.0), r2 (accumulator), and r7 (final output).
    Guarantees valid forward register dependencies and live output in r7.
    Returns (bytecode_array, rejected_overlength).
    """
    coeffs = poly.coeff_indices
    if not coeffs:
        # 0 polynomial: CSEL r7, r1, b=0 (loads 0.0)
        words = [0] * N_INSTR
        words[0] = encode_instr(0x0F, dst=7, a=1, b=0)
        return np.array(words, dtype=np.uint32), False

    deg = len(coeffs) - 1
    instructions: list[np.uint32] = []

    # Degree 0: constant
    if deg == 0:
        instructions.append(encode_instr(0x0F, dst=7, a=1, b=coeffs[0]))
    else:
        # Load highest coefficient a_n into r2
        instructions.append(encode_instr(0x0F, dst=2, a=1, b=coeffs[0]))
        for i in range(1, len(coeffs)):
            # r2 = r2 * x (MUL r2, r2, r0)
            instructions.append(encode_instr(0x03, dst=2, a=2, b=0))
            c_idx = coeffs[i]
            val = float(CONST_BANK[c_idx & 0x0F])
            target_reg = 7 if i == len(coeffs) - 1 else 2
            if abs(val) > 1e-4:
                # Add coefficient: CSEL target, r2, b=c_idx
                instructions.append(encode_instr(0x0F, dst=target_reg, a=2, b=c_idx))
            elif target_reg == 7:
                # Final assignment to r7
                instructions.append(encode_instr(0x01, dst=7, a=2, b=1))

    if len(instructions) > N_INSTR:
        return None, True

    # Pad with NOPs
    words = instructions[:]
    while len(words) < N_INSTR:
        words.append(np.uint32(0))

    prog = np.array(words[:N_INSTR], dtype=np.uint32)
    return prog, False


def compile_expr_to_bytecode(
    expr: Expr,
) -> tuple[np.ndarray | None, bool]:
    """Compile an expression tree into 16-word bytecode v0.

    Allocates registers r2..r6 for scratch subtrees, r0 for x, r1 for 0.0,
    and r7 for root output. Returns (bytecode_array, rejected_overlength).
    """
    if isinstance(expr, HornerPoly):
        return compile_horner_to_bytecode(expr)

    instructions: list[np.uint32] = []
    reg_alloc = 2  # cycle through r2..r6

    def emit(e: Expr, dst: int) -> int:
        nonlocal reg_alloc
        if len(instructions) >= N_INSTR:
            return -1

        if isinstance(e, Var):
            # Write x (r0) to dst: ADD dst, r0, r1 (r1 is 0.0)
            if dst == 0:
                return 0
            if len(instructions) >= N_INSTR:
                return -1
            instructions.append(encode_instr(0x01, dst=dst, a=0, b=1))
            return dst

        elif isinstance(e, Const):
            # CSEL dst, r1, b=e.const_idx (0 + const)
            if len(instructions) >= N_INSTR:
                return -1
            instructions.append(encode_instr(0x0F, dst=dst, a=1, b=e.const_idx))
            return dst

        elif isinstance(e, BinOp):
            # Optimization: Addition of constant -> CSEL
            if e.op == "+" and isinstance(e.right, Const):
                r_l = emit(e.left, dst)
                if r_l == -1 or len(instructions) >= N_INSTR:
                    return -1
                instructions.append(encode_instr(0x0F, dst=dst, a=r_l, b=e.right.const_idx))
                return dst

            r_l_target = reg_alloc
            reg_alloc = 2 + ((reg_alloc - 1) % 5)
            r_l = emit(e.left, r_l_target)
            if r_l == -1:
                return -1

            r_r_target = reg_alloc
            reg_alloc = 2 + ((reg_alloc - 1) % 5)
            r_r = emit(e.right, r_r_target)
            if r_r == -1:
                return -1

            if len(instructions) >= N_INSTR:
                return -1

            op_code = 0x01 if e.op == "+" else (0x02 if e.op == "-" else 0x03)
            instructions.append(encode_instr(op_code, dst=dst, a=r_l, b=r_r))
            return dst

        return -1

    res = emit(expr, dst=7)
    if res == -1 or len(instructions) > N_INSTR:
        return None, True

    # Ensure r7 was written
    _, last_dst, _, _ = decode_instr(instructions[-1])
    if last_dst != 7:
        if len(instructions) >= N_INSTR:
            return None, True
        instructions.append(encode_instr(0x01, dst=7, a=last_dst, b=1))

    # Pad with NOPs
    words = instructions[:]
    while len(words) < N_INSTR:
        words.append(np.uint32(0))

    prog = np.array(words[:N_INSTR], dtype=np.uint32)
    return prog, False


# ==============================================================================
# Grammar Sampling & Mutation
# ==============================================================================


def sample_random_horner(
    rng: random.Random,
    max_degree: int = 3,
) -> HornerPoly:
    """Sample a random polynomial in Horner form."""
    deg = rng.randint(1, max_degree)
    # Highest degree coefficient non-zero: choose from non-zero indices
    non_zero_indices = [i for i in PREREGISTERED_CONST_INDICES if i != 0]
    lead_c = rng.choice(non_zero_indices)
    rest_c = [rng.choice(PREREGISTERED_CONST_INDICES) for _ in range(deg)]
    return HornerPoly(coeff_indices=[lead_c] + rest_c)


def sample_random_tree(
    rng: random.Random,
    depth: int = 0,
    max_depth: int = 3,
) -> Expr:
    """Sample a random polynomial expression tree."""
    if depth >= max_depth or (depth > 0 and rng.random() < 0.35):
        if rng.random() < 0.6:
            return Var()
        else:
            return Const(rng.choice(PREREGISTERED_CONST_INDICES))

    op = rng.choice(["+", "-", "*"])
    l = sample_random_tree(rng, depth + 1, max_depth)
    r = sample_random_tree(rng, depth + 1, max_depth)
    return BinOp(op, l, r)


def sample_grammar_candidate(
    rng: random.Random | None = None,
    max_degree: int = 3,
) -> np.ndarray:
    """Sample a grammar-valid polynomial bytecode candidate."""
    r = rng if rng is not None else random.Random()
    for _ in range(50):
        # 50% Horner, 50% expression tree
        if r.random() < 0.5:
            poly = sample_random_horner(r, max_degree=max_degree)
            prog, overlength = compile_horner_to_bytecode(poly)
        else:
            tree = sample_random_tree(r, max_depth=max_degree)
            prog, overlength = compile_expr_to_bytecode(tree)

        if not overlength and prog is not None and is_valid(prog):
            canon_prog, _ = canonicalize_bytecode(prog)
            return canon_prog

    # Fallback linear program y = x
    words = [0] * N_INSTR
    words[0] = encode_instr(0x01, dst=7, a=0, b=1)  # ADD r7, r0, r1
    return np.array(words, dtype=np.uint32)


def sample_grammar_batch(
    n_samples: int,
    device: torch.device,
    seed: int = 42,
    max_degree: int = 3,
) -> torch.Tensor:
    """Sample a batch of grammar-compliant polynomial bytecode candidates resident on device."""
    rng = random.Random(seed)
    candidates = []
    for _ in range(n_samples):
        cand = sample_grammar_candidate(rng, max_degree=max_degree)
        candidates.append(cand)
    arr = np.stack(candidates, axis=0).astype(np.int64)
    return torch.from_numpy(arr).to(device)


def grammar_mutate_program(
    program: np.ndarray,
    rng: random.Random,
    p_mut: float = 0.25,
) -> np.ndarray:
    """Mutate a bytecode program while preserving grammatical polynomial validity."""
    if rng.random() < 0.15:
        # Full grammatical re-sampling
        return sample_grammar_candidate(rng)

    words = list(program)

    for i in range(N_INSTR):
        if rng.random() > p_mut:
            continue
        op, dst, a, b = decode_instr(words[i])
        if op == 0x00:
            continue

        mut_type = rng.choice(["coeff", "op_swap", "negate"])
        if mut_type == "coeff" and op == 0x0F:
            # Mutate constant index
            new_idx = rng.choice(PREREGISTERED_CONST_INDICES)
            words[i] = encode_instr(0x0F, dst=dst, a=a, b=new_idx)
        elif mut_type == "op_swap" and op in (0x01, 0x02):
            # Swap ADD <-> SUB
            new_op = 0x02 if op == 0x01 else 0x01
            words[i] = encode_instr(new_op, dst=dst, a=a, b=b)
        elif mut_type == "negate" and op == 0x0F:
            # Negate constant if negative exists in bank
            val = float(CONST_BANK[b & 0x0F])
            neg_val = -val
            for idx, c in enumerate(CONST_BANK):
                if abs(float(c) - neg_val) < 1e-4:
                    words[i] = encode_instr(0x0F, dst=dst, a=a, b=idx)
                    break

    mut_arr = np.array(words, dtype=np.uint32)
    if is_valid(mut_arr):
        canon, _ = canonicalize_bytecode(mut_arr)
        return canon

    return program


def grammar_mutate_batch(
    population: torch.Tensor,
    device: torch.device,
    p_mut: float = 0.25,
    seed: int = 42,
) -> torch.Tensor:
    """Apply grammar-aware mutation across a population tensor resident on device."""
    rng = random.Random(seed)
    pop_cpu = population.cpu().numpy().astype(np.uint32)
    n_pop = pop_cpu.shape[0]

    mutated_pop = np.empty_like(pop_cpu)
    for i in range(n_pop):
        mutated_pop[i] = grammar_mutate_program(pop_cpu[i], rng, p_mut=p_mut)

    return torch.from_numpy(mutated_pop.astype(np.int64)).to(device)


class GrammarResidentEvolution(GPUResidentEvolution):
    """GPU-resident evolution with 100% grammar-constrained initialization, mutation, and injection."""

    def __init__(
        self,
        xs: np.ndarray | torch.Tensor,
        ys: np.ndarray | torch.Tensor,
        config: EvolutionConfig | None = None,
        device: torch.device | None = None,
        seed: int = 42,
    ) -> None:
        dev = device if device is not None else torch.device("cpu")
        cfg = config if config is not None else EvolutionConfig()
        init_pop = sample_grammar_batch(cfg.pop_size, device=dev, seed=seed)
        super().__init__(xs, ys, config=cfg, device=dev, initial_population=init_pop)
        self.seed = seed
        self.rng_counter = seed

    def step(self) -> dict[str, Any]:
        self.generation += 1
        self.rng_counter += 1
        t_start = time.perf_counter()

        preds, flags = execute_population_torch(
            self.population, self.xs, device=self.device, buffer=self.vm_buffer
        )
        diff = preds - self.ys.unsqueeze(0)
        mse = (diff**2).mean(dim=1)
        invalid = flags.any(dim=1) | torch.isnan(mse) | torch.isinf(mse)
        fitness = torch.where(invalid, mse + 1e6, mse)

        sorted_fit, sorted_idx = torch.sort(fitness)
        sorted_pop = self.population[sorted_idx]
        sorted_mse = mse[sorted_idx]

        gen_best_fit = float(sorted_fit[0].item())
        gen_best_mse = float(sorted_mse[0].item())
        if gen_best_fit < self.best_fitness:
            self.best_fitness = gen_best_fit
            self.best_mse = gen_best_mse
            self.best_program = sorted_pop[0].cpu().numpy().astype(np.uint32)

        pop_size = self.config.pop_size
        k_elites = min(self.config.elite_k, pop_size)
        elites = sorted_pop[:k_elites]

        n_inject = max(
            int(np.ceil(self.config.random_inject_p * pop_size)),
            int(np.ceil(0.10 * pop_size)),
        )
        n_offspring = pop_size - k_elites - n_inject
        pool_size = max(4, min(pop_size, max(20, int(0.25 * pop_size))))

        n_pairs = (n_offspring + 1) // 2
        p1 = gpu_tournament_selection(
            sorted_pop, sorted_fit, n_pairs, self.config.tournament_size, pool_size
        )
        p2 = gpu_tournament_selection(
            sorted_pop, sorted_fit, n_pairs, self.config.tournament_size, pool_size
        )

        c1, c2 = gpu_crossover_single_point(p1, p2, crossover_p=self.config.crossover_p)
        offspring = torch.cat([c1, c2], dim=0)[:n_offspring]

        # Grammar-constrained mutation
        mutated_offspring = grammar_mutate_batch(
            offspring,
            device=self.device,
            p_mut=self.config.gene_mut_p,
            seed=self.rng_counter,
        )

        # Grammar-constrained injections
        injected = sample_grammar_batch(n_inject, device=self.device, seed=self.rng_counter + 777)

        self.population = torch.cat([elites, mutated_offspring, injected], dim=0)[:pop_size]
        self._sync()
        t_step = time.perf_counter() - t_start

        valid_count = int((~invalid).sum().item())
        return {
            "generation": self.generation,
            "best_fitness": self.best_fitness,
            "best_mse": self.best_mse,
            "gen_best_fit": gen_best_fit,
            "gen_best_mse": gen_best_mse,
            "valid_rate": float(valid_count / pop_size),
            "step_time_s": t_step,
            "candidates_per_sec": pop_size / max(t_step, 1e-6),
        }
