# Q-Forge experiments Q-E1..Q-E7

**Status:** decision (order binding; each needs its phase gate green).

Conventions for all quantum experiments: evolution never sees exact
solutions (`ψ_exact`, known symmetries); they are used only for post-hoc
scientific scoring. Splits, seeds, hashes, and wall-clock budgets follow
`docs/BENCHMARKS.md` and `docs/REPRODUCIBILITY.md`.

## Q-E1 — Conserved-operator discovery (start here)

Known models: transverse-field Ising `H = -J Σ ZiZi+1 - h Σ Xi`, Heisenberg
`H = J Σ (XiXi+1 + YiYi+1 + ZiZi+1)`, later J1-J2 and others.

Protocol per Hamiltonian: hide its known symmetries from the algorithm,
generate candidates, score `||[H, O]||`, penalize complexity, preserve
structurally different survivors, evolve. Goal: automatically rediscover
known conserved operators first; only then hunt less obvious structures.

## Q-E2 — Ground-state search (small systems, exact oracle available)

Generate compact ansatze (vectors, circuits, tensor structures, parametric
amplitudes, math programs). Verifier: energy expectation. Primary fitness:
`E_candidate`. Secondary (scoring only, never selection): fidelity
`|<ψ_exact|ψ_candidate>|²`. Report `E_candidate - E_exact` and fidelity.
The algorithm receives the Hamiltonian and energy fitness — never `ψ_exact`.

## Q-E3 — Circuit evolution + superoptimization

Evolve the circuit bytecode toward: target-state preparation, target-unitary
approximation, energy minimization, specific entanglement, fewer gates,
shallower depth. Fitness: `target_fidelity - gate_penalty - depth_penalty`.

Superoptimization variant: hand the system a known circuit; it must find an
*equivalent* circuit with fewer gates / smaller depth / fewer two-qubit
gates. Verification: for tiny systems, exact unitary comparison ignoring
global phase; for larger systems, efficient/certified methods only (never
hand-waved equivalence).

## Q-E4 — Formula discovery from simulated observables

Use the main symbolic-regression module on quantum-simulated data: couplings
`g`, field `h`, temperature `T`, size `N` -> observables (energy,
magnetization, correlation, entanglement, gap). Hide the original relation;
rediscover compact formulas, approximations, scaling laws, asymptotics.
Goal order: known relations first, unclear-analytic regimes only after.

## Q-E5 — Schrodinger residual search

Datasets from systems with known solutions (harmonic oscillator, particle in
a box, two-level system, small spin chains). Hide part of the structure;
evolve wavefunctions, energy formulas, compact approximations with the
EvoByte math programs (`EXP, MUL, ADD, POW, SIN, COS, ...`). Given `Hψ = Eψ`,
fitness is `||Hψ - Eψ|| + normalization_error + boundary_error +
complexity_penalty`.

## Q-E6 — Hamiltonian rediscovery (later)

Provide initial states, time evolution, measured observables; hide the
Hamiltonian that generated the data. Candidates `H_candidate` are scored by
"would this Hamiltonian reproduce the observed dynamics?" (predicted-vs-
observed dynamics error). Start with known artificial Hamiltonians (e.g.
`a·XX + b·YY + c·ZZ + h·Z`) and check structural recovery.

## Q-E7 — Quantum identity discovery

Generate expressions over Pauli operators, commutators, tensor products,
small matrices, unitaries; hunt identities (e.g. distributivity shapes
applied to far more complex quantum structures). Verifier: exact or symbolic
equality. Keep only identities that are correct, nontrivial, compact, and
novel relative to the archive. Validate the method on known identities first.
