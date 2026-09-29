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

## Corrective stages after the P13–P14 ablation list (D012)

The objective remains millions of useful possibilities tested per second
on the reference hardware, with real rediscovery evidence. Stage numbering
preserves history; execute prerequisites before returning to P13/P14.

- [P15 — Measurement integrity and reproducible harness](phases/P15-measurement-integrity.md).
- [P16 — Population-parallel GPU interpreter](phases/P16-population-gpu-vm.md).
- [P17 — GPU-resident evolutionary cycle](phases/P17-resident-evolution.md).
- [P18 — Streaming GPU cascade and bounded memory](phases/P18-streaming-cascade.md).
- [P19 — Strict verification and discovery evidence](phases/P19-strict-verification.md).
- [P20 — Sustained throughput and quality experiment](phases/P20-sustained-throughput.md).
- [P21 — Independent reproduction and usable model](phases/P21-independent-reproduction.md).
- [P22 — Optional learning across tasks](phases/P22-cross-task-learning.md).

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
