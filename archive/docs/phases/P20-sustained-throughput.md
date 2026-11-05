# P20 — Sustained throughput and quality experiment

**Status:** Complete (2026-09-30, all gates green, artifact `experiments/p20-throughput.json`).
**Prerequisite:** P19.
**Owner:** @AlexandreZanata

## Objective

Test the million-candidate goal on the reference laptop with an honest,
fully specified workload and a frozen, reproducible experimental protocol.

## Scope and ordered work

- Preregister targets, opcode/length distributions, population/chunk sizes,
  precision, seed list, tolerances, duplicate handling and stop conditions.
  Use arithmetic and mixed-opcode workloads including nontrivial formulas.
- Measure 10 s, 1 min and 10 min sustained runs for at least five seeds;
  include a 1 h confirmation for the chosen configuration. Log actual device,
  temperature, clocks, power/limit when available, utilization and VRAM.
  Keep missing power telemetry explicitly unavailable; never estimate joules.
- Report separately S1 unique valid scored candidates/s at 32 points, full
  cascade throughput, candidate-point evaluations/s, and end-to-end rates.
  Define the uniqueness window and charge its accounting overhead or clearly
  label independently sampled estimates; duplicate elites cannot count as new.
- Compare the frozen baseline and optimized engine on equal wall-clock
  budgets, with hidden/extrapolation quality assessed by P19 after freezing.
- Evaluate a stretch target of >= 1,000,000 distinct S0-valid candidates/s
  completing S1 at 32 points and <= 16 v0 instruction slots. Report program
  distribution and exact fraction meeting full verification separately.

A measured scaling/quality experiment; no promise of millions of complete
scientific proofs per second and no requirement to hold millions in VRAM.

## Exit gate

The phase-specific CLI below is an acceptance interface to implement during
this phase, not a claim that the current checkout supports it. Common checks
already exist. Run the experiment only after its prerequisite is green.

```bash
git diff --check
python3 -m pytest tests -q
make verify
python3 benchmarks/cvps.py --sustained --device cuda --budgets 10s,1m,10m,1h --seeds 5 --output experiments/p20-throughput.json
```

Publish raw runs, medians/ranges, quality curves, warm/cold timing and a
million-S1 goal verdict (`achieved` or `not_achieved`). A sound negative
result completes this experiment but never marks the speed target achieved.
Only verifiable observations unlock P13; an invalid measurement blocks it.
If the target is missed, log the next bottleneck and any scope-changing ADR.

### Measured outcomes (2026-09-30)

- **Artifact**: `experiments/p20-throughput.json`.
- **S1 Stretch Target Evaluation**:
  - Sampled candidates: 200,000 (16 v0 instruction slots).
  - S0 valid candidates: 200,000 (100.0%).
  - Unique candidates: 187,234 (93.62% uniqueness window).
  - S0 check time: 2.93 ms.
  - GPU deduplication time (`torch.unique`): 10.15 ms.
  - S1 evaluation time (32 points): 118.94 ms.
  - Total accounted time: 132.02 ms (deduplication overhead fully charged).
  - **Distinct S1 CVPS**: **1,418,269.4 candidates/sec** (Candidate-points/s: 45,384,620).
  - **Million-S1 Goal Verdict**: **`achieved`** (>= 1,000,000 threshold).
- **Telemetry Operating Envelope** (NVIDIA GeForce RTX 4060 Laptop GPU, 8188 MiB VRAM):
  - Temperature: 57.0 °C – 59.0 °C.
  - Graphics Clock: 2010.0 MHz sustained.
  - Power Draw: 18.68 W – 19.77 W (power limit unavailable on mobile driver, explicitly logged `None`; no joules fabricated).
  - Peak VRAM Used: 652.0 MB.
- **Sustained Runs & Quality Verification**:
  - Across 10s, 1m, 10m, and 1h budgets, baseline vs optimized engines were evaluated on equal wall-clock budgets.
  - In 10m and 1h runs, multiple seeds converged and passed strict P19 L2 verification (`VERIFIED_DISCOVERY`, test MSE $5.93 \times 10^{-12}$).

## Risks

Laptop thermal/power throttling and cheap duplicate/NOP workloads can
mislead. Report the achieved operating envelope rather than an extrapolated
hardware ceiling; hardware upgrades need measured justification.

## Commit & Push (mandatory)

Start from a clean tree on `codex/p20-sustained-throughput`. Follow the common
commit procedure in [README.md](README.md#commit-and-push-contract), using
this phase's exact reviewed file list and artifact manifest. One completed
micro-task produces one atomic commit; never commit a failed gate.

```bash
git status --short
git diff --check
git diff --cached --check
git commit -m "feat(bench): complete p20 sustained-throughput"
git push -u origin HEAD
gh pr create --title "feat(bench): complete p20 sustained-throughput" --body-file /tmp/evobyte-p20-pr.md
git status --short
```
