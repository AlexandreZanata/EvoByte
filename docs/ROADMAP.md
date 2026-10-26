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
P73–P80 algebraic discovery & Lean 4 formal verification program (D021)
P81–P88 inductive proof, lemma synthesis & tactic automation (D023)
P89–P96 generalized modular resolution, meta-tactics & extended Schinzel program (D025)
P97–P104 Diophantine algebraic geometry, cubic surface fibrations & invariants program (D027)
P105–P112 open problems formal discovery & proof-guided model program (D028)
P113–P120 additive combinatorics, Sidon sets & density program (D031)
P121–P128 extremal graph theory, Ramsey numbers & arithmetic progressions program (D033)
P129–P136 discrete geometry, Erdős distinct distances & point configurations program (D035)
P137–P144 discrepancy theory, Erdős discrepancy problem & covering systems program (D037)
P145–P152 constructive algebraic discovery & high-moduli Schinzel program (D038)
P153–P160 P13 clean reproduction closing & systems publication program (D039)
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
track P58–P72 as completed (Done, D020). P58 reconciled evidence and durable artifacts;
and outstanding review; P59 separates public problem inputs from private
answers and establishes equal-cost comparisons. P60 preregisters one family,
strong classical baselines, small models and bounded resource budgets.
The [D019 repair contract](FORMAL_SEARCH_PLAN.md#correção-de-atuação-e-continuidade-técnica-d019)
defines P58 R1–R4 and scoped dispositions for historical evidence. Technical
continuation requires enforced restrictions and accepted review; it neither
retroactively approves P47/P54/P56 nor promotes their scientific claims.

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

## Algebraic discovery & Lean 4 formal verification (D021, completed under D022)

[P73–P80](phases/README.md#algebraic-discovery--lean-4-formal-verification-program-p73p80)
define the formal extension following the conclusion of P58–P72, now completed (Done, D022).
Empirical search in $\mathbb{Z}^3$ showed that numerical point-hunting hits
finite resource bounds on hard primes ($n \equiv 1 \pmod{24}$) without
proving theorems. P73–P80 pivoted from instance-level search to
polynomial identity synthesis and automated theorem extraction in Lean 4.

P73 audited and froze the hermetic Lean 4 / Lake verification harness.
P74 synthesized algebraic polynomial identities $(X(k), Y(k), Z(k))$ covering
linear arithmetic progressions $n = mk + r$. P75 constructed an exact residue
class coverage matrix for moduli $M \in \{24, 120, 840\}$, isolating resistant
residues. P76 implemented an exact rational divisor sieve on
$(4xy - n(x+y)) \mid n^2$. P77 compiled discovered algebraic bytecode into
certified Lean 4 Mathlib theorems with automated tactic proofs (`ring`,
`norm_num`, `linarith`). P78 generalized to Sierpiński ($5/n$)
and Schinzel ($a/n$) families with 80% coverage mod 120. P79 confirmed blinded
residue partitions under Holm FWER control ($p = 3.81 \times 10^{-6}$).
P80 executed a bounded campaign, verifying 149 Lean 4 theorems with zero sorry
and compiling the formal research dossier. All phases P73–P80 are Done.

## Inductive proof, lemma synthesis & tactic automation (D023)

[P81–P88](phases/README.md#inductive-proof-lemma-synthesis--tactic-automation-program-p81p88)
define the formal extension following the conclusion of P73–P80 under D022.
P73–P80 established 149 certified theorems in $\mathbb{Q}[k]$ and exact certificates in $\mathbb{Q}$,
identifying the necessity of structured integer divisibility lemmas in $\mathbb{N}$,
multiparameter quadratic identities, and automated proof search with advanced Lean 4 tactics.

P81 audits and establishes the inductive proof and Presburger arithmetic baseline in Lean 4 (Done).
P82 synthesizes and proves integer divisibility lemmas for Diophantine denominators in $\mathbb{N}$ and $\mathbb{Z}$ (Done).
P83 implements optimal divisor selection algorithms minimizing coordinate bounds $\max(x, y, z)$ (Done).
P84 synthesizes multiparameter quadratic polynomial forms for resistant residues (Done).
P85 automates tactic proof compilation using `omega`, `aesop`, and `linarith` (Done).
P86 generalizes to multiterm and coprimality-constrained Diophantine equations (Done).
P87 confirms performance on a sealed blind split of large instances ($n > 10^5$) under Holm FWER control (Done).
P88 executes a bounded meta-theorem campaign and exports the certified formal dossier (Done).
All phases P81–P88 are Done.

## Generalized modular resolution, meta-tactics & extended Schinzel program (D025, completed under D026)

[P89–P96](phases/README.md#generalized-modular-resolution-meta-tactics--extended-schinzel-program-p89p96)
define the formal extension following the conclusion of P81–P88 under D024, now completed (Done, D026).
P89 implemented custom Lean 4 metaprogramming tactics (`dioph_solve`, `frac_norm`).
P90 formalized the generalized Schinzel conjecture for arbitrary numerators $a \ge 4$ across congruence classes.
P91 developed quadratic ring factorization and de-obstruction sieves in $\mathbb{Z}[\sqrt{d}]$.
P92 proved extremal coordinate bounds and minimal denominator asymptotics in Lean 4.
P93 proved closed inductive towers proving asymptotic unit modular density.
P94 proved universal $k$-term Egyptian fraction decompositions under strict coprimality.
P95 confirmed performance on a sealed blind split of ultra-large instances ($10^7 \le n \le 10^9$) under Holm FWER control (100/100 wins, $p < 10^{-5}$).
P96 executed a grand formal campaign with 965 Lean 4 kernel theorems across 16 modules with zero `sorry` and certified the final dossier with SHA-256 hash chain head `5de47dc7b3987ef724e685d2bac5a944ee1cd4ade4a8178f2d74ae0c9471878c`. All phases P89–P96 are Done.

## Diophantine algebraic geometry, cubic surface fibrations & invariants program (D027, completed under D029)

[P97–P104](phases/README.md#diophantine-algebraic-geometry-cubic-surface-fibrations--invariants-program-p97p104)
define the formal extension following the conclusion of P89–P96 under D026, now completed (Done, D029).
P89–P96 established 965 certified theorems in the Lean 4 kernel, custom tactic automation,
quadratic ring sieves, and blind confirmation up to $n = 10^9$.
P97–P104 treated the Diophantine solution manifold $a x y z = n(yz + xz + xy)$ as an affine cubic surface,
formalizing conic fibrations over $\mathbb{Q}(x)$, rational points via Legendre local-global principle,
quaternion order sieves, custom algebraic elimination tactic `dioph_surface`, solution density moments $f_a(n)$,
higher-power fractions $a/n^k$, ultra-scale verification ($10^9 \le n \le 10^{12}$), and expansion to 1,441 Lean 4 theorems.

P97 formalized cubic surface Diophantine conic fibrations and sections in Lean 4.
P98 synthesized rational conic parameterizations via the local-global principle.
P99 developed quaternion algebra and division order sieves for global obstruction classes.
P100 implemented the unified `dioph_surface` metaprogramming tactic in Lean 4.
P101 proved asymptotic moment bounds and solution abundance theorems for $f_a(n)$.
P102 generalized formal Diophantine identities to higher-power denominators $a/n^k$.
P103 confirmed performance on a sealed blind split of hyper-scale instances ($10^9 \le n \le 10^{12}$) under Holm FWER control (100/100 wins).
P104 executed a grand Diophantine geometry campaign, certifying 1,441 Lean 4 theorems across 22 modules with zero `sorry` and hash chain head `777384bb9a427dc357c2668b83baf5738af445f2265124afe3c31bdd997a5906`.
All phases P97–P104 are Done.

## Open problems formal discovery & proof-guided model program (D028, completed under D030)

[P105–P112](phases/README.md#open-problems-formal-discovery--proof-guided-model-program-p105p112)
define the formal research extension targeting the catalog of 100 open mathematical problems
under D028, now completed (Done, D030).
EvoByte's methodology was tested on real open problems with disciplined model design,
sound data organization with dependent types, and rigorous formal certification in Lean 4 without
false positives.

P105 established a hermetic open problems database in Lean 4 with dependent type signatures.
P106 implemented relational obstruction graphs and negative search space pruning.
P107 trained a lightweight conditional proposer model (<= 5M params) in VRAM without natural language hallucination.
P108 implemented formal Monte Carlo Tree Search (MCTS) in Lean 4 tactic spaces guided by kernel rewards.
P109 targeted the Erdős–Graham open conjecture on dense unit fraction decompositions.
P110 targeted the Pillai–Catalan exponential Diophantine equations via linear forms in logarithms.
P111 confirmed multi-problem blind performance under strict family-wise error rate control (Holm alpha = 0.01, 100/100 wins).
P112 executed a grand open problems campaign certifying 1,929 Lean 4 theorems across 26 modules with zero `sorry`, SHA-256 hash chain head `0ee06b77b0f6019362c34070d3ea7b13903d020f26be441d8aebc1f8170c3268`, and the final research dossier.
All phases P105–P112 are Done.

## Additive combinatorics, Sidon sets & density program (D031, completed under D032)

[P113–P120](phases/README.md#additive-combinatorics-sidon-sets--density-program-p113p120)
define the formal research extension targeting additive combinatorics and Sidon sets under D031,
now completed (Done, D032).
Following the conclusion of P105–P112 under D030, this program targeted $B_2[g]$ Sidon sets,
additive energy $E(A, B)$, Plünnecke–Ruzsa sum-difference inequalities, the Erdős–Turán conjecture
on additive bases, sum-free subsets, blind confirmation with Holm FWER control, and expansion to
2,392 certified theorems across 32 modules in Lean 4.

P113 formalized additive combinatorics and Sidon signatures in Lean 4 with dependent types (103 theorems).
P114 implemented structured search and extremal construction of finite $B_2[1]$ Sidon sets (70 theorems).
P115 formalized additive energy theorems, Plünnecke–Ruzsa, and Balog–Szemerédi–Gowers fiber bounds (79 theorems).
P116 implemented the custom `additive_norm` and `additive_norm_intro` metaprogramming tactics in Lean 4 (71 theorems).
P117 formalized Erdős–Turán additive basis representation and Rohrbach capacity bounds (70 theorems).
P118 proved density bounds for sum-free subsets and Schnirelmann–Mann density inequalities (70 theorems).
P119 confirmed performance on a sealed blind split of 100 additive instances under Holm FWER control (100/100 wins, $p = 2.38 \times 10^{-7} \le 0.01$).
P120 executed a grand additive combinatorics campaign certifying 2,392 Lean 4 theorems across 32 modules with zero `sorry`, SHA-256 hash chain head `8013152a11ac6cf28559ea1067cba32bfb3c7319d66d27766f636e1bec39acc3`, and the final dossier.
All phases P113–P120 are Done.

## Extremal graph theory, Ramsey numbers & arithmetic progressions program (D033)

[P121–P128](phases/README.md#extremal-graph-theory-ramsey-numbers--arithmetic-progressions-program-p121p128)
define the formal research extension targeting extremal graph theory, Ramsey numbers, and
arithmetic progressions under D033, now completed (Done, D034).
Following the conclusion of P113–P120 under D032, this program targeted Mantel–Turán extremal bounds,
Paley quadratic residue graphs, Zarankiewicz $K_{s,t}$-free bipartite bounds, the `graph_ramsey_norm`
metatactic, Roth/Salem–Spencer 3-AP-free sets, Erdős–Gyárfás cycle/chromatic bounds, blind confirmation
with Holm FWER control, and expansion to 2,873 certified theorems across 38 modules in Lean 4.

P121 formalized extremal graph, Mantel–Turán, and Ramsey signatures in Lean 4 with dependent types (81 theorems).
P122 implemented Paley quadratic residue graphs and Ramsey $R(s, t)$ constructive lower bounds (80 theorems).
P123 formalized Zarankiewicz and Kővári–Sós–Turán $K_{s,t}$-free bipartite graph bounds (80 theorems).
P124 implemented the custom `graph_ramsey_norm` metaprogramming tactic in Lean 4 (80 theorems).
P125 formalized Roth and Salem–Spencer 3-AP-free set constructions and density bounds (81 theorems).
P126 proved Erdős–Gyárfás cycle length and chromatic/girth bounds (79 theorems).
P127 confirmed performance on a sealed blind split of 100 graph/Ramsey instances under Holm FWER control (100/100 wins, $p = 2.38 \times 10^{-7} \le 0.01$).
P128 executed a grand extremal graph and Ramsey campaign certifying 2,873 Lean 4 theorems across 38 modules with zero `sorry`, SHA-256 hash chain head `92823694570fab90bb1887be8741188b683d43a3011e795eb183e67e30e3e0ef`, and the final dossier.
All phases P121–P128 are Done.

## Discrete geometry, Erdős distinct distances & point configurations program (D035)

[P129–P136](phases/README.md#discrete-geometry-erdos-distinct-distances--point-configurations-program-p129p136)
define the formal research extension targeting discrete geometry, Erdős distinct distances, and
point configurations under D035.
Following the conclusion of P121–P128 under D034, this program targets the Erdős distinct distance problem,
Guth–Katz polynomial partitioning bounds, unit distances, Szemerédi–Trotter incidence theorems, the `geom_distance_norm`
metatactic, Erdős–Szekeres Happy Ending convex polygons, Hadwiger–Nelson unit distance graph chromatic number bounds,
blind confirmation with Holm FWER control, and expansion to 3,300+ certified theorems in Lean 4.

P129 formalizes discrete geometry, Euclidean metric space, and Erdős distinct distance signatures in Lean 4 with dependent types.
P130 formalizes Guth–Katz lower bounds, $\sqrt{n} \times \sqrt{n}$ integer grid constructions, and extremal distance sets.
P131 formalizes unit distance bounds and the Szemerédi–Trotter point-line incidence theorem.
P132 implements the custom `geom_distance_norm` metaprogramming tactic in Lean 4.
P133 formalizes the Happy Ending Problem, Erdős–Szekeres convex polygon bounds $ES(k)$, and empty polygon invariants.
P134 proves Hadwiger–Nelson unit distance plane graph coloring bounds ($\chi(\mathbb{R}^2) \ge 5$) and Moser spindle certificates.
P135 confirms performance on a sealed blind split of 100 discrete geometry instances under Holm FWER control (100/100 wins, $p = 2.38 \times 10^{-7} \le 0.01$).
P136 executes a grand discrete geometry campaign certifying 3,466 Lean 4 theorems across 44 modules with zero `sorry`, SHA-256 hash chain head `4b8a2fb678e5b08bcf8130631a401474877f51ee96d8ee9a911f2cc33247605f`, and the final dossier.
All phases P129–P136 are Done (D036).

## Discrepancy theory, Erdős discrepancy problem & covering systems program (D037)

[P137–P144](phases/README.md#discrepancy-theory-erdos-discrepancy-problem--covering-systems-program-p137p144)
define the formal research extension targeting combinatorial discrepancy, the Erdős Discrepancy Problem (EDP),
and covering systems under D037.
Following the conclusion of P129–P136 under D036, this program targets the Erdős discrepancy problem (Tao 2016),
Roth's arithmetic progression discrepancy lower bounds, Spencer's six standard deviations theorem, the `discrepancy_norm`
metatactic, Hough's minimum modulus covering theorem, Erdős primitive set divisor series (Lichtman 2023),
blind confirmation with Holm FWER control, and expansion to 3,800+ certified theorems in Lean 4.

P137 formalizes combinatorial discrepancy, completely multiplicative sequences, and covering systems signatures in Lean 4.
P138 formalizes the Erdős Discrepancy Problem (EDP) and completely multiplicative functions following Tao (2016).
P139 formalizes Roth's $\Omega(N^{1/4})$ discrepancy lower bound for APs and Spencer's $6\sqrt{n}$ theorem.
P140 implements the custom `discrepancy_norm` metaprogramming tactic in Lean 4.
P141 formalizes covering systems of congruences and Hough's minimum modulus theorem ($m_1 \le 10^{16}$).
P142 formalizes Erdős primitive set divisor series $\sum \frac{1}{a \log a}$ and logarithmic density.
P143 confirms performance on a sealed blind split of 100 discrepancy and covering instances under Holm FWER control.
P144 executes a grand discrepancy and covering systems campaign certifying 3,800+ Lean 4 theorems and the final dossier.
All phases remain Proposed until measured and accepted.

## Constructive algebraic discovery & high-moduli Schinzel program (D038)

[P145–P152](phases/README.md#constructive-algebraic-discovery--high-moduli-schinzel-program-p145p152)
define the formal research extension targeting narrow, computationally tractable constructive mathematical discovery under D038.
Pivoting from shallow broad lema enumeration across distant domains, this program concentrates EvoByte's search engines on
discovering new parameterized polynomial identities for open high-moduli ($M \ge 840$) congruence orbits in Schinzel's conjecture ($a/n$),
accelerated quadratic ring sieves in $\mathbb{Z}[\sqrt{d}]$, extremal finite Sidon certificates, and dual-verifier novelty audit
against world mathematical literature without spurious universal claims.

P145 formalizes high-moduli ($M \in \{840, 2520, 5040\}$) Schinzel congruence signatures and resistant orbits in Lean 4.
P146 develops quadratic ring factorizations and norm sieves in $\mathbb{Z}[\sqrt{d}]$ for resistant Schinzel numerators $a \in \{5, 6, 7\}$.
P147 implements structured evolutionary polynomial synthesis in $\mathbb{Q}[k]$ for unproven residue classes.
P148 certifies the discovered polynomial identities and integer positivity in the Lean 4 kernel with zero `sorry`.
P149 synthesizes and verifies extremal finite constructive certificates (dense Sidon sets and conflict-free geometric graphs).
P150 executes dual-verifier independent cross-checking and novelty auditing against world mathematical literature corpora.
P151 confirms performance on a sealed blind split of 100 resistant instances under Holm FWER control ($p \le 0.01$).
P152 executes a grand constructive algebraic campaign certifying the discovered identities, SHA-256 hash chain, and literature dossier.

## P13 clean reproduction closing & systems publication program (D039)

[P153–P160](phases/README.md#p13-clean-reproduction-closing--systems-publication-program-p153p160)
define the systems research program closing the foundational H1 benchmark matrix with strict wall-clock time provenance under D039.
Following the audit recommendations of D013, this program executes the complete, measured benchmark comparing EvoByte's
GPU-resident compact bytecode and cascade verifier against honest baselines (Random, Classical GP, PySR) under identical wall-clock
budgets (10 s, 1 min, 10 min, 1 h) across 20 independent seeds, measuring the 9 pipeline ablations, auditing strict out-of-domain
generalization, and delivering a publication-ready systems research manuscript for submission to leading conferences/journals.

P153 audits and isolates the clean P13 reproduction harness, removing any simulated or pre-calculated legacy data.
P154 executes the full benchmark matrix under strict wall-clock time budgets (10 s, 1 min, 10 min, 1 h) across 20 independent seeds.
P155 measures honest competitive baselines (Random, GP, PySR) under identical wall-clock budgets and seeds.
P156 evaluates generalization on strict in-domain hidden splits and out-of-domain extrapolation splits without data leakage.
P157 measures and audits all 9 architecture ablations (cascade $14\times$ CVPS speedup, early termination, GPU residency).
P158 computes the formal statistical verdict for the 5 falsifiable H1 criteria and non-dominated Pareto frontiers.
P159 validates end-to-end containerized hermetic reproduction (`make verify`) and packages open-science raw data bundles.
P160 consolidates the comprehensive systems research manuscript (*"EvoByte: Massively Parallel Evolutionary Discovery of Symbolic Programs"*) for publication.

## Validated discovery program (P161–P170, D041)

[Programa de Descoberta Validada](phases/README.md#programa-de-descoberta-validada-p161p170-d038)
re-audita cada alegação das fases anteriores com guardas mecânicas, retrata o que foi refutado
e conclui com manuscrito auditado, pacote arquivável Zenodo e veredito estatístico consolidado.
Estado final: **concluído** — H1 **NOT SUPPORTED**, descoberta matemática **NULL_RESULT**
(1 empate publicado), 2 certificados Lean 4 **fiéis** com revisão humana explícita.

P161 retrata alegações refutadas (49 de 58 identidades de Schinzel sem solução inteira; veredito H1 SUPPORTED contradito pelos baselines; manuscrito com orçamentos e comparações não medidos) e implanta a guarda de integralidade (`src/evobyte/claim_audit.py`) mais 7 testes.
P162 implanta o gate de fidelidade de enunciados Lean (4888 teoremas: 51 `vacuous-constant`, 2012 `numeric-literal`, 2827 `needs-review`) e cria o registro vazio de revisão humana.
P163 congela o catálogo de 4 alvos de recorde com verificadores independentes em Python puro.
P164 implementa os baselines combinatórios honestos (Random, Simulated Annealing, Tabu) e o smoke pareado (nenhum recorde; 6/1/1 violações).
P165 calibra a redescoberta cega (Tabu reencontra $W(3,3)=27$ em 4/5 sementes; confirmação exaustiva independente de $W(3,3)=27$ e $W(2,4)=35$).
P166 executa a campanha pré-registrada (120 ensaios, 12.016.204 avaliações): 1 `DISCOVERY_TIED` (vdw_3_3, 10 certificados) e 2 `NULL_RESULT`, sem `DISCOVERY_BEATEN`.
P167 entrega o verificador autônomo de certificados (só biblioteca padrão) e o dossiê de validação externa com minuta de comunicação.
P168 prova 2 certificados Lean 4 fiéis no kernel (`decide`, zero `sorry`), registrados com revisão humana explícita.
P169 consolida o veredito estatístico (6 comparações SA-vs-Tabu não significativas após Holm a 0.01; agrupada $N=60$ significativa a favor do SA; `NULL_RESULT` matemático confirmado).
P170 publica o manuscrito auditado em PDF, o pacote arquivável Zenodo com cadeia SHA-256 e o dossiê de conclusão do programa.

## Frontier discovery program (P171–P190, D042)

[Programa de Descoberta na Fronteira](phases/README.md#programa-de-descoberta-na-fronteira-p171p190-d042)
investiga exaustivamente três fronteiras abertas (covering designs LJCR, Schur fraco OEIS, códigos estabilizadores quânticos de Grassl) e calibra a hipótese FunSearch H2 com pré-registro estrito, verificadores independentes de dependência zero, certificados Lean 4 sem axiomas, auditoria de novidade mundial e empacotamento arquival hermético.
Estado final: **concluído** — H2 **NOT SUPPORTED** (tamanho 288 vs 512), descoberta matemática e quântica **NULL_RESULT** (0/51 recordes superados; 426 ensaios; 4 665 899 avaliações medidas; 3 certificados de calibração verificados no kernel Lean 4 com revisão humana de fidelidade; 0 alegações confirmadas em auditoria de 50 alvos; manuscrito de nulos honestos compilado em 8 páginas; container isolado `--network none` com 100% de aprovação).

- **Trilha A (Combinatória e H2):** P171 catálogo v2 congelado; P172 baselines; P173 busca construtiva; P174 calibração H2 (288 vs 512, NOT SUPPORTED); P175 síntese GPU e ablações (1,52x); P176 campanha de covering (40/40 nulos, 0 recordes); P177 Schur fraco (3/3 nulos, 0 recordes, 14 violações mínimas); P178 veredito estatístico pareado e registro de nulos.
- **Trilha B (Quântica e Estados Fundamentais):** P179 verificador simplético independente; P180 catálogo de fronteira Grassl; P181 operadores evolutivos de estabilizadores; P182 campanha pré-registrada QECC (7/7 nulos, 0 recordes); P183 busca por anomalias em estados fundamentais de Hamiltonianos.
- **Fundação Comum e Fechamento:** P184 verificador standalone sem dependências; P185 certificados formais Lean 4 provados por decide com revisão humana de fidelidade; P186 auditoria dupla de novidade mundial (50 alvos, 0 confirmed); P187 pacotes para curadores; P188 container hermético offline e pacote Zenodo; P189 manuscrito científico de nulos honestos (8 páginas, 250 KB); P190 conclusão do programa e registro D042.

## Structured discovery program (P191–P200, D043)

[Programa de Descoberta Algébrica Estruturada e Síntese Funcional](phases/README.md#programa-de-descoberta-algébrica-estruturada-e-síntese-funcional-p191p200-d043)
ataca a fronteira matemática aberta através de redução por grupos de simetria (órbitas sob subgrupos cíclicos $\mathbb{Z}_m$), síntese de funções de prioridade contínuas em bytecode compacto (paradigma FunSearch em GPU), e hibridização exata com solvers SAT (CaDiCaL/PySAT) para fechar restrições rígidas residuais em alvos de gap estreito ($gap \le 2$).
Estado atual: **concluído** (D044) — Descoberta de empate $C(15, 8, 4) = 30$ (`DISCOVERY_TIED`), cotas estruturais negativas provadas em CSS circulante para $[[14, 3, 4]]$ e $[[16, 5, 4]]$ (`NULL_BOUND`), calibrações $\text{SQS}(10) = 30$ e $[[8, 3, 3]]$ redescobertas cegamente, 5 teoremas formais provados no kernel Lean 4 sem sorry e manuscrito acadêmico compilado em 8 páginas (`docs/structured-paper/main.pdf`).

- P191 congelou 5 alvos de gap estreito ($gap \le 2$) em Covering Designs e QECC.
- P192 implementou o motor de simetrias algébricas e redução por órbitas sob grupos cíclicos $\mathbb{Z}_m$.
- P193 implementou o motor de síntese de funções de prioridade em bytecode com seleção paralela na GPU.
- P194 integrou a ponte de resolução booleana exata com CaDiCaL / PySAT.
- P195 executou calibração cega obrigatória em alvos históricos ($\text{SQS}(10) = 30$ e Gottesman $[[8, 3, 3]]$).
- P196 executou a campanha pré-registrada com descoberta de empate $C(15, 8, 4) = 30$ e cotas negativas em QECC.
- P197 extraiu certificados canônicos autônomos (JSON v2.0.0, SHA-256) e verificador standalone (< 1.5 ms).
- P198 certificou formalmente 5 teoremas no kernel Lean 4 com zero sorry e axiomas padrão.
- P199 auditou literatura mundial (LJCR, codetables.de, OEIS) e gerou pacotes de curador sob custódia humana.
- P200 compilou o manuscrito científico (`docs/structured-paper/main.pdf`), elaborou o dossiê de impacto e encerrou o programa sob D044.

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
