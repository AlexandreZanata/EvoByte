"""Circuit evolution and superoptimization (spec: docs/quantum/ROADMAP.md, Q08).

Evolves quantum circuit bytecode toward target states or unitary operators
penalized by gate count, circuit depth, and two-qubit gate counts.
Provides exact unitary equivalence checking and certified superoptimization.
"""

from __future__ import annotations

import time
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np

from evobyte.quantum.circuit import (
    ANGLE_BANK,
    OPCODE_CNOT,
    OPCODE_CZ,
    OPCODE_H,
    OPCODE_NOP,
    OPCODE_RX,
    OPCODE_RY,
    OPCODE_RZ,
    OPCODE_S,
    OPCODE_SWAP,
    OPCODE_T,
    OPCODE_X,
    OPCODE_Y,
    OPCODE_Z,
    V0_GATE_TABLE,
    CircuitInstruction,
    circuit_depth,
    circuit_to_unitary,
    gate_count,
    strip_nops,
    two_qubit_count,
)

# Standard gate subset for general synthesis
DEFAULT_SYNTHESIS_GATES: tuple[int, ...] = (
    OPCODE_H,
    OPCODE_X,
    OPCODE_Y,
    OPCODE_Z,
    OPCODE_S,
    OPCODE_T,
    OPCODE_RX,
    OPCODE_RY,
    OPCODE_RZ,
    OPCODE_CNOT,
    OPCODE_CZ,
    OPCODE_SWAP,
)


@dataclass(frozen=True)
class EquivalenceCertificate:
    """Exact unitary equivalence certificate between two circuits (ignoring global phase)."""

    is_equivalent: bool
    process_fidelity: float
    global_phase_angle: float
    frobenius_error: float
    dim: int
    n_qubits: int
    orig_gates: int
    orig_depth: int
    orig_two_qubits: int
    opt_gates: int
    opt_depth: int
    opt_two_qubits: int

    @property
    def gate_reduction(self) -> int:
        return self.orig_gates - self.opt_gates

    @property
    def depth_reduction(self) -> int:
        return self.orig_depth - self.opt_depth

    @property
    def two_qubit_reduction(self) -> int:
        return self.orig_two_qubits - self.opt_two_qubits


# -----------------------------------------------------------------------------
# Unitary & State Equivalence Checking
# -----------------------------------------------------------------------------


def unitary_fidelity(u1: np.ndarray, u2: np.ndarray) -> tuple[float, float, float]:
    """Calculate process fidelity, optimal global phase angle, and phase-aligned Frobenius error.

    F_process = |Tr(U1^dag U2)|^2 / D^2 in [0, 1].
    Returns: (process_fidelity, phase_angle, frobenius_error).
    """
    dim = u1.shape[0]
    if u1.shape != u2.shape or dim == 0:
        raise ValueError(f"mismatched or empty unitary shapes: {u1.shape} vs {u2.shape}")

    m = u1.conj().T @ u2
    tr = complex(np.trace(m))
    tr_abs = abs(tr)
    proc_fid = float(np.clip((tr_abs**2) / (dim**2), 0.0, 1.0))

    if tr_abs < 1e-12:
        phase = 0.0
        aligned_err = float(np.linalg.norm(u1 - u2, ord="fro"))
    else:
        # Optimal phase e^{i phi} that aligns U2 to U1: U1 ~ e^{i phi} U2
        # argmax_phi Re(e^{-i phi} Tr(U1^dag U2)) -> phi = -arg(Tr(U1^dag U2))
        phase = float(-np.angle(tr))
        aligned_err = float(np.linalg.norm(u1 - np.exp(1.0j * phase) * u2, ord="fro"))

    return proc_fid, phase, aligned_err


def check_circuit_equivalence(
    circuit_ref: Sequence[CircuitInstruction],
    circuit_cand: Sequence[CircuitInstruction],
    n_qubits: int,
    tol: float = 1e-6,
) -> EquivalenceCertificate:
    """Verify whether two circuits implement the exact same unitary up to global phase."""
    u_ref = circuit_to_unitary(circuit_ref, n_qubits)
    u_cand = circuit_to_unitary(circuit_cand, n_qubits)

    proc_fid, phase, err = unitary_fidelity(u_ref, u_cand)
    is_equiv = bool((1.0 - proc_fid <= tol) and (err <= tol * (1 << n_qubits)))

    return EquivalenceCertificate(
        is_equivalent=is_equiv,
        process_fidelity=proc_fid,
        global_phase_angle=phase,
        frobenius_error=err,
        dim=1 << n_qubits,
        n_qubits=n_qubits,
        orig_gates=gate_count(circuit_ref),
        orig_depth=circuit_depth(circuit_ref, n_qubits),
        orig_two_qubits=two_qubit_count(circuit_ref),
        opt_gates=gate_count(circuit_cand),
        opt_depth=circuit_depth(circuit_cand, n_qubits),
        opt_two_qubits=two_qubit_count(circuit_cand),
    )


def state_fidelity(
    circuit: Sequence[CircuitInstruction],
    target_state: np.ndarray,
    n_qubits: int,
    initial_state: np.ndarray | None = None,
) -> float:
    """Compute state fidelity |<target | U | initial>|^2."""
    dim = 1 << n_qubits
    if initial_state is None:
        psi_0 = np.zeros(dim, dtype=np.complex128)
        psi_0[0] = 1.0  # |00...0>
    else:
        psi_0 = initial_state / np.linalg.norm(initial_state)

    target_norm = target_state / np.linalg.norm(target_state)
    u = circuit_to_unitary(circuit, n_qubits)
    psi_out = u @ psi_0
    overlap = np.vdot(target_norm, psi_out)
    return float(np.clip(abs(overlap) ** 2, 0.0, 1.0))


# -----------------------------------------------------------------------------
# Circuit Sampling and Genetic Operators
# -----------------------------------------------------------------------------


def sample_random_instruction(
    rng: np.random.Generator,
    n_qubits: int,
    allowed_opcodes: Sequence[int] | None = None,
) -> CircuitInstruction:
    """Sample a random valid quantum instruction."""
    opcodes = DEFAULT_SYNTHESIS_GATES if allowed_opcodes is None else allowed_opcodes
    gate = int(rng.choice(opcodes))
    info = V0_GATE_TABLE[gate]

    param = 0.0
    if info.is_parameterized:
        param = float(rng.choice(ANGLE_BANK))

    if info.num_qubits == 0:
        return CircuitInstruction(gate, 0, 0, param)

    if info.num_qubits == 1:
        qa = int(rng.integers(0, n_qubits))
        return CircuitInstruction(gate, qa, 0, param)

    # 2-qubit gate
    qa = int(rng.integers(0, n_qubits))
    qb = int(rng.integers(0, n_qubits - 1))
    if qb >= qa:
        qb += 1
    return CircuitInstruction(gate, qa, qb, param)


def sample_random_circuit(
    rng: np.random.Generator,
    n_qubits: int,
    max_gates: int = 6,
    allowed_opcodes: Sequence[int] | None = None,
) -> list[CircuitInstruction]:
    """Sample a random sequence of valid instructions."""
    n_gates = int(rng.integers(1, max_gates + 1))
    return [sample_random_instruction(rng, n_qubits, allowed_opcodes) for _ in range(n_gates)]


def mutate_circuit(
    circuit: list[CircuitInstruction],
    n_qubits: int,
    rng: np.random.Generator,
    p_mut: float = 0.35,
    max_gates: int = 12,
    allowed_opcodes: Sequence[int] | None = None,
) -> list[CircuitInstruction]:
    """Mutate a circuit by replacing, inserting, modifying, or deleting gates."""
    cand = [inst for inst in circuit if inst.gate != OPCODE_NOP]
    if len(cand) == 0:
        return [sample_random_instruction(rng, n_qubits, allowed_opcodes)]

    res: list[CircuitInstruction] = []

    for inst in cand:
        if rng.random() < p_mut:
            action = int(rng.integers(0, 5))
            if action == 0:
                # Replace with completely new random instruction
                res.append(sample_random_instruction(rng, n_qubits, allowed_opcodes))
            elif action == 1:
                # Modify operands while keeping gate
                info = V0_GATE_TABLE[inst.gate]
                param = inst.param
                if info.is_parameterized and rng.random() < 0.5:
                    param = float(rng.choice(ANGLE_BANK))
                if info.num_qubits == 1:
                    qa = int(rng.integers(0, n_qubits))
                    res.append(CircuitInstruction(inst.gate, qa, 0, param))
                elif info.num_qubits == 2:
                    qa = int(rng.integers(0, n_qubits))
                    qb = int(rng.integers(0, n_qubits - 1))
                    if qb >= qa:
                        qb += 1
                    res.append(CircuitInstruction(inst.gate, qa, qb, param))
                else:
                    res.append(inst)
            elif action == 2:
                # Delete gate (skip it)
                pass
            elif action == 3:
                # Mutate angle of parameterized gate
                info = V0_GATE_TABLE[inst.gate]
                if info.is_parameterized:
                    param = float(rng.choice(ANGLE_BANK))
                    res.append(CircuitInstruction(inst.gate, inst.qubit_a, inst.qubit_b, param))
                else:
                    res.append(inst)
            else:
                res.append(inst)
        else:
            res.append(inst)

    # Opportunity to insert a new gate if length permits
    if len(res) < max_gates and rng.random() < 0.3:
        insert_idx = int(rng.integers(0, len(res) + 1))
        new_inst = sample_random_instruction(rng, n_qubits, allowed_opcodes)
        res.insert(insert_idx, new_inst)

    return res[:max_gates]


def crossover_circuits(
    parent_a: list[CircuitInstruction],
    parent_b: list[CircuitInstruction],
    rng: np.random.Generator,
) -> tuple[list[CircuitInstruction], list[CircuitInstruction]]:
    """Splice crossover between two circuit instruction sequences."""
    clean_a = [inst for inst in parent_a if inst.gate != OPCODE_NOP]
    clean_b = [inst for inst in parent_b if inst.gate != OPCODE_NOP]

    if len(clean_a) == 0 or len(clean_b) == 0:
        return list(clean_a or clean_b), list(clean_b or clean_a)

    pt_a = int(rng.integers(0, len(clean_a) + 1))
    pt_b = int(rng.integers(0, len(clean_b) + 1))

    child_a = clean_a[:pt_a] + clean_b[pt_b:]
    child_b = clean_b[:pt_b] + clean_a[pt_a:]

    return child_a, child_b


# -----------------------------------------------------------------------------
# Circuit Evolution: Target State Preparation
# -----------------------------------------------------------------------------


def evolve_circuit_state_prep(
    target_state: np.ndarray,
    n_qubits: int,
    pop_size: int = 50,
    generations: int = 60,
    max_gates: int = 6,
    seed: int = 0,
    target_fidelity: float = 0.9999,
    w_gate: float = 1e-3,
    w_depth: float = 1e-3,
    w_two_qubit: float = 2e-3,
    allowed_opcodes: Sequence[int] | None = None,
) -> dict[str, Any]:
    """Evolve a quantum circuit from scratch to prepare target state from |0...0>."""
    rng = np.random.default_rng(seed)

    # 1. Initialize population
    population = [
        sample_random_circuit(rng, n_qubits, max_gates=max_gates, allowed_opcodes=allowed_opcodes)
        for _ in range(pop_size)
    ]

    t0 = time.perf_counter()
    best_cand: list[CircuitInstruction] = population[0]
    best_fid = 0.0
    best_score = -float("inf")
    best_gen = 0
    total_evals = 0
    tts: float | None = None
    tte: int | None = None

    for gen in range(generations):
        scores: list[float] = []
        fidelities: list[float] = []

        for cand in population:
            clean = strip_nops(cand)
            fid = state_fidelity(clean, target_state, n_qubits)
            total_evals += 1
            fidelities.append(fid)

            # Cost penalty for depth and gate counts
            cost = (
                w_gate * gate_count(clean)
                + w_depth * circuit_depth(clean, n_qubits)
                + w_two_qubit * two_qubit_count(clean)
            )

            # High fidelity bonus unlocks cost minimization
            if fid >= target_fidelity:
                score = 10.0 + (1.0 - cost)
                if tts is None:
                    tts = time.perf_counter() - t0
                    tte = total_evals
            else:
                score = fid - cost * 0.1

            scores.append(score)

            if score > best_score:
                best_score = score
                best_fid = fid
                best_cand = clean
                best_gen = gen

        # Early stopping if perfect target reached and circuit is minimal
        if best_fid >= target_fidelity and gate_count(best_cand) <= 2:
            break

        # 2. Reproduction
        sorted_idx = sorted(range(pop_size), key=lambda i: scores[i], reverse=True)
        new_pop = [population[sorted_idx[0]], population[sorted_idx[1]]]  # elitism

        # Random injection floor
        n_injected = max(1, int(pop_size * 0.15))
        for _ in range(n_injected):
            new_pop.append(
                sample_random_circuit(
                    rng, n_qubits, max_gates=max_gates, allowed_opcodes=allowed_opcodes
                )
            )

        while len(new_pop) < pop_size:
            # Tournament selection
            c1 = rng.choice(pop_size, size=3, replace=False)
            c2 = rng.choice(pop_size, size=3, replace=False)
            p1 = population[max(c1, key=lambda i: scores[i])]
            p2 = population[max(c2, key=lambda i: scores[i])]

            child_a, child_b = crossover_circuits(p1, p2, rng)
            child_a = mutate_circuit(
                child_a, n_qubits, rng, max_gates=max_gates, allowed_opcodes=allowed_opcodes
            )
            child_b = mutate_circuit(
                child_b, n_qubits, rng, max_gates=max_gates, allowed_opcodes=allowed_opcodes
            )

            new_pop.append(child_a)
            if len(new_pop) < pop_size:
                new_pop.append(child_b)

        population = new_pop

    dt = max(time.perf_counter() - t0, 1e-9)

    return {
        "best_circuit": best_cand,
        "fidelity": best_fid,
        "success": best_fid >= target_fidelity,
        "gate_count": gate_count(best_cand),
        "circuit_depth": circuit_depth(best_cand, n_qubits),
        "two_qubit_count": two_qubit_count(best_cand),
        "generations_run": gen + 1,
        "best_generation": best_gen,
        "evaluations": total_evals,
        "qvps": total_evals / dt,
        "elapsed_s": dt,
        "tts_s": tts,
        "tte_evals": tte,
        "seed": seed,
        "n_qubits": n_qubits,
    }


# -----------------------------------------------------------------------------
# Circuit Superoptimizer (Exact Unitary Equivalence + Cost Reduction)
# -----------------------------------------------------------------------------


def superoptimize_circuit(
    circuit_ref: Sequence[CircuitInstruction],
    n_qubits: int,
    pop_size: int = 60,
    generations: int = 50,
    seed: int = 0,
    tol: float = 1e-6,
    allowed_opcodes: Sequence[int] | None = None,
) -> dict[str, Any]:
    """Superoptimize circuit: find an exactly equivalent circuit with strictly lower cost."""
    rng = np.random.default_rng(seed)
    clean_ref = strip_nops(circuit_ref)
    ref_gates = gate_count(clean_ref)
    ref_depth = circuit_depth(clean_ref, n_qubits)
    ref_two_q = two_qubit_count(clean_ref)
    ref_cost = ref_gates + ref_depth + 2 * ref_two_q

    u_ref = circuit_to_unitary(clean_ref, n_qubits)

    # 1. Initialize population seeded with variations of reference + empty circuit + pruned/shorter circuits
    population: list[list[CircuitInstruction]] = [clean_ref, []]
    while len(population) < pop_size:
        if rng.random() < 0.4:
            # Perturbed copy of reference
            mut = mutate_circuit(
                clean_ref,
                n_qubits,
                rng,
                p_mut=0.4,
                max_gates=ref_gates,
                allowed_opcodes=allowed_opcodes,
            )
            population.append(mut)
        else:
            # Shorter candidate circuit
            short = sample_random_circuit(
                rng, n_qubits, max_gates=max(1, ref_gates - 1), allowed_opcodes=allowed_opcodes
            )
            population.append(short)

    t0 = time.perf_counter()
    best_cand = clean_ref
    best_cost = ref_cost
    best_cert = check_circuit_equivalence(clean_ref, clean_ref, n_qubits, tol=tol)
    total_evals = 0

    for gen in range(generations):
        scores: list[float] = []

        for cand in population:
            clean = strip_nops(cand)
            u_cand = circuit_to_unitary(clean, n_qubits)
            total_evals += 1

            fid, _, _ = unitary_fidelity(u_ref, u_cand)
            g = gate_count(clean)
            d = circuit_depth(clean, n_qubits)
            q2 = two_qubit_count(clean)
            cost = g + d + 2 * q2

            # Scoring: reward equivalent circuits with strictly lower cost
            if fid >= 1.0 - tol:
                # Exact equivalent!
                score = 100.0 + (ref_cost - cost) * 5.0
                if cost < best_cost:
                    cert = check_circuit_equivalence(clean_ref, clean, n_qubits, tol=tol)
                    if cert.is_equivalent:
                        best_cost = cost
                        best_cand = clean
                        best_cert = cert
            else:
                score = fid * 10.0 - cost * 0.05

            scores.append(score)

        # 2. Reproduction
        sorted_idx = sorted(range(pop_size), key=lambda i: scores[i], reverse=True)
        new_pop = [population[sorted_idx[0]], population[sorted_idx[1]]]

        # Injections
        for _ in range(max(1, int(pop_size * 0.15))):
            new_pop.append(
                sample_random_circuit(
                    rng,
                    n_qubits,
                    max_gates=max(1, gate_count(best_cand)),
                    allowed_opcodes=allowed_opcodes,
                )
            )

        while len(new_pop) < pop_size:
            c1 = rng.choice(pop_size, size=3, replace=False)
            c2 = rng.choice(pop_size, size=3, replace=False)
            p1 = population[max(c1, key=lambda i: scores[i])]
            p2 = population[max(c2, key=lambda i: scores[i])]

            child_a, child_b = crossover_circuits(p1, p2, rng)
            child_a = mutate_circuit(
                child_a, n_qubits, rng, max_gates=ref_gates, allowed_opcodes=allowed_opcodes
            )
            child_b = mutate_circuit(
                child_b, n_qubits, rng, max_gates=ref_gates, allowed_opcodes=allowed_opcodes
            )

            new_pop.append(child_a)
            if len(new_pop) < pop_size:
                new_pop.append(child_b)

        population = new_pop

    dt = max(time.perf_counter() - t0, 1e-9)

    return {
        "best_circuit": best_cand,
        "reference_circuit": clean_ref,
        "certificate": best_cert,
        "is_equivalent": best_cert.is_equivalent,
        "gate_reduction": best_cert.gate_reduction,
        "depth_reduction": best_cert.depth_reduction,
        "two_qubit_reduction": best_cert.two_qubit_reduction,
        "improved": best_cost < ref_cost,
        "generations_run": gen + 1,
        "evaluations": total_evals,
        "qvps": total_evals / dt,
        "elapsed_s": dt,
        "seed": seed,
    }
