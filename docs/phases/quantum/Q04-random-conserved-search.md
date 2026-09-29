# Q04 — Random conserved-operator search

**Status:** Done (2026-09-29; 7/7 search tests green; pure vs structured baselines measured; QVPS ~11k-68k).
**Goal:** baselines (pure + structured) for the commutator objective.

## Objective

Seeded random search over the Pauli search engine
(`[coefficient_id, x_mask, z_mask]` x `{1,2,4}` terms) against small Ising /
Heisenberg Hamiltonians. Fitness: `commutator_error + complexity_penalty`.
Report: candidates/sec, best commutator norm, terms used, seeds.

## Scope

In: candidate codec, samplers, commutator fitness, baseline tables.
Out: selection/mutation operators (Q05), novelty, neural models.

## Tasks

1. `feat(quantum): add conserved-operator candidate codec and samplers`.
2. `test(quantum): seeded reproducibility + validity bounds`.
3. `feat(quantum): run pure-vs-structured baselines on 2–4 qubit models`.

## Exit gate

```bash
git diff --check
python3 -m pytest tests/test_quantum_search.py -q
python3 benchmarks/qforge_smoke.py --experiment conserved --seeds 3
```

Artifact: baseline table (QVPS, best norm, terms) with Hamiltonian hashes.

## Commit & Push (mandatory for this phase)

```bash
git status --short
git add src/evobyte/quantum/search.py tests/test_quantum_search.py benchmarks/qforge_smoke.py docs/phases/quantum/Q04-random-conserved-search.md
git commit -m "feat(quantum): add random conserved-operator baselines"
git push -u origin phase-q04-random-conserved-search
gh pr create --title "feat(quantum): add random conserved-operator baselines" --body "Q04 exit gate green. Closes #<issue>."
```
