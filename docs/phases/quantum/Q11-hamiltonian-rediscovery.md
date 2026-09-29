# Q11 — Hamiltonian rediscovery

**Status:** Complete (2026-09-29).
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

### Measured Artifacts (`experiments/q11_hamiltonian_rediscovery.py --seeds 5`)

- **Target Hamiltonian:** $+1.0000\cdot X_0 X_1 + 0.5000\cdot Y_0 Y_1 + 0.8000\cdot Z_0 Z_1 + 0.4000\cdot Z_0$
- **Dataset SHA-256 Provenance:** `ef653d3366b82832c865e823df9f5cbc383d1a53f461076c7f0c265bc5d4431c`
- **Sanity Oracle MSE (True H):** $0.0000$

#### Term-Recovery Table Across 5 Seeds
| Seed | Gen | Evals | Time (s) | MSE Dyn | Precision | Recall | F1 | MAE Coeff | Result | Discovered Hamiltonian |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 11 | 880 | 16.27 | $6.98\times 10^{-8}$ | 1.00 | 1.00 | 1.00 | 0.0002 | PASS | `+0.4001*Z0 + +0.9999*X0 X1 + +0.5001*-1*Y0 Y1 + +0.7994*Z0 Z1` |
| 1 | 30 | 2400 | 55.82 | $7.43\times 10^{-8}$ | 1.00 | 1.00 | 1.00 | 0.0002 | PASS | `+0.3997*Z0 + +0.9997*X0 X1 + +0.5001*-1*Y0 Y1 + +0.7998*Z0 Z1` |
| 2 | 4 | 320 | 5.80 | $8.24\times 10^{-8}$ | 1.00 | 1.00 | 1.00 | 0.0002 | PASS | `+0.3998*Z0 + +1.0003*X0 X1 + +0.4998*-1*Y0 Y1 + +0.7999*Z0 Z1` |
| 3 | 3 | 240 | 5.25 | $1.30\times 10^{-7}$ | 1.00 | 1.00 | 1.00 | 0.0003 | PASS | `+0.4005*Z0 + +0.9996*X0 X1 + +0.5002*-1*Y0 Y1 + +0.7999*Z0 Z1` |
| 4 | 33 | 2640 | 59.16 | $8.79\times 10^{-8}$ | 1.00 | 1.00 | 1.00 | 0.0003 | PASS | `+0.3996*Z0 + +0.9998*X0 X1 + +0.4998*-1*Y0 Y1 + +0.7997*Z0 Z1` |

- **Success Rate:** 5/5 (100.0%)
- **Mean Precision:** 1.00
- **Mean Recall:** 1.00
- **Mean F1:** 1.00
- **Mean Coeff MAE:** 0.0003
- **Mean Dynamics MSE:** $8.90\times 10^{-8}$
- **Exit Gate Verdict:** PASS

## Commit & Push (mandatory for this phase)

```bash
git status --short
git add src/evobyte/quantum/hamdisc.py experiments/q11_hamiltonian_rediscovery.py tests/test_quantum_hamdisc.py docs/phases/quantum/Q11-hamiltonian-rediscovery.md
git commit -m "feat(quantum): rediscover hamiltonians from dynamics"
git push -u origin phase-q11-hamiltonian-rediscovery
gh pr create --title "feat(quantum): rediscover hamiltonians from dynamics" --body "Q11 exit gate green. Closes #<issue>."
```
