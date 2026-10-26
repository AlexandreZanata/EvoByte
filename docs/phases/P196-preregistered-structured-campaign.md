# P196 — Campanha pré-registrada estruturada nos alvos de gap estreito

**Status:** Proposed.
**Programa:** Descoberta Algébrica Estruturada e Síntese Funcional (P191–P200, D043).
**Dependência:** P195 concluída com sucesso (calibração aprovada).
**Owner:** agente executor; autor correspondente humano audita os logs da campanha.
**Branch:** `codex/p196-preregistered-structured-campaign`.
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [`docs/phases/P191-narrow-gap-frontier-targets.md`](P191-narrow-gap-frontier-targets.md),
[`docs/phases/P195-hard-historical-records-calibration.md`](P195-hard-historical-records-calibration.md).

## Por que esta fase existe

Esta é a fase central de ataque à fronteira científica: a execução da campanha de busca sobre os 5 alvos de fronteira de gap estreito selecionados em P191, utilizando o pipeline calibrado e validado em P195.

Para evitar viés de seleção e garantir reprodutibilidade hermética:
1. **Pré-registro Estrito:** O manifesto de execução (`experiments/p196-campaign-manifest.json`) congela as sementes (10 sementes independentes por alvo), o orçamento de parede (600 s por corrida), os parâmetros dos grupos de simetria e as funções objetivo antes do primeiro ciclo de cálculo.
2. **Monitoramento e Checkpointing:** Salvamento determinístico de checkpoints a cada 60 s para resiliência e auditoria de convergência.
3. **Classificação Falsificável:** Cada tentativa é classificada mecanicamente como:
   - `DISCOVERY_BEATEN`: se encontrar um objeto estritamente superior ao recorde mundial tabelado.
   - `DISCOVERY_TIED`: se igualar o recorde mundial existente com uma construção não isomórfica.
   - `NULL_RESULT`: se não atingir ou superar o recorde dentro do orçamento.

## Pergunta falsificável da fase

> O pipeline de busca estruturada consegue encontrar pelo menos uma construção que supere (`DISCOVERY_BEATEN`) ou iguale de forma não isomórfica (`DISCOVERY_TIED`) o limite publicado em um dos 5 alvos de gap estreito investigados?

## Escopo

**Arquivos a criar/editar:**
- `experiments/p196-campaign-manifest.json`: manifesto pré-registrado congelado.
- `benchmarks/run_structured_frontier_campaign.py`: harness de execução da campanha.
- `experiments/p196-campaign-results.json`: resultados completos com tempos, sementes e contagens de avaliações.
- `docs/research/p196-campaign-verdict.md`: relatório e veredito estatístico da campanha.
- `tests/test_structured_campaign.py`: testes de integridade, manifest e formato dos resultados.

## Critérios de Saída (Gates)

1. `tests/test_structured_campaign.py` passa 100% verde.
2. Execução completa dos 50 ensaios (5 alvos $\times$ 10 sementes) sem interrupções ou omissões de log.
3. Todos os objetos candidatos são verificados pelo verificador independente de dependência zero.
4. `git diff --check`, `git status --short`, `make lint` e `python3 -m pytest tests -q` passam sem erros.
