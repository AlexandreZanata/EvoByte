# P35 — Certified program corpus for specialist training

**Status:** Done.
**Prerequisite:** P30–P32 integrity accepted and P34 operating envelope measured.
**Owner:** Alexandre Zanata
**Result:** 4 certified positives / 36 negatives; 0 checker failures; 0 group/item leakage; learner promotion blocked (limit published).
**Branch:** `codex/p35-verified-training-corpus`.

## Objective

Replace unfiltered population snippets with certified supervision for a single
specialist family. Make the training set large and diverse enough to test learning
rather than imitation of failed searches.

## Scope

Training corpus collection in math_specialist/math_corpus and existing checker/lineage
modules. No learner comparison or final-test evaluation yet.

## Ordered work

- Generate a declared curriculum within polynomial_arithmetic from
  source-group-separated tasks and exact constructions, plus teacher searches using the
  accepted engine. Track problem features, program structure, constants, certificate and
  teacher lineage.
- Accept a positive label only after P31 task-specific checking and the appropriate
  hidden/extrapolation or symbolic-equivalence verification. population[:32], S0
  validity and low training loss alone cannot establish a solved target. Failed
  candidates become separately labelled negatives, never positive supervision.
- Deduplicate bytecode, canonical polynomial forms and related target templates.
  Partition before collecting solutions; keep final-test tasks, answers and archives
  inaccessible. Publish how much of P25 is actually used and exclude reference_only
  labels.
- Define features available at inference time. For regression, train/validation
  input-output observations are permitted; target formula, reference program, hidden
  values and final-test answers are not features.
- Record solved/failed target counts, degree/coefficients/length coverage,
  positive/negative counts and verified label quality. Publish validation learning-curve
  prerequisites and a fixed data-size ladder; do not manufacture duplicate positives to
  meet a quota.
- Bill teacher generation, exact certification, conversion, deduplication and storage
  separately from learner fitting. Pin source/checker/runtime/config hashes and archive
  a retrievable corpus.

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
python3 benchmarks/math_specialist.py --build-verified-corpus --family polynomial_arithmetic --split-manifest experiments/p30-splits.json --output experiments/p35-training-corpus.json
```

A certified corpus manifest with zero positive-label checker failures, zero
source/template test leakage, declared reachable coverage and full teacher cost. If
sufficient certified examples cannot be produced, publish the limit and stop learner
promotion until a new scoped data experiment is accepted.

## Resource and evidence contract

Use the accepted RTX 4060 Laptop operating envelope: current free VRAM minus
reserve, bounded chunks/buffers, explicit stream dependencies, synchronized
timing, controlled failure and complete checkpoints. Add streams/workers
only with measured benefit. Keep bytecode/data resident in the hot loop;
text conversion, exact checking and artifact I/O remain outside it and their
costs are disclosed. Record clean revision, full configuration, RNG state,
actual device, dataset/split/checker hashes and durable raw-artifact hashes.

## Risks

Teacher bias may collapse diversity. Negative-label imbalance, incorrect constants and
hidden data in features can create impressive training losses without useful generation.

## Commit & Push (mandatory)

Start from a clean tree on `codex/p35-verified-training-corpus` from the accepted
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
git commit -m "feat(generator): complete p35 verified-training-corpus"
git push -u origin HEAD
gh pr create --title "feat(generator): complete p35 verified-training-corpus" --body-file /tmp/evobyte-p35-pr.md
git status --short
```
