# EvoByte QECC Research Dossier — Markus Grassl (codetables.de)

## 1. Overview
This package compiles results from the EvoByte quantum stabilizer code search campaign targeting
open distance bounds in Markus Grassl's quantum code tables (`codetables.de`).

- **Investigation Track:** Quantum Error-Correcting Stabilizer Codes $[[n, k, d]]$.
- **Audited Campaign:** P182 (`experiments/p182-qecc-results.json`).
- **P186 Novelty Audit:** `experiments/p186-novelty-audit.json` (CONFIRMED: 0, NULL_RESULT: 7).
- **Outcome:** Grassl upper bounds $d_{hi}$ remain unbeaten across all 7 evaluated open codes
  ($[[14,3]], [[16,5]], [[17,3]], [[18,3]], [[19,10]], [[20,2]], [[20,3]]$).

## 2. Independent Verification in 3 Commands
```bash
# 1. Run standalone verifier on Steane [[7, 1, 3]] calibration code
python3 verify_frontier_certificate.py --type qecc_stabilizer --sample

# 2. Check local files presence
test -f null-result-notice.md && echo "Notice present: OK"

# 3. Read the formal null-result notice
cat null-result-notice.md
```

## 3. Human Submission Status
**Status:** `pending_human_submission`.
This package is prepared for human review and transmission. No automated contact has occurred.
