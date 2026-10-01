# P39 — Bounded mathematical campaign with novelty review

**Status:** Proposed.
**Prerequisite:** Accepted P38 integrity and frozen pipeline; P31 independent certificate checkers.
**Owner:** assigned when moving to Building.
**Branch:** `codex/p39-certified-science`.

## Objective

Apply the verified search platform to one bounded mathematical target and assess whether
the result contributes new knowledge. Certificates and novelty, not throughput alone,
determine the scientific claim.

## Scope

One campaign in open_problems with the existing checker/lineage stack. No concurrent
broad conjecture hunt, unbounded mathematical map or post hoc relaxation of bounds.
Additional targets are separate research cycles.

## Ordered work

- Nominate one current research question with precise statement, integer/rational
  domains, bounds, decidable verifier, baseline constructions and novelty-search plan.
  Confirm its status in current primary literature; known solved/nonexistence results
  are benchmarks, not newly open conjectures.
- Separate an instance/construction search from a universal theorem claim. Define
  complete search coverage versus stochastic/budget-limited exploration; a failed finite
  search is not a counterexample to an existential conjecture.
- Execute the frozen P38 method with a matched arithmetic/structured baseline, P34 safe
  limits, full P32 lineage and checkpoint/resume. Guard integer overflow on GPU and
  promote finalists to independent arbitrary-precision checking.
- Enforce nominated bounds for all constrained coordinates. Store an individual
  certificate for every claimed instance, coverage/budget records for nulls and
  retrievable raw evidence. Recheck the nomination statement as well as the numeric
  result.
- Search the literature/catalogues for each potential new result and state limitations
  of novelty verification. A previously uncatalogued instance alone is not proof of a
  new theorem. Universal claims require an appropriate formal proof and checker version.
- Obtain independent reproduction/review where available and publish one of rediscovery,
  candidate, verified-construction, counterexample, proven-theorem, exhaustive_null or
  budget_exhausted. Explain which evidence is missing for a stronger classification.

## Exit gate

The phase-specific CLI below is an interface to implement during this phase;
it is not a claim that these flags already exist. Run its experiment only
after prerequisites and common checks pass. Freeze configurations before
measurement. Complete one bounded micro-task at a time; failed correctness
or integrity gates block commit/push. A sound negative experiment is not a
reason to weaken its registered thresholds.

```bash
git diff --check
git status --short
python3 -m pytest tests -q
make verify
python3 benchmarks/open_problems.py --problem erdos-straus --certified-campaign --freeze-manifest experiments/p38-confirmation.json --nomination experiments/p39-nomination.json --output experiments/p39-science.json
```

A preregistered nomination plus independently checked, bounded certificates or honest
null/budget result, full provenance and novelty assessment. A scientific discovery
requires correctness, established novelty, independent reproduction and appropriate
certificate/proof; otherwise retain the weaker label.

## Resource and evidence contract

Use the accepted RTX 4060 Laptop operating envelope: current free VRAM minus
reserve, bounded chunks/buffers, explicit stream dependencies, synchronized
timing, controlled failure and complete checkpoints. Add streams/workers
only with measured benefit. Keep bytecode/data resident in the hot loop;
text conversion, exact checking and artifact I/O remain outside it and their
costs are disclosed. Record clean revision, full configuration, RNG state,
actual device, dataset/split/checker hashes and durable raw-artifact hashes.

## Risks

Efficient arithmetic filtering can rediscover known constructions. A checksum does not
certify mathematics, and millions of tested instances do not prove a universal
statement.

## Commit & Push (mandatory)

Start from a clean tree on `codex/p39-certified-science` from the accepted predecessor.
Follow [README.md](README.md#commit-and-push-contract); explicitly stage
only reviewed implementation/test/documentation files and the small phase
manifest. Never commit large/private raw data. Create/update a PR against
the accepted predecessor (or main after it is integrated), then confirm a
clean tree. Each finished micro-task produces one atomic commit after all
its applicable gates pass; the block below is for final phase completion.

```bash
git status --short
git diff --check
git diff --cached --check
git commit -m "feat(science): complete p39 certified-science"
git push -u origin HEAD
gh pr create --title "feat(science): complete p39 certified-science" --body-file /tmp/evobyte-p39-pr.md
git status --short
```
