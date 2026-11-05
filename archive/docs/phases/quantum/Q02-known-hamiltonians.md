# Q02 — Known Hamiltonians

**Status:** Done (2026-09-29; 13/13 tests green; N=2..6 shapes/terms verified; symmetries isolated from search).
**Goal:** trusted builders for the laboratory models.

## Objective

Implement `src/evobyte/quantum/hamiltonians.py`: transverse-field Ising
(`-J Σ ZZ - h Σ X`), Heisenberg XXX (`J Σ (XX + YY + ZZ)`), J1-J2 extension,
as compact `PauliTerm` lists (coefficient + masks), open chain v0.

## Scope

In: builders + term-count tests + human decoder for logs.
Out: exact diagonalization (Q03), search, GPU.

## Tasks

1. `feat(quantum): add ising, heisenberg, j1j2 builders`.
2. `test(quantum): assert term counts and mask shapes for N = 2..6`.

## Exit gate

```bash
git diff --check
python3 -m pytest tests/test_quantum_hamiltonians.py -q
```

Artifact: builders green; known-symmetry list recorded but hidden from
search code paths (review checklist).

## Commit & Push (mandatory for this phase)

```bash
git status --short
git add src/evobyte/quantum/hamiltonians.py tests/test_quantum_hamiltonians.py docs/phases/quantum/Q02-known-hamiltonians.md
git commit -m "feat(quantum): add known hamiltonian builders"
git push -u origin phase-q02-known-hamiltonians
gh pr create --title "feat(quantum): add known hamiltonian builders" --body "Q02 exit gate green. Closes #<issue>."
```
