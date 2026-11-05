# P78 — Sierpiński / Schinzel generalization record

- Command: `bash experiments/p78-run.sh` (clean tree, `config: experiments/p78-config.json`)
- Verdict: **ACCEPTED**, 0 findings, `run_id=9ac211e38e852d14`, revision `278bb21aed11`
- Python 3.12.2, CPU only, seed 42, Lean 4 v4.34.0 (hermetic Lake build)

## Results (measured)

| Item | Value |
| --- | --- |
| 5/n identities, modulus 120 | 96/120 classes covered (80.0%), all verified exactly over Q[k] |
| Uncovered 5/n classes | 24 (odd residues coprime to 120, plus r=1); left to the per-instance sieve |
| Sieve a=4,5,6,7 on 35 primes (3..1609) | 35/35 solved for each a, dual-checked (integer + Fraction) |
| Mod-120 coverage a=4 (existing P75 engine) vs a=5 | 98.3% vs 80.0% |
| Sieve candidates, 26 default primes (a=5 / a=4) | ratio 0.258 (71 vs 275 candidates) |
| Synthesis time a=5 / a=4 | 0.156 s vs 0.087 s (ratio 1.79) |
| Lean 4 catalog | 149 theorems, 0 sorry; 96 Sierpiński identities (`ring`), 10 Sierpiński certificates (`norm_num`) |

## Scope and limits

- Identities and certificates are individually proved; no universal claim for the Sierpiński or Schinzel conjectures.
- The a=4 coverage figure uses the P75 mod-120 classification, which counts only non-resistant residues; it is not directly an a=5-style search under identical rules, so the coverage gap is indicative.
- Timings are single-run wall clock on one machine.
