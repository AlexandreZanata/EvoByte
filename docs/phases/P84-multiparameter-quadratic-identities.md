# P84 — Síntese de identidades quadráticas multiparâmetro

**Status:** Proposed.
**Dependência:** P83 Proposed; branch a partir de `codex/p83-optimal-divisor-selection`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P83 concluída com crivo ótimo de divisores.
**Branch:** `codex/p84-multiparameter-quadratic-identities`.

## Hipótese, objetivo e escopo

Sintetizar identidades algébricas diofantinas parametrizadas por formas quadráticas e de 2 parâmetros $n = a u^2 + b u v + c v^2$ para abordar os resíduos resistentes mod 840 de Erdős–Straus e mod 120 de Sierpiński, com validação formal no kernel Lean 4.

Alterações permitidas: `src/evobyte/algebraic.py`, `src/evobyte/formal_bridge.py`, `lean_proofs/Generated/`, `benchmarks/science_matrix.py`, `experiments/`.
Fora do escopo: soluções não polinomiais; alegação de cobertura universal total sem prova formal completa.

## Trabalho ordenado

1. Implementar sintetizador de identidades algébricas multivariadas em $\mathbb{Q}[u, v]$.
2. Descobrir e certificar identidades para resíduos quadráticos resistentes selecionados (ex.: $n \equiv 121 \pmod{840}$).
3. Exportar teoremas para Lean 4 (`QuadraticIdentities.lean`) e compilar via Lake com zero `sorry`.

## Gate de saída

Identidades quadráticas sintetizadas e compiladas no Lean 4 com aceitação integral:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P84 --config experiments/p84-config.json --output /tmp/evobyte-p84-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p84 multiparameter quadratic identities"
git push -u origin HEAD
gh pr create --base codex/p83-optimal-divisor-selection --title "feat(formal): implement p84 multiparameter quadratic identities" --body-file /tmp/evobyte-p84-pr.md
```
