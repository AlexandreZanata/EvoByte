# P138 — Problema da discrepância de Erdős (EDP) e multiplicatividade completa

**Status:** In review.
**Dependência:** P137 concluída; branch a partir de `codex/p137-discrepancy-covering-formal-database`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P137 concluída com assinaturas de discrepância e recobrimentos aprovadas no Lean 4.
**Branch:** `codex/p138-erdos-discrepancy-completely-multiplicative`.

## Hipótese, objetivo e escopo

Formalizar no Lean 4 os teoremas do Problema da Discrepância de Erdős (EDP), funções completamente multiplicativas e a estrutura do teorema histórico de Terence Tao (2016) (`lean_proofs/Generated/ErdosDiscrepancyTheorems.lean`). Provar que para qualquer função completamente multiplicativa $f: \mathbb{N} \to \{-1, +1\}$, se $f$ não simula uma função de pretensão com caráter de Dirichlet, a discrepância $\sup_{n} |\sum_{k=1}^n f(k)| = \infty$, estabelecendo limitantes para sequências de Liouville truncadas e balanceamento homogêneo de discrepância.

Alterações permitidas: `lean_proofs/`, `src/evobyte/discrepancy.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p138-config.json`, `experiments/p138-run.sh`.
Fora do escopo: alegações de novas provas analíticas do EDP fora do framework formal já estabelecido.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-teoria-de-discrepância-problema-da-discrepância-de-erdős-e-sistemas-de-recobrimento-em-lean-4-p137p144).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar teoremas de multiplicatividade completa, propriedades de sequências de Liouville e bounds de discrepância homogênea em `lean_proofs/Generated/ErdosDiscrepancyTheorems.lean`.
2. Adicionar geradores de sequências completamente multiplicativas e verificadores de discrepância do EDP em `src/evobyte/discrepancy.py`.
3. Adicionar interface de auditoria P138 em `benchmarks/science_matrix.py` (`run_p138_erdos_discrepancy_audit`).

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry` e auditoria P138 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P138 --config experiments/p138-config.json --output /tmp/evobyte-p138-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p138 erdos discrepancy completely multiplicative"
git push -u origin HEAD
gh pr create --base codex/p137-discrepancy-covering-formal-database --title "feat(formal): implement p138 erdos discrepancy completely multiplicative" --body-file /tmp/evobyte-p138-pr.md
```
