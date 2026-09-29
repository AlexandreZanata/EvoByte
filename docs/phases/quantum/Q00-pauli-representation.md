# Q00 — Pauli bit representation

**Status:** Done (2026-09-29; 10/10 unit tests green, 64-qubit width and edge table verified).
**Goal:** symplectic codec no later phase can silently break.

## Objective

Implement `src/evobyte/quantum/pauli.py` per
[REPRESENTATION.md](../../quantum/REPRESENTATION.md): `(x_mask, z_mask)` ops,
Z4 phase tracking, `multiply`, `commutes_with` (even-parity rule),
single-Pauli constructors, human decoder for logs only.

## Scope

In: codec + algebra + unit tests (product table, commutation parity,
`Y = iXZ` phase, 64-qubit mask width).
Out: matrices, Hamiltonians, search, GPU.

## Tasks

1. `feat(quantum): add symplectic pauli codec and algebra`.
2. `test(quantum): cover multiply/commute/parity/phase edge table`.

## Exit gate

```bash
git diff --check
python3 -m pytest tests/test_quantum_pauli.py -q
```

Artifact: algebra tests green; doc rules match code rules (review checklist).

## Commit & Push (mandatory for this phase)

```bash
git status --short
git add src/evobyte/quantum/pauli.py tests/test_quantum_pauli.py docs/quantum/REPRESENTATION.md docs/phases/quantum/Q00-pauli-representation.md
git commit -m "feat(quantum): add symplectic pauli codec and algebra"
git push -u origin phase-q00-pauli-representation
gh pr create --title "feat(quantum): add symplectic pauli codec and algebra" --body "Q00 exit gate green. Closes #<issue>."
```
