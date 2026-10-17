"""Lightweight conditional neural proposer for structured Diophantine search and Lean 4 tactics (P107).

Spec: docs/phases/P107-lightweight-conditional-proposer.md
Hard caps: <= 5M parameters, VRAM resident (< 100 MB), zero hallucination
(strictly closed vocabulary of tactics and candidate ranking without free text).
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

P107_MAX_PARAMS = 5_000_000
DEFAULT_VRAM_CAP_MB = 100.0

CANONICAL_LEAN_TACTICS: list[str] = [
    "norm_num",
    "omega",
    "ring",
    "linarith",
    "nlinarith",
    "aesop",
    "dioph_surface",
    "exact",
    "positivity",
    "decide",
]

CANONICAL_ALGEBRAIC_IDENTITIES: list[str] = [
    "erdos_straus_type1",
    "erdos_straus_type2",
    "sierpinski_4k",
    "schinzel_poly",
    "quadratic_param",
    "cubic_fibration",
    "coprime_sieve",
    "general_sieve",
]

STANDARD_MODULI: list[int] = [2, 3, 4, 5, 7, 8, 9, 11, 12, 13, 17, 19, 23, 24]


def encode_instance_features(a: int, n: int) -> torch.Tensor:
    """Encode instance features into a deterministic continuous representation.

    Features:
    - a normalized (1)
    - log1p(n) scale (1)
    - parity of n (1)
    - sine/cosine harmonic embedding for each modulus in STANDARD_MODULI (2 * 14 = 28)
    - direct modular residues normalized by modulus (14)
    Total dimension = 1 + 1 + 1 + 28 + 14 = 45.
    """
    feats: list[float] = [
        float(a) / 10.0,
        float(math.log1p(max(1, n))) / 20.0,
        float(n % 2),
    ]
    for m in STANDARD_MODULI:
        rem = float(n % m)
        phase = 2.0 * math.pi * rem / float(m)
        feats.append(math.sin(phase))
        feats.append(math.cos(phase))
        feats.append(rem / float(m))
    return torch.tensor(feats, dtype=torch.float32)


def encode_divisor_features(a: int, n: int, d: int) -> torch.Tensor:
    """Encode candidate divisor features into a deterministic continuous representation.

    Features:
    - log1p(d) relative to log1p(n^2) (1)
    - parity of d (1)
    - is d <= n (1)
    - normalized d mod a (1)
    - normalized d mod 4 (1)
    - normalized log distance from optimal center n / a (1)
    - sine/cosine harmonic embedding of d for key moduli [2, 3, 4, 8, 12, 24] (2 * 6 = 12)
    Total dimension = 1 + 1 + 1 + 1 + 1 + 1 + 12 = 18.
    """
    n2_scale = max(1.0, 2.0 * math.log1p(max(1, n)))
    log_d = math.log1p(max(1, d))
    center = max(1.0, float(n) / max(1.0, float(a)))
    log_dist = math.log1p(abs(float(d) - center)) / max(1.0, math.log1p(float(n)))

    feats: list[float] = [
        float(log_d / n2_scale),
        float(d % 2),
        1.0 if d <= n else 0.0,
        float(d % max(1, a)) / float(max(1, a)),
        float(d % 4) / 4.0,
        float(log_dist),
    ]
    for m in [2, 3, 4, 8, 12, 24]:
        rem = float(d % m)
        phase = 2.0 * math.pi * rem / float(m)
        feats.append(math.sin(phase))
        feats.append(math.cos(phase))

    return torch.tensor(feats, dtype=torch.float32)


class ResidualBlock(nn.Module):
    """Pre-LayerNorm residual block with GELU activation."""

    def __init__(self, d_model: int, dropout: float = 0.05) -> None:
        super().__init__()
        self.norm1 = nn.LayerNorm(d_model)
        self.linear1 = nn.Linear(d_model, d_model * 2)
        self.linear2 = nn.Linear(d_model * 2, d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        res = x
        h = self.norm1(x)
        h = F.gelu(self.linear1(h))
        h = self.dropout(h)
        h = self.linear2(h)
        return res + h


class StructuredConditionalProposer(nn.Module):
    """Compact conditional neural proposer (< 5M params) for Diophantine search and Lean 4 tactics.

    Predicts:
    1. Candidate divisor ranking scores for optimal coordinate Diophantine solutions.
    2. Discrete Lean 4 tactic distributions (strictly closed vocabulary).
    3. Discrete algebraic identity families (strictly closed vocabulary).
    Zero natural language generation, zero hallucination.
    """

    def __init__(
        self,
        instance_feat_dim: int = 45,
        divisor_feat_dim: int = 18,
        d_model: int = 256,
        num_layers: int = 4,
        dropout: float = 0.05,
        num_tactics: int = len(CANONICAL_LEAN_TACTICS),
        num_identities: int = len(CANONICAL_ALGEBRAIC_IDENTITIES),
    ) -> None:
        super().__init__()
        self.instance_feat_dim = instance_feat_dim
        self.divisor_feat_dim = divisor_feat_dim
        self.d_model = d_model
        self.num_layers = num_layers
        self.num_tactics = num_tactics
        self.num_identities = num_identities

        # Instance encoder
        self.instance_proj = nn.Linear(instance_feat_dim, d_model)
        self.encoder_blocks = nn.ModuleList(
            [ResidualBlock(d_model, dropout=dropout) for _ in range(num_layers)]
        )
        self.instance_norm = nn.LayerNorm(d_model)

        # Divisor scorer head
        self.divisor_proj = nn.Linear(divisor_feat_dim, d_model)
        self.divisor_head = nn.Sequential(
            nn.Linear(d_model * 2, d_model),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_model, 1),
        )

        # Lean 4 tactic dispatch head
        self.tactic_head = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.GELU(),
            nn.Linear(d_model // 2, num_tactics),
        )

        # Algebraic identity template head
        self.identity_head = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.GELU(),
            nn.Linear(d_model // 2, num_identities),
        )

    def count_parameters(self) -> int:
        """Count total trainable parameters in the model."""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)

    def resident_memory_mb(self) -> float:
        """Estimate resident memory in megabytes for parameters and buffers."""
        param_bytes = sum(p.numel() * p.element_size() for p in self.parameters())
        buffer_bytes = sum(b.numel() * b.element_size() for b in self.buffers())
        return float((param_bytes + buffer_bytes) / (1024 * 1024))

    def encode_instance(self, instance_feats: torch.Tensor) -> torch.Tensor:
        """Encode batch of instance features (B, instance_feat_dim) -> (B, d_model)."""
        h = self.instance_proj(instance_feats)
        for block in self.encoder_blocks:
            h = block(h)
        return self.instance_norm(h)

    def forward(
        self,
        instance_feats: torch.Tensor,
        divisor_feats: torch.Tensor | None = None,
    ) -> dict[str, torch.Tensor]:
        """Compute forward pass.

        Args:
            instance_feats: (B, instance_feat_dim)
            divisor_feats: (B, K, divisor_feat_dim) or (B, divisor_feat_dim)

        Returns:
            dict with:
                - 'instance_embed': (B, d_model)
                - 'tactic_logits': (B, num_tactics)
                - 'identity_logits': (B, num_identities)
                - 'divisor_scores': (B, K) or (B, 1) if divisor_feats provided
        """
        inst_embed = self.encode_instance(instance_feats)
        tactic_logits = self.tactic_head(inst_embed)
        identity_logits = self.identity_head(inst_embed)

        out: dict[str, torch.Tensor] = {
            "instance_embed": inst_embed,
            "tactic_logits": tactic_logits,
            "identity_logits": identity_logits,
        }

        if divisor_feats is not None:
            if divisor_feats.dim() == 2:
                # (B, divisor_feat_dim) -> single candidate per instance
                div_embed = self.divisor_proj(divisor_feats)
                combined = torch.cat([inst_embed, div_embed], dim=-1)
                scores = self.divisor_head(combined).squeeze(-1)
                out["divisor_scores"] = scores
            elif divisor_feats.dim() == 3:
                # (B, K, divisor_feat_dim) -> K candidates per instance
                B, K, _ = divisor_feats.shape
                inst_expanded = inst_embed.unsqueeze(1).expand(B, K, -1)
                div_embed = self.divisor_proj(divisor_feats)
                combined = torch.cat([inst_expanded, div_embed], dim=-1)
                scores = self.divisor_head(combined).squeeze(-1)  # (B, K)
                out["divisor_scores"] = scores

        return out

    def rank_divisors(
        self,
        a: int,
        n: int,
        candidates: list[int],
        device: str | torch.device = "cpu",
    ) -> list[int]:
        """Rank a candidate list of divisors strictly by neural priority score.

        GUARANTEE: Zero hallucination. Returns a permutation of the input candidates
        ordered by predicted likelihood of yielding an optimal coordinate solution.
        """
        if not candidates:
            return []
        if len(candidates) == 1:
            return list(candidates)

        self.eval()
        with torch.no_grad():
            inst_feat = encode_instance_features(a, n).unsqueeze(0).to(device)  # (1, 45)
            div_feats_list = [encode_divisor_features(a, n, d) for d in candidates]
            div_feats = torch.stack(div_feats_list, dim=0).unsqueeze(0).to(device)  # (1, K, 18)

            out = self.forward(inst_feat, div_feats)
            scores = out["divisor_scores"].squeeze(0).cpu().numpy()  # (K,)

        # Sort indices descending by score
        ranked_indices = np.argsort(-scores)
        return [candidates[i] for i in ranked_indices]

    def predict_tactics(
        self,
        a: int,
        n: int,
        device: str | torch.device = "cpu",
    ) -> list[tuple[str, float]]:
        """Predict probability distribution over canonical Lean 4 tactics."""
        self.eval()
        with torch.no_grad():
            inst_feat = encode_instance_features(a, n).unsqueeze(0).to(device)
            out = self.forward(inst_feat)
            probs = F.softmax(out["tactic_logits"].squeeze(0), dim=-1).cpu().numpy()

        results = [(CANONICAL_LEAN_TACTICS[i], float(probs[i])) for i in range(len(probs))]
        results.sort(key=lambda x: -x[1])
        return results

    def predict_identities(
        self,
        a: int,
        n: int,
        device: str | torch.device = "cpu",
    ) -> list[tuple[str, float]]:
        """Predict probability distribution over canonical algebraic identities."""
        self.eval()
        with torch.no_grad():
            inst_feat = encode_instance_features(a, n).unsqueeze(0).to(device)
            out = self.forward(inst_feat)
            probs = F.softmax(out["identity_logits"].squeeze(0), dim=-1).cpu().numpy()

        results = [(CANONICAL_ALGEBRAIC_IDENTITIES[i], float(probs[i])) for i in range(len(probs))]
        results.sort(key=lambda x: -x[1])
        return results

    def save_checkpoint(
        self,
        path: str | Path,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Save weights and architecture metadata to a reproducible checkpoint."""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        checkpoint = {
            "state_dict": self.state_dict(),
            "config": {
                "instance_feat_dim": self.instance_feat_dim,
                "divisor_feat_dim": self.divisor_feat_dim,
                "d_model": self.d_model,
                "num_layers": self.num_layers,
                "num_tactics": self.num_tactics,
                "num_identities": self.num_identities,
            },
            "metadata": metadata or {},
        }
        torch.save(checkpoint, p)

    @classmethod
    def load_checkpoint(
        cls,
        path: str | Path,
        map_location: str | torch.device = "cpu",
    ) -> tuple[StructuredConditionalProposer, dict[str, Any]]:
        """Load a frozen model checkpoint."""
        p = Path(path)
        checkpoint = torch.load(p, map_location=map_location, weights_only=False)
        cfg = checkpoint["config"]
        model = cls(
            instance_feat_dim=cfg["instance_feat_dim"],
            divisor_feat_dim=cfg["divisor_feat_dim"],
            d_model=cfg["d_model"],
            num_layers=cfg["num_layers"],
            num_tactics=cfg["num_tactics"],
            num_identities=cfg["num_identities"],
        )
        model.load_state_dict(checkpoint["state_dict"])
        model.to(map_location)
        model.eval()
        return model, checkpoint.get("metadata", {})
