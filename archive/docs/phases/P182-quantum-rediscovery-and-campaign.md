# P182 — Redescoberta cega de QECC e campanha pré-registrada em parâmetros abertos

**Status:** Completed.
**Programa:** Descoberta na Fronteira (P171–P190, D042). Trilhas A, B e fundação comum.
**Dependência:** P180 (catálogo QECC) e P181 (motor de busca) concluídas; branch a partir de `codex/p181-quantum-stabilizer-evolution`.
**Owner:** agente executor; revisor formal/estatístico nos gates de veredito.
**Branch:** `codex/p182-quantum-rediscovery-and-campaign`.
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [regras do programa P171–P190](README.md#programa-de-descoberta-na-fronteira-p171p190-d042), [`docs/phases/P180-grassl-bounds-frontier-catalogue.md`](P180-grassl-bounds-frontier-catalogue.md), [`docs/phases/P181-quantum-stabilizer-evolution.md`](P181-quantum-stabilizer-evolution.md).

## Por que esta fase existe

Antes de caçar recordes quânticos, o motor precisa provar competência reproduzindo códigos
conhecidos **sem ver a resposta** (redescoberta cega de Steane [[7,1,3]] e Shor [[9,1,3]] a
partir de inicialização aleatória) e, em seguida, executar a campanha pré-registrada nos
parâmetros abertos do catálogo P180 — com a mesma disciplina da P166 (manifesto antes,
veredito honesto depois, `NULL_RESULT` se for o caso).

## Pergunta falsificável da fase

> O motor da P181 redescobre Steane [[7,1,3]] e Shor [[9,1,3]] a partir de inicialização
> aleatória dentro do orçamento de calibração, e a campanha pré-registrada nos parâmetros
> abertos do catálogo produz ao menos um `DISCOVERY_BEATEN` certificado — ou registra
> `NULL_RESULT` formal?

## Fatos de partida (todos re-verificados na execução)

| Fato | Fonte |
|---|---|
| Steane [[7,1,3]] / Shor [[9,1,3]]: geradores canônicos e `d = 3` | P179 (verificador + testes) |
| Alvos abertos (`role = record`, gap documentado) e calibrações | Catálogo P180 (`qecc_frontier_v1.json`) |
| Motor de busca + protocolo de ensaio com checkpoint | P181 (`benchmarks/run_stabilizer_search.py`) |
| Disciplina de pré-registro | P166/P176 (manifesto antes, veredito depois) |

## Escopo

**Arquivos que você pode criar:**
- `benchmarks/run_qecc_campaign.py` (redescoberta cega + campanha pré-registrada, com checkpoint)
- `experiments/p182-qecc-manifest.json` (pré-registro: alvos, orçamento, sementes, regra de veredito)
- `experiments/p182-qecc-results.json` (resultado medido + hashes)
- `tests/test_qecc_campaign.py` (só lógica: veredito, checkpoint, integridade; suíte < 3 s)
- `docs/research/p182-qecc-campaign-report.md`

**Arquivos que você pode editar:**
- `docs/phases/P182-quantum-rediscovery-and-campaign.md`: só a linha de Status e o bloco final de execução.

**Proibido:**
- inicializar a busca com os geradores publicados (a população inicial é aleatória;
  *seeds* manuais de soluções são proibidas — a P183 reforça a mesma regra para Hamiltonianos);
- mudar a meta, o tamanho ou o critério de vitória no meio da campanha;
- buscas/evoluções dentro de `tests/`.

## Trabalho ordenado

### Passo 1 — Branch e pré-condições

```bash
git status --short
git switch codex/p181-quantum-stabilizer-evolution
git switch -c codex/p182-quantum-rediscovery-and-campaign
test -f docs/research/targets/qecc_frontier_v1.json || { echo "P180 NAO CONCLUIDA"; exit 1; }
python3 -m pytest tests/test_qecc_catalogue.py -q -m "not slow"     # portões P180 verdes
python3 -m pytest tests/test_stabilizer_search.py -q -m "not slow"  # portões P181 verdes
```

### Passo 2 — Manifesto `experiments/p182-qecc-manifest.json` (congelar ANTES de rodar)

```json
{
  "phase": "P182",
  "calibration": {"targets": ["steane_7_1_3", "shor_9_1_3"], "budget_sec_per_seed": 30.0, "seeds": [42, 101]},
  "campaign": {"targets": ["<ids role=record do catálogo P180>"], "budget_sec_per_seed": 300.0, "seeds": [42, 101, 202]},
  "targets_source": "docs/research/targets/qecc_frontier_v1.json",
  "algorithms": ["StabilizerEvolution"],
  "verifier": "qecc_verifier.code_distance",
  "verdict_rule": {
    "REDISCOVERY_OK": "calibração reencontra d publicado a partir de init aleatório",
    "DISCOVERY_BEATEN": "candidato certificado com d > best_known_value do catálogo",
    "NULL_RESULT": "orçamento esgotado sem certificado acima da cota"
  }
}
```

Os `target_id` de campanha vêm do catálogo (copiar do JSON, não da memória). Commit do
manifesto **antes** da execução.

### Passo 3 — `benchmarks/run_qecc_campaign.py`

`--manifest ... --output ... --checkpoint ... [--resume]`: Fase 1 = redescoberta cega
(calibrações, init aleatório, sem seeds manuais); Fase 2 = campanha nos alvos de recorde.
Todo candidato com `d > best_known_value` é revalidado pelo verificador P179 imediatamente;
certificado → `DISCOVERY_BEATEN` com o conjunto estabilizador + SHA-256. Checkpoint
incremental; resumo com trials brutos + vereditos.

### Passo 4 — Testes `tests/test_qecc_campaign.py` (todos < 0,2 s; suíte < 3 s)

1. `test_verdict_rule_beaten_vs_null`: certificado com `d` acima da cota → `DISCOVERY_BEATEN`; sem certificado → `NULL_RESULT` (fixtures estáticas).
2. `test_no_manual_seeds_in_campaign_config`: o manifesto e o script rejeitam inicialização com geradores publicados (checagem estática: nenhuma string estabilizadora literal de calibração no caminho de init).
3. `test_checkpoint_resume_roundtrip`: checkpoint parcial falso retoma sem repetir ensaios.
4. `test_manifest_schema`: alvos, orçamentos, sementes, algoritmos, verificador e regra de veredito presentes; todo alvo existe no catálogo P180.

### Passo 5 — Relatório `docs/research/p182-qecc-campaign-report.md`

Redescoberta (atingida ou não, com tempos), vereditos por alvo de recorde (certificados ou
nulos com melhor `d` medido), integridade (hash do manifesto, seeds, orçamentos) e a frase
literal aplicável (vitória com certificado, ou a declaração de resultado nulo do AGENTS.md).

## Regras de parada (PARE, não commite, reporte)

- Qualquer certificado `DISCOVERY_BEATEN` falhar no verificador independente.
- O script abortar no meio sem gravar os dados brutos.
- Qualquer teste > 0,2 s ou suíte > 3 s; qualquer busca/evolução dentro de `tests/`.
- Se a calibração falhar (motor não reencontra Steane/Shor): reporte como evidência contra o
  motor e **PARE antes da campanha** (não faz sentido caçar recordes sem calibrar).
- Falha no pytest ou no `make verify`.

## Gate de saída

```bash
git diff --check
python3 -m pytest tests/test_qecc_campaign.py -q -m "not slow"   # FAST LOOP, ~1s
python3 benchmarks/run_qecc_campaign.py --manifest experiments/p182-qecc-manifest.json --output experiments/p182-qecc-results.json --checkpoint experiments/p182-qecc-checkpoint.json
python3 -m pytest tests/test_qecc_campaign.py -q                 # FINAL GATE, < 3s
make verify
git status --short
```

## Commit & Push (obrigatório)

```bash
git add benchmarks/run_qecc_campaign.py experiments/p182-qecc-manifest.json \
  experiments/p182-qecc-results.json experiments/p182-qecc-checkpoint.json \
  tests/test_qecc_campaign.py docs/research/p182-qecc-campaign-report.md \
  docs/phases/P182-quantum-rediscovery-and-campaign.md
git diff --cached --check
git commit -m "feat(quantum): execute p182 qecc rediscovery and preregistered campaign"
git push -u origin HEAD
gh pr create --base codex/p181-quantum-stabilizer-evolution \
  --title "feat(quantum): p182 qecc campaign" \
  --body-file /tmp/evobyte-p182-pr.md
git status --short
```

O corpo do PR (`/tmp/evobyte-p182-pr.md`) traz: problema, comportamento resultante, comandos de
validação exatos, números medidos (redescoberta sim/não com tempos; vereditos por alvo),
limitações e o link do relatório.
