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

## Binding revision for future runs (D012)

P15 supplies trustworthy measurement; P16–P20 validate the accelerated
pipeline; P13 then executes the full real comparison; P21 reproduces it.
The protocol in [phases/P13-full-benchmark.md](phases/P13-full-benchmark.md)
and the evidence rules in [ABLATIONS.md](ABLATIONS.md) govern the resumed
campaign. Previous summaries without raw executed records do not satisfy it.

Every requested budget is executed, not extrapolated. A predeclared nested
trajectory is allowed only with actual timestamped snapshots at each budget
and disclosure of shared trajectories; otherwise run independent cells.
Charge setup/training/fitting consistently and report cold and steady-state
cost separately. Run baseline solvers, including PySR, with pinned versions,
explicit thread/device limits and no access to target formula identifiers.
Pareto fronts are per dataset with a declared size metric; opcode count and
AST-node count are not automatically equivalent measures of complexity.

Each result has a durable raw artifact, config and all split hashes. Missing
baselines are `not_run`, never synthetic estimates. Numerical held-out success
and symbolic proof are separate outcomes. Larger scientific datasets require
P14's preregistration and P21's independently runnable predictor.
