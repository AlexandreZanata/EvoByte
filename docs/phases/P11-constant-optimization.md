# P11 — Constant optimization

**Status:** Done.
**Goal:** separate structure search from coefficient fitting — with budget honesty.

## Objective

Add constant slots (<= 4 tunable per program) + hill-climb local search on
promoted candidates only, then least-squares for linear heads. Fitting cost
counts against the method.

## Scope

In: `constants.py`, S3/L2-only fitting hooks, absurd-constant penalties.
Out: full-gradient training, symbolic solvers in L1.

## Tasks

1. `feat(constants): add tunable slots with bank fallback`.
2. `feat(constants): add local search + linear least squares (S3/L2 only)`.
3. `feat(bench): bank-only vs fitted A/B on constant-heavy targets`.

## Exit gate

```bash
git diff --check
python3 -m pytest tests/test_constants.py -q
python3 experiments/p11_constants_ab.py --seeds 5
```

Artifact: A/B table (targets with `pi`, `0.173`-style constants) proving
fitted path wins per wall-clock second including fit cost.

| Target | Cond A MSE | Cond B MSE | MSE Gain | Time A | Time B (Billed) | Winner |
|---|---|---|---|---|---|---|
| `y = 3.14159 x^2 + 0.173 x` | 1.71072 | 0.09264 | 18.5x | 6.91s | 7.40s | Cond B |
| `y = 3.14159 x + 0.173` | 0.06481 | 0.00000 | >10000x | 5.44s | 5.71s | Cond B |

## Risks

- Fit cost hidden — harness bills optimizer steps explicitly.

## Commit & Push (mandatory for this phase)

```bash
git status --short
git add src/evobyte/constants.py experiments/p11_constants_ab.py tests/test_constants.py docs/CONSTANTS.md docs/phases/P11-constant-optimization.md
git commit -m "feat(constants): add slots with budgeted local search"
git push -u origin phase-11-constant-optimization
gh pr create --title "feat(constants): add slots with budgeted local search" --body "P11 exit gate green. Closes #<issue>."
```
