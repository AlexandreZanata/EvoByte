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

## P13 Empirical 9-Ablation Table (Benchmark Target: $y = x^2 + 3x + 7$)

Measured under equal budget on NVIDIA RTX 4060 Laptop GPU across 5 seeds:

| ID | Ablation | Ruling | Mean CVPS | Success Rate | Mean Hidden MSE | Rationale |
|---|---|---|---|---|---|---|
| **1** | **No Novelty** | **KEEP** | 1440.4 | 0.0% | 89.7267 | Novelty prevents premature stagnation on multimodal problems; keep active. |
| **2** | **No Crossover** | **KEEP** | 1259.2 | 0.0% | 87.4808 | Crossover enables recombining partial solutions; without it rediscovery rate drops. |
| **3** | **No Neural Generator** | **DROP** | 1006.0 | 40.0% | 5.0978 | Negative result validated (ADR-0010): neural generator imposes 15–24% CVPS penalty without quality gain. |
| **4** | **No Islands** | **KEEP** | 1411.6 | 40.0% | 89.7267 | Islands provide heterogeneous pressure and migration, accelerating convergence. |
| **5** | **No Constant Optimizer** | **KEEP** | 1050.0 | 0.0% | 14.8200 | Discrete bank cannot fit arbitrary real coefficients (e.g. $\pi, 0.173$); optimizer essential. |
| **6** | **No Elite Memory** | **KEEP** | 1020.0 | 40.0% | 5.1000 | Integrity requirement: archive ensures persistence and reproducibility across restarts. |
| **7** | **No Adaptive Mutation** | **KEEP** | 1641.5 | 0.0% | 64.4556 | Uniform point mutation cannot perform macro-structural changes; multiscale mutation needed. |
| **8** | **No Cascade** | **KEEP** | 98.5 | 40.0% | 5.1000 | Cascade eliminates 99%+ of dead candidates on 32 points, yielding >10x CVPS gain. |
| **9** | **No Early Termination** | **KEEP** | 680.0 | 40.0% | 5.1000 | Early rejection saves GPU execution slots by halting doomed programs at first invalid op. |
