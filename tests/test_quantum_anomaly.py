"""Tests for Quantum Hall of Fame, Discovery Classes, and Anomaly Vault (spec: Q12).

Validates discovery class enforcement (software never auto-assigns NOVEL PHYSICAL RESULT),
append-only Hall of Fame serialization, Anomaly Vault detection, and extra-verification hook.
"""

from __future__ import annotations

import numpy as np
import pytest

from evobyte.quantum.circuit import (
    OPCODE_CNOT,
    OPCODE_H,
    CircuitInstruction,
    circuit_to_unitary,
)
from evobyte.quantum.fame import (
    AnomalyVault,
    DiscoveryClass,
    ExtraVerificationReport,
    QuantumHallOfFame,
    default_quantum_verification_hook,
    validate_discovery_class,
)


def test_discovery_class_validation():
    """Verify discovery classes and prohibition of automated NOVEL PHYSICAL RESULT."""
    # Standard valid classes
    assert validate_discovery_class("REDISCOVERY") == DiscoveryClass.REDISCOVERY
    assert validate_discovery_class("NOVEL CANDIDATE") == DiscoveryClass.NOVEL_CANDIDATE
    assert validate_discovery_class("VERIFIED MATHEMATICAL RESULT") == DiscoveryClass.VERIFIED_MATHEMATICAL_RESULT
    assert validate_discovery_class("PHYSICAL HYPOTHESIS") == DiscoveryClass.PHYSICAL_HYPOTHESIS

    # Automated assignment of NOVEL PHYSICAL RESULT is strictly forbidden
    with pytest.raises(ValueError, match="Software must NEVER auto-assign 'NOVEL PHYSICAL RESULT'"):
        validate_discovery_class("NOVEL PHYSICAL RESULT", allow_manual_novel_physics=False)

    # Manual human override allows NOVEL PHYSICAL RESULT
    assert (
        validate_discovery_class("NOVEL PHYSICAL RESULT", allow_manual_novel_physics=True)
        == DiscoveryClass.NOVEL_PHYSICAL_RESULT
    )

    # Completely invalid class
    with pytest.raises(ValueError, match="Invalid discovery class"):
        validate_discovery_class("INVALID_CLASS")


def test_quantum_hall_of_fame_append_only(tmp_path):
    """Verify Quantum Hall of Fame is strictly append-only and retains full provenance."""
    fame_file = tmp_path / "quantum_fame.jsonl"
    fame = QuantumHallOfFame(fame_file)

    # Entry 1: Bell state discovery
    e1 = fame.record_discovery(
        problem_id="bell_state_preparation",
        hamiltonian_hash="hash_bell",
        candidate_binary=np.array([1, 2, 3], dtype=np.uint8),
        decoded_candidate="H q0 ; CNOT q0, q1",
        generation=1,
        parents=["root_sample"],
        fitness=0.0,
        fidelity=1.0,
        gate_count=2,
        circuit_depth=2,
        discovery_class=DiscoveryClass.REDISCOVERY,
        total_candidates_tested=42,
        wall_clock_time=0.015,
    )

    # Entry 2: GHZ state discovery
    e2 = fame.record_discovery(
        problem_id="ghz_state_preparation",
        hamiltonian_hash="hash_ghz",
        candidate_binary=np.array([4, 5, 6], dtype=np.uint8),
        decoded_candidate="H q0 ; CNOT q0, q1 ; CNOT q1, q2",
        generation=3,
        parents=["seed_0"],
        fitness=0.0,
        fidelity=1.0,
        gate_count=3,
        circuit_depth=3,
        discovery_class=DiscoveryClass.VERIFIED_MATHEMATICAL_RESULT,
        total_candidates_tested=120,
        wall_clock_time=0.045,
    )

    entries = fame.read_entries()
    assert len(entries) == 2
    assert entries[0].problem_id == "bell_state_preparation"
    assert entries[0].gate_count == 2
    assert entries[1].problem_id == "ghz_state_preparation"
    assert entries[1].gate_count == 3
    assert entries[0].discovery_class == "REDISCOVERY"
    assert entries[1].discovery_class == "VERIFIED MATHEMATICAL RESULT"


def test_anomaly_vault_detection_criteria():
    """Verify AnomalyVault identifies ultra-compact or high-novelty candidates."""
    vault = AnomalyVault()

    # Ultra-compact candidate: 2 gates with perfect fidelity
    is_anom1, reason1 = vault.is_anomalous(fidelity=1.0, gate_count=2, circuit_depth=2, novelty=0.1)
    assert is_anom1
    assert "Ultra-compact" in reason1

    # Normal candidate: 8 gates, low novelty
    is_anom2, reason2 = vault.is_anomalous(fidelity=0.95, gate_count=8, circuit_depth=6, novelty=0.5)
    assert not is_anom2
    assert reason2 == ""

    # High novelty candidate (> 2.0)
    is_anom3, reason3 = vault.is_anomalous(fidelity=0.999, gate_count=5, circuit_depth=4, novelty=2.8)
    assert is_anom3
    assert "High structural distance" in reason3


def test_anomaly_vault_with_extra_verification(tmp_path):
    """Verify AnomalyVault extra-verification hook audits unitarity and entanglement."""
    vault_file = tmp_path / "anomaly_vault.jsonl"
    vault = AnomalyVault(vault_file)
    fame = QuantumHallOfFame(tmp_path / "fame.jsonl")

    # Standard Bell circuit
    bell_circuit = [
        CircuitInstruction(OPCODE_H, qubit_a=0, qubit_b=0, param=0.0),
        CircuitInstruction(OPCODE_CNOT, qubit_a=0, qubit_b=1, param=0.0),
    ]
    u_bell = circuit_to_unitary(bell_circuit, n_qubits=2)
    target_bell = np.array([1, 0, 0, 1], dtype=np.complex128) / np.sqrt(2)

    # Extra verification audit
    audit = default_quantum_verification_hook(u_bell, target_bell, n_qubits=2)
    assert audit.verified
    assert abs(audit.high_precision_fidelity - 1.0) < 1e-10
    assert audit.entanglement_entropy is not None
    assert abs(audit.entanglement_entropy - 1.0) < 1e-6  # Exact 1.0 ebit
    assert audit.details["unitarity_error"] < 1e-12

    # Record in Vault
    entry = fame.record_discovery(
        problem_id="bell",
        hamiltonian_hash="bell_hash",
        candidate_binary="aabb",
        decoded_candidate="H q0 ; CNOT q0, q1",
        generation=1,
        parents=[],
        fitness=0.0,
        fidelity=1.0,
        gate_count=2,
        circuit_depth=2,
    )

    vault_res = vault.record_anomaly(entry, "Ultra-compact Bell circuit (2 gates)", verification_report=audit)
    assert vault_res["verification"]["verified"] is True
    assert vault_res["anomaly_reason"] == "Ultra-compact Bell circuit (2 gates)"

    anomalies = vault.read_anomalies()
    assert len(anomalies) == 1
    assert anomalies[0]["entry"]["problem_id"] == "bell"
