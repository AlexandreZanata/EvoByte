# P196 — Campanha pré-registrada estruturada nos alvos de gap estreito

**Status:** Done (2026-10-26).
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

**Resposta:** Sim. A campanha alcançou o veredito **`DISCOVERY_TIED`** em 10 de 10 sementes para o alvo de covering design $C(15, 8, 4) = 30$, igualando o limite mundial publicado (tabelas Gordon/LJCR) por meio de uma construção não isomórfica baseada em 2 órbitas cíclicas $\mathbb{Z}_{15}$, estritamente verificada pelo verificador de dependência zero (`verify_covering_design`).

## Escopo

**Arquivos criados/editados:**
- `experiments/p196-campaign-manifest.json`: manifesto pré-registrado congelado com 5 alvos e 10 sementes (50 ensaios).
- `benchmarks/run_structured_frontier_campaign.py`: harness de execução da campanha e checkpointing.
- `experiments/p196-campaign-results.json`: resultados completos com tempos, sementes e hashes SHA-256.
- `experiments/p196-campaign-checkpoint.json`: arquivo de recuperação e checkpointing incremental.
- `docs/research/p196-campaign-verdict.md`: relatório e veredito estatístico da campanha.
- `tests/test_structured_campaign.py`: testes de integridade, manifesto e formato dos resultados.

## Critérios de Saída (Gates)

1. `tests/test_structured_campaign.py` passa 100% verde (4/4 testes aprovados).
2. Execução completa dos 50 ensaios (5 alvos $\times$ 10 sementes) sem interrupções ou omissões de log.
3. Todos os objetos candidatos são verificados pelo verificador independente de dependência zero.
4. `git diff --check`, `git status --short`, `make lint` e `python3 -m pytest tests -q` passam sem erros.

## Commit & Push

```bash
git add experiments/p196-campaign-manifest.json \
        benchmarks/run_structured_frontier_campaign.py \
        experiments/p196-campaign-results.json \
        experiments/p196-campaign-checkpoint.json \
        docs/research/p196-campaign-verdict.md \
        tests/test_structured_campaign.py \
        docs/phases/P196-preregistered-structured-campaign.md
git commit -m "feat(frontier): execute preregistered structured campaign on narrow-gap targets (P196)"
git push -u origin codex/p196-preregistered-structured-campaign
gh pr create --base main --head codex/p196-preregistered-structured-campaign \
  --title "feat(frontier): execute preregistered structured campaign on narrow-gap targets (P196)" \
  --body "Execute preregistered campaign across 50 trials (5 targets x 10 seeds), achieving DISCOVERY_TIED on C(15,8,4)=30 for P196."
```
