# Phases P00–P22 (executable plan)

One file per phase. Each phase states objective, scope (in/out),
tasks, exit gate (artifact runs + measured), risks, and a **Commit & Push**
block. Rules:

- Exactly one phase in flight. Its declared prerequisite gates must be green.
- Small diffs, reversible steps, no TODOs/stubs/placeholders.
- Gates from the phase file block commit and push — never defer a red gate.

## Index

- [P00 — Foundation, hardware probe, reproducibility harness](P00-foundation-hw-probe.md)
- [P01 — Bytecode v0 frozen](P01-bytecode-v0.md)
- [P02 — CPU reference interpreter](P02-cpu-interpreter.md)
- [P03 — Random generators](P03-random-generators.md)
- [P04 — Level-1 verifier + cascade + early stop](P04-verifier-l1.md)
- [P05 — GPU interpreter + CVPS benchmark](P05-gpu-interpreter.md)
- [P06 — Massive batching at scale](P06-massive-batching.md)
- [P07 — Elite archive + checkpoints + resume](P07-elite-archive.md)
- [P08 — Genetic evolution + first rediscovery](P08-genetic-evolution.md)
- [P09 — Quality diversity (MAP-Elites + novelty)](P09-quality-diversity.md)
- [P10 — Islands + migration](P10-islands.md)
- [P11 — Constant optimization](P11-constant-optimization.md)
- [P12 — Micro neural generator](P12-neural-generator.md)
- [P13 — Full benchmark + baselines + ablations](P13-full-benchmark.md)
- [P14 — Scientific datasets](P14-scientific-datasets.md)

Status convention per file: `Proposed | Building | Done (commit SHA + date +
measurement)`.

## Added corrective phases

- [P15 — Measurement integrity and reproducible harness](P15-measurement-integrity.md).
- [P16 — Population-parallel GPU interpreter](P16-population-gpu-vm.md).
- [P17 — GPU-resident evolutionary cycle](P17-resident-evolution.md).
- [P18 — Streaming GPU cascade and bounded memory](P18-streaming-cascade.md).
- [P19 — Strict verification and discovery evidence](P19-strict-verification.md).
- [P20 — Sustained throughput and quality experiment](P20-sustained-throughput.md).
- [P21 — Independent reproduction and usable model](P21-independent-reproduction.md).
- [P22 — Optional learning across tasks](P22-cross-task-learning.md).

## Execution and acceptance contract

```text
P12 -> P15 -> P16 -> P17 -> P18 -> P19 -> P20 -> P13 -> P21 -> P14
                                                       P21 -> P22 (optional)
```

P15 is the next task. Numbers preserve historical references; the dependency
order above, adopted in D012, replaces numeric ordering. Assign an owner
and freeze a machine-readable experiment configuration before Building.
Proposed CLI flags in new phase files are implementation acceptance
contracts; adding these documents does not implement those commands.
No new phase is complete merely because the roadmap was edited.

Common gates before every implementation commit are `git diff --check`,
`git status --short`, `python3 -m pytest tests -q` and `make verify`, plus the
phase experiment and its artifact validation. P15 must first make lint/CI
failures blocking; a suppressed failure never constitutes a green gate.
Do not run later-phase experiments to bypass a failed prerequisite.

## Commit and push contract

Before editing, check the tree is clean and create the phase's `codex/`
branch from the accepted predecessor. Use an isolated checkout when another
task owns uncommitted changes. Work on one bounded micro-task at a time.
Before the commit block, inspect and explicitly stage only reviewed files
with `git add` and explicit paths; never use blanket staging. Include the
small checksummed artifact manifest and a durable raw-artifact reference.
Do not commit large results or private data.

Write `/tmp/evobyte-pNN-pr.md` using the actual phase number, with the
problem, resulting behavior, exact validation commands, measured outcomes,
limitations and reproduction link. Run the phase's Commit & Push block and
open/update a PR against the accepted predecessor branch. All gates must
pass first; never push to main, force-push or bypass hooks. Confirm the tree
is clean afterward. Each completed micro-task has exactly one atomic commit;
mark the phase Done only after its final measured gate and push.
