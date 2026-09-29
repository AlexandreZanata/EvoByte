# Q05 — Evolutionary conserved-operator search

**Status:** Proposed.
**Goal:** first rediscovery — a known conserved operator, found blind.

## Objective

Add selection + mask/coefficient mutation + term-level crossover on top of
Q04, with complexity penalty and novelty reward, and rediscover a known
conserved operator (e.g. Heisenberg total-`Sz`, Ising parity) on 2–6 qubits
without feeding the symmetry to the loop.

## Scope

In: operators, loop runner, archive hooks, rediscovery experiment (5 seeds).
Out: ground-state search (Q06), islands, neural models.

## Tasks

1. `feat(quantum): add evolution operators for pauli candidates`.
2. `test(quantum): random-injection floor + seeded repeatability`.
3. `feat(quantum): blind rediscovery run with hidden+generalization scoring`.

## Exit gate

```bash
git diff --check
python3 -m pytest tests/ -q
python3 experiments/q05_conserved_rediscovery.py --seeds 5
```

Artifact: rediscovery table (time, candidates, QVPS, norm, terms, success
rate ≥ 3/5).

## Commit & Push (mandatory for this phase)

```bash
git status --short
git add src/evobyte/quantum/evolution_q.py experiments/q05_conserved_rediscovery.py tests/test_quantum_search.py docs/phases/quantum/Q05-evolutionary-conserved-search.md
git commit -m "feat(quantum): evolve conserved operators to rediscovery"
git push -u origin phase-q05-evolutionary-conserved-search
gh pr create --title "feat(quantum): evolve conserved operators to rediscovery" --body "Q05 exit gate green. Closes #<issue>."
```
