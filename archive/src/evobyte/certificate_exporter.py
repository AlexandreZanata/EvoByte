"""Standardized certificate export for external validation (P167).

A certificate is a self-contained JSON document that a third party can verify
without installing this package: it carries the candidate object itself, the
parameters needed to check it, the literature reference, the seed that
reproduces the search and a checksum of the certified object.

The exported document is exactly what `scripts/verify_certificate_standalone.py`
consumes (stdlib only), so the verification path does not depend on `evobyte`.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from evobyte.target_catalogue import verify_schur_partition, verify_vanderwaerden_coloring

CERTIFICATE_VERSION = "1.0.0"
CERTIFICATE_TYPES = ("vanderwaerden", "schur")


@dataclass(frozen=True)
class Certificate:
    """A standardized, externally verifiable mathematical certificate."""

    target_id: str
    certificate_type: str
    candidate: tuple[int, ...]
    parameters: dict[str, int]
    reference_literature: str
    reproduction_seed: int
    provenance: dict[str, Any] = field(default_factory=dict)

    def payload(self) -> dict[str, Any]:
        """The mathematical object being certified (candidate + parameters)."""
        return {
            "certificate_type": self.certificate_type,
            "target_id": self.target_id,
            "candidate": list(self.candidate),
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
                "SHA-256 of the canonical JSON of "
                "{certificate_type, target_id, candidate, parameters}"
            ),
            "reproduction_seed": self.reproduction_seed,
        }
        if self.certificate_type == "vanderwaerden":
            document["coloring"] = list(self.candidate)
            document["r"] = int(self.parameters["r"])
            document["k"] = int(self.parameters["k"])
        elif self.certificate_type == "schur":
            document["partition"] = list(self.candidate)
            document["k"] = int(self.parameters["k"])
        else:
            raise ValueError(f"unsupported certificate type {self.certificate_type!r}")
        if self.provenance:
            document["provenance"] = dict(self.provenance)
        return document


def export_certificate(
    candidate: list[int] | tuple[int, ...],
    target_id: str,
    certificate_type: str,
    parameters: dict[str, int],
    reference_literature: str,
    reproduction_seed: int,
    provenance: dict[str, Any] | None = None,
) -> Certificate:
    """Build a certificate from a candidate, after checking it locally."""
    if certificate_type not in CERTIFICATE_TYPES:
        raise ValueError(f"unsupported certificate type {certificate_type!r}")
    certificate = Certificate(
        target_id=target_id,
        certificate_type=certificate_type,
        candidate=tuple(int(c) for c in candidate),
        parameters={k: int(v) for k, v in parameters.items()},
        reference_literature=reference_literature,
        reproduction_seed=int(reproduction_seed),
        provenance=dict(provenance or {}),
    )
    ok, message = verify_with_oracle(certificate)
    if not ok:
        raise ValueError(f"candidate does not certify against the local oracle: {message}")
    return certificate


def verify_with_oracle(certificate: Certificate) -> tuple[bool, str]:
    """Check the certificate with the repository's independent verifier."""
    if certificate.certificate_type == "vanderwaerden":
        return verify_vanderwaerden_coloring(
            list(certificate.candidate),
            int(certificate.parameters["r"]),
            int(certificate.parameters["k"]),
        )
    return verify_schur_partition(list(certificate.candidate), int(certificate.parameters["k"]))


def write_certificate(path: str | Path, certificate: Certificate) -> str:
    """Write the certificate as JSON and return the SHA-256 of the written file."""
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(certificate.to_dict(), indent=2, ensure_ascii=False) + "\n"
    out_path.write_text(payload, encoding="utf-8")
    return hashlib.sha256(out_path.read_bytes()).hexdigest()


def load_certificate(path: str | Path) -> dict[str, Any]:
    """Read a certificate document back from disk."""
    return json.loads(Path(path).read_text(encoding="utf-8"))
