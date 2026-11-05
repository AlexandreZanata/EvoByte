# P156 — Avaliação de generalização em splits ocultos e extrapolação estrita sem vazamento

**Status:** Proposed.
**Dependência:** P155 concluída; branch a partir de `codex/p155-honest-baselines-gp-pysr-execution`.
**Owner:** agente executor; revisor formal/sistemas nos gates indicados.
**Pré-requisito:** P154 e P155 concluídas com dados de treino gerados.
**Branch:** `codex/p156-generalization-hidden-extrapolation-audit`.

## Hipótese, objetivo e escopo

Avaliar os programas vencedores gerados pelo EvoByte e pelos baselines nos splits estritos de generalização: (1) split oculto in-domain ($X_{\text{hidden}} \subset [a, b]$); e (2) split de extrapolação out-of-domain ($X_{\text{extrap}} \subset [b, 2b]$). Auditar contra qualquer forma de memorização, overfitting ou constantes infladas ($|c| > 10^6$). Verificar se as expressões compactas descobertas em bytecode generalizam melhor do que árvores GP super-parametrizadas (bloat).

Alterações permitidas: `benchmarks/evaluate_generalization.py`, `experiments/p156-generalization/`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p156-config.json`, `experiments/p156-run.sh`.
Fora do escopo: acesso aos splits de teste durante a busca/treino; afrouxamento dos critérios de extrapolação.

Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar protocolo de avaliação cega em splits ocultos e de extrapolação em `benchmarks/evaluate_generalization.py`.
2. Computar métricas de teste ($R^2_{\text{hidden}}$, $R^2_{\text{extrap}}$, MSE, taxa de explosão assintótica) para todas as soluções de P154 e P155.
3. Verificar conformidade com o Critério 4 de H1 (Generalização) e ausência de degenerescência.
4. Adicionar interface de auditoria P156 em `benchmarks/science_matrix.py` (`run_p156_generalization_audit`).

## Gate de saída

Avaliação completa de generalização sem vazamentos e auditoria P156 aceita:

```bash
git diff --check
git status --short
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P156 --config experiments/p156-config.json --output /tmp/evobyte-p156-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(benchmark): implement p156 generalization hidden extrapolation audit"
git push -u origin HEAD
gh pr create --base codex/p155-honest-baselines-gp-pysr-execution --title "feat(benchmark): implement p156 generalization hidden extrapolation audit" --body-file /tmp/evobyte-p156-pr.md
```
