# P176 — Campanha pré-registrada de covering designs (40 alvos LJCR, objetivo: recorde)

**Status:** Completed.
**Programa:** Descoberta na Fronteira (P171–P190, D042). Trilhas A, B e fundação comum.
**Dependência:** P171 (catálogo v2 com 40 alvos) e P172 (baselines calibrados) concluídas; branch a partir de `codex/p172-frontier-baselines-solver-harness`.
**Owner:** agente executor; revisor estatístico nos gates de veredito.
**Branch:** `codex/p176-preregistered-covering-designs-campaign`.
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [regras do programa P171–P190](README.md#programa-de-descoberta-na-fronteira-p171p190-d042), [`docs/phases/P171-frontier-target-catalogue-v2.md`](P171-frontier-target-catalogue-v2.md).

## Por que esta fase existe

O catálogo v2 da P171 congela 40 alvos de covering designs com cotas publicadas **não
provadas ótimas** — o primeiro terreno do programa onde um recorde mundial é matematicamente
possível. Esta fase executa a campanha pré-registrada contra esses 40 alvos: se algum
candidato com menos blocos que `published_size` passar no verificador independente da P171,
temos uma descoberta inédita; se o orçamento esgotar sem isso, registra-se `NULL_RESULT`
por alvo, sem redefinir a meta no meio do caminho.

## Pergunta falsificável da fase

> Sob orçamento pré-registrado por alvo, alguma busca (SA / Hill-Climbing / guloso+vizinhança)
> produz um covering design com estritamente menos blocos que `published_size` para qualquer
> um dos 40 alvos congelados, validado pelo verificador independente da P171?

## Fatos de partida (todos do catálogo v2; re-verificar antes de rodar)

| Fato | Como obter (não decorar) |
|---|---|
| Os 40 `target_id` de covering + `published_size` + `verifier=verify_covering_design` | `docs/research/targets/frontier_targets_v2.json` (ler do arquivo) |
| Verificador aceita Fano/AG(2,3)/S(3,4,8) e rejeita remoções | P171 teste 1–2 (rodar de novo aqui como portão) |
| Baselines calibrados e orçamento por ensaio | P172 (`frontier_baselines.py` + `p172-calibration.json`) |
| `ljcr_pool_v2.json` documenta o pool e a regra de seleção | P171 (não re-selecionar; usar os 40 congelados) |

> [!IMPORTANT]
> **Regra do tamanho.** O alvo de recorde para `C(v,k,t)` usa exatamente `published_size - 1`
> blocos como *primeira* tentativa de quebra (se existir covering com esse tamanho, é recorde
> por definição). Tamanhos menores entram na fila só se o anterior for encontrado e certificado.

## Escopo

**Arquivos que você pode criar:**
- `benchmarks/run_covering_campaign.py` (campanha com checkpoint de progresso + orçamento configurável)
- `experiments/p176-covering-manifest.json` (pré-registro: alvos, orçamento, sementes, regra de veredito)
- `experiments/p176-covering-results.json` (resultado medido + hashes)
- `tests/test_covering_campaign.py` (só lógica: veredito, checkpoint, integridade; suíte < 3 s)
- `docs/research/p176-covering-campaign-report.md`

**Arquivos que você pode editar:**
- `docs/phases/P176-preregistered-covering-designs-campaign.md`: só a linha de Status e o bloco final de execução.

**Proibido:**
- mudar a meta, o tamanho de quebra ou o critério de vitória no meio da campanha;
- chamar resultado nulo de vitória; se não bateu o recorde, o veredito é `NULL_RESULT`;
- buscas ou avaliações de covering dentro de `tests/` (tudo > 0,2 s é proibido).

## Trabalho ordenado

### Passo 1 — Branch e pré-condições

```bash
git status --short
git switch codex/p172-frontier-baselines-solver-harness
git switch -c codex/p176-preregistered-covering-designs-campaign
test -f docs/research/targets/frontier_targets_v2.json || { echo "P171 NAO CONCLUIDA"; exit 1; }
python3 -m pytest tests/test_frontier_catalogue.py -q -m "not slow"  # portões P171 verdes
```

### Passo 2 — Manifesto `experiments/p176-covering-manifest.json` (congelar ANTES de rodar)

```json
{
  "phase": "P176",
  "targets": ["covering_C_..._...", "..."],
  "targets_source": "docs/research/targets/frontier_targets_v2.json",
  "attempt_sizes": ["published_size - 1"],
  "budget_sec_per_seed": 120.0,
  "seeds": [42, 101, 202],
  "algorithms": ["SimulatedAnnealing", "HillClimbing", "GreedyPlusLocalSearch"],
  "verifier": "frontier_catalogue.verify_covering_design",
  "verdict_rule": {
    "DISCOVERY_BEATEN": "candidato certificado com blocos < published_size",
    "NULL_RESULT": "orçamento esgotado sem certificado abaixo de published_size"
  }
}
```

Os 40 `target_id` vêm do catálogo (copiar do JSON, não da memória). Commit do manifesto
**antes** da execução (commit separado ou mesma PR com timestamp anterior, como na P166).

### Passo 3 — `benchmarks/run_covering_campaign.py`

Executor com `--manifest ... --output ... --checkpoint ... --resume`:
- para cada `(alvo, tamanho, algoritmo, semente)`: busca sob orçamento duplo
  (tempo OU avaliações, o que estourar primeiro);
- **todo** candidato com blocos < `published_size` é submetido ao verificador P171
  **imediatamente**; certificado → registra `DISCOVERY_BEATEN` com o objeto + SHA-256 e
  segue para o próximo alvo (não para a campanha: um recorde não cancela os demais alvos);
- checkpoint incremental em JSON após cada ensaio (resume sem recomeçar);
- ao final: `summary.json` com trials brutos + vereditos por alvo + hashes + tempo total.

### Passo 4 — Testes `tests/test_covering_campaign.py` (todos < 0,2 s; suíte < 3 s)

1. `test_verdict_rule_beaten_vs_null`: veredito `DISCOVERY_BEATEN` com certificado menor que
   `published_size` (fixture estática); `NULL_RESULT` sem certificado.
2. `test_checkpoint_resume_roundtrip`: escreve checkpoint parcial falso, retoma e não repete
   ensaios concluídos.
3. `test_manifest_schema`: manifesto tem alvos, tamanhos, orçamento, sementes, algoritmos e
   regra de veredito; todo `target_id` existe no catálogo v2.
4. `test_break_size_is_published_minus_one`: para 3 alvos amostrados do catálogo, o tamanho
   de quebra usado pelo executor é exatamente `published_size - 1`.

### Passo 5 — Relatório `docs/research/p176-covering-campaign-report.md`

Resumo executivo (alvos, ensaios, avaliações, tempo), tabela de vereditos por alvo
(`DISCOVERY_BEATEN` com certificado + hash, ou `NULL_RESULT` com melhor cobertura medida),
integridade (hash do manifesto, seeds, orçamentos) e a frase literal aplicável:
para cada alvo sem recorde, *"A busca estocástica sob o orçamento pré-registrado não superou
a cota publicada. O resultado nulo é publicado de acordo com a regra de integridade
científica de AGENTS.md."*

## Regras de parada (PARE, não commite, reporte)

- Qualquer candidato rotulado `DISCOVERY_BEATEN` falhar no verificador independente.
- O script abortar no meio sem gravar os dados brutos (o checkpoint existe para isso; se
  mesmo assim houver perda, reporte).
- Qualquer teste > 0,2 s ou suíte > 3 s; qualquer busca dentro de `tests/`.
- Falha no pytest ou no `make verify`.

## Gate de saída

```bash
git diff --check
python3 -m pytest tests/test_covering_campaign.py -q -m "not slow"   # FAST LOOP, ~1s
python3 benchmarks/run_covering_campaign.py --manifest experiments/p176-covering-manifest.json --output experiments/p176-covering-results.json --checkpoint experiments/p176-covering-checkpoint.json
python3 -m pytest tests/test_covering_campaign.py -q                 # FINAL GATE, < 3s
make verify
git status --short
```

## Commit & Push (obrigatório)

```bash
git add benchmarks/run_covering_campaign.py experiments/p176-covering-manifest.json \
  experiments/p176-covering-results.json experiments/p176-covering-checkpoint.json \
  tests/test_covering_campaign.py docs/research/p176-covering-campaign-report.md \
  docs/phases/P176-preregistered-covering-designs-campaign.md
git diff --cached --check
git commit -m "feat(research): execute p176 preregistered covering designs campaign"
git push -u origin HEAD
gh pr create --base codex/p172-frontier-baselines-solver-harness \
  --title "feat(research): p176 covering designs campaign" \
  --body-file /tmp/evobyte-p176-pr.md
git status --short
```

O corpo do PR (`/tmp/evobyte-p176-pr.md`) traz: problema, comportamento resultante, comandos de
validação exatos, números medidos (ensaios, avaliações, vereditos por alvo com certificados ou
nulos), limitações (orçamento por alvo, sem redefinição de meta) e o link do relatório.
