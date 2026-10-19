# P155 — Medição exata dos baselines competitivos pareados sob mesmo orçamento

**Status:** Proposed.
**Dependência:** P154 concluída; branch a partir de `codex/p154-wall-clock-benchmark-matrix-execution`.
**Owner:** agente executor; revisor formal/sistemas nos gates indicados.
**Pré-requisito:** P154 concluída com matriz bruta do EvoByte gerada.
**Branch:** `codex/p155-honest-baselines-gp-pysr-execution`.

## Hipótese, objetivo e escopo

Executar os baselines de controle honestos sob rigorosamente o mesmo orçamento de tempo de parede (10 s, 1 min, 10 min, 1 h) e as mesmas sementes aleatórias: (1) Random Search em bytecode; (2) Classical Genetic Programming (DEAP ou gplearn); e (3) Regressão Simbólica padrão (PySR ou SymbolicRegressor). Registrar o tempo de execução real, a taxa de sucesso de redescoberta, a complexidade da fórmula resultante e o Pareto (MSE vs. tamanho da expressão). Provar se EvoByte supera baselines em time-to-solution sob hardware equivalente.

Alterações permitidas: `benchmarks/baselines/`, `experiments/p155-baselines/`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p155-config.json`, `experiments/p155-run.sh`.
Fora do escopo: uso de parâmetros penalizantes artificiais contra os baselines; alteração de versões de pacotes.

Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Configurar adaptadores padronizados para Random Search, GP clássico e PySR com terminação estrita por `timeout` de parede.
2. Executar baselines sobre os mesmos alvos de P154 com 20 sementes pareadas em `experiments/p155-baselines/`.
3. Extrair dados comparativos diretos de MSE final, complexidade e candidatos/segundo avaliados.
4. Adicionar interface de auditoria P155 em `benchmarks/science_matrix.py` (`run_p155_baselines_audit`).

## Gate de saída

Execução integral dos baselines pareados com dados registrados e auditoria P155 aceita:

```bash
git diff --check
git status --short
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P155 --config experiments/p155-config.json --output /tmp/evobyte-p155-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(benchmark): implement p155 honest baselines gp pysr execution"
git push -u origin HEAD
gh pr create --base codex/p154-wall-clock-benchmark-matrix-execution --title "feat(benchmark): implement p155 honest baselines gp pysr execution" --body-file /tmp/evobyte-p155-pr.md
```
