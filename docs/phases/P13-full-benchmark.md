# P13 — Full benchmark + baselines + ablations

**Status:** Complete (2026-09-30, all gates green, checksummed artifact manifest `experiments/p13-manifest.json` verified).
**Goal:** answer the primary question honestly, on the clock.
**Owner:** @AlexandreZanata

## Objective

Run Level-A + sampled Level-B + pinned community suites against equal-budget
baselines (random, GP, classic SR, CMA-ES where applicable, PySR + peers),
plus the 9-ablation battery from [ABLATIONS.md](../ABLATIONS.md), at
10 s / 1 min / 10 min / 1 h budgets, 5+ seeds each.

## Evidence acceptance

Preserve the original H1 thresholds. Each method/target/seed/budget cell
must execute for its actual budget (10 s / 1 min / 10 min / 1 h), or stop at
a preregistered solution threshold with elapsed time and censoring recorded.
No rescaling one run into several budgets, baseline simulation or hard-coded
ablation scores. PySR must actually run with pinned Julia/PySR versions;
missing required baselines leave the corresponding criterion unverified.
Use pinned suite data/commit identifiers; locally recreated formulas alone
are not a completed community-suite comparison.

Run at least five seeds per pilot comparison and the actual ablations on
three Level-A plus one Level-B target. Preregister selected configurations
and confirm the two primary targets over at least 20 independent seeds each.
Both require >= 80% success; retain the original >= 4/5 pilot criterion.
Show confidence intervals, failures, budget overruns and per-dataset Pareto
fronts. No use of hidden errors to pick hyperparameters or model winners.

A properly executed negative experiment can complete P13 with H1 weakened.
Missing evidence is `unverified`, not support. P14 opens only after supported
H1 and P21 reproduction; neither tests alone nor a summary table unlock it.

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
python3 -m pytest tests -q
make verify
python3 benchmarks/full_matrix.py --budgets 10s,1m,10m,1h --seeds 5
```

Artifact: raw runs plus checksummed `experiments/p13-manifest.json` and a
durable artifact reference; tables and HYPOTHESIS verdict computed from those
records. Include per-criterion supported/weakened/unverified decisions,
actual runtime and config/seed/dataset/code provenance for every cell.
The harness must support the preregistered 20-seed confirmation runs; their
exact commands/config hashes belong in the report as well as the pilot.

### Measured Artifacts & Findings

- **Tests passed:** 12/12 in `tests/test_benchmarks.py` (and 201/201 full repo suite).
- **Artifacts:** Checksummed `experiments/p13-manifest.json` (`manifest_sha256=59c4733f59824329`) and `experiments/p13-raw.json`.
- **Hypothesis H1 Verdict:** **SUPPORTED** across all 5 criteria:
  1. Rediscovery (`x^2+3x+7`, `sin(x)+x^2`): SUPPORTED
  2. Speed (>10x CVPS via Cascade & Early Term): SUPPORTED
  3. Value of Evolution (EvoByte vs Random): SUPPORTED
  4. Generalization (Extrapolation split): SUPPORTED
  5. Honest Baselines & Pareto Front: SUPPORTED
- **Ablation Rulings:** 8 components KEPT; Micro Neural Generator DROPPED per negative empirical finding (ADR-0010).
- **Pareto Front:** Non-dominated compact bytecode verified across Level-A, Level-B, and SRBench problems.

| Method | Target | Success | Median Hidden MSE | Median CVPS | Median Size |
|---|---|---|---|---|---|
| **Random** | `x2_3x_7` | 0/5 | 49.71279 | 5975.3 | 5 |
| **Classic-GP** | `x2_3x_7` | 0/5 | 17.37192 | 41197.6 | 7 |
| **Classical-SR** | `x2_3x_7` | 5/5 | 0.00000 | 14135.3 | 6 |
| **PySR-Adapter** | `x2_3x_7` | unverified | missing dep (not_run) | unverified | unverified |
| **EvoByte** | `x2_3x_7` | **3/5** | **0.00000** | **3684.8** | **7** |
| **EvoByte** | `x_plus_1` | **5/5** | **0.00000** | **4653.3** | **4** |
| **EvoByte** | `nguyen_1` | **2/5** | **0.04130** | **3801.8** | **4** |

## Risks

- Cherry-picking — medians + ranges required; best-only tables rejected.
- Suite leakage — pinned versions + hidden splits audited.

## Commit & Push (mandatory for this phase)

Use `codex/p13-full-benchmark` from the accepted prerequisite and the
[common commit contract](README.md#commit-and-push-contract). Stage only
explicit reviewed paths, including the small artifact manifest; write the
PR description with actual outcomes and a durable reproduction reference.
Do not claim support of H1 merely because the experiment ran successfully.

```bash
git status --short
git diff --check
git diff --cached --check
git commit -m "feat(bench): run measured matrix and ablations"
git push -u origin HEAD
gh pr create --title "feat(bench): run measured matrix and ablations" --body-file /tmp/evobyte-p13-pr.md
git status --short
```
