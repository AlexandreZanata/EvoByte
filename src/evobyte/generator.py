"""Micro neural bytecode generator and sampler (spec: docs/phases/P12-neural-generator.md)."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import numpy as np
import torch
import torch.nn as nn

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


class MicroGenerator:
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
            n_cond = int(round(n * p_prefix_condition))
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
