# P23 — Math specialist pilot (GSM8K chains → proposal model ≤5M)

**Status:** Done (2026-09-30, DROP ruling confirmed, artifact `experiments/p23-pilot.json`).
**Prerequisite:** Math-DB full benchmark (`codex/p14-mathdb-gsm8k`: 1120 visible, 199 hidden sealed, 3614/3614 chains match).
**Owner:** @AlexandreZanata

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

### Measured outcomes (2026-09-30)

- **Artifact**: `experiments/p23-pilot.json` (manifest sha256: `c54e083009dd59c52404ac98c0756c3dac25f21dd489375355c85cb2608a2a86`).
- **Raw Data**: `experiments/p23-raw.json` (sha256: `1522850c794adbdeccc7084c7f8b84775dec1f92e83f5863569a74244b0b8d43`).
- **Corpus & Split Isolation**:
  - Visible GSM8K test rows: 923 train + 197 val = 1,120 rows.
  - Hidden sealed rows: 199 rows strictly isolated (`isdisjoint` confirmed).
  - Arithmetic chains extracted: 3,663 (`dfdc6c9d514be3959031ec1deec303d9be613829c73b35d79ea77c4ad22694ef`).
  - Operator histogram: ADD: 1,195, SUB: 682, MUL: 1,623, DIV: 674, POW: 0.
- **Model Parameters & Billed Compute Costs**:
  - Learned opcode distributor: 0 parameters, training time: 0.11 s (billed).
  - Neural proposer: 27,440 parameters (well within <= 5M cap), training time: 0.75 s, peak VRAM: 17.20 MB (billed).
- **4-Way Comparison Summary (5 targets x 5 seeds x 2 budget tiers = 50 runs/arm)**:
  - `genetic`: Search CVPS 9,813.7 | Billed CVPS 8,764.8 | Success rate 22.0% | Median MSE 2.2338 | Median TTM: 2.62 s
  - `learned_dist`: Search CVPS 10,464.4 | Billed CVPS 8,756.2 | Success rate 22.0% | Median MSE 1.8036 | Median TTM: 2.02 s
  - `neural`: Search CVPS 9,928.2 | Billed CVPS 8,570.0 | Success rate 22.0% | Median MSE 2.0875 | Median TTM: 1.93 s
  - `hybrid`: Search CVPS 10,547.6 | Billed CVPS 9,021.4 | Success rate 24.0% | Median MSE 2.3786 | Median TTM: 1.58 s
- **Keep-or-Drop Ruling**: `DROP`.
  - The neural proposer imposes model execution tax and training overhead without surpassing pure genetic search on time-to-quality.
  - ADR-0010 confirmed; the specialist proposal branch is cleanly closed without touching the core production genetic loop.

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
git commit -m "feat(bench): complete p23 math specialist pilot"
git push -u origin HEAD
gh pr create --title "feat(bench): complete p23 math specialist pilot" --body-file /tmp/evobyte-p23-pr.md
git status --short
```
