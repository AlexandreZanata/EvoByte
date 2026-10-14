# P103 — Confirmação cega em hiper-escala (10^9 a 10^12) sob controle FWER

**Status:** Proposed.
**Dependência:** P102 concluída; branch a partir de `codex/p97-p104-diophantine-geometry-program`.
**Owner:** agente executor; revisor estatístico/matemático nos gates indicados.
**Pré-requisito:** P102 concluída com identidades de potências superiores verificadas; ambiente de teste estritamente cego e selado.
**Branch:** `codex/p103-hyper-scale-blind-confirmation`.

## Hipótese, objetivo e escopo

Validar empiricamente o motor de resolução e crivo diofantino em 100 instâncias de hiper-escala ($10^9 \le n \le 10^{12}$) geradas com partição cega selada, aplicando controle estatístico rigoroso de Family-Wise Error Rate (FWER) via procedimento de Bonferroni-Holm com nível global $\alpha = 0{,}01$, demonstrando 100% de vitórias com significância estatística extrema e zero falsos positivos.

Alterações permitidas: `benchmarks/science_matrix.py`, `src/evobyte/formal_bridge.py`, `tests/`, `experiments/p103-config.json`, `experiments/p103-run.sh`.
Fora do escopo: ajuste a posteriori de parâmetros de busca após quebra do selo cego.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-geometria-algébrica-diofantina-fibrados-de-superfícies-cúbicas-e-invariantes-em-lean-4-p97p104).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar gerador determinístico de instâncias cegas seladas em hiper-escala ($10^9 \le n \le 10^{12}$) em `src/evobyte/formal_bridge.py`.
2. Adicionar motor de auditoria P103 com teste de Holm FWER em `benchmarks/science_matrix.py` (`run_p103_blind_confirmation_audit`).
3. Criar scripts de execução e configuração reproduzíveis em `experiments/p103-config.json` e `experiments/p103-run.sh`.

## Gate de saída

Execução do teste cego em 100 instâncias com 100% de sucesso e $p_{\text{adjusted}} < 0{,}01$:

```bash
git diff --check
git status --short
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P103 --config experiments/p103-config.json --output /tmp/evobyte-p103-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p103 hyper scale blind confirmation"
git push -u origin HEAD
gh pr create --base codex/p97-p104-diophantine-geometry-program --title "feat(formal): implement p103 hyper scale blind confirmation" --body-file /tmp/evobyte-p103-pr.md
```
