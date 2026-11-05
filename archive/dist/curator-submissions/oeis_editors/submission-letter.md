# Submission Letter — OEIS Editorial Board

**Recipient:** The Editorial Board, Online Encyclopedia of Integer Sequences (OEIS)
**Author:** Alexandre Zanata (Corresponding Author, EvoByte Project)
**Date:** 2026-10-25
**Subject:** Verification and null-result notes on Weak Schur numbers (A072842, A118771)
**Audit Reference:** `experiments/p186-novelty-audit.json` (CONFIRMED: 0)

Dear OEIS Editors,

We are submitting an independent verification report regarding sequence A072842 and A118771
(Weak Schur numbers $WS(k)$).

Using GPU-accelerated heuristic search and symmetric partition checking, the EvoByte project
evaluated the open frontiers at $k=5$ and $k=6$.

### What is Reported:
1. **Confirmation of Published Bounds:** In our pre-registered trials for $k=5$, partitioned
   colorings at size 208 persistently encountered $\ge 14$ weak Schur violations, corroborating
   the stability of Rowley's 2025 bound $WS(5) \ge 207$.
2. **Standalone Verifier:** We provide a verified Python script checking weak sum-free partitions
   according to OEIS definitions.

### What is NOT Claimed:
- We do NOT claim any new record term or sequence modification.
- P186 audit verdict confirms: `CONFIRMED: 0`.
- No new sequence entries or edits are requested.

This communication is provided for archival documentation and independent verification purposes.

Sincerely,
Alexandre Zanata
Corresponding Author, EvoByte Project
