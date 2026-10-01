# P33 — Structured candidate search for polynomial arithmetic

**Status:** Proposed.
**Prerequisite:** Accepted P32 baseline and P31 exact verifier.
**Owner:** assigned when moving to Building.
**Branch:** `codex/p33-structured-search`.

## Objective

Test whether grammatical, data-dependent candidate construction improves verified
solutions per second over unrestricted byte mutation. Start with the single
polynomial_arithmetic family.

## Scope

Candidate construction/mutation in existing evolution/resident modules, the
math_specialist benchmark and conformance tests. No neural fitting or additional quantum
mechanisms.

## Ordered work

- Preregister variable count, rational coefficient bounds, degree, live instruction
  length, allowed operations, tolerances and development tasks. Exclude final-test
  groups from tuning. Preserve bytecode v0 and its CPU oracle; semantic changes require
  an ADR, version bump and old interpreter.
- Build typed expression generation offline or with resident numeric structure tensors.
  Compile to existing bytecode with valid register dependencies, operand domains and an
  output depending on intended inputs. The hot loop contains no strings or AST parsing.
- Separate active/live instructions from padding, dead code and constant outputs.
  Canonicalize cheaply justified identities to reduce syntactic duplication; do not
  claim equivalence from equal probes alone. Report compilation/repair costs and
  rejected overlength programs.
- Compare unrestricted structured sampling, grammar sampling, genetic evolution and
  grammar-constrained evolution. Pair tasks/seeds, match workload and total
  resource/time budgets, rotate arm order and perform the same warmup.
- Measure verified success, censored time-to-solution, bytes/behavior diversity,
  invalidity, uniqueness window and full pipeline throughput on real 10 s/1 min budgets
  with at least five seeds. Publish all failures; verify frozen finalists exactly off
  the hot path.

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
python3 benchmarks/math_specialist.py --structured-search --family polynomial_arithmetic --budgets 10s,1m --seeds 5 --output experiments/p33-structured-search.json
```

A preregistered control comparison with certified finalists and no test exposure. Adopt
structured operators only on supported workloads when the quality/time gate wins; a
sound null completes the experiment using the accepted baseline for P34.

## Resource and evidence contract

Use the accepted RTX 4060 Laptop operating envelope: current free VRAM minus
reserve, bounded chunks/buffers, explicit stream dependencies, synchronized
timing, controlled failure and complete checkpoints. Add streams/workers
only with measured benefit. Keep bytecode/data resident in the hot loop;
text conversion, exact checking and artifact I/O remain outside it and their
costs are disclosed. Record clean revision, full configuration, RNG state,
actual device, dataset/split/checker hashes and durable raw-artifact hashes.

## Risks

A restrictive grammar may exclude the answer. Report reachable target coverage and
coefficient/length limits; narrowing the space after looking at test failures requires a
new experiment.

## Commit & Push (mandatory)

Start from a clean tree on `codex/p33-structured-search` from the accepted predecessor.
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
git commit -m "feat(evolution): complete p33 structured-search"
git push -u origin HEAD
gh pr create --title "feat(evolution): complete p33 structured-search" --body-file /tmp/evobyte-p33-pr.md
git status --short
```
