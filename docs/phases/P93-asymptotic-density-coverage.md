# P93 — Teoremas de densidade assintótica e cobertura modular completa

**Status:** Proposed.
**Dependência:** P92 Proposed; branch a partir de `codex/p92-extremal-coordinate-bounds`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P92 concluída com cotas extremais verificadas.
**Branch:** `codex/p93-asymptotic-density-coverage`.

## Hipótese, objetivo e escopo

Formalizar no Lean 4 e comprovar empiricamente que a densidade assintótica natural $\delta(S) = \lim_{N \to \infty} \frac{|S \cap [1, N]|}{N}$ dos inteiros resolvidos por identidades polinomiais converge para $1$ à medida que módulos compostos $M$ crescem.

Alterações permitidas: `lean_proofs/`, `src/evobyte/algebraic.py`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p93-config.json`, `experiments/p93-run.sh`.
Fora do escopo: alegação de que densidade $1$ implica que nenhum contraexemplo existe em $\mathbb{N}$.

## Trabalho ordenado

1. Implementar cálculo exato e limites analíticos de densidade assintótica modular em `src/evobyte/algebraic.py`.
2. Provar lemas de densidade no Lean 4 demonstrando $\delta(S) \ge 1 - \epsilon$.
3. Adicionar auditoria P93 em `benchmarks/science_matrix.py` (`run_p93_asymptotic_density_audit`).

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry` e auditoria P93 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P93 --config experiments/p93-config.json --output /tmp/evobyte-p93-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p93 asymptotic density coverage"
git push -u origin HEAD
gh pr create --base codex/p92-extremal-coordinate-bounds --title "feat(formal): implement p93 asymptotic density coverage" --body-file /tmp/evobyte-p93-pr.md
```
