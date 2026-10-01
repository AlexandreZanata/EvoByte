# P30 — Corpus isolation by original problem and template

**Status:** Done (2026-10-01, zero leakage verified across 1507 groups, 640 GSM8K defects reproduced, experiments/p30-splits.json generated).
**Prerequisite:** P29 outcome recorded; review evidence frozen. P24–P29 Done labels are historical, not acceptance of the defects under review.
**Owner:** Alexandre Zanata / EvoByte Agent.
**Branch:** `codex/p30-corpus-isolation`.

## Objective

Repair the train/validation/test boundary before any new training or comparison. Keep
related calculation chains, final answers, paraphrases and problem templates together.
Preserve the exposed GSM8K test disclosure.

## Scope

Split/conversion changes in benchmarks/math_corpus.py and tests/test_math_corpus.py.
Answer correctness is evaluated in P31; P30 must label unverified labels as
reference_only. No model fitting or final-test performance measurement.

## Ordered work

- Freeze dataset revisions, source IDs, conversion version and a before/after
  contamination audit. The review found 640 GSM8K source problems shared by train and
  held-out in the P25 snapshot; reproduce this from IDs, without using test answers for
  tuning.
- Group by original source problem BEFORE stratification. Deduplicate normalized content
  and related cross-source/template variants; distinguish an unseen problem from an
  unseen template or family.
- Create a development train/validation split and a fresh final test. Previously exposed
  examples are development data only; exclude them from pristine-test claims. Freeze
  group membership, seed, hashes and access policy.
- Add an enforced loader boundary and access log for final-test reads. Serialize
  grouping metadata and a durable corpus reference; a seal hash alone is not access
  control.
- Test sibling chains across EXECUTE/FIND, paraphrases, reused source IDs, duplicate
  templates, determinism and unauthorized final-test access. Report ungroupable records
  explicitly.

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
python3 benchmarks/math_corpus.py --audit-splits --group-by source-problem-template --output experiments/p30-splits.json
```

A checksummed split manifest and contamination audit prove zero source/group overlap and
declare template/family overlap separately. All accepted pristine-test groups are
unexposed. Raw snapshots are retrievable and hash-checked. Failed isolation blocks P31.

## Resource and evidence contract

Use the accepted RTX 4060 Laptop operating envelope: current free VRAM minus
reserve, bounded chunks/buffers, explicit stream dependencies, synchronized
timing, controlled failure and complete checkpoints. Add streams/workers
only with measured benefit. Keep bytecode/data resident in the hot loop;
text conversion, exact checking and artifact I/O remain outside it and their
costs are disclosed. Record clean revision, full configuration, RNG state,
actual device, dataset/split/checker hashes and durable raw-artifact hashes.

## Risks

Normalization can miss semantic duplicates or combine unrelated problems. Publish the
grouping rule and coverage; never silently discard hard examples to improve the audit.

## Commit & Push (mandatory)

Start from a clean tree on `codex/p30-corpus-isolation` from the accepted predecessor.
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
git commit -m "fix(bench): complete p30 corpus-isolation"
git push -u origin HEAD
gh pr create --title "fix(bench): complete p30 corpus-isolation" --body-file /tmp/evobyte-p30-pr.md
git status --short
```
