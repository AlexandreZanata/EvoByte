# Q12 — Anomaly Vault, Quantum Hall of Fame, Infinite Monkey Quantum

**Status:** Complete (2026-09-29).
**Goal:** preserve the weird, honor the best, measure the absurd.

## Objective

Implement per [ANOMALY.md](../../quantum/ANOMALY.md): the Quantum Hall of
Fame writer (full provenance rows, append-only), discovery-class labeling
(software-never-`NOVEL PHYSICAL RESULT`), the Anomaly Vault with extra
verification, and the Infinite Monkey Quantum benchmark (pure / structured /
evolution / +novelty / micro-model on Bell, GHZ, conserved-operator, and
ground-state targets; candidates-to-first-solution recorded).

## Scope

In: fame writer, labels, vault, monkey harness.
Out: new search operators, harder systems (Q13).

## Tasks

1. `feat(quantum): add hall-of-fame writer and discovery labels`.
2. `feat(quantum): add anomaly vault with extra-verification hook`.
3. `feat(quantum): add infinite-monkey benchmark harness + first table`.

## Exit gate

```bash
git diff --check
python3 -m pytest tests/test_quantum_anomaly.py -q
python3 benchmarks/qforge_monkey.py --targets bell,ghz --seeds 3
```

Artifact: fame sample row + monkey table (candidates to first solution).

### Measured Artifacts (`benchmarks/qforge_monkey.py --targets bell,ghz --seeds 3`)

#### Infinite Monkey Quantum Table (Candidates to First Solution)

| Target | Sampler | Seed | Result | TTE (Evaluations) | Time (s) | QPS | Fidelity | Discovered Circuit |
|---|---|---|---|---|---|---|---|---|
| BELL | pure_random | 0 | PASS | 36 | 0.0027 | 13,278 | 1.0000 | `H q[1]; CNOT q[1], q[0]` |
| BELL | pure_random | 1 | PASS | 97 | 0.0081 | 11,997 | 1.0000 | `H q[1]; CNOT q[1], q[0]` |
| BELL | pure_random | 2 | PASS | 521 | 0.0263 | 19,806 | 1.0000 | `H q[1]; CNOT q[1], q[0]` |
| BELL | structured_random | 0 | PASS | 3 | 0.0002 | 12,975 | 1.0000 | `RY(1.5708) q[1]; CNOT q[1], q[0]` |
| BELL | structured_random | 1 | PASS | 2 | 0.0002 | 11,502 | 1.0000 | `RY(1.5708) q[1]; CNOT q[1], q[0]` |
| BELL | structured_random | 2 | PASS | 3 | 0.0002 | 13,937 | 1.0000 | `H q[1]; CNOT q[1], q[0]` |
| BELL | evolution | 0 | PASS | 36 | 0.0018 | 19,558 | 1.0000 | `H q[1]; CNOT q[1], q[0]` |
| BELL | evolution | 1 | PASS | 217 | 0.0077 | 28,306 | 1.0000 | `H q[0]; CNOT q[0], q[1]` |
| BELL | evolution | 2 | PASS | 530 | 0.0179 | 29,617 | 1.0000 | `H q[1]; CNOT q[1], q[0]` |
| BELL | evolution_novelty | 0 | PASS | 36 | 0.0018 | 19,576 | 1.0000 | `H q[1]; CNOT q[1], q[0]` |
| BELL | evolution_novelty | 1 | PASS | 148 | 0.0074 | 19,995 | 1.0000 | `H q[0]; CNOT q[0], q[1]` |
| BELL | evolution_novelty | 2 | PASS | 197 | 0.0099 | 19,878 | 1.0000 | `H q[1]; CNOT q[1], q[0]` |
| BELL | micro_model | 0 | PASS | 1 | 0.0001 | 15,579 | 1.0000 | `H q[0]; CNOT q[0], q[1]` |
| BELL | micro_model | 1 | PASS | 1 | 0.0001 | 17,955 | 1.0000 | `H q[0]; CNOT q[0], q[1]` |
| BELL | micro_model | 2 | PASS | 1 | 0.0000 | 20,287 | 1.0000 | `H q[0]; CNOT q[0], q[1]` |
| GHZ | pure_random | 0 | PASS | 4,464 | 0.3073 | 14,525 | 1.0000 | `RY(1.5708) q[0]; CNOT q[0], q[2]; CNOT q[2], q[1]` |
| GHZ | pure_random | 1 | PASS | 3,046 | 0.1928 | 15,799 | 1.0000 | `RY(1.5708) q[2]; CNOT q[2], q[0]; CNOT q[0], q[1]` |
| GHZ | pure_random | 2 | PASS | 6,681 | 0.4219 | 15,834 | 1.0000 | `H q[0]; CNOT q[0], q[1]; CNOT q[1], q[2]` |
| GHZ | structured_random | 0 | PASS | 102 | 0.0056 | 18,141 | 1.0000 | `RY(1.5708) q[0]; CNOT q[0], q[1]; CNOT q[0], q[2]` |
| GHZ | structured_random | 1 | PASS | 11 | 0.0007 | 15,817 | 1.0000 | `RY(1.5708) q[2]; CNOT q[2], q[1]; CNOT q[2], q[0]` |
| GHZ | structured_random | 2 | PASS | 7 | 0.0004 | 15,568 | 1.0000 | `RY(1.5708) q[1]; CNOT q[1], q[0]; CNOT q[1], q[2]` |
| GHZ | evolution | 0 | FAIL | 25,000 | 1.0311 | 24,247 | 0.0000 | N/A (Budget exhausted) |
| GHZ | evolution | 1 | FAIL | 25,000 | 0.9659 | 25,882 | 0.0000 | N/A (Budget exhausted) |
| GHZ | evolution | 2 | FAIL | 25,000 | 1.0432 | 23,964 | 0.0000 | N/A (Budget exhausted) |
| GHZ | evolution_novelty | 0 | FAIL | 25,000 | 2.8093 | 8,899 | 0.0000 | N/A (Budget exhausted) |
| GHZ | evolution_novelty | 1 | PASS | 18,435 | 2.0638 | 8,933 | 1.0000 | `H q[2]; CNOT q[2], q[0]; CNOT q[0], q[1]` |
| GHZ | evolution_novelty | 2 | PASS | 5,895 | 0.6587 | 8,950 | 1.0000 | `H q[2]; CNOT q[2], q[1]; CNOT q[1], q[0]` |
| GHZ | micro_model | 0 | PASS | 1 | 0.0001 | 15,500 | 1.0000 | `H q[0]; CNOT q[0], q[1]; CNOT q[1], q[2]` |
| GHZ | micro_model | 1 | PASS | 1 | 0.0001 | 17,847 | 1.0000 | `H q[0]; CNOT q[0], q[1]; CNOT q[1], q[2]` |
| GHZ | micro_model | 2 | PASS | 1 | 0.0001 | 19,045 | 1.0000 | `H q[0]; CNOT q[0], q[1]; CNOT q[1], q[2]` |

#### Sample Quantum Hall of Fame Row (`quantum_fame.jsonl`)

```json
{
  "problem_id": "monkey_bell",
  "hamiltonian_hash": "hash_bell",
  "candidate_binary": "000000000000f03f000000000000f03f000000000000f03f00000000000000000000000000002440000000000000f03f00000000000000000000000000000000",
  "decoded_candidate": "H q[1]; CNOT q[1], q[0]",
  "generation": 1,
  "parents": ["pure_random"],
  "fitness": 0.0,
  "energy": null,
  "exact_energy": null,
  "energy_error": null,
  "fidelity": 1.0,
  "commutator_norm": null,
  "gate_count": 2,
  "circuit_depth": 2,
  "novelty": 0.0,
  "discovery_timestamp": 1790713524.9587204,
  "total_candidates_tested": 36,
  "wall_clock_time": 0.0027112329989904538,
  "discovery_class": "REDISCOVERY"
}
```

#### Sample Anomaly Vault Row (`anomaly_vault.jsonl`)

```json
{
  "entry": {
    "problem_id": "monkey_bell",
    "hamiltonian_hash": "hash_bell",
    "candidate_binary": "000000000000f03f000000000000f03f000000000000f03f00000000000000000000000000002440000000000000f03f00000000000000000000000000000000",
    "decoded_candidate": "H q[1]; CNOT q[1], q[0]",
    "generation": 1,
    "parents": ["pure_random"],
    "fitness": 0.0,
    "fidelity": 1.0,
    "gate_count": 2,
    "circuit_depth": 2,
    "novelty": 0.0,
    "discovery_timestamp": 1790713524.9587204,
    "total_candidates_tested": 36,
    "wall_clock_time": 0.0027112329989904538,
    "discovery_class": "REDISCOVERY"
  },
  "anomaly_reason": "Ultra-compact structure (2 gates); Minimal circuit depth (2)",
  "verification": {
    "verified": true,
    "high_precision_fidelity": 0.9999999999999996,
    "perturbation_stability": 0.9999999935634487,
    "entanglement_entropy": 1.0,
    "details": {
      "unitarity_error": 2.220446049250313e-16
    }
  },
  "vault_timestamp": 1790713524.959563
}
```

## Commit & Push (mandatory for this phase)

```bash
git status --short
git add src/evobyte/quantum/fame.py benchmarks/qforge_monkey.py tests/test_quantum_anomaly.py docs/quantum/ANOMALY.md docs/phases/quantum/Q12-anomaly-fame-monkey.md
git commit -m "feat(quantum): add fame vault and monkey benchmark"
git push -u origin phase-q12-anomaly-fame-monkey
gh pr create --title "feat(quantum): add fame vault and monkey benchmark" --body "Q12 exit gate green. Closes #<issue>."
```
