# P206 — Campanha pré-registrada estruturada em alvos não-circulantes e afins (Preregistered Generalized Campaign)

**Status:** Proposed.
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

## Escopo

**Arquivos a criar/editar:**
- `benchmarks/run_p206_generalized_campaign.py`: harness executável da campanha estruturada com controle de orçamento e sementes.
- `experiments/p206-generalized-campaign-results.json`: resultados brutos completos com tempos e métricas.
- `docs/research/p206-generalized-campaign-report.md`: relatório detalhado de achados e análises comparativas.
- `tests/test_p206_generalized_campaign.py`: verificação automatizada de sanidade e integridade dos resultados.
- `docs/phases/P206-preregistered-generalized-campaign.md`: atualização de status e evidências.

## Critérios de Saída (Gates)

1. `tests/test_p206_generalized_campaign.py` passa 100% verde.
2. Todos os ensaios executados respeitam o orçamento pré-registrado e salvam checkpoints com hashes imutáveis.
3. `git diff --check`, `git status --short`, `make lint` e `python3 -m pytest tests -q` passam sem erros.

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
