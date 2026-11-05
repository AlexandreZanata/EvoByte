# Quantum metrics and ablations

**Status:** decision (experimental track).

## New metrics (in addition to CVPS)

- **QVPS — Quantum Candidates Verified Per Second** (through the cheapest
  quantum verification stage reached or passed, always named).
- **TTS — Time To Solution** (wall-clock to first candidate meeting the
  pre-registered success threshold).
- **TTE — Time To Exactness** (wall-clock to matching the exact oracle
  within tolerance).

Example report shape (illustrative, never a claim):

```text
QVPS: 4.8M, TTE: 37.4 s, candidates explored: 178M
```

Never invent numbers — measure experimentally with hardware, driver, commit,
seed, and Hamiltonian-hash provenance.

## Quantum ablation battery

Same Hamiltonian, same hardware, same wall-clock budget; measure best
energy, fidelity, commutator error, candidate throughput, time-to-discovery:

```text
PURE RANDOM vs GENETIC vs MAP-ELITES vs ISLAND MODEL
vs MICRO-GENERATOR vs MICRO-GENERATOR + EVOLUTION
```

A component stays only if it improves quality or time at fixed budget.

## Chaos quota (binding floor)

A fraction of GPU capacity stays dedicated to **pure chaos** even after
evolution works (initial shape `60% exploitation / 20% mutation / 10%
crossover / 10% complete random` — starting point only, then measured and
adapted automatically). Rationale: preserve the chance of finding structures
entirely outside current families. Never allow 100% elite-derived
populations.
