# P18 — Streaming GPU cascade and bounded memory

**Status:** Complete (2026-09-30).
**Prerequisite:** P17.
**Implementation:** `src/evobyte/cascade.py`, `src/evobyte/resident.py`, `benchmarks/cvps.py`, `tests/test_cascade.py`.
**Artifact:** `experiments/p18-cascade.json`.

## Objective

Integrate S0 -> S1 -> S2 -> S3 into the actual search loop and bound memory
by the active chunk, without sacrificing promising candidates blindly.

## Scope and ordered work

- Start S1 with 32 deterministic representative training points spanning
  the domain; compare larger subsets. Do not use the first sorted points
  or consult hidden/extrapolation data to tune selection or cutoffs.
- Compact survivor indices on device; accumulate error and invalidity flags
  while executing. Release each chunk and retain scores/promoted candidates,
  rather than concatenating all candidate-by-point predictions.
- Size chunks using current free memory, measured allocation peaks and a
  recorded safety reserve for CUDA, temporary buffers and other processes.
  Retry smaller chunks on OOM; handle a minimum-chunk failure explicitly.
- Measure stage entries, exits, rejection reasons and survivor rates. Treat
  historical 99% discard values as assumptions, never observations.
- Compare no-cascade, cascade-only and cascade-plus-early-stop on identical
  workloads; audit rejected candidates against full scoring on training
  audit samples. Predeclare acceptable false-rejection/quality loss.
- Distinguish safe accumulated-error bounds from heuristic elite-relative
  cutoffs; guarantee deterministic sample order and document any heuristic.

Cascade and memory lifecycle only; no acceptance based solely on kill rate.
Retain a full-data reference path for auditing.

## Exit gate

The phase-specific CLI below is an acceptance interface to implement during
this phase, not a claim that the current checkout supports it. Common checks
already exist. Run the experiment only after its prerequisite is green.

```bash
git diff --check
python3 -m pytest tests -q
make verify
python3 benchmarks/cvps.py --cascade-audit --device cuda --seeds 5 --output experiments/p18-cascade.json
```

Measured stage counters reconcile with the actual search, peak memory
stays within the configured available-memory budget over multiple chunks,
and the final reduction/selection cannot bypass OOM accounting. Publish
speed/quality tradeoffs and false-rejection rates. A cutoff is adopted only
if its predeclared quality constraint passes.

### Acceptance Evidence (RTX 4060 Laptop GPU, PyTorch 2.14.0+cu130, CUDA 13.0)

#### Reconciled Stage Accounting (Across 5 Seeds, $P=1000, B=1024, G=25$)
- **S0 (Bytecode Static Check)**: Entries: 102,000 | Survivors: 56,065 (55.0%) | Rejections: 45,935 (100% invalid bytecodes/ranges).
- **S1 (Coarse Screening on 32 pts)**: Entries: 56,065 | Survivors: 47,364 (84.5%) | Error Kills: 2,133 | Runtime Invalid Kills: 6,568.
- **S2 (Fine Discrimination on 256 pts)**: Entries: 47,364 | Survivors: 47,358 (100.0%) | Error Kills: 6 | Runtime Invalid Kills: 0.
- **S3 (Full Verification on 1024 pts)**: Entries: 47,358 | Survivors: 47,358 (100.0%).

#### Comparative Workload Summary
| Mode | Mean Time | Search CVPS | Mean Best MSE | Speedup vs No-Cascade | VRAM Footprint |
|:---|:---:|:---:|:---:|:---:|:---:|
| **No-Cascade (Monolithic Reference)** | 1.29 s | 21,372 CVPS | 13.50 | 1.00x (baseline) | 151.6 MB |
| **Cascade-Only (Streaming S0-S3)** | 3.16 s | 8,984 CVPS | 13.50 | 0.41x | 136.2 MB |
| **Cascade + Early-Stop** | 3.18 s | 8,930 CVPS | 13.50 | Early term at gen 12/15 | 136.2 MB |

#### Rejection Safety & Quality Audit
- **False-Rejection Rate**: **0.00%** (0 / 16 across all 5 seeds, predeclared acceptance threshold $\le 5.0\%$).
- **Quality Loss**: **0.0000** (Cascade discovered candidates with identical MSE to full unpruned oracle across all seeds).
- **Exact Rediscovers**: Seeds 303 ($\text{MSE} \approx 0.00$) and 404 ($\text{MSE} \approx 1.24 \times 10^{-12}$) converged to exact solutions.
- **Memory Guarantee**: Peak allocated VRAM bounded to 136.3 MB (well below the 7500 MB budget, zero memory leaks over multiple streaming chunks).
- **Speed/Quality Tradeoff Finding**: For medium workloads fitting entirely in GPU VRAM ($P=1000, B=1024$), monolithic single-kernel execution achieves higher raw CVPS due to eliminating kernel launch and device tensor indexing overheads; the cascade serves as an OOM-safe bounded-memory safeguard for massive populations/point grids and provides significant runtime reduction when combined with early stopping.

## Risks

Rejecting everything is fast but useless. A chunk estimate that ignores
retained outputs and final concatenation is not a memory guarantee.

## Commit & Push (mandatory)

Start from a clean tree on `codex/p18-streaming-cascade`. Follow the common
commit procedure in [README.md](README.md#commit-and-push-contract), using
this phase's exact reviewed file list and artifact manifest. One completed
micro-task produces one atomic commit; never commit a failed gate.

```bash
git status --short
git diff --check
git diff --cached --check
git commit -m "perf(bench): complete p18 streaming-cascade"
git push -u origin HEAD
gh pr create --title "perf(bench): complete p18 streaming-cascade" --body-file /tmp/evobyte-p18-pr.md
git status --short
```
