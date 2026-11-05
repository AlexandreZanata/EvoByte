# EvoByte Q-Forge (experimental quantum track)

**Status:** experimental laboratory. Same doctrine as the main track, applied
to quantum mechanics and quantum information problems.

Q-Forge applies the architecture:

```text
GENERATE -> VERIFY -> SELECT -> EVOLVE -> ARCHIVE -> REPEAT
```

to problems where finding is hard and verifying is cheap. Priority stays on:
minimal binary representation, extremely fast generation, mathematically
trustworthy verification, saturated GPU, millions of candidates when
possible, no natural language in the hot path, persistent memory of the
best discoveries.

We do not want an LLM to "explain physics". We want the machine to generate
mathematical structures and let mathematics decide which survive.

Contents:

- [VISION.md](VISION.md) — principle, target problem class, scientific questions.
- [REPRESENTATION.md](REPRESENTATION.md) — binary Pauli representation, Pauli
  search engine, Hamiltonian layout, quantum circuit bytecode.
- [EXPERIMENTS.md](EXPERIMENTS.md) — experiments Q-E1..Q-E7 (conserved
  operators, ground states, circuits, superoptimization, formula discovery,
  Schrodinger residuals, Hamiltonian rediscovery, identities).
- [VERIFIER.md](VERIFIER.md) — residual-is-not-proof doctrine, quantum cascade
  verifier, exact oracle, difficulty scaling.
- [METRICS.md](METRICS.md) — QVPS, TTS, TTE, quantum ablation battery.
- [ANOMALY.md](ANOMALY.md) — Quantum Hall of Fame, discovery classes,
  Anomaly Vault, chaos quota, Infinite Monkey Quantum.
- [ROADMAP.md](ROADMAP.md) — Q0–Q13 phase order and gate into harder systems.

Executable plan: [../phases/quantum/README.md](../phases/quantum/README.md).
Reference implementation: `src/evobyte/quantum/`.
