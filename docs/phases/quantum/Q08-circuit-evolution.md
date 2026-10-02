# Q08 — Circuit evolution and superoptimization

**Status:** Complete (2026-09-29).
**Goal:** evolve circuits; then beat a known circuit at its own game.

## Objective

Evolve circuit bytecode toward target fidelity minus gate/depth penalties;
then the superoptimizer variant: given a known circuit, find an equivalent
one with fewer gates / shallower depth / fewer two-qubit gates. Tiny-system
equivalence is exact (unitary comparison ignoring global phase); larger
systems use certified methods only.

## Scope

In: circuit operators, fidelity fitness, exact-equivalence checker (tiny N),
superoptimization experiment (Bell/GHZ preparation first).
Out: large-N equivalence heuristics without certification proof.

## Tasks

1. `feat(quantum): add circuit evolution with fidelity fitness`.
2. `feat(quantum): add exact-equivalence checker + superoptimizer run`.
3. `test(quantum): bell-state preparation rediscovered from scratch (seeded)`.

## Exit gate

```bash
git diff --check
python3 -m pytest tests/test_quantum_circuit.py -q
python3 experiments/q08_superoptimize.py --seeds 3
```

### Empirical Artifact: Superoptimization & Equivalence Certificates

- **Date:** 2026-09-29
- **Environment:** x86_64, Linux 7.1.5-76070105-generic, Python 3.12.2, NumPy 2.4.6, PyTorch 2.14.0+cu130, GPU NVIDIA GeForce RTX 4060 Laptop (Driver 580.173.02)
- **Equivalence Criterion:** $\mathcal{F}_{process}(U_1, U_2) = \frac{|\mathrm{Tr}(U_1^\dagger U_2)|^2}{D^2} \ge 1.0 - 10^{-6}$ and phase-aligned Frobenius error $\le 10^{-6} \cdot D$.

| Benchmark | $N$ | Reference Circuit Profile (G/D/2Q) | Superoptimized Profile (G/D/2Q) | Delta (G/D/2Q) | Certified Equivalence | Process Fidelity | Mean QVPS |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Redundant Bell Circuit** | 2 | 6 / 4 / 1 | 2 / 2 / 1 | **-4 / -2 / -0** | **YES (3/3 seeds)** | 1.0000 | 20,244 |
| **Redundant GHZ Circuit** | 3 | 7 / 4 / 2 | 3 / 3 / 2 | **-4 / -1 / -0** | **YES (3/3 seeds)** | 1.0000 | 16,610 |
| **Identity Involutions** | 2 | 4 / 4 / 2 | 0 / 0 / 0 | **-4 / -4 / -2** | **YES (3/3 seeds)** | 1.0000 | 24,826 |

All 3 benchmark families achieved 100% certified unitary equivalence with exact gate/depth/2Q reductions. Bell state preparation rediscovered from scratch ($H(0) \to \mathrm{CNOT}(0, 1)$) at fidelity 1.0.

## Commit & Push (mandatory for this phase)

```bash
git status --short
git add src/evobyte/quantum/circuit_evo.py experiments/q08_superoptimize.py tests/test_quantum_circuit.py docs/phases/quantum/Q08-circuit-evolution.md
git commit -m "feat(quantum): evolve and superoptimize circuits"
git push -u origin phase-q08-circuit-evolution
gh pr create --title "feat(quantum): evolve and superoptimize circuits" --body "Q08 exit gate green. Closes #<issue>."
```
