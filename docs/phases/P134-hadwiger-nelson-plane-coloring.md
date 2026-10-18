# P134 — Colorações de distâncias unitárias no plano e problema de Hadwiger-Nelson

**Status:** Proposed.
**Dependência:** P133 concluída; branch a partir de `codex/p133-convex-polygons-happy-ending`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P133 concluída com teoremas de polígonos convexos provados e compilados no Lean 4.
**Branch:** `codex/p134-hadwiger-nelson-plane-coloring`.

## Hipótese, objetivo e escopo

Formalizar no Lean 4 o problema de Hadwiger–Nelson sobre o número cromático do plano $\mathbb{R}^2$ sob distâncias unitárias proibidas (`lean_proofs/Generated/HadwigerNelsonColoringTheorems.lean`), provando a cota inferior clássica via o fuso de Moser ($\chi(\mathbb{R}^2) \ge 4$), a cota inferior de Aubrey de Grey ($\chi(\mathbb{R}^2) \ge 5$), a cota superior hexagonal de Isbell $\chi(\mathbb{R}^2) \le 7$ e a independência de subgrafos de distâncias unitárias finitos.

Alterações permitidas: `lean_proofs/`, `src/evobyte/discrete_geometry.py`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p134-config.json`, `experiments/p134-run.sh`.
Fora do escopo: resolução de $\chi(\mathbb{R}^2) \in \{5, 6, 7\}$; axiomas não padrão.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-geometria-discreta-distâncias-distintas-de-erdős-e-configurações-de-pontos-em-lean-4-p129p136).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar formalização de grafos de distâncias unitárias, fuso de Moser e pavimentações hexagonais em `lean_proofs/Generated/HadwigerNelsonColoringTheorems.lean`.
2. Adicionar geradores do grafo de Moser (7 vértices, 11 arestas) e teste exato de validade de 4-colorações em `src/evobyte/discrete_geometry.py`.
3. Adicionar interface de auditoria P134 em `benchmarks/science_matrix.py` (`run_p134_hadwiger_nelson_coloring_audit`) com compilação hermética sem `sorry`.

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry` e auditoria P134 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P134 --config experiments/p134-config.json --output /tmp/evobyte-p134-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p134 hadwiger nelson plane coloring"
git push -u origin HEAD
gh pr create --base codex/p133-convex-polygons-happy-ending --title "feat(formal): implement p134 hadwiger nelson plane coloring" --body-file /tmp/evobyte-p134-pr.md
```
