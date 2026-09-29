# Hypothesis and success criteria

**Status:** principle.

## Primary question

> In problems where candidates verify extremely fast, can massively parallel
> stochastic search with autoevolution match or beat more sophisticated
> methods per unit of compute time?

## Falsifiable criteria

H1 is **supported** if, under equal wall-clock budgets (10 s / 1 min /
10 min / 1 h) on reference hardware, EvoByte on Level-A + sampled Level-B
targets shows:

1. **Rediscovery:** `y = x^2 + 3x + 7` and `sin(x) + x^2` re-found (symbolic
   equivalence or hidden + extrapolation error within tolerance) in >= 4/5
   seeds within 1 h on 8 GB VRAM.
2. **Speed:** CVPS measured and reported with full provenance; cascade +
   early termination demonstrably raise verified throughput vs. naive
   full-data scoring (ablation 8–9).
3. **Value of evolution:** genetic + QD beats pure random at fixed budget
   (time-to-quality), or H1's evolution claim is rejected and recorded.
4. **Generalization:** winners beat memorizers on hidden + extrapolation;
   no Hall of Fame entry without both.
5. **Honest baselines:** equal-budget comparison vs. random/GP/PySR-class
   methods with pinned versions; Pareto (error vs. size) reported.

H1 is **weakened** if (a) only trivial targets (`x+1`, `x^2`) are found,
(b) evolution adds nothing over random at fixed budget, or (c) a micro
generator cannot beat genetic search per wall-clock second.

## Research questions the project must be able to answer

- How much faster is bytecode than text representations? (measured, P05)
- How many candidates/sec verified? (CVPS, P05–P06)
- Does pure random achieve anything? (P03 baseline)
- How much do evolution / novelty / islands / constants help? (ablations)
- How many candidates before a known formula is found? (P08/P13)
- Does a micro-generator help, and at what size tradeoff? (P12 gate)
- Does more candidates stop helping? (scaling curve, P13)
- Can it beat traditional methods at equal wall-clock? (P13 main experiment)

No claim passes without 5+ seeds, hidden + extrapolation numbers, and a
reproduction command.
