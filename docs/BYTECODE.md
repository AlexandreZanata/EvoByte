# Bytecode specification (v0)

**Status:** decision. `OPCODE_VERSION = 0`. Any change bumps the version and
keeps the old interpreter for reproducibility.

## Why this design

Priority order: generation speed > execution speed > mutation ease >
parallelism > memory > invalid elimination > zero text parsing.

Comparison of candidates considered:

| Option | Verdict | Reason |
|---|---|---|
| Stack machine / RPN tokens | considered | simple, dense; harder to bound registers |
| Fixed-length register chromosome | **chosen for v0** | uniform 4 B/instr, trivial mutate, SIMD-friendly |
| DAG / SSA | deferred | better expressivity, harder codegen on GPU |
| Serialized trees | rejected | parse + variable length hurts throughput |
| x86/CUDA assembly | rejected | compile overhead, sync cost |

## Layout

- Program: **16 instructions**, each **4 bytes** => **64 bytes** per candidate.
- Instruction (uint32, little-endian): `[op:8][dst:4][a:4][b:8][flags:8]`.
  Simpler view: `[OP, DST, A, B]` where each field is one byte.
- Registers: 8 float32 (`r0..r7`). `r0..r1` preload inputs (x, y for 2-var),
  rest zero-init. Last written register used as output (or `r7` by convention).
- Unused slots encode `NOP`. Short programs are NOP-padded, never
  variable-length in VRAM.

## Opcode table (v0, 16 ops)

| OP | Byte | Semantics (`dst = f(a, b)`) | Safe-math rule |
|---|---|---|---|
| NOP | 0x00 | no-op | — |
| ADD | 0x01 | `ra + rb` | clamp to ±1e30 |
| SUB | 0x02 | `ra - rb` | clamp |
| MUL | 0x03 | `ra * rb` | clamp, flush subnormals to 0 |
| DIV | 0x04 | `ra / rb` | if `|rb| < 1e-12` -> invalid flag, output 0 |
| SIN | 0x05 | `sin(ra)` | range-reduce via `fmod(ra, 2pi)` |
| COS | 0x06 | `cos(ra)` | same as SIN |
| EXP | 0x07 | `exp(ra)` | clamp input to `[-20, 20]`, else invalid-penalty |
| LOG | 0x08 | `log(|ra|)` | if `|ra| < 1e-12` -> invalid flag |
| POW | 0x09 | `pow(|ra|, clamp(rb,-6,6))` | negative base uses abs; overflow -> invalid |
| ABS | 0x0A | `|ra|` | — |
| SQRT | 0x0B | `sqrt(|ra|)` | — |
| NEG | 0x0C | `-ra` | — |
| MIN | 0x0D | `min(ra, rb)` | — |
| MAX | 0x0E | `max(ra, rb)` | — |
| CSEL* | 0x0F | `ra + c[b]` (const-bank add) | `c` = 16-entry bank (see CONSTANTS) |

`*` v0 constants: 16-entry quantized bank
`[0, 1, -1, 2, 0.5, 3.14159, 2.71828, 10, 0.1, -0.5, 7, 3, 0.01, 100, -10, 0.001]`.
No free float immediates in v0 (prevents lucky-float hits from dominating).

## Validity rules (cheap, pre-execution)

1. At least one non-NOP instruction.
2. All register indices `< 8`, opcode `< 0x10`.
3. Output register written at least once.
4. No `DIV/LOG/POW/EXP/SQRT` chain longer than 4 without a bounded op
   (static heuristic; execution still guards).

Violations are rejected in Stage-0 without data evaluation.

## Examples

`y = x^2 + 3x + 7` (x in r0, consts via CSEL) assembles conceptually to:

```text
MUL r2, r0, r0      ; x^2
CSEL r3, r0, #3     ; 3*x via bank add chain (simplified)
ADD r4, r2, r3
CSEL r5, r4, #7bank ; +7
```

Exact encodings live in `src/evobyte/bytecode.py` and its tests. Text forms
are for humans only and never enter the hot path.

## Versioning

- `OPCODE_VERSION` is a uint16 header in every checkpoint/archive row.
- v0 is frozen when P01's exit gate passes. Later versions add ops/registers
  only with a migration note and a retained v0 interpreter.

## P49 compact candidate profile (`p49-compact-polynomial`, revision 0)

The v0 codec already satisfies the nominated family, so P49 freezes a
profile over it with **no codec change, no `OPCODE_VERSION` bump and no
interpreter fork** (a bump would additionally require an ADR first):

- Integer ids: 16 `uint32` words, 64 bytes per candidate (`compact_encode`
  / `compact_decode`, length-checked both ways).
- Allowed ops: NOP, ADD, SUB, MUL, CSEL only; other v0 ops stay globally
  valid but are outside this profile.
- Register refs: r0–r7 with the r7-output rule; S0 validity
  (`is_valid`) still enforced underneath.
- Bounded rational constants: the 16 `CONST_BANK` slots with exact
  rationals of the stored binary values (`compact_candidate_profile()`,
  same rule the P42 checker applies, so profile and certificates agree);
  slots 5–6 are approximate transcendental slots and never carry exact
  certificates.
- Decoding: field layout per § Layout; `validate_compact_candidate()`
  rejects unknown versions, bad shapes/dtypes, out-of-range refs,
  off-profile ops and S0 failures with explicit reasons.
- Certificates: text/Lean/SymPy live only at the certification boundary;
  a compact candidate converts to the same certified mathematical object
  (`program_to_sympy` + exact identity, P42).
- Coverage: the defined grammar only (Horner degree ≤ 3 / expression
  trees depth ≤ 3 over bank rationals). Compactness claims nothing about
  universality and reduces no search complexity by itself.

## P67 verified macros (references, no new opcodes)

- Macros are references to existing instruction blocks, expanded before
  execution (`p67_expand_tokens`); opcode table, codec and semantics are
  unchanged, so no ADR and no `OPCODE_VERSION` bump.
- Mining (`p67_mine_macros`): recurrent non-NOP subsequences of length
  2–4, canonicalized by register renaming in order of first appearance,
  top 32 by exact count. Macro≡expansion holds by construction (same
  stream under the frozen interpreter); round-trip and execution equality
  are tested, never assumed.
- Compression (`p67_compress_program`): greedy longest match, deterministic;
  expansion rejects overflow, unknown ids and invalid words with `None`
  (never silent truncation).
