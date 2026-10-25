"""Standardized frontier certificate export for external standalone validation (P184).

Exports self-contained JSON certificates for:
- Covering designs C(v, k, t)
- Strong Schur partitions
- Weak Schur partitions
- Cap sets in F_3^n
- Quantum error-correcting stabilizer codes [[n, k, d]]

Every certificate is verifiable by `scripts/verify_frontier_certificate.py`
using strictly Python standard library without EvoByte installed.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

CERTIFICATE_VERSION = "1.0.0"
VALID_FRONTIER_CERTIFICATE_TYPES = (
    "covering",
    "schur",
    "weak_schur",
    "cap_set",
    "qecc_stabilizer",
)


@dataclass(frozen=True)
class FrontierCertificate:
    """A standardized, externally verifiable frontier certificate."""

    target_id: str
    certificate_type: str
    candidate: Any
    parameters: dict[str, Any]
    reference_literature: str
    reproduction_seed: int
    provenance: dict[str, Any] = field(default_factory=dict)

    def payload(self) -> dict[str, Any]:
        """The mathematical object being certified (candidate + parameters)."""
        return {
            "certificate_type": self.certificate_type,
            "target_id": self.target_id,
            "candidate": self.candidate,
            "parameters": dict(self.parameters),
        }

    def sha256_checksum(self) -> str:
        """SHA-256 of the canonical JSON of the certified object."""
        canonical = json.dumps(
            self.payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        document: dict[str, Any] = {
            "certificate_version": CERTIFICATE_VERSION,
            "target_id": self.target_id,
            "certificate_type": self.certificate_type,
            "candidate_length": len(self.candidate),
            "reference_literature": self.reference_literature,
            "sha256_checksum": self.sha256_checksum(),
            "sha256_scope": (
                "SHA-256 of canonical JSON of "
                "{certificate_type, target_id, candidate, parameters}"
            ),
            "reproduction_seed": self.reproduction_seed,
        }

        if self.certificate_type == "covering":
            document["blocks"] = list(self.candidate)
            document["v"] = int(self.parameters["v"])
            document["k"] = int(self.parameters["k"])
            document["t"] = int(self.parameters["t"])
        elif self.certificate_type in ("schur", "weak_schur"):
            document["partition"] = list(self.candidate)
            document["k"] = int(self.parameters["k"])
        elif self.certificate_type == "cap_set":
            document["points"] = [list(pt) for pt in self.candidate]
            document["n"] = int(self.parameters["n"])
        elif self.certificate_type == "qecc_stabilizer":
            document["stabilizers"] = list(self.candidate)
            document["n"] = int(self.parameters["n"])
            document["k_claimed"] = int(self.parameters["k_claimed"])
            document["d_claimed"] = int(self.parameters["d_claimed"])
        else:
            raise ValueError(f"unsupported certificate type: {self.certificate_type!r}")

        if self.provenance:
            document["provenance"] = dict(self.provenance)
        return document


def export_frontier_certificate(
    cert: FrontierCertificate, output_path: str | Path
) -> Path:
    """Write standardized frontier certificate JSON to disk."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(cert.to_dict(), indent=2), encoding="utf-8")
    return out
