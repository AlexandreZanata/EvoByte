# Roadmap (phased, measurable, no false positives)

**Status:** decision. Order is binding; skipping a phase needs a
`DECISIONS.md` entry.

Each phase is one file in [phases/](phases/README.md), with objective,
scope, tasks, exit gate (executable artifact + measurement), and a
**Commit & Push** block. No phase starts with a declared prerequisite gate red.

```text
P00 foundation + hardware probe + reproducibility harness
P01 bytecode v0 frozen (spec + codec + validity)
P02 CPU reference interpreter (deterministic oracle + conformance)
P03 random generators (pure + structured + validity metrics)
P04 Level-1 verifier (vectorized + cascade + early stop)
P05 GPU interpreter (PyTorch ops + CVPS benchmark)
P06 massive batching (VRAM-resident cascade tuning)
P07 elite archive (Hall of Fame + checkpoints + resume)
P08 genetic evolution (selection/mutation/crossover + first rediscovery)
P09 quality diversity (MAP-Elites + novelty)
P10 islands + migration vs. single-population control
P11 constant optimization (slots + local search + least squares)
P12 micro neural generator (<= 5M params, must-beat-genetic gate)
P13 full benchmark (retained ID; blocked until P20)
P14 scientific datasets (retained ID; blocked until P13 + P21)
P15 measurement integrity + reproducible harness
P16 population-parallel GPU interpreter
P17 GPU-resident evolutionary cycle
P18 streaming cascade + measured memory + rejection audit
P19 strict float64 verification + frozen hidden evaluation
P20 sustained speed/quality experiment + million-S1 verdict
P21 clean-environment reproduction + usable learned model
P22 optional cross-task learning with fully billed cost
P23 math specialist pilot (GSM8K chains, <=5M, billed; DROP recorded)
P24 stable RTX 4060 limits with real budgets and reconciled counters
P25 leak-free math corpus (GSM8K audit + NuminaMath + symbolic tasks)
P26 reproducible tracing + exploration map
P27 quantum-inspired randomness, one falsifiable hypothesis per cycle
P28 new narrow-family specialist with its own hypothesis
P29 open problems with verifiable certificates (binding discovery criterion)
```

## Revised execution order (D012)

The phase numbers are stable identifiers, not execution order. P00–P12
remain historical milestones; their implementation is not proof that the
GPU-residency, cascade or scientific-evidence goals are already satisfied.
New corrective phases explicitly validate those gaps without rewriting old
experiment history. Execute one phase at a time in this dependency order:

```text
P12 -> P15 -> P16 -> P17 -> P18 -> P19 -> P20 -> P13 -> P21 -> P14
                                                        P21 -> P14(mathdb) -> P23 -> P22 (optional)
                                                        P23 -> P24 -> P25 -> P26 -> P27 -> P28 -> P29
```

P23 (math specialist pilot on GSM8K chains, <= 5M, billed cost) runs after
the math-DB benchmark; only a KEEP with ADR unlocks P22 confirmation.
P24–P29 consolidate the hypothesis-byte-generator program: stable GPU
limits (P24), leak-free corpus (P25), lineage + exploration map (P26),
one-falsifiable-hypothesis-per-cycle quantum-inspired sampling (P27), a new
narrow-family specialist with its own hypothesis (P28), and certified open
problems (P29). No validated novel mathematical discovery exists to date;
P29 defines the binding discovery criterion.

P15 is next. P13 completion must be re-evaluated against raw executed runs;
provisional P13 reports cannot unlock P14. P13 is a valid experiment even
if H1 is weakened, but P14 requires support of the unchanged H1 criteria
and P21 reproduction. P22 is optional and does not block scientific entry.
A missed million-S1 target remains a negative speed result, never a reason
to manufacture numbers or silently relax the workload.

The reference system is RTX 4060 Laptop (8 GB), i7-13620H and approximately
32 GB system RAM. Optimize measured software bottlenecks before considering
hardware changes. The output is a verified symbolic predictor, not a claim
of general intelligence. See [ABLATIONS.md](ABLATIONS.md) for the added
stages immediately after the P13–P14 ablation list.

Movement rule: a phase moves Proposed -> Building when it has problem,
scope, owner, exit gate, and risks. It moves to Done only when its gate
artifact runs, is measured, is committed, and is pushed to GitHub.

The original sequence put the hardware probe before bytecode freezing and
batching before the archive. D012 adds explicit corrective gates because
those earlier milestones alone do not demonstrate resident massive search.

## Quantum track (experimental, deferred expansion)

Existing quantum artifacts are preserved. New quantum development is
scheduled only after P21; Q13 still requires its own rediscovery gates.
Quantum operation throughput cannot substitute for symbolic-search CVPS.
This supersedes the earlier parallel-expansion priority (D012).

The Q-Forge laboratory retains its own phase line
([phases/quantum/](phases/quantum/README.md), Q00–Q13) and never blocks the
main track: Q0 Pauli representation -> Q1 algebra benchmark -> Q2 known
Hamiltonians -> Q3 exact oracle -> Q4 random conserved search -> Q5
evolutionary conserved search -> Q6 ground states -> Q7 circuit bytecode ->
Q8 circuit evolution/superoptimization -> Q9 observable formulas -> Q10
Schrodinger residuals -> Q11 Hamiltonian rediscovery -> Q12 vault/fame/monkey
-> Q13 harder systems (gated on consistent rediscovery). Details and gates:
[quantum/ROADMAP.md](quantum/ROADMAP.md).
