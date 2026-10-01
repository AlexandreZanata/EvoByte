# Q07 — Quantum circuit bytecode

**Status:** Complete (2026-09-29).
**Goal:** freeze the circuit gate table and codec.

## Objective

Implement the `[GATE, QUBIT_A, QUBIT_B, PARAM]` codec per
[REPRESENTATION.md](../../quantum/REPRESENTATION.md): frozen v0 gate table,
qubit-range validity, depth/gate-count accounting, human decoder for logs.

## Scope

In: codec + validity + cost accounting + tests.
Out: evolution, equivalence checking (Q08), parameterized fitting.

## Tasks

1. `feat(quantum): add circuit bytecode codec and v0 gate table`.
2. `test(quantum): cover validity, depth math, NOP-equivalent padding`.

## Exit gate

```bash
git diff --check
python3 -m pytest tests/test_quantum_circuit.py -q
```

### Artifact: Frozen v0 Gate Table (`CIRCUIT_BYTECODE_VERSION = 0`)

| Opcode | Name | Arity (Qubits) | Parameterized | Description |
|:---:|:---:|:---:|:---:|:---|
| 0 | `NOP` | 0 | No | No-operation (padding / identity) |
| 1 | `H` | 1 | No | Hadamard gate |
| 2 | `X` | 1 | No | Pauli-X gate |
| 3 | `Y` | 1 | No | Pauli-Y gate |
| 4 | `Z` | 1 | No | Pauli-Z gate |
| 5 | `S` | 1 | No | Phase gate ($S = Z^{1/2}$) |
| 6 | `T` | 1 | No | $\pi/8$ gate ($T = Z^{1/4}$) |
| 7 | `RX` | 1 | Yes | Rotation around X by angle `PARAM` |
| 8 | `RY` | 1 | Yes | Rotation around Y by angle `PARAM` |
| 9 | `RZ` | 1 | Yes | Rotation around Z by angle `PARAM` |
| 10 | `CNOT` | 2 | No | Controlled-NOT (control=`QUBIT_A`, target=`QUBIT_B`) |
| 11 | `CZ` | 2 | No | Controlled-Z (`QUBIT_A`, `QUBIT_B`) |
| 12 | `SWAP` | 2 | No | Swap gate (`QUBIT_A`, `QUBIT_B`) |

Document table in [REPRESENTATION.md](../../quantum/REPRESENTATION.md) matches code table in `src/evobyte/quantum/circuit.py`. Tests cover codec roundtrip, operand bounds, arity validation, critical path depth math, and NOP padding invariance.

## Commit & Push (mandatory for this phase)

```bash
git status --short
git add src/evobyte/quantum/circuit.py tests/test_quantum_circuit.py docs/quantum/REPRESENTATION.md docs/phases/quantum/Q07-circuit-bytecode.md
git commit -m "feat(quantum): freeze circuit bytecode v0"
git push -u origin phase-q07-circuit-bytecode
gh pr create --title "feat(quantum): freeze circuit bytecode v0" --body "Q07 exit gate green. Closes #<issue>."
```
