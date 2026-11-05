# ADR-0010: Keep-or-Drop Ruling on Micro Neural Bytecode Generator

**Status:** Accepted (Ruling: **DROP** from main search loop; retained in `evobyte.generator` as experimental module).
**Date:** 2026-09-29
**Phase:** P12 — Micro neural generator

## Context

Phase P12 investigated whether a lightweight causal neural model (100K–5M parameters) trained on elite archives could accelerate symbolic regression discovery relative to high-throughput bitwise/GPU genetic operators under equal wall-clock budgets and strict VRAM constraints.

Per `docs/phases/P12-neural-generator.md` and Decision D007:
> "generator stays only if it beats genetic per wall-clock second without hurting CVPS beyond its cap. Negative results are valid and recorded."

## Empirical Evidence

A 4-way benchmark (`experiments/p12_generator_ab.py`) was executed across 5 independent seeds (`[42, 101, 202, 303, 404]`) on Level-A Target 1 ($y = x^2 + 3x + 7$) under a strict equal wall-clock budget of 600.0s (10 minutes total, 30.0s per method per seed).

### 4-Way Comparison Summary

| Method | Success Rate | Mean Train MSE | Mean Hidden MSE | Mean Extrap MSE | Mean CVPS |
|---|---|---|---|---|---|
| **Random Search** | 0.0% (0/5) | 49.55071 | 49.16120 | 245.06421 | 1011.6 |
| **Genetic Evolution** | **40.0% (2/5)** | **5.31195** | **5.09780** | **817.64567** | **1006.0** |
| **Neural Standalone** | 0.0% (0/5) | 58.97506 | 57.05634 | 6704.95076 | 851.7 |
| **Neural + Genetic Hybrid** | 40.0% (2/5) | 13.47213 | 12.98033 | 1337.87829 | 762.4 |

### Observations

1. **Throughput Penalty (CVPS):**
   - Pure genetic evolution achieved **1006.0 CVPS**.
   - Neural standalone dropped to **851.7 CVPS** (-15.3%).
   - Neural + genetic hybrid dropped to **762.4 CVPS** (-24.2%).
   The overhead of autoregressive token-by-token sampling and gradient updates creates an unavoidable throughput tax compared to GPU-chunked vectorized genetic operators.

2. **Solution Quality:**
   - Pure genetic evolution achieved the lowest Mean Train MSE (**5.31**) and Mean Hidden MSE (**5.10**).
   - Neural alone struggled to discover exact closed forms within 30s (0/5 successes, Mean MSE 58.98).
   - Neural + genetic matched the 40% success rate of pure genetic, but with higher average error (13.47 MSE) and 24% fewer candidate evaluations.

## Decision

**DROP** the micro neural generator from the primary production search pipeline (`GENERATE -> VERIFY -> SELECT -> EVOLVE`).

The implementation is preserved in `src/evobyte/generator.py` and validated by unit tests (`tests/test_generator.py`) as an offline sampling and transfer-learning capability, but will not be placed in the hot path of subsequent benchmark phases (P13+).

## Consequences

- The production engine remains 100% compliant with Architecture Rule 2: pure deterministic NumPy/PyTorch genetic operators with maximal CVPS.
- Zero VRAM overhead during production symbolic regression runs.
- Negative empirical results are transparently documented with reproducible provenance.
