# Agent rules (mandatory)

These rules apply to any AI agent or human contributor acting in this repository.

## 1. Execution and Git

- **One micro-task at a time:** do exactly one task per cycle. Do not accumulate
  tasks, skip steps, or expand scope.
- **Atomic commits:** each finished task produces exactly one atomic commit
  after all its gates pass.
- **Commit format:** Conventional Commits (`type(scope): description`), per
  `docs/COMMITS.md`. First line <= 72 chars whenever possible.
- **Local commit + remote push, every phase:** each phase file in
  `docs/phases/` ends with an explicit Commit & Push block. Follow it:
  commit locally, push the phase branch to `origin`, open/update a PR.
  Never push directly to `main`; never use `--force`, `--no-verify`.
- **Clean tree:** confirm `git status --short` is clean before starting and
  after finishing.
- **No secrets:** never commit credentials, tokens, private data, or
  production dumps.
- **Stop rule:** if any test, build, or gate fails, or requirements are
  unclear — stop. Do not commit. Do not weaken a test or threshold to fit
  an implementation.

## 2. Architecture (binding until changed via ADR)

- CPU reference first: pure deterministic Python + NumPy, no strings/AST
  parsing in the hot path.
- GPU next: dataset and population stay in VRAM; mutation, execution,
  selection on GPU whenever feasible (PyTorch ops first, Triton/CUDA only
  with measured justification).
- No natural language in the main loop: no prompts, sentences, JSON, LLM
  APIs, or Chain of Thought in `GENERATE -> VERIFY -> SELECT -> EVOLVE`.
- Fixed opcode versioning: any bytecode change bumps `OPCODE_VERSION` and
  keeps the old interpreter for reproducibility.

## 3. Evidence over claims

- Never invent performance numbers. Measure with `benchmarks/` and record
  hardware, driver, commit, seed, dataset hash.
- No false positives: a phase is done only when its exit gate artifact runs
  and is measured. Documentation promises must be verifiable; code promises
  must be tested.
- Prefer editing existing files over creating new ones. Keep changes small,
  idiomatic, with error handling. No TODOs, stubs, or placeholders.

## 4. Validation gates

Before any commit, at minimum:

```bash
git diff --check
git status --short
python3 -m pytest tests -q
```

Full gates live in `Makefile` (`lint`, `test`, `verify`). A failing gate
blocks commit and push — never defer a known failure to a later phase.
