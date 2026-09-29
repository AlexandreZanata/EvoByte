# P02 — CPU reference interpreter

**Status:** Done (2026-09-29 — gate green: 12/12 VM tests, 42/42 full suite,
oracle vectors green, fuzz run 1k random programs x edge inputs = 0 NaN/Inf;
see commit `feat(vm)` below).
**Goal:** deterministic oracle all future backends must match.

## Objective

Implement `src/evobyte/vm.py` (NumPy, float32, fixed order) per
[VM.md](../VM.md): total termination in <= 16 steps, safe-math on every op
(no NaN/Inf escape), `invalid` flags, `regs[7]` output convention.

## Scope

In: CPU interpreter + conformance vectors (edge inputs per opcode +
`x+1` and `x^2+3x+7` end-to-end).
Out: batching optimization, GPU, scoring.

## Tasks

1. `feat(vm): add deterministic CPU reference interpreter`.
2. `test(vm): add per-opcode edge conformance (0, tiny, huge, NaN/Inf in)`.
3. `test(vm): add end-to-end x+1 and x^2+3x+7 vectors`.

## Exit gate

```bash
git diff --check
python3 -m pytest tests/test_vm.py -q
```

Artifact: oracle vectors green; fuzz run (1k random programs x edge inputs)
produces zero NaN/Inf outputs (log the command + seed in the PR).

## Risks

- Nondeterministic reduction order — fix loop order, pin float32, test it.

## Commit & Push (mandatory for this phase)

```bash
git status --short
git add src/evobyte/vm.py tests/test_vm.py docs/VM.md docs/phases/P02-cpu-interpreter.md
git commit -m "feat(vm): add deterministic CPU reference interpreter"
git push -u origin phase-02-cpu-interpreter
gh pr create --title "feat(vm): add deterministic CPU reference interpreter" --body "P02 exit gate green. Closes #<issue>."
```
