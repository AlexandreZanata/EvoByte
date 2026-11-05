# EvoByte Covering Designs Research Dossier — Dan Gordon (LJCR)

## 1. Overview
This package compiles the results of the EvoByte pre-registered combinatorial search campaign
targeting open and active covering designs $C(v, k, t)$.

- **Investigation Track:** Combinatorial covering designs $C(v, k, t)$.
- **Audited Campaign:** P176 (`experiments/p176-covering-results.json`).
- **P186 Novelty Audit:** `experiments/p186-novelty-audit.json` (CONFIRMED: 0, NULL_RESULT: 40).
- **Outcome:** LJCR published tables remain strictly unbeaten. All 40 investigated targets
  produced negative results (`NULL_RESULT`). No new covering designs beating published bounds
  are claimed.

## 2. Independent Verification in 3 Commands
To verify the calibration baseline and confirm the verification suite offline:

```bash
# 1. Run standalone verifier on calibration sample (Fano plane C(7, 3, 2) = 7)
python3 verify_frontier_certificate.py --type covering --sample

# 2. Verify SHA-256 integrity of this package
sha256sum -c <<'EOF'
EOF

# 3. Read the formal null-result notice
cat null-result-notice.md
```

## 3. Human Submission Status
**Status:** `pending_human_submission`.
This dossier is prepared for review and optional transmission by the human corresponding author.
The automated AI agent does not contact maintainers or send correspondence.
