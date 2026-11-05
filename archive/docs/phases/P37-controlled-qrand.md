# P37 — One controlled quantum-inspired sampling hypothesis

**Status:** Done.
**Prerequisite:** P32/P34 valid harness and P36 scoped verdict recorded.
**Owner:** Alexandre Zanata
**Result:** NULL — dependency-correlated bigram rotation shows no gain over the
matched classical bigram (both 0 verified; genetic baseline verifies 17.8% of
trials). Baseline selected; nothing nominated for P38.
**Branch:** `codex/p37-controlled-qrand`.

## Objective

Test one new sampling mechanism with fair controls and a mathematical falsification
rule. Preserve P27 as a short, single-target null pilot rather than a global rejection
of quantum-inspired search.

## Scope

One sampler intervention in qrand_ab and shared accepted engine; not simultaneous
quantum mechanisms, new datasets or a hardware-quantum claim.

## Ordered work

- Choose exactly one mechanism per cycle, for example dependency-correlated
  opcode/operand sampling or a tunneling-inspired structural jump. Freeze equations,
  classical implementation, prior-art review, affected operator and expected effect
  before running.
- Distinguish quantum inspiration from quantum hardware or advantage. A nonlinear
  probability parameterization alone does not demonstrate a new algorithm; compare a
  classical distribution with the same expressive capacity and update budget.
- Use the P33 grammar/initial distribution, length/live-op mix, constraints and
  verification across arms. Pair problem/seed, reset independent RNG streams, rotate arm
  order and match warmup/total resources. Avoid comparing dense random 16-op programs to
  a shorter structured genetic population as an attribution test.
- Run genetic, matched classical distribution and proposed mechanism at actual 10 s/1
  min/10 min budgets over at least five seeds and multiple development tasks. Exclude
  final-test exposure and include tracing/update/sampling costs.
- Report verified solutions per second and censored time-to-solution as primary
  outcomes, with diversity as secondary. Label finite probe signatures as behaviors.
  Preregister effect size and uncertainty procedure; do not infer significance from a
  mean or add post hoc OR/AND verdict rules.
- Record gain/loss/null, all failures and resource envelope. Every additional mechanism
  requires a new preregistration, isolated micro-task, artifact and commit on its own
  branch.

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
python3 benchmarks/qrand_ab.py --hypothesis dependency-correlated --controlled --budgets 10s,1m,10m --seeds 5 --output experiments/p37-qrand-dependency-correlated.json
```

A preregistered matched-control result with valid certificates, billed timing and
untouched final test. A sound null completes the cycle and leaves the baseline selected.
Only observed pilot gains are nominated for independent confirmation in P38.

## Resource and evidence contract

Use the accepted RTX 4060 Laptop operating envelope: current free VRAM minus
reserve, bounded chunks/buffers, explicit stream dependencies, synchronized
timing, controlled failure and complete checkpoints. Add streams/workers
only with measured benefit. Keep bytecode/data resident in the hot loop;
text conversion, exact checking and artifact I/O remain outside it and their
costs are disclosed. Record clean revision, full configuration, RNG state,
actual device, dataset/split/checker hashes and durable raw-artifact hashes.

## Risks

Changing multiple sampling rules obscures causality. Novelty needs literature evidence;
extra distinct bytes or randomness does not guarantee useful mathematical exploration.

## Commit & Push (mandatory)

Start from a clean tree on `codex/p37-controlled-qrand` from the accepted predecessor.
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
git commit -m "feat(bench): complete p37 controlled-qrand"
git push -u origin HEAD
gh pr create --title "feat(bench): complete p37 controlled-qrand" --body-file /tmp/evobyte-p37-pr.md
git status --short
```
