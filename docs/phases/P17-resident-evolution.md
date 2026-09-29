# P17 — GPU-resident evolutionary cycle

**Status:** Proposed.
**Prerequisite:** P16.
**Owner:** assigned when moving to Building; see the phase index.

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
