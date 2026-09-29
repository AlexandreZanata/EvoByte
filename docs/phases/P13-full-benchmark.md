# P13 — Full benchmark + baselines + ablations

**Status:** Proposed.
**Goal:** answer the primary question honestly, on the clock.

## Objective

Run Level-A + sampled Level-B + pinned community suites against equal-budget
baselines (random, GP, classic SR, CMA-ES where applicable, PySR + peers),
plus the 9-ablation battery from [ABLATIONS.md](../ABLATIONS.md), at
10 s / 1 min / 10 min / 1 h budgets, 5+ seeds each.

## Scope

In: suite pins, baseline adapters, ablation runner, Pareto (error vs size)
report, scaling curve (does more candidates stop helping?).
Out: real scientific data (P14), new operators.

## Tasks

1. `feat(bench): pin suites and baseline versions with hashes`.
2. `feat(bench): run main wall-clock comparison (Pareto + medians)`.
3. `test(bench): execute 9 ablations; keep-or-drop ruling per component`.
4. `docs(results): publish tables with reproduction commands`.

## Exit gate

```bash
git diff --check
python3 -m pytest tests/test_benchmarks.py -q
python3 benchmarks/full_matrix.py --budgets 10s,1m,10m,1h --seeds 5
```

Artifact: results tables + HYPOTHESIS verdict (supported/weakened per
criterion) with commit + config + seed for every cell.

## Risks

- Cherry-picking — medians + ranges required; best-only tables rejected.
- Suite leakage — pinned versions + hidden splits audited.

## Commit & Push (mandatory for this phase)

```bash
git status --short
git add benchmarks/full_matrix.py tests/test_benchmarks.py docs/BENCHMARKS.md docs/ABLATIONS.md docs/HYPOTHESIS.md docs/phases/P13-full-benchmark.md
git commit -m "feat(bench): run full wall-clock matrix and ablations"
git push -u origin phase-13-full-benchmark
gh pr create --title "feat(bench): run full wall-clock matrix and ablations" --body "P13 exit gate green. Closes #<issue>."
```
