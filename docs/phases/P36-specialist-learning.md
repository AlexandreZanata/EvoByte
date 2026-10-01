# P36 — Specialist learning from certified solutions

**Status:** Proposed.
**Prerequisite:** Accepted P35 corpus and P34 resource configuration.
**Owner:** assigned when moving to Building.
**Branch:** `codex/p36-specialist-learning`.

## Objective

Test whether learning improves verified time-to-quality in the declared family, using
correct supervision and adequate budgets. Preserve the P12/P23/P28 negative findings as
scoped history.

## Scope

Learning and comparison in existing math_specialist/generator modules. No >5M expansion,
language-model API, new family or final-test tuning. KEEP requires an ADR superseding
D010 for this specific family only.

## Ordered work

- Preregister a counting/distribution baseline, joint-output network and short
  sequential proposer, initially <=5M parameters. Specify how sampled
  opcodes/operands/register dependencies are conditioned; a GRU receiving only
  positional inputs does not establish conditioning on previously sampled instructions.
- Train on certified positives and explicitly labelled negatives with grammar/type
  masks, constant handling, duplicate/invalidity penalties and a fixed
  random-exploration floor. Track train/validation curves and candidate certificate
  rates; choose stopping on validation, not a fixed five-epoch success declaration.
- Compare random/structured, genetic, distributor, neural and hybrid arms using
  identical tasks, total resources and real wall-clock budgets. Measure pure proposal
  and proposal+genetic separately. Match initialization rules and account for
  corpus/teacher, training, inference and tracking.
- Use development held-out problem/template groups for the five-seed pilot at 10 s/1
  min/10 min, not the untouched P38 test. Report censored failures, verified success,
  actual time-to-solution, diversity and quality per target.
- Freeze the exact quality/time criterion before results; report intervals and paired
  outcomes. A 20% time-to-quality improvement is the initial adoption target, with
  throughput/VRAM limits declared per workload. Do not select one network by throughput
  then use another network's quality to award KEEP.
- Export selected weights, bytecode schema, constants/linear heads, domains and
  versioned prediction/proposal commands. Publish observed and modelled amortized costs
  separately over declared query counts.

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
python3 benchmarks/math_specialist.py --train-certified --corpus-manifest experiments/p35-training-corpus.json --family polynomial_arithmetic --budgets 10s,1m,10m --seeds 5 --output experiments/p36-specialist.json
```

A fully billed, certificate-based pilot verdict and reproducible model artifacts.
KEEP/DROP/inconclusive are valid outcomes; lack of successes cannot support a
time-to-solution win. P37 uses the accepted genetic baseline when the specialist is not
promoted.

## Resource and evidence contract

Use the accepted RTX 4060 Laptop operating envelope: current free VRAM minus
reserve, bounded chunks/buffers, explicit stream dependencies, synchronized
timing, controlled failure and complete checkpoints. Add streams/workers
only with measured benefit. Keep bytecode/data resident in the hot loop;
text conversion, exact checking and artifact I/O remain outside it and their
costs are disclosed. Record clean revision, full configuration, RNG state,
actual device, dataset/split/checker hashes and durable raw-artifact hashes.

## Risks

Fast fitting on poor labels and mean-MSE changes can be mistaken for solving.
Extrapolation/family transfer claims require separate evidence; a failed small model
does not disprove all learning approaches.

## Commit & Push (mandatory)

Start from a clean tree on `codex/p36-specialist-learning` from the accepted
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
git commit -m "feat(generator): complete p36 specialist-learning"
git push -u origin HEAD
gh pr create --title "feat(generator): complete p36 specialist-learning" --body-file /tmp/evobyte-p36-pr.md
git status --short
```
