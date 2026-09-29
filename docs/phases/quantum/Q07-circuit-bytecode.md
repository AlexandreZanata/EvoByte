# Q07 — Quantum circuit bytecode

**Status:** Proposed.
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

Artifact: frozen gate table; doc table matches code table.

## Commit & Push (mandatory for this phase)

```bash
git status --short
git add src/evobyte/quantum/circuit.py tests/test_quantum_circuit.py docs/quantum/REPRESENTATION.md docs/phases/quantum/Q07-circuit-bytecode.md
git commit -m "feat(quantum): freeze circuit bytecode v0"
git push -u origin phase-q07-circuit-bytecode
gh pr create --title "feat(quantum): freeze circuit bytecode v0" --body "Q07 exit gate green. Closes #<issue>."
```
