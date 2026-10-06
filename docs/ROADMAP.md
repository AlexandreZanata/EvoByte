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
P30 corpus isolation by original problem and template
P31 independent answer verification + certificate bounds
P32 replay/resume + fail-closed evidence acceptance
P33 structured candidate search (polynomial arithmetic first)
P34 profiled full-pipeline throughput + bounded tracing
P35 certified program corpus for specialist training
P36 specialist learning with fully billed comparisons
P37 one controlled quantum-inspired sampling hypothesis
P38 clean-environment confirmation + frozen model export
P39 bounded mathematical campaign + novelty review
P40–P57 guided formal-search program (see executor runbook and phase index)
P58–P60 accepted base, equal-information controls and frozen workbench
P61–P70 ten isolated speculative hypotheses
P71 fresh independent confirmation with selection control
P72 one precise novelty nomination and certified campaign
```

## Execution order and acceptance review (D013, D014)

The phase numbers are stable identifiers, not execution order. P00–P12
remain historical milestones; their implementation is not proof that the
GPU-residency, cascade or scientific-evidence goals are already satisfied.
New corrective phases explicitly validate those gaps without rewriting old
experiment history. Execute one phase at a time in this dependency order:

```text
P12 -> P15 -> P16 -> P17 -> P18 -> P19 -> P20 -> P13 -> P21 -> P14
                                                        P21 -> P14(mathdb) -> P23 -> P22 (optional)
                                                        P23 -> P24 -> P25 -> P26 -> P27 -> P28 -> P29
P29 recorded outcome -> P30 -> P31 -> P32 -> P33 -> P34 -> P35 -> P36 -> P37 -> P38 -> P39
```

P23 (math specialist pilot on GSM8K chains, <= 5M, billed cost) runs after
the math-DB benchmark; only a KEEP with ADR unlocks P22 confirmation.
P24–P29 consolidate the hypothesis-byte-generator program: stable GPU
limits (P24), leak-free corpus (P25), lineage + exploration map (P26),
one-falsifiable-hypothesis-per-cycle quantum-inspired sampling (P27), a new
narrow-family specialist with its own hypothesis (P28), and certified open
problems (P29). No validated novel mathematical discovery exists to date;
P29 defines the binding discovery criterion.

P30 was the entry micro-task of D014, beginning with corpus isolation.
P24–P29 outcomes are historical inputs to the acceptance review, not proof
that all of their documented gates were enforced. P30 repairs split
boundaries, P31 repairs mathematical acceptance and P32 establishes the
clean baseline before new search/model comparisons. Preserve old artifacts;
map unsupported claims to provisional/superseded records rather than
rewriting measurements. P13 completion must be re-evaluated against actual
executed runs; provisional reports cannot unlock P14. P13 is a valid
experiment even if H1 is rejected, but P14 requires the unchanged H1 criteria
and P21 reproduction. P22 is optional and does not block scientific entry.
A missed million-S1 target remains a negative speed result, never a reason
to manufacture numbers or silently relax the workload.

P33–P37 use development tasks only. P30's fresh final test is opened for
authorized frozen scoring in P38, with an access log and no subsequent
tuning. P36 KEEP needs a scoped ADR; neither a pilot gain nor a same-family
confirmation automatically unlocks P22 cross-family claims. P39 evaluates
one bounded nomination with exact independent certificates and novelty
review; no unbounded conjecture is proved by a finite successful search.

The full P30–P39 scope and executable acceptance contracts are indexed in
[phases/README.md](phases/README.md#acceptance-and-specialist-program-p30p39).
These files are Proposed; their new CLI flags are implementation contracts,
not existing commands or completed experiments.

The reference system is RTX 4060 Laptop (8 GB), i7-13620H and approximately
32 GB system RAM. Optimize measured software bottlenecks before considering
hardware changes. The output is a verified symbolic predictor, not a claim
of general intelligence. See [ABLATIONS.md](ABLATIONS.md) for the added
stages immediately after the P13–P14 ablation list.

Movement rule: a phase moves Proposed -> Building when it has problem,
scope, owner, exit gate, and risks. It moves to Done only when its gate
artifact runs, is measured, is committed, and is pushed to GitHub.

The original sequence put the hardware probe before bytecode freezing and
batching before the archive. D013 adds explicit corrective gates because
those earlier milestones alone do not demonstrate resident massive search.

## Guided search extension (D017)

[The executor runbook](FORMAL_SEARCH_PLAN.md) and
[P40–P57 contracts](phases/README.md#guided-formal-search-program-p40p57)
define the next proposed program. First audit and reconcile P33–P39
evidence (P40); repair artifact isolation, exact checking, real resume,
GPU residency and actual full-pipeline timing (P41–P45). Then curate 100
open problems without claiming to have formalized or searched all of them.

Freeze one development family, formal-checker boundary, compact candidates,
honest controls and bounded replay. Train one small conditional proposer
only with sufficient certified data. Compare fully billed costs and keep
the classical baseline if learning or sampling loses. Final scoring uses
a fresh sealed test and an unchanged accepted implementation. End with one
bounded campaign and human novelty review, not a universal theorem claim
based on tested instances.

P40 was the entry of D017. P40–P57 outcomes now exist in their phase files;
their recorded human-review pendencies and provisional evidence are not
waived by Done labels. No historical H1, P14 or cross-family claim is unlocked.
The existing quantum roadmap is preserved.

## Speculative hypotheses extension (D018)

[P58–P72](phases/README.md#speculative-hypothesis-program-p58p72) and
[the updated executor contract](FORMAL_SEARCH_PLAN.md#programa-especulativo-p58p72)
are Proposed. P58 is next: reconcile dirty-run evidence, durable artifacts
and outstanding review; P59 separates public problem inputs from private
answers and establishes equal-cost comparisons. P60 preregisters one family,
strong classical baselines, small models and bounded resource budgets.

P61–P70 test modular shadows, error repair, verifier feedback, learned
obstructions, backward constructions, composite jumps, verified macros,
adversarial conjectures, residue-guided islands and parametric proof search.
Each tests one mechanism; null results are retained and modules are not
automatically stacked. P71 confirms at most two selected methods on fresh
groups with independent review and selection/multiple-comparison control.
P72 nominates one precise mathematical result and reviews correctness,
novelty and reproduction. No universal claim follows from finite testing.

Adding these files executes no new experiment and establishes no worldwide
novelty, quantum advantage or solved open problem. Existing results remain
unchanged; integrity failures block advancement, not honest negative findings.

## Quantum track (experimental, deferred expansion)

Existing quantum artifacts are preserved. New quantum development is
scheduled only after P21; Q13 still requires its own rediscovery gates.
Quantum operation throughput cannot substitute for symbolic-search CVPS.
This supersedes the earlier parallel-expansion priority (D013).

The integration audit (D015) keeps Q10–Q13 scientific acceptance provisional:
QHO and dimer runs use known initial solutions, Q12's `micro_model` is a
hand-written motif sampler, and Q13 consults reference energy for stopping.
Q11's reported population counter omits local refinement. Corrected software
and green CI do not establish a new law, learned-model superiority, exact
symbolic proof or prospective registration. P32 records these distinctions;
independent verification and controlled unseeded arms are required before
accepting new quantum discovery claims. See the corrections in the phase files.

The Q-Forge laboratory retains its own phase line
([phases/quantum/](phases/quantum/README.md), Q00–Q13) and never blocks the
main track: Q0 Pauli representation -> Q1 algebra benchmark -> Q2 known
Hamiltonians -> Q3 exact oracle -> Q4 random conserved search -> Q5
evolutionary conserved search -> Q6 ground states -> Q7 circuit bytecode ->
Q8 circuit evolution/superoptimization -> Q9 observable formulas -> Q10
Schrodinger residuals -> Q11 Hamiltonian rediscovery -> Q12 vault/fame/monkey
-> Q13 harder systems (gated on consistent rediscovery). Details and gates:
[quantum/ROADMAP.md](quantum/ROADMAP.md).
