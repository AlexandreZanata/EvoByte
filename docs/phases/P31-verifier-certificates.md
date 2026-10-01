# P31 — Independent answer verification and certificate bounds

**Status:** Done.
**Prerequisite:** Accepted P30 isolation manifest.
**Owner:** Codex
**Branch:** `codex/p31-verifier-certificates`.

## Objective

Make acceptance depend on the actual mathematical statement, not on a stored answer, a
hash or the same checker called twice. Correct the corpus verifier and P29 certificate
boundaries.

## Scope

Acceptance logic in benchmarks/math_corpus.py, benchmarks/open_problems.py and their
existing tests. Add adversarial wrong-answer, forged-count, out-of-bound, overflow,
domain and altered-artifact cases. No new scientific novelty claims or search algorithm.

## Ordered work

- Replace unconditional success for scalar FIND targets with an independently derived
  reference or a verified solution witness. EXECUTE checks exact/rational arithmetic
  where appropriate. Symbolic targets require identities, derivatives, initial
  conditions or other task-specific evidence, not copying target_values.
- Unsupported natural-language statements remain reference_only/out_of_scope, excluded
  from verified-solver accuracy. Publish verified coverage and unsupported counts with
  the full denominator.
- Write a second checker using a different formulation/implementation for accepted
  certificates. For Erdős–Straus, independently compare exact fractions against the
  integer-identity checker. A repeated call to check_erdos_straus is self-checking, not
  independent reproduction.
- State which coordinates each search bound constrains and enforce it during search and
  certification. Reclassify historical solutions exceeding the declared 10^9 bound
  without disputing their exact identities. Check n >= 2, integer types, positivity,
  overflow safety and all nominated instances.
- For bounded-null claims, replay the complete nominated domain with independent exact
  checking or a proven exclusion certificate. Reusing matches_count == 0 cannot certify
  absence. An incomplete search is budget_exhausted, not exhaustive_null.
- Validate hashes and certificate schemas. SHA-256 is a checksum, not a digital
  signature. Freeze corrected thresholds and preserve old artifacts as superseded
  diagnostics.

## Exit gate

The phase-specific CLI below is an interface to implement during this phase;
it is not a claim that these flags already exist. Run its experiment only
after prerequisites and common checks pass. Freeze configurations before
measurement. Complete one bounded micro-task at a time; failed correctness
or integrity gates block commit/push. A sound negative experiment is not a
reason to weaken its registered thresholds.

```bash
git diff --check
git status --short
python3 -m pytest tests -q
make verify
python3 benchmarks/open_problems.py --audit-certificates --bounds-strict --output experiments/p31-certificates.json
python3 benchmarks/math_corpus.py --verify-independent --split-manifest experiments/p30-splits.json --certificate-report experiments/p31-certificates.json --output experiments/p31-verification.json
```

The acceptance report links independently checked answers and corrected certificates,
with zero accepted false-positive fixtures. Every claimed finite-domain bound is
enforced. Unverifiable records are explicitly excluded. A positive/negative mathematical
result is valid; an unsound checker blocks P32.

## Resource and evidence contract

Use the accepted RTX 4060 Laptop operating envelope: current free VRAM minus
reserve, bounded chunks/buffers, explicit stream dependencies, synchronized
timing, controlled failure and complete checkpoints. Add streams/workers
only with measured benefit. Keep bytecode/data resident in the hot loop;
text conversion, exact checking and artifact I/O remain outside it and their
costs are disclosed. Record clean revision, full configuration, RNG state,
actual device, dataset/split/checker hashes and durable raw-artifact hashes.

## Risks

Numeric equality is not a proof of a universal statement. Independent implementations
can share the same mistaken assumptions; include a specification review and exact
reference cases.

## Commit & Push (mandatory)

Start from a clean tree on `codex/p31-verifier-certificates` from the accepted
predecessor.
Follow [README.md](README.md#commit-and-push-contract); explicitly stage
only reviewed implementation/test/documentation files and the small phase
manifest. Never commit large/private raw data. Create/update a PR against
the accepted predecessor (or main after it is integrated), then confirm a
clean tree. Each finished micro-task produces one atomic commit after all
its applicable gates pass; the block below is for final phase completion.

```bash
git status --short
git diff --check
git diff --cached --check
git commit -m "fix(verifier): complete p31 verifier-certificates"
git push -u origin HEAD
gh pr create --title "fix(verifier): complete p31 verifier-certificates" --body-file /tmp/evobyte-p31-pr.md
git status --short
```
