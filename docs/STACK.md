# Technology stack

**Status:** decision.

## Ladder (use the cheapest rung that meets the CVPS target)

| Layer | Choice | Why |
|---|---|---|
| Language | Python 3.11+ | ecosystem, fast iteration; hot path stays in array ops |
| CPU arrays | NumPy | deterministic reference, zero extra toolchain |
| GPU arrays | PyTorch (`src/evobyte/vm_torch.py`, resident tensor ops) | resident tensors, mature CUDA, easy profiling (P05 verified) |
| Optional GPU kernels | Triton, then CUDA C++ | only with measured PyTorch bottleneck + determinism proof |
| Rejected for hot path | CuPy-as-required, per-candidate `torch.compile`, AST/sympy in L1 | extra deps / compile stalls / parse cost |
| Tests | pytest | hermetic, no network/GPU required |
| Lint | ruff | fast, single tool |

Standard-library-first for everything else. A new dependency needs a
`DECISIONS.md` entry with alternatives and measured justification.

## Hot-path bans (enforced by review)

Python `for` over candidates, per-candidate objects/allocations, strings,
AST parsing, per-candidate compilation, CPU<->GPU sync per candidate,
needless copies, LLM APIs.

## Hardware

- Reference: NVIDIA RTX 4060 Laptop, 8 GB VRAM.
- `benchmarks/hw_probe.py` records GPU, driver, CUDA, VRAM, CPU, RAM.
- All performance claims cite: hardware + driver + commit + seed +
  dataset hash. No exceptions.
