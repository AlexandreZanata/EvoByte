# P12 — Micro neural generator

**Status:** Done.
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

| Method | Success Rate | Mean Train MSE | Mean Hidden MSE | Mean Extrap MSE | Mean CVPS |
|---|---|---|---|---|---|
| **Random Search** | 0.0% (0/5) | 49.55071 | 49.16120 | 245.06421 | 1011.6 |
| **Genetic Evolution** | **40.0% (2/5)** | **5.31195** | **5.09780** | **817.64567** | **1006.0** |
| **Neural Standalone** | 0.0% (0/5) | 58.97506 | 57.05634 | 6704.95076 | 851.7 |
| **Neural + Genetic Hybrid** | 40.0% (2/5) | 13.47213 | 12.98033 | 1337.87829 | 762.4 |

**Ruling:** DROP from main loop (documented in `docs/adr/ADR-0010-neural-generator.md` and Decision D010). Genetic search remains superior in wall-clock throughput (1006 CVPS vs 762-852 CVPS) and solution error (5.31 vs 13.47-58.98 MSE).

**Independent verification (2026-09-29, RTX 4060 Laptop GPU, commit `1e3603e`):**
re-ran the full exit gate (`--budget 10min --seeds 5`). Deterministic methods
reproduced bit-identically (random 49.55071, genetic 5.31195/5.09780/817.64567);
neural/hybrid varied within the same conclusion (neural 0/5, hybrid 1/5,
genetic still best at 2/5 with ~1004 CVPS). DROP ruling confirmed.

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
