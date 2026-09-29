# P13 — Full benchmark + baselines + ablations

**Status:** Proposed (requires P15–P20; provisional results need evidence audit).
**Goal:** answer the primary question honestly, on the clock.

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
