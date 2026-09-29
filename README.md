# EvoByte

**Massively parallel evolutionary discovery of symbolic programs via ultra-compact bytecode and deterministic verification.**

EvoByte tests one hypothesis:

> If a candidate can be verified orders of magnitude faster than it can be
> rationally discovered, it may be more efficient to generate gigantic numbers
> of extremely cheap candidates and let a trusted verifier select promising
> structures automatically.

No LLM in the hot path. No Chain of Thought. No natural-language tokens.
The main loop is:

```text
GPU ARRAY -> MUTATE -> EXECUTE -> SCORE -> TOP-K -> RECOMBINE -> REPEAT
```

First research domain: **automatic discovery of mathematical formulas from data**
(`F(X) ~= Y`), starting from synthetic rediscovery (`y = x^2 + 3x + 7`).

- License: MIT (100% open source). See [LICENSE](LICENSE).
- Docs index: [docs/README.md](docs/README.md).
- Roadmap: [docs/ROADMAP.md](docs/ROADMAP.md).
- MVP definition: [docs/MVP.md](docs/MVP.md).
- Technical architecture: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
- Quantum track: [docs/quantum/README.md](docs/quantum/README.md) (Q-Forge lab).
- Contribute: [CONTRIBUTING.md](CONTRIBUTING.md).
- Wiki mirror: https://github.com/AlexandreZanata/EvoByte/wiki (mirror of `docs/`).

## Status

P00–P12 have implementation and experiment records. The next planned work
is P15–P20: repair evidence accounting and establish a genuinely parallel,
resident GPU search before resuming P13. P14 scientific evaluation remains
locked behind P13 evidence and P21 reproduction. Million-candidate throughput
is an experimental target, not an achieved result. See the binding dependency
order in [docs/ROADMAP.md](docs/ROADMAP.md).

## Quickstart

```bash
git clone git@github.com:AlexandreZanata/EvoByte.git
cd EvoByte
python3 -m venv .venv && source .venv/bin/activate
make setup
make test
python3 benchmarks/synthetic.py --smoke
```

Hardware probe (safe on any machine; GPU section skips gracefully without CUDA):

```bash
make hw-probe
```

## Repository layout

```text
src/evobyte/      Python reference implementation (CPU-first, GPU-next)
tests/            deterministic unit tests, no network, no GPU required
benchmarks/       synthetic datasets, hardware probe, CVPS harness
experiments/      per-experiment configs + logs (large artifacts git-ignored)
docs/             research specification (source of truth)
docs/phases/      P00-P22 dependency-gated plan, one file per phase
.github/          minimal CI (fast checks only)
```

See [docs/REPOSITORY.md](docs/REPOSITORY.md) for the full contract.

## Performance doctrine

Primary metric: **CVPS — Candidates Verified Per Second.**

We never compare generation counts. We compare **wall-clock time** under equal
compute budget (10 s / 1 min / 10 min / 1 h). See [docs/METRICS.md](docs/METRICS.md).

When in doubt between (A) a more sophisticated architecture and (B) a much
faster architecture that tests many more candidates — **choose B first** and
measure.

## How work proceeds (read before contributing)

1. Pick exactly one phase file in `docs/phases/`.
2. Implement only its scope. Keep changes small and reversible.
3. Run the gates named in that phase (`make test` minimum, never skip a red gate).
4. Commit locally with Conventional Commits (see [docs/COMMITS.md](docs/COMMITS.md)).
5. Push to GitHub on a phase branch and open a PR — **every phase ends with
   a local commit AND a remote push**. Never push directly to `main`.
6. Record decisions in [docs/DECISIONS.md](docs/DECISIONS.md).

Agent rules: [AGENTS.md](AGENTS.md).
