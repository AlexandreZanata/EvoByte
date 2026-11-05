# Submission Letter — Dan Gordon (LJCR Covering Tables)

**Recipient:** Dan Gordon, Maintainer, La Jolla Covering Repository
**Author:** Alexandre Zanata (Corresponding Author, EvoByte Project)
**Date:** 2026-10-25
**Subject:** External confirmation and null-result notification for LJCR covering targets
**Audit Reference:** `experiments/p186-novelty-audit.json` (CONFIRMED: 0)

Dear Dr. Gordon,

We are writing to share the results of an algorithmic verification and search campaign conducted
by the EvoByte project on covering designs $C(v, k, t)$.

Using your published covering tables (snapshot commit `459bcaf`), we evaluated 40 active
parameter sets using heuristic and evolutionary search algorithms under strict pre-registered
computational budgets.

### What is Reported:
1. **Resilience of LJCR Bounds:** In all 40 investigated targets, our algorithms failed to find
   any covering design smaller than your published upper bounds (zero broken bounds; all targets
   registered `NULL_RESULT`).
2. **Independent Verifier:** We provide a zero-dependency Python verifier
   (`verify_frontier_certificate.py`) implementing colexicographical ranking over the combinatorial
   number system.

### What is NOT Claimed:
- We do NOT claim any new record or smaller covering design.
- P186 audit verdict confirms: `CONFIRMED: 0`.
- No modifications to the LJCR tables are required or requested.

This dossier is provided solely as an independent confirmation of the strength of the published
LJCR bounds.

Sincerely,
Alexandre Zanata
Corresponding Author, EvoByte Project
