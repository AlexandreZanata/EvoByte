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
8. No cascade (full-data scoring for all) — tests cascade value.
9. No early termination — tests rejection value.

Each ablation runs >= 5 seeds on >= 3 Level-A targets + 1 Level-B target.
A component stays only if it improves time-to-quality or diversity at fixed
budget, or is required for integrity (archive/resume always stay).


> **Status note (D013):** the empirical table below is merged P13 evidence under independent audit. The corrective program that follows is the binding path to acceptance.
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

## Corrective stages after the P13–P14 ablation list (D013 — audit, provisional)

The objective remains millions of useful possibilities tested per second
on the reference hardware, with real rediscovery evidence. Stage numbering
preserves history; execute prerequisites before returning to P13/P14.

- P15 — Measurement integrity and reproducible harness.
- P16 — Population-parallel GPU interpreter.
- P17 — GPU-resident evolutionary cycle.
- P18 — Streaming GPU cascade and bounded memory.
- P19 — Strict verification and discovery evidence.
- P20 — Sustained throughput and quality experiment.
- P21 — Independent reproduction and usable model.
- P22 — Optional learning across tasks.

Execution order:

```text
P12 -> P15 -> P16 -> P17 -> P18 -> P19 -> P20 -> P13 -> P21 -> P14
                                                       P21 -> P22 (optional)
```

## Evidence rules for the resumed ablation campaign

- Use actual enabled/disabled code paths and one component difference per
  comparison. Pin target/split, seed, total population, compute resources,
  operators and budget. Freeze configurations before final hidden scoring.
- No estimated PySR values, copied historical CVPS, assumed rejection rates
  or prewritten KEEP/DROP verdicts. Label missing runs `not_run`; optional
  failures must be visible and cannot support a required H1 criterion.
- Separate MAP-Elites, novelty bonuses and islands where needed to attribute
  effects. A combined novelty/QD removal is labelled a combined experiment.
  Do not call fixed-rate mutation an adaptive baseline without a working
  adaptation mechanism. Mark that comparison not applicable until one exists.
- D010 keeps the neural generator out of the default loop. A historical P12
  result may be cited as such, not presented as a freshly executed P13 cell;
  any new neural comparison obeys the same resource and timing contract.
- Measure cascade-only versus full scoring, then early-stop on/off with the
  cascade fixed. Report false rejection of promising training candidates,
  as well as speed and actual stage kill rates.
- Integrity archives/checkpoints stay available even when elite reuse across
  restarts is disabled. Test memory reuse, not removal of research records.
- Five seeds and three Level-A plus one Level-B target are the minimum pilot.
  Freeze the chosen configuration, then use at least 20 independent seeds on
  the primary rediscovery targets for confirmation; publish success
  intervals, median/range and timeouts. Never pool different targets' errors
  into a single Pareto front or treat censored runs as successful discoveries.
- Preserve the original H1 >= 4/5 requirement for BOTH named targets;
  confirmation must also meet >= 80% success on each. Report uncertainty;
  a negative or inconclusive result is valid research, not a failed test to
  weaken. Statistical advantage needs a predeclared comparison procedure.

## Acceptance and new controlled experiments (D014, P30–P39)

P30–P32 correct corpus grouping, exact checking, certificate bounds,
checkpoint continuation and evidence acceptance before new comparisons.
See the [phase index](phases/README.md#acceptance-and-specialist-program-p30p39)
for their Proposed contracts and dependencies. Historical P24–P29 outcomes
are retained, but do not independently satisfy these corrective gates.

- P33 compares grammatical/dependency-constrained search against matched
  unrestricted/structured/genetic controls in polynomial arithmetic.
- P34 compares tracing off/on on the SAME algorithm and workload; add one
  profiled optimization at a time. Include generation, scoring, selection,
  deduplication and tracking in full-pipeline time; confirm actual durations.
- P35 certifies positive training labels and keeps failed candidates as
  labelled negatives. Source/template groups are isolated before collection.
- P36 compares distributor, joint-output, sequential and hybrid proposals
  with genetic controls, billing teacher data, fitting, inference and I/O.
  Quality and throughput must refer to the same nominated model.
- P37 changes exactly one sampling mechanism with matched grammar, live-op
  mix and resources; a probability transform alone is not quantum advantage.
- P38 freezes selection before fresh final-test scoring and uses at least
  20 seeds plus a preregistered uncertainty/comparison procedure. P39 then
  evaluates one bounded mathematical nomination with independent certificates.

Use per-target verified success and censored time-to-solution as primary
metrics. Distinct bytes, probe behavior buckets and exact mathematical
equivalence are different quantities. Extra randomness or a mean-MSE gain
without accepted solutions cannot establish a solution-rate win. Sound
nulls are publishable; integrity failures block acceptance.
