# Q08 — Circuit evolution and superoptimization

**Status:** Proposed.
**Goal:** evolve circuits; then beat a known circuit at its own game.

## Objective

Evolve circuit bytecode toward target fidelity minus gate/depth penalties;
then the superoptimizer variant: given a known circuit, find an equivalent
one with fewer gates / shallower depth / fewer two-qubit gates. Tiny-system
equivalence is exact (unitary comparison ignoring global phase); larger
systems use certified methods only.

## Scope

In: circuit operators, fidelity fitness, exact-equivalence checker (tiny N),
superoptimization experiment (Bell/GHZ preparation first).
Out: large-N equivalence heuristics without certification proof.

## Tasks

1. `feat(quantum): add circuit evolution with fidelity fitness`.
2. `feat(quantum): add exact-equivalence checker + superoptimizer run`.
3. `test(quantum): bell-state preparation rediscovered from scratch (seeded)`.

## Exit gate

```bash
git diff --check
python3 -m pytest tests/test_quantum_circuit.py -q
python3 experiments/q08_superoptimize.py --seeds 3
```

Artifact: gate-count/depth deltas with equivalence certificates.

## Commit & Push (mandatory for this phase)

```bash
git status --short
git add src/evobyte/quantum/circuit_evo.py experiments/q08_superoptimize.py tests/test_quantum_circuit.py docs/phases/quantum/Q08-circuit-evolution.md
git commit -m "feat(quantum): evolve and superoptimize circuits"
git push -u origin phase-q08-circuit-evolution
gh pr create --title "feat(quantum): evolve and superoptimize circuits" --body "Q08 exit gate green. Closes #<issue>."
```
