# P12 — Micro neural generator

**Status:** Proposed.
**Goal:** test whether a tiny bytecode model adds anything per wall-clock second.

## Objective

Train a 100K–5M param sampler on elite archives:
`P(next_instruction | elite_prefix)` or whole-chromosome sampler, pipeline
`elites -> micro-generator -> candidates -> mutation -> verification`,
under a strict VRAM cap. Mandatory comparison: random vs genetic vs neural
vs neural+genetic at equal budget.

## Scope

In: `generator.py` (<= 5M params, VRAM-capped), training on elites only,
4-way A/B harness.
Out: LLMs, natural-language conditioning, > 5M params without ADR.

## Tasks

1. `feat(generator): add micro sampler with VRAM cap`.
2. `feat(bench): 4-way comparison (random/genetic/neural/neural+genetic)`.
3. `docs(adr): record keep-or-drop ruling with numbers`.

## Exit gate

```bash
git diff --check
python3 -m pytest tests/test_generator.py -q
python3 experiments/p12_generator_ab.py --budget 10min --seeds 5
```

Artifact: 4-way table; generator stays only if it beats genetic per
wall-clock second without hurting CVPS beyond its cap. Negative results are
valid and recorded.

## Risks

- VRAM theft — cap enforced; CI asserts param count + resident size.

## Commit & Push (mandatory for this phase)

```bash
git status --short
git add src/evobyte/generator.py experiments/p12_generator_ab.py tests/test_generator.py docs/phases/P12-neural-generator.md
git commit -m "feat(generator): add micro bytecode sampler with gate"
git push -u origin phase-12-neural-generator
gh pr create --title "feat(generator): add micro bytecode sampler with gate" --body "P12 exit gate green. Closes #<issue>."
```
