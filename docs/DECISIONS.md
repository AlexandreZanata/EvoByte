# Decision log (append-only)

Accepted technical/product decisions are appended here; they are never
rewritten. A reversal adds a new entry superseding the old one.

| Date | ID | Decision | Context | Consequences |
|---|---|---|---|---|
| 2026-09-29 | D001 | MIT license; 100% open source research base | maximize reuse and reproduction | patent grant via MIT is minimal; revisit only with explicit ADR |
| 2026-09-29 | D002 | CPU reference first (NumPy), PyTorch ops before Triton/CUDA | determinism + iteration speed | GPU kernels need measured justification |
| 2026-09-29 | D003 | Bytecode v0: 16 instr x 4 B = 64 B, 8 regs, 16 ops, const bank | throughput + mutability + VRAM math | expressivity limits accepted until measured |
| 2026-09-29 | D004 | Cascade verifier + early termination as fixed principle | never waste budget on junk | cutoffs tuned per phase, principle stays |
| 2026-09-29 | D005 | Hidden + extrapolation splits mandatory; leak = integrity failure | anti-memorization | L2-only access enforced by review + audit |
| 2026-09-29 | D006 | P00 hardware probe + reproducibility harness before bytecode freeze | no invented numbers | phases cannot claim speed without provenance |
| 2026-09-29 | D007 | Neural generator deferred to P12 with must-beat-genetic gate | VRAM protection | no LLM-scale models without ADR |
| 2026-09-29 | D008 | Q-Forge quantum track: symplectic Pauli bits, exact oracle scoring-only, Q00–Q13 gated line | finding-hard/verifying-cheap quantum problems fit H1 | dense matrices forbidden in L1; Q13 locked until consistent rediscovery |
