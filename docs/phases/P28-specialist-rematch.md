# P28 — New specialist micro-model (narrow family, own hypothesis)

**Status:** Proposed.
**Prerequisite:** P25 corpus sealed AND P26 lineage available. The P23 DROP
(27,440-param proposer, billed, `experiments/p23-pilot.json`) stays on
record; this phase tests a different architecture/hypothesis, not a retry
of the same bet.
**Owner:** assigned when moving to Building; see the phase index.

## Objective

Train a new <= 5M specialist for ONE narrow family first (e.g. arithmetic
expressions or polynomial identities): problem features in, batched
ops/operands/constants/mutations out. Win requires reproducible advantage
over controls on held-out families with all costs billed. A second DROP is
a complete, valid outcome.

## Scope

In: one preregistered narrow family, problem featurizer, three contestants
(statistical distributor, small multi-head net emitting fields jointly,
short sequential model — small first, 5M ceiling), training on solved
problems + verified candidates + rejected examples, penalties for
duplicates/invalid/verifier-gaming, mandatory random-exploration floor,
billed train/infer/diversity/time-to-solution accounting, amortized
cost-per-query over declared problem counts.
Out: broad multi-family claims (that is P22), > 5M without ADR, hidden-set
training, LLM conditioning, re-litigating P23 (its DROP stands as its own
result).

## Ordered work

- Preregister the family, hypothesis (why THIS architecture beats P23's),
  minimum time-to-quality benefit and maximum throughput penalty.
- Build the featurizer + three contestants under the param/VRAM caps.
- Train with the penalty schedule (duplicates, invalid, gaming) and the
  exploration floor; log every billed cost.
- Equal wall-clock comparison vs genetic + distributor on held-out
  families; amortize over 1/10/100/1000 new problems.
- KEEP needs an ADR superseding D010 for this family with evidence; DROP
  keeps genetic default. Publish negatives fully.

## Max-GPU rule (standing)

Training in micro-batches under the adaptive VRAM budget, inference fused
and batched, CPU workers on data/lineage, billed peaks recorded. No crash,
no hidden cost.

## Exit gate

The phase-specific CLI below is an acceptance interface to implement during
this phase, not a claim that the current checkout supports it. Common checks
already exist. Run the experiment only after its prerequisite is green.

```bash
git diff --check
python3 -m pytest tests -q
make verify
python3 benchmarks/math_specialist.py --family <name> --seeds 5 --output experiments/p28-specialist.json
```

Artifact: checksummed `experiments/p28-specialist.json` with family
definition, billed costs, held-out 4-way table, amortized analysis and the
keep/drop ruling (+ADR on KEEP). Done means a reproducible verdict on the
new hypothesis — not a useful specialist by declaration.

## Risks

Family too narrow to matter, gaming the verifier instead of solving,
amortization math hiding training cost, P23-rerun disguised as novelty
(the hypothesis delta must be explicit and falsifiable).

## Commit & Push (mandatory)

Start from a clean tree on `codex/p28-specialist`. Follow the common
commit procedure in [README.md](README.md#commit-and-push-contract), using
this phase's exact reviewed file list and artifact manifest. One completed
micro-task produces one atomic commit; never commit a failed gate.

```bash
git status --short
git diff --check
git diff --cached --check
git commit -m "feat(bench): complete p28 specialist"
git push -u origin HEAD
gh pr create --title "feat(bench): complete p28 specialist" --body-file /tmp/evobyte-p28-pr.md
git status --short
```
