# P27 — Quantum-inspired randomness hypotheses (one per cycle, falsifiable)

**Status:** Done (2026-10-01; FALSIFIED_NULL recorded; amplitude-distribution vs 3 controls across 5 seeds; artifact `experiments/p27-qrand-amplitude-distribution.json`; `make verify` + `pytest` green).
**Prerequisite:** P26 lineage available.
**Owner:** executed on `codex/p27-qrand-amplitude-distribution` from `f943b65`.

## Objective

Test, one hypothesis per cycle, whether quantum-inspired sampling improves
relevant exploration or solution rate over uniform sampling, a simple
learned distribution and genetic evolution — same wall-clock, same
verifier, same problems, classical execution on the RTX 4060. Inspiration
is a claim about search distribution/dynamics, not quantum execution.
Prior art exists (e.g. https://arxiv.org/abs/quant-ph/0610105); literature
is checked before calling any mechanism novel.

## Scope

In: exactly one hypothesis per cycle from: amplitude-distribution sampling,
entanglement-inspired correlated variables, phase-combination operators,
tunneling-inspired structural jumps. Each needs equations, an implementable
mechanism and a falsifiable prediction. Controls: uniform, learned-dist,
genetic. Confirmation on held-out problems; null results published.
Out: quantum hardware/simulation claims, calling classical,//sampling
"quantum", multiple hypotheses per cycle, held-out contamination,
originality claims without literature check.

## Ordered work

- Preregister the single hypothesis: equations, mechanism, predicted effect
  and the falsification threshold — before implementation.
- Implement with lineage (P26) recording the sampler arm of every candidate.
- Run equal-budget comparisons with the three controls; report gains,
  losses and nulls with intervals on held-out splits.
- Literature check for the tested mechanism; record prior art or the
  bounded novelty claim explicitly.
- A second hypothesis is a new cycle (new preregistration), never scope
  creep in the same commit.

## Max-GPU rule (standing)

Sampler kernels run fused/batched under the adaptive VRAM budget; RNG state
stays resident; CPU workers handle lineage I/O off the critical path. Extra
randomness only counts if it raises relevant exploration or solution rate.

## Exit gate

The phase-specific CLI below is an acceptance interface to implement during
this phase, not a claim that the current checkout supports it. Common checks
already exist. Run the experiment only after its prerequisite is green.

```bash
git diff --check
python3 -m pytest tests -q
make verify
python3 benchmarks/qrand_ab.py --hypothesis <name> --seeds 5 --output experiments/p27-qrand-<name>.json
```

Artifact: checksummed per-hypothesis JSON with preregistration hash,
control comparisons, held-out confirmation and literature note. Done means a
published gain/loss/null per cycle — more randomness without measured
benefit fails the hypothesis, not the gate.

## Risks

Mysticism over measurement, hypothesis-hopping after seeing results,
control arms tuned worse than the novel arm, held-out peeking. Any of these
invalidates the cycle.

## Commit & Push (mandatory)

Start from a clean tree on `codex/p27-qrand-<name>`. Follow the common
commit procedure in [README.md](README.md#commit-and-push-contract), using
this phase's exact reviewed file list and artifact manifest. One completed
micro-task produces one atomic commit; never commit a failed gate.

```bash
git status --short
git diff --check
git diff --cached --check
git commit -m "feat(bench): complete p27 qrand-<name>"
git push -u origin HEAD
gh pr create --title "feat(bench): complete p27 qrand-<name>" --body-file /tmp/evobyte-p27-pr.md
git status --short
```
