# P15 — Measurement integrity and reproducible harness

**Status:** Done (2026-09-29; audit manifest `0a42178c423cd120`; `make verify` + `pytest` green; short real run + not_run fixture validate counters/manifest).
**Prerequisite:** P12; evidence review takes priority over any provisional P13 verdict.
**Owner:** codex/p15-measurement-integrity.

## Objective

Establish trustworthy counters, timing and provenance before optimizing or
making comparative claims. Audit the P13 draft and legacy P05/P06/P12
reports against executable code and raw artifacts; retain history, but mark
unsupported conclusions as unverified and supersede their decisions.

## Scope and ordered work

- Replace fabricated PySR results and fixed ablation outputs with actual
  execution or explicit `not_run` records. Missing dependencies never count
  as wins or zero error. No result may be inferred from the target name.
- Distinguish VM-only throughput, S0 validity, scored S1 completions, full
  cascade completions and end-to-end search. Count repeats and distinct
  candidates separately with a documented bounded-memory counting method.
- Enforce a monotonic deadline for each method/target/seed/budget. Include
  generation, transfers, selection, fitting and online training; log setup,
  compilation, warmup, final verification and deadline overshoot separately.
  GPU work must finish before timing stops. Never synthesize budget curves.
- Save machine-readable per-run manifests and raw observations under
  `experiments/`; implement the provenance contract in REPRODUCIBILITY.md.
  Seed NumPy and all PyTorch CPU/CUDA RNGs. CUDA requests must fail explicitly
  if CUDA is unavailable, instead of silently reporting CPU as GPU.
- Remove lint failure suppression in Makefile/CI, fix resulting violations
  without weakening rules, and install the CPU torch dependency in CI.
  Test counter accuracy, missing-baseline behavior, deadlines, manifest
  hashes and that changing an ablation actually changes the executed path.

Extend existing benchmark modules and tests; no search algorithm changes,
performance claims, full expensive matrix or forced positive H1 verdict.

## Exit gate

The phase-specific CLI below is an acceptance interface to implement during
this phase, not a claim that the current checkout supports it. Common checks
already exist. Run the experiment only after its prerequisite is green.

```bash
git diff --check
python3 -m pytest tests -q
make verify
python3 benchmarks/full_matrix.py --audit-only --output experiments/p15-audit.json
```

An audit bundle maps every retained claim to raw evidence or `unverified`;
a short real run and unavailable-baseline fixture validate the manifest and
counter contract. Tests must reject hard-coded results, unexecuted ablations,
mislabelled devices and rescaled budget records. Full lint/test/verify gates
pass without suppression. P13 remains locked until P20.

## Risks

A smoke test passing is not proof of a scientific claim. Keep raw records
and explicit missing evidence; do not replace historical numbers with new
unsupported numbers.

## Commit & Push (mandatory)

Start from a clean tree on `codex/p15-measurement-integrity`. Follow the common
commit procedure in [README.md](README.md#commit-and-push-contract), using
this phase's exact reviewed file list and artifact manifest. One completed
micro-task produces one atomic commit; never commit a failed gate.

```bash
git status --short
git diff --check
git diff --cached --check
git commit -m "feat(bench): complete p15 measurement-integrity"
git push -u origin HEAD
gh pr create --title "feat(bench): complete p15 measurement-integrity" --body-file /tmp/evobyte-p15-pr.md
git status --short
```
