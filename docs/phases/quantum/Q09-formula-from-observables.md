# Q09 — Formula discovery from simulated observables

**Status:** Proposed.
**Goal:** reuse the main symbolic-regression module on quantum data.

## Objective

Simulate observables (energy, magnetization, correlation, entanglement, gap)
over `(g, h, T, N)` grids with the Q02/Q03 stack, hide the generating
relation, and rediscover compact formulas / scaling laws with the main-track
pipeline. Known relations first; unclear regimes only after.

## Scope

In: dataset generator, hidden-relation protocol, rediscovery runs.
Out: new search machinery (reuse P08+ as-is), claims on unclear regimes.

## Tasks

1. `feat(quantum): add observable dataset generator with hashes`.
2. `feat(quantum): rediscover a known scaling relation blind (5 seeds)`.

## Exit gate

```bash
git diff --check
python3 -m pytest tests/test_quantum_formula.py -q
python3 experiments/q09_observable_formula.py --seeds 5
```

Artifact: rediscovery table with hidden + extrapolation errors.

## Commit & Push (mandatory for this phase)

```bash
git status --short
git add src/evobyte/quantum/observables.py experiments/q09_observable_formula.py tests/test_quantum_formula.py docs/phases/quantum/Q09-formula-from-observables.md
git commit -m "feat(quantum): rediscover formulas from observables"
git push -u origin phase-q09-formula-from-observables
gh pr create --title "feat(quantum): rediscover formulas from observables" --body "Q09 exit gate green. Closes #<issue>."
```
