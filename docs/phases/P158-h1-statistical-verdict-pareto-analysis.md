# P158 — Veredito estatístico dos 5 critérios de H1 e análise de fronteira de Pareto

**Status:** Proposed.
**Dependência:** P157 concluída; branch a partir de `codex/p157-full-cascade-gpu-ablations-measurement`.
**Owner:** agente executor; revisor formal/sistemas nos gates indicados.
**Pré-requisito:** P154–P157 concluídas com dados brutos auditados.
**Branch:** `codex/p158-h1-statistical-verdict-pareto-analysis`.

## Hipótese, objetivo e escopo

Consolidar a análise estatística formal sobre os dados brutos reais de P154–P157 para avaliar conclusivamente os 5 critérios falsificáveis de H1 definidos em `docs/HYPOTHESIS.md`: (1) Redescoberta; (2) Throughput CVPS provado; (3) Valor da evolução vs. aleatório; (4) Generalização vs. memorização; (5) Baselines honestos e Fronteira de Pareto (MSE vs. tamanho em bytes). Aplicar testes de postos sinalizados de Wilcoxon e controle FWER de Bonferroni–Holm ($\alpha = 0.01$). Emitir veredito final formal com intervalos de confiança de 95%.

Alterações permitidas: `benchmarks/statistical_verdict.py`, `docs/research/p158-h1-verdict-report.md`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p158-config.json`, `experiments/p158-run.sh`.
Fora do escopo: alteração seletiva de outliers; cálculo de médias sem intervalos de dispersão.

Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar rotina de consolidação estatística formal em `benchmarks/statistical_verdict.py`.
2. Computar curvas de Pareto empíricas (CVPS vs. MSE e Tamanho de Expressão vs. MSE) comparando EvoByte contra Random, GP e PySR.
3. Emitir o relatório detalhado de avaliação dos 5 critérios em `docs/research/p158-h1-verdict-report.md`.
4. Adicionar interface de auditoria P158 em `benchmarks/science_matrix.py` (`run_p158_h1_verdict_audit`).

## Gate de saída

Veredito formal estatisticamente suportado ($p \le 0.01$) e relatório aceito em árvore limpa:

```bash
git diff --check
git status --short
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P158 --config experiments/p158-config.json --output /tmp/evobyte-p158-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(statistical): implement p158 h1 statistical verdict pareto analysis"
git push -u origin HEAD
gh pr create --base codex/p157-full-cascade-gpu-ablations-measurement --title "feat(statistical): implement p158 h1 statistical verdict pareto analysis" --body-file /tmp/evobyte-p158-pr.md
```
