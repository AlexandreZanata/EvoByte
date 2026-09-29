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
