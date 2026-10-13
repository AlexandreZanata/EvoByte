# P75 — Matriz de cobertura de classes de congruência modulares

**Status:** Proposed.
**Dependência:** P74 Proposed; branch a partir de `codex/p74-algebraic-identity-synthesis`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P74 aceita com motor de síntese de identidades operando.
**Branch:** `codex/p75-residue-class-coverage`.

## Hipótese, objetivo e escopo

Mapear exaustivamente a cobertura modular para módulos $M \in \{24, 120, 840, 2520\}$ sob Erdős–Straus, identificando exatamente quais classes possuem identidades polinomiais associadas e quais constituem resíduos resistentes (quadráticos não cobertos).

Alterações permitidas: `benchmarks/open_problems.py`, `src/evobyte/algebraic.py`, `tests/test_algebraic.py`.
Fora do escopo: extrapolação empírica não demonstrada, relaxamento de cobertura exata.

## Trabalho ordenado

1. Mapear todas as classes $\mathbb{Z}/M\mathbb{Z}$ para $M=840$ e associar identidades conhecidas e sintetizadas.
2. Isolar as classes irredutíveis (quadráticas módulo 840, ex.: $n \equiv 1, 121, 169, 289, 361, 529 \pmod{840}$).
3. Produzir matriz auditável de cobertura percentual exata com checksum imutável.

## Gate de saída

Checksum imutável da matriz de cobertura $M=840$, verificação de que todas as identidades cobrem 100% de suas respectivas classes sem exceções, e auditoria via `science_matrix.py`:

```bash
git diff --check
git status --short
python3 -m pytest tests/test_algebraic.py -q
python3 benchmarks/science_matrix.py --acceptance-phase P75
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p75 residue class coverage"
git push -u origin HEAD
gh pr create --base codex/p74-algebraic-identity-synthesis --title "feat(formal): implement p75 residue class coverage" --body-file /tmp/evobyte-p75-pr.md
```
