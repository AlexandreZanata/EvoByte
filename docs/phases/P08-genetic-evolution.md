# P08 — Genetic evolution + first rediscovery

**Status:** Proposed.
**Goal:** MVP gate — blind rediscovery of `y = x^2 + 3x + 7`.

## Objective

Add selection (tournament/top-K), point + block mutation, single-point
crossover, elitism (K=64), random injection >= 10%, rate controls with
logging; run the closed loop to rediscovery on Level-A target 1.

## Scope

In: operators + loop runner + first-rediscovery experiment (5 seeds).
Out: QD grid, islands, constant fitting, neural models.

## Tasks

1. `feat(evolution): add selection, mutation, crossover, elitism`.
2. `feat(evolution): add loop runner with archive + checkpoint hooks`.
3. `test(evolution): prove random-injection floor + seeded repeatability`.
4. `feat(bench): rediscover x^2+3x+7 blind (5 seeds, hidden+extrapolation)`.

## Exit gate

```bash
git diff --check
python3 -m pytest tests/ -q
python3 experiments/p08_first_rediscovery.py --seeds 5 --budget 1h
```

Artifact: rediscovery table (time, candidates, CVPS, hidden/extrapolation,
size, success rate). MVP target 1 needs >= 3/5 within 1 h.

## Risks

- Collapse to one formula — random floor + diversity metric watched.

## Commit & Push (mandatory for this phase)

```bash
git status --short
git add src/evobyte/evolution.py experiments/p08_first_rediscovery.py tests/test_evolution.py docs/MVP.md docs/phases/P08-genetic-evolution.md
git commit -m "feat(evolution): close loop and rediscover x^2+3x+7"
git push -u origin phase-08-genetic-evolution
gh pr create --title "feat(evolution): close loop and rediscover x^2+3x+7" --body "P08 exit gate green. Closes #<issue>."
```
