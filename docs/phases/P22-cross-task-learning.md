# P22 — Optional learning across tasks

**Status:** Proposed.
**Prerequisite:** P21; optional separate experiment after the core mechanism is evaluated.
**Owner:** assigned when moving to Building; see the phase index.

## Objective

Test whether learning from earlier discoveries improves unfamiliar tasks,
while preserving the genetic engine as a control and D010 as the default.

## Scope and ordered work

- Preregister disjoint problem families for training, validation and final
  evaluation. Split by structure/family, not just points of the same formula;
  keep held-out benchmark solutions and test trajectories out of archives.
- Compare genetic search, a simple learned opcode/mutation distribution,
  a <= 5M-parameter neural proposal model and a hybrid under equal search
  budgets. Neural training is offline or explicitly budgeted, not a hidden
  cost charged only to the baseline.
- Report cold-start cost and amortized cost across a declared number of
  new tasks, including training, archive construction, inference and VRAM.
  Apply at least the P13 pilot/confirmation seed discipline.
- Enforce the same P19 final evaluation and P20 throughput accounting.
  Preregister a minimum time-to-quality benefit and acceptable throughput
  penalty, then retain only configurations supported across held-out tasks.
- A KEEP result requires an ADR superseding D010 with evidence. A DROP/null
  result is valid; the existing single-target result is not a universal
  rejection of all learned proposal methods.

Transfer of symbolic-search experience; no LLM in the hot path, no general
intelligence claim and no dependency for the P14 scientific-data gate.

## Exit gate

The phase-specific CLI below is an acceptance interface to implement during
this phase, not a claim that the current checkout supports it. Common checks
already exist. Run the experiment only after its prerequisite is green.

```bash
git diff --check
python3 -m pytest tests -q
make verify
python3 experiments/p12_generator_ab.py --cross-task --seeds 5 --output experiments/p22-transfer.json
```

A reproducible held-out-family report includes all compute costs, resource
caps and a preregistered keep/drop verdict. Missing transfer benefit leaves
the production search genetic; merely fitting training elites does not pass
as learned generalization.

## Risks

Family leakage, archive contamination and unbilled training can manufacture
an apparent benefit. The hardware budget and scientific split contract apply.

## Commit & Push (mandatory)

Start from a clean tree on `codex/p22-cross-task-learning`. Follow the common
commit procedure in [README.md](README.md#commit-and-push-contract), using
this phase's exact reviewed file list and artifact manifest. One completed
micro-task produces one atomic commit; never commit a failed gate.

```bash
git status --short
git diff --check
git diff --cached --check
git commit -m "feat(bench): complete p22 cross-task-learning"
git push -u origin HEAD
gh pr create --title "feat(bench): complete p22 cross-task-learning" --body-file /tmp/evobyte-p22-pr.md
git status --short
```
