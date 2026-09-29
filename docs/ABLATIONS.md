# Ablations

**Status:** decision.

Remove one component at a time, keep total wall-clock budget fixed, measure
delta on: CVPS, time-to-solution, quality (hidden + extrapolation),
diversity (archive coverage).

## Ablation list (P13–P14)

1. No novelty (fitness `w_n = 0`, no MAP-Elites).
2. No crossover (mutation only).
3. No neural generator (genetic vs. neural vs. neural+genetic).
4. No islands (single population, same total N).
5. No constant optimizer (bank only vs. slots + local search).
6. No elite memory (no archive/carryover across restarts).
7. No adaptive mutation (fixed rates).
8. No cascade (full-data scoring for all) — proves cascade value.
9. No early termination — proves rejection value.

Each ablation runs >= 5 seeds on >= 3 Level-A targets + 1 Level-B target.
A component stays only if it improves time-to-quality or diversity at fixed
budget, or is required for integrity (archive/resume always stay).
