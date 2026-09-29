# Q03 — Exact-diagonalization oracle

**Status:** Proposed.
**Goal:** controlled laboratory ground truth with scoring-only discipline.

## Objective

Add the small-`N` exact oracle: Pauli-term list -> dense Hermitian ->
`eigh` -> `(E_exact, ψ_exact)`, plus `commutator_norm(H, O)` and
`energy_and_fidelity(H, ψ_candidate)`. Enforce: oracle outputs never flow
into generation/selection inputs (audit test imports only scoring paths).

## Scope

In: `oracle.py` (NumPy only), hidden-from-loop audit test, 2-qubit Ising
golden values.
Out: search, GPU, sparse/Lanczos methods (only at the scaling bottleneck).

## Tasks

1. `feat(quantum): add exact oracle with scoring-only guard`.
2. `test(quantum): golden energies for 2-qubit ising; hermiticity checks`.

## Exit gate

```bash
git diff --check
python3 -m pytest tests/test_quantum_oracle.py -q
```

Artifact: golden-value log; audit test proving no oracle leakage into
search inputs.

## Commit & Push (mandatory for this phase)

```bash
git status --short
git add src/evobyte/quantum/oracle.py tests/test_quantum_oracle.py docs/quantum/VERIFIER.md docs/phases/quantum/Q03-exact-oracle.md
git commit -m "feat(quantum): add exact-diagonalization oracle"
git push -u origin phase-q03-exact-oracle
gh pr create --title "feat(quantum): add exact-diagonalization oracle" --body "Q03 exit gate green. Closes #<issue>."
```
