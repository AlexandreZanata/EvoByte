# Quantum verifier: cascade, oracle, scaling

**Status:** decision (experimental track).

## Residual is not proof (binding doctrine)

A candidate may show a small residual on sampled points and still be wrong.
Therefore every quantum experiment runs the staged doctrine:

```text
FAST VERIFY (few points) -> DENSE VERIFY (many points)
-> HIGH-PRECISION VERIFY -> STRICT VERIFY
```

and compares against analytic solutions or exact diagonalization whenever
possible.

## Quantum cascade verifier (v0 shape, cutoffs tuned by measurement)

```text
10,000,000 candidates
  STAGE 0  binary validity            -> ~5,000,000
  STAGE 1  cheap mathematical constraints -> ~500,000
  STAGE 2  32 quantum samples         -> ~20,000
  STAGE 3  256 samples                -> ~1,000
  STAGE 4  full simulation            -> ~10
  STAGE 5  exact / high-precision     -> ELITES
```

Objective: never run expensive quantum simulation on evidently bad
candidates. Exact numbers are calibration outputs, not promises — the
principle (cheap rejection first) is fixed.

## Exact oracle (small Hilbert spaces)

While the Hilbert space stays small, exact diagonalization is ground truth:

```text
H -> exact diagonalization -> E_exact, ψ_exact
```

EvoByte never uses `ψ_exact` to produce candidates; it is used afterwards to
measure closeness. This creates a controlled scientific laboratory.

## Progressive difficulty (binding order)

Scale `2 -> 4 -> 6 -> 8 -> 10 -> 12 ...` qubits while reasonable. Record the
point where exact verification becomes the bottleneck; only then introduce
sparse methods, Lanczos, symmetry reduction, Monte Carlo, or tensor networks
— never preemptively.
