# P47 Nomination — frozen family and first experiment (pending human review)

Source of truth: `experiments/p47-nomination.json` (frozen hash
`18af5df916836e5a…`, computed over canonical JSON excluding the frozen
block). This document is the review surface; on any conflict the JSON wins.

## Scope A — proposer development: `polynomial_arithmetic` over ℚ

- Representation: v0 16-word bytecode, r7 output, pinned CONST_BANK.
  Transcendental bank slots are numerical-only by construction.
- Certificate: P42 `exact_certificate` (unified symbols, explicit domain,
  pole freedom). Numerical evidence is never a success.
- Source: `data/processed/p25_corpus.jsonl` (pinned sha256 in the JSON) via
  the P30 source-group-separated pipeline. No natural language in the loop.
- Tasks: deterministic sampler (degree ≤ 2, rationals with denominator
  dividing 12), seed `42047`, canonical-form dedup; exact list materializes
  at experiment time and is sealed then.
- Splits frozen before any training; source record plus all
  equivalences/variations of one canonical target share a group.
- Success: per-task `exact_certificate`; aggregates certified success rate
  and median time-to-certified. MSE is excluded as a success metric.
- Baselines: grammar sampling (P33 accepted path) and genetic evolution at
  equal total cost.
- Final test: closed. Storage `experiments/p47-final-test/` with an empty
  persistent access log. The ten P38-observed ids are forbidden and listed
  in the JSON. Fresh `p47ft-` ids materialize at confirmation time.

## Scope B — later scientific campaign: bounded Erdős–Straus

- Certificate: exact integer triple, dual checkers, M ≤ 10⁹ strict.
- Baseline: matched CPU enumeration, equal wall-clock.
- Calibration only: n ∈ {1009, 10007, 100003} (already observed in P39;
  pipeline validation, no discovery claims).
- Discovery instances: from the P46 `finite_search_candidates` bucket,
  human-approved list, currently pending.
- Coverage windows are declared per run before execution; a finite miss is
  never a counterexample; no universal claims from finite runs, ever.

## Pre-fixed hypothesis

Under equal total cost, the structured/conditioned proposer achieves a
higher exact-certificate rate (or lower median time-to-certified) than the
matched classical baseline on sealed tasks of the nominated family.
Falsification: paired bootstrap 95% CI of the rate difference includes zero
or favors the baseline → rejected for this family, no post-hoc metric
substitution.

## Controls

Must certify exactly: x²−1 (bank-exact Horner), x²+3x+7 (exact fixture),
n=1009 triple (253, 85100, 944524900, dual-checked).
Must reject: train-coincident x⁸/10¹² perturbation (numerical only), y-vs-x
symbol mismatch, x/0 invalid program, pole-in-domain rational (all four are
P42 regressions; records cited, not copied).

## Thresholds and non-claims

Threshold quantities are frozen; numeric values await human review.
Explicit non-claims: infra reuse ≠ model transfer; narrow-family win ≠ H1;
finite miss ≠ counterexample; catalogue membership ≠ novelty proof.

## Review checklist (human)

1. Family/domain choice and rational-coefficient policy.
2. Split/grouping rule and fresh-test procedure (incl. forbidden P38 ids).
3. Hypothesis wording, effect measure, falsification rule, MSE exclusion.
4. Control set completeness (known + false).
5. Threshold quantities and proposed values.
6. Scope-B calibration/discovery split and no-universal-claims rule.
7. P46 curation approval (separate gate, still pending).

Approval is recorded with author/date/justification in the nomination
(`human_review`) and does not authorize merges.
