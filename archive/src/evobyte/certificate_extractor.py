"""Autonomous Structured Certificate Extractor (P197).

Extracts and serializes mathematical certificates from structured search campaigns
and calibration runs into canonical, self-contained JSON documents with zero EvoByte
runtime dependencies.

Each certificate contains:
1. Exact problem specification and parameters.
2. Canonical mathematical candidate object (e.g., covering blocks, orbit base blocks,
   stabilizer generator strings).
3. Literature / benchmark comparison and discovery verdict (e.g. DISCOVERY_TIED).
4. Provenance metadata (timestamp, commit hash, random seed, solver stats).
5. Deterministic SHA-256 payload checksum.

Part of the Structured Discovery and Functional Synthesis Program (P191-P200, D043).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
import json
from pathlib import Path
import time
from typing import Any, Sequence

from evobyte.frontier_catalogue import verify_covering_design
from evobyte.qecc_verifier import check_stabilizer, code_distance
from evobyte.sat_bridge import complete_covering_orbits
from evobyte.symmetry_engine import CoveringOrbitEngine

CERTIFICATE_SPEC_VERSION = "2.0.0"


@dataclass(frozen=True)
class CanonicalCertificate:
    """A self-contained mathematical discovery or calibration certificate."""

    certificate_type: str
    target_id: str
    verdict: str
    parameters: dict[str, Any]
    candidate: dict[str, Any]
    metadata: dict[str, Any]
    certificate_version: str = CERTIFICATE_SPEC_VERSION
    sha256_checksum: str = ""

    def payload(self) -> dict[str, Any]:
        """Return canonical dictionary of mathematical content (excluding checksum)."""
        return {
            "certificate_version": self.certificate_version,
            "certificate_type": self.certificate_type,
            "target_id": self.target_id,
            "verdict": self.verdict,
            "parameters": self.parameters,
            "candidate": self.candidate,
            "metadata": self.metadata,
        }

    def compute_checksum(self) -> str:
        """Compute deterministic SHA-256 over canonical JSON serialization."""
        payload_dict = self.payload()
        canonical_bytes = json.dumps(
            payload_dict,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        return hashlib.sha256(canonical_bytes).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        """Convert certificate to complete dictionary with computed checksum."""
        doc = self.payload()
        doc["sha256_checksum"] = self.sha256_checksum or self.compute_checksum()
        return doc

    def save(self, output_path: Path | str) -> str:
        """Write canonical certificate to file and return its SHA-256 checksum."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        doc = self.to_dict()
        formatted_json = json.dumps(doc, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
        path.write_text(formatted_json, encoding="utf-8")
        return doc["sha256_checksum"]


def extract_covering_certificate(
    target_id: str,
    v: int,
    k: int,
    t: int,
    blocks: Sequence[Sequence[int]],
    base_blocks: Sequence[Sequence[int]] | None = None,
    symmetry_group: str | None = None,
    verdict: str = "DISCOVERY_TIED",
    published_best: int | None = None,
    metadata: dict[str, Any] | None = None,
    one_indexed: bool = True,
) -> CanonicalCertificate:
    """Create a canonical certificate for a covering design C(v, k, t)."""
    norm_blocks = [sorted(int(x) for x in b) for b in blocks]
    norm_blocks.sort()

    candidate_dict: dict[str, Any] = {
        "indexing": 1 if one_indexed else 0,
        "num_blocks": len(norm_blocks),
        "blocks": norm_blocks,
    }

    if base_blocks:
        norm_bases = [sorted(int(x) for x in b) for b in base_blocks]
        norm_bases.sort()
        candidate_dict["symmetry"] = {
            "group": symmetry_group or f"Z_{v}",
            "order": v,
            "num_base_blocks": len(norm_bases),
            "base_blocks": norm_bases,
        }

    params = {
        "v": v,
        "k": k,
        "t": t,
        "claimed_blocks": len(norm_blocks),
    }
    if published_best is not None:
        params["published_best"] = published_best

    meta = {
        "generator": "EvoByte-Structured-SAT-Engine",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    if metadata:
        meta.update(metadata)

    cert = CanonicalCertificate(
        certificate_type="covering_design",
        target_id=target_id,
        verdict=verdict,
        parameters=params,
        candidate=candidate_dict,
        metadata=meta,
    )
    checksum = cert.compute_checksum()
    return CanonicalCertificate(
        certificate_type=cert.certificate_type,
        target_id=cert.target_id,
        verdict=cert.verdict,
        parameters=cert.parameters,
        candidate=cert.candidate,
        metadata=cert.metadata,
        sha256_checksum=checksum,
    )


def extract_qecc_certificate(
    target_id: str,
    n: int,
    k: int,
    d: int,
    generators: Sequence[str],
    verdict: str = "CALIBRATION_REPRODUCED",
    metadata: dict[str, Any] | None = None,
) -> CanonicalCertificate:
    """Create a canonical certificate for a quantum stabilizer code [[n, k, d]]."""
    gen_list = [str(g).strip().upper() for g in generators]
    params = {
        "n": n,
        "k": k,
        "claimed_d": d,
        "num_generators": len(gen_list),
    }
    candidate_dict = {
        "generators": gen_list,
    }
    meta = {
        "generator": "EvoByte-Structured-SAT-Engine",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    if metadata:
        meta.update(metadata)

    cert = CanonicalCertificate(
        certificate_type="qecc_stabilizer",
        target_id=target_id,
        verdict=verdict,
        parameters=params,
        candidate=candidate_dict,
        metadata=meta,
    )
    checksum = cert.compute_checksum()
    return CanonicalCertificate(
        certificate_type=cert.certificate_type,
        target_id=cert.target_id,
        verdict=cert.verdict,
        parameters=cert.parameters,
        candidate=cert.candidate,
        metadata=cert.metadata,
        sha256_checksum=checksum,
    )


def extract_c15_8_4_certificate(
    results_path: Path | str | None = None,
    output_path: Path | str | None = None,
) -> CanonicalCertificate:
    """Extract and reconstruct the C(15, 8, 4) = 30 discovery certificate from P196 campaign."""
    res = complete_covering_orbits(
        fixed_base_blocks=[],
        v=15,
        k=8,
        t=4,
        max_additional_orbits=2,
        solver_name="cadical153",
        one_indexed=True,
    )
    if not res.verified or not res.completed_blocks:
        raise RuntimeError("Failed to reconstruct verified C(15, 8, 4) design")

    engine = CoveringOrbitEngine(v=15, k=8, t=4)
    reps = engine.compute_orbit_representatives()
    matched_bases_0 = []
    completed_set = set(res.completed_blocks)
    for rep in reps:
        orbit = engine.group.orbit(rep)
        orbit_1 = {tuple(sorted(x + 1 for x in b)) for b in orbit}
        if orbit_1.issubset(completed_set):
            matched_bases_0.append(rep)

    base_blocks_1 = [tuple(sorted(x + 1 for x in r)) for r in matched_bases_0]

    git_commit = "unknown"
    if results_path and Path(results_path).is_file():
        try:
            with open(results_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                git_commit = data.get("git_commit", "unknown")
        except Exception:
            pass

    cert = extract_covering_certificate(
        target_id="covering_C_15_8_4",
        v=15,
        k=8,
        t=4,
        blocks=res.completed_blocks,
        base_blocks=base_blocks_1,
        symmetry_group="Z_15",
        verdict="DISCOVERY_TIED",
        published_best=30,
        metadata={
            "source_campaign": "P196",
            "git_commit": git_commit,
            "literature_record": "LJCR Gordon (1996) C(15, 8, 4) <= 30",
            "sat_stats": res.sat_stats,
        },
        one_indexed=True,
    )

    if output_path:
        cert.save(output_path)

    return cert


def extract_c10_4_3_certificate(
    output_path: Path | str | None = None,
) -> CanonicalCertificate:
    """Extract and export C(10, 4, 3) = 30 Steiner Quadruple System SQS(10) calibration certificate."""
    engine = CoveringOrbitEngine(v=10, k=4, t=3)
    # The 3 canonical base blocks in Z_10 from hard calibration:
    base_blocks_0 = [(0, 1, 2, 6), (0, 1, 3, 4), (0, 2, 4, 7)]
    base_blocks_1 = [tuple(sorted(x + 1 for x in b)) for b in base_blocks_0]
    expanded_1 = engine.expand_base_blocks(base_blocks_0, one_indexed=True)

    verified, msg = verify_covering_design(expanded_1, 10, 4, 3)
    if not verified:
        raise RuntimeError(f"C(10, 4, 3) verification failed: {msg}")

    cert = extract_covering_certificate(
        target_id="covering_c10_4_3",
        v=10,
        k=4,
        t=3,
        blocks=expanded_1,
        base_blocks=base_blocks_1,
        symmetry_group="Z_10",
        verdict="CALIBRATION_REPRODUCED",
        published_best=30,
        metadata={
            "source_phase": "P195",
            "mathematical_structure": "Steiner Quadruple System SQS(10)",
            "literature_record": "Mills (1979) C(10, 4, 3) = 30",
        },
        one_indexed=True,
    )

    if output_path:
        cert.save(output_path)

    return cert


def extract_qecc_8_3_3_certificate(
    output_path: Path | str | None = None,
) -> CanonicalCertificate:
    """Extract and export Gottesman [[8, 3, 3]] quantum stabilizer calibration certificate."""
    gens = [
        "YYXYYYYY",
        "ZYYYIXXI",
        "IYZZZYZI",
        "IYYIXZYX",
        "ZXXZIIZY",
    ]
    ok_stab, s_info = check_stabilizer(gens)
    ok_dist, d_info = code_distance(gens)
    if not (ok_stab and ok_dist and d_info.get("d", 0) >= 3):
        raise RuntimeError("Gottesman [[8, 3, 3]] code verification failed")

    cert = extract_qecc_certificate(
        target_id="qecc_8_3_3",
        n=8,
        k=3,
        d=3,
        generators=gens,
        verdict="CALIBRATION_REPRODUCED",
        metadata={
            "source_phase": "P195",
            "literature_record": "Gottesman (1996) [[8, 3, 3]] stabilizer code",
            "stabilizer_info": s_info,
            "distance_info": d_info,
        },
    )

    if output_path:
        cert.save(output_path)

    return cert


def load_canonical_certificate(path: Path | str) -> dict[str, Any]:
    """Load canonical certificate JSON from disk."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
