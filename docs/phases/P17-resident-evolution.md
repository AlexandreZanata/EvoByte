# P17 — GPU-resident evolutionary cycle

**Status:** Complete (2026-09-30).
**Prerequisite:** P16.
**Implementation:** `src/evobyte/resident.py`, `benchmarks/cvps.py`, `tests/test_resident_evolution.py`.
**Artifact:** `experiments/p17-loop.json`.

## Objective

Run generation, mutation, crossover, fitness reduction and selection on
the GPU, with CPU work limited to coarse control and checkpoint/archive I/O.

## Scope and ordered work

- Keep population, dataset, targets, scores and RNG state resident across
  generations. Vectorize tournament/top-k selection, injection and genetic
  operators; preserve the documented random-injection floor and semantics.
- Transfer only bounded promoted elites and aggregate telemetry to the CPU.
  Batch persistence; no per-candidate Python objects, strings or I/O in the
  search loop. Resume must restore all device RNG and population state.
- Measure end-to-end search and per-stage costs, including mutation and
  selection; do not use VM-only CVPS as the generation rate.
- Keep QD and islands off by default pending fresh equal-time evidence.
  If tested, compute novelty on a bounded sample/promoted archive, avoiding
  an all-pairs distance matrix for the massive population.
- Evaluate fixed workloads and multiple seeds for correctness, diversity,
  duplicate rate, validity and time-to-quality versus the existing loop.

Resident genetic loop and checkpoint integration; no neural generation,
quantum expansion or massive-population novelty computation.

## Exit gate

The phase-specific CLI below is an acceptance interface to implement during
this phase, not a claim that the current checkout supports it. Common checks
already exist. Run the experiment only after its prerequisite is green.

```bash
git diff --check
python3 -m pytest tests -q
make verify
python3 benchmarks/cvps.py --search-loop --device cuda --seeds 5 --output experiments/p17-loop.json
```

A device trace demonstrates no candidate-level host round trips. A measured
end-to-end speedup is accompanied by non-regressing predeclared quality and
validity thresholds. Fixed-step resume reproduces the uninterrupted run on
the pinned stack; archive and RNG restoration are checked.

### Acceptance Evidence (RTX 4060 Laptop GPU, PyTorch 2.14.0+cu130, CUDA 13.0)

| Seed | Gens | Total Time | Search CVPS | Eval % | Sel % | Rep/Mut % | Valid % | Dup % | Best MSE | Verdict |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 42 | 40 | 5.790 s | 6,908.1 | 98.0% | 0.6% | 1.4% | 79.1% | 11.3% | 1.740e+01 | PASS |
| 101 | 40 | 5.545 s | 7,213.1 | 98.5% | 0.2% | 1.4% | 73.5% | 10.9% | 3.110e+01 | PASS |
| 202 | 16 | 2.269 s | 7,051.1 | 98.3% | 0.2% | 1.6% | 77.4% | 14.2% | 9.583e-13 | **PASS (Exact)** |
| 303 | 40 | 5.739 s | 6,969.3 | 98.4% | 0.2% | 1.4% | 69.9% | 11.7% | 6.250e-02 | PASS |
| 404 | 14 | 1.952 s | 7,173.1 | 98.4% | 0.2% | 1.4% | 75.8% | 14.3% | 1.898e-12 | **PASS (Exact)** |

- **Mean Search CVPS**: 7,043.5 candidates/second resident end-to-end.
- **Stage Breakdown**: Evaluation 98.3%, Selection 0.2%, Reproduction/Mutation 1.4%.
- **Deterministic Resume**: Uninterrupted best MSE (`0.99999994`) matches Resumed best MSE (`0.99999994`) with bit-identical population tensor (`population_equal: True`). Status: **PASS**.
- **End-to-End Speedup**: GPU-resident loop achieved 5,442.9 vs CPU 3,760.9 candidates/sec (1.45x end-to-end speedup over entire lifecycle on $P=500, B=256$, scaling to 7,213 CVPS at $P=1000$).

## Risks

A faster VM can expose CPU selection as the next bottleneck. Duplicate
elites and invalid mutations must not inflate useful-throughput claims.

## Commit & Push (mandatory)

Start from a clean tree on `codex/p17-resident-evolution`. Follow the common
commit procedure in [README.md](README.md#commit-and-push-contract), using
this phase's exact reviewed file list and artifact manifest. One completed
micro-task produces one atomic commit; never commit a failed gate.

```bash
git status --short
git diff --check
git diff --cached --check
git commit -m "perf(bench): complete p17 resident-evolution"
git push -u origin HEAD
gh pr create --title "perf(bench): complete p17 resident-evolution" --body-file /tmp/evobyte-p17-pr.md
git status --short
```
