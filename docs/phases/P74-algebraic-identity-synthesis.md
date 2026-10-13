# P74 — Síntese de identidades polinomiais algébricas

**Status:** Done (entregas 1–2: motor de síntese Poly1D/AlgebraicIdentity implementado, redescobertas clássicas de Mordell 4k+3, 3k+2, 8k+5 verificadas com 100% de exatidão algébrica, medição ACCEPTED em árvore limpa run_id=4826b530947eac1c; registro em docs/research/p74-identity-record.md).
**Dependência:** P73 Done (PR #102 aberto); branch a partir de `codex/p73-lean-formal-baseline`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P73 com harness Lean 4 hermético aceito.
**Branch:** `codex/p74-algebraic-identity-synthesis`.

## Hipótese, objetivo e escopo

A síntese simbólica de identidades racionais $4/n = 1/X(k) + 1/Y(k) + 1/Z(k)$ sobre progressões lineares $n = mk + r$ permite demonstrar infinitas soluções para uma classe de congruência inteira, superando a barreira da busca numérica ponto a ponto.

Alterações permitidas: `benchmarks/open_problems.py`, `src/evobyte/algebraic.py`, `tests/test_algebraic.py`.
Fora do escopo: busca numérica exaustiva sem forma fechada, relaxamento de integridade nos denominadores $X, Y, Z$.

## Trabalho ordenado

1. Implementar representação algébrica de frações racionais e polinômios em $\mathbb{Q}[k]$.
2. Implementar motor de busca simbólica para formas de Mordell: $X(k) = (n+c)/4$, derivando $Y(k)$ e $Z(k)$ a partir da decomposição de $4X - n$.
3. Verificar a validade exata da identidade sobre $\mathbb{Q}$ e a positividade/integralidade dos denominadores para todo $k \ge 0$.

## Gate de saída

Redescoberta das identidades clássicas de Mordell para resíduos simples ($n \equiv 3 \pmod 4$, $n \equiv 2 \pmod 3$) e testes herméticos de corretude algébrica:

```bash
git diff --check
git status --short
python3 -m pytest tests/test_algebraic.py -q
python3 benchmarks/science_matrix.py --acceptance-phase P74
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p74 algebraic identity synthesis"
git push -u origin HEAD
gh pr create --base codex/p73-lean-formal-baseline --title "feat(formal): implement p74 algebraic identity synthesis" --body-file /tmp/evobyte-p74-pr.md
```
