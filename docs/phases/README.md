# Phases P00–P14 (executable plan)

One file per phase. Each phase states objective, scope (in/out),
tasks, exit gate (artifact runs + measured), risks, and a **Commit & Push**
block. Rules:

- Exactly one phase in flight. Previous exit gate must be green.
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
