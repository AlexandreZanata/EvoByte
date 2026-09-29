# P09 — Quality diversity (MAP-Elites + novelty)

**Status:** Proposed.
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
