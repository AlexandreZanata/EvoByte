# P00 — Foundation, hardware probe, reproducibility harness

**Status:** Building (base commit in this push).
**Goal:** a clean, reproducible, measurable starting point. No speed claims
without provenance from here on.

## Objective

Stand up the repo skeleton, fast CI, hardware reporter, synthetic smoke
dataset, and run-record convention.

## Scope

In: `pyproject.toml`, `Makefile`, `src/evobyte/__init__.py`, `metrics.py`
stub with timing helpers, `benchmarks/hw_probe.py`, `benchmarks/synthetic.py`
(smoke only), `tests/` hello + determinism check, `.github/workflows/quick.yml`,
`experiments/README.md`.
Out: bytecode semantics, VM execution, any GPU kernel.

## Tasks

1. `chore(project): wire layout, make targets, gitignore, templates`.
2. `feat(bench): add hw_probe reporting GPU/driver/CUDA/VRAM or graceful skip`.
3. `feat(bench): add synthetic smoke dataset (x^2+3x+7, seeded, hashed)`.
4. `ci(quick): add fast workflow (ruff + pytest + smoke, no GPU)`.

## Exit gate (must all pass)

```bash
git diff --check
python3 -m pytest tests -q
python3 benchmarks/synthetic.py --smoke
python3 benchmarks/hw_probe.py
```

Artifact: `hw_probe` JSON + smoke dataset hash printed; both reproducible
across two runs with the same seed.

## Risks

- GPU absent in CI — probe must skip gracefully, never fail the build.
- Over-scaffolding — keep files minimal; no speculative modules.

## Commit & Push (mandatory for this phase)

Run after the exit gate is green. Never push to `main` directly; use a
phase branch and open a PR:

```bash
git status --short
git add pyproject.toml Makefile .gitignore .gitmessage src benchmarks tests experiments .github docs README.md LICENSE AGENTS.md CONTRIBUTING.md SECURITY.md CITATION.cff
git commit -m "chore(project): stand up P00 foundation and hw probe"
git push -u origin phase-00-foundation-hw-probe
gh pr create --title "chore(project): stand up P00 foundation and hw probe" --body "P00 exit gate green. Closes #<issue>."
```

Merge only with green CI and a clean tree.
