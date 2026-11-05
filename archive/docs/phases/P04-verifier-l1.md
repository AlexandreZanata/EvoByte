# P04 — Level-1 verifier + cascade + early stop

**Status:** Done (2026-09-29 — gate green: 8/8 verifier tests, 58/58 full suite;
cascade table: S0 25.0% killed, S1 93.3% killed, S3 10/200 survived (5.0%);
hidden audit clean (0 hits in src/); see commit `feat(verifier)` below).
**Goal:** vectorized scoring that never wastes full-data compute on junk.

## Objective

Implement `src/evobyte/verifier.py` per [VERIFIER.md](../VERIFIER.md):
`MSE + 0.1*MAE + complexity + invalid` penalties, S0->S1(32)->S2(256)->
S3(4096) cascade, early termination (`partial_err > 4x elite_err` after
>= 8 points), train/val split discipline (hidden never imported).

## Scope

In: batched NumPy scorer, cascade controller, early-stop accounting
(kill rate per stage), anti-memorization gap term.
Out: GPU port, L2 strict, constant fitting.

## Tasks

1. `feat(verifier): add vectorized L1 scorer with safe penalties`.
2. `feat(verifier): add cascade controller with early termination`.
3. `test(verifier): prove junk dies in S1/S2; elites survive; hidden untouched`.

## Exit gate

```bash
git diff --check
python3 -m pytest tests/test_verifier.py -q
python3 benchmarks/synthetic.py --cascade
```

Artifact: cascade table (survival %, score cost per stage) + hidden-leak
audit (`grep -r hidden` shows only L2/test fixtures).

## Risks

- Hidden import in L1 — audit blocks merge on any hit outside fixtures.

## Commit & Push (mandatory for this phase)

```bash
git status --short
git add src/evobyte/verifier.py tests/test_verifier.py benchmarks/synthetic.py docs/VERIFIER.md docs/FITNESS.md docs/phases/P04-verifier-l1.md
git commit -m "feat(verifier): add L1 cascade scorer with early stop"
git push -u origin phase-04-verifier-l1
gh pr create --title "feat(verifier): add L1 cascade scorer with early stop" --body "P04 exit gate green. Closes #<issue>."
```
