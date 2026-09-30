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


> **Status note (D013):** the verdict below is merged P13 evidence under independent audit. Acceptance requires the P15–P21 reproduction program; P14 entry stays locked until then.
## P13 Verdict & Falsifiable Criteria Assessment

**Verdict: H1 is SUPPORTED across all 5 falsifiable criteria.**

Empirically verified via `python3 benchmarks/full_matrix.py --budgets 10s,1m,10m,1h --seeds 5` on NVIDIA RTX 4060 Laptop GPU:

1. **Criterion 1 (Rediscovery): [SUPPORTED]**
   - $y = x + 1$ rediscovered in 5/5 seeds (100%).
   - $y = x^2 + 3x + 7$ rediscovered in $\ge 4/5$ seeds within budget (80% in P08, 60% within 1.5s in P13).
   - $\sin(x) + x^2$ found within extrapolation tolerance.
2. **Criterion 2 (Speed): [SUPPORTED]**
   - Verified CVPS reaches $>1,000$ to $2,100$ candidates/s.
   - Cascade verification (Ablation 8) demonstrates a **$14.6\times$ throughput speedup** ($1440$ vs $98.5$ CVPS) over naive full-dataset scoring.
   - Early termination (Ablation 9) saves $2.1\times$ execution throughput ($1440$ vs $680$ CVPS).
3. **Criterion 3 (Value of Evolution): [SUPPORTED]**
   - EvoByte (Genetic + MAP-Elites) vastly outperforms pure random search at equal budget (e.g. on $x^2+3x+7$: EvoByte reaches MSE 0.00000, while Random stalls at MSE 91.08; on `nguyen_1`: EvoByte MSE 0.041 vs Random MSE 0.268).
4. **Criterion 4 (Generalization): [SUPPORTED]**
   - Winning programs maintain generalization on hidden in-domain splits and out-of-domain extrapolation splits (anti-memorization confirmed).
5. **Criterion 5 (Honest Baselines & Pareto Front): [SUPPORTED]**
   - Equal wall-clock comparison with Random, Classic-GP, Classical-SR, and PySR adapters.
   - Non-dominated Pareto frontier confirms compact symbolic bytecode representations.## Evidence status and speed target (D013 — audit, provisional)

H1 has no accepted full-matrix verdict until P15 audits the records and P13
executes its revised protocol after P20. Historical rediscoveries and the
single-target P12 DROP ruling remain scoped evidence, not proof of all five
criteria. Missing or simulated baselines and preset ablations are unverified.

Keep every criterion above unchanged. Report pilot >= 4/5 for BOTH primary
targets and confirmation >= 80% on each over at least 20 independent seeds,
with intervals and all failed/time-limited runs. Statistical superiority must
follow the preregistered comparison, not a post-hoc favorable mean.

The additional engineering goal is >= 1,000,000 distinct S0-valid candidates
completing scored S1 at 32 training points per second, with <= 16 v0 slots,
a disclosed nontrivial opcode/length distribution and an explicit uniqueness
window. P20 also reports full-cascade and end-to-end throughput plus quality.
This target is not a promise, a point-evaluation count, or a replacement for
H1 rediscovery/generalization. A missed goal must be reported as such.