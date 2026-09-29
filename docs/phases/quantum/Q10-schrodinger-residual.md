# Q10 — Schrodinger residual search

**Status:** Complete (2026-09-29).
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

### Measured Artifacts (`experiments/q10_residual_search.py --seeds 3`)

#### 1. Analytic Sanity Oracle Log Across Stages
| System | Stage | Grid Points | Residual Norm | Rayleigh Energy | Norm Error | BC Error | Fidelity | Total Loss |
|---|---|---|---|---|---|---|---|---|
| QHO | FAST | 32 | $7.0374\times 10^{-3}$ | 0.497930 | $7.72\times 10^{-1}$ | $1.27\times 10^{-7}$ | N/A | $4.6061\times 10^{-2}$ |
| QHO | DENSE | 128 | $1.4596\times 10^{-5}$ | 0.500001 | $7.72\times 10^{-1}$ | $1.27\times 10^{-7}$ | N/A | $3.9039\times 10^{-2}$ |
| QHO | HIGH_PRECISION | 256 | $4.3384\times 10^{-5}$ | 0.500002 | $7.72\times 10^{-1}$ | $1.27\times 10^{-7}$ | N/A | $3.9067\times 10^{-2}$ |
| QHO | STRICT | 256 | $4.3384\times 10^{-5}$ | 0.500002 | $7.72\times 10^{-1}$ | $1.27\times 10^{-7}$ | 1.000000 | $3.9067\times 10^{-2}$ |
| Box | FAST | 32 | $4.2779\times 10^{-4}$ | 0.499572 | $5.71\times 10^{-1}$ | $4.87\times 10^{-15}$ | N/A | $2.9068\times 10^{-2}$ |
| Box | DENSE | 128 | $1.4607\times 10^{-4}$ | 0.500000 | $5.71\times 10^{-1}$ | $4.87\times 10^{-15}$ | N/A | $2.8786\times 10^{-2}$ |
| Box | HIGH_PRECISION | 256 | $5.9105\times 10^{-4}$ | 0.500000 | $5.71\times 10^{-1}$ | $4.87\times 10^{-15}$ | N/A | $2.9231\times 10^{-2}$ |
| Box | STRICT | 256 | $5.9105\times 10^{-4}$ | 0.500000 | $5.71\times 10^{-1}$ | $4.87\times 10^{-15}$ | 1.000000 | $2.9231\times 10^{-2}$ |

#### 2. Staged Rediscovery Results (3 Seeds per System)
| System | Seed | Gen | Evals | Time (s) | Residual Norm | Energy | Fidelity | Result | Discovered Expression |
|---|---|---|---|---|---|---|---|---|---|
| BOX | 0 | 4 | 1200 | 1.120 | $1.2830\times 10^{-3}$ | 0.500000 | 1.000000 | PASS | `CSEL r6, r6, 0x03 ; CSEL r3, r5, 0x0a ; SIN r2, r0, 0x06 ; CSEL r1, r2, 0x03 ; SUB r7, r6, 0x01 ; SUB r6, r1, 0x07` |
| BOX | 1 | 10 | 3000 | 3.023 | $5.9105\times 10^{-4}$ | 0.500000 | 1.000000 | PASS | `SIN r2, r0, 0x02 ; CSEL r5, r1, 0x0e ; ADD r1, r7, 0x05 ; MIN r5, r7, 0x00 ; ADD r7, r2, 0x05` |
| BOX | 2 | 1 | 300 | 0.287 | $5.9105\times 10^{-4}$ | 0.500000 | 1.000000 | PASS | `ADD r6, r5, 0x00 ; SIN r7, r0, 0x03 ; EXP r3, r7, 0x06` |
| QHO | 0 | 1 | 300 | 0.280 | $4.3384\times 10^{-5}$ | 0.500002 | 1.000000 | PASS | `MUL r1, r0, 0x00 ; CSEL r2, r6, 0x09 ; MUL r3, r1, 0x02 ; EXP r7, r3, 0x00` |
| QHO | 1 | 1 | 300 | 0.276 | $4.3384\times 10^{-5}$ | 0.500002 | 1.000000 | PASS | `MUL r1, r0, 0x00 ; CSEL r2, r6, 0x09 ; MUL r3, r1, 0x02 ; EXP r7, r3, 0x00` |
| QHO | 2 | 1 | 300 | 0.273 | $4.3384\times 10^{-5}$ | 0.500002 | 1.000000 | PASS | `MUL r1, r0, 0x00 ; CSEL r2, r6, 0x09 ; MUL r3, r1, 0x02 ; EXP r7, r3, 0x00` |

- **Success Rate:** 6/6 (100.0%)
- **Mean Residual Norm:** $4.33\times 10^{-4}$
- **Mean Fidelity:** 1.000000
- **Exit Gate Verdict:** PASS

## Commit & Push (mandatory for this phase)

```bash
git status --short
git add src/evobyte/quantum/residual.py experiments/q10_residual_search.py tests/test_quantum_residual.py docs/phases/quantum/Q10-schrodinger-residual.md
git commit -m "feat(quantum): search wavefunctions by residual"
git push -u origin phase-q10-schrodinger-residual
gh pr create --title "feat(quantum): search wavefunctions by residual" --body "Q10 exit gate green. Closes #<issue>."
```
