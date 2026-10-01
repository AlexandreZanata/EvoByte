# P32 — Replay, resume and honest evidence acceptance

**Status:** Proposed.
**Prerequisite:** P30 isolation and P31 verifier gates green.
**Owner:** assigned when moving to Building.
**Branch:** `codex/p32-replay-acceptance`.

## Objective

Establish a trustworthy baseline for all subsequent research: actual continuation from
checkpoints, correct lineage, honest counters and fail-closed manifests from a clean
revision.

## Scope

Existing provenance, resident/checkpoint, evo_trace and gpu_limits paths and their
acceptance tests. No new optimization, learned model or open-problem campaign.

## Ordered work

- Audit P24/P26 checkpoint and lineage paths against execution. Store population/buffers
  needed to resume, fitted constants, counters, archive, all CPU/CUDA RNG states and
  algorithm state. Compare an uninterrupted trajectory with a resumed trajectory
  bit-for-bit under fixed steps; opening a checkpoint is insufficient.
- Validate both parents and offspring ordering for crossover/mutation, promoted
  ancestry, replayed bytecode and fitness/flags. Behavioral signatures are probe
  buckets, not proven mathematical equivalence classes.
- Separate total generation, S0-valid, executed/scored, distinct bytes per declared
  window, repeated bytes and exact semantic equivalence where available. Sampled
  validity is labelled estimated. A full hash-set cap yields unknown duplicate counts,
  never invented repeats.
- Ensure deadlines cover generation, execution, scoring, selection, fitting and
  tracking; synchronize GPU completion and report overshoot. Compare equal step counts
  for determinism and equal real wall time for performance.
- Make PASS/eligibility derive from mandatory check results. Verify raw-artifact hashes
  against the saved files and reject missing/altered artifacts. Test that a changed
  configuration changes the executed path, not merely the config hash.
- Produce a claim-to-evidence audit of retained P13–P29 conclusions with
  accepted/provisional/superseded/not_run classifications. Freeze a clean code revision
  and complete resolved config/dependency/split hashes. Re-evaluate H1 only under its
  unchanged original criteria.

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
python3 benchmarks/evo_trace.py --acceptance-audit --resume --seeds 5 --output experiments/p32-integrity.json
```

A clean-revision audit reproduces fixed-step continuations and true ancestry, reconciles
counters, rejects bad manifests and records the status of each retained claim. A missing
scientific win can be a valid negative result; any integrity failure blocks P33.

## Resource and evidence contract

Use the accepted RTX 4060 Laptop operating envelope: current free VRAM minus
reserve, bounded chunks/buffers, explicit stream dependencies, synchronized
timing, controlled failure and complete checkpoints. Add streams/workers
only with measured benefit. Keep bytecode/data resident in the hot loop;
text conversion, exact checking and artifact I/O remain outside it and their
costs are disclosed. Record clean revision, full configuration, RNG state,
actual device, dataset/split/checker hashes and durable raw-artifact hashes.

## Risks

Same-machine replay is numerical reproducibility, not independent authorship. Archive
the exact runtime and source revision; fixed-time trajectories need statistical
comparisons.

## Commit & Push (mandatory)

Start from a clean tree on `codex/p32-replay-acceptance` from the accepted predecessor.
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
git commit -m "fix(bench): complete p32 replay-acceptance"
git push -u origin HEAD
gh pr create --title "fix(bench): complete p32 replay-acceptance" --body-file /tmp/evobyte-p32-pr.md
git status --short
```
