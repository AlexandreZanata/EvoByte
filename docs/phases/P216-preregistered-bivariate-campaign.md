# P216 — Campanha pré-registrada estruturada em alvos bivariados e projetivos (Preregistered Bivariate Campaign)

**Status:** Done (2026-10-28).
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
  - `DISCOVERY_BROKEN` (ou `DISCOVERY_BEATEN`): caso uma solução supere a cota conhecida da literatura mundial ($d > d_{lo}$ em QECC ou tamanho de bloco $< U$ em coverings).
  - `DISCOVERY_TIED`: caso atinja a melhor cota conhecida igualando o recorde mundial ($d = d_{lo}$ ou tamanho $= U$).
  - `NULL_BOUND`: caso a busca exhaustiva em órbitas comprove impossibilidade de solução no espaço explorado.
  - `NULL_RESULT` (ou `INCONCLUSIVE`): caso o orçamento se esgote sem decisão completa.
- **Isolamento de Sementes e Reprodutibilidade:** Sementes pseudoaleatórias congeladas e registradas.

## Pergunta falsificável da fase

> A campanha pré-registrada produz resultados auditáveis nos 5 alvos congelados sob orçamentos pré-definidos, gerando vereditos matemáticos rastreáveis sem qualquer falso positivo ou alteração de thresholds post-hoc?

**Resposta:** SIM. A campanha pré-registrada foi executada em todos os 25 ensaios (5 alvos $\times$ 5 sementes `[42, 43, 44, 45, 46]`) em $69,63$\,s, alcançando veredito global **`DISCOVERY_TIED`**:
1. **5 realizações `DISCOVERY_TIED`:** Código quântico bicíclico bivariado $[[20, 2, 6]]$ sobre $\mathbb{F}_2[\mathbb{Z}_5 \times \mathbb{Z}_2]$ empatando com o recorde de Markus Grassl ($d=6$), verificado pelo verificador de estabilizadores e certificado por SAT solver exato (CaDiCaL) em $< 0,1$\,s por ensaio.
2. **10 provas analíticas `NULL_BOUND`:** Provado que qualquer covering design invariante sob $\text{PGL}(2, 13)$ em $C(14, 6, 3)$ exige pelo menos 91 blocos ($> 25$), e sob $\text{AGL}(2, 4)$ em $C(16, 7, 3)$ exige pelo menos 160 blocos ($> 24$).
3. **10 ensaios `NULL_RESULT`:** Para $[[18, 3, d]]$ e $[[20, 3, d]]$, o solver gerou códigos quânticos válidos com $d=4$, mantendo-se honestamente abaixo dos recordes de Grassl ($d=5$ e $d=6$).

## Escopo Realizado

**Arquivos criados/editados:**
- `src/evobyte/bivariate_campaign.py`: orquestrador da campanha pré-registrada.
- `experiments/p216-bivariate-campaign-results.json`: log exato de todos os candidatos, tempos, orçamentos e vereditos.
- `docs/research/p216-preregistered-bivariate-campaign-report.md`: relatório técnico formal da campanha.
- `tests/test_bivariate_campaign.py`: testes de conformidade com o manifesto da P211 (6/6 testes verdes).
- `docs/phases/P216-preregistered-bivariate-campaign.md`: atualização de status e evidências.

## Critérios de Saída (Gates)

1. `tests/test_bivariate_campaign.py` passa 100% verde validando orçamentos e vereditos — Aprovado (6/6 testes verdes em 39,97s).
2. Todos os 5 alvos congelados da P211 possuem registro estruturado em `experiments/p216-bivariate-campaign-results.json` — Aprovado (25 ensaios registrados com hash SHA-256).
3. `git diff --check`, `git status --short`, `make lint` e `python3 -m pytest tests -q` passam sem erros — Aprovado.

## Commit & Push

```bash
git add src/evobyte/bivariate_campaign.py \
  experiments/p216-bivariate-campaign-results.json \
  experiments/p216-bivariate-campaign-checkpoint.json \
  docs/research/p216-preregistered-bivariate-campaign-report.md \
  tests/test_bivariate_campaign.py \
  docs/phases/P216-preregistered-bivariate-campaign.md
git commit -m "feat(frontier): execute preregistered bivariate campaign (P216)"
git push -u origin codex/p216-preregistered-bivariate-campaign
gh pr create --base main \
  --title "feat(frontier): execute preregistered bivariate campaign (P216)" \
  --body "Executa campanha pré-registrada bivariada e projetiva sob D047."
```
