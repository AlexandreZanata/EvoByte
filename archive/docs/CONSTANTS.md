# Constants strategy

**Status:** decision.

Symbolic regression lives or dies on constants (`y = 3.14159 x^2 + 0.173 x`).
Random floats will never hit them reliably. Separate **structure search**
from **coefficient fitting**.

## Ladder (in order)

1. **v0 — quantized bank (P01–P08):** 16 fixed constants via `CSEL`
   (see BYTECODE). Zero fitting cost; measures whether structure search
   works at all.
2. **P11a — constant slots + local search:** up to 4 tunable slots per
   program; hill-climb / Gaussian perturbation on promoted candidates only
   (never in the full-population hot path).
3. **P11b — least squares for linear head:** if program output is linear in
   slots, solve closed-form on S3 candidates.
4. **Later — CMA-ES / small gradient steps:** only on L2 finalists, with
   wall-clock budget accounting (fitting cost counts against the method).

## Rules

- Fitting budget is part of the method's cost. A method that fits 10x more
  must be 10x better to win.
- Absurd constants (`|c| > 1e6`, precision beyond data noise) are penalized
  in fitness and flagged in L2.
- Every fitted constant is logged with its optimizer, steps, and validation
  delta — no silent "magic numbers".

## Benchmark Evidence (P11)

Measured across 5 seeds on constant-heavy targets with non-bank floats (`0.173`):
- `y = 3.14159 x^2 + 0.173 x`: Cond A MSE = 1.71072, Cond B MSE = 0.09264 (18.5x gain).
- `y = 3.14159 x + 0.173`: Cond A MSE = 0.06481, Cond B MSE = 0.00000 (>10000x gain).
All fitting costs (optimizer steps and milliseconds) are explicitly tracked and billed.
