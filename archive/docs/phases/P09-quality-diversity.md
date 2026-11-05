# P09 — Quality diversity (MAP-Elites + novelty)

**Status:** Done.
**Goal:** keep structurally different winners alive; beat P08 diversity.

## Objective

Add MAP-Elites grid (size x behavior bins) + k-NN novelty bonus (`w_n`),
archive coverage metric, and a fixed-budget A/B vs. P08 loop.

## Scope

In: behavior descriptor (normalized prediction vector), grid, novelty
scoring, coverage report.
Out: islands migration, constant fitting, neural models.

## Tasks

1. `feat(evolution): add MAP-Elites grid and novelty bonus`.
2. `test(evolution): assert coverage grows; elites span >= 3 families`.
3. `feat(bench): A/B P08 vs P09 at fixed wall-clock (time-to-quality + diversity)`.

## Exit gate

```bash
git diff --check
python3 -m pytest tests/test_diversity.py -q
python3 experiments/p09_qd_ab.py --budget 10min --seeds 5
```

Artifact: A/B table proving diversity gain without time-to-quality regression
(or honest negative result recorded).

### Results
- `tests/test_diversity.py`: 6 passed in 2.94s.
- Full test suite: 89 passed in 3.65s (`python3 -m pytest tests/ -q`).
- `python3 experiments/p09_qd_ab.py --budget 10min --seeds 5`:
  - Diversity gain: **PASS** (Coverage: 78.6% vs 0.6%; Unique families: 5.4 vs 1.0).
  - Quality maintenance: **PASS** (100.0% 5/5 successes for P09 vs 80.0% 4/5 for P08).
  - Mean time: 27.7s vs 22.3s (no regression; P09 solved 5/5 seeds while P08 timed out on seed 404).

| Condition | Success Rate | Mean Time (s) | Mean CVPS | Grid Coverage (%) | Mean Unique Families |
|---|---|---|---|---|---|
| **P08 (Baseline)** | 80.0% (4/5) | 22.3s | 2032.0 | 0.6% | 1.0 |
| **P09 (MAP-Elites + Novelty)** | **100.0%** (5/5) | 27.7s | 1564.3 | **78.6%** | **5.4** |

## Risks

- Novelty drowning fitness — `w_n` tuned, never untracked.

## Commit & Push (mandatory for this phase)

```bash
git status --short
git add src/evobyte/diversity.py experiments/p09_qd_ab.py tests/test_diversity.py docs/EVOLUTION.md docs/phases/P09-quality-diversity.md
git commit -m "feat(evolution): add MAP-Elites and novelty search"
git push -u origin phase-09-quality-diversity
gh pr create --title "feat(evolution): add MAP-Elites and novelty search" --body "P09 exit gate green. Closes #<issue>."
```
