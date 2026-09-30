# EvoByte documentation

This folder is the research source of truth. Documents distinguish:

- **Principle:** durable commitment, changed only with strong public justification.
- **Decision:** adopted rule for the current version, revisable with a record.
- **Hypothesis:** assumption that must be validated by measurement.
- **Open question:** not yet decided.

Precedence on conflict:

1. [VISION.md](VISION.md);
2. [ARCHITECTURE.md](ARCHITECTURE.md);
3. the topic-specific document;
4. [ROADMAP.md](ROADMAP.md);
5. historical materials.

Newcomers start at the root [README.md](../README.md), then:

## Research direction

- [VISION.md](VISION.md) — hypothesis, non-goals, hot-path philosophy.
- [HYPOTHESIS.md](HYPOTHESIS.md) — falsifiable success criteria.
- [MVP.md](MVP.md) — minimal scope and exit thresholds.
- [ROADMAP.md](ROADMAP.md) — validated phase sequence.
- [phases/](phases/README.md) — one executable file per phase (P00–P22; dependency order in ROADMAP.md).

## Quantum track (experimental)

- [quantum/](quantum/README.md) — Q-Forge laboratory index.
- [quantum/VISION.md](quantum/VISION.md) — target problem class and questions.
- [quantum/REPRESENTATION.md](quantum/REPRESENTATION.md) — Pauli bits, search
  engine, Hamiltonian layout, circuit bytecode.
- [quantum/EXPERIMENTS.md](quantum/EXPERIMENTS.md) — experiments Q-E1..Q-E7.
- [quantum/VERIFIER.md](quantum/VERIFIER.md) — cascade, exact oracle, scaling.
- [quantum/METRICS.md](quantum/METRICS.md) — QVPS, TTS, TTE, chaos quota.
- [quantum/ANOMALY.md](quantum/ANOMALY.md) — Hall of Fame, labels, vault, monkey.
- [quantum/ROADMAP.md](quantum/ROADMAP.md) — Q0–Q13 order and gate.
- [phases/quantum/](phases/quantum/README.md) — one executable file per phase.

## Technical specification

- [ARCHITECTURE.md](ARCHITECTURE.md) — system overview and memory map.
- [BYTECODE.md](BYTECODE.md) — binary representation v0 (frozen by gate).
- [VM.md](VM.md) — minimal math virtual machine (safe, deterministic).
- [VERIFIER.md](VERIFIER.md) — Level-1 fast + Level-2 strict + cascade.
- [FITNESS.md](FITNESS.md) — multi-objective scoring and parsimony.
- [EVOLUTION.md](EVOLUTION.md) — selection, QD, islands, autoevolution.
- [CONSTANTS.md](CONSTANTS.md) — structure vs. coefficient strategy.
- [STACK.md](STACK.md) — technology choices and why.
- [GPU_ACCESS.md](GPU_ACCESS.md) — RTX 4060 access runbook: detection steps,
  wake-up, troubleshooting, measured baseline (read before any GPU task).
- [REPOSITORY.md](REPOSITORY.md) — repo layout contract.

## Measurement

- [METRICS.md](METRICS.md) — CVPS and supporting metrics.
- [BENCHMARKS.md](BENCHMARKS.md) — synthetic suites, baselines, protocol.
- [ABLATIONS.md](ABLATIONS.md) — what to remove and what it proves.
- [REPRODUCIBILITY.md](REPRODUCIBILITY.md) — seeds, hashes, opcode versions.
- [DASHBOARD.md](DASHBOARD.md) — live view + Hall of Fame.

## Governance

- [COMMITS.md](COMMITS.md) — Conventional Commits + branch/PR rules.
- [DECISIONS.md](DECISIONS.md) — decision log (append-only).
- [GLOSSARY.md](GLOSSARY.md) — shared vocabulary.
- [RISKS.md](RISKS.md) — risks, assumptions, mitigations.

## Maintenance rule

Any change that alters incentives, scoring, opcodes, verification strictness,
or reproducibility must update the affected docs and append one entry to
`DECISIONS.md` in the same change set.
