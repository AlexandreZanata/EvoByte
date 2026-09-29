# Q11 — Hamiltonian rediscovery

**Status:** Proposed (later; needs Q02–Q05 green).
**Goal:** recover a hidden Hamiltonian from its dynamics.

## Objective

Generate datasets (initial states + time evolution + measured observables)
from a hidden artificial Hamiltonian (e.g. `a·XX + b·YY + c·ZZ + h·Z`);
evolve `H_candidate` in the compact `PauliTerm` layout scored by
predicted-vs-observed dynamics error; report structural recovery.

## Scope

In: dynamics simulator for data generation, dynamics-matching fitness,
recovery experiment.
Out: real-device data, open-system dynamics.

## Tasks

1. `feat(quantum): add dynamics dataset generator + matching fitness`.
2. `test(quantum): true hamiltonian scores ~0 dynamics error (sanity)`.
3. `feat(quantum): blind structural-recovery run (5 seeds)`.

## Exit gate

```bash
git diff --check
python3 -m pytest tests/test_quantum_hamdisc.py -q
python3 experiments/q11_hamiltonian_rediscovery.py --seeds 5
```

Artifact: term-recovery table (precision/recall on Pauli terms + coefficients).

## Commit & Push (mandatory for this phase)

```bash
git status --short
git add src/evobyte/quantum/hamdisc.py experiments/q11_hamiltonian_rediscovery.py tests/test_quantum_hamdisc.py docs/phases/quantum/Q11-hamiltonian-rediscovery.md
git commit -m "feat(quantum): rediscover hamiltonians from dynamics"
git push -u origin phase-q11-hamiltonian-rediscovery
gh pr create --title "feat(quantum): rediscover hamiltonians from dynamics" --body "Q11 exit gate green. Closes #<issue>."
```
