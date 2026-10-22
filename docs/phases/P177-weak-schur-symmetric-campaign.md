# P177 — Campanha pré-registrada de Schur fraco com simetria cíclica (WS)

**Status:** Proposed.
**Programa:** Descoberta na Fronteira (P171–P190, D042). Trilhas A, B e fundação comum.
**Dependência:** P171 (catálogo v2 com `weak_schur_*`) e P172 (baselines) concluídas; branch a partir de `codex/p172-frontier-baselines-solver-harness`.
**Owner:** agente executor; revisor de sistemas nos gates de medição.
**Branch:** `codex/p177-weak-schur-symmetric-campaign`.
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [regras do programa P171–P190](README.md#programa-de-descoberta-na-fronteira-p171p190-d042), [`docs/phases/P171-frontier-target-catalogue-v2.md`](P171-frontier-target-catalogue-v2.md).

## Por que esta fase existe

Os números de Schur fraco (`weak_schur_5/6/7` no catálogo v2) estão entre os poucos recordes
combinatórios atacáveis por busca: partições de inteiros com restrição fraca
(`x < y`, `x + y = z` proibido na mesma classe) têm espaço de busca tratável por heurísticas
com simetria imposta. Esta fase executa a campanha pré-registrada nesses alvos com
**simetria cíclica** como heurística de redução — e registra o veredito honestamente,
inclusive se for nulo.

## Pergunta falsificável da fase

> Sob orçamento pré-registrado por alvo, alguma busca com simetria cíclica produz uma
> partição fraca válida estritamente maior que `best_known_value` do catálogo congelado
> para `weak_schur_5`, `weak_schur_6` ou `weak_schur_7`, certificada pelo verificador
> independente da P171?

## Fatos de partida (todos do catálogo v2; re-verificar antes de rodar)

| Fato | Como obter (não decorar) |
|---|---|
| `best_known_value`, `claimed_values`, `source_id` e `verifier` de `weak_schur_5/6/7` | `docs/research/targets/frontier_targets_v2.json` (ler do arquivo; a regra do pior caso já resolveu conflitos como OEIS-vs-papers) |
| Verificador fraco aceita `[1,1,2,1,2,2,2,1]` e rejeita `[1,1,2,1,2,2,1,2]`? | P171 teste 4 + verificador `verify_weak_schur_partition` (rodar de novo aqui como portão) |
| Simetria cíclica como heurística: partições invariantes por deslocamento têm espaço menor | Definição operacional abaixo (não é teorema; é viés de busca declarado) |

> [!IMPORTANT]
> **Nenhum valor é afirmado neste arquivo.** Em particular, **não** presuma `WS(6) ≥ 650` nem
> qualquer outro número: o alvo a superar é `best_known_value` do catálogo congelado, lido do
> JSON na execução.

## Escopo

**Arquivos que você pode criar:**
- `benchmarks/run_weak_schur_campaign.py` (campanha com simetria cíclica opcional + checkpoint)
- `experiments/p177-weak-schur-manifest.json` (pré-registro)
- `experiments/p177-weak-schur-results.json` (resultado medido + hashes)
- `tests/test_weak_schur_campaign.py` (só lógica; suíte < 3 s)
- `docs/research/p177-weak-schur-campaign-report.md`

**Arquivos que você pode editar:**
- `docs/phases/P177-weak-schur-symmetric-campaign.md`: só a linha de Status e o bloco final de execução.

**Proibido:**
- mudar a meta, o tamanho-alvo ou o critério de vitória no meio da campanha;
- chamar resultado nulo de vitória;
- buscas ou avaliações de partições dentro de `tests/`.

## Trabalho ordenado

### Passo 1 — Branch e pré-condições

```bash
git status --short
git switch codex/p172-frontier-baselines-solver-harness
git switch -c codex/p177-weak-schur-symmetric-campaign
test -f docs/research/targets/frontier_targets_v2.json || { echo "P171 NAO CONCLUIDA"; exit 1; }
python3 - <<'PY'
import json
cat = json.load(open("docs/research/targets/frontier_targets_v2.json"))
for t in cat["targets"]:
    if t["target_id"].startswith("weak_schur_"):
        print(t["target_id"], t["best_known_value"], t["verifier"])
PY
```

### Passo 2 — Manifesto `experiments/p177-weak-schur-manifest.json` (congelar ANTES de rodar)

```json
{
  "phase": "P177",
  "targets": ["weak_schur_5", "weak_schur_6", "weak_schur_7"],
  "targets_source": "docs/research/targets/frontier_targets_v2.json",
  "attempt_sizes": ["best_known_value + 1"],
  "symmetry": {"kind": "cyclic_shift_period_p", "periods": [1], "note": "heurística de redução, não teorema"},
  "budget_sec_per_seed": 120.0,
  "seeds": [42, 101, 202],
  "algorithms": ["SimulatedAnnealing", "HillClimbing"],
  "verifier": "frontier_catalogue.verify_weak_schur_partition",
  "verdict_rule": {
    "DISCOVERY_BEATEN": "partição fraca válida de tamanho best_known_value + 1, certificada",
    "NULL_RESULT": "orçamento esgotado sem certificado acima de best_known_value"
  }
}
```

**Simetria cíclica (definição operacional honesta):** o modo simétrico restringe a busca a
partições periódicas de período `p` (`cor[i] = cor[i mod p]`); o modo livre não restringe.
Ambos os modos rodam sob o mesmo orçamento; o relatório compara os dois. Como a restrição
pode excluir o ótimo, um `NULL_RESULT` no modo simétrico **não** prova inexistência — e o
relatório diz isso explicitamente.

### Passo 3 — `benchmarks/run_weak_schur_campaign.py`

Mesmo protocolo da P176 (`--manifest/--output/--checkpoint/--resume`): para cada
`(alvo, algoritmo, semente, modo)`, busca sob orçamento duplo; **toda** partição válida de
tamanho `best_known_value + 1` é submetida ao verificador P171 imediatamente; certificado →
`DISCOVERY_BEATEN` com o objeto + SHA-256. Checkpoint incremental, resumo com trials brutos.

### Passo 4 — Testes `tests/test_weak_schur_campaign.py` (todos < 0,2 s; suíte < 3 s)

1. `test_verdict_rule_beaten_vs_null`: certificado maior que `best_known_value` → `DISCOVERY_BEATEN`; sem certificado → `NULL_RESULT` (fixtures estáticas, sem busca).
2. `test_symmetric_mode_restricts_space`: com período `p`, o gerador de vizinhança só propõe partições `p`-periódicas (verificação estática do invariante, sem busca).
3. `test_manifest_schema`: manifesto tem alvos, tamanhos, orçamento, sementes, algoritmos, simetria e regra de veredito; todo `target_id` existe no catálogo v2 com `role = record`.
4. `test_break_size_is_best_plus_one`: para os 3 alvos, o tamanho de quebra usado é exatamente `best_known_value + 1` lido do catálogo (nunca número digitado).

### Passo 5 — Relatório `docs/research/p177-weak-schur-campaign-report.md`

Tabela de vereditos por alvo e modo, melhor partição encontrada por configuração, integridade
(hash do manifesto, seeds, orçamentos), comparação simétrico-vs-livre, e a frase literal
aplicável (vitória com certificado, ou a declaração de resultado nulo do AGENTS.md).

## Regras de parada (PARE, não commite, reporte)

- Qualquer certificado `DISCOVERY_BEATEN` falhar no verificador independente.
- O script abortar no meio sem gravar os dados brutos.
- Qualquer teste > 0,2 s ou suíte > 3 s; qualquer busca dentro de `tests/`.
- Falha no pytest ou no `make verify`.

## Gate de saída

```bash
git diff --check
python3 -m pytest tests/test_weak_schur_campaign.py -q -m "not slow"   # FAST LOOP, ~1s
python3 benchmarks/run_weak_schur_campaign.py --manifest experiments/p177-weak-schur-manifest.json --output experiments/p177-weak-schur-results.json --checkpoint experiments/p177-weak-schur-checkpoint.json
python3 -m pytest tests/test_weak_schur_campaign.py -q                 # FINAL GATE, < 3s
make verify
git status --short
```

## Commit & Push (obrigatório)

```bash
git add benchmarks/run_weak_schur_campaign.py experiments/p177-weak-schur-manifest.json \
  experiments/p177-weak-schur-results.json experiments/p177-weak-schur-checkpoint.json \
  tests/test_weak_schur_campaign.py docs/research/p177-weak-schur-campaign-report.md \
  docs/phases/P177-weak-schur-symmetric-campaign.md
git diff --cached --check
git commit -m "feat(research): execute p177 weak schur symmetric campaign"
git push -u origin HEAD
gh pr create --base codex/p172-frontier-baselines-solver-harness \
  --title "feat(research): p177 weak schur campaign" \
  --body-file /tmp/evobyte-p177-pr.md
git status --short
```

O corpo do PR (`/tmp/evobyte-p177-pr.md`) traz: problema, comportamento resultante, comandos de
validação exatos, números medidos (vereditos por alvo/modo, melhores partições), limitações
(simetria é heurística, não prova de inexistência) e o link do relatório.
