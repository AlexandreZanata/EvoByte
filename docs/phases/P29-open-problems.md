# P29 — Open problems with verifiable certificates

**Status:** Proposed.
**Prerequisite:** P26 lineage (ancestry/audit) AND P28 verdict recorded.
Only finalists reach exact checking; the search stays stochastic.
**Owner:** assigned when moving to Building; see the phase index.

## Objective

Aim the mature pipeline (stable GPU limits, sealed corpora, lineage,
controls) at bounded open problems where a result can be CERTIFIED:
combinatorial constructions, identities, counterexamples, finite instances
of Diophantine problems. GPU generates/filters; exact arithmetic,
independent verification and (for universal claims) formal proof decide.
Many favorable numeric tests support a conjecture; a universal statement
requires proof (e.g. Lean, https://lean-lang.org/doc/reference/latest/ValidatingProofs/).

## Scope

In: problem nominations with bounded search + decidable checker,
GPU generate/filter campaigns with lineage, exact-arithmetic finalist
verification, independent reproduction of each claimed result, Lean proof
artifacts for universal claims, classification of every outcome as
rediscovery / candidate / verified-construction / counterexample /
proven-theorem.
Out: "discovery" from numeric fit alone, unbounded conjectures presented
as theorems, proof by authority or by plot, skipping the novelty
literature check.

## Ordered work

- Nominate problems with: bounded statement, checker definition,
  novelty-search plan, certificate type. Preregister before searching.
- Campaign on GPU with full P26 lineage; promote finalists only through
  the exact checker + independent reproduction (different seed/operator
  where applicable).
- For universal claims: formalize and machine-check the proof; store the
  proof artifact with its checker version.
- Literature novelty check for each claimed result; classify honestly,
  including "candidate (unproven)" and "null after budget".
- Publish the certificate bundle per result; a null campaign with intact
  lineage completes honestly.

## Discovery criterion (binding)

A scientific discovery counts iff ALL hold: correct result, novelty
confirmed against the literature, independent reproduction, and the
appropriate certificate or proof. Until then the honest labels are
rediscovery, candidate, or null. No validated novel mathematical
discovery exists in this project to date.

## Max-GPU rule (standing)

Generate/filter at P24 stable limits with lineage on; exact checking and
proof work off-GPU on CPU workers. Certificates, not throughput, are the
headline metric here.

## Exit gate

The phase-specific CLI below is an acceptance interface to implement during
this phase, not a claim that the current checkout supports it. Common checks
already exist. Run the experiment only after its prerequisite is green.

```bash
git diff --check
python3 -m pytest tests -q
make verify
python3 benchmarks/open_problems.py --problem <id> --output experiments/p29-<id>.json
```

Artifact: checksummed per-problem JSON (nomination, campaign lineage ref,
checker evidence, reproduction, classification) plus certificate/proof
artifacts where claimed. Done means certified results or honest
nulls/candidates — never an uncertified "discovery".

## Risks

Moving goalposts on "bounded", checker bugs certifying falsehoods (checker
itself needs tests + review), proof artifacts that don't actually check,
confusing a fast campaign with a result. The checker is part of the claim
and must be reviewed as such.

## Commit & Push (mandatory)

Start from a clean tree on `codex/p29-<id>`. Follow the common
commit procedure in [README.md](README.md#commit-and-push-contract), using
this phase's exact reviewed file list and artifact manifest. One completed
micro-task produces one atomic commit; never commit a failed gate.

```bash
git status --short
git diff --check
git diff --cached --check
git commit -m "feat(science): complete p29 <id>"
git push -u origin HEAD
gh pr create --title "feat(science): complete p29 <id>" --body-file /tmp/evobyte-p29-pr.md
git status --short
```
