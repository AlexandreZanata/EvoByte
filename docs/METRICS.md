# Metrics

**Status:** decision.

## Primary: CVPS

**CVPS = Candidates Verified Per Second** (through Level-1 S1 or deeper).
Report with: population, batch, cascade cutoffs, hardware, driver, commit,
seed, dataset hash. Never report CVPS without that tuple.

## Supporting

- candidates generated/sec, evaluated/sec (per cascade stage);
- bytes/candidate (v0: 64);
- evaluations/joule (when power telemetry available; else omit, never invent);
- GPU utilization %, VRAM used/total;
- verifier throughput per stage + early-termination kill rate;
- time-to-quality (seconds to reach error thresholds on named targets);
- population diversity (mean pairwise behavioral distance + archive coverage);
- improvement/hour (best-fitness delta per wall-clock hour).

## Doctrine

- Compare **wall-clock time** under equal budget (10 s / 1 min / 10 min / 1 h),
  never generation counts.
- No invented numbers. `benchmarks/` measures; docs record hardware + commit.
- A metric without a reproduction command is a rumor. Every metric names its
  harness (`make bench`, `make hw-probe`, experiment config hash).

## Recommended Cascade Batching & VRAM Table (8 GB budget / 7500 MB active)

Tuned in P06 via `src/evobyte/batching.py` and `benchmarks/cvps.py --tune`:

| Stage | Role | Target Candidates | Points | Safe Chunk Size | Active VRAM (est) | Expected Kill % |
|---|---|---|---|---|---|---|
| **S1** | Coarse screening | 100,000 | 256 | 480,000 | ~117 MB | 99.0% |
| **S2** | Fine discrimination | 1,000 | 4,096 | 30,000 | ~188 MB | 99.0% |
| **S3** | Full verification | 10 | 10,000 | 12,288 | ~4.6 MB | 0.0% |

All stages run under OOM-safe dynamic fallback: memory pressure automatically halves the chunk size and clears the cache without interrupting the run.
