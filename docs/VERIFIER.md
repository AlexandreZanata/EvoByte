# Verifier (Level-1 fast + Level-2 strict + cascade)

**Status:** decision.

## Level-1 fast (all candidates)

Fully vectorized, GPU-native when available. Per program:

```text
Y_pred = VM(program, X_batch)          # finite by construction
err    = MSE(Y_pred, Y) + 0.1 * MAE    # robust to outliers
pen    = lambda_c * complexity + lambda_inv * invalid_rate
score  = err + pen                      # lower is better
```

- `complexity` = non-NOP count + 0.5 * distinct-op count (cheap parsimony).
- `invalid_rate` = fraction of points that raised the VM invalid flag.
- Deterministic: fixed reduction order, float32, no data shuffling inside
  a generation.

## Cascade (never spend expensive compute on obvious junk)

```text
S0 validity check (no data)      -> rejects raw-random programs (~0% pass,
                                    structured-random ~100%; measured in P03)
S1 32 points                     -> keep top ~5%
S2 256 points                    -> keep top ~1% of survivors
S3 4096 points                   -> keep top ~10 programs
L2 strict (rare)                 -> full + held-out + extrapolation
```

Batching example: 100k candidates x 256 points in VRAM, kill 99%, then
1k survivors x 10k points, then ~10 x full data. Exact cutoffs are tuned in
P06 with CVPS measurements — the principle (cheap rejection first) is fixed.

## Early termination

After each cascade stage, if `partial_err > k * elite_err` (v0: `k = 4`
after >= 8 points), stop evaluating that candidate and assign the penalty
score. This maximizes cheap rejections.

## Level-2 strict (top ~0.001% only)

CPU-led, may be slow. Runs:

- full train + validation + **hidden test** (never seen by evolution);
- float64 re-evaluation;
- symbolic simplification and equivalence check when ground truth is known
  (synthetic benchmarks);
- extrapolation test (e.g. train `[-10, 10]`, test `[-100, 100]`);
- adversarial points near singularities; dimensional analysis when units exist.

`training error ~= 0` alone is never reported as discovery.

## Degenerate-expression guards

Reject or heavily penalize: constant-only outputs, `NaN/Inf` sources,
single-point memorization patterns, absurd constants (`|c| > 1e6` without
justification), dead instructions (> 50% NOP-equivalent after liveness pass
in L2 only — L1 keeps the cheap count).

## Alternatives considered

- Single full-data evaluation for all: rejected (wastes ~100x budget).
- Learned verifier / surrogate model in L1: rejected for v0 (trust +
  determinism risk); revisit only as a measured ablation.
- float64 everywhere: rejected (halves throughput for no L1 benefit).
