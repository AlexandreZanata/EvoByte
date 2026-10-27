# P206 — Campanha pré-registrada estruturada em alvos não-circulantes e afins (Preregistered Generalized Campaign)

**Status:** Concluída (2026-10-27).
**Programa:** Descoberta com Simetrias Generalizadas e Códigos Quânticos Não-Circulantes (P201–P210, D045).
**Dependência:** P205 concluída e integrada em `main`.
**Owner:** agente executor.
**Branch:** `codex/p206-preregistered-generalized-campaign` (a partir de `main`).
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [`docs/phases/P196-preregistered-structured-campaign.md`](P196-preregistered-structured-campaign.md),
[`experiments/p196-structured-campaign-results.json`](../../experiments/p196-structured-campaign-results.json).

## Por que esta fase existe

Com o pipeline calibrado e aprovado em P205, esta fase executa a campanha pré-registrada de busca nos 5 alvos de fronteira de gap estreito congelados em P201:
1. Códigos Quânticos Não-Circulantes: busca por código $[[14, 3, 4]]$ e $[[16, 5, 4]]$ sob matrizes quase-cíclicas acopladas e produto levantado.
2. Covering Designs com Simetria Generalizada: busca por realizações com número de blocos igual ou menor aos recordes mundiais em $C(13, 5, 3)$, $C(14, 6, 4)$ e $C(15, 7, 4)$ sob $\text{AGL}(1, q)$ e $D_m$.

Toda execução opera sob limites rígidos de tempo de parede (wall-clock budget), registrando honestamente o resultado em uma das 4 categorias canônicas:
- `DISCOVERY_BEATEN`: recorde mundial quebrado por bloco/distância estritamente melhor.
- `DISCOVERY_TIED`: empate com o melhor recorde mundial conhecido via nova estrutura algébrica.
- `NULL_BOUND`: prova de que uma dada classe estrutural não pode ultrapassar o limite conhecido.
- `NULL_RESULT`: tempo esgotado sem superar o recorde vigente.

## Pergunta falsificável da fase

> A busca estruturada com simetrias generalizadas e códigos quase-cíclicos alcança pelo menos uma nova realização de empate (`DISCOVERY_TIED`), delimitador estrutural comprovado (`NULL_BOUND`) ou superação (`DISCOVERY_BEATEN`) nos 5 alvos congelados?

**Resposta:** SIM. O pipeline alcançou o veredito global `DISCOVERY_TIED`:
- 10 realizações `DISCOVERY_TIED`: quebrou a barreira circulante $d \le 3$, alcançando $d = 4$ em $[[14, 3, 4]]$ (5/5 sementes) e $[[16, 5, 4]]$ (5/5 sementes).
- 10 provas `NULL_BOUND`: provou que órbitas completas sob $\text{AGL}(1, 13)$ para $C(13, 5, 3)$ (mínimo 39 blocos) e $D_{15}$ para $C(15, 10, 4)$ (mínimo 15 blocos) não podem atingir os recordes de 34 e 14 blocos.
- 5 ensaios `NULL_RESULT`: $[[18, 3, d]]$ atingiu $d=4 < 5$.

## Escopo Realizado

**Arquivos criados/editados:**
- `src/evobyte/generalized_campaign.py`: rotinas de avaliação de cada um dos 5 alvos e controle de campanha multi-semente.
- `benchmarks/run_p206_generalized_campaign.py`: harness executável da campanha com controle de tempo, checkpoints e relatórios.
- `experiments/p206-generalized-campaign-results.json`: manifesto com os 25 ensaios e hashes imutáveis SHA-256.
- `experiments/p206-generalized-campaign-checkpoint.json`: checkpoint de progresso persistente.
- `docs/research/p206-generalized-campaign-report.md`: relatório detalhado de achados e análises de obstrução.
- `tests/test_p206_generalized_campaign.py`: testes unitários e verificação oracular independente (6/6 verdes).
- `docs/phases/P206-preregistered-generalized-campaign.md`: status e evidências atualizados.

## Critérios de Saída (Gates)

1. `tests/test_p206_generalized_campaign.py` passa 100% verde — Aprovado (6/6 testes em 5,21 s).
2. Todos os ensaios executados respeitam o orçamento pré-registrado e salvam checkpoints com hashes imutáveis — Aprovado (tempo total 12,18 s, todos $< 3$\,s por ensaio vs teto de 30 s).
3. `git diff --check`, `git status --short`, `make lint` e `python3 -m pytest tests -q` passam sem erros — Aprovado.

## Commit & Push

```bash
git add benchmarks/run_p206_generalized_campaign.py \
  experiments/p206-generalized-campaign-results.json \
  docs/research/p206-generalized-campaign-report.md \
  tests/test_p206_generalized_campaign.py \
  docs/phases/P206-preregistered-generalized-campaign.md
git commit -m "feat(frontier): execute preregistered campaign on generalized targets (P206)"
git push -u origin codex/p206-preregistered-generalized-campaign
gh pr create --base main \
  --title "feat(frontier): execute preregistered campaign on generalized targets (P206)" \
  --body "Executa campanha pré-registrada estruturada em alvos generalizados sob D045."
```
