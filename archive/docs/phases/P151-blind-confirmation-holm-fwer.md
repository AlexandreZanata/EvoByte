# P151 — Confirmação cega em partição selada sob controle estatístico Holm FWER

**Status:** Proposed.
**Dependência:** P150 concluída; branch a partir de `codex/p150-world-literature-novelty-dual-audit`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P150 concluída com auditoria de novidade e checadores duais aprovados.
**Branch:** `codex/p151-blind-confirmation-holm-fwer`.

## Hipótese, objetivo e escopo

Validar a superioridade e solidez das identidades sintetizadas e do crivo de alta ordem sobre uma partição cega selada de 100 instâncias residuais resistentes ($M \in \{840, 2520, 5040\}$ e numeradores $a \in \{5, 6, 7\}$) contra baselines ingênuos de força bruta. Controlar rigorosamente a taxa de erro familiar (FWER) sob o procedimento step-down de Bonferroni–Holm em $\alpha = 0.01$. Exigir taxa de sucesso de 100% nas instâncias cobertas pelas identidades, com rejeição estatisticamente significativa da hipótese nula de equivalência com busca aleatória ($p < 10^{-5}$).

Alterações permitidas: `experiments/p151-blind-split.json`, `src/evobyte/statistical.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p151-config.json`, `experiments/p151-run.sh`.
Fora do escopo: alteração a posteriori da partição cega selada; flexibilização do nível alfa.

Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Gerar partição cega imutável selada com 100 instâncias resistentes em `experiments/p151-blind-split.json`.
2. Executar protocolo de confirmação cega comparando o motor construtivo contra busca não estruturada sob orçamentos idênticos.
3. Avaliar significância estatística via teste dos sinais e ajuste de Bonferroni–Holm em `src/evobyte/statistical.py`.
4. Adicionar interface de auditoria P151 em `benchmarks/science_matrix.py` (`run_p151_blind_confirmation_audit`).

## Gate de saída

Confirmação estatística cega com $p_{\text{Holm}} \le 0.01$ e zero falhas em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P151 --config experiments/p151-config.json --output /tmp/evobyte-p151-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(statistical): implement p151 blind confirmation holm fwer"
git push -u origin HEAD
gh pr create --base codex/p150-world-literature-novelty-dual-audit --title "feat(statistical): implement p151 blind confirmation holm fwer" --body-file /tmp/evobyte-p151-pr.md
```
