# P03 — Random generators

**Status:** Proposed.
**Goal:** baselines A (pure) and B (structured) with measured validity rates.

## Objective

Add generation primitives (seeded RNG, never global): uniform-bytes sampler
+ S0 filter (A), opcode-aware sampler respecting register/validity priors (B).
Report: programs/sec + S0 pass rate for each.

## Scope

In: `src/evobyte/evolution.py` generation half (sampling only), generator
benchmark script, seed discipline.
Out: selection, crossover, novelty, neural models.

## Tasks

1. `feat(evolution): add pure and structured random samplers`.
2. `test(evolution): assert seeded reproducibility + validity bounds`.
3. `feat(bench): report gen/sec and S0 pass rate for A vs B`.

## Exit gate

```bash
git diff --check
python3 -m pytest tests/test_evolution.py -q
python3 benchmarks/synthetic.py --generators
```

Artifact: A-vs-B table (gen/sec, S0%) with seed + commit in the PR body.

## Risks

- Unseeded RNG — fail review if any `np.random` default path remains.

## Commit & Push (mandatory for this phase)

```bash
git status --short
git add src/evobyte/evolution.py tests/test_evolution.py benchmarks/synthetic.py docs/phases/P03-random-generators.md
git commit -m "feat(evolution): add pure and structured random generators"
git push -u origin phase-03-random-generators
gh pr create --title "feat(evolution): add pure and structured random generators" --body "P03 exit gate green. Closes #<issue>."
```
