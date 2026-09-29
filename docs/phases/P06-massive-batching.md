# P06 — Massive batching at scale

**Status:** Done (2026-09-29 — gate green: 5/5 batching tests, 68/68 full suite;
cascade tuned under 7500 MB VRAM budget: S1 100k x 256 @ 3,106.1 CVPS / 117MB, S2 1k x 4096 @ 1,296.3 CVPS / 188MB, S3 10 x 10000 @ 654.5 CVPS / 4.6MB;
OOM-safe dynamic fallback verified; see commit `perf(bench)` below).
**Goal:** tune `N programs x points` without exploding 8 GB VRAM.

## Objective

Grid-tune the cascade (100k x 256 kill 99% -> 1k x 10k -> ~10 x full) on
reference hardware; record VRAM curve, per-stage throughput, early-stop
kill rate; freeze recommended defaults.

## Scope

In: batching policy + OOM-safe chunking + measurement tables.
Out: archive, evolution operators, L2.

## Tasks

1. `perf(bench): tune cascade cutoffs under 8 GB with chunking`.
2. `test(bench): assert OOM-safe fallback (chunk shrink, never crash)`.
3. `docs(metrics): record recommended N x batch + VRAM table`.

## Exit gate

```bash
git diff --check
python3 -m pytest tests/test_batching.py -q
python3 benchmarks/cvps.py --tune --vram-budget 7500
```

Artifact: N-x-batch table + VRAM usage + kill rates in the PR.

## Risks

- OOM on 8 GB — chunking + `torch.cuda.empty_cache` discipline, measured.

## Commit & Push (mandatory for this phase)

```bash
git status --short
git add benchmarks/cvps.py tests/test_batching.py docs/METRICS.md docs/phases/P06-massive-batching.md
git commit -m "perf(bench): tune VRAM-safe cascade batching"
git push -u origin phase-06-massive-batching
gh pr create --title "perf(bench): tune VRAM-safe cascade batching" --body "P06 exit gate green. Closes #<issue>."
```
