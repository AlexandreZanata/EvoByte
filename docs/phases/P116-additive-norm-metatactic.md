# P116 — Meta-tática customizada additive_norm e automação em Lean 4

**Status:** In review.
**Dependência:** P115 concluída; branch a partir de `codex/p115-additive-energy-balog-szemeredi`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P115 concluída com teoremas de energia aditiva provados em Lean 4.
**Branch:** `codex/p116-additive-norm-metatactic`.

## Hipótese, objetivo e escopo

Desenvolver e certificar uma meta-tática customizada em Lean 4 (`additive_norm`) no módulo `lean_proofs/Generated/AdditiveTacticTheorems.lean` capaz de simplificar automaticamente expressões de somas de Minkowski, cancelamentos de conjuntos, relações de inclusão $A \subseteq B \implies A + C \subseteq B + C$, comutatividade e associatividade de somas e cotas elementares de cardinalidade, reduzindo a complexidade de prova para lemas combinatórios.

Alterações permitidas: `lean_proofs/`, `src/evobyte/additive.py`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p116-config.json`, `experiments/p116-run.sh`.
Fora do escopo: uso de axiomas ad-hoc; táticas que admitem metas sem verificação completa do kernel.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-combinatória-aditiva-conjuntos-de-sidon-e-teoria-de-densidade-em-lean-4-p113p120).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar e meta-programar a tática `additive_norm` em Lean 4.
2. Provar teoremas de cobertura de tática e normalização em `lean_proofs/Generated/AdditiveTacticTheorems.lean`.
3. Adicionar interface de auditoria P116 em `benchmarks/science_matrix.py` (`run_p116_additive_norm_audit`) com validação de compilação sem `sorry`.

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry` e auditoria P116 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P116 --config experiments/p116-config.json --output /tmp/evobyte-p116-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p116 additive norm metatactic"
git push -u origin HEAD
gh pr create --base codex/p115-additive-energy-balog-szemeredi --title "feat(formal): implement p116 additive norm metatactic" --body-file /tmp/evobyte-p116-pr.md
```
