# Q09 — Formula discovery from simulated observables

**Status:** Complete (2026-09-29).
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

### Empirical Artifact: Blind Scaling Rediscovery & Extrapolation Table

- **Date:** 2026-09-29
- **Environment:** x86_64, Linux 7.1.5-76070105-generic, Python 3.12.2, NumPy 2.4.6, PyTorch 2.14.0+cu130, GPU NVIDIA GeForce RTX 4060 Laptop (Driver 580.173.02)
- **Target Observable:** Ground-state energy scaling $E_0(J) = -3 J$ on $N=2$ Heisenberg XXX.
- **Dataset SHA-256 Hash:** `e6b8c49731f6c52b`
- **Domain Partitions:**
  - Training Domain: $J \in [0.50, 4.00]$ (64 points)
  - Hidden Test Domain: $J \in [0.52, 3.98]$ (64 points, interleaved holdout)
  - Extrapolation Domain: $J \in [5.00, 10.00]$ (64 points, out-of-domain)

| Seed | Gen | Eval | Time (s) | CVPS | Train MSE | Hidden MSE | Extrap MSE | Result | Discovered Expression |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| 0 | 8 | 8000 | 8.841 | 905 | 1.04e-13 | 8.55e-14 | 9.81e-13 | PASS | `SUB r7, r7, 0x00 ; CSEL r0, r1, 0x0b ; DIV r3, r5, 0x00 ; MUL r7, r7, 0x00 ; SUB r6, r2, 0x04 ; ABS r3, r4, 0x01` |
| 1 | 80 | 80000 | 102.081 | 784 | 1.14e-01 | 1.07e-01 | 3.21e+01 | FAIL | `CSEL r4, r0, 0x71 ; CSEL r3, r5, 0x18 ; ADD r0, r4, 0x03 ; SIN r6, r0, 0xba ; SUB r2, r6, 0x04 ; ADD r4, r0, 0x01 ; SUB r7, r2, 0x04` |
| 2 | 4 | 4000 | 3.767 | 1062 | 1.04e-13 | 8.55e-14 | 9.81e-13 | PASS | `SUB r7, r1, 0x00 ; POW r1, r2, 0x04 ; ADD r6, r0, 0x00 ; CSEL r1, r6, 0x03 ; COS r5, r5, 0x06 ; MUL r2, r0, 0x03 ; SUB r7, r7, 0x06` |
| 3 | 7 | 7000 | 8.092 | 865 | 1.04e-13 | 8.55e-14 | 9.81e-13 | PASS | `NEG r1, r0, 0x05 ; SUB r6, r0, 0x04 ; ADD r2, r6, 0x06 ; SUB r7, r1, 0x02 ; MUL r6, r1, 0x03 ; ADD r5, r7, 0x00 ; SIN r2, r6, 0xca` |
| 4 | 4 | 4000 | 3.698 | 1082 | 1.04e-13 | 8.55e-14 | 9.81e-13 | PASS | `SUB r2, r4, 0x00 ; ADD r7, r3, 0x01 ; ADD r5, r7, 0x00 ; POW r6, r6, 0x01 ; SUB r7, r2, 0x00 ; SUB r7, r7, 0x00` |

- **Summary:** 4/5 successes (80.0%) | Mean Hidden MSE: 2.15e-02 | Mean Extrapolation MSE: 6.43e+00
- **Exit Gate Verdict:** PASS (rate $\ge$ 3/5)

## Commit & Push (mandatory for this phase)

```bash
git status --short
git add src/evobyte/quantum/observables.py experiments/q09_observable_formula.py tests/test_quantum_formula.py docs/phases/quantum/Q09-formula-from-observables.md
git commit -m "feat(quantum): rediscover formulas from observables"
git push -u origin phase-q09-formula-from-observables
gh pr create --title "feat(quantum): rediscover formulas from observables" --body "Q09 exit gate green. Closes #<issue>."
```
