# Q-Forge roadmap (Q0–Q13)

**Status:** decision. Order binding; no advance to Q13 before consistent
rediscovery of known results is demonstrated.

```text
Q0  Pauli bit representation (masks, symplectic rules, codec)
Q1  Pauli multiplication/commutation benchmark (XOR/AND/POPCOUNT throughput)
Q2  Known Hamiltonians (Ising, Heisenberg, J1-J2 builders)
Q3  Exact-diagonalization oracle (E_exact, ψ_exact; scoring-only discipline)
Q4  Random conserved-operator search (pure + structured baselines)
Q5  Evolutionary conserved-operator search (selection/mutation/crossover)
Q6  Ground-state candidate search (energy fitness, fidelity scoring)
Q7  Quantum circuit bytecode (gate table freeze)
Q8  Circuit evolution + superoptimization
Q9  Formula discovery from simulated observables (main-track module reuse)
Q10 Schrodinger residual search (residual + norm + boundary + complexity)
Q11 Hamiltonian rediscovery (dynamics-matching fitness)
Q12 Anomaly Vault + Quantum Hall of Fame + Infinite Monkey Quantum
Q13 Harder / less-understood systems (gated: consistent rediscovery first)
```

Executable files: [../phases/quantum/README.md](../phases/quantum/README.md).
Each phase states objective, scope, tasks, exit gate, and a Commit & Push
block. Movement rule (same as main track): a phase is Done only when its
gate artifact runs, is measured, is committed, and is pushed to GitHub.

## Scheduling revision (D013)

Preserve existing quantum artifacts, but defer new quantum development until
main-track P21 reproduction. This changes scheduling only: Q0–Q13 retain
their representation, correctness and rediscovery gates. Pauli bit-op or
quantum-candidate throughput is a separate metric and cannot substantiate
symbolic-search CVPS or the main-track million-S1 target.

## Integration acceptance audit (D015)

The Q07–Q13 software has been integrated with strict CI, while research
acceptance remains scoped to the evidence actually available. Known seeds
in Q10/Q13 and hand-written motifs in Q12 cannot count as blind learned
discovery; reference-based stopping in Q13 is not scoring-only isolation.
Historical tables remain intact with explicit interpretation corrections.
Q11's human-readable Y phases are corrected without changing the matrix
algebra, and its counter still excludes coefficient-refinement calls.
P32 records accepted/provisional/superseded/not_run classifications before
these records are used to support a new claim. This audit does not unlock
an expanded hard-system campaign or waive the existing rediscovery gates.
