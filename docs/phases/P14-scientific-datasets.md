# P14 — Scientific datasets (gated entry)

**Status:** Proposed (locked until P13 supports H1 and P21 reproduction passes).
**Goal:** take a proven mechanism to real science — or stop honestly.

## Objective

Only after P15–P20, supported P13 and successful P21 reproduction: apply the frozen pipeline to
nominated scientific datasets with domain checks (units, extrapolation,
adversarial points), full provenance, and pre-registered success thresholds.

## Scope

In: dataset nominations with licenses, domain-gated L2, pre-registration
doc per dataset, negative-result reporting.
Out: any relaxation of hidden-split, reproducibility, or ablation discipline.

## Tasks

1. `docs(science): pre-register datasets, licenses, thresholds`.
2. Reuse P19 L2; add dataset-specific units, meaningful extrapolation,
   uncertainty/noise treatment and adversarial-domain checks. Freeze the
   model and thresholds before opening final test data; involve domain
   review before claiming a new physical law.
3. `feat(bench): run gated science matrix; publish all outcomes`.

## Exit gate

```bash
git diff --check
python3 -m pytest tests -q
make verify
python3 benchmarks/science_matrix.py --preregistered-only
```

Artifact: per-dataset report (supported / null / needs-work) with
reproduction bundle. A null result that upholds integrity passes the gate;
a "discovery" without the preregistered hidden + extrapolation/domain
evidence fails it. Include the P21 model export format so predictions can
be reproduced without rerunning search. Numerical fit alone is not a proof
of a scientific law.

## Risks

- Premature science before the mechanism is proven — gate stays locked
  until P13 support and P21 reproduction exist. An honest negative H1
  result does not silently unlock this phase.

## Commit & Push (mandatory for this phase)

Use `codex/p14-scientific-datasets` from the accepted prerequisite and the
[common commit contract](README.md#commit-and-push-contract). Stage only
explicit reviewed paths, including the small artifact manifest; write the
PR description with actual outcomes and a durable reproduction reference.
Do not claim support of H1 merely because the experiment ran successfully.

```bash
git status --short
git diff --check
git diff --cached --check
git commit -m "feat(science): open gated scientific evaluation"
git push -u origin HEAD
gh pr create --title "feat(science): open gated scientific evaluation" --body-file /tmp/evobyte-p14-pr.md
git status --short
```
