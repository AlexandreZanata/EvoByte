# Quantum Hall of Fame, discovery classes, Anomaly Vault

**Status:** decision (experimental track).

## Quantum Hall of Fame (separate section, append-only)

One entry per promotion; never overwrite an earlier discovery:

```text
problem_id, hamiltonian_hash, candidate_binary, decoded_candidate,
generation, parents, fitness, energy, exact_energy, energy_error, fidelity,
commutator_norm, gate_count, circuit_depth, novelty,
discovery_timestamp, total_candidates_tested, wall_clock_time
```

## Discovery classes (label every result; the software never auto-assigns the last)

- **REDISCOVERY** — known result recovered automatically.
- **NOVEL CANDIDATE** — apparently different result, not yet verified.
- **VERIFIED MATHEMATICAL RESULT** — property proven/mathematically verified.
- **PHYSICAL HYPOTHESIS** — structure consistent with data/simulation but
  without experimental proof.
- **NOVEL PHYSICAL RESULT** — must NOT be assigned automatically by software.

A formula that fits data is not automatically a new law of physics.

## Anomaly Vault

A special file for candidates with abnormally high fitness, highly unusual
structure, low complexity, high generalization, or large structural distance
from current elites. They receive extra verification. Rationale: never lose
an interesting result just because it came from a strange region of search.

## Infinite Monkey Quantum (official fun benchmark)

Question: with an extremely cheap generator producing an absurd number of
random quantum objects and a perfect verifier, how long until a valid
structure appears? Run separately: pure random, structured random,
evolution, evolution + novelty, micro-model. Targets: Bell-state
preparation, GHZ preparation, equivalent-circuit finding, conserved-operator
finding, ground-state approximation. Record candidates needed until the
first solution.
