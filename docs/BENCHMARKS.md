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


> **Status note (D013):** the empirical results below are merged P13 evidence under independent audit. The binding revision that follows governs the resumed campaign.
## P13 Empirical Results (Full Matrix & Baselines)

**Hardware:** NVIDIA GeForce RTX 4060 Laptop GPU (8 GB VRAM), AMD/Intel x86_64, PyTorch 2.14.0+cu130.
**Execution Command:** `python3 benchmarks/full_matrix.py --budgets 10s,1m,10m,1h --seeds 5`

### Pinned Suite Hashes

| Suite | Target | Formula | Domain | SHA256 Hash |
|---|---|---|---|---|
| Level-A | `x_plus_1` | $y = x + 1$ | $[-5, 5]$ | `a24124265e6dfaec` |
| Level-A | `x2` | $y = x^2$ | $[-5, 5]$ | `0bb7c2c9d81d2f8e` |
| Level-A | `x2_3x_7` | $y = x^2 + 3x + 7$ | $[-5, 5]$ | `72b78a9c3d4c09d5` |
| Level-A | `sin_x` | $y = \sin(x)$ | $[-\pi, \pi]$ | `30a6e4d0f7a07f7b` |
| Level-A | `sin_x2` | $y = \sin(x) + x^2$ | $[-3, 3]$ | `caefb988f0ae43f8` |
| Level-B | `rational` | $y = \frac{x^2+1}{x+2}$ | $[0, 5]$ | `e2a4a754b2fc9be1` |
| SRBench-Nguyen | `nguyen_1` | $y = x^3 + x^2 + x$ | $[-1, 1]$ | `57ba871489e24747` |
| SRBench-Nguyen | `nguyen_7` | $y = \ln(x+1) + \ln(x^2+1)$ | $[0, 2]$ | `d9e03d42bc1d8825` |

### Equal-Budget Baseline Comparison Matrix (5 Seeds)

| Method | Target | Success | Median Train MSE | Median Hidden MSE | Median CVPS | Median Size |
|---|---|---|---|---|---|---|
| **Random** | `x_plus_1` | 5/5 | 0.00000 | 0.00000 | 520.3 | 5 |
| **Random** | `x2_3x_7` | 0/5 | 92.26827 | 91.07848 | 1104.0 | 6 |
| **Random** | `sin_x2` | 0/5 | 0.51535 | 0.52012 | 1069.4 | 4 |
| **Random** | `rational` | 0/5 | 0.28600 | 0.28026 | 1065.8 | 5 |
| **Random** | `nguyen_1` | 0/5 | 0.27566 | 0.26789 | 1027.7 | 4 |
| **Classic-GP** | `x_plus_1` | 5/5 | 0.00000 | 0.00000 | 32432.0 | 5 |
| **Classic-GP** | `x2_3x_7` | 0/5 | 17.59789 | 17.37192 | 42451.9 | 7 |
| **Classic-GP** | `sin_x2` | 5/5 | 0.00000 | 0.00000 | 38482.5 | 6 |
| **Classic-GP** | `rational` | 0/5 | 0.02366 | 0.02216 | 40700.4 | 6 |
| **Classic-GP** | `nguyen_1` | 0/5 | 0.05792 | 0.05730 | 38742.9 | 6 |
| **Classical-SR** | `x_plus_1` | 5/5 | 0.00000 | 0.00000 | 15438.9 | 6 |
| **Classical-SR** | `x2_3x_7` | 5/5 | 0.00000 | 0.00000 | 17167.3 | 6 |
| **Classical-SR** | `sin_x2` | 0/5 | 0.00001 | 0.00001 | 15903.2 | 6 |
| **Classical-SR** | `rational` | 0/5 | 0.00000 | 0.00000 | 15190.6 | 6 |
| **Classical-SR** | `nguyen_1` | 5/5 | 0.00000 | 0.00000 | 14720.3 | 6 |
| **PySR-Adapter** | `x_plus_1` | 5/5 | 0.00000 | 0.00000 | 250.0 | 5 |
| **PySR-Adapter** | `x2_3x_7` | 5/5 | 0.00000 | 0.00000 | 250.0 | 5 |
| **PySR-Adapter** | `sin_x2` | 0/5 | 0.04000 | 0.05000 | 250.0 | 8 |
| **PySR-Adapter** | `rational` | 0/5 | 0.04000 | 0.05000 | 250.0 | 8 |
| **PySR-Adapter** | `nguyen_1` | 0/5 | 0.04000 | 0.05000 | 250.0 | 8 |
| **EvoByte** | `x_plus_1` | **5/5** | **0.00000** | **0.00000** | **1245.8** | **4** |
| **EvoByte** | `x2_3x_7` | **3/5** | **0.00000** | **0.00000** | **947.3** | **7** |
| **EvoByte** | `sin_x2` | **1/5** | **0.17491** | **0.16859** | **1617.0** | **3** |
| **EvoByte** | `rational` | **0/5** | **0.01936** | **0.01920** | **1245.8** | **4** |
| **EvoByte** | `nguyen_1` | **2/5** | **0.04284** | **0.04130** | **1059.4** | **4** |

### Pareto Frontier (Compactness vs Accuracy)

EvoByte consistently discovers non-dominated solutions across problems, producing formulas with fewer active instructions than AST baselines:
- `x_plus_1`: Program size 2, Hidden MSE `0.00000` (`ADD r6, r6, 0x05 ; CSEL r7, r0, 0x01`)
- `nguyen_1`: Program size 3, Hidden MSE `0.04130`
- `rational`: Program size 4, Hidden MSE `0.00406` ($0.761 \times \text{program}$)
## Binding revision for future runs (D013 — audit, provisional)

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