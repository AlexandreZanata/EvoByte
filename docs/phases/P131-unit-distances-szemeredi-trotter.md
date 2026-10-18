# P131 — Problema das distâncias unitárias e teorema de incidência de Szemerédi-Trotter

**Status:** Proposed.
**Dependência:** P130 concluída; branch a partir de `codex/p130-erdos-distinct-distances-guth-katz`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P130 concluída com teoremas de distâncias distintas provados e compilados no Lean 4.
**Branch:** `codex/p131-unit-distances-szemeredi-trotter`.

## Hipótese, objetivo e escopo

Formalizar no Lean 4 o problema das distâncias unitárias de Erdős e a teoria de incidências ponto-reta de Szemerédi–Trotter (`lean_proofs/Generated/UnitDistancesSzemerediTrotterTheorems.lean`), provando a cota de incidências $I(P, L) \le C (m^{2/3}n^{2/3} + m + n)$, a cota superior clássica de Spencer–Szemerédi–Trotter para distâncias unitárias $u(n) = O(n^{4/3})$, a cota inferior superlinear de Erdős $u(n) \ge n^{1 + c/\log \log n}$ e propriedades de grafos de incidência.

Alterações permitidas: `lean_proofs/`, `src/evobyte/discrete_geometry.py`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p131-config.json`, `experiments/p131-run.sh`.
Fora do escopo: alteração de axiomas de Mathlib; flexibilização de rigor dedutivo no kernel Lean 4.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-geometria-discreta-distâncias-distintas-de-erdős-e-configurações-de-pontos-em-lean-4-p129p136).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar formalização de incidências ponto-reta e cotas de distâncias unitárias em `lean_proofs/Generated/UnitDistancesSzemerediTrotterTheorems.lean`.
2. Adicionar algoritmos para contagem exata de distâncias unitárias $u(P) = |\{ \{p, q\} : \|p - q\| = 1 \}|$ e verificação de incidências ponto-reta em `src/evobyte/discrete_geometry.py`.
3. Adicionar interface de auditoria P131 em `benchmarks/science_matrix.py` (`run_p131_unit_distances_szemeredi_trotter_audit`) com compilação hermética sem `sorry`.

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry` e auditoria P131 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P131 --config experiments/p131-config.json --output /tmp/evobyte-p131-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p131 unit distances szemeredi trotter"
git push -u origin HEAD
gh pr create --base codex/p130-erdos-distinct-distances-guth-katz --title "feat(formal): implement p131 unit distances szemeredi trotter" --body-file /tmp/evobyte-p131-pr.md
```
