# Q10 — Schrodinger residual search

**Status:** Proposed.
**Goal:** evolve wavefunctions scored by the Schrodinger residual.

## Objective

Datasets from solvable systems (harmonic oscillator, particle in a box,
two-level system, small spin chains) with hidden structure; evolve EvoByte
math programs scored by `||Hψ - Eψ|| + normalization_error +
boundary_error + complexity_penalty`, under the staged
fast -> dense -> high-precision -> strict doctrine.

## Scope

In: residual fitness, boundary/norm constraints, staged evaluation.
Out: new-physics claims (rediscovery validation only).

## Tasks

1. `feat(quantum): add schrodinger residual fitness with constraints`.
2. `test(quantum): analytic solution scores ~0 residual (sanity oracle)`.
3. `feat(quantum): staged rediscovery run on two solvable systems`.

## Exit gate

```bash
git diff --check
python3 -m pytest tests/test_quantum_residual.py -q
python3 experiments/q10_residual_search.py --seeds 3
```

Artifact: residual tables per strictness stage; analytic-sanity log.

## Commit & Push (mandatory for this phase)

```bash
git status --short
git add src/evobyte/quantum/residual.py experiments/q10_residual_search.py tests/test_quantum_residual.py docs/phases/quantum/Q10-schrodinger-residual.md
git commit -m "feat(quantum): search wavefunctions by residual"
git push -u origin phase-q10-schrodinger-residual
gh pr create --title "feat(quantum): search wavefunctions by residual" --body "Q10 exit gate green. Closes #<issue>."
```
