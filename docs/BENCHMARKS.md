# Benchmarks

**Status:** decision.

## Synthetic ladder (gated, in order)

Level A (MVP must clear): `y = x + 1`, `y = x^2`, `y = x^2 + 3x + 7`,
`y = sin(x)`, `y = sin(x) + x^2`, `y = x*y + z`.

Level B (post-MVP): rational, piecewise-smooth, multi-var, noisy variants,
extrapolation splits.

`benchmarks/synthetic.py` generates datasets from known formulas with a
logged seed + hash. EvoByte never receives the formula.

Per target record: time-to-discovery, candidates evaluated, CVPS,
generalization (hidden + extrapolation), found size, repeat-success rate
(>= 5 seeds).

## Recognized suites (P13)

Adopt current community symbolic-regression suites (e.g. SRBench-style) only
after Level A is green. Pin suite version + commit; never train on suite
solutions.

## Main experiment (P13)

Question: *under equal wall-clock budget, does massively parallel stochastic
search with autoevolution match/beat sophisticated methods?*

Baselines (equal budget): random search, genetic programming,
traditional symbolic regression, CMA-ES where applicable, PySR, other
relevant methods pinned by version.

Budgets: 10 s, 1 min, 10 min, 1 h. Metric: best hidden + extrapolation error
vs. time, plus program size. Report Pareto (error vs. size), not just error.

## Protocol (binding)

- Train/val/hidden/extrapolation splits fixed per dataset hash.
- Evolution never sees hidden; L2 sees it once per promotion.
- 5+ seeds per claim; report median + range, not best cherry-pick.
- All runs log: seed, commit, config, GPU, driver, dataset hash, opcode
  version, population params.
