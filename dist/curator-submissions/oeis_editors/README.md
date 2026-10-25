# EvoByte Integer Sequences Research Dossier — OEIS Editorial Board

## 1. Overview
This package compiles results from EvoByte algorithmic searches relating to integer sequences:
- A072842 & A118771: Weak Schur numbers $WS(k)$.
- A090245: Maximum size of cap sets in $\mathbb{F}_3^n$.
- A030126: Strong Schur numbers $S(k)$.

- **Audited Campaigns:** P177 (`experiments/p177-weak-schur-results.json`).
- **P186 Novelty Audit:** `experiments/p186-novelty-audit.json` (CONFIRMED: 0, NULL_RESULT: 3).
- **Outcome:** OEIS published bounds remain unbroken:
  - $WS(5) \ge 207$ (Rowley 2025) remains intact; attempts at 208 revealed 14 irreducible violations.
  - $WS(6) \ge 650$ (Rodrigo 2026) remains intact.

## 2. Independent Verification in 3 Commands
```bash
# 1. Run standalone verifier on weak Schur calibration WS(2) = 8
python3 verify_frontier_certificate.py --type weak_schur --sample

# 2. Check local files presence
test -f null-result-notice.md && echo "Notice present: OK"

# 3. Read the formal null-result notice
cat null-result-notice.md
```

## 3. Human Submission Status
**Status:** `pending_human_submission`.
Prepared for review by the human corresponding author. No automated submission is made.
