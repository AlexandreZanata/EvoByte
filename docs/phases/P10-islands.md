# P10 — Islands + migration

**Status:** Proposed.
**Goal:** decide single-population vs. islands with equal total budget.

## Objective

Run 4 islands (small-size / high-mut / low-mut / high-novelty), ring
migration of top-4 every M generations, vs. single-population control at
identical total N and wall-clock.

## Scope

In: island topology, migration controller, control experiment.
Out: neural island (deferred to P12), constant fitting.

## Tasks

1. `feat(evolution): add island runner and ring migration`.
2. `test(evolution): assert migration preserves determinism per seed`.
3. `feat(bench): islands vs single-pop A/B (5 seeds, fixed budget)`.

## Exit gate

```bash
git diff --check
python3 -m pytest tests/test_islands.py -q
python3 experiments/p10_islands_ab.py --budget 10min --seeds 5
```

Artifact: A/B table (time-to-quality + diversity); winning topology frozen
or honest null result.

## Risks

- Migration storms (too frequent) — M tuned, logged, reversible.

## Commit & Push (mandatory for this phase)

```bash
git status --short
git add src/evobyte/islands.py experiments/p10_islands_ab.py tests/test_islands.py docs/EVOLUTION.md docs/phases/P10-islands.md
git commit -m "feat(evolution): add island model with migration"
git push -u origin phase-10-islands
gh pr create --title "feat(evolution): add island model with migration" --body "P10 exit gate green. Closes #<issue>."
```
