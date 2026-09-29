# Repository layout contract

**Status:** decision.

```text
README.md            handoff: vision, quickstart, gates, layout
LICENSE              MIT
AGENTS.md            mandatory agent/human rules
CONTRIBUTING.md      PR/branch/commit workflow
SECURITY.md          reporting + rules
CITATION.cff         citation metadata
pyproject.toml       package + deps (numpy, torch; dev: pytest, ruff)
Makefile             setup | test | lint | verify | bench | hw-probe
.gitmessage          commit template
src/evobyte/         reference implementation (CPU-first)
  __init__.py        version + OPCODE_VERSION re-export
  bytecode.py        opcode table, encode/decode, validity
  vm.py              CPU reference interpreter (NumPy)
  verifier.py        Level-1 scoring, cascade, early stop
  evolution.py       selection / mutation / crossover basics
  metrics.py         CVPS + diversity + timing
tests/               hermetic unit tests (no GPU/network)
benchmarks/
  synthetic.py       dataset generator + smoke/bench harness
  hw_probe.py        hardware/driver reporter
experiments/
  README.md          per-experiment log convention (artifacts git-ignored)
docs/                specification (source of truth)
docs/phases/         P00-P14 executable plans
.github/workflows/
  quick.yml          fast CI: ruff + pytest + smoke (no GPU)
```

Rules:

- `src/evobyte/` stays dependency-light (`numpy` + `torch` only).
- `tests/` must pass without CUDA and without network.
- Large artifacts (`runs/`, `checkpoints/`, datasets) are git-ignored.
- `docs/` promises must be verifiable; code promises must be tested.
- New top-level directories need a `DECISIONS.md` entry.
