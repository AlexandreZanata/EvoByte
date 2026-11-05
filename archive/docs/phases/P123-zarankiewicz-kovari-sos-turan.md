# P123 — Problema de Zarankiewicz e desigualdade de Kővári-Sós-Turán para grafos K_{s,t}-free

**Status:** In review.
**Dependência:** P122 concluída; branch a partir de `codex/p122-paley-graphs-ramsey-constructions`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P122 concluída com grafos de Paley e construções de Ramsey provadas em Lean 4.
**Branch:** `codex/p123-zarankiewicz-kovari-sos-turan`.

## Hipótese, objetivo e escopo

Formalizar o problema de Zarankiewicz $z(m, n; s, t)$ e a desigualdade de Kővári–Sós–Turán (KST) para grafos livres de subgrafos bipartidos completos $K_{s,t}$ (em particular grafos livres de $C_4 = K_{2,2}$, onde $\sum_{u \in U} \binom{d(u)}{2} \le \binom{n}{2}$), combinada com construções de matrizes de incidência de planos projetivos finitos $\text{PG}(2, q)$ que atingem a cota extremal $(q+1)(q^2+q+1)$ arestas sem $C_4$, gerando `lean_proofs/Generated/ZarankiewiczKovariSosTuranTheorems.lean`.

Alterações permitidas: `lean_proofs/`, `src/evobyte/graph_ramsey.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p123-config.json`, `experiments/p123-run.sh`.
Fora do escopo: uso de axiomas não padrão ou `sorry`.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-teoria-extremal-de-grafos-números-de-ramsey-e-progressões-aritméticas-em-lean-4-p121p128).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar verificação de ausência de $K_{s,t}$ ($C_4$-free), contagem de cerejas $\sum \binom{d(v)}{2}$, limitante de Kővári–Sós–Turán e grafo de incidência projetiva de Reiman em `src/evobyte/graph_ramsey.py`.
2. Exportar mais de 60 teoremas formais em `lean_proofs/Generated/ZarankiewiczKovariSosTuranTheorems.lean` com zero `sorry`.
3. Adicionar interface de auditoria P123 em `benchmarks/science_matrix.py` (`run_p123_zarankiewicz_kst_audit`).

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry` e auditoria P123 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P123 --config experiments/p123-config.json --output /tmp/evobyte-p123-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p123 zarankiewicz kovari sos turan"
git push -u origin HEAD
gh pr create --base codex/p122-paley-graphs-ramsey-constructions --title "feat(formal): implement p123 zarankiewicz kovari sos turan" --body-file /tmp/evobyte-p123-pr.md
```
