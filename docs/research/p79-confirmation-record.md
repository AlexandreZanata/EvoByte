# P79 — Blind residue confirmation and statistical selection control record

- Command: `bash experiments/p79-run.sh` (clean tree, `config: experiments/p79-config.json`)
- Split: `experiments/p79-blind-split.json` (SHA256: `d1d657cc0077fd205f2cde7b5ba6bb772b0144ad2d5025cb345b9440e21b63c6`)
- Verdict: **ACCEPTED**, 0 findings, `run_id=1dacdf80fdb1c90a`, revision `c00059702c6d`
- Python 3.12.2, CPU only, seed 42, coordinate bound $10^9$

## Results (measured)

| Metric | Track H_ES ($a=4$) | Track H_SIER ($a=5$) |
| --- | --- | --- |
| Target problem | Erdős–Straus held-out | Sierpiński held-out |
| Base modulus | $m = 840$ | $m = 120$ |
| Held-out instances | 20 ($k \in [10, 29]$) | 20 ($k \in [10, 29]$) |
| Instance domain | $n \in [8401, 25129]$ | $n \in [1201, 3577]$ |
| Paired outcomes (sieve vs baseline) | W=20, L=0, T=0 | W=20, L=0, T=0 |
| Total sieve candidates evaluated | 66 candidates | 66 candidates |
| Total baseline candidates evaluated | 167,351 candidates | 12,148 candidates |
| Mean candidate reduction | 2,535.6x | 184.1x |
| Raw exact two-sided sign p-value | $1.9073 \times 10^{-6}$ | $1.9073 \times 10^{-6}$ |
| Holm-adjusted FWER p-value ($\alpha=0.05$) | $3.8147 \times 10^{-6}$ | $3.8147 \times 10^{-6}$ |
| Track outcome | **CONFIRMED** | **CONFIRMED** |
| Exact Diophantine dual verification | 20/20 integer + Fraction | 20/20 integer + Fraction |

## Statistical decision and conclusions

1. **Family-wise error rate control:** Both tracks reject the null hypothesis of equal candidate efficiency under the step-down Holm procedure at family-wise error rate $\alpha = 0.05$ ($p_{\text{adj}} = 3.81 \times 10^{-6} \ll 0.05$).
2. **Absence of symbolic overfitting:** Performance improvements hold uniformly across held-out residue classes that were sealed and immutable prior to evaluation.
3. **Dual mathematical certification:** Every solution found on both tracks satisfies exact integer equality $a x y z = n(x y + y z + z x)$ and independent rational fraction arithmetic $\frac{a}{n} = \frac{1}{x} + \frac{1}{y} + \frac{1}{z}$ within coordinate limit $10^9$.

## Scope and limitations

- Confirmation certifies algorithmic search efficiency on tested held-out congruence classes.
- Does not constitute a formal universal proof of the Erdős–Straus or Sierpiński conjectures for all positive integers.
