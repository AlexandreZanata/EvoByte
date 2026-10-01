# P24 — Stable limits of the RTX 4060 (real budgets, reconciled counters)

**Status:** Done (2026-09-30; STABLE, headline 138,468 distinct/s; artifact `experiments/p24-limits.json`; `make verify` + `pytest` green).
**Prerequisite:** P23 pilot recorded (DROP, billed costs in `experiments/p23-pilot.json`).
**Owner:** executed on `codex/p24-stable-limits` from `5f9c129`.

## Objective

Find the highest STABLE end-to-end throughput of distinct generated +
evaluated candidates per second on the RTX 4060 Laptop, with real budgets,
reconciled counters and bounded memory. Extends
[test_max_gpu.py](../../tests/test_max_gpu.py) to representative workloads.
Corrects the P20 caveats: short 0.13 s windows, generation/error excluded
from the counted interval, NOP-heavy populations and `time_scale = 0.02`
sustained campaigns must not pass as full sustained speed here.

## Scope

In: batch grid (P x B at 32/256/1024 points), program-length and
opcode-mix grid (short/long, arithmetic-only/full set), 1/2/4 CUDA streams
with private buffers + explicit sync, 1/2/4/8 CPU workers for
prepare/final-verify/record (adopted only if measured better), adaptive VRAM
budget from free memory minus reserve for system/context/temporaries,
gradual batch growth with OOM halving + checkpoint + record, controlled
shutdown on unrecoverable failure, real 10 s / 1 min / 10 min runs plus a
real 1 h confirmation (no budget scaling, no early convergence exit in the
stability leg), telemetry (peak VRAM, temp, clocks, utilization, latency
histograms), CPU-oracle parity, resume, no-leak check.
Out: new search algorithms, new opcode semantics, quality/rediscovery
claims (those belong to P13/P19-style gates), held-out math corpora.

## Ordered work

- Freeze the workload grid and the stability definition before measuring:
  fixed seeds, opcode/length distributions with disclosed NOP fraction,
  uniqueness window, duplicate handling, stop conditions.
- Sweep batches/streams/workers; each stream owns its buffers; CPU never
  blocks the GPU critical path. Record per-stage costs INCLUDING generation
  and error computation in the counted rate.
- Run the real budget ladder per seed; log OOM halvings, checkpoints and
  any controlled abort. A scaled-down campaign is a scouting run, never the
  reported number.
- Reconcile counters (generated vs S0-valid vs distinct vs S1-scored),
  verify parity against the CPU oracle, resume from checkpoint and compare,
  assert flat memory across the run.

## Max-GPU rule (standing)

Max of the 4060 without crashing: VRAM budget from CURRENT free memory
(never a fixed 7000 MB assumption without measuring), chunk cap, 8 CPU
threads max, streams with private buffers, `empty_cache` + `synchronize`
before timing, OOM halving with checkpoint. High occupancy or high memory
alone never counts as efficiency; only stable reconciled throughput does.

## Exit gate

The phase-specific CLI below is an acceptance interface to implement during
this phase, not a claim that the current checkout supports it. Common checks
already exist. Run the experiment only after its prerequisite is green.

```bash
git diff --check
python3 -m pytest tests -q
make verify
python3 benchmarks/gpu_limits.py --budgets 10s,1m,10m --confirm-1h --seeds 5 --output experiments/p24-limits.json
```

Artifact: checksummed `experiments/p24-limits.json` with the stable
configuration, reconciled counters, parity/resume/leak evidence, full
telemetry series and a durable raw-artifact reference. The headline number
is the highest STABLE rate; scouting/peak numbers are labelled as such.

### Empirical artifact (2026-09-30, RTX 4060 Laptop 8 GB, torch 2.14.0+cu130)

Workload grid hash `112fd9810360eca9`, target `quad-x2-3x-7`. Winner config
(standard/full mix, disclosed audit): P=20000, B=256, 1 stream, 1 worker.
Extra streams/workers measured slower-or-equal and were not adopted. VRAM
budget adapted from current free memory (6472 MB); peak held at 320-336 MB:
the pipeline is launch/CPU-orchestration bound at this workload, not
VRAM-bound. Zero OOM events in all 31 legs.

| Leg | Seeds | Distinct/s (range) | Raw/s | Iters | Peak VRAM |
|:---|:---:|:---:|:---:|:---:|:---:|
| 10 s ladder | 5 | 93,093–162,525 | 96k–168k | 49–84 | 320 MB |
| 1 min ladder | 5 | 124,606–144,197 | 129k–149k | 386–447 | 320 MB |
| 10 min ladder | 5 | 138,468–150,121 | 143k–155k | 4285–4646 | 320 MB |
| 1 h confirm (seed 404, median) | 1 | 130,049 | 134,138 | 24,145 | 336 MB |
| Resident xcheck (P17 path, 60 s) | 1 | — (8,714 search cvps) | — | 262 gens | — |

Headline (min-seed 10 min): **138,468 distinct/s**. Confirm within 8.6% of
the 10 min median (tolerance 15%). Parity worst-abs-err 7.63e-06 (PASS),
resume from checkpoint PASS, allocator growth 62.5 MB <= 64 MB (PASS).
Scout variants (10 s, labelled SCOUT, never the headline): B=32 reaches
157k distinct/s while B=1024 drops to 54k (4x points = 4x work per
candidate; the pipeline is launch-bound at small B, compute-bound at large
B). The arith/short mix peaks at 517k distinct/s — a real but
non-representative workload (short arithmetic programs); only the
standard/full mix feeds the reported ladder.

## Risks

Thermal throttling across the 1 h run, driver memory fragmentation, cheap
duplicate/NOP workloads flattering the rate, stream-sync bugs silently
serializing execution. A faster number without reconciliation is rejected.

## Commit & Push (mandatory)

Start from a clean tree on `codex/p24-stable-limits`. Follow the common
commit procedure in [README.md](README.md#commit-and-push-contract), using
this phase's exact reviewed file list and artifact manifest. One completed
micro-task produces one atomic commit; never commit a failed gate.

```bash
git status --short
git diff --check
git diff --cached --check
git commit -m "perf(bench): complete p24 stable-limits"
git push -u origin HEAD
gh pr create --title "perf(bench): complete p24 stable-limits" --body-file /tmp/evobyte-p24-pr.md
git status --short
```
