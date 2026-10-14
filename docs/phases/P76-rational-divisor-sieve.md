# P76 — Crivo de fatoração racional e decomposição de divisores

**Status:** Done.
**Dependência:** P75 Proposed; branch a partir de `codex/p75-residue-class-coverage`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P75 aceita com matriz de resíduos mapeada.
**Branch:** `codex/p76-rational-divisor-sieve`.

## Hipótese, objetivo e escopo

A equação diofantina de Erdős–Straus pode ser formulada como $(4xy - n(x+y)) \mid n^2$. Um crivo determinístico sobre divisores de $n^2$ e formas quadráticas binárias permite podar o espaço de busca de denominadores para resíduos resistentes com complexidade sublinear em relação ao teto de coordenadas.

Alterações permitidas: `benchmarks/open_problems.py`, `src/evobyte/algebraic.py`, `tests/test_algebraic.py`.
Fora do escopo: busca cega em $\mathbb{Z}^3$, heurísticas sem prova exata de limites.

## Trabalho ordenado

1. Implementar decomposição de divisores racionais $d \mid n^2$ e relacionar a $(4x - n)(4y - n) = n^2 + 4nz$.
2. Implementar crivo rápido com eliminação de divisores incompatíveis módulo pequenos primos.
3. Comparar tempo e chamadas ao checker contra a busca aritmética padrão em instâncias desafiadoras ($n \equiv 1 \pmod{24}$).

## Gate de saída

Aceleração mensurada sem nenhuma perda de solução no benchmark de validação, ausência de falsos negativos e verificação exata:

```bash
git diff --check
git status --short
python3 -m pytest tests/test_algebraic.py -q
python3 benchmarks/science_matrix.py --acceptance-phase P76
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p76 rational divisor sieve"
git push -u origin HEAD
gh pr create --base codex/p75-residue-class-coverage --title "feat(formal): implement p76 rational divisor sieve" --body-file /tmp/evobyte-p76-pr.md
```
