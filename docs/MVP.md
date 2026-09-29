# MVP

**Status:** decision (scope-frozen until P06 passes).

## Objective

Prove the loop `GENERATE -> VERIFY -> SELECT -> EVOLVE -> REPEAT` runs
continuously with measured CVPS — then rediscover two formulas blind.

## Scope (deliberately small)

- 1 variable (+ optional 2nd for `x*y+z` stretch only after first wins).
- 8–16 opcodes (v0 table), programs <= 16 instructions (64 bytes).
- Synthetic datasets only; train/val/hidden/extrapolation splits enforced.
- Random generation (pure + structured) + GPU evaluation + Top-K +
  automatic mutation. **No neural network before this works.**
- CPU reference interpreter as correctness oracle.

## First targets (in order)

1. `y = x^2 + 3x + 7` (MVP gate).
2. `y = sin(x) + x^2` (MVP+ gate).

## Exit thresholds

- `make test` + `make verify` green without GPU.
- CVPS measured on reference hardware with full provenance.
- Target 1 re-found in >= 3/5 seeds (hidden + extrapolation within
  tolerance, size within 2x of minimal).
- No hidden-data leak (audit passes), no NaN/Inf escape (conformance passes).

## Out of MVP

Neural generator, islands, MAP-Elites full grid, constant fitting beyond
the bank, scientific datasets, dashboard beyond logs + Hall of Fame file,
Triton/CUDA custom kernels (unless PyTorch demonstrably bottlenecks).
