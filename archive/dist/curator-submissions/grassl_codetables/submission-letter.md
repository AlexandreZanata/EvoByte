# Submission Letter — Markus Grassl (codetables.de)

**Recipient:** Markus Grassl, Maintainer, codetables.de
**Author:** Alexandre Zanata (Corresponding Author, EvoByte Project)
**Date:** 2026-10-25
**Subject:** External verification report on open quantum code parameters
**Audit Reference:** `experiments/p186-novelty-audit.json` (CONFIRMED: 0)

Dear Dr. Grassl,

We are writing to share independent verification data from the EvoByte evolutionary search
campaign on quantum stabilizer codes $[[n, k, d]]$.

Focusing on 7 open targets from your tables ($[[14,3]], [[16,5]], [[17,3]], [[18,3]], [[19,10]],
[[20,2]], [[20,3]]$), our resident GPU evolution pipeline explored candidate stabilizer spaces
under pre-registered mutation and selection budgets.

### What is Reported:
1. **Bounds Stability:** All 7 open targets resulted in `NULL_RESULT`. No stabilizer configuration
   reached the upper bound d_hi, reaffirming the tightness of your published bounds.
2. **Standalone Verification:** Calibration codes ($[[7,1,3]]$, $[[9,1,3]]$, $[[5,1,3]]$) were verified
   using pure standard-library symplectic weight search.

### What is NOT Claimed:
- We do NOT claim any new record code or distance improvement.
- P186 audit verdict confirms: `CONFIRMED: 0`.
- No updates to `codetables.de` are requested.

This dossier is submitted solely as an external confirmation of your table bounds.

Sincerely,
Alexandre Zanata
Corresponding Author, EvoByte Project
