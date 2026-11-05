# P25 — Math corpus consolidation (leak-free benchmark)

**Status:** Done (2026-10-01; verified corpus + sealed test; 5,864 items [4,281 EXECUTE, 1,583 FIND]; artifact `experiments/p25-corpus.json`; `make verify` + `pytest` green).
**Prerequisite:** P24 stable limits recorded.
**Owner:** executed on `codex/p25-math-corpus` from `66c00dd`.

## Objective

Turn external math data into a reproducible, leak-free benchmark: an
audited GSM8K base plus an extended corpus (verifiable NuminaMath subset +
SymbolicMathematics-compatible symbolic tasks), with pinned versions,
hashes, licenses and a held-out test set that training and tuning never
touch. Separates two evaluations: EXECUTE a given calculation chain vs
FIND a solution from the problem — passing the first never counts as the
second. Note: GSM8K test was already used internally (see
`experiments/mathdb-*.json`), so it cannot be presented as an untouched
official test set.

## Scope

In: GSM8K audit (license MIT, source
https://github.com/openai/grade-school-math, chain annotations as first
executable corpus), verifiable NuminaMath-1.5 subset
(https://huggingface.co/datasets/AI-MO/NuminaMath-1.5, invalid
problem/solution filtering), symbolic tasks compatible with
https://github.com/facebookresearch/SymbolicMathematics, offline converter
(problem -> inputs/constraints/allowed-ops/verifier) with explicit
out-of-scope list, family/problem-model stratified held-out test,
coverage report.
Out: downloading anything before this phase executes (pin now, fetch in
Building), training any model on the held-out set, retrieval/LLM
solvers, claims about the full upstream datasets beyond the declared
subset.

## Ordered work

- Pin now (no download yet): dataset IDs, revisions, licenses, subset
  definitions and the family stratification for the held-out test.
- In Building: download once, verify hashes, filter invalid entries with a
  logged reason each, convert supported problems offline; unconvertible
  problems go to the explicit out-of-scope list, never silently dropped.
- Verify every stored answer independently (guarded arithmetic re-check);
  publish coverage (families x difficulty x convertible/testable).
- Seal the held-out test before any training/tuning; access logged, zero
  reads during development. Report EXECUTE-chain vs FIND-solution metrics
  separately on identical splits.

## Max-GPU rule (standing)

Corpus build and verification run chunked under the adaptive VRAM budget
with 8 CPU workers for parse/convert in parallel with GPU numeric checks,
synchronized timing and OOM halving. No crash, no leak, no silent skip.

## Exit gate

The phase-specific CLI below is an acceptance interface to implement during
this phase, not a claim that the current checkout supports it. Common checks
already exist. Run the experiment only after its prerequisite is green.

```bash
git diff --check
python3 -m pytest tests -q
make verify
python3 benchmarks/math_corpus.py --build --verify --output experiments/p25-corpus.json
```

Artifact: checksummed `experiments/p25-corpus.json` (pins, hashes,
coverage, out-of-scope list, held-out seal log) plus the versioned corpus
snapshot reference. Done means reproducible corpus + verified answers +
declared coverage + sealed test — not model performance.

## Risks

Upstream dataset mutation (re-pin on hash mismatch, never force), family
leakage through near-duplicate problems, converter bugs marking hard
problems out-of-scope to flatter coverage. GSM8K-test reuse as "official
test" is forbidden.

## Commit & Push (mandatory)

Start from a clean tree on `codex/p25-math-corpus`. Follow the common
commit procedure in [README.md](README.md#commit-and-push-contract), using
this phase's exact reviewed file list and artifact manifest. One completed
micro-task produces one atomic commit; never commit a failed gate.

```bash
git status --short
git diff --check
git diff --cached --check
git commit -m "feat(bench): complete p25 math-corpus"
git push -u origin HEAD
gh pr create --title "feat(bench): complete p25 math-corpus" --body-file /tmp/evobyte-p25-pr.md
git status --short
```
