"""Micro neural bytecode generator and sampler (spec: docs/phases/P12-neural-generator.md)."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch import nn

from evobyte.bytecode import (
    MAX_RISKY_CHAIN,
    N_INSTR,
    RISKY_OPS,
    decode_instr,
    encode_instr,
    is_valid,
)
from evobyte.evolution import mutate_candidate

MIN_GENERATOR_PARAMS = 100_000
MAX_GENERATOR_PARAMS = 5_000_000
DEFAULT_VRAM_CAP_MB = 100.0


@dataclass
class GeneratorConfig:
    """Hyperparameters for micro neural bytecode generator."""

    d_model: int = 128
    nhead: int = 4
    num_layers: int = 3
    dim_feedforward: int = 256
    dropout: float = 0.05
    lr: float = 1e-3
    batch_size: int = 64
    temperature: float = 0.8
    vram_cap_mb: float = DEFAULT_VRAM_CAP_MB


class BytecodeAutoregressiveModel(nn.Module):
    """Causal Transformer predicting P(next_instruction | prefix) for 16-instruction chromosomes."""

    def __init__(
        self,
        d_model: int = 128,
        nhead: int = 4,
        num_layers: int = 3,
        dim_feedforward: int = 256,
        dropout: float = 0.05,
    ) -> None:
        super().__init__()
        self.d_model = d_model
        self.bos_embed = nn.Parameter(torch.randn(1, 1, d_model) * 0.02)

        # Token embeddings for instruction components
        self.op_embed = nn.Embedding(16, d_model)
        self.dst_embed = nn.Embedding(8, d_model)
        self.a_embed = nn.Embedding(8, d_model)
        self.b_embed = nn.Embedding(16, d_model)
        self.pos_embed = nn.Embedding(N_INSTR + 1, d_model)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=True,
            activation="gelu",
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)

        # Output projection heads for instruction components
        self.head_op = nn.Linear(d_model, 16)
        self.head_dst = nn.Linear(d_model, 8)
        self.head_a = nn.Linear(d_model, 8)
        self.head_b = nn.Linear(d_model, 16)

    def count_parameters(self) -> int:
        return sum(p.numel() for p in self.parameters())

    def resident_memory_mb(self) -> float:
        param_bytes = sum(p.numel() * p.element_size() for p in self.parameters())
        buffer_bytes = sum(b.numel() * b.element_size() for b in self.buffers())
        return float((param_bytes + buffer_bytes) / (1024 * 1024))

    def forward_loss(
        self,
        ops: torch.Tensor,
        dsts: torch.Tensor,
        as_: torch.Tensor,
        bs: torch.Tensor,
    ) -> torch.Tensor:
        """Compute autoregressive cross-entropy loss given target token sequences (B, 16)."""
        B, T = ops.shape
        pos = torch.arange(T, device=ops.device).unsqueeze(0).expand(B, -1)

        # Inputs: BOS at position 0, followed by previous tokens
        prev_ops = ops[:, :-1]
        prev_dsts = dsts[:, :-1]
        prev_as = as_[:, :-1]
        prev_bs = bs[:, :-1]

        prev_emb = (
            self.op_embed(prev_ops)
            + self.dst_embed(prev_dsts)
            + self.a_embed(prev_as)
            + self.b_embed(prev_bs)
        )
        x = torch.cat([self.bos_embed.expand(B, 1, -1), prev_emb], dim=1) + self.pos_embed(pos)

        mask = nn.Transformer.generate_square_subsequent_mask(T, device=ops.device)
        h = self.transformer(x, mask=mask, is_causal=True)

        loss = (
            nn.functional.cross_entropy(self.head_op(h).reshape(-1, 16), ops.reshape(-1))
            + nn.functional.cross_entropy(self.head_dst(h).reshape(-1, 8), dsts.reshape(-1))
            + nn.functional.cross_entropy(self.head_a(h).reshape(-1, 8), as_.reshape(-1))
            + nn.functional.cross_entropy(self.head_b(h).reshape(-1, 16), bs.reshape(-1))
        )
        return loss

    def sample(
        self,
        n: int,
        prefix_ops: torch.Tensor | None = None,
        prefix_dsts: torch.Tensor | None = None,
        prefix_as: torch.Tensor | None = None,
        prefix_bs: torch.Tensor | None = None,
        temperature: float = 0.8,
        device: torch.device | str = "cpu",
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """Autoregressively sample N sequences of length 16, optionally conditioned on prefix."""
        self.eval()
        dev = torch.device(device)
        temp = max(1e-3, float(temperature))

        with torch.no_grad():
            k = prefix_ops.shape[1] if prefix_ops is not None else 0
            curr_ops = (
                prefix_ops.clone().to(dev)
                if prefix_ops is not None
                else torch.zeros((n, 0), dtype=torch.long, device=dev)
            )
            curr_dsts = (
                prefix_dsts.clone().to(dev)
                if prefix_dsts is not None
                else torch.zeros((n, 0), dtype=torch.long, device=dev)
            )
            curr_as = (
                prefix_as.clone().to(dev)
                if prefix_as is not None
                else torch.zeros((n, 0), dtype=torch.long, device=dev)
            )
            curr_bs = (
                prefix_bs.clone().to(dev)
                if prefix_bs is not None
                else torch.zeros((n, 0), dtype=torch.long, device=dev)
            )

            for step in range(k, N_INSTR):
                seq_len = step + 1
                pos = torch.arange(seq_len, device=dev).unsqueeze(0).expand(n, -1)
                if step == 0:
                    x = self.bos_embed.expand(n, 1, -1) + self.pos_embed(pos)
                else:
                    prev_emb = (
                        self.op_embed(curr_ops)
                        + self.dst_embed(curr_dsts)
                        + self.a_embed(curr_as)
                        + self.b_embed(curr_bs)
                    )
                    x = torch.cat(
                        [self.bos_embed.expand(n, 1, -1), prev_emb], dim=1
                    ) + self.pos_embed(pos)

                mask = nn.Transformer.generate_square_subsequent_mask(seq_len, device=dev)
                h = self.transformer(x, mask=mask, is_causal=True)[:, -1, :]

                op = torch.distributions.Categorical(logits=self.head_op(h) / temp).sample()
                dst = torch.distributions.Categorical(logits=self.head_dst(h) / temp).sample()
                a = torch.distributions.Categorical(logits=self.head_a(h) / temp).sample()
                b = torch.distributions.Categorical(logits=self.head_b(h) / temp).sample()

                curr_ops = torch.cat([curr_ops, op.unsqueeze(1)], dim=1)
                curr_dsts = torch.cat([curr_dsts, dst.unsqueeze(1)], dim=1)
                curr_as = torch.cat([curr_as, a.unsqueeze(1)], dim=1)
                curr_bs = torch.cat([curr_bs, b.unsqueeze(1)], dim=1)

            return curr_ops, curr_dsts, curr_as, curr_bs


def assert_generator_resource_cap(
    model: nn.Module,
    max_mb: float = DEFAULT_VRAM_CAP_MB,
) -> dict[str, Any]:
    """Assert model parameter count is in [100K, 5M] and resident memory <= VRAM cap."""
    param_count = sum(p.numel() for p in model.parameters())
    if param_count < MIN_GENERATOR_PARAMS:
        raise ValueError(
            f"Generator parameter count ({param_count}) below minimum threshold ({MIN_GENERATOR_PARAMS})."
        )
    if param_count > MAX_GENERATOR_PARAMS:
        raise ValueError(
            f"Generator parameter count ({param_count}) exceeds maximum cap ({MAX_GENERATOR_PARAMS})."
        )

    param_bytes = sum(p.numel() * p.element_size() for p in model.parameters())
    buffer_bytes = sum(b.numel() * b.element_size() for b in model.buffers())
    resident_mb = float((param_bytes + buffer_bytes) / (1024 * 1024))

    if resident_mb > max_mb:
        raise ValueError(
            f"Generator resident size ({resident_mb:.2f} MB) exceeds VRAM cap ({max_mb:.2f} MB)."
        )

    return {
        "param_count": param_count,
        "resident_mb": resident_mb,
        "vram_cap_mb": max_mb,
    }


def encode_programs_to_tensors(
    programs: np.ndarray | list[np.ndarray],
    device: torch.device | str = "cpu",
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    """Convert an array of uint32 bytecode programs into token tensors (B, 16)."""
    progs = np.asarray(programs, dtype=np.uint32)
    if progs.ndim == 1:
        progs = progs.reshape(1, -1)
    B, T = progs.shape

    ops = np.zeros((B, T), dtype=np.int64)
    dsts = np.zeros((B, T), dtype=np.int64)
    as_ = np.zeros((B, T), dtype=np.int64)
    bs = np.zeros((B, T), dtype=np.int64)

    for b in range(B):
        for t in range(T):
            op, dst, a, b_val = decode_instr(progs[b, t])
            ops[b, t] = int(op) & 0x0F
            dsts[b, t] = int(dst) % 8
            as_[b, t] = int(a) % 8
            bs[b, t] = int(b_val) & 0x0F

    dev = torch.device(device)
    return (
        torch.tensor(ops, dtype=torch.long, device=dev),
        torch.tensor(dsts, dtype=torch.long, device=dev),
        torch.tensor(as_, dtype=torch.long, device=dev),
        torch.tensor(bs, dtype=torch.long, device=dev),
    )


def decode_sampled_tokens_to_programs(
    ops: torch.Tensor,
    dsts: torch.Tensor,
    as_: torch.Tensor,
    bs: torch.Tensor,
) -> np.ndarray:
    """Decode sampled token tensors into valid uint32 bytecode programs, guaranteeing S0-validity."""
    ops_np = ops.cpu().numpy().astype(np.uint32)
    dsts_np = dsts.cpu().numpy().astype(np.uint32)
    as_np = as_.cpu().numpy().astype(np.uint32)
    bs_np = bs.cpu().numpy().astype(np.uint32)

    B, T = ops_np.shape
    progs = np.zeros((B, T), dtype=np.uint32)

    for b_idx in range(B):
        has_r7_write = False
        seen_non_nop = False
        risky_run = 0

        for t in range(T):
            op = int(ops_np[b_idx, t]) & 0x0F
            if op in RISKY_OPS:
                risky_run += 1
                if risky_run > MAX_RISKY_CHAIN:
                    op = 0x01  # Reset to ADD to avoid violating Rule 4
                    risky_run = 0
            else:
                if op != 0x00:
                    risky_run = 0

            dst = int(dsts_np[b_idx, t]) % 8
            a = int(as_np[b_idx, t]) % 8
            b_val = int(bs_np[b_idx, t])
            b = (b_val & 0x0F) if op == 0x0F else (b_val % 8)

            progs[b_idx, t] = encode_instr(op, dst, a, b)
            if op != 0x00:
                seen_non_nop = True
                if dst == 7:
                    has_r7_write = True

        if not has_r7_write or not seen_non_nop:
            # Guarantee S0-validity: write to r7 on last instruction with non-risky op
            op = int(ops_np[b_idx, T - 1]) & 0x0F
            if op == 0x00 or op in RISKY_OPS:
                op = 0x01  # ADD
            a = int(as_np[b_idx, T - 1]) % 8
            b_val = int(bs_np[b_idx, T - 1])
            b = (b_val & 0x0F) if op == 0x0F else (b_val % 8)
            progs[b_idx, T - 1] = encode_instr(op, 7, a, b)

    return progs


# ==============================================================================
# P53 — Small history-conditional sequential proposer (single model, <= 1M params)
# ==============================================================================

P53_MAX_PARAMS = 1_000_000
P53_EXPLORATION_FLOOR = 0.10
P53_MASK_NORMAL = 0
P53_MASK_FINAL = 1


def p53_position_mask_id(step: int) -> int:
    """Validity-mask id for an instruction slot: the final slot forbids NOP."""
    return P53_MASK_FINAL if step == N_INSTR - 1 else P53_MASK_NORMAL


class SequentialHistoryProposer(nn.Module):
    """GRU proposer conditioned on numeric objective, sampled history and mask.

    Unlike a position-only network, every step observes the feature-encoded
    objective plus all previously sampled instruction tokens and the
    validity-mask id of the current slot. Training uses teacher forcing;
    sampling feeds back actually sampled tokens autoregressively.
    """

    def __init__(
        self,
        feat_dim: int = 16,
        feat_width: int = 32,
        gru_width: int = 64,
    ) -> None:
        super().__init__()
        self.feat_dim = int(feat_dim)
        self.feat_width = int(feat_width)
        self.gru_width = int(gru_width)
        self.feat_encoder = nn.Sequential(
            nn.Linear(feat_dim, feat_width),
            nn.ReLU(),
        )
        self.op_embed = nn.Embedding(16, 8)
        self.dst_embed = nn.Embedding(8, 4)
        self.a_embed = nn.Embedding(8, 4)
        self.b_embed = nn.Embedding(16, 8)
        self.mask_embed = nn.Embedding(2, 4)
        self.gru = nn.GRU(feat_width + 8 + 4 + 4 + 8 + 4, gru_width, 1, batch_first=True)
        self.head_op = nn.Linear(gru_width, 16)
        self.head_dst = nn.Linear(gru_width, 8)
        self.head_a = nn.Linear(gru_width, 8)
        self.head_b = nn.Linear(gru_width, 16)

    def count_parameters(self) -> int:
        return sum(p.numel() for p in self.parameters())

    def _encode_window(
        self,
        feats: torch.Tensor,
        ops: torch.Tensor,
        dsts: torch.Tensor,
        a_s: torch.Tensor,
        b_s: torch.Tensor,
    ) -> torch.Tensor:
        """Encode one prefix window (B, L+1): BOS + history, features, mask ids."""
        per = ops.shape[0]
        cur_len = ops.shape[1] + 1
        bos = torch.zeros(per, 1, dtype=torch.long, device=ops.device)
        mask_ids = torch.zeros(per, cur_len, dtype=torch.long, device=ops.device)
        mask_ids[:, -1] = 1 if cur_len == N_INSTR else 0
        x = torch.cat(
            [
                self.feat_encoder(feats).unsqueeze(1).expand(per, cur_len, -1),
                self.op_embed(torch.cat([bos, ops], dim=1)),
                self.dst_embed(torch.cat([bos, dsts], dim=1)),
                self.a_embed(torch.cat([bos, a_s], dim=1)),
                self.b_embed(torch.cat([bos, b_s], dim=1)),
                self.mask_embed(mask_ids),
            ],
            dim=-1,
        )
        h, _ = self.gru(x)
        return h[:, -1, :]

    def forward_loss(
        self,
        feats: torch.Tensor,
        ops: torch.Tensor,
        dsts: torch.Tensor,
        a_s: torch.Tensor,
        b_s: torch.Tensor,
    ) -> torch.Tensor:
        """Next-token cross-entropy with teacher-forced history (B, 16 targets)."""
        per = ops.shape[0]
        bos = torch.zeros(per, 1, dtype=torch.long, device=ops.device)
        full = torch.arange(N_INSTR, device=ops.device).unsqueeze(0).expand(per, -1)
        mask_ids = torch.where(
            full == N_INSTR - 1,
            torch.ones_like(full),
            torch.zeros_like(full),
        )
        x = torch.cat(
            [
                self.feat_encoder(feats).unsqueeze(1).expand(per, N_INSTR, -1),
                self.op_embed(torch.cat([bos, ops[:, :-1]], dim=1)),
                self.dst_embed(torch.cat([bos, dsts[:, :-1]], dim=1)),
                self.a_embed(torch.cat([bos, a_s[:, :-1]], dim=1)),
                self.b_embed(torch.cat([bos, b_s[:, :-1]], dim=1)),
                self.mask_embed(mask_ids),
            ],
            dim=-1,
        )
        h, _ = self.gru(x)
        B = ops.shape[0]
        return (
            nn.functional.cross_entropy(self.head_op(h).reshape(B * N_INSTR, 16), ops.reshape(-1))
            + nn.functional.cross_entropy(
                self.head_dst(h).reshape(B * N_INSTR, 8), dsts.reshape(-1)
            )
            + nn.functional.cross_entropy(self.head_a(h).reshape(B * N_INSTR, 8), a_s.reshape(-1))
            + nn.functional.cross_entropy(self.head_b(h).reshape(B * N_INSTR, 16), b_s.reshape(-1))
        ) / 4.0

    def propose_step(
        self,
        feats_row: torch.Tensor,
        ops: torch.Tensor,
        dsts: torch.Tensor,
        a_s: torch.Tensor,
        b_s: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """Logits for the next slot given the actually sampled prefix."""
        last = self._encode_window(feats_row, ops, dsts, a_s, b_s)
        return self.head_op(last), self.head_dst(last), self.head_a(last), self.head_b(last)


def p53_proposer_schema(
    feat_dim: int = 16,
    feat_width: int = 32,
    gru_width: int = 64,
    feature_mean: list[float] | None = None,
    feature_std: list[float] | None = None,
) -> dict[str, Any]:
    """Serializable schema: vocabs, normalization, mask rule and decoder rules."""
    return {
        "schema_version": "p53-v1",
        "architecture": "SequentialHistoryProposer",
        "feat_dim": int(feat_dim),
        "feat_width": int(feat_width),
        "gru_width": int(gru_width),
        "vocabs": {"op": 16, "dst": 8, "a": 8, "b": 16},
        "n_instr": int(N_INSTR),
        "feature_mean": [float(v) for v in (feature_mean or [])],
        "feature_std": [float(v) for v in (feature_std or [])],
        "mask_rule": "mask id 1 at the final slot only; NOP logit forced to -inf there",
        "decoder_rules": "b masked to 4 bits for CSEL else register; last slot writes r7 non-NOP (S0)",
        "exploration_floor_source": "grammar sampling (structured random)",
    }


def train_sequential_proposer(
    *,
    train_features: np.ndarray,
    train_programs: np.ndarray,
    val_features: np.ndarray,
    val_programs: np.ndarray,
    seed: int = 42,
    batch_size: int = 32,
    max_epochs: int = 20,
    max_train_sec: float = 1800.0,
    lr: float = 3e-3,
    gru_width: int = 64,
    device: torch.device | str = "cpu",
) -> dict[str, Any]:
    """Train one sequential proposer with teacher forcing; checkpoint by validation.

    Caps (epochs, wall time, 1M params) are enforced, never widened: with
    insufficient VRAM the batch shrinks instead. Returns the model holding
    the best-validation weights plus curves and billed costs.
    """
    import torch as _torch

    dev = _torch.device(device)
    _torch.manual_seed(seed % (2**32))
    np.random.seed(seed % (2**32))
    feat_dim = int(np.asarray(train_features).shape[1])
    mu = np.asarray(train_features, dtype=np.float64).mean(axis=0)
    sigma = np.asarray(train_features, dtype=np.float64).std(axis=0) + 1e-6
    norm_train = ((np.asarray(train_features, dtype=np.float64) - mu) / sigma).astype(np.float32)
    norm_val = ((np.asarray(val_features, dtype=np.float64) - mu) / sigma).astype(np.float32)

    model = SequentialHistoryProposer(feat_dim=feat_dim, gru_width=int(gru_width)).to(dev)
    param_count = model.count_parameters()
    if param_count > P53_MAX_PARAMS:
        raise ValueError(f"P53 proposer has {param_count} params, cap is {P53_MAX_PARAMS}")

    tr_ops, tr_dst, tr_a, tr_b = encode_programs_to_tensors(train_programs, device="cpu")
    va_ops, va_dst, va_a, va_b = encode_programs_to_tensors(val_programs, device="cpu")
    tr_f = _torch.tensor(norm_train, dtype=_torch.float32)
    va_f = _torch.tensor(norm_val, dtype=_torch.float32)
    n_train = len(norm_train)
    opt = _torch.optim.AdamW(model.parameters(), lr=float(lr))

    def _epoch_loss(train: bool, batch: int) -> float:
        model.train(train)
        tot, steps = 0.0, 0
        if train:
            perm = _torch.randperm(n_train)
            for s in range(0, n_train, batch):
                idx = perm[s : s + batch]
                opt.zero_grad()
                loss = model.forward_loss(
                    tr_f[idx].to(dev),
                    tr_ops[idx].to(dev),
                    tr_dst[idx].to(dev),
                    tr_a[idx].to(dev),
                    tr_b[idx].to(dev),
                )
                loss.backward()
                opt.step()
                tot += float(loss.item())
                steps += 1
            return tot / max(1, steps)
        with _torch.no_grad():
            loss = model.forward_loss(
                va_f.to(dev), va_ops.to(dev), va_dst.to(dev), va_a.to(dev), va_b.to(dev)
            )
            return float(loss.item())

    t0 = time.perf_counter()
    batch_used = int(batch_size)
    train_curve: list[float] = []
    val_curve: list[float] = []
    best_val = float("inf")
    best_epoch = -1
    best_state: dict[str, Any] | None = None
    epochs_run = 0
    stopped_by: str = "max_epochs"
    for epoch in range(max(1, int(max_epochs))):
        if time.perf_counter() - t0 > float(max_train_sec):
            stopped_by = "time_cap"
            break
        try:
            tr_loss = _epoch_loss(True, batch_used)
        except RuntimeError as exc:
            if "out of memory" not in str(exc).lower() or batch_used <= 4:
                raise
            batch_used = max(4, batch_used // 2)
            if dev.type == "cuda":
                _torch.cuda.empty_cache()
            tr_loss = _epoch_loss(True, batch_used)
        va_loss = _epoch_loss(False, batch_used)
        train_curve.append(tr_loss)
        val_curve.append(va_loss)
        epochs_run += 1
        if va_loss < best_val:
            best_val = va_loss
            best_epoch = epoch
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
    train_sec = time.perf_counter() - t0
    if best_state is not None:
        model.load_state_dict({k: v.to(dev) for k, v in best_state.items()})
    return {
        "model": model,
        "param_count": param_count,
        "train_curve": train_curve,
        "val_curve": val_curve,
        "best_val_loss": best_val,
        "best_epoch": best_epoch,
        "epochs_run": epochs_run,
        "stopped_by": stopped_by,
        "batch_used": batch_used,
        "batch_requested": int(batch_size),
        "train_sec": train_sec,
        "feature_mean": [float(v) for v in mu],
        "feature_std": [float(v) for v in sigma],
    }


def save_proposer(path: str | Path, model: SequentialHistoryProposer) -> str:
    """Save proposer weights; returns the sha256 of the written file."""
    import hashlib as _hashlib
    from pathlib import Path as _Path

    out = _Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    _torch_state = {k: v.cpu() for k, v in model.state_dict().items()}
    torch.save(_torch_state, out)
    return _hashlib.sha256(out.read_bytes()).hexdigest()


def load_proposer(
    path: str | Path,
    schema: dict[str, Any],
    device: torch.device | str = "cpu",
) -> SequentialHistoryProposer:
    """Independently load proposer weights into a fresh instance from schema."""
    model = SequentialHistoryProposer(
        feat_dim=int(schema.get("feat_dim", 16)),
        feat_width=int(schema.get("feat_width", 32)),
        gru_width=int(schema.get("gru_width", 64)),
    ).to(torch.device(device))
    state = torch.load(path, map_location=torch.device(device), weights_only=True)
    model.load_state_dict(state)
    model.eval()
    return model


def sample_proposer_standalone(
    model: SequentialHistoryProposer,
    features: np.ndarray,
    n: int,
    *,
    seed: int = 42,
    temperature: float = 0.8,
    exploration_floor: float = P53_EXPLORATION_FLOOR,
    device: torch.device | str = "cpu",
) -> tuple[np.ndarray, list[str]]:
    """Standalone proposal without evolution: model samples plus a random floor.

    Returns (programs, origins) with origins in {"model", "floor"}; at least
    the exploration floor fraction always comes from structured random sampling.
    Seeded runs reproduce bit-exactly.
    """
    from evobyte.grammar import sample_grammar_batch as _sample_batch

    dev = torch.device(device)
    temp = max(1e-3, float(temperature))
    torch.manual_seed(seed % (2**32))
    np.random.seed(seed % (2**32))
    model.eval()
    feats = np.asarray(features, dtype=np.float32)
    if feats.ndim == 1:
        feats = feats.reshape(1, -1)
    n_floor = 0
    if n > 1:
        import math as _math

        n_floor = min(n, max(1, _math.ceil(n * float(exploration_floor))))
    n_model = n - n_floor

    progs: list[np.ndarray] = []
    origins: list[str] = []
    with torch.no_grad():
        rows = feats.shape[0]
        per_row = max(1, (n_model + max(1, rows) - 1) // max(1, rows))
        for bi in range(rows):
            if sum(len(p) for p in progs) >= n_model:
                break
            f_row = torch.tensor(feats[bi : bi + 1], dtype=torch.float32, device=dev)
            ops = torch.zeros(per_row, 0, dtype=torch.long, device=dev)
            dsts = torch.zeros(per_row, 0, dtype=torch.long, device=dev)
            a_s = torch.zeros(per_row, 0, dtype=torch.long, device=dev)
            b_s = torch.zeros(per_row, 0, dtype=torch.long, device=dev)
            co, cd, ca, cb = [], [], [], []
            for _ in range(N_INSTR):
                lo, ld, la, lb = model.propose_step(f_row, ops, dsts, a_s, b_s)
                if ops.shape[1] == N_INSTR - 1:
                    lo = lo.clone()
                    lo[:, 0] = float("-inf")
                o = torch.multinomial(torch.softmax(lo / temp, dim=-1), 1)
                d = torch.multinomial(torch.softmax(ld / temp, dim=-1), 1)
                a = torch.multinomial(torch.softmax(la / temp, dim=-1), 1)
                b = torch.multinomial(torch.softmax(lb / temp, dim=-1), 1)
                co.append(o)
                cd.append(d)
                ca.append(a)
                cb.append(b)
                ops = torch.cat([ops, o], dim=1)
                dsts = torch.cat([dsts, d % 8], dim=1)
                a_s = torch.cat([a_s, a % 8], dim=1)
                b_s = torch.cat([b_s, b], dim=1)
            decoded = decode_sampled_tokens_to_programs(
                torch.cat(co, dim=1),
                torch.cat(cd, dim=1),
                torch.cat(ca, dim=1),
                torch.cat(cb, dim=1),
            )
            progs.append(decoded)
            origins.extend(["model"] * len(decoded))
    model_progs = (
        np.concatenate(progs, axis=0)[:n_model]
        if progs
        else np.zeros((0, N_INSTR), dtype=np.uint32)
    )
    model_origins = origins[:n_model]
    if n_floor > 0:
        floor = _sample_batch(n_floor, device=dev, seed=seed + 1).cpu().numpy().astype(np.uint32)
        if floor.ndim == 1:
            floor = floor.reshape(1, -1)
        return np.concatenate([model_progs, floor[:n_floor]], axis=0), model_origins + [
            "floor"
        ] * n_floor
    return model_progs, model_origins


class MicroGenerator:
    """Micro neural bytecode generator trained on elite archives under a strict VRAM cap."""

    """Micro neural bytecode generator trained on elite archives under a strict VRAM cap."""

    def __init__(
        self,
        config: GeneratorConfig | None = None,
        device: torch.device | str | None = None,
    ) -> None:
        self.config = config or GeneratorConfig()
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        self.model = BytecodeAutoregressiveModel(
            d_model=self.config.d_model,
            nhead=self.config.nhead,
            num_layers=self.config.num_layers,
            dim_feedforward=self.config.dim_feedforward,
            dropout=self.config.dropout,
        ).to(self.device)

        self.caps = assert_generator_resource_cap(self.model, max_mb=self.config.vram_cap_mb)

        self.optimizer = torch.optim.AdamW(
            self.model.parameters(),
            lr=self.config.lr,
            weight_decay=1e-4,
        )

    def train_on_elites(
        self,
        elites: np.ndarray | list[np.ndarray],
        epochs: int = 5,
        batch_size: int | None = None,
    ) -> dict[str, float]:
        """Supervised training of micro-generator on elite programs using next-token cross-entropy."""
        t0 = time.perf_counter()
        progs = np.asarray(elites, dtype=np.uint32)
        if len(progs) == 0:
            return {"loss": 0.0, "time_sec": 0.0, "steps": 0}

        bsz = batch_size or min(len(progs), self.config.batch_size)
        ops, dsts, as_, bs = encode_programs_to_tensors(progs, device=self.device)
        n_samples = len(progs)

        self.model.train()
        total_loss = 0.0
        steps = 0

        for _ in range(epochs):
            indices = torch.randperm(n_samples, device=self.device)
            for start in range(0, n_samples, bsz):
                batch_idx = indices[start : start + bsz]
                self.optimizer.zero_grad()
                loss = self.model.forward_loss(
                    ops[batch_idx], dsts[batch_idx], as_[batch_idx], bs[batch_idx]
                )
                loss.backward()
                self.optimizer.step()
                total_loss += float(loss.item())
                steps += 1

        elapsed = time.perf_counter() - t0
        avg_loss = total_loss / max(1, steps)
        return {
            "loss": avg_loss,
            "time_sec": elapsed,
            "steps": steps,
        }

    def sample_candidates(
        self,
        n: int,
        elites: np.ndarray | list[np.ndarray] | None = None,
        p_prefix_condition: float = 0.5,
        min_prefix: int = 1,
        max_prefix: int = 8,
        temperature: float | None = None,
    ) -> np.ndarray:
        """Sample N candidate programs, optionally conditioning on random elite prefixes."""
        temp = temperature if temperature is not None else self.config.temperature

        if elites is not None and len(elites) > 0 and p_prefix_condition > 0.0:
            n_cond = round(n * p_prefix_condition)
            n_uncond = n - n_cond

            batches = []
            if n_cond > 0:
                elites_arr = np.asarray(elites, dtype=np.uint32)
                # Sample random elites and random prefix lengths
                k = int(np.random.randint(min_prefix, max_prefix + 1))
                rand_idx = np.random.randint(0, len(elites_arr), size=n_cond)
                chosen_elites = elites_arr[rand_idx]

                ops_all, dsts_all, as_all, bs_all = encode_programs_to_tensors(
                    chosen_elites, device=self.device
                )
                pref_ops = ops_all[:, :k]
                pref_dsts = dsts_all[:, :k]
                pref_as = as_all[:, :k]
                pref_bs = bs_all[:, :k]

                s_ops, s_dsts, s_as, s_bs = self.model.sample(
                    n=n_cond,
                    prefix_ops=pref_ops,
                    prefix_dsts=pref_dsts,
                    prefix_as=pref_as,
                    prefix_bs=pref_bs,
                    temperature=temp,
                    device=self.device,
                )
                batches.append(decode_sampled_tokens_to_programs(s_ops, s_dsts, s_as, s_bs))

            if n_uncond > 0:
                s_ops, s_dsts, s_as, s_bs = self.model.sample(
                    n=n_uncond,
                    temperature=temp,
                    device=self.device,
                )
                batches.append(decode_sampled_tokens_to_programs(s_ops, s_dsts, s_as, s_bs))

            return np.concatenate(batches, axis=0) if len(batches) > 1 else batches[0]
        else:
            s_ops, s_dsts, s_as, s_bs = self.model.sample(
                n=n,
                temperature=temp,
                device=self.device,
            )
            return decode_sampled_tokens_to_programs(s_ops, s_dsts, s_as, s_bs)

    def pipeline_step(
        self,
        elites: np.ndarray | list[np.ndarray],
        n_candidates: int,
        rng: np.random.Generator,
        p_mutation: float = 0.1,
        train_epochs: int = 2,
    ) -> tuple[np.ndarray, dict[str, float]]:
        """Executes full pipeline: elites -> micro-generator -> candidates -> mutation."""
        t0 = time.perf_counter()
        train_stats = self.train_on_elites(elites, epochs=train_epochs)
        candidates = self.sample_candidates(n_candidates, elites=elites, p_prefix_condition=0.5)

        # Mutate a fraction of the candidates
        mutated_candidates = []
        for cand in candidates:
            if rng.random() < p_mutation:
                cand = mutate_candidate(cand, rng, p_gene=0.10, p_block=0.0, p_byte=0.0)
                if not is_valid(cand):
                    op, _, a, b = decode_instr(cand[-1])
                    if op == 0x00 or op in RISKY_OPS:
                        op = 0x01  # ADD
                    cand[-1] = encode_instr(op, 7, a % 8, (b & 0x0F) if op == 0x0F else (b % 8))
            mutated_candidates.append(cand)

        total_time = time.perf_counter() - t0
        stats = {
            "train_loss": train_stats["loss"],
            "train_time_sec": train_stats["time_sec"],
            "total_pipeline_time_sec": total_time,
            "candidates_count": len(candidates),
        }
        return np.stack(mutated_candidates), stats
