# P08 — Genetic evolution + first rediscovery

**Status:** Done.
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

### Results
- `tests/test_evolution.py`: 17 passed in 1.40s.
- Full test suite: 83 passed in 2.91s (`python3 -m pytest tests/ -q`).
- `python3 experiments/p08_first_rediscovery.py --seeds 5 --budget 1h`:
  - Success rate: **4/5 (80.0%)** (Gate requirement: >= 3/5).
  - Total benchmark time: ~117 s (well under 1 h budget).
  - Average CVPS: ~2,100 candidates/s.

| Seed | Status | Gen | Time (s) | Candidates | CVPS | Train MSE | Hidden MSE | Extrap MSE | Size | Expression |
|---|---|---|---|---|---|---|---|---|---|---|
| 42 | **SUCCESS** | 61 | 40.8 | 61000 | 1496.2 | 7.60e-13 | 7.50e-13 | 3.23e-11 | 8 | `POW r1, r5, 0x05 ; SUB r1, r2, 0x00 ; MUL ...` |
| 101 | **SUCCESS** | 17 | 8.1 | 17000 | 2108.9 | 1.50e-12 | 1.78e-12 | 5.02e-11 | 8 | `MUL r3, r2, 0x00 ; CSEL r1, r6, 0x03 ; SUB ...` |
| 202 | **SUCCESS** | 34 | 14.2 | 34000 | 2401.1 | 5.97e-13 | 4.83e-13 | 4.68e-11 | 6 | `CSEL r7, r0, 0x8a ; ADD r4, r7, 0x03 ; CSEL ...` |
| 303 | **SUCCESS** | 16 | 6.7 | 16000 | 2404.5 | 4.97e-13 | 4.90e-13 | 3.05e-11 | 7 | `MUL r4, r0, 0x00 ; ADD r2, r0, 0x01 ; CSEL ...` |
| 404 | FAIL | 100 | 47.3 | 100000 | 2115.8 | 2.02e+00 | 2.01e+00 | 6.59e-01 | 6 | `CSEL r0, r0, 0x08 ; CSEL r0, r0, 0x09 ; ...` |

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
