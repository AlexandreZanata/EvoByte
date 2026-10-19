# P143 — Confirmação cega em larga escala em discrepância e recobrimentos sob controle FWER

**Status:** Proposed.
**Dependência:** P142 concluída; branch a partir de `codex/p142-primitive-sets-divisor-series-erdos`.
**Owner:** agente executor; revisor estatístico nos gates indicados.
**Pré-requisito:** P142 concluída; integridade e isolamento de split preservados.
**Branch:** `codex/p143-discrepancy-covering-blind-confirmation`.

## Hipótese, objetivo e escopo

Avaliar empiricamente o motor de busca formal e estruturada em teoria de discrepância, EDP e sistemas de recobrimento contra baselines ingênuos sobre uma partição cega selada de 100 instâncias (`experiments/p143-blind-split.json`), com 25 instâncias em 4 trilhas independentes:
1. `erdos_discrepancy`: instâncias de prefixos de funções completamente multiplicativas e sequências de Liouville;
2. `roth_spencer_progressions`: instâncias de discrepância sobre progressões aritméticas de comprimentos variados;
3. `covering_systems`: instâncias de sistemas de congruências com módulos distintos e verificação de recobrimento;
4. `primitive_sets`: instâncias de famílias primitivas extremais e cotas parciais de séries de divisores.

A hipótese de confirmação exige vitória estatisticamente significativa do motor guiado em todas as 4 trilhas com controle estrito de erro familiar (FWER) via procedimento step-down de Bonferroni–Holm em $\alpha = 0{,}01$.

Alterações permitidas: `experiments/p143-blind-split.json`, `src/evobyte/statistical.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p143-config.json`, `experiments/p143-run.sh`.
Fora do escopo: vazamento de instâncias seladas para o crivo de desenvolvimento; alteração de dados pós-congelamento.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-teoria-de-discrepância-problema-da-discrepância-de-erdős-e-sistemas-de-recobrimento-em-lean-4-p137p144).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Gerar e selar a partição de 100 instâncias cegas em `experiments/p143-blind-split.json` com checksum SHA-256 e verificação de não vazamento (`zero_leakage_verified`).
2. Implementar a avaliação em `src/evobyte/statistical.py` (`evaluate_discrepancy_covering_blind_confirmation`) com teste de sinais pareado e ajuste de Bonferroni–Holm.
3. Adicionar interface de auditoria P143 em `benchmarks/science_matrix.py` (`run_p143_discrepancy_covering_blind_confirmation_audit`).

## Gate de saída

Controle estrito de FWER ($\max p_{\text{Holm}} \le 0{,}01$), 100% de vitórias nas 4 trilhas e auditoria P143 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P143 --config experiments/p143-config.json --output /tmp/evobyte-p143-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p143 discrepancy covering blind confirmation"
git push -u origin HEAD
gh pr create --base codex/p142-primitive-sets-divisor-series-erdos --title "feat(formal): implement p143 discrepancy covering blind confirmation" --body-file /tmp/evobyte-p143-pr.md
```
