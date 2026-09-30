# P23 — Math specialist pilot (GSM8K chains → proposal model ≤5M)

**Status:** Proposed.
**Prerequisite:** Math-DB full benchmark (`codex/p14-mathdb-gsm8k`: 1120 visible, 199 hidden sealed, 3614/3614 chains match).
**Owner:** assigned when moving to Building; see the phase index.

## Objective

Test whether a small proposal model trained on GSM8K arithmetic chains adds
anything per wall-clock second over pure genetic search, with every compute
cost billed. This is the pilot for the optional P22 transfer program: a
KEEP here (with ADR) unlocks P22 held-out-family confirmation; a DROP/null
closes the specialist line without touching the production genetic loop.

## Scope

In: opcode/mutation distributor + tiny neural proposer (each <= 5M params,
VRAM-capped), corpus built ONLY from train/val chains (hidden sealed),
equal wall-clock 4-way comparison
(genetic vs learned-dist vs neural vs hybrid), billed training/inference
cost, keep-or-drop ruling with ADR on KEEP.
Out: LLMs in the hot path, hidden-split training, > 5M params without ADR,
any claim on held-out families (that is P22), changes to v0 semantics.

## Ordered work

- Sample GSM8K train/val `<<expr=result>>` chains into an opcode/mutation
  corpus (operator histogram + mutation contexts). Hidden 199 stay sealed;
  corpus hash pinned in the manifest. No natural-language conditioning.
- Train offline (or explicitly budgeted online): a counting-based opcode
  distributor first (cheapest baseline), then a <= 5M neural proposer.
  Record training wall-clock, VRAM peak and energy/telemetry when available.
  Training cost is billed to the learned arms, never hidden.
- Compare at equal search budgets (10 s / 1 min pilot, 5+ seeds): time to
  chain-match rate on train/val-sampled expression targets plus CVPS with
  the model cap charged. Preregister minimum time-to-quality benefit and
  maximum acceptable throughput penalty before running.
- Publish the 4-way table, all failed/time-limited runs, billed totals and
  the ruling. KEEP requires an ADR superseding D010 for this corpus with
  evidence; DROP/null is valid and keeps genetic as default.

Corpus + pilot comparison only; no held-out-family generalization claim.

## Max-GPU rule (standing)

All execution uses the max of the RTX 4060 Laptop without crashing: VRAM
budget 7000 MB, chunk cap 20000, 8 CPU threads, 2 CUDA streams,
`empty_cache` + `synchronize` before timing, OOM halving. Same rule applies
to training (micro-batches under the cap) and to every comparison arm.

## Exit gate

The phase-specific CLI below is an acceptance interface to implement during
this phase, not a claim that the current checkout supports it. Common checks
already exist. Run the experiment only after its prerequisite is green.

```bash
git diff --check
python3 -m pytest tests -q
make verify
python3 benchmarks/math_specialist.py --pilot --seeds 5 --output experiments/p23-pilot.json
```

Artifact: checksummed `experiments/p23-pilot.json` with corpus hash, billed
training cost, 4-way medians/ranges, per-criterion keep/drop ruling and a
durable raw-artifact reference. A negative pilot completes the phase; only a
KEEP with ADR unlocks P22.

## Risks

Corpus leakage (hidden chains in training), unbilled training flattering the
neural arm, trivial-expression workloads overstating benefit. Family leakage
and archive contamination belong to P22 gates, not this pilot.

## Commit & Push (mandatory)

Start from a clean tree on `codex/p23-specialist-pilot`. Follow the common
commit procedure in [README.md](README.md#commit-and-push-contract), using
this phase's exact reviewed file list and artifact manifest. One completed
micro-task produces one atomic commit; never commit a failed gate.

```bash
git status --short
git diff --check
git diff --cached --check
git commit -m "docs(phases): add p23 math specialist pilot"
git push -u origin HEAD
gh pr create --title "docs(phases): add p23 math specialist pilot" --body-file /tmp/evobyte-p23-pr.md
git status --short
```
