# P57 campaign review — bounded Erdős–Straus instances (primes 1 mod 24)

Status: evidence complete; novelty NOT sustained (no independent reproduction
by another party, no catalog-backed novelty claim). No discovery is claimed.
Instance work only — nothing here settles the open conjecture.

## 1. Literature (reviewed 2026-10-05)

- Erdős (1948) conjectures 4/n = 1/x + 1/y + 1/z in positive integers for all
  n ≥ 2. Status in 2026: open in general; verified computationally to n ≤ 10^17.
- Only primes need checking: a composite solution scales down from its prime
  factors, so composites are redundant.
- Parametric identities settle whole residue classes without search:
  - even n = 2m: (m, m+1, m(m+1)) — check: 1/m + 1/(m+1) + 1/(m(m+1)) = 2/m;
  - n ≡ 2 (mod 3): (n, (n+1)/3, n(n+1)/3);
  - 3 | n: (n/3, 2n, 2n);
  - greedy/Sylvester covers every n not ≡ 1 (mod 4) in ≤ 3 terms.
- The remaining hard class is primes n ≡ 1 (mod 24) (odd, ≡ 1 mod 3,
  ≡ 1 mod 4): no identity above applies. Analytic work (Mordell 1967;
  Elsholtz–Tao 2013 and later) narrows but does not close it.
- References: Erdős 1948; Mordell 1967 (Diophantine Equations);
  Elsholtz–Tao 2013 (J. Aust. Math. Soc.); Hardy–Wright (background).

## 2. Nomination (frozen)

- 1181 primes n ≡ 1 (mod 24), 2 ≤ n ≤ 100000 (first 73; includes the 1009
  control anchor). Frozen list in `experiments/p57-config.json`, verified
  byte-identical by the audit before any search ran.
- Bounds: x, y, z positive integers ≤ 10^9, strictly enforced (out-of-bound
  matches are skipped, never accepted). Search cap: 3600 s wall.
- Classical comparison: the three parametric families above, each exactly
  verified on samples (n = 4, 5, 3). Applicability to the nominated list:
  0/1181 (expected: the residue class excludes all three by construction).

## 3. Method (accepted, no new algorithms)

- Accepted GPU arithmetic search (`run_erdos_straus_campaign`) in bounded
  windows, strict bounds, dual exact checkers (integer identity + rational
  fractions) on CPU for every finalist. The polynomial proposer (P53) was
  not used: no experiment shows fit to this representation (P54 DROP kept
  the accepted arithmetic search).
- 13,171,481,445 candidates evaluated; finished naturally (no time cap hit).

## 4. Results

- rediscovery: 1 (n = 1009 → (253, 85100, 944524900), the P47-cited k3
  anchor, bit-identical).
- candidate: 931 (dual-verified, in-bounds, computationally exact; novelty
  unreviewed — see §5).
- budget-exhausted: 249 (windowed search, larger n mostly; never
  exhaustive-null: coverage is a bounded window, not the finite domain).
- Max coordinate over all certificates: 998,967,081 (< 10^9).
- Certificates: `experiments/p57-certificates.json` (932 compact entries
  with per-triple sha256; recomputable from (n, x, y, z)).

## 5. Novelty assessment (per contract)

- rediscovery (1009): matches the cited construction — not novel, useful
  as an end-to-end control that the pipeline reproduces known truth.
- candidate (931): each is an exactly verified instance solution, but
  novelty is NOT decided by absence from a catalog, and no catalog sweep
  plus no independent reproduction by another party exists. They stay
  `candidate`; `verified-construction` requires reviewer-sustained novelty.
- No `counterexample`, `proven-theorem`, `exhaustive-null`, or discovery:
  single instances cannot disprove anything here, the domain was not fully
  covered, and discovery additionally requires correctness + sustained
  novelty + independent reproduction + the proper certificate or proof.
- Reproduction status: dual-checker self-repeat in fresh processes
  (implementation-independent checkers); independent authorship unavailable.

## 6. Costs and limits

- Search ≈ 5.5 s GPU wall for 13.2B evaluations + CPU dual verification
  per finalist (all billed in the acceptance report).
- Sample limits: 1181 nominated instances of one residue class; results do
  not generalize to the conjecture. A post-campaign change needs a new
  campaign; P38's final was not reused.
