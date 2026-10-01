# P26 — Reproducible tracing and exploration map

**Status:** Proposed.
**Prerequisite:** P25 corpus sealed.
**Owner:** assigned when moving to Building; see the phase index.

## Objective

Make every run reconstructible and every accepted solution explainable:
full per-run lineage (problem, method, config, bytecode version, sampler
state, batches, results, rejections, promotion ancestry) plus an
exploration map grouping expressions by structure, ops, length, behavior
and quality — counting distinct byte programs and, where decidable,
mathematically distinct expressions separately. Tracing cost is measured
and included in all throughput numbers.

## Scope

In: lineage record schema, checkpoints + reproducible seeds + batch hashes
+ aggregate counters for million-scale runs (full retention only for
promoted candidates), audit mode storing ALL candidates on small
campaigns, map builder (structure/op/length/behavior/quality buckets,
equivalence-class counting where cheap), replay-from-seed verifier,
tracing-overhead accounting.
Out: new search methods, new benchmarks, storing every candidate of every
massive run (bounded by design), semantic equivalence proofs (report
buckets, not theorems).

## Ordered work

- Freeze the lineage schema first: every field required to replay a run
  and to answer "where did this accepted solution come from".
- Implement aggregate tracing (counters + hashes + checkpoints) with
  overhead measured against a no-tracing baseline on the P24 stable config.
- Implement audit mode (full candidate store) for small campaigns and a
  replay tool that rebuilds trajectories and promotion ancestry bit-exactly.
- Build the map over a reference campaign: bucket counts, distinct-bytes
  vs distinct-expression accounting, coverage of the declared space.
- Publish overhead numbers alongside map and replay evidence.

## Max-GPU rule (standing)

Tracing must not become the bottleneck: async device-to-host copies on a
dedicated stream, batched writes from CPU workers, bounded buffers with
backpressure (slow the search rather than OOM). Audit mode is small-campaign
only by construction.

## Exit gate

The phase-specific CLI below is an acceptance interface to implement during
this phase, not a claim that the current checkout supports it. Common checks
already exist. Run the experiment only after its prerequisite is green.

```bash
git diff --check
python3 -m pytest tests -q
make verify
python3 benchmarks/evo_trace.py --audit --seeds 3 --output experiments/p26-lineage.json
```

Artifact: checksummed `experiments/p26-lineage.json` with replay evidence
(bit-exact rebuild on audit campaigns), the exploration map, and measured
tracing overhead. Done means: rebuild any run from (commit, config, seed)
and explain each accepted solution's ancestry — with tracing cost on the
bill.

## Risks

Logging that serializes the GPU loop, unbounded disk growth, ancestry
pointers broken by dedup/resume, equivalence bucketing mistaken for proof.
Overhead above the preregistered ceiling fails the gate even if replay works.

## Commit & Push (mandatory)

Start from a clean tree on `codex/p26-lineage-map`. Follow the common
commit procedure in [README.md](README.md#commit-and-push-contract), using
this phase's exact reviewed file list and artifact manifest. One completed
micro-task produces one atomic commit; never commit a failed gate.

```bash
git status --short
git diff --check
git diff --cached --check
git commit -m "feat(bench): complete p26 lineage-map"
git push -u origin HEAD
gh pr create --title "feat(bench): complete p26 lineage-map" --body-file /tmp/evobyte-p26-pr.md
git status --short
```
