# P21 — Independent reproduction and usable model

**Status:** Done (2026-09-30; reproduction `experiments/p21-reproduction.json` PASS; 17 models verified without search; max-GPU suite `tests/test_max_gpu.py` 5/5 green on RTX 4060 Laptop).
**Prerequisite:** P13 completed with measured verdict and valid evidence.
**Owner:** codex/p21-independent-reproduction.

## Objective

Reproduce the frozen result in a clean environment and deliver the actual
learned predictor, including its constants and limits of validity.

## Scope and ordered work

- Pin dependencies, dataset/split hashes and code revision; document one
  runnable reproduction command and archive checksummed machine-readable
  results with a durable reference, not only an ignored local directory.
- Re-run predeclared representative successes and failures from a clean
  checkout without private caches. Compare trajectory determinism on the
  same stack and performance within predeclared statistical tolerance.
  Record independent reviewer/operator identity when available; do not
  claim independent authorship for a second run by the same operator.
- Export each selected model as bytecode plus constants/linear head, input
  schema, output schema, domain/units, verifier evidence and opcode version.
  A prediction command must run without starting the evolutionary search.
- Publish per-criterion H1 verdicts, all failed/time-limited runs, Pareto
  fronts per dataset, and practical hardware/expressivity limits.
- Decide P14 entry explicitly: both P13 support of unchanged H1 criteria and
  successful reproduction are required. Otherwise publish the negative result
  and propose a separately reviewed next experiment without weakening gates.

Reproduction and model export; no new search algorithm or retroactive
hyperparameter tuning against the final test results.

## Exit gate

The phase-specific CLI below is an acceptance interface to implement during
this phase, not a claim that the current checkout supports it. Common checks
already exist. Run the experiment only after its prerequisite is green.

```bash
git diff --check
python3 -m pytest tests -q
make verify
python3 benchmarks/full_matrix.py --reproduce-manifest experiments/p13-manifest.json --output experiments/p21-reproduction.json
```

A clean-environment reproduction report links to the original raw records;
the exported predictor reproduces verified values without search. Mark P14
eligible only with supported H1 and passing reproduction. A truthful negative
H1 outcome can complete P21 while P14 remains locked.

## Risks

A second run is not automatically an independent scientific replication.
Separate provenance verification, numerical reproducibility and speed variance.

## Commit & Push (mandatory)

Start from a clean tree on `codex/p21-independent-reproduction`. Follow the common
commit procedure in [README.md](README.md#commit-and-push-contract), using
this phase's exact reviewed file list and artifact manifest. One completed
micro-task produces one atomic commit; never commit a failed gate.

```bash
git status --short
git diff --check
git diff --cached --check
git commit -m "feat(bench): complete p21 independent-reproduction"
git push -u origin HEAD
gh pr create --title "feat(bench): complete p21 independent-reproduction" --body-file /tmp/evobyte-p21-pr.md
git status --short
```
