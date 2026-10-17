# P107 — Modelo neural condicional leve (<= 5M) para proposição estruturada sem alucinação

**Status:** Done.
**Dependência:** P106 concluída; branch a partir de `codex/p106-obstruction-graphs-data-engine`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P106 concluída com grafos de obstrução e banco formal hermético; dados de treino estritamente derivados de certificados formais.
**Branch:** `codex/p107-lightweight-conditional-proposer`.
**Resultado:** ACCEPTED — StructuredConditionalProposer (1.270.547 parâmetros <= 5M, 4,85 MB em memória), treinado com reprodutibilidade determinística bit-a-bit sobre certificados formais, zero alucinação (vocabulário fechado e permutações estritas de candidatos), acelerando a busca diofantina em 39,38x (redução de 97,5% em passos de candidatos) com 0 falsos negativos.

## Hipótese, objetivo e escopo

Treinar e congelar um modelo neural condicional compacto ($\le 5\text{M}$ parâmetros) residente em VRAM que prevê ordenações ótimas de divisores, caminhos de táticas e transformações algébricas sem emitir linguagem natural livre (sem alucinações), restrito à gramática sintática de bytecode e táticas Lean 4, com validação contra baselines clássicos sob mesmo orçamento computacional.

Alterações permitidas: `src/evobyte/models.py`, `src/evobyte/training.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p107-config.json`, `experiments/p107-run.sh`.
Fora do escopo: modelos LLM acima de 5M parâmetros; chamadas a APIs externas; alucinação de teoremas sem checagem de kernel.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-descoberta-formal-em-problemas-abertos-e-teoria-de-modelos-guiada-por-provas-em-lean-4-p105p112).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar arquitetura de modelo condicional estruturado ($\le 5\text{M}$ parâmetros) em `src/evobyte/models.py`.
2. Adicionar pipeline de treino supervisionado sobre certificados diofantinos formais em `src/evobyte/training.py`.
3. Adicionar interface de auditoria P107 em `benchmarks/science_matrix.py` (`run_p107_conditional_proposer_audit`) comparando rendimento frente a baselines clássicos.

## Gate de saída

Execução limpa de treinamento, exportação de pesos congelados e auditoria comparativa P107:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P107 --config experiments/p107-config.json --output /tmp/evobyte-p107-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p107 lightweight conditional proposer"
git push -u origin HEAD
gh pr create --base codex/p106-obstruction-graphs-data-engine --title "feat(formal): implement p107 lightweight conditional proposer" --body-file /tmp/evobyte-p107-pr.md
```
