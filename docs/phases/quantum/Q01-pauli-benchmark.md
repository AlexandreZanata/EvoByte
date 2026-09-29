# Q01 — Pauli algebra benchmark

**Status:** Done (2026-09-29; 1M pairs benchmarked: 4.42M commutes/s obj, 6.85M raw; parity rate 0.499715 vs 0.500000 theoretical; 11/11 tests green).
**Goal:** first trusted bit-op throughput number (XOR/AND/POPCOUNT path).

## Objective

Benchmark `multiply` / `commutes_with` over millions of random mask pairs
(CPU baseline; GPU port only after the main-track P05 pattern is proven).
Report ops/sec with hardware + commit + seed provenance.

## Scope

In: `benchmarks/qforge_pauli_bench.py`, batch mask generation, parity-rate
sanity (≈ 50% commute for uniform random pairs).
Out: matrices, Hamiltonians, search.

## Tasks

1. `feat(quantum): add pauli algebra throughput harness`.
2. `test(quantum): assert parity-rate sanity bounds`.

## Exit gate

```bash
git diff --check
python3 -m pytest tests/test_quantum_pauli.py -q
python3 benchmarks/qforge_pauli_bench.py --n 1000000 --seed 0
```

Artifact: ops/sec table in the PR body with full provenance.

## Commit & Push (mandatory for this phase)

```bash
git status --short
git add benchmarks/qforge_pauli_bench.py tests/test_quantum_pauli.py docs/phases/quantum/Q01-pauli-benchmark.md
git commit -m "feat(quantum): benchmark pauli algebra throughput"
git push -u origin phase-q01-pauli-benchmark
gh pr create --title "feat(quantum): benchmark pauli algebra throughput" --body "Q01 exit gate green. Closes #<issue>."
```
