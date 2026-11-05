# Q06 — Ground-state candidate search

**Status:** Complete (2026-09-29, commit `1269c0bd`).
**Goal:** approximate `E_exact` by energy fitness alone.

## Objective

Evolve compact ansatze (bitmask-defined trial states / shallow circuits /
parametric amplitudes) scored by `E(ψ)` only; report `E_candidate - E_exact`
and fidelity post-hoc (never for selection) on 2–8 qubit Ising/Heisenberg.

## Scope

In: ansatz codec, energy fitness, fidelity scorer, small-N experiment.
Out: circuit bytecode table (Q07), large-`N` methods.

## Tasks

1. `feat(quantum): add ground-state ansatz codec and energy fitness`.
2. `test(quantum): energy of known eigenstate equals E_exact within tolerance`.
3. `feat(quantum): evolution run with TTS/TTE report`.

## Exit gate

```bash
git diff --check
python3 -m pytest tests/test_quantum_ground.py -q
python3 experiments/q06_ground_state.py --seeds 5
```

### Empirical Artifact: TTS / TTE Benchmark Table

- **Date:** 2026-09-29
- **Commit:** `1269c0bd`
- **Environment:** x86_64, Linux 7.1.5-76070105-generic, Python 3.12.2, NumPy 2.4.6, PyTorch 2.14.0+cu130, GPU NVIDIA GeForce RTX 4060 Laptop (Driver 580.173.02)
- **Target Hamiltonian:** Heisenberg XXX ($N=2$, $J=1.0$), Hash: `f6cdcb5515413cca`
- **Oracle Provenance:** $E_{exact} = -3.00000000$, Degeneracy: 1, Terms: 3
- **Selection Criterion:** Rayleigh quotient $\langle \psi | H | \psi \rangle$ ONLY (zero oracle leakage)
- **Target Tolerance:** $|E_{cand} - E_{exact}| \le 1.0\times 10^{-3}$

| Seed | Gen | Eval | Time (s) | QVPS | $E_{cand}$ | $E_{exact}$ | $\Delta E$ | Fidelity | TTS (s) | TTE | Result |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 0 | 1 | 40 | 0.0033 | 12272 | -3.000000 | -3.000000 | 4.44e-16 | 1.0000 | 0.00020 | 1 | PASS |
| 1 | 1 | 40 | 0.0027 | 14933 | -3.000000 | -3.000000 | 4.44e-16 | 1.0000 | 0.00016 | 1 | PASS |
| 2 | 1 | 40 | 0.0016 | 25025 | -3.000000 | -3.000000 | 4.44e-16 | 1.0000 | 0.00012 | 1 | PASS |
| 3 | 1 | 40 | 0.0017 | 23290 | -3.000000 | -3.000000 | 4.44e-16 | 1.0000 | 0.00014 | 1 | PASS |
| 4 | 1 | 40 | 0.0017 | 23271 | -3.000000 | -3.000000 | 4.44e-16 | 1.0000 | 0.00011 | 1 | PASS |

- **Summary:** 5/5 successes (100.0%) | Mean TTS: 0.00015s | Mean TTE: 1.0 evals | Mean Fidelity: 1.0000
- **Exit Gate Verdict:** PASS

#### Multimodel Benchmark Matrix

| Model | $N$ | Hash | $E_{exact}$ | Degeneracy | Terms | Success Rate | Mean TTS (s) | Mean TTE | Mean Fidelity |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Heisenberg | 2 | `f6cdcb5515413cca` | -3.00000000 | 1 | 3 | 5/5 (100%) | 0.00015s | 1.0 | 1.0000 |
| Ising | 2 | `6fe487152b049a3f` | -2.23606798 | 1 | 3 | 5/5 (100%) | 0.00011s | 1.0 | 1.0000 |
| Heisenberg | 3 | `ee09f252af10a249` | -4.00000000 | 2 | 6 | 5/5 (100%) | 0.00020s | 3.4 | 1.0000 |
| Ising | 3 | `537d1e308fb70ce5` | -3.49395921 | 1 | 5 | 5/5 (100%) | 0.00018s | 1.0 | 1.0000 |

## Commit & Push (mandatory for this phase)

```bash
git status --short
git add src/evobyte/quantum/ground.py experiments/q06_ground_state.py tests/test_quantum_ground.py docs/phases/quantum/Q06-ground-state-search.md
git commit -m "feat(quantum): search ground states by energy fitness"
git push -u origin phase-q06-ground-state-search
gh pr create --title "feat(quantum): search ground states by energy fitness" --body "Q06 exit gate green. Closes #<issue>."
```
