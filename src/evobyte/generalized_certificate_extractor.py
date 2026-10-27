"""Autonomous Generalized Certificate Extractor v3.0.0 (P207).

Extracts and serializes mathematical certificates from P205 and P206 into canonical,
self-contained JSON documents with zero EvoByte runtime dependencies.

Supports v3.0.0 certificate types:
1. covering_design: Covers all t-subsets with b blocks; supports affine plane AG(2, 3) checks.
2. qecc_stabilizer: Stabilizer codes [[n, k, d]] including non-circulant CSS check matrices.
3. structural_null_bound: Rigorous algebraic proofs of structural impossibility under group actions.

Part of the Generalized Symmetries & Non-Circulant Quantum Codes Program (P201-P210, D045).
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import time
from typing import Any, Sequence

CERTIFICATE_SPEC_VERSION = "3.0.0"


@dataclass(frozen=True)
class GeneralizedCertificate:
    """A self-contained v3.0.0 mathematical discovery or calibration certificate."""

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


def extract_affine_covering_certificate(
    target_id: str,
    v: int,
    k: int,
    t: int,
    blocks: Sequence[Sequence[int]],
    verdict: str = "CALIBRATION_REPRODUCED",
    published_best: int | None = None,
    affine_plane: bool = True,
    metadata: dict[str, Any] | None = None,
) -> GeneralizedCertificate:
    """Create a canonical certificate for an affine covering design C(v, k, t)."""
    norm_blocks = [sorted(list(b)) for b in blocks]
    norm_blocks.sort()

    candidate = {
        "blocks": norm_blocks,
        "total_blocks": len(norm_blocks),
        "indexing": 1,
        "is_affine_plane": affine_plane,
    }

    params: dict[str, Any] = {
        "v": v,
        "k": k,
        "t": t,
        "claimed_blocks": len(norm_blocks),
    }
    if published_best is not None:
        params["published_best"] = published_best

    meta = {
        "generator": "EvoByte Autonomous Discovery Engine",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "provenance": "P205 Blind Calibration",
    }
    if metadata:
        meta.update(metadata)

    cert = GeneralizedCertificate(
        certificate_type="covering_design",
        target_id=target_id,
        verdict=verdict,
        parameters=params,
        candidate=candidate,
        metadata=meta,
    )
    return GeneralizedCertificate(
        certificate_type=cert.certificate_type,
        target_id=cert.target_id,
        verdict=cert.verdict,
        parameters=cert.parameters,
        candidate=cert.candidate,
        metadata=cert.metadata,
        certificate_version=cert.certificate_version,
        sha256_checksum=cert.compute_checksum(),
    )


def extract_qecc_certificate(
    target_id: str,
    n: int,
    k: int,
    claimed_d: int,
    generators: Sequence[str],
    verdict: str = "DISCOVERY_TIED",
    code_structure: str = "non_circulant_css",
    check_matrices: dict[str, list[list[int]]] | None = None,
    metadata: dict[str, Any] | None = None,
) -> GeneralizedCertificate:
    """Create a canonical certificate for a quantum stabilizer code [[n, k, d]]."""
    gens_list = [g.upper() for g in generators]

    candidate: dict[str, Any] = {
        "generators": gens_list,
        "num_generators": len(gens_list),
        "code_structure": code_structure,
    }
    if check_matrices:
        candidate["check_matrices"] = check_matrices

    params = {
        "n": n,
        "k": k,
        "claimed_d": claimed_d,
    }

    meta = {
        "generator": "EvoByte Autonomous Discovery Engine",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    if metadata:
        meta.update(metadata)

    cert = GeneralizedCertificate(
        certificate_type="qecc_stabilizer",
        target_id=target_id,
        verdict=verdict,
        parameters=params,
        candidate=candidate,
        metadata=meta,
    )
    return GeneralizedCertificate(
        certificate_type=cert.certificate_type,
        target_id=cert.target_id,
        verdict=cert.verdict,
        parameters=cert.parameters,
        candidate=cert.candidate,
        metadata=cert.metadata,
        certificate_version=cert.certificate_version,
        sha256_checksum=cert.compute_checksum(),
    )


def extract_null_bound_certificate(
    target_id: str,
    family: str,
    parameters: dict[str, Any],
    group_name: str,
    group_order: int,
    orbit_count: int,
    orbit_lengths: list[int],
    min_orbit_length: int,
    published_best: int,
    proof_statement: str,
    metadata: dict[str, Any] | None = None,
) -> GeneralizedCertificate:
    """Create a canonical certificate for a proven structural obstruction (NULL_BOUND)."""
    candidate = {
        "group_name": group_name,
        "group_order": group_order,
        "orbit_count": orbit_count,
        "orbit_lengths": sorted(list(set(orbit_lengths))),
        "min_orbit_length": min_orbit_length,
        "published_best": published_best,
        "proof_statement": proof_statement,
    }

    params = dict(parameters)
    params["published_best"] = published_best

    meta = {
        "generator": "EvoByte Autonomous Discovery Engine",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "provenance": "P206 Preregistered Generalized Campaign",
    }
    if metadata:
        meta.update(metadata)

    cert = GeneralizedCertificate(
        certificate_type="structural_null_bound",
        target_id=target_id,
        verdict="NULL_BOUND",
        parameters=params,
        candidate=candidate,
        metadata=meta,
    )
    return GeneralizedCertificate(
        certificate_type=cert.certificate_type,
        target_id=cert.target_id,
        verdict=cert.verdict,
        parameters=cert.parameters,
        candidate=cert.candidate,
        metadata=cert.metadata,
        certificate_version=cert.certificate_version,
        sha256_checksum=cert.compute_checksum(),
    )


def extract_all_p207_certificates(
    p205_results_path: Path | str = "experiments/p205-calibration-results.json",
    p206_results_path: Path | str = "experiments/p206-generalized-campaign-results.json",
    output_dir: Path | str = "experiments/certificates",
) -> list[str]:
    """Extract and write all canonical v3.0.0 certificates from P205 and P206."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    saved_files: list[str] = []

    # 1. P205 Calibrations
    with open(p205_results_path, "r", encoding="utf-8") as f:
        p205 = json.load(f)

    # 1.1 C(9, 3, 2)
    cov_trial = p205["targets"]["covering_c9_3_2"]["trials"][0]
    cert_c9 = extract_affine_covering_certificate(
        target_id="calib_covering_C_9_3_2",
        v=9,
        k=3,
        t=2,
        blocks=cov_trial["blocks"],
        verdict="CALIBRATION_REPRODUCED",
        published_best=12,
        affine_plane=True,
        metadata={"seed": cov_trial["seed"], "solve_time_seconds": cov_trial["solve_time_seconds"]},
    )
    p_c9 = out_dir / "calib_covering_C_9_3_2.json"
    cert_c9.save(p_c9)
    saved_files.append(str(p_c9))

    # 1.2 Steane [[7, 1, 3]]
    steane_trial = p205["targets"]["steane_7_1_3"]["trials"][0]
    cert_steane = extract_qecc_certificate(
        target_id="calib_steane_7_1_3",
        n=7,
        k=1,
        claimed_d=3,
        generators=steane_trial["generators"],
        verdict="CALIBRATION_REPRODUCED",
        code_structure="steane_fano_css",
        metadata={
            "seed": steane_trial["seed"],
            "solve_time_seconds": steane_trial["solve_time_seconds"],
        },
    )
    p_steane = out_dir / "calib_steane_7_1_3.json"
    cert_steane.save(p_steane)
    saved_files.append(str(p_steane))

    # 1.3 Shor [[9, 1, 3]]
    shor_trial = p205["targets"]["shor_9_1_3"]["trials"][0]
    cert_shor = extract_qecc_certificate(
        target_id="calib_shor_9_1_3",
        n=9,
        k=1,
        claimed_d=3,
        generators=shor_trial["generators"],
        verdict="CALIBRATION_REPRODUCED",
        code_structure="non_circulant_stabilizer",
        metadata={
            "seed": shor_trial["seed"],
            "solve_time_seconds": shor_trial["solve_time_seconds"],
        },
    )
    p_shor = out_dir / "calib_shor_9_1_3.json"
    cert_shor.save(p_shor)
    saved_files.append(str(p_shor))

    # 2. P206 Campaign Discoveries
    with open(p206_results_path, "r", encoding="utf-8") as f:
        p206 = json.load(f)

    # 2.1 qecc_14_3 [[14, 3, 4]]
    t14 = p206["targets"]["qecc_14_3_noncirculant"]["trials"][0]
    cert_14 = extract_qecc_certificate(
        target_id="qecc_14_3_noncirculant",
        n=14,
        k=3,
        claimed_d=4,
        generators=t14["generators"],
        verdict="DISCOVERY_TIED",
        code_structure="non_circulant_css",
        metadata={"seed": t14["seed"], "wall_clock_seconds": t14["wall_clock_seconds"]},
    )
    p_14 = out_dir / "qecc_14_3_tied_record.json"
    cert_14.save(p_14)
    saved_files.append(str(p_14))

    # 2.2 qecc_16_5 [[16, 5, 4]]
    t16 = p206["targets"]["qecc_16_5_noncirculant"]["trials"][0]
    cert_16 = extract_qecc_certificate(
        target_id="qecc_16_5_noncirculant",
        n=16,
        k=5,
        claimed_d=4,
        generators=t16["generators"],
        verdict="DISCOVERY_TIED",
        code_structure="non_circulant_css",
        metadata={"seed": t16["seed"], "wall_clock_seconds": t16["wall_clock_seconds"]},
    )
    p_16 = out_dir / "qecc_16_5_tied_record.json"
    cert_16.save(p_16)
    saved_files.append(str(p_16))

    # 2.3 covering_C_13_5_3 NULL_BOUND
    t13 = p206["targets"]["covering_C_13_5_3_affine"]["trials"][0]
    d13 = t13["details"]
    cert_c13 = extract_null_bound_certificate(
        target_id="covering_C_13_5_3_affine",
        family="covering_design",
        parameters={"v": 13, "k": 5, "t": 3},
        group_name=d13["group"],
        group_order=d13["group_order"],
        orbit_count=d13["orbit_count"],
        orbit_lengths=d13["orbit_lengths"],
        min_orbit_length=d13["min_orbit_length"],
        published_best=34,
        proof_statement=d13["proof"],
    )
    p_c13 = out_dir / "covering_C_13_5_3_null_bound.json"
    cert_c13.save(p_c13)
    saved_files.append(str(p_c13))

    # 2.4 covering_C_15_10_4 NULL_BOUND
    t15 = p206["targets"]["covering_C_15_10_4_affine"]["trials"][0]
    d15 = t15["details"]
    cert_c15 = extract_null_bound_certificate(
        target_id="covering_C_15_10_4_affine",
        family="covering_design",
        parameters={"v": 15, "k": 10, "t": 4},
        group_name=d15["group"],
        group_order=d15["group_order"],
        orbit_count=d15["orbit_count"],
        orbit_lengths=d15["orbit_lengths"],
        min_orbit_length=d15["min_non_trivial_orbit_length"],
        published_best=14,
        proof_statement=d15["proof"],
    )
    p_c15 = out_dir / "covering_C_15_10_4_null_bound.json"
    cert_c15.save(p_c15)
    saved_files.append(str(p_c15))

    return saved_files


if __name__ == "__main__":
    files = extract_all_p207_certificates()
    print(f"Extracted {len(files)} certificates:")
    for f in files:
        print(f"  - {f}")
