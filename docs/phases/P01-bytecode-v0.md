# P01 — Bytecode v0 frozen

**Status:** Proposed.
**Goal:** freeze `OPCODE_VERSION = 0` with codec + validity tests. No execution yet.

## Objective

Implement `src/evobyte/bytecode.py` per [BYTECODE.md](../BYTECODE.md):
16 instr x 4 B = 64 B, 8 registers, 16 opcodes, 16-entry const bank, S0
validity rules, encode/decode helpers, `OPCODE_VERSION`.

## Scope

In: codec, validity checker, VRAM-size table test, human-readable decoder
(for logs only, never hot path).
Out: VM execution, scoring, GPU code.

## Tasks

1. `feat(bytecode): add opcode table v0 and const bank`.
2. `feat(bytecode): add encode/decode and S0 validity`.
3. `test(bytecode): cover all opcodes, invalid registers, NOP padding, size math`.

## Exit gate

```bash
git diff --check
python3 -m pytest tests/test_bytecode.py -q
python3 -c "from evobyte.bytecode import OPCODE_VERSION; assert OPCODE_VERSION == 0"
```

Artifact: frozen spec + passing codec tests; doc table matches code table
(review checklist in PR).

## Risks

- Spec/code drift — PR must show spec bytes == code bytes.

## Commit & Push (mandatory for this phase)

```bash
git status --short
git add src/evobyte/bytecode.py tests/test_bytecode.py docs/BYTECODE.md docs/phases/P01-bytecode-v0.md
git commit -m "feat(bytecode): freeze opcode v0 codec and validity"
git push -u origin phase-01-bytecode-v0
gh pr create --title "feat(bytecode): freeze opcode v0 codec and validity" --body "P01 exit gate green. Closes #<issue>."
```
