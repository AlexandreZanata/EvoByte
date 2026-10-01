# Quantum binary representation

**Status:** decision (experimental track, v0).

## Pauli strings as bits (never strings in the hot path)

Never represent `X0 Z1 Y2` as text. For `N` qubits use two bitmasks:

```text
X_MASK, Z_MASK  (N bits each)
I = 00, X = 10, Z = 01, Y = 11   (per-qubit (x, z) bits)
```

Example (conceptual): `x_mask = 00100101`, `z_mask = 00001101`, plus a
coefficient and a phase. A Pauli operator over up to 64 qubits fits in two
`uint64` masks. This is the binary symplectic representation of the Pauli
group, and v0 uses it because multiplication, commutation, anticommutation,
and equivalence reduce overwhelmingly to:

```text
XOR, AND, POPCOUNT, PARITY, BIT SHIFT
```

Dense matrices are forbidden wherever this cheaper equivalent exists; they
appear only in the exact oracle (small `N`) and Level-2 strict checks.

## Symplectic rules (binding)

- Product: `(x1, z1) * (x2, z2) = phase * (x1^x2, z1^z2)`, phase tracked in
  Z4 (`1, i, -1, -i`) via the symplectic form `z1·x2 (mod 2)`.
- Commutation: `P1, P2` commute iff
  `popcount(x1 & z2) + popcount(z1 & x2)` is **even** (symplectic inner
  product zero); otherwise they anticommute.
- Single-Pauli phase convention: `I, X, Z` carry phase `1`; `Y` carries `i`
  (since `Y = iXZ`).

## Pauli search engine (v0)

Generate millions of operators of the form:

```text
O = c1*P1 + c2*P2 + ... + cn*Pn
```

Candidate layout (fixed maximum size; `n` in `{1, 2, 4, 8, 16}`):

```text
[coefficient_id, x_mask, z_mask]
[coefficient_id, x_mask, z_mask]
...
```

Coefficients come from the same quantized-bank doctrine as the main track
(see `docs/CONSTANTS.md`): structure search first, coefficient fitting only
on promoted candidates with budgeted cost. Goal: discover operators with
target properties (commutation, low energy, target fidelity).

## Hamiltonian layout (compact, mutable)

```text
struct PauliTerm { coefficient; x_mask; z_mask; }
Hamiltonian: PauliTerm[N]
```

This permits mutating terms, adding/removing terms, swapping operators, and
retuning coefficients with zero symbolic parsing.

## Quantum circuit bytecode (Q07+)

Fixed-width instructions, never QASM text in the hot path:

```text
[GATE, QUBIT_A, QUBIT_B, PARAM]
[GATE, QUBIT_A, QUBIT_B, PARAM]
...
```

### Frozen v0 Gate Table (`CIRCUIT_BYTECODE_VERSION = 0`)

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

Parameterized gates reference the quantized angle bank (`ANGLE_BANK`);
free-angle fitting follows the constants ladder (P11 doctrine) on promoted circuits only.

## Alternatives considered

- Dense-matrix candidates — rejected in L1 (exponential memory, kills
  throughput); kept only in the exact oracle.
- QASM/string IR — rejected (parse cost per candidate).
- Statevector candidates for large `N` — deferred until sparse/Lanczos/
  tensor-network verifiers exist (see VERIFIER.md scaling ladder).
