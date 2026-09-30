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

## Historical P06 batching estimates (pending P15/P18 audit)

These legacy figures are retained for traceability, not recommended safe
limits or measured rejection rates. The harness uses configured kill rates,
an analytical memory estimate and a smaller S1 measurement population than
its displayed target. P15 audits provenance; P18 replaces the defaults with
measured peak memory and actual survivor accounting.

| Stage | Role | Target Candidates | Points | Safe Chunk Size | Active VRAM (est) | Expected Kill % |
|---|---|---|---|---|---|---|
| **S1** | Coarse screening | 100,000 | 256 | 480,000 | ~117 MB | 99.0% |
| **S2** | Fine discrimination | 1,000 | 4,096 | 30,000 | ~188 MB | 99.0% |
| **S3** | Full verification | 10 | 10,000 | 12,288 | ~4.6 MB | 0.0% |

Current chunk fallback does not guarantee the final retained predictions
or concatenation fit. P18 must bound the entire lifecycle and handle terminal
OOM explicitly. Do not claim an unconditional no-crash guarantee.

## Required measurement distinctions (P15 onward)

- Generated/s and S0-valid/s measure proposal volume, not verification.
- VM-only programs/s measures execution without scoring and is not CVPS.
- S1 CVPS counts actual valid candidates with predictions AND score completed
  on the declared points; record stage counts and unique/repeated counts.
- Full-cascade CVPS counts S3 completions; strict L2 completions are separate.
- End-to-end S1 CVPS divides S1 completions by full search wall time including
  generation, execution, selection, mutation, transfers and online fitting.
- Candidate-point evaluations/s counts data-point work, not distinct models.

Define uniqueness window and method (exact bytecode/constant hash or labelled
estimate); byte-distinct programs are not necessarily distinct functions.
Record accounting overhead and sample-based behavioral diversity separately.
Every rate names its numerator, timer boundaries, sample size and workload.
Observe CUDA completion before stopping timers; include warmup/setup cost in
cold-start reporting. Temperature/clocks and peak allocated/reserved memory
must be recorded when available, not inferred from the GPU model name.

P20 tests the million-S1 target; no historical rate implies it is achieved.
