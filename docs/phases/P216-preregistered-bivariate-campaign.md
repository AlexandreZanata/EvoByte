# P216 — Campanha pré-registrada estruturada em alvos bivariados e projetivos (Preregistered Bivariate Campaign)

**Status:** Proposed.
**Programa:** Descoberta com Códigos Quânticos Bicíclicos Bivariados e Geometrias Projetivas (P211–P220, D047).
**Dependência:** P215 concluída e integrada em `main`.
**Owner:** agente executor.
**Branch:** `codex/p216-preregistered-bivariate-campaign` (a partir de `main`).
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [`docs/phases/P206-preregistered-generalized-campaign.md`](P206-preregistered-generalized-campaign.md),
[`docs/phases/P196-preregistered-structured-campaign.md`](P196-preregistered-structured-campaign.md).

## Por que esta fase existe

Esta fase executa a busca sistemática nos 5 alvos de fronteira congelados na P211, operando sob o protocolo científico estrito do EvoByte:
- **Orçamentos Rígidos Pré-Registrados:** Limite determinístico de iterações, candidatos avaliados e timeout de parede por alvo.
- **Protocolo de Classificação:**
  - `DISCOVERY_BROKEN`: caso uma solução supere a cota conhecida da literatura mundial ($d > d_{lo}$ em QECC ou tamanho de bloco $< U$ em coverings).
  - `DISCOVERY_TIED`: caso atinja a melhor cota conhecida igualando o recorde mundial ($d = d_{lo}$ ou tamanho $= U$).
  - `NULL_BOUND`: caso a busca exhaustiva em órbitas comprove impossibilidade de solução no espaço explorado.
  - `INCONCLUSIVE`: caso o orçamento se esgote sem decisão completa.
- **Isolamento de Sementes e Reprodutibilidade:** Sementes pseudoaleatórias congeladas e registradas.

## Pergunta falsificável da fase

> A campanha pré-registrada produz resultados auditáveis nos 5 alvos congelados sob orçamentos pré-definidos, gerando vereditos matemáticos rastreáveis sem qualquer falso positivo ou alteração de thresholds post-hoc?

## Escopo

**Arquivos a criar/editar:**
- `src/evobyte/bivariate_campaign.py`: orquestrador da campanha pré-registrada.
- `experiments/p216-bivariate-campaign-results.json`: log exato de todos os candidatos, tempos, orçamentos e vereditos.
- `docs/research/p216-preregistered-bivariate-campaign-report.md`: relatório técnico formal da campanha.
- `tests/test_bivariate_campaign.py`: testes de conformidade com o manifesto da P211.
- `docs/phases/P216-preregistered-bivariate-campaign.md`: atualização de status e evidências.

## Critérios de Saída (Gates)

1. `tests/test_bivariate_campaign.py` passa 100% verde validando orçamentos e vereditos.
2. Todos os 5 alvos congelados da P211 possuem registro estruturado em `experiments/p216-bivariate-campaign-results.json`.
3. `git diff --check`, `git status --short`, `make lint` e `python3 -m pytest tests -q` passam sem erros.

## Commit & Push

```bash
git add src/evobyte/bivariate_campaign.py \
  experiments/p216-bivariate-campaign-results.json \
  docs/research/p216-preregistered-bivariate-campaign-report.md \
  tests/test_bivariate_campaign.py \
  docs/phases/P216-preregistered-bivariate-campaign.md
git commit -m "feat(frontier): execute preregistered bivariate campaign (P216)"
git push -u origin codex/p216-preregistered-bivariate-campaign
gh pr create --base main \
  --title "feat(frontier): execute preregistered bivariate campaign (P216)" \
  --body "Executa campanha pré-registrada bivariada e projetiva sob D047."
```
