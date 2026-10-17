# P111 — Confirmação cega multiproblema com controle estatístico rigoroso FWER (Bonferroni-Holm)

**Status:** In review.
**Dependência:** P110 concluída; branch a partir de `codex/p110-pillai-exponential-diophantine`.
**Owner:** agente executor; revisor estatístico/matemático nos gates indicados.
**Pré-requisito:** P110 concluída com crivos algébricos e lemas de Baker; partição cega de 100 instâncias selada e intocada.
**Branch:** `codex/p111-multiproblem-blind-confirmation`.

## Hipótese, objetivo e escopo

Submeter o motor unificado de busca e prova formal a uma partição cega selada de 100 instâncias de grande porte sorteadas do catálogo de problemas abertos (Erdős-Graham, Pillai, Schinzel, Giuga), avaliando superioridade de resolução frente a baselines tradicionais sob controle estrito de taxa de erro familiar (FWER) via ajuste de Bonferroni-Holm ($\alpha = 0{,}01$).

Alterações permitidas: `src/evobyte/statistical.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p111-config.json`, `experiments/p111-run.sh`.
Fora do escopo: vazamento de instâncias de teste para os crivos de desenvolvimento; afrouxamento do $\alpha$ ou teste unilateral sem pré-registro.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-descoberta-formal-em-problemas-abertos-e-teoria-de-modelos-guiada-por-provas-em-lean-4-p105p112).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar gerador de partição cega selada multiproblema com verificação de não-vazamento em `src/evobyte/statistical.py`.
2. Executar protocolo de confirmação cega frente a baselines pareados sob Bonferroni-Holm ($\alpha = 0{,}01$).
3. Adicionar interface de auditoria P111 em `benchmarks/science_matrix.py` (`run_p111_multiproblem_confirmation_audit`).

## Gate de saída

Confirmação estatística cega com controle FWER atingido e auditoria P111 aprovada:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P111 --config experiments/p111-config.json --output /tmp/evobyte-p111-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p111 multiproblem blind confirmation"
git push -u origin HEAD
gh pr create --base codex/p110-pillai-exponential-diophantine --title "feat(formal): implement p111 multiproblem blind confirmation" --body-file /tmp/evobyte-p111-pr.md
```
