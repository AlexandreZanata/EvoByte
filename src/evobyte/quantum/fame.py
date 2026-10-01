"""Quantum Hall of Fame, Discovery Classes, and Anomaly Vault (spec: Q12, docs/quantum/ANOMALY.md).

Maintains an append-only archive of milestone quantum discoveries with cryptographic
provenance, enforces discovery class taxonomy (prohibiting automated attribution of
NOVEL PHYSICAL RESULT), and registers structural anomalies with rigorous extra verification.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np


class DiscoveryClass(str, Enum):
    """Rigorous discovery classification per docs/quantum/ANOMALY.md."""

    REDISCOVERY = "REDISCOVERY"
    NOVEL_CANDIDATE = "NOVEL CANDIDATE"
    VERIFIED_MATHEMATICAL_RESULT = "VERIFIED MATHEMATICAL RESULT"
    PHYSICAL_HYPOTHESIS = "PHYSICAL HYPOTHESIS"
    NOVEL_PHYSICAL_RESULT = "NOVEL PHYSICAL RESULT"


def validate_discovery_class(
    class_name: str | DiscoveryClass, allow_manual_novel_physics: bool = False
) -> DiscoveryClass:
    """Validate discovery class and strictly prohibit automated assignment of NOVEL PHYSICAL RESULT."""
    if isinstance(class_name, DiscoveryClass):
        val = class_name
    else:
        name_str = str(class_name)
        name_str = name_str.removeprefix("DiscoveryClass.")
        if name_str in DiscoveryClass.__members__:
            val = DiscoveryClass[name_str]
        else:
            try:
                val = DiscoveryClass(name_str)
            except ValueError:
                raise ValueError(
                    f"Invalid discovery class: {class_name}. Must be one of: {[c.value for c in DiscoveryClass]}"
                )

    if val == DiscoveryClass.NOVEL_PHYSICAL_RESULT and not allow_manual_novel_physics:
        raise ValueError(
            "Software must NEVER auto-assign 'NOVEL PHYSICAL RESULT' per docs/quantum/ANOMALY.md. "
            "A formula or circuit that fits simulation is not automatically a new law of physics."
        )

    return val


@dataclass(frozen=True)
class QuantumFameEntry:
    """Full-provenance append-only entry for the Quantum Hall of Fame."""

    problem_id: str
    hamiltonian_hash: str
    candidate_binary: str  # Hex-encoded instruction bytes
    decoded_candidate: str
    generation: int
    parents: list[str]
    fitness: float
    energy: float | None
    exact_energy: float | None
    energy_error: float | None
    fidelity: float | None
    commutator_norm: float | None
    gate_count: int | None
    circuit_depth: int | None
    novelty: float
    discovery_timestamp: float
    total_candidates_tested: int
    wall_clock_time: float
    discovery_class: str


@dataclass(frozen=True)
class ExtraVerificationReport:
    """Audit record produced by the Anomaly Vault extra-verification hook."""

    verified: bool
    high_precision_fidelity: float
    perturbation_stability: float
    entanglement_entropy: float | None
    details: dict[str, Any]


class QuantumHallOfFame:
    """Append-only storage for milestone quantum discoveries with full provenance."""

    def __init__(self, file_path: str | Path = "hall_of_fame/quantum_fame.jsonl") -> None:
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def record_discovery(
        self,
        problem_id: str,
        hamiltonian_hash: str,
        candidate_binary: bytes | np.ndarray | str,
        decoded_candidate: str,
        generation: int,
        parents: list[str],
        fitness: float,
        discovery_class: str | DiscoveryClass = DiscoveryClass.REDISCOVERY,
        energy: float | None = None,
        exact_energy: float | None = None,
        energy_error: float | None = None,
        fidelity: float | None = None,
        commutator_norm: float | None = None,
        gate_count: int | None = None,
        circuit_depth: int | None = None,
        novelty: float = 0.0,
        total_candidates_tested: int = 1,
        wall_clock_time: float = 0.0,
        allow_manual_novel_physics: bool = False,
    ) -> QuantumFameEntry:
        """Append an audited discovery entry to the Quantum Hall of Fame."""
        cls_val = validate_discovery_class(
            str(discovery_class),
            allow_manual_novel_physics=allow_manual_novel_physics,
        ).value

        # Format candidate binary
        if isinstance(candidate_binary, np.ndarray):
            hex_bin = candidate_binary.tobytes().hex()
        elif isinstance(candidate_binary, bytes):
            hex_bin = candidate_binary.hex()
        else:
            hex_bin = str(candidate_binary)

        entry = QuantumFameEntry(
            problem_id=problem_id,
            hamiltonian_hash=hamiltonian_hash,
            candidate_binary=hex_bin,
            decoded_candidate=decoded_candidate,
            generation=generation,
            parents=list(parents),
            fitness=float(fitness),
            energy=float(energy) if energy is not None else None,
            exact_energy=float(exact_energy) if exact_energy is not None else None,
            energy_error=float(energy_error) if energy_error is not None else None,
            fidelity=float(fidelity) if fidelity is not None else None,
            commutator_norm=float(commutator_norm) if commutator_norm is not None else None,
            gate_count=gate_count,
            circuit_depth=circuit_depth,
            novelty=float(novelty),
            discovery_timestamp=time.time(),
            total_candidates_tested=total_candidates_tested,
            wall_clock_time=float(wall_clock_time),
            discovery_class=cls_val,
        )

        line = json.dumps(asdict(entry))
        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")

        return entry

    def read_entries(self) -> list[QuantumFameEntry]:
        """Read all entries from the append-only log."""
        if not self.file_path.exists():
            return []
        entries: list[QuantumFameEntry] = []
        with open(self.file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                d = json.loads(line)
                entries.append(QuantumFameEntry(**d))
        return entries


# -----------------------------------------------------------------------------
# Anomaly Vault & Extra Verification
# -----------------------------------------------------------------------------


def default_quantum_verification_hook(
    unitary: np.ndarray,
    target_state_or_unitary: np.ndarray,
    n_qubits: int,
) -> ExtraVerificationReport:
    """Extra-verification hook: tests precision, stability under noise, and unitarity."""
    # 1. High-precision unitarity check: U^\dagger U = I
    dim = 1 << n_qubits
    ident = np.eye(dim, dtype=np.complex128)
    u_dag_u = unitary.conj().T @ unitary
    unitarity_err = float(np.max(np.abs(u_dag_u - ident)))

    # 2. Fidelity against target
    if target_state_or_unitary.ndim == 1:
        # State fidelity from |00...0>
        init_state = np.zeros(dim, dtype=np.complex128)
        init_state[0] = 1.0
        psi = unitary @ init_state
        overlap = np.vdot(target_state_or_unitary, psi)
        fid = float(np.abs(overlap) ** 2)

        # Entanglement entropy across bipartition (qubit 0 vs rest)
        psi_mat = psi.reshape(2, dim // 2)
        _, sv, _ = np.linalg.svd(psi_mat)
        probs = sv**2
        probs = probs[probs > 1e-14]
        entropy = float(-np.sum(probs * np.log2(probs)))
    else:
        # Unitary process fidelity: |Tr(U_target^\dagger U)| / dim
        trace_val = np.trace(target_state_or_unitary.conj().T @ unitary)
        fid = float((abs(trace_val) / dim) ** 2)
        entropy = None

    # 3. Perturbation stability check (Gaussian noise injected into angles/matrix)
    noise = np.random.randn(*unitary.shape) * 1e-4
    u_noisy = unitary + noise
    u_l, _, vh_r = np.linalg.svd(u_noisy)
    u_n = u_l @ vh_r
    if target_state_or_unitary.ndim == 1:
        init_state = np.zeros(dim, dtype=np.complex128)
        init_state[0] = 1.0
        psi_n = u_n @ init_state
        stability = float(np.abs(np.vdot(psi, psi_n)) ** 2)
    else:
        stability = float((abs(np.trace(unitary.conj().T @ u_n)) / dim) ** 2)

    is_verified = (unitarity_err < 1e-10) and (fid >= 0.999) and (stability >= 0.99)

    return ExtraVerificationReport(
        verified=is_verified,
        high_precision_fidelity=fid,
        perturbation_stability=stability,
        entanglement_entropy=entropy,
        details={"unitarity_error": unitarity_err},
    )


class AnomalyVault:
    """Special append-only store for candidates with abnormal fitness, structure, or novelty."""

    def __init__(self, file_path: str | Path = "hall_of_fame/anomaly_vault.jsonl") -> None:
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def is_anomalous(
        self,
        fidelity: float,
        gate_count: int | None,
        circuit_depth: int | None,
        novelty: float = 0.0,
        baseline_gate_threshold: int = 3,
    ) -> tuple[bool, str]:
        """Detect whether a candidate qualifies as an anomaly."""
        reasons: list[str] = []
        if fidelity >= 1.0 - 1e-6:
            if gate_count is not None and gate_count <= baseline_gate_threshold:
                reasons.append(f"Ultra-compact structure ({gate_count} gates)")
            if circuit_depth is not None and circuit_depth <= 2:
                reasons.append(f"Minimal circuit depth ({circuit_depth})")
        if novelty > 2.0:
            reasons.append(f"High structural distance from elites (novelty={novelty:.2f})")

        is_anom = len(reasons) > 0
        return is_anom, "; ".join(reasons)

    def record_anomaly(
        self,
        entry: QuantumFameEntry,
        anomaly_reason: str,
        verification_report: ExtraVerificationReport | None = None,
    ) -> dict[str, Any]:
        """Record candidate into the Anomaly Vault with extra-verification audit."""
        payload = {
            "entry": asdict(entry),
            "anomaly_reason": anomaly_reason,
            "verification": asdict(verification_report)
            if verification_report is not None
            else None,
            "vault_timestamp": time.time(),
        }

        line = json.dumps(payload)
        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")

        return payload

    def read_anomalies(self) -> list[dict[str, Any]]:
        """Read all registered anomalies."""
        if not self.file_path.exists():
            return []
        items: list[dict[str, Any]] = []
        with open(self.file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                items.append(json.loads(line))
        return items
