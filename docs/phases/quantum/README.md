# Quantum phases Q00–Q13 (executable plan)

One file per phase for the Q-Forge track (see
[../../quantum/ROADMAP.md](../../quantum/ROADMAP.md)). Same rules as the main
track: one phase in flight, previous exit gate green, small reversible diffs,
gates block commit and push, every phase ends with a local commit AND a
remote push on a phase branch with a PR.

## Index

- [Q00 — Pauli bit representation](Q00-pauli-representation.md)
- [Q01 — Pauli algebra benchmark](Q01-pauli-benchmark.md)
- [Q02 — Known Hamiltonians](Q02-known-hamiltonians.md)
- [Q03 — Exact-diagonalization oracle](Q03-exact-oracle.md)
- [Q04 — Random conserved-operator search](Q04-random-conserved-search.md)
- [Q05 — Evolutionary conserved-operator search](Q05-evolutionary-conserved-search.md)
- [Q06 — Ground-state candidate search](Q06-ground-state-search.md)
- [Q07 — Quantum circuit bytecode](Q07-circuit-bytecode.md)
- [Q08 — Circuit evolution and superoptimization](Q08-circuit-evolution.md)
- [Q09 — Formula discovery from simulated observables](Q09-formula-from-observables.md)
- [Q10 — Schrodinger residual search](Q10-schrodinger-residual.md)
- [Q11 — Hamiltonian rediscovery](Q11-hamiltonian-rediscovery.md)
- [Q12 — Anomaly Vault, Hall of Fame, Infinite Monkey](Q12-anomaly-fame-monkey.md)
- [Q13 — Harder systems (gated)](Q13-harder-systems.md)

Status convention per file: `Proposed | Building | Done (commit SHA + date +
measurement)`.

## Integration acceptance audit (D015)

Implementation status and scientific acceptance are separate. Q07–Q13
software integration preserves the old measurements; it does not promote
pilot results to independent discoveries. Q10–Q13 contain interpretation
corrections, including known solution seeds, a hand-written motif sampler,
oracle-based stopping and incomplete evaluation counters. P32 audits these
claims with the main-track evidence. Numerical equivalence/fidelity checks
must state their tolerances; they are not exact symbolic proofs. Further
scientific acceptance requires controlled unseeded comparisons, complete
provenance and independent final verification. Provisional quantum records
do not block the main track's P30–P39 corrective program.
