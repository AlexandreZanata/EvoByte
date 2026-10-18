# P127 — Confirmação cega em larga escala em grafos e Ramsey sob controle FWER (Bonferroni-Holm)

**Status:** Proposed.
**Dependência:** P126 concluída; branch a partir de `codex/p126-erdos-gyarfas-cycles-chromatic`.
**Owner:** agente executor; revisor estatístico/matemático nos gates indicados.
**Pré-requisito:** P126 concluída com teoremas de ciclos e número cromático provados; partição cega selada de 100 instâncias intocada.
**Branch:** `codex/p127-graph-ramsey-blind-confirmation`.

## Hipótese, objetivo e escopo

Validar o motor formal de grafos extremais, Ramsey, Zarankiewicz e 3-AP-free do EvoByte em partição cega selada de 100 instâncias (`experiments/p127-blind-split.json`, 25 instâncias em cada uma das 4 trilhas: `turan_paley_ramsey`, `zarankiewicz_kst`, `roth_salem_spencer`, `erdos_gyarfas_chromatic`) sob controle rigoroso de erro familiar (FWER via Bonferroni–Holm em $\alpha = 0{,}01$).

Alterações permitidas: `src/evobyte/graph_ramsey.py`, `src/evobyte/statistical.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p127-config.json`, `experiments/p127-run.sh`, `experiments/p127-blind-split.json`.
Fora do escopo: vazamento de instâncias seladas; flexibilização de $\alpha = 0{,}01$.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-teoria-extremal-de-grafos-números-de-ramsey-e-progressões-aritméticas-em-lean-4-p121p128).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Gerar e selar criptograficamente a partição cega de 100 instâncias em `experiments/p127-blind-split.json`.
2. Implementar motor de avaliação pareada e confirmação cega em `src/evobyte/statistical.py`.
3. Adicionar interface de auditoria P127 em `benchmarks/science_matrix.py` (`run_p127_graph_ramsey_blind_confirmation_audit`).

## Gate de saída

Execução da confirmação cega com 100/100 certificados aprovados, FWER controlado em $\alpha = 0{,}01$ e árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P127 --config experiments/p127-config.json --output /tmp/evobyte-p127-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p127 graph ramsey blind confirmation"
git push -u origin HEAD
gh pr create --base codex/p126-erdos-gyarfas-cycles-chromatic --title "feat(formal): implement p127 graph ramsey blind confirmation" --body-file /tmp/evobyte-p127-pr.md
```
