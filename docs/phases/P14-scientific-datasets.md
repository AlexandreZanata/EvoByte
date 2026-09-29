# P14 — Scientific datasets (gated entry)

**Status:** Done.
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
  until P13 verdict exists.

## Commit & Push (mandatory for this phase)

```bash
git status --short
git add benchmarks/science_matrix.py tests/test_science.py docs/phases/P14-scientific-datasets.md
git commit -m "feat(science): open gated scientific evaluation"
git push -u origin phase-14-scientific-datasets
gh pr create --title "feat(science): open gated scientific evaluation" --body "P14 exit gate green. Closes #<issue>."
```
