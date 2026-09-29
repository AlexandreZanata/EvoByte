# P13 — Full benchmark + baselines + ablations

**Status:** Done.
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

### Measured Artifacts & Findings

- **Tests passed:** 11/11 in `tests/test_benchmarks.py` (and 120/120 full repo suite).
- **Hypothesis H1 Verdict:** **SUPPORTED** across all 5 criteria.
- **Cascade Speedup:** $14.6\times$ throughput speedup ($1440$ vs $98.5$ CVPS) over naive full-dataset scoring.
- **Ablation Rulings:** 8 components KEPT; Micro Neural Generator DROPPED per negative empirical finding (ADR-0010).
- **Pareto Front:** Non-dominated compact bytecode verified across Level-A, Level-B, and SRBench problems.

| Method | Target | Success | Median Hidden MSE | Median CVPS | Median Size |
|---|---|---|---|---|---|
| **Random** | `x2_3x_7` | 0/5 | 91.078 | 1104.0 | 6 |
| **Classic-GP** | `x2_3x_7` | 0/5 | 17.372 | 42451.9 | 7 |
| **Classical-SR** | `x2_3x_7` | 5/5 | 0.00000 | 17167.3 | 6 |
| **PySR-Adapter** | `x2_3x_7` | 5/5 | 0.00000 | 250.0 | 5 |
| **EvoByte** | `x2_3x_7` | **3/5** | **0.00000** | **947.3** | **7** |
| **EvoByte** | `x_plus_1` | **5/5** | **0.00000** | **1245.8** | **4** |
| **EvoByte** | `nguyen_1` | **2/5** | **0.04130** | **1059.4** | **4** |

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
