"""Quantum circuit bytecode codec and v0 gate table (spec: docs/quantum/REPRESENTATION.md, Q07).

Fixed-width instruction representation [GATE, QUBIT_A, QUBIT_B, PARAM],
frozen v0 gate table, qubit-range validation, circuit depth and gate count accounting,
NOP-equivalent padding, and human decoder for logs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np

# Bytecode versioning per AGENTS.md / ARCHITECTURE.md
CIRCUIT_BYTECODE_VERSION: int = 0

# Opcodes for v0 frozen gate table
OPCODE_NOP: int = 0
OPCODE_H: int = 1
OPCODE_X: int = 2
OPCODE_Y: int = 3
OPCODE_Z: int = 4
OPCODE_S: int = 5
OPCODE_T: int = 6
OPCODE_RX: int = 7
OPCODE_RY: int = 8
OPCODE_RZ: int = 9
OPCODE_CNOT: int = 10
OPCODE_CZ: int = 11
OPCODE_SWAP: int = 12

# Standard quantized angle bank for discrete structure search
ANGLE_BANK: tuple[float, ...] = (
    0.0,
    np.pi / 4.0,
    np.pi / 2.0,
    3.0 * np.pi / 4.0,
    np.pi,
    -np.pi / 4.0,
    -np.pi / 2.0,
    -3.0 * np.pi / 4.0,
)


@dataclass(frozen=True)
class GateInfo:
    """Static metadata for a gate opcode."""

    opcode: int
    name: str
    num_qubits: int
    is_parameterized: bool


# Frozen v0 gate table
V0_GATE_TABLE: dict[int, GateInfo] = {
    OPCODE_NOP: GateInfo(opcode=OPCODE_NOP, name="NOP", num_qubits=0, is_parameterized=False),
    OPCODE_H: GateInfo(opcode=OPCODE_H, name="H", num_qubits=1, is_parameterized=False),
    OPCODE_X: GateInfo(opcode=OPCODE_X, name="X", num_qubits=1, is_parameterized=False),
    OPCODE_Y: GateInfo(opcode=OPCODE_Y, name="Y", num_qubits=1, is_parameterized=False),
    OPCODE_Z: GateInfo(opcode=OPCODE_Z, name="Z", num_qubits=1, is_parameterized=False),
    OPCODE_S: GateInfo(opcode=OPCODE_S, name="S", num_qubits=1, is_parameterized=False),
    OPCODE_T: GateInfo(opcode=OPCODE_T, name="T", num_qubits=1, is_parameterized=False),
    OPCODE_RX: GateInfo(opcode=OPCODE_RX, name="RX", num_qubits=1, is_parameterized=True),
    OPCODE_RY: GateInfo(opcode=OPCODE_RY, name="RY", num_qubits=1, is_parameterized=True),
    OPCODE_RZ: GateInfo(opcode=OPCODE_RZ, name="RZ", num_qubits=1, is_parameterized=True),
    OPCODE_CNOT: GateInfo(opcode=OPCODE_CNOT, name="CNOT", num_qubits=2, is_parameterized=False),
    OPCODE_CZ: GateInfo(opcode=OPCODE_CZ, name="CZ", num_qubits=2, is_parameterized=False),
    OPCODE_SWAP: GateInfo(opcode=OPCODE_SWAP, name="SWAP", num_qubits=2, is_parameterized=False),
}

# Reverse lookup by name (case-insensitive)
NAME_TO_OPCODE: dict[str, int] = {info.name.upper(): op for op, info in V0_GATE_TABLE.items()}


@dataclass(frozen=True)
class CircuitInstruction:
    """Single fixed-width instruction: [GATE, QUBIT_A, QUBIT_B, PARAM]."""

    gate: int
    qubit_a: int = 0
    qubit_b: int = 0
    param: float = 0.0

    def to_tuple(self) -> tuple[int, int, int, float]:
        """Convert to (gate, qubit_a, qubit_b, param) tuple."""
        return (self.gate, self.qubit_a, self.qubit_b, float(self.param))


# -----------------------------------------------------------------------------
# Codec and Conversions
# -----------------------------------------------------------------------------

def encode_circuit(instructions: Sequence[CircuitInstruction | tuple[int, int, int, float]]) -> np.ndarray:
    """Encode instructions into an (L, 4) float64 ndarray buffer."""
    if len(instructions) == 0:
        return np.zeros((0, 4), dtype=np.float64)

    buf = np.zeros((len(instructions), 4), dtype=np.float64)
    for i, inst in enumerate(instructions):
        if isinstance(inst, CircuitInstruction):
            buf[i] = [inst.gate, inst.qubit_a, inst.qubit_b, inst.param]
        else:
            buf[i] = [inst[0], inst[1], inst[2], inst[3]]
    return buf


def decode_circuit(buffer: np.ndarray | Sequence[Any]) -> list[CircuitInstruction]:
    """Decode an (L, 4) array or list of tuples into CircuitInstruction objects."""
    arr = np.asarray(buffer, dtype=np.float64)
    if arr.ndim == 1:
        if arr.size == 0:
            return []
        if arr.size % 4 != 0:
            raise ValueError(f"1D buffer size {arr.size} is not a multiple of 4")
        arr = arr.reshape(-1, 4)
    elif arr.ndim == 2:
        if arr.shape[1] != 4:
            raise ValueError(f"expected 2D buffer with shape (L, 4), got {arr.shape}")
    else:
        raise ValueError(f"unsupported buffer dimension {arr.ndim}")

    instructions: list[CircuitInstruction] = []
    for row in arr:
        gate = int(np.round(row[0]))
        qa = int(np.round(row[1]))
        qb = int(np.round(row[2]))
        param = float(row[3])
        instructions.append(CircuitInstruction(gate, qa, qb, param))
    return instructions


# -----------------------------------------------------------------------------
# Validation
# -----------------------------------------------------------------------------

def validate_instruction(inst: CircuitInstruction, n_qubits: int) -> tuple[bool, str]:
    """Validate a single instruction against qubit bounds and gate specifications."""
    if n_qubits <= 0:
        return False, f"n_qubits must be positive, got {n_qubits}"

    if inst.gate not in V0_GATE_TABLE:
        return False, f"unknown gate opcode {inst.gate} (not in v0 gate table)"

    info = V0_GATE_TABLE[inst.gate]

    if not np.isfinite(inst.param):
        return False, f"parameter {inst.param} is not finite"

    if info.num_qubits == 0:
        # NOP
        return True, ""

    if info.num_qubits == 1:
        if not (0 <= inst.qubit_a < n_qubits):
            return False, f"qubit_a={inst.qubit_a} out of range [0, {n_qubits}) for gate {info.name}"
        return True, ""

    if info.num_qubits == 2:
        if not (0 <= inst.qubit_a < n_qubits):
            return False, f"qubit_a={inst.qubit_a} out of range [0, {n_qubits}) for gate {info.name}"
        if not (0 <= inst.qubit_b < n_qubits):
            return False, f"qubit_b={inst.qubit_b} out of range [0, {n_qubits}) for gate {info.name}"
        if inst.qubit_a == inst.qubit_b:
            return False, f"qubit_a and qubit_b must be distinct for 2-qubit gate {info.name}, got {inst.qubit_a}"
        return True, ""

    return False, f"unsupported arity {info.num_qubits} for gate {info.name}"


def validate_circuit(
    circuit: Sequence[CircuitInstruction | tuple[int, int, int, float]] | np.ndarray,
    n_qubits: int,
) -> bool:
    """Validate entire circuit against qubit bounds; raises ValueError on violation."""
    if isinstance(circuit, np.ndarray):
        insts = decode_circuit(circuit)
    elif len(circuit) > 0 and not isinstance(circuit[0], CircuitInstruction):
        insts = decode_circuit(circuit)
    else:
        insts = list(circuit)  # type: ignore[arg-type]

    for idx, inst in enumerate(insts):
        valid, err = validate_instruction(inst, n_qubits)
        if not valid:
            raise ValueError(f"circuit validation error at index {idx}: {err}")
    return True


def is_valid_circuit(
    circuit: Sequence[CircuitInstruction | tuple[int, int, int, float]] | np.ndarray,
    n_qubits: int,
) -> bool:
    """Check if circuit is valid without raising exceptions."""
    try:
        return validate_circuit(circuit, n_qubits)
    except (ValueError, TypeError):
        return False


# -----------------------------------------------------------------------------
# Accounting: Depth, Gate Counts, and Padding
# -----------------------------------------------------------------------------

def gate_count(circuit: Sequence[CircuitInstruction | tuple[int, int, int, float]] | np.ndarray) -> int:
    """Count non-NOP instructions in circuit."""
    insts = decode_circuit(circuit) if not isinstance(circuit, list) or (circuit and not isinstance(circuit[0], CircuitInstruction)) else circuit
    return sum(1 for inst in insts if inst.gate != OPCODE_NOP)  # type: ignore[union-attr]


def two_qubit_count(circuit: Sequence[CircuitInstruction | tuple[int, int, int, float]] | np.ndarray) -> int:
    """Count 2-qubit instructions (CNOT, CZ, SWAP) in circuit."""
    insts = decode_circuit(circuit) if not isinstance(circuit, list) or (circuit and not isinstance(circuit[0], CircuitInstruction)) else circuit
    count = 0
    for inst in insts:
        info = V0_GATE_TABLE.get(inst.gate)  # type: ignore[union-attr]
        if info is not None and info.num_qubits == 2:
            count += 1
    return count


def circuit_depth(
    circuit: Sequence[CircuitInstruction | tuple[int, int, int, float]] | np.ndarray,
    n_qubits: int,
) -> int:
    """Calculate critical-path circuit depth (NOPs contribute 0 depth)."""
    if n_qubits <= 0:
        return 0

    insts = decode_circuit(circuit) if not isinstance(circuit, list) or (circuit and not isinstance(circuit[0], CircuitInstruction)) else circuit
    qubit_depth = np.zeros(n_qubits, dtype=np.int32)

    for inst in insts:
        gate = inst.gate  # type: ignore[union-attr]
        if gate == OPCODE_NOP:
            continue

        info = V0_GATE_TABLE.get(gate)
        if info is None:
            continue

        qa = inst.qubit_a  # type: ignore[union-attr]
        qb = inst.qubit_b  # type: ignore[union-attr]

        if info.num_qubits == 1:
            if 0 <= qa < n_qubits:
                qubit_depth[qa] += 1
        elif info.num_qubits == 2:
            if 0 <= qa < n_qubits and 0 <= qb < n_qubits:
                step = max(qubit_depth[qa], qubit_depth[qb]) + 1
                qubit_depth[qa] = step
                qubit_depth[qb] = step

    return int(np.max(qubit_depth)) if len(qubit_depth) > 0 else 0


def pad_circuit(
    circuit: Sequence[CircuitInstruction | tuple[int, int, int, float]] | np.ndarray,
    target_length: int,
) -> list[CircuitInstruction]:
    """Pad circuit with NOP instructions to fixed length."""
    insts = decode_circuit(circuit) if not isinstance(circuit, list) or (circuit and not isinstance(circuit[0], CircuitInstruction)) else list(circuit)  # type: ignore[arg-type]
    if len(insts) > target_length:
        raise ValueError(f"circuit length {len(insts)} exceeds target_length {target_length}")

    padded = list(insts)
    nop = CircuitInstruction(OPCODE_NOP, 0, 0, 0.0)
    while len(padded) < target_length:
        padded.append(nop)
    return padded


def strip_nops(
    circuit: Sequence[CircuitInstruction | tuple[int, int, int, float]] | np.ndarray,
) -> list[CircuitInstruction]:
    """Strip all NOP instructions from circuit."""
    insts = decode_circuit(circuit) if not isinstance(circuit, list) or (circuit and not isinstance(circuit[0], CircuitInstruction)) else circuit
    return [inst for inst in insts if inst.gate != OPCODE_NOP]  # type: ignore[union-attr]


# -----------------------------------------------------------------------------
# Human-Readable Decoder for Logs
# -----------------------------------------------------------------------------

def decode_instruction_text(inst: CircuitInstruction) -> str:
    """Format single instruction as human-readable string for logs."""
    info = V0_GATE_TABLE.get(inst.gate)
    if info is None:
        return f"UNKNOWN({inst.gate}, {inst.qubit_a}, {inst.qubit_b}, {inst.param})"

    if info.opcode == OPCODE_NOP:
        return "NOP"

    if info.is_parameterized:
        return f"{info.name}({inst.param:.4f}) q[{inst.qubit_a}]"

    if info.num_qubits == 1:
        return f"{info.name} q[{inst.qubit_a}]"

    if info.num_qubits == 2:
        return f"{info.name} q[{inst.qubit_a}], q[{inst.qubit_b}]"

    return f"{info.name}(q[{inst.qubit_a}], q[{inst.qubit_b}])"


def decode_circuit_text(
    circuit: Sequence[CircuitInstruction | tuple[int, int, int, float]] | np.ndarray,
    multiline: bool = False,
) -> str:
    """Format entire circuit as human-readable string for logs and artifacts."""
    insts = decode_circuit(circuit) if not isinstance(circuit, list) or (circuit and not isinstance(circuit[0], CircuitInstruction)) else circuit
    tokens = [decode_instruction_text(inst) for inst in insts]  # type: ignore[arg-type]
    if multiline:
        return "\n".join(tokens)
    return "; ".join(tokens)


# -----------------------------------------------------------------------------
# Unitary Matrix Simulator (Verification and Equivalence Testing)
# -----------------------------------------------------------------------------

def single_qubit_gate_matrix(gate: int, param: float = 0.0) -> np.ndarray:
    """2x2 complex unitary matrix for 1-qubit gate."""
    if gate == OPCODE_NOP:
        return np.eye(2, dtype=np.complex128)
    if gate == OPCODE_H:
        return np.array([[1.0, 1.0], [1.0, -1.0]], dtype=np.complex128) / np.sqrt(2.0)
    if gate == OPCODE_X:
        return np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128)
    if gate == OPCODE_Y:
        return np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=np.complex128)
    if gate == OPCODE_Z:
        return np.array([[1.0, 0.0], [0.0, -1.0]], dtype=np.complex128)
    if gate == OPCODE_S:
        return np.array([[1.0, 0.0], [0.0, 1.0j]], dtype=np.complex128)
    if gate == OPCODE_T:
        return np.array([[1.0, 0.0], [0.0, np.exp(1.0j * np.pi / 4.0)]], dtype=np.complex128)
    if gate == OPCODE_RX:
        c = np.cos(param / 2.0)
        s = np.sin(param / 2.0)
        return np.array([[c, -1.0j * s], [-1.0j * s, c]], dtype=np.complex128)
    if gate == OPCODE_RY:
        c = np.cos(param / 2.0)
        s = np.sin(param / 2.0)
        return np.array([[c, -s], [s, c]], dtype=np.complex128)
    if gate == OPCODE_RZ:
        return np.array([
            [np.exp(-1.0j * param / 2.0), 0.0],
            [0.0, np.exp(1.0j * param / 2.0)],
        ], dtype=np.complex128)
    raise ValueError(f"not a 1-qubit gate: opcode {gate}")


def circuit_to_unitary(
    circuit: Sequence[CircuitInstruction | tuple[int, int, int, float]] | np.ndarray,
    n_qubits: int,
) -> np.ndarray:
    """Build exact 2^N x 2^N unitary matrix for circuit (strict verification)."""
    validate_circuit(circuit, n_qubits)
    insts = decode_circuit(circuit) if not isinstance(circuit, list) or (circuit and not isinstance(circuit[0], CircuitInstruction)) else circuit
    dim = 1 << n_qubits
    u_total = np.eye(dim, dtype=np.complex128)

    for inst in insts:
        gate = inst.gate  # type: ignore[union-attr]
        if gate == OPCODE_NOP:
            continue

        info = V0_GATE_TABLE[gate]
        qa = inst.qubit_a  # type: ignore[union-attr]
        qb = inst.qubit_b  # type: ignore[union-attr]
        param = inst.param  # type: ignore[union-attr]

        if info.num_qubits == 1:
            u_gate = single_qubit_gate_matrix(gate, param)
            # Embed 1-qubit gate into N-qubit Hilbert space
            # Qubit order: q0 is LSB (basis index = sum_k bit_k * 2^k)
            u_step = np.zeros((dim, dim), dtype=np.complex128)
            for i in range(dim):
                bit_val = (i >> qa) & 1
                for out_bit in (0, 1):
                    j = (i & ~(1 << qa)) | (out_bit << qa)
                    u_step[j, i] += u_gate[out_bit, bit_val]
            u_total = u_step @ u_total

        elif info.num_qubits == 2:
            u_step = np.zeros((dim, dim), dtype=np.complex128)
            for i in range(dim):
                bit_a = (i >> qa) & 1
                bit_b = (i >> qb) & 1

                if gate == OPCODE_CNOT:
                    out_a = bit_a
                    out_b = bit_b ^ bit_a
                    j = (i & ~(1 << qb)) | (out_b << qb)
                    u_step[j, i] = 1.0
                elif gate == OPCODE_CZ:
                    phase = -1.0 if (bit_a == 1 and bit_b == 1) else 1.0
                    u_step[i, i] = phase
                elif gate == OPCODE_SWAP:
                    j = (i & ~(1 << qa) & ~(1 << qb)) | (bit_b << qa) | (bit_a << qb)
                    u_step[j, i] = 1.0

            u_total = u_step @ u_total

    return u_total
