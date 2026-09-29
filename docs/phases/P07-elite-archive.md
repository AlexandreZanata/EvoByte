# P07 — Elite archive + checkpoints + resume

**Status:** Proposed.
**Goal:** progress is never lost; restarts continue exactly.

## Objective

Add host-side archive (`archive.py`, SQLite/Parquet): elite rows per
[EVOLUTION.md](../EVOLUTION.md) schema, Hall of Fame writer, checkpoint
(RNG + generation + population sample + archive pointer) and
resume-equivalence test.

## Scope

In: archive store, hash/dedup, checkpoint/resume, Hall of Fame file.
Out: novelty, islands, neural models.

## Tasks

1. `feat(archive): add elite store with full provenance rows`.
2. `feat(archive): add checkpoint and resume with equivalence test`.
3. `feat(dashboard): write Hall of Fame JSONL (memorizers ineligible)`.

## Exit gate

```bash
git diff --check
python3 -m pytest tests/test_archive.py -q
python3 -m evobyte.archive --selftest-resume
```

Artifact: resume-equivalence log (same seed, continued == uninterrupted)
+ sample Hall of Fame entry.

## Risks

- Silent schema drift — archive rows carry `OPCODE_VERSION`; reader keeps v0.

## Commit & Push (mandatory for this phase)

```bash
git status --short
git add src/evobyte/archive.py tests/test_archive.py hall_of_fame/fame.jsonl docs/EVOLUTION.md docs/DASHBOARD.md docs/phases/P07-elite-archive.md
git commit -m "feat(archive): add elite archive with resume"
git push -u origin phase-07-elite-archive
gh pr create --title "feat(archive): add elite archive with resume" --body "P07 exit gate green. Closes #<issue>."
```
