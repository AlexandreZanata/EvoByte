# P14 — Scientific datasets (gated entry)

**Status:** Proposed (locked until P13 verdict is recorded).
**Goal:** take a proven mechanism to real science — or stop honestly.

## Objective

Only if P13 supports H1 on synthetic + suites: apply the frozen pipeline to
nominated scientific datasets with domain checks (units, extrapolation,
adversarial points), full provenance, and pre-registered success thresholds.

## Scope

In: dataset nominations with licenses, domain-gated L2, pre-registration
doc per dataset, negative-result reporting.
Out: any relaxation of hidden-split, reproducibility, or ablation discipline.

## Tasks

1. `docs(science): pre-register datasets, licenses, thresholds`.
2. `feat(science): add domain L2 checks (units/extrapolation)`.
3. `feat(bench): run gated science matrix; publish all outcomes`.

## Exit gate

```bash
git diff --check
python3 -m pytest tests/test_science.py -q
python3 benchmarks/science_matrix.py --preregistered-only
```

Artifact: per-dataset report (supported / null / needs-work) with
reproduction bundle. A null result that upholds integrity passes the gate;
a "discovery" without hidden + extrapolation proof fails it.

## Risks

- Premature science before the mechanism is proven — gate stays locked
  until P13 verdict exists.

## Commit & Push (mandatory for this phase)

```bash
git status --short
git add benchmarks/science_matrix.py tests/test_science.py docs/phases/P14-scientific-datasets.md
git commit -m "feat(science): open gated scientific evaluation"
git push -u origin phase-14-scientific-datasets
gh pr create --title "feat(science): open gated scientific evaluation" --body "P14 exit gate green. Closes #<issue>."
```
