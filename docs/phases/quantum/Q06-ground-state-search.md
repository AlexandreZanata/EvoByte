# Q06 — Ground-state candidate search

**Status:** Proposed.
**Goal:** approximate `E_exact` by energy fitness alone.

## Objective

Evolve compact ansatze (bitmask-defined trial states / shallow circuits /
parametric amplitudes) scored by `E(ψ)` only; report `E_candidate - E_exact`
and fidelity post-hoc (never for selection) on 2–8 qubit Ising/Heisenberg.

## Scope

In: ansatz codec, energy fitness, fidelity scorer, small-N experiment.
Out: circuit bytecode table (Q07), large-`N` methods.

## Tasks

1. `feat(quantum): add ground-state ansatz codec and energy fitness`.
2. `test(quantum): energy of known eigenstate equals E_exact within tolerance`.
3. `feat(quantum): evolution run with TTS/TTE report`.

## Exit gate

```bash
git diff --check
python3 -m pytest tests/test_quantum_ground.py -q
python3 experiments/q06_ground_state.py --seeds 5
```

Artifact: TTS/TTE table with oracle provenance per cell.

## Commit & Push (mandatory for this phase)

```bash
git status --short
git add src/evobyte/quantum/ground.py experiments/q06_ground_state.py tests/test_quantum_ground.py docs/phases/quantum/Q06-ground-state-search.md
git commit -m "feat(quantum): search ground states by energy fitness"
git push -u origin phase-q06-ground-state-search
gh pr create --title "feat(quantum): search ground states by energy fitness" --body "Q06 exit gate green. Closes #<issue>."
```
