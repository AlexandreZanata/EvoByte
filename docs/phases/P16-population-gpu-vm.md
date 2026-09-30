# P16 — Population-parallel GPU interpreter

**Status:** Complete (2026-09-30).
**Prerequisite:** P15.
**Owner:** AlexandreZanata.

## Objective

Make the population dimension genuinely parallel while retaining the v0
CPU oracle and protected-math semantics. Establish where launch overhead,
memory traffic and opcode divergence limit the RTX 4060 Laptop.

## Scope and ordered work

- Profile the current implementation with P15 timing; preserve its measured
  baseline before changing it. Record CPU dispatch and CUDA kernel activity.
- Remove Python loops over candidates, tensor-to-CPU decoding and repeated
  allocations from population execution. A bounded loop over instruction
  slots is acceptable; population bytecode and input data stay on device.
- Start with vectorized PyTorch and reusable buffers. Evaluate interpreter
  compilation/fusion only when the profile justifies it; Triton/CUDA needs
  measured benefit and conformance evidence. Never compile each candidate.
- Compare arithmetic-only and the full opcode set at 32/256/4096 points and
  increasing batch sizes under measured VRAM limits. Record active program
  lengths and opcode distributions so trivial/NOP-heavy workloads are clear.
- Test population-level parity, malformed operands, NaN/Inf, domain edges,
  constants and mixed-opcode programs against the CPU oracle. Preserve
  opcode version; any semantic change needs an ADR and a new version.

VM execution and its profiling harness only; no evolution rewrite or new
opcode semantics. Optimized code is adopted only for supported workloads.

## Exit gate

```bash
git diff --check
python3 -m pytest tests -q
make verify
python3 benchmarks/cvps.py --grid --provenance --device cuda --output experiments/p16-vm.json
```

Artifact: reproducible CPU/current-GPU/new-GPU comparison including synchronized timings,
peak allocated/reserved VRAM, and 100% conformance against the CPU oracle.

### Measured Artifacts (`experiments/p16-vm.json`)

#### Hardware & Provenance Telemetry
- **GPU:** NVIDIA GeForce RTX 4060 Laptop GPU (7,805 MB VRAM, CUDA 13.0)
- **PyTorch:** 2.14.0+cu130
- **Platform:** Linux 7.1.5-76070105-generic x86_64, Python 3.12.2

#### CVPS Grid: Candidates Verified Per Second
| Candidates (P) | Batch (B) | Latency (ms) | CVPS (progs/s) | Evals/sec | Alloc VRAM | Res VRAM | Conformance |
|---|---|---|---|---|---|---|---|
| 100 | 32 | 56.62 ms | 1,766.2 | 56,519.5 | 0.20 MB | 2.00 MB | **PASS** |
| 500 | 32 | 91.84 ms | 5,444.3 | 174,218.7 | 0.97 MB | 2.00 MB | **PASS** |
| 1000 | 32 | 93.55 ms | 10,689.8 | 342,073.5 | 1.94 MB | 4.00 MB | **PASS** |
| 2000 | 32 | 96.61 ms | 20,701.7 | 662,455.6 | 3.87 MB | 24.00 MB | **PASS** |
| 100 | 256 | 64.46 ms | 1,551.4 | 397,167.0 | 1.61 MB | 24.00 MB | **PASS** |
| 500 | 256 | 86.11 ms | 5,806.6 | 1,486,482.8 | 7.06 MB | 24.00 MB | **PASS** |
| 1000 | 256 | 86.81 ms | 11,519.4 | 2,948,971.8 | 14.14 MB | 28.00 MB | **PASS** |
| 2000 | 256 | 89.90 ms | 22,246.7 | 5,695,153.7 | 28.74 MB | 48.00 MB | **PASS** |
| 100 | 1024 | 58.73 ms | 1,702.7 | 1,743,535.1 | 8.03 MB | 48.00 MB | **PASS** |
| 500 | 1024 | 83.82 ms | 5,965.1 | 6,108,280.9 | 28.47 MB | 48.00 MB | **PASS** |
| 1000 | 1024 | 87.72 ms | 11,399.8 | 11,673,444.0 | 57.20 MB | 82.00 MB | **PASS** |
| 2000 | 1024 | 86.85 ms | 23,026.9 | 23,579,529.8 | 113.24 MB | 146.00 MB | **PASS** |

#### CPU vs GPU Representative Comparison (P=500, B=256)
- **CPU Sequential Throughput:** 139.1 CVPS (3,593.94 ms)
- **GPU Vectorized Throughput:** 6,182.5 CVPS (80.87 ms)
- **GPU Speedup Ratio:** **44.4x**
- **Peak Throughput Achieved:** **23,026.9 CVPS** (and **23.58M evals/sec** at $P=2000, B=1024$)
- **Correctness Parity:** 100% exact numerical match across all edge-cases, domain edges, malformed operands, and NaN/Inf guards.

## Commit & Push (mandatory)

Start from a clean tree on `codex/p16-population-gpu-vm`. Follow the common
commit procedure in [README.md](README.md#commit-and-push-contract), using
this phase's exact reviewed file list and artifact manifest. One completed
micro-task produces one atomic commit; never commit a failed gate.

```bash
git status --short
git diff --check
git diff --cached --check
git commit -m "perf(vm): complete p16 population-gpu-vm"
git push -u origin HEAD
gh pr create --title "perf(vm): complete p16 population-gpu-vm" --body-file /tmp/evobyte-p16-pr.md
git status --short
```
