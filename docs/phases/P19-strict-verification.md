# P19 — Strict verification and discovery evidence

**Status:** Proposed.
**Prerequisite:** P18.
**Owner:** assigned when moving to Building; see the phase index.

## Objective

Separate a fast search score from a trustworthy claim of mathematical
rediscovery, preserving unseen data until the experiment is frozen.

## Scope and ordered work

- Implement a true float64 execution path for promoted programs: inputs,
  constants, registers and arithmetic must use the required precision.
  Casting float32 predictions after execution is insufficient.
- Validate on disjoint in-domain data, extrapolation on both domain sides
  where meaningful, and adversarial points near singularities/boundaries.
  Compare protected VM behavior with ordinary mathematical domains.
- Freeze winners/configurations using training/validation evidence before
  final hidden evaluation. Hidden results never influence resampling,
  stopping, promotion, tuning or the next task's training corpus.
- Add symbolic equivalence where applicable; otherwise report numerical
  evidence with domain, tolerance and failure limits, not a proof claim.
- Persist complete bytecode, fitted constants/linear head, opcode version,
  units/domain, hashes and verifier outcome. Use null for unmeasured archive
  errors; default zero must never imply perfect held-out performance.
- Require hidden and extrapolation evidence before Hall of Fame promotion;
  keep provisional training elites separate from confirmed discoveries.

L2 and evidence storage only; no symbolic parsing in L1 and no changes to
v0 execution semantics without versioning.

## Exit gate

The phase-specific CLI below is an acceptance interface to implement during
this phase, not a claim that the current checkout supports it. Common checks
already exist. Run the experiment only after its prerequisite is green.

```bash
git diff --check
python3 -m pytest tests -q
make verify
python3 benchmarks/synthetic.py --strict-verification --seeds 5 --output experiments/p19-l2.json
```

Known-correct programs pass; deliberate overfits, protected-domain exploits
and a rounding-sensitive float32/float64 example fail appropriately. Audit
logs show hidden data absent from the search and selection process. Exported
candidate-plus-constants reproduces its recorded predictions.

## Risks

Repeated hidden-set inspection creates adaptive leakage. Protected
operators can fit samples while representing a different mathematical law.

## Commit & Push (mandatory)

Start from a clean tree on `codex/p19-strict-verification`. Follow the common
commit procedure in [README.md](README.md#commit-and-push-contract), using
this phase's exact reviewed file list and artifact manifest. One completed
micro-task produces one atomic commit; never commit a failed gate.

```bash
git status --short
git diff --check
git diff --cached --check
git commit -m "feat(bench): complete p19 strict-verification"
git push -u origin HEAD
gh pr create --title "feat(bench): complete p19 strict-verification" --body-file /tmp/evobyte-p19-pr.md
git status --short
```
