# Roadmap (phased, measurable, no false positives)

**Status:** decision. Order is binding; skipping a phase needs a
`DECISIONS.md` entry.

Each phase is one file in [phases/](phases/README.md), with objective,
scope, tasks, exit gate (executable artifact + measurement), and a
**Commit & Push** block. No phase starts with the previous exit gate red.

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
P13 full benchmark (suites + baselines + ablations, wall-clock)
P14 scientific datasets (gated entry to real science)
```

Movement rule: a phase moves Proposed -> Building when it has problem,
scope, owner, exit gate, and risks. It moves to Done only when its gate
artifact runs, is measured, is committed, and is pushed to GitHub.

The reviewed order above differs slightly from the initial sketch by moving
the hardware probe and reproducibility harness to P00 (before any bytecode
freezes) and placing batching (P06) before the archive (P07), so the first
rediscovery (P08) already runs at scale.
