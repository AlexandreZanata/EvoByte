# P133 — Problema do Final Feliz e polígonos convexos de Erdős-Szekeres

**Status:** Proposed.
**Dependência:** P132 concluída; branch a partir de `codex/p132-geom-distance-norm-metatactic`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P132 concluída com meta-tática geométrica e teoremas provados no Lean 4.
**Branch:** `codex/p133-convex-polygons-happy-ending`.

## Hipótese, objetivo e escopo

Formalizar no Lean 4 o célebre Problema do Final Feliz (Happy Ending Problem) de Klein–Erdős–Szekeres (`lean_proofs/Generated/ConvexPolygonsHappyEndingTheorems.lean`), provando a cota binomial clássica de Erdős–Szekeres $ES(k) \le \binom{2k-4}{k-2} + 1$, os valores exatos conhecidos $ES(3) = 3$, $ES(4) = 5$, $ES(5) = 9$, $ES(6) = 17$, a existência de quadriláteros convexos em qualquer conjunto de 5 pontos em posição geral e a não existência de 7-buracos convexos vazios em certas configurações.

Alterações permitidas: `lean_proofs/`, `src/evobyte/discrete_geometry.py`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p133-config.json`, `experiments/p133-run.sh`.
Fora do escopo: alegações infundadas sobre $ES(k)$ geral; supressão de restrições de posição geral.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-geometria-discreta-distâncias-distintas-de-erdős-e-configurações-de-pontos-em-lean-4-p129p136).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar formalização de orientação de triplas (determinante $2 \times 2$), convexidade de $k$-gonos e cotas de Erdős–Szekeres em `lean_proofs/Generated/ConvexPolygonsHappyEndingTheorems.lean`.
2. Adicionar algoritmos determinísticos para teste de posição geral, envoltória convexa de Graham e busca de subconjuntos convexos em `src/evobyte/discrete_geometry.py`.
3. Adicionar interface de auditoria P133 em `benchmarks/science_matrix.py` (`run_p133_convex_polygons_happy_ending_audit`) com compilação hermética sem `sorry`.

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry` e auditoria P133 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P133 --config experiments/p133-config.json --output /tmp/evobyte-p133-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p133 convex polygons happy ending"
git push -u origin HEAD
gh pr create --base codex/p132-geom-distance-norm-metatactic --title "feat(formal): implement p133 convex polygons happy ending" --body-file /tmp/evobyte-p133-pr.md
```
