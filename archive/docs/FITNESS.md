# Fitness (multi-objective)

**Status:** decision.

## Formula (v0)

```text
fitness = w_err * norm_err + w_c * complexity + w_s * instability
          - w_n * novelty + w_v * validation_gap
```

Lower is better. Default weights (tuned in P08, never hand-waved):

- `w_err = 1.0`, `norm_err = MSE + 0.1 * MAE` on current cascade stage.
- `w_c = 1e-3`: parsimony — if two programs explain data equally, prefer
  the smaller (non-NOP count + 0.5 * distinct ops).
- `w_s = 1.0`: instability = invalid_rate + overflow_rate + variance blowup
  across batches.
- `w_n = 0.05`: novelty bonus (behavioral distance, see EVOLUTION).
- `w_v = 0.5`: `max(0, val_err - train_err)` measured on promotion to S3/L2.

## Penalties (hard)

- Any NaN/Inf escaping the VM: automatic worst score (should be impossible;
  treated as VM bug if observed).
- Dead instructions, useless-op chains (`ADD 0`, `MUL 1` loops), absurd
  constants: counted in complexity, surfaced in L2 simplification.
- Memorization signatures (near-zero train + large validation gap): blocked
  from Hall of Fame even with good train fitness.

## Alternatives considered

- Pure MSE: rejected — breeds bloated, unstable, memorizing programs.
- Pareto-front only: deferred — scalarized fitness is faster to rank on GPU
  (top-K); explicit Pareto analysis lives in L2/archive tooling.
- Learned fitness: rejected — verifier must stay deterministic and trusted.
