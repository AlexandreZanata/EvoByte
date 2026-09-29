"""VRAM-budget-aware batching and OOM-safe chunking policy (spec: docs/VM.md, P06)."""

from __future__ import annotations

import numpy as np
import torch

from evobyte.vm_torch import execute_population_torch, get_default_device

BYTES_PER_FLOAT32 = 4
N_REGS = 8


def compute_chunk_size(
    n_points: int,
    vram_budget_mb: float = 7500.0,
    safety_factor: float = 0.75,
) -> int:
    """Compute maximum candidate programs per chunk under a VRAM budget.

    Memory model per candidate:
    - Registers: 8 regs x n_points x 4 bytes = 32 x n_points bytes.
    - Intermediate tensor ops & invalid masks: ~16 x n_points bytes.
    - Total per candidate: ~48 x n_points bytes.
    """
    if n_points <= 0:
        raise ValueError(f"n_points must be > 0, got {n_points}")
    if vram_budget_mb <= 0:
        raise ValueError(f"vram_budget_mb must be > 0, got {vram_budget_mb}")

    bytes_per_candidate = 48 * n_points
    available_bytes = vram_budget_mb * 1024 * 1024 * safety_factor
    chunk = int(available_bytes / bytes_per_candidate)
    return max(1, chunk)


def execute_chunked(
    programs: np.ndarray | torch.Tensor,
    xs: np.ndarray | torch.Tensor,
    x1s: np.ndarray | torch.Tensor | None = None,
    chunk_size: int | None = None,
    vram_budget_mb: float = 7500.0,
    device: torch.device | str | None = None,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Execute a population of programs in VRAM-budgeted slices with OOM-safe dynamic fallback.

    If an OutOfMemoryError is encountered during chunk execution, the chunk size is halved,
    the cache is emptied, and the chunk is retried until execution succeeds.
    """
    if device is None:
        device = get_default_device()
    else:
        device = torch.device(device)

    total_programs = len(programs)
    if total_programs == 0:
        b_len = len(xs)
        return torch.empty((0, b_len), device=device), torch.empty(
            (0, b_len), dtype=torch.bool, device=device
        )

    n_points = len(xs)
    if chunk_size is None:
        current_chunk = min(total_programs, compute_chunk_size(n_points, vram_budget_mb))
    else:
        current_chunk = min(total_programs, max(1, int(chunk_size)))

    all_preds = []
    all_flags = []

    idx = 0
    while idx < total_programs:
        end = min(idx + current_chunk, total_programs)
        batch_slice = programs[idx:end]

        try:
            p_preds, p_flags = execute_population_torch(batch_slice, xs, x1s=x1s, device=device)
            all_preds.append(p_preds)
            all_flags.append(p_flags)
            idx = end
        except (torch.cuda.OutOfMemoryError, MemoryError):
            if current_chunk > 1:
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                current_chunk = max(1, current_chunk // 2)
            else:
                raise

    final_preds = (
        torch.cat(all_preds, dim=0) if all_preds else torch.empty((0, n_points), device=device)
    )
    final_flags = (
        torch.cat(all_flags, dim=0)
        if all_flags
        else torch.empty((0, n_points), dtype=torch.bool, device=device)
    )
    return final_preds, final_flags


def get_recommended_cascade_policy(vram_budget_mb: float = 7500.0) -> dict:
    """Return recommended N x batch grid for 8 GB VRAM."""
    return {
        "vram_budget_mb": vram_budget_mb,
        "stages": [
            {
                "stage": 1,
                "name": "S1 (coarse screening)",
                "target_candidates": 100_000,
                "points": 256,
                "chunk_size": compute_chunk_size(256, vram_budget_mb),
                "est_vram_mb": (compute_chunk_size(256, vram_budget_mb) * 48 * 256) / (1024 * 1024),
                "expected_kill_rate": 0.99,
            },
            {
                "stage": 2,
                "name": "S2 (fine discrimination)",
                "target_candidates": 1_000,
                "points": 4096,
                "chunk_size": compute_chunk_size(4096, vram_budget_mb),
                "est_vram_mb": (min(1000, compute_chunk_size(4096, vram_budget_mb)) * 48 * 4096)
                / (1024 * 1024),
                "expected_kill_rate": 0.99,
            },
            {
                "stage": 3,
                "name": "S3 (full verification)",
                "target_candidates": 10,
                "points": 10_000,
                "chunk_size": compute_chunk_size(10000, vram_budget_mb),
                "est_vram_mb": (10 * 48 * 10_000) / (1024 * 1024),
                "expected_kill_rate": 0.0,
            },
        ],
    }
