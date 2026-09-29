# P10 — Islands + migration

**Status:** Done.
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

### Results
- `tests/test_islands.py`: 4 passed in 2.03s.
- Full test suite: 93 passed in 4.12s (`python3 -m pytest tests/ -q`).
- `python3 experiments/p10_islands_ab.py --budget 10min --seeds 5`:
  - 4-Island Ring Migration: **60.0% (3/5)** success rate, mean time 25.9s, CVPS 2276.5.
  - Single-Population (Control): **80.0% (4/5)** success rate, mean time 20.7s, CVPS 2211.2.
  - Result: Islands accelerate escape on specific seeds (e.g. Seed 42 converged in 8.5s under Islands vs 28.9s under Single-pop), while Single-pop maintains stronger unified selection pressure.

| Condition | Success Rate | Mean Time (s) | Mean CVPS | Notes |
|---|---|---|---|---|
| **Single-Population (Control)** | 80.0% (4/5) | 20.7s | 2211.2 | Unified selection pool |
| **4-Island Ring Migration** | **60.0%** (3/5) | 25.9s | 2276.5 | Heterogeneous pressures + ring transfer |

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
