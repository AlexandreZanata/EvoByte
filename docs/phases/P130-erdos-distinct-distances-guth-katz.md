# P130 — Cota inferior de Guth-Katz e configurações extremais de distâncias distintas

**Status:** Proposed.
**Dependência:** P129 concluída; branch a partir de `codex/p129-discrete-geometry-formal-database`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P129 concluída com tipos de geometria discreta provados e compilados no Lean 4.
**Branch:** `codex/p130-erdos-distinct-distances-guth-katz`.

## Hipótese, objetivo e escopo

Formalizar no Lean 4 os teoremas estruturais e construções extremais do problema de distâncias distintas de Erdős (`lean_proofs/Generated/ErdosDistinctDistancesTheorems.lean`), provando a cota assintótica da rede quadrada $\sqrt{n} \times \sqrt{n}$ ($|\Delta(\text{Grid}_k)| = O(n/\sqrt{\log n})$ via soma de dois quadrados de Landau–Ramanujan), a cota inferior quase-ótima de Guth–Katz ($|\Delta(P)| = \Omega(n / \log n)$) e invariantes métricos de configurações triangulares e circulares.

Alterações permitidas: `lean_proofs/`, `src/evobyte/discrete_geometry.py`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p130-config.json`, `experiments/p130-run.sh`.
Fora do escopo: alegações de resolução universal definitiva além dos limites de literatura estabelecidos; alteração de axiomas de Mathlib.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-geometria-discreta-distâncias-distintas-de-erdős-e-configurações-de-pontos-em-lean-4-p129p136).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar teoremas de contagem de distâncias em redes inteiras e limites de Guth–Katz em `lean_proofs/Generated/ErdosDistinctDistancesTheorems.lean`.
2. Adicionar construtores de redes bidimensionais $\text{Grid}(k)$, polígonos regulares e geradores de distâncias distintas exatas em `src/evobyte/discrete_geometry.py`.
3. Adicionar interface de auditoria P130 em `benchmarks/science_matrix.py` (`run_p130_erdos_distinct_distances_audit`) com compilação hermética sem `sorry`.

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry` e auditoria P130 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P130 --config experiments/p130-config.json --output /tmp/evobyte-p130-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p130 erdos distinct distances guth katz"
git push -u origin HEAD
gh pr create --base codex/p129-discrete-geometry-formal-database --title "feat(formal): implement p130 erdos distinct distances guth katz" --body-file /tmp/evobyte-p130-pr.md
```
