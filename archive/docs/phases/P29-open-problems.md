# P29 — Open problems with verifiable certificates

**Status:** Done (2026-10-01; certified erdos-straus rediscovery; artifact `experiments/p29-erdos-straus.json`; `make verify` green).
**Prerequisite:** P26 lineage (ancestry/audit) AND P28 verdict recorded.
Only finalists reach exact checking; the search stays stochastic.
**Owner:** Codex / Antigravity.


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

## Outcome & Certified Results

- **Nominated Problem:** `erdos-straus` (Erdős-Straus Diophantine Decomposition: $4/n = 1/x + 1/y + 1/z$).
- **Registry Suite Implemented:**
  - `erdos-straus`: Diophantine fraction problem with exact integer certificate.
  - `taxicab`: Hardy-Ramanujan cube sum collisions ($x^3 + y^3 = z^3 + w^3$).
  - `diophantine-quintuple`: Search for 5th extension to $\{1, 3, 8, 120\}$, certified bounded null.
- **Campaign Execution:**
  - **Candidates Filtered on GPU:** 1,085,094 candidates at 6,506,948 CVPS in 0.17s.
  - **Finalist Promoted to CPU:** $n = 1009 \implies x = 253, y = 85096, z = 1974822872$.
  - **Exact Arithmetic Check:** $\text{LHS} = 4xyz = 170066121441100544$, $\text{RHS} = n(xy+yz+xz) = 170066121441100544$, Residual = 0 (bit-exact).
  - **Independent Reproduction:** Pass; reproduction hash `4e1801ad2d7a1df00195087bb0333dd71586fa7ce73bdd8e312e5dcecf2212dd`.
- **Classification:** `rediscovery` (per P29 binding Discovery Criterion; matches known literature instances, Mordell 1967 / Elsholtz & Tao 2013).
- **Artifact:** `experiments/p29-erdos-straus.json` (checksummed manifest with raw trace and signed certificate).

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
