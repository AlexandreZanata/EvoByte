# P38 — Clean-environment confirmation and frozen model export

**Status:** Done.
**Prerequisite:** P30–P37 reports valid; selected method and all tuning frozen.
**Owner:** Alexandre Zanata
**Result:** PROVISIONAL — frozen grammar baseline verifies 0.20 of the sealed
final-test polynomial slice (20 seeds); resume deterministic, 1 authorized
access logged, H1 NOT_CONFIRMED (out of scope).
**Branch:** `codex/p38-independent-confirmation`.

## Objective

Confirm the selected system on a fresh final test and a clean runtime, then publish
usable artifacts and narrowly scoped conclusions before a new scientific campaign.

## Scope

Confirmation/reproduction in full_matrix plus existing export and benchmark paths. No
algorithm change during final scoring; no requirement to manufacture positive H1, model
or speed results.

## Ordered work

- Pin code, dependencies, checker, corpus/split hashes, model weights, resolved
  configurations and environment. Recover raw data without private caches. Document one
  reproduction command and an independent checker/operator when available;
  self-repetition is not independent authorship.
- Freeze the selected genetic/model/sampler pipeline using only development evidence.
  Open the P30 final test once for authorized scoring, record access, and never retune
  against it. An inconclusive result needing changes requires a fresh future test.
- Run at least 20 independent seeds on preregistered representative problems at equal
  real time/resource budgets. Compare per-problem verified success intervals, censored
  time-to-solution and quality/cost curves; report timeouts and all negative results.
  Use the predeclared paired statistical procedure.
- Reproduce successes and failures with independent exact checking, deterministic
  fixed-step resume and measured timing variance. Confirm the P34 operating envelope for
  the frozen workload; do not substitute a microbenchmark rate for complete search
  performance.
- Export a standalone predictor/proposer including weights when used, bytecode,
  constants, schema, domains and verifier evidence. Predictions from a selected model
  must run without starting evolutionary search.
- Publish accepted/provisional/rejected verdicts per claim. A full H1 claim additionally
  requires its original two named targets, >=80% confirmation success on each, honest
  baselines and original generalization/ablation criteria. A narrow-family win cannot
  silently replace H1.

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
python3 benchmarks/full_matrix.py --confirm-program --freeze-manifest experiments/p37-qrand-dependency-correlated.json --split-manifest experiments/p30-splits.json --seeds 20 --output experiments/p38-confirmation.json
```

A clean-environment reproduction bundle, complete final-test outcomes, access log and
usable exports with independent certificate checks. Negative findings are valid
completion. Integrity failures block P39; performance losers revert to the accepted
baseline in the next campaign.

## Resource and evidence contract

Use the accepted RTX 4060 Laptop operating envelope: current free VRAM minus
reserve, bounded chunks/buffers, explicit stream dependencies, synchronized
timing, controlled failure and complete checkpoints. Add streams/workers
only with measured benefit. Keep bytecode/data resident in the hot loop;
text conversion, exact checking and artifact I/O remain outside it and their
costs are disclosed. Record clean revision, full configuration, RNG state,
actual device, dataset/split/checker hashes and durable raw-artifact hashes.

## Risks

Repeated final-test peeking, selective reporting and operator identity can inflate
confidence. Registered tests control selection bias; runtime differences must be
reported statistically.

## Commit & Push (mandatory)

Start from a clean tree on `codex/p38-independent-confirmation` from the accepted
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
git commit -m "feat(bench): complete p38 independent-confirmation"
git push -u origin HEAD
gh pr create --title "feat(bench): complete p38 independent-confirmation" --body-file /tmp/evobyte-p38-pr.md
git status --short
```
