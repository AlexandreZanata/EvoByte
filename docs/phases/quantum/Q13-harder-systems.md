# Q13 — Harder / less-understood systems (gated)

**Status:** Complete (2026-09-29).
**Goal:** apply the frozen pipeline to hard regimes with scaling verifiers and mandatory negative-result reporting.

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

### Measured Artifacts (`benchmarks/qforge_hard_matrix.py --preregistered-only`)

#### Pre-Registered Hard Target Matrix

| Target ID | Model | N | Dim | Outcome | Evals | Time (s) | E_found | E_ref | Delta E | Fidelity | Verifier Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `T1_J1J2_MG_N6` | j1j2 | 6 | 64 | **SUPPORTED** | 1 | 0.0037 | -9.0000 | -9.0000 | $3.55\times 10^{-15}$ | 1.0000 | `symmetry_reduced` |
| `T2_J1J2_MG_N8` | j1j2 | 8 | 256 | **SUPPORTED** | 1 | 0.0418 | -12.0000 | -12.0000 | $7.11\times 10^{-15}$ | 1.0000 | `symmetry_reduced` |
| `T3_J1J2_MG_N10` | j1j2 | 10 | 1,024 | **SUPPORTED** | 1 | 0.2220 | -15.0000 | -15.0000 | $5.33\times 10^{-15}$ | 1.0000 | `symmetry_reduced` |
| `T4_ISING_CRIT_N8` | ising | 8 | 256 | **NULL** | 5,000 | 0.4431 | -7.4000 | -9.8380 | 2.44 | 0.1463 | `sparse_lanczos` |
| `T5_HEISENBERG_N10` | heisenberg | 10 | 1,024 | **NULL** | 6,000 | 0.9260 | -10.1964 | -17.0321 | 6.84 | 0.1266 | `symmetry_reduced` |
| `T6_UNSOLVED_FRUST_N12` | j1j2 | 12 | 4,096 | **NULL** | 1,500 | 2.1448 | -18.0000 | -19.3073 | 1.31 | 0.6390 | `symmetry_reduced` |

#### Outcome Summary
- **SUPPORTED:** 3 / 6 (Majumdar-Ghosh dimer ground states recovered exactly at $N=6, 8, 10$ with machine precision)
- **NULL:** 3 / 6 (Mandatory negative results upheld; unreached thresholds under budget correctly reported without false claims)
- **NEEDS_WORK:** 0 / 6
- **Total Wall-Clock Time:** 3.78 s
- **Exit Gate Verdict:** PASS (Integrity verified; negative and positive outcomes published)

#### Reproduction Bundles
- `[SUPPORTED]` `T1_J1J2_MG_N6`: `python3 benchmarks/qforge_hard_matrix.py --targets T1_J1J2_MG_N6 --seed 42`
- `[SUPPORTED]` `T2_J1J2_MG_N8`: `python3 benchmarks/qforge_hard_matrix.py --targets T2_J1J2_MG_N8 --seed 42`
- `[SUPPORTED]` `T3_J1J2_MG_N10`: `python3 benchmarks/qforge_hard_matrix.py --targets T3_J1J2_MG_N10 --seed 42`
- `[NULL     ]` `T4_ISING_CRIT_N8`: `python3 benchmarks/qforge_hard_matrix.py --targets T4_ISING_CRIT_N8 --seed 42`
- `[NULL     ]` `T5_HEISENBERG_N10`: `python3 benchmarks/qforge_hard_matrix.py --targets T5_HEISENBERG_N10 --seed 42`
- `[NULL     ]` `T6_UNSOLVED_FRUST_N12`: `python3 benchmarks/qforge_hard_matrix.py --targets T6_UNSOLVED_FRUST_N12 --seed 42`

## Commit & Push (mandatory for this phase)

```bash
git status --short
git add src/evobyte/quantum/scaling.py benchmarks/qforge_hard_matrix.py tests/test_quantum_scaling.py docs/phases/quantum/Q13-harder-systems.md
git commit -m "feat(quantum): open gated hard-system evaluation"
git push -u origin phase-q13-harder-systems
gh pr create --title "feat(quantum): open gated hard-system evaluation" --body "Q13 exit gate green. Closes #<issue>."
```
