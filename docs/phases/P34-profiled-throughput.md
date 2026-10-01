# P34 — Profiled full-pipeline throughput and bounded tracing

**Status:** Proposed.
**Prerequisite:** P33 verdict recorded; use its winning path or the P32 accepted baseline.
**Owner:** assigned when moving to Building.
**Branch:** `codex/p34-profiled-throughput`.

## Objective

Improve sustained useful throughput on the RTX 4060 while billing all generation,
scoring, selection and tracking costs. Establish whether CPU orchestration, kernel
launches, logging or computation is the current bottleneck.

## Scope

Existing gpu_limits, batching, VM, resident and evo_trace paths. Adopt one measured
optimization at a time with correctness checks; no corpus change, model training or
weakened verifier.

## Ordered work

- Profile CPU/CUDA operations and transfers on the same engine with tracing off/on.
  Preserve a frozen baseline, data distribution and live-op lengths; report arithmetic
  and mixed-opcode workloads separately at 32/256/1024 points.
- Remove measured unnecessary host transfers, per-candidate hashing/decoding,
  allocations and synchronizations. Test reusable buffers, vectorized kernels, torch
  compilation/fusion and CUDA Graphs when the profile supports them; Triton/CUDA
  requires measured benefit plus conformance. Include setup/compilation/capture time
  separately and bill it appropriately.
- Implement bounded batched lineage writes and asynchronous copies with correct
  event/stream dependencies and backpressure. Keep exact tracking in small audit
  campaigns and replayable aggregate tracking in large ones. Preregister a <=15%
  added-time target for aggregate tracing on the same algorithm; report misses honestly.
- Re-sweep batch sizes, streams and CPU worker counts under current free VRAM minus
  reserve; include temporary allocations, invalid masks, deduplication and final
  reduction. Exercise controlled OOM halving and resumed execution rather than claiming
  safety solely from zero OOM observations.
- Run real 10 s/1 min/10 min campaigns over five seeds and a 1 h confirmation. Stability
  workloads run for their actual duration; search convergence is a separate leg. Record
  thermal/power/utilization/latency/VRAM series and no-growth evidence.
- Report distinct S0-valid scored candidates/s at 32 points, full search throughput,
  full-verifier acceptance rate and candidate-points/s separately. Million/s remains a
  stretch hypothesis. Distinct-by-lot is never global novelty; short arithmetic peaks
  cannot become general-model headlines.

## Exit gate

The phase-specific CLI below is an interface to implement during this phase;
it is not a claim that these flags already exist. Run its experiment only
after prerequisites and common checks pass. Freeze configurations before
measurement. Complete one bounded micro-task at a time; failed correctness
or integrity gates block commit/push. A sound negative experiment is not a
reason to weaken its registered thresholds.

```bash
git diff --check
git status --short
python3 -m pytest tests -q
make verify
python3 benchmarks/gpu_limits.py --profile-pipeline --tracing --budgets 10s,1m,10m --confirm-1h --seeds 5 --output experiments/p34-throughput.json
```

A synchronized baseline/optimized/tracing comparison and real sustained operating
envelope with replay/parity/resource gates green. A missed speed/tracing target is a
published negative finding, not achieved. P35 uses only a validated configuration and
includes its measured tracking cost.

## Resource and evidence contract

Use the accepted RTX 4060 Laptop operating envelope: current free VRAM minus
reserve, bounded chunks/buffers, explicit stream dependencies, synchronized
timing, controlled failure and complete checkpoints. Add streams/workers
only with measured benefit. Keep bytecode/data resident in the hot loop;
text conversion, exact checking and artifact I/O remain outside it and their
costs are disclosed. Record clean revision, full configuration, RNG state,
actual device, dataset/split/checker hashes and durable raw-artifact hashes.

## Risks

The highest measured rate is not the hardware ceiling. More VRAM occupancy, threads or
streams need not improve throughput. Profiler overhead and asynchronous timing can
distort comparisons.

## Commit & Push (mandatory)

Start from a clean tree on `codex/p34-profiled-throughput` from the accepted
predecessor.
Follow [README.md](README.md#commit-and-push-contract); explicitly stage
only reviewed implementation/test/documentation files and the small phase
manifest. Never commit large/private raw data. Create/update a PR against
the accepted predecessor (or main after it is integrated), then confirm a
clean tree. Each finished micro-task produces one atomic commit after all
its applicable gates pass; the block below is for final phase completion.

```bash
git status --short
git diff --check
git diff --cached --check
git commit -m "perf(bench): complete p34 profiled-throughput"
git push -u origin HEAD
gh pr create --title "perf(bench): complete p34 profiled-throughput" --body-file /tmp/evobyte-p34-pr.md
git status --short
```
