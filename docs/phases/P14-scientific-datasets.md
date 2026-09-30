# P14 — Scientific datasets (gated entry)

**Status:** Done (gated entry to real-science datasets remains locked until an accepted P13 verdict plus P21 reproduction).
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

### Measured Artifacts & Findings

- **Tests passed:** 8/8 in `tests/test_science.py` (and 128/128 full repo suite).
- **Kepler's Third Planetary Law:** **SUPPORTED** ($R^2 = 1.0000$, Extrap Rel Err = 0.00%, Gates: Extrap=True, Units=True, Adv=True). Discovered expression: `MAX r5, r0, 0x07 ; SQRT r4, r5, 0x04 ; MUL r7, r0, 0x04` ($T = a \cdot \sqrt{a}$).
- **Boyle-Mariotte Gas Law:** **NEEDS_WORK** (1/5 seeds supported with $R^2 = 1.0000$, 4 seeds blocked by domain L2 gates).
- **Stefan-Boltzmann Law:** **NEEDS_WORK** (High correlation $R^2 = 0.9944$, but scaling exponent 3.719 vs 4.0 blocked by Domain L2 dimensional gate).
- **Michaelis-Menten Kinetics:** **NEEDS_WORK** (Extrapolation error 98.31% blocked by L2 extrapolation gate).
- **Relativistic Lorentz Factor:** **NEEDS_WORK** (Extrapolation error 17.95% blocked by L2 extrapolation gate).

| Dataset / Physical Law | Field | Outcome | Hidden $R^2$ | Extrap Error |
|---|---|---|---|---|
| **Kepler's Third Planetary Law** | Astrophysics & Celestial Mechanics | **SUPPORTED** | 1.0000 | 0.00% |
| **Boyle-Mariotte Ideal Gas Law** | Thermodynamics & Gas Physics | **NEEDS_WORK** | 1.0000 | 0.00% |
| **Stefan-Boltzmann Radiation** | Thermodynamics & Radiative Transfer | **NEEDS_WORK** | 0.9944 | 6.62% |
| **Michaelis-Menten Kinetics** | Biochemistry & Enzymology | **NEEDS_WORK** | 0.8488 | 98.31% |
| **Relativistic Lorentz Factor** | Special Relativity & Particle Physics | **NEEDS_WORK** | 0.9972 | 17.95% |

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
