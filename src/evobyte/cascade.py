"""Streaming GPU cascade with bounded memory and stage accounting (P18 scope).

Integrates S0 -> S1 -> S2 -> S3 into the GPU-resident search loop.
Bounds VRAM footprint to active chunks, compacts survivors on device,
and audits rejection safety against full evaluation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import torch

from evobyte.batching import compute_chunk_size
from evobyte.bytecode import N_REGS
from evobyte.vm_torch import execute_population_torch, get_default_device


@dataclass
class CascadeStageCounters:
    """Accounting counters for stage entries, survivors, and rejection reasons."""

    s0_entries: int = 0
    s0_survivors: int = 0
    s0_rejected_invalid: int = 0

    s1_entries: int = 0
    s1_survivors: int = 0
    s1_rejected_error: int = 0
    s1_rejected_invalid: int = 0

    s2_entries: int = 0
    s2_survivors: int = 0
    s2_rejected_error: int = 0
    s2_rejected_invalid: int = 0

    s3_entries: int = 0
    s3_survivors: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert counters to dictionary with computed survivor rates."""
        s0_rate = self.s0_survivors / max(self.s0_entries, 1)
        s1_rate = self.s1_survivors / max(self.s1_entries, 1)
        s2_rate = self.s2_survivors / max(self.s2_entries, 1)
        s3_rate = self.s3_survivors / max(self.s3_entries, 1)

        return {
            "s0_entries": self.s0_entries,
            "s0_survivors": self.s0_survivors,
            "s0_rejected_invalid": self.s0_rejected_invalid,
            "s0_survivor_rate": float(s0_rate),
            "s1_entries": self.s1_entries,
            "s1_survivors": self.s1_survivors,
            "s1_rejected_error": self.s1_rejected_error,
            "s1_rejected_invalid": self.s1_rejected_invalid,
            "s1_survivor_rate": float(s1_rate),
            "s2_entries": self.s2_entries,
            "s2_survivors": self.s2_survivors,
            "s2_rejected_error": self.s2_rejected_error,
            "s2_rejected_invalid": self.s2_rejected_invalid,
            "s2_survivor_rate": float(s2_rate),
            "s3_entries": self.s3_entries,
            "s3_survivors": self.s3_survivors,
            "s3_survivor_rate": float(s3_rate),
        }


@dataclass
class CascadeConfig:
    """Configuration for streaming GPU cascade."""

    vram_budget_mb: float = 7500.0
    safety_factor: float = 0.75
    reserve_mb: float = 512.0
    s1_points: int = 32
    s2_points: int = 256
    k_cutoff: float = 10.0
    elite_margin: float = 5.0
    enable_cascade: bool = True
    early_stop_mse: float = 1e-5


def get_representative_indices(
    total_points: int,
    n_samples: int,
    device: torch.device | str | None = None,
) -> torch.Tensor:
    """Deterministic equispaced representative sample spanning the training domain."""
    dev = torch.device(device) if device is not None else get_default_device()
    n = min(total_points, max(1, n_samples))
    if n == total_points:
        return torch.arange(total_points, dtype=torch.long, device=dev)
    # Linspace rounding guarantees endpoints and uniform interior spacing
    return torch.linspace(0, total_points - 1, n, device=dev).round().long()


def query_available_vram_mb(
    device: torch.device,
    budget_mb: float = 7500.0,
    safety_factor: float = 0.75,
    reserve_mb: float = 512.0,
) -> float:
    """Query currently free VRAM with safety reserve."""
    if device.type == "cuda" and torch.cuda.is_available():
        free_bytes, _ = torch.cuda.mem_get_info(device)
        free_mb = free_bytes / (1024 * 1024)
        usable_mb = max(100.0, (free_mb - reserve_mb) * safety_factor)
        return min(budget_mb, usable_mb)
    return budget_mb


class StreamingGPUCascade:
    """Streaming multi-stage GPU cascade with bounded memory and on-device survivor compaction."""

    def __init__(
        self,
        config: CascadeConfig | None = None,
        device: torch.device | str | None = None,
    ) -> None:
        self.device = torch.device(device) if device is not None else get_default_device()
        self.config = config if config is not None else CascadeConfig()
        self.counters = CascadeStageCounters()
        self.oom_retries = 0

    def _execute_stage_chunked(
        self,
        programs: torch.Tensor,
        xs: torch.Tensor,
        ys: torch.Tensor,
        x1s: torch.Tensor | None = None,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """Execute candidates across given points in streaming chunks, returning (mse, invalid)."""
        P = programs.shape[0]
        B = xs.shape[0]

        if P == 0:
            return torch.empty(0, device=self.device), torch.empty(
                0, dtype=torch.bool, device=self.device
            )

        eff_budget = query_available_vram_mb(
            self.device,
            budget_mb=self.config.vram_budget_mb,
            safety_factor=self.config.safety_factor,
            reserve_mb=self.config.reserve_mb,
        )
        chunk_size = min(P, compute_chunk_size(B, vram_budget_mb=eff_budget))

        mse_chunks = []
        invalid_chunks = []
        idx = 0

        while idx < P:
            end = min(idx + chunk_size, P)
            batch = programs[idx:end]
            try:
                preds, flags = execute_population_torch(batch, xs, x1s=x1s, device=self.device)
                diff = preds - ys.unsqueeze(0)
                chunk_mse = (diff**2).mean(dim=1)
                chunk_invalid = flags.any(dim=1)

                mse_chunks.append(chunk_mse)
                invalid_chunks.append(chunk_invalid)
                idx = end
            except (torch.cuda.OutOfMemoryError, MemoryError):
                self.oom_retries += 1
                if chunk_size > 1:
                    if self.device.type == "cuda":
                        torch.cuda.empty_cache()
                    chunk_size = max(1, chunk_size // 2)
                else:
                    raise

        all_mse = torch.cat(mse_chunks, dim=0)
        all_invalid = torch.cat(invalid_chunks, dim=0)
        return all_mse, all_invalid

    def evaluate(
        self,
        programs: torch.Tensor,
        xs: torch.Tensor,
        ys: torch.Tensor,
        elite_score: float | None = None,
        x1s: torch.Tensor | None = None,
    ) -> tuple[torch.Tensor, torch.Tensor, CascadeStageCounters]:
        """Execute full S0 -> S1 -> S2 -> S3 streaming cascade."""
        P = programs.shape[0]
        N = xs.shape[0]
        self.counters = CascadeStageCounters()

        # Final score & invalid arrays
        fitnesses = torch.full((P,), 1e9, dtype=torch.float32, device=self.device)
        mses = torch.full((P,), 1e9, dtype=torch.float32, device=self.device)

        # ----------------------------------------------------
        # Stage 0: Bytecode Static Filter (S0)
        # ----------------------------------------------------
        self.counters.s0_entries = P
        ops = programs & 0xFF
        dsts = (programs >> 8) & 0xFF
        as_ = (programs >> 16) & 0xFF
        has_r7 = ((dsts == 7) & (ops != 0)).any(dim=1)
        valid_s0 = (
            has_r7 & (ops <= 15).all(dim=1) & (dsts < N_REGS).all(dim=1) & (as_ < N_REGS).all(dim=1)
        )

        s0_survivor_indices = torch.nonzero(valid_s0).squeeze(1)
        self.counters.s0_survivors = int(s0_survivor_indices.numel())
        self.counters.s0_rejected_invalid = P - self.counters.s0_survivors

        if not self.config.enable_cascade:
            # No-cascade reference path: evaluate all valid S0 candidates directly on full S3
            if self.counters.s0_survivors > 0:
                full_mse, full_invalid = self._execute_stage_chunked(
                    programs[s0_survivor_indices], xs, ys, x1s=x1s
                )
                self.counters.s3_entries = self.counters.s0_survivors
                self.counters.s3_survivors = int((~full_invalid).sum().item())

                c_ops = programs[s0_survivor_indices] & 0xFF
                comp = (c_ops != 0).sum(dim=1).to(torch.float32)
                penalized = torch.where(full_invalid, full_mse + 1e6, full_mse)
                fitnesses[s0_survivor_indices] = penalized + 0.001 * comp
                mses[s0_survivor_indices] = full_mse
            return fitnesses, mses, self.counters

        if self.counters.s0_survivors == 0:
            return fitnesses, mses, self.counters

        # ----------------------------------------------------
        # Stage 1: Coarse Screening (32 Representative Points)
        # ----------------------------------------------------
        self.counters.s1_entries = self.counters.s0_survivors
        s1_pts = min(N, self.config.s1_points)
        s1_idx = get_representative_indices(N, s1_pts, device=self.device)
        xs_s1 = xs[s1_idx]
        ys_s1 = ys[s1_idx]
        x1s_s1 = x1s[s1_idx] if x1s is not None else None

        s1_programs = programs[s0_survivor_indices]
        s1_mse, s1_invalid = self._execute_stage_chunked(s1_programs, xs_s1, ys_s1, x1s=x1s_s1)

        # Cutoff rule
        if elite_score is not None and elite_score < 1e5:
            cutoff = self.config.k_cutoff * max(elite_score, self.config.elite_margin)
        else:
            cutoff = 1e5

        s1_pass_error = s1_mse <= cutoff
        s1_pass_valid = ~s1_invalid
        s1_survivor_mask = s1_pass_error & s1_pass_valid

        # If too aggressively pruned, retain top candidates to ensure search continues
        min_survivors = max(4, min(16, self.counters.s0_survivors))
        if int(s1_survivor_mask.sum().item()) < min_survivors:
            sort_order = torch.argsort(torch.where(s1_invalid, s1_mse + 1e6, s1_mse))
            s1_survivor_mask = torch.zeros_like(s1_survivor_mask)
            s1_survivor_mask[sort_order[:min_survivors]] = True

        s1_survivor_indices = s0_survivor_indices[s1_survivor_mask]
        self.counters.s1_survivors = int(s1_survivor_indices.numel())

        rejected_s1 = ~s1_survivor_mask
        self.counters.s1_rejected_invalid = int((rejected_s1 & s1_invalid).sum().item())
        self.counters.s1_rejected_error = int((rejected_s1 & (~s1_invalid)).sum().item())

        # ----------------------------------------------------
        # Stage 2: Fine Discrimination (256 Representative Points)
        # ----------------------------------------------------
        self.counters.s2_entries = self.counters.s1_survivors
        s2_pts = min(N, self.config.s2_points)
        if s2_pts > s1_pts:
            s2_idx = get_representative_indices(N, s2_pts, device=self.device)
            xs_s2 = xs[s2_idx]
            ys_s2 = ys[s2_idx]
            x1s_s2 = x1s[s2_idx] if x1s is not None else None

            s2_programs = programs[s1_survivor_indices]
            s2_mse, s2_invalid = self._execute_stage_chunked(s2_programs, xs_s2, ys_s2, x1s=x1s_s2)

            s2_pass_error = s2_mse <= cutoff
            s2_pass_valid = ~s2_invalid
            s2_survivor_mask = s2_pass_error & s2_pass_valid

            if int(s2_survivor_mask.sum().item()) < min_survivors:
                sort_order = torch.argsort(torch.where(s2_invalid, s2_mse + 1e6, s2_mse))
                s2_survivor_mask = torch.zeros_like(s2_survivor_mask)
                s2_survivor_mask[sort_order[:min_survivors]] = True

            s2_survivor_indices = s1_survivor_indices[s2_survivor_mask]
            self.counters.s2_survivors = int(s2_survivor_indices.numel())

            rejected_s2 = ~s2_survivor_mask
            self.counters.s2_rejected_invalid = int((rejected_s2 & s2_invalid).sum().item())
            self.counters.s2_rejected_error = int((rejected_s2 & (~s2_invalid)).sum().item())
        else:
            s2_survivor_indices = s1_survivor_indices
            self.counters.s2_survivors = self.counters.s1_survivors

        # ----------------------------------------------------
        # Stage 3: Full Verification (All N Training Points)
        # ----------------------------------------------------
        self.counters.s3_entries = self.counters.s2_survivors
        s3_programs = programs[s2_survivor_indices]
        s3_mse, s3_invalid = self._execute_stage_chunked(s3_programs, xs, ys, x1s=x1s)
        self.counters.s3_survivors = int((~s3_invalid).sum().item())

        c_ops = s3_programs & 0xFF
        comp = (c_ops != 0).sum(dim=1).to(torch.float32)
        penalized_s3 = torch.where(s3_invalid, s3_mse + 1e6, s3_mse)
        fitnesses[s2_survivor_indices] = penalized_s3 + 0.001 * comp
        mses[s2_survivor_indices] = s3_mse

        return fitnesses, mses, self.counters


def audit_cascade_accuracy(
    programs: torch.Tensor,
    xs: torch.Tensor,
    ys: torch.Tensor,
    cascade: StreamingGPUCascade,
    top_k: int = 16,
    x1s: torch.Tensor | None = None,
) -> dict[str, Any]:
    """Audit streaming cascade false-rejections against full reference scoring."""
    # 1. Full ground truth evaluation with S0 static validity gate
    ops = programs & 0xFF
    dsts = (programs >> 8) & 0xFF
    as_ = (programs >> 16) & 0xFF
    has_r7 = ((dsts == 7) & (ops != 0)).any(dim=1)
    s0_valid = (
        has_r7 & (ops <= 15).all(dim=1) & (dsts < N_REGS).all(dim=1) & (as_ < N_REGS).all(dim=1)
    )

    full_mse, full_invalid = cascade._execute_stage_chunked(programs, xs, ys, x1s=x1s)
    c_ops = programs & 0xFF
    comp = (c_ops != 0).sum(dim=1).to(torch.float32)
    oracle_fitness = torch.where(full_invalid, full_mse + 1e6, full_mse) + 0.001 * comp
    oracle_fitness = torch.where(
        s0_valid, oracle_fitness, torch.tensor(1e9, device=programs.device)
    )

    oracle_best_fit, oracle_order = torch.sort(oracle_fitness)
    oracle_topk_idx = set(oracle_order[:top_k].cpu().tolist())

    # 2. Cascade evaluation
    best_oracle_score = float(oracle_best_fit[0].item())
    casc_fitness, _, counters = cascade.evaluate(
        programs, xs, ys, elite_score=best_oracle_score, x1s=x1s
    )

    # 3. Identify false rejections
    # Evaluated candidates in S3 are those with finite (non-1e9) fitness
    evaluated_in_s3 = set(torch.nonzero(casc_fitness < 1e8).squeeze(1).cpu().tolist())
    false_rejections = [idx for idx in oracle_topk_idx if idx not in evaluated_in_s3]
    false_rejection_rate = len(false_rejections) / float(top_k)

    casc_best_fit = float(casc_fitness.min().item())
    quality_loss = abs(casc_best_fit - best_oracle_score)

    return {
        "total_candidates": int(programs.shape[0]),
        "oracle_top_k": top_k,
        "oracle_best_fitness": best_oracle_score,
        "cascade_best_fitness": casc_best_fit,
        "quality_loss": quality_loss,
        "false_rejections": len(false_rejections),
        "false_rejection_rate": false_rejection_rate,
        "counters": counters.to_dict(),
        "passed_predeclared_audit": false_rejection_rate <= 0.05,
    }
