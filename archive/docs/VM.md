# Minimal math VM

**Status:** decision.

## Contract

- Deterministic: same `(program, inputs)` -> same outputs, bit-identical on
  CPU reference (float32, fixed op order, no data-dependent branches).
- Total: every program terminates in exactly `<= 16` steps; no loops,
  no jumps, no dynamic allocation in v0.
- Safe: NaN/Inf/overflow/domain errors can never escape. They set an
  `invalid` flag and yield a finite penalty value (see VERIFIER).
- Text-free: the hot path takes `uint8/uint32` arrays, never strings or ASTs.

## Semantics

```text
regs[0..7] = 0; regs[0] = x0; regs[1] = x1 (if present)
invalid = 0
for each instr in program (16 max):
  if op == NOP: continue
  (dst, a, b) = decode(instr)
  regs[dst], flag = safe_apply(op, regs[a], regs[b])
  invalid |= flag
output = regs[7]   # convention; decoder may also use last-written
```

`safe_apply` clamps magnitudes to `±1e30`, flushes subnormals, guards
division/log/sqrt/exp/pow domains, and never emits NaN/Inf.

## Implementations (ladder)

1. **CPU reference (P02, NumPy):** correctness oracle. Simple loops over
   programs in Python + vectorization over data points. Slow but obviously
   correct; all GPU results must match it within float32 tolerance on the
   conformance corpus.
2. **Batched CPU (P04):** fully vectorized over `(programs x points)`.
3. **GPU (P05+):** PyTorch tensor ops first. Custom Triton/CUDA kernels only
   if `CVPS` measurement shows PyTorch is the bottleneck and the kernel
   keeps determinism.

No per-candidate Python objects, no string formatting, no exception-driven
control flow in any timed path.

## Conformance

`tests/test_vm.py` holds the oracle vectors: edge inputs
(`0, ±1e-12, ±1e30, infinities in, NaN in`) for every opcode, plus two
end-to-end programs (`x+1`, `x^2+3x+7`). GPU backends must reproduce the
CPU oracle exactly (bitwise for integer flags, `<= 1e-6` relative for
finite float outputs) before they can claim throughput.

## Alternatives and tradeoffs

- Variable-length chromosomes: save bytes but cost branchy decode; rejected
  for v0, revisit after CVPS baseline.
- Adding branches/loops: rejected — non-termination risk kills verification
  throughput.
- float64 in L1: rejected — halves GPU throughput; float64 lives in Level-2
  strict verification only.
