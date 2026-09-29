# Q13 — Harder / less-understood systems (gated)

**Status:** Proposed and **locked** until Q04–Q11 show consistent rediscovery
of known results (recorded verdict, not aspiration).

## Objective

Apply the frozen Q-Forge pipeline to harder or less-understood regimes
(larger `N` at the exact-verification bottleneck with sparse/Lanczos/
symmetry-reduction/tensor-network verifiers; J1-J2 and beyond; pre-registered
thresholds), with full provenance and mandatory negative-result reporting.

## Scope

In: scaling verifiers (only now), pre-registered hard targets, full reports.
Out: any relaxation of oracle discipline, splits, or labeling rules.

## Tasks

1. `docs(quantum): pre-register hard targets, thresholds, verifier ladder`.
2. `feat(quantum): add bottleneck verifier (measured need only)`.
3. `feat(quantum): run gated hard-system matrix; publish all outcomes`.

## Exit gate

```bash
git diff --check
python3 -m pytest tests/test_quantum_scaling.py -q
python3 benchmarks/qforge_hard_matrix.py --preregistered-only
```

Artifact: per-target report (supported / null / needs-work) with
reproduction bundles. A null result upholding integrity passes; an
unproven "discovery" fails.

## Commit & Push (mandatory for this phase)

```bash
git status --short
git add src/evobyte/quantum/scaling.py benchmarks/qforge_hard_matrix.py tests/test_quantum_scaling.py docs/phases/quantum/Q13-harder-systems.md
git commit -m "feat(quantum): open gated hard-system evaluation"
git push -u origin phase-q13-harder-systems
gh pr create --title "feat(quantum): open gated hard-system evaluation" --body "Q13 exit gate green. Closes #<issue>."
```
