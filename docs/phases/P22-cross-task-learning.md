# P22 — Optional learning across tasks

**Status:** Done (2026-09-30; verdict DROP, D010 stands; artifact `experiments/p22-transfer.json`; `make verify` + `pytest` green).
**Prerequisite:** P21; optional separate experiment after the core mechanism is evaluated.
**Owner:** executed on `codex/p22-cross-task-learning` from `5f9c129`.

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

### Empirical artifact (2026-09-30, RTX 4060 Laptop, torch 2.14.0+cu130)

Families preregistered by structure: train `quad` (x^2+3x+7, sha16
`3e05172a75a520ee`), held-out `cubic` (x^3-2x+1, `19e57c107af80d31`) and
`sinlin` (sin(x)+2x+1, `a49cf5a026aca8a4`). Equal budgets (15 s per
method/task/seed, 5 seeds [42,101,202,303,404]); neural <= 5M params trained
offline on train elites only and billed; hidden splits scoring-only.

| Held-out task | Genetic hidden MSE | Best learned (benefit / CVPS ratio) | Pass |
|:---|:---:|:---:|:---:|
| cubic | 0.507 | learned-dist (+0.4% / 53.6%) | FAIL |
| sinlin | 0.444 | learned-dist (+0.7% / 64.6%) | FAIL |

Genetic also wins outright on hidden MSE (cubic 0.507 vs 0.586-1.300;
sinlin 0.444 vs 0.530). Neural generator has 412,080 params (<= 5M cap) and
its frozen CVPS is only 38-40% of genetic; the hybrid matches genetic
throughput on sinlin (103%) but with worse quality. Verdict **DROP**: no
learned configuration reaches the preregistered +15% time-to-quality
benefit with CVPS >= 70% on either held-out family (0/5 successes everywhere
at these budgets; amortized cost 71.0 s per new task including 21.3 s
archive + billed neural training). D010 stands; the production search
remains genetic. No ADR required.

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
