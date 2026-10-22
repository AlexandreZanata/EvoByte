# P166 — Campanha pré-registrada de busca por novos recordes mundiais sob orçamento fixo

**Status:** Prepared (manifesto pré-registrado e congelado antes da execução).
**Dependência:** P165 concluída; branch a partir de `codex/p165-blind-rediscovery-protocol`.
**Owner:** agente executor; revisor formal nos gates de veredito.
**Branch:** `codex/p166-preregistered-record-campaign`.
**Leia antes:** [regras do executor P161–P170](README.md#programa-de-descoberta-validada-p161p170-d038).

## Por que esta fase existe

A verdadeira ciência exige pré-registro: definir as regras e o orçamento **antes** de rodar o
experimento, aceitando o resultado qualquer que seja ele.
1. Se a busca encontrar um certificado que supere a cota publicada da literatura (ex: $W(2,6) \ge 1132$,
   $S(5) \ge 161$ ou um grafo conexo que refuta uma conjectura espectral em aberto), temos uma
   **descoberta matemática genuína e inédita**.
2. Se a busca consumir o orçamento total sem encontrar um novo recorde, o resultado é classificado
   formalmente como **`NULL_RESULT` (resultado nulo)**. Resultados nulos pré-registrados possuem
   alto valor científico porque delimitam empiricamente os limites da heurística e evitam publicação
   seletiva de falsos positivos.

Esta fase executa a campanha com orçamento fixo, alvos congelados e cadeia de custódia SHA-256.

## Escopo

**Arquivos que você pode criar:**
- `benchmarks/run_preregistered_campaign.py`
- `experiments/p166-campaign-manifest.json`
- `experiments/p166-campaign/summary.json`
- `docs/research/p166-campaign-verdict.md`

**Arquivos que você pode editar:**
- `docs/phases/P166-preregistered-record-campaign.md`: linha de Status.

**Proibido:** alterar a meta ou o critério de vitória no meio da campanha. Proibido chamar um
resultado nulo de vitória. Se não bateu o recorde, o veredito é estritamente `NULL_RESULT`.

## Trabalho ordenado

### Passo 1 — Branch e manifesto pré-registrado

```bash
git status --short
git switch codex/p165-blind-rediscovery-protocol
git switch -c codex/p166-preregistered-record-campaign
```

Crie o arquivo `experiments/p166-campaign-manifest.json` congelando:
- Lista de alvos: IDs de `open_targets.json`.
- Orçamento por ensaio: ex: 60.0 segundos de relógio por semente (ajustável para orçamento de produção).
- Lista de sementes fixas: `[42, 101, 202, 303, 404, 505, 606, 707, 808, 909]`.
- Algoritmos participantes: `["SimulatedAnnealing", "TabuSearch"]`.

### Passo 2 — Criar `benchmarks/run_preregistered_campaign.py`

Implemente o executor que:
1. Carrega o manifesto pré-registrado e confere integridade.
2. Executa cada par `(alvo, algoritmo, semente)` sob monitoramento de timeout estrito.
3. Submete qualquer candidato de pontuação recorde ao verificador independente de `target_catalogue.py`.
4. Classifica o resultado final de cada alvo em:
   - `DISCOVERY_BEATEN`: superou estritamente o valor publicado da literatura.
   - `DISCOVERY_TIED`: empatou com o melhor recorde mundial conhecido.
   - `NULL_RESULT`: orçamento esgotado sem alcançar nem superar o recorde.
5. Gera `experiments/p166-campaign/summary.json` contendo todos os dados brutos e hashes.

### Passo 3 — Executar a campanha pré-registrada

```bash
python3 benchmarks/run_preregistered_campaign.py \
  --manifest experiments/p166-campaign-manifest.json \
  --output-dir experiments/p166-campaign
```

Confira que `experiments/p166-campaign/summary.json` foi gerado e está com formato íntegro.

### Passo 4 — Relatório `docs/research/p166-campaign-verdict.md`

Estrutura obrigatória:
1. Resumo Executivo: Número de alvos, total de avaliações, tempo total de máquina.
2. Tabela de Vereditos por Alvo:
   `Alvo | Recorde Literatura | Melhor Encontrado | Status | Verificador Independente`
3. Seção "Registro de Descobertas ou Resultados Nulos":
   - Se houver `DISCOVERY_BEATEN`: anexar o certificado completo e o hash SHA-256.
   - Se todos forem `NULL_RESULT`: declarar com integridade: *"A busca estocástica sob o orçamento
     pré-registrado não superou os recordes mundiais da literatura. O resultado nulo é publicado de
     acordo com a regra de integridade científica de AGENTS.md."*

## Regras de parada (PARE, não commite, reporte)

- Qualquer candidato rotulado como `DISCOVERY_BEATEN` falhar no verificador independente de `target_catalogue.py`.
- O script abortar no meio sem gravar os dados brutos.

## Gate de saída

```bash
git diff --check
python3 -m pytest tests/test_target_catalogue.py tests/test_combinatorial_baselines.py -q
test -f experiments/p166-campaign/summary.json
make verify
git status --short
```

## Commit & Push (obrigatório)

```bash
git add benchmarks/run_preregistered_campaign.py experiments/p166-campaign-manifest.json \
  experiments/p166-campaign/summary.json docs/research/p166-campaign-verdict.md \
  docs/phases/P166-preregistered-record-campaign.md
git diff --cached --check
git commit -m "feat(research): execute p166 preregistered record campaign and emit honest verdict"
git push -u origin HEAD
gh pr create --base codex/p165-blind-rediscovery-protocol \
  --title "feat(research): execute p166 preregistered record campaign" \
  --body-file /tmp/evobyte-p166-pr.md
git status --short
```
