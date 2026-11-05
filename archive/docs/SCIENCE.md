# Scientific Datasets & Pre-Registration Registry

**Status:** decision (P14 scope).

EvoByte evaluates real scientific formulas only through pre-registered datasets
with domain constraints, units verification, extrapolation bounds, and
adversarial testing.

## Pre-Registered Registry

| Dataset Key | Physical Law | Domain Field | License | Input Units | Output Units | Target $R^2$ | Max Extrap Error |
|---|---|---|---|---|---|---|---|
| `kepler_third_law` | $T = a^{3/2} = a \sqrt{a}$ | Celestial Mechanics | NASA (Public Domain) | AU | Earth Years | 0.999 | 5.0% |
| `boyle_gas_law` | $P = k / V$ | Thermodynamics | NIST (Public Domain) | Liters (L) | Atm (atm) | 0.990 | 8.0% |
| `stefan_boltzmann` | $j^* = \sigma T^4$ | Thermal Physics | NIST (CC0) | kK | $\text{kW/m}^2$ | 0.990 | 8.0% |
| `michaelis_menten` | $v = \frac{V_{max} [S]}{K_m + [S]}$ | Biochemistry | BioModels (CC0) | $\mu\text{M}$ | $\mu\text{M/s}$ | 0.980 | 8.0% |
| `lorentz_factor` | $\gamma = \frac{1}{\sqrt{1 - \beta^2}}$ | Special Relativity | CERN (CC-BY 4.0) | $v/c$ (dim-less) | dimensionless | 0.980 | 15.0% |

## Domain Level-2 Verifier Protocol

Every promoted scientific candidate must clear Level-2 domain gates:

1. **Float64 Numerical Precision:** Re-evaluated in `float64` to detect precision degradation.
2. **Dimensional / Units Scaling Invariance:** Checked via $f(\lambda x)/f(x) \approx \lambda^\alpha$. For Kepler, $\alpha \approx 1.5$; for Stefan-Boltzmann, $\alpha \approx 4.0$.
3. **Monotonicity & Asymptotes:** Bounded derivatives ($dY/dX \ge 0$ or $\le 0$) and finite asymptote bounds (e.g. $V_{max}$ in enzymology).
4. **Adversarial Domain Audit:** Evaluated at domain boundaries and singularities ($x \to 0$, $x \to \infty$, $\beta \to 1$).
5. **Anti-Degeneracy Guards:** Rejection of constant-only models ($\text{std} < 10^{-6}$), absurd constants ($|c| > 10^6$), and single-point memorization.

## Integrity Principle: Negative Results reporting

Per P14 specification:
- A candidate that passes all domain L2 gates is classified as **SUPPORTED**.
- A candidate that fails pre-registered thresholds or domain constraints is classified as **NEEDS_WORK** or **NULL**.
- A null result that upholds scientific integrity is fully valid and published.
