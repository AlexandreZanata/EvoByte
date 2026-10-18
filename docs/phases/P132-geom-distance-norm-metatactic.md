# P132 — Meta-tática customizada geom_distance_norm e automação geométrica em Lean 4

**Status:** Proposed.
**Dependência:** P131 concluída; branch a partir de `codex/p131-unit-distances-szemeredi-trotter`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P131 concluída com teoremas de distâncias unitárias provados e compilados no Lean 4.
**Branch:** `codex/p132-geom-distance-norm-metatactic`.

## Hipótese, objetivo e escopo

Desenvolver e validar a meta-tática customizada `geom_distance_norm` em Lean 4 (`lean_proofs/Generated/DiscreteGeometryTacticTheorems.lean`), automatizando a expansão algébrica de distâncias euclidianas ao quadrado, cancelamento de coordenadas métricas, verificação da desigualdade triangular $\|p - r\| \le \|p - q\| + \|q - r\|$, convexidade de normas e simplificação de desigualdades de distâncias sem intervenção manual.

Alterações permitidas: `lean_proofs/`, `src/evobyte/discrete_geometry.py`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p132-config.json`, `experiments/p132-run.sh`.
Fora do escopo: uso de axiomas não padrão; enfraquecimento de metas dedutivas.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-geometria-discreta-distâncias-distintas-de-erdős-e-configurações-de-pontos-em-lean-4-p129p136).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar a meta-tática `geom_distance_norm` e lemas de automação geométrica em `lean_proofs/Generated/DiscreteGeometryTacticTheorems.lean`.
2. Validar que dezenas de teoremas métricos são provados exclusivamente com `geom_distance_norm` e `geom_distance_intro`.
3. Adicionar interface de auditoria P132 em `benchmarks/science_matrix.py` (`run_p132_geom_distance_norm_audit`) com compilação hermética sem `sorry`.

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry` e auditoria P132 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P132 --config experiments/p132-config.json --output /tmp/evobyte-p132-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p132 geom distance norm metatactic"
git push -u origin HEAD
gh pr create --base codex/p131-unit-distances-szemeredi-trotter --title "feat(formal): implement p132 geom distance norm metatactic" --body-file /tmp/evobyte-p132-pr.md
```
