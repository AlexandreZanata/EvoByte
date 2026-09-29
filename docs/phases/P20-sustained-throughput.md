# P20 — Sustained throughput and quality experiment

**Status:** Proposed.
**Prerequisite:** P19.
**Owner:** assigned when moving to Building; see the phase index.

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
