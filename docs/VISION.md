# Vision

**Status:** principle.

## Hypothesis (H1)

> If a candidate can be verified orders of magnitude faster than it can be
> rationally discovered, generating gigantic numbers of extremely cheap
> candidates and letting a trusted verifier select promising structures can
> beat sophisticated reasoning per unit of wall-clock time.

EvoByte exists to test H1 in the cheapest falsifiable domain first:
**symbolic regression from data** (`F(X) ~= Y`).

## What EvoByte is

- Massive generation of ultra-compact candidates (target 16–128 bytes each).
- A minimal deterministic math VM — no text, no AST, no per-candidate compile.
- A two-level verifier: Level-1 fast (all candidates, GPU-vectorized) and
  Level-2 strict (top ~0.001%, full data + held-out + extrapolation).
- Automatic selection, mutation, recombination, diversity (QD / islands),
  and a permanent elite archive with checkpoints and resume.
- Maximum safe use of GPU VRAM for population, data, buffers, and results.

## What EvoByte is not (non-goals)

- Not an LLM producing formulas as text.
- Not Chain of Thought, prompts, JSON, or LLM APIs in the hot path.
- Not a giant neural model consuming most of VRAM.
- Not `training error ~= 0` presented as scientific discovery.
- Not a traditional large-AI system that "thinks deeply". The generator may
  be dumb; **the verifier must be smart**.

## Hot-path philosophy

```text
GPU ARRAY -> MUTATE -> EXECUTE -> SCORE -> TOP-K -> RECOMBINE -> REPEAT
```

Banned from the main loop: prompts, sentences, words, natural-language
tokens, JSON, LLM APIs, Chain of Thought, per-candidate string parsing,
per-candidate compilation, Python loops over candidates, needless CPU<->GPU
copies or synchronizations.

## Speed doctrine

Between (A) a more sophisticated architecture and (B) a much faster one that
tests many more candidates — **choose B first** and measure. Intelligence
should emerge from `scale x verification x evolution x memory`, not from
complexity.

## Scope order

1. Synthetic rediscovery (1 variable, 8–16 opcodes, <= 32 instructions).
2. Recognized symbolic-regression suites (no real science before the
   mechanism is proven).
3. Scientific datasets only after benchmarks + ablations are green.
