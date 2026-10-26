"""Functional Priority Bytecode Engine (P193).

Implements vectorized priority function evaluation via compact 64-byte bytecode
programs, accelerated greedy constructors with bitmask lookup tables for
extremal combinatorial objects (Cap Sets in F_3^n and Covering Designs via
automorphism orbits), and high-throughput evolutionary synthesis.

Part of the Structured Discovery Program (P191-P200, D043).
"""

from __future__ import annotations

import hashlib
import itertools
import math
import time
from typing import Any, Sequence

import numpy as np

from evobyte.bytecode import (
    CONST_BANK,
    N_INSTR,
    N_REGS,
    decode_instr,
    encode_instr,
    is_valid,
    nop_program,
)
from evobyte.frontier_catalogue import verify_cap_set
from evobyte.narrow_gap_catalogue import verify_covering_design
from evobyte.priority_evolution import _sample_valid_program, mutate_priority_program
from evobyte.symmetry_engine import CoveringOrbitEngine

try:
    import torch

    _TORCH_AVAILABLE = True
except ImportError:  # pragma: no cover
    _TORCH_AVAILABLE = False


class FunctionalPriorityEvaluator:
    """Evaluates bytecode priority functions vectorially over candidate feature matrices."""

    def __init__(self, const_bank: Sequence[float] | None = None) -> None:
        self.const_bank = np.asarray(
            const_bank if const_bank is not None else CONST_BANK, dtype=np.float32
        )

    def evaluate_vectorized(
        self,
        program: np.ndarray,
        features: np.ndarray,
        context: np.ndarray | None = None,
    ) -> np.ndarray:
        """Evaluate a single 16-instruction bytecode program over an (N, D) feature matrix.

        Returns an (N,) float32 array of priority scores extracted from register 7.
        Handles all v1 instructions safely with bounded numerical behavior.
        """
        feats = np.asarray(features, dtype=np.float32)
        if feats.ndim == 1:
            feats = feats.reshape(1, -1)
        n_points, n_feats = feats.shape

        regs = np.zeros((n_points, N_REGS), dtype=np.float32)
        n_init = min(7, n_feats)
        if n_init > 0:
            regs[:, :n_init] = feats[:, :n_init]

        ctx = (
            np.asarray(context, dtype=np.float32)
            if context is not None
            else np.zeros((n_points, 16), dtype=np.float32)
        )
        if ctx.ndim == 1:
            ctx = np.tile(ctx, (n_points, 1))

        prog = np.asarray(program, dtype=np.uint32)
        if prog.shape != (N_INSTR,):
            return np.full((n_points,), -np.inf, dtype=np.float32)

        for word in prog:
            op, dst, a, _b = decode_instr(int(word))
            if op == 0x00:
                continue
            b = int(_b)
            if dst >= N_REGS or a >= N_REGS:
                return np.full((n_points,), -np.inf, dtype=np.float32)

            if op == 0x10:  # CTX: r[dst] = ctx[b & 0x0F]
                idx = b & 0x0F
                regs[:, dst] = ctx[:, idx] if idx < ctx.shape[1] else 0.0
                continue
            elif op == 0x11:  # FEAT: r[dst] = feat[b & 0x0F]
                idx = b & 0x0F
                regs[:, dst] = feats[:, idx] if idx < n_feats else 0.0
                continue

            if op == 0x0F:  # IMM
                rb = np.full((n_points,), float(b), dtype=np.float32)
            else:
                rb = regs[:, b % N_REGS]

            ra = regs[:, a]

            if op == 0x01:  # ADD
                with np.errstate(invalid="ignore", over="ignore"):
                    regs[:, dst] = ra + rb
            elif op == 0x02:  # SUB
                with np.errstate(invalid="ignore", over="ignore"):
                    regs[:, dst] = ra - rb
            elif op == 0x03:  # MUL
                with np.errstate(invalid="ignore", over="ignore"):
                    regs[:, dst] = ra * rb
            elif op == 0x04:  # DIV
                nz = np.abs(rb) > 1e-7
                with np.errstate(divide="ignore", invalid="ignore"):
                    regs[:, dst] = np.where(nz, ra / np.where(nz, rb, 1.0), 0.0)
            elif op == 0x05:  # NEG
                regs[:, dst] = -ra
            elif op == 0x06:  # CONST
                regs[:, dst] = self.const_bank[b % len(self.const_bank)]
            elif op == 0x07:  # EXP
                regs[:, dst] = np.exp(np.clip(ra, -15.0, 15.0))
            elif op == 0x08:  # LOG
                regs[:, dst] = np.log(np.maximum(np.abs(ra), 1e-7))
            elif op == 0x09:  # POW
                base = np.maximum(ra, 0.0)
                exp = np.clip(rb, -5.0, 5.0)
                pos_base = base > 1e-7
                nonneg_exp = exp >= 0.0
                safe = pos_base | nonneg_exp
                with np.errstate(divide="ignore", invalid="ignore"):
                    regs[:, dst] = np.where(safe, np.power(np.where(safe, base, 1.0), exp), 0.0)
            elif op == 0x0A:  # SQRT
                regs[:, dst] = np.sqrt(np.maximum(ra, 0.0))
            elif op == 0x0B:  # ABS
                regs[:, dst] = np.abs(ra)
            elif op == 0x0C:  # MAX
                regs[:, dst] = np.maximum(ra, rb)
            elif op == 0x0D:  # MIN
                regs[:, dst] = np.minimum(ra, rb)
            elif op == 0x0E:  # CLAMP
                regs[:, dst] = np.clip(ra, -1.0, 1.0)

        scores = regs[:, 7]
        return np.nan_to_num(scores, nan=-1e9, posinf=1e9, neginf=-1e9)


class FastGreedyCapSetBuilder:
    """High-throughput bitmask greedy constructor for Cap Sets in F_3^n."""

    def __init__(self, n: int = 3) -> None:
        if n not in (3, 4):
            raise ValueError(f"FastGreedyCapSetBuilder currently supports n=3 or n=4, got {n}")
        self.n: int = int(n)
        self.points: list[tuple[int, ...]] = list(itertools.product(range(3), repeat=self.n))
        self.n_points: int = len(self.points)
        self._pts_np = np.array(self.points, dtype=np.int32)

        # Precompute third point completing line: -(p + q) mod 3
        third_pt_idx = np.zeros((self.n_points, self.n_points), dtype=np.int32)
        for i in range(self.n_points):
            for j in range(self.n_points):
                target = (-(self._pts_np[i] + self._pts_np[j])) % 3
                idx = int(np.where((self._pts_np == target).all(axis=1))[0][0])
                third_pt_idx[i, j] = idx

        self.third_pt_idx: np.ndarray = third_pt_idx
        self.third_mask: list[list[int]] = [
            [1 << int(third_pt_idx[i, j]) for j in range(self.n_points)]
            for i in range(self.n_points)
        ]
        self.pow2: list[int] = [1 << i for i in range(self.n_points)]

    def build_from_scores(self, scores: Sequence[float] | np.ndarray) -> list[int]:
        """Construct cap set greedily in descending score order using fast bitmasks."""
        arr = np.asarray(scores, dtype=np.float32)
        if len(arr) != self.n_points:
            raise ValueError(f"Expected {self.n_points} scores, got {len(arr)}")

        # Argsort descending (break ties by lower index)
        order = np.argsort(-arr)
        forbidden = 0
        cap: list[int] = []

        pow2 = self.pow2
        third_mask = self.third_mask

        for p_val in order:
            p = int(p_val)
            if not (forbidden & pow2[p]):
                cap.append(p)
                row = third_mask[p]
                for q in cap[:-1]:
                    forbidden |= row[q]

        return cap

    def build_cap_points(self, scores: Sequence[float] | np.ndarray) -> list[tuple[int, ...]]:
        """Return cap set as a list of coordinate integer tuples."""
        indices = self.build_from_scores(scores)
        return [self.points[idx] for idx in indices]

    def batched_build_cap_sizes(self, scores_batch: np.ndarray) -> np.ndarray:
        """Process an (N_batch, n_points) matrix of scores and return cap sizes."""
        batch = np.asarray(scores_batch, dtype=np.float32)
        n_batch = batch.shape[0]
        sizes = np.zeros(n_batch, dtype=np.int32)
        for i in range(n_batch):
            sizes[i] = len(self.build_from_scores(batch[i]))
        return sizes

    def batched_build_cap_sizes_torch(self, scores_tensor: Any, device: Any | None = None) -> Any:
        """GPU/Torch batched greedy cap set constructor for massive throughput."""
        if not _TORCH_AVAILABLE:  # pragma: no cover
            raise RuntimeError("PyTorch is not available for batched_build_cap_sizes_torch")

        scores = scores_tensor.to(device) if device is not None else scores_tensor
        B, N = scores.shape
        third_t = torch.tensor(self.third_pt_idx, device=scores.device, dtype=torch.long)

        order = torch.argsort(scores, dim=1, descending=True)
        forbidden = torch.zeros((B, N), dtype=torch.bool, device=scores.device)
        cap_sizes = torch.zeros(B, dtype=torch.long, device=scores.device)
        cap_members = torch.zeros((B, N), dtype=torch.long, device=scores.device)
        arange_b = torch.arange(B, device=scores.device)

        for k in range(N):
            cand = order[:, k]
            is_forb = forbidden[arange_b, cand]
            accept = ~is_forb
            accept_idx = torch.nonzero(accept).squeeze(1)
            if accept_idx.numel() == 0:
                continue
            p = cand[accept_idx]
            cur_sizes = cap_sizes[accept_idx]

            max_prev = int(cur_sizes.max().item())
            for prev in range(max_prev):
                valid_prev = cur_sizes > prev
                v_idx = accept_idx[valid_prev]
                p_v = p[valid_prev]
                q_v = cap_members[v_idx, prev]
                third = third_t[p_v, q_v]
                forbidden[v_idx, third] = True

            cap_members[accept_idx, cur_sizes] = p
            cap_sizes[accept_idx] += 1

        return cap_sizes


def compute_capset_features(n: int) -> np.ndarray:
    """Precompute informative 16-dimensional geometric and algebraic feature vectors for F_3^n."""
    pts = np.array(list(itertools.product(range(3), repeat=n)), dtype=np.float32)
    n_pts = len(pts)
    feats = np.zeros((n_pts, 16), dtype=np.float32)

    # Centered coordinates: x - 1 in {-1, 0, 1}
    centered = pts - 1.0

    if n == 3:
        feats[:, 0:3] = pts
        feats[:, 3:6] = centered**2
        feats[:, 6] = pts[:, 0] * pts[:, 1]
        feats[:, 7] = pts[:, 1] * pts[:, 2]
        feats[:, 8] = pts[:, 0] * pts[:, 2]
        feats[:, 9] = centered[:, 0] * centered[:, 1]
        feats[:, 10] = centered[:, 1] * centered[:, 2]
        feats[:, 11] = centered[:, 0] * centered[:, 2]
        feats[:, 12] = np.sum(pts, axis=1)
        feats[:, 13] = np.sum(centered**2, axis=1)
        feats[:, 14] = np.prod(pts + 1.0, axis=1)
        feats[:, 15] = np.sum(np.abs(centered), axis=1)
    elif n == 4:
        feats[:, 0:4] = pts
        feats[:, 4:8] = centered**2
        feats[:, 8] = pts[:, 0] * pts[:, 1]
        feats[:, 9] = pts[:, 0] * pts[:, 2]
        feats[:, 10] = pts[:, 0] * pts[:, 3]
        feats[:, 11] = pts[:, 1] * pts[:, 2]
        feats[:, 12] = pts[:, 1] * pts[:, 3]
        feats[:, 13] = pts[:, 2] * pts[:, 3]
        feats[:, 14] = np.sum(pts, axis=1)
        feats[:, 15] = np.sum(centered**2, axis=1)

    return feats


class CapSetPrioritySearch:
    """Synthesizes bytecode priority programs to discover extremal Cap Sets."""

    def __init__(self, n: int = 3, seed: int = 42) -> None:
        self.n: int = int(n)
        self.seed: int = int(seed)
        self.builder: FastGreedyCapSetBuilder = FastGreedyCapSetBuilder(n=self.n)
        self.evaluator: FunctionalPriorityEvaluator = FunctionalPriorityEvaluator()
        self.features: np.ndarray = compute_capset_features(self.n)
        self.rng: np.random.Generator = np.random.default_rng(self.seed)

    def evaluate_program(self, prog: np.ndarray) -> tuple[int, list[tuple[int, ...]]]:
        """Evaluate program, construct cap set, and return (size, point_list)."""
        scores = self.evaluator.evaluate_vectorized(prog, self.features)
        indices = self.builder.build_from_scores(scores)
        pts = [self.builder.points[i] for i in indices]
        return len(pts), pts

    def search(
        self,
        target_size: int,
        max_evaluations: int = 10000,
        max_seconds: float = 10.0,
        pop_size: int = 64,
    ) -> dict[str, Any]:
        """Evolutionary synthesis search for a priority bytecode program reaching target_size."""
        t0 = time.perf_counter()

        # Seed population with valid random programs
        pop: list[np.ndarray] = [_sample_valid_program(self.rng) for _ in range(pop_size)]
        fitness: list[int] = []
        for p in pop:
            sz, _ = self.evaluate_program(p)
            fitness.append(sz)

        best_idx = int(np.argmax(fitness))
        best_prog = pop[best_idx].copy()
        best_size = fitness[best_idx]
        evals = pop_size

        if best_size >= target_size:
            elapsed = time.perf_counter() - t0
            _, best_pts = self.evaluate_program(best_prog)
            is_valid_cap, msg = verify_cap_set(best_pts, self.n)
            return {
                "discovered": True,
                "target_size": target_size,
                "best_size": best_size,
                "program": best_prog,
                "cap_points": best_pts,
                "evaluations": evals,
                "elapsed_sec": elapsed,
                "certified": is_valid_cap,
                "certification_msg": msg,
                "sha256": hashlib.sha256(repr(sorted(best_pts)).encode()).hexdigest(),
            }

        # Evolution loop with elitist tournament selection and point mutations
        while evals < max_evaluations and (time.perf_counter() - t0) < max_seconds:
            for i in range(pop_size):
                # 2-tournament selection
                i1, i2 = int(self.rng.integers(0, pop_size)), int(self.rng.integers(0, pop_size))
                p_idx = i1 if fitness[i1] >= fitness[i2] else i2

                child = mutate_priority_program(pop[p_idx], self.rng)
                child_sz, _ = self.evaluate_program(child)
                evals += 1

                if child_sz >= fitness[p_idx]:
                    pop[p_idx] = child
                    fitness[p_idx] = child_sz
                    if child_sz > best_size:
                        best_size = child_sz
                        best_prog = child.copy()

                if best_size >= target_size:
                    break

            if best_size >= target_size:
                break

        elapsed = time.perf_counter() - t0
        _, best_pts = self.evaluate_program(best_prog)
        is_valid_cap, msg = verify_cap_set(best_pts, self.n)

        return {
            "discovered": best_size >= target_size,
            "target_size": target_size,
            "best_size": best_size,
            "program": best_prog,
            "cap_points": best_pts,
            "evaluations": evals,
            "elapsed_sec": elapsed,
            "certified": is_valid_cap,
            "certification_msg": msg,
            "sha256": hashlib.sha256(repr(sorted(best_pts)).encode()).hexdigest(),
        }


class CoveringOrbitPriorityBuilder:
    """Greedy constructor for covering designs C(v, k, t) guided by bytecode priority scores."""

    def __init__(self, v: int, k: int, t: int) -> None:
        self.v: int = v
        self.k: int = k
        self.t: int = t
        self.orbit_engine: CoveringOrbitEngine = CoveringOrbitEngine(v=v, k=k, t=t)
        self.base_blocks: list[tuple[int, ...]] = self.orbit_engine.compute_orbit_representatives()
        self.all_t_subsets: list[tuple[int, ...]] = list(itertools.combinations(range(v), t))
        self.n_subsets: int = len(self.all_t_subsets)
        self.subset_to_idx: dict[tuple[int, ...], int] = {
            s: i for i, s in enumerate(self.all_t_subsets)
        }

        # Precompute coverage masks for each base block orbit
        self.orbit_masks: list[int] = []
        self.orbit_blocks: list[list[tuple[int, ...]]] = []
        for rep in self.base_blocks:
            orbit = self.orbit_engine.group.orbit(rep)
            self.orbit_blocks.append(orbit)
            mask = 0
            for blk in orbit:
                for sub in itertools.combinations(blk, t):
                    idx = self.subset_to_idx[tuple(sorted(sub))]
                    mask |= 1 << idx
            self.orbit_masks.append(mask)

        # Precompute feature matrix for base blocks
        self.features: np.ndarray = self._compute_block_features()

    def _compute_block_features(self) -> np.ndarray:
        n_reps = len(self.base_blocks)
        feats = np.zeros((n_reps, 16), dtype=np.float32)
        target_full = (1 << self.n_subsets) - 1

        for i, rep in enumerate(self.base_blocks):
            orbit_size = len(self.orbit_blocks[i])
            covered_count = bin(self.orbit_masks[i]).count("1")

            feats[i, 0] = float(len(rep))
            feats[i, 1] = float(orbit_size)
            feats[i, 2] = float(covered_count)
            feats[i, 3] = float(covered_count / orbit_size if orbit_size > 0 else 0.0)
            feats[i, 4] = float(np.mean(rep))
            feats[i, 5] = float(np.std(rep))
            diffs = [
                (rep[b] - rep[a]) % self.v for a in range(len(rep)) for b in range(a + 1, len(rep))
            ]
            feats[i, 6] = float(len(set(diffs)))
            feats[i, 7] = float(len(diffs))

        return feats

    def build_covering(
        self, scores: Sequence[float] | np.ndarray, one_based: bool = False
    ) -> list[tuple[int, ...]]:
        """Greedily select base block orbits in priority order until all t-subsets are covered."""
        arr = np.asarray(scores, dtype=np.float32)
        order = np.argsort(-arr)

        selected_blocks: list[tuple[int, ...]] = []
        current_mask = 0
        target_mask = (1 << self.n_subsets) - 1

        for idx_val in order:
            idx = int(idx_val)
            mask = self.orbit_masks[idx]
            # Only add if it provides new coverage
            if (mask & ~current_mask) != 0:
                current_mask |= mask
                selected_blocks.extend(self.orbit_blocks[idx])
                if current_mask == target_mask:
                    break

        if one_based:
            return [tuple(x + 1 for x in blk) for blk in selected_blocks]
        return selected_blocks


def measure_priority_throughput(
    n: int = 3, n_iterations: int = 50000, use_torch: bool = False
) -> dict[str, float]:
    """Measure complete Cap Set constructions per second on CPU (or GPU)."""
    builder = FastGreedyCapSetBuilder(n=n)
    evaluator = FunctionalPriorityEvaluator()
    features = compute_capset_features(n)

    # Sample a canonical valid program
    prog = nop_program()
    prog[0] = encode_instr(0x01, dst=7, a=0, b=1)

    # Compute baseline scores
    scores = evaluator.evaluate_vectorized(prog, features)

    t0 = time.perf_counter()
    if use_torch and _TORCH_AVAILABLE and torch.cuda.is_available():
        dev = torch.device("cuda")
        scores_t = torch.from_numpy(scores).to(dev).unsqueeze(0).repeat(n_iterations, 1)
        torch.cuda.synchronize()
        t0 = time.perf_counter()
        builder.batched_build_cap_sizes_torch(scores_t, device=dev)
        torch.cuda.synchronize()
        t1 = time.perf_counter()
    else:
        # Fast CPU bitmask loop
        pow2 = builder.pow2
        third_mask = builder.third_mask
        order = [int(x) for x in np.argsort(-scores)]

        t0 = time.perf_counter()
        for _ in range(n_iterations):
            forbidden = 0
            cap: list[int] = []
            for p in order:
                if not (forbidden & pow2[p]):
                    cap.append(p)
                    row = third_mask[p]
                    for q in cap[:-1]:
                        forbidden |= row[q]
        t1 = time.perf_counter()

    elapsed = t1 - t0
    rate = float(n_iterations) / elapsed if elapsed > 0 else 0.0

    return {
        "n": float(n),
        "iterations": float(n_iterations),
        "elapsed_sec": float(elapsed),
        "constructions_per_sec": float(rate),
    }
