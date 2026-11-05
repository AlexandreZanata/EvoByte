# Risks and assumptions

**Status:** living decision log input.

| # | Risk / assumption | Impact | Mitigation | Phase that retires it |
|---|---|---|---|---|
| R1 | Random search finds nothing beyond trivial targets | H1 weakened early | Level-A ladder + budget-fixed baselines | P03/P08 |
| R2 | GPU port slower than NumPy at MVP sizes | wasted complexity | PyTorch-ops-first; Triton/CUDA only with measured win | P05 |
| R3 | NaN/Inf/domain errors corrupt selection | false winners | total safe-math VM + invalid flags + conformance corpus | P02/P04 |
| R4 | Memorization mistaken for discovery | false positives | hidden + extrapolation splits; archive bars memorizers | P04/P07 |
| R5 | Population collapse (single formula) | stalls progress | random injection >= 10%, novelty, islands, MAP-Elites | P08–P10 |
| R6 | Constants dominate failures | structure search blamed unfairly | bank first, then slots + local search with budgeted cost | P11 |
| R7 | Neural generator steals VRAM for no gain | lower CVPS | VRAM cap + must-beat-genetic gate | P12 |
| R8 | Non-reproducible runs (seeds, versions) | science void | full run record + resume-equivalence test | P00/P07 |
| R9 | Benchmark leakage (solutions in training) | invalid claims | pinned suites, hidden splits, no solution training | P13 |
| R10 | Overengineering before first loop | no measurable loop | MVP-first order; each phase executable + measured | P00–P06 |

Assumptions: RTX 4060 Laptop 8 GB as reference; float32 suffices for L1;
16-op / 64-byte v0 is expressive enough for Level A. All are tested, not trusted.
