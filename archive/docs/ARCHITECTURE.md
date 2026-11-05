# Architecture

**Status:** decision (binding until changed via `DECISIONS.md` + doc update).

## Overview

```text
                    +-------------------+
                    |   DATASET (VRAM)  |  train / val / hidden (hidden never in loop)
                    +--------+----------+
                             |
GENERATE (random / genetic / neural) -> POPULATION (VRAM, compact bytecode)
                             |
                    +--------v----------+
                    | CASCADE VERIFIER  |  S0 validity -> S1 32 pts -> S2 256 pts
                    | Level-1 fast      |  -> S3 4k pts, early termination
                    +--------+----------+
                             | top-K + novelty
                    +--------v----------+
                    | SELECT + ARCHIVE  |  elite archive, MAP-Elites, islands
                    +--------+----------+
                             |
                    +--------v----------+
                    | EVOLVE (mutate /  |  GPU whenever feasible
                    |  crossover /      |
                    |  migrate / inject)|
                    +--------+----------+
                             | survivors -> next generation
                    +--------v----------+
                    | LEVEL-2 STRICT    |  full data, held-out, extrapolation,
                    | (rare, CPU-led)   |  simplification, equivalence
                    +-------------------+
```

CPU owns experiment control, elite persistence, logs, and Level-2 checks.
GPU owns population, data, mutation, execution, and selection whenever viable.

## Memory map (RTX 4060 Laptop, 8 GB VRAM)

Budget priority: population > data > execution buffers > results > elites.

| Candidate size | 1M candidates | 4M candidates | 16M candidates |
|---|---|---|---|
| 16 B | 16 MB | 64 MB | 256 MB |
| 32 B | 32 MB | 128 MB | 512 MB |
| 64 B | 64 MB | 256 MB | 1024 MB |
| 128 B | 128 MB | 512 MB | 2048 MB |

v0 choice: **64 bytes per candidate** (16 instructions x 4 bytes). That is
64 MB per 1M candidates for bytecode only. This does not establish runtime
headroom on 8 GB: `[1M, 8, 256]` float32 registers alone need 8.192 GB
(decimal), before predictions, flags, temporaries and CUDA overhead. P18
uses measured streaming chunks, not a bytecode-only population budget. Smaller (32 B) is an explicit P05 ablation; larger (128 B) needs
measured justification.

VRAM layout (logical):

- `POP`: `[N, 16]` uint32 instructions (N = population).
- `DATA`: `[D, F+1]` float32 inputs + target (stays resident).
- `REGS`: current materialized layout `[chunk_N, R, points]` float32
  (R = 8 in v0); a fused implementation may keep point-local registers on chip.
- `PRED`: `[N]` or `[N, batch]` float32 predictions.
- `SCORE`: `[N]` float32 fitness + `[N]` uint8 validity flags.
- `ELITE`: small pinned ring (<= 10k) + host-side archive.

## Module map (`src/evobyte/`)

| Module | Owns | Must not import |
|---|---|---|
| `bytecode.py` | opcode table, encode/decode, `OPCODE_VERSION` | torch, strings in hot path |
| `vm.py` | CPU reference interpreter (NumPy, deterministic) | LLM APIs, AST |
| `verifier.py` | Level-1 scoring, cascade, early stop | hidden test split |
| `evolution.py` | selection, mutation, crossover, MAP-Elites, islands | Level-2 logic |
| `archive.py` (P07) | elite persistence, hash, resume | GPU-only code |
| `constants.py` (P11) | constant banks + local search | symbolic libs in L1 |
| `generator.py` (P12) | micro-model bytecode sampler | > 5M params without ADR |
| `metrics.py` | CVPS, diversity, timing | I/O in hot path |

Strict verifier, dashboard, and neural generator do not exist before their
phases. Do not pre-build them.

## Data splits (binding)

- `train`: visible to evolution.
- `validation`: visible for model/hyperparameter choice, not for per-step selection.
- `hidden test`: never touched by evolution; Level-2 only.
- `extrapolation`: e.g. train `x in [-10, 10]`, test `x in [-100, 100]`.

Any leak of hidden data into the loop is a research-integrity failure and
blocks release.

## Alternatives considered

- x86/CUDA strings as candidate IR — rejected: compile/sync overhead.
- Tree/AST with parsing per candidate — rejected: parse cost dominates.
- Single-level verifier — rejected: wastes budget on obvious junk.
- Giant neural generator first — rejected: VRAM theft + unproven benefit.

See [STACK.md](STACK.md) for the technology ladder (NumPy -> PyTorch ops ->
Triton/CUDA only with measurement).
