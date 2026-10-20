# P142 — Conjuntos primitivos e conjectura de Erdős sobre séries de divisores

**Status:** Done.
**Dependência:** P141 concluída; branch a partir de `codex/p141-covering-systems-minimum-modulus-hough`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P141 concluída com teoremas de recobrimento e Hough aprovados.
**Branch:** `codex/p142-primitive-sets-divisor-series-erdos`.

## Hipótese, objetivo e escopo

Formalizar no Lean 4 a teoria de conjuntos primitivos de inteiros positivos (conjuntos onde nenhum elemento divide qualquer outro) e a conjectura clássica de Paul Erdős (1935) resolvida por Jared Duker Lichtman (2023) (`lean_proofs/Generated/PrimitiveSetsDivisorsTheorems.lean`). Provar que para qualquer conjunto primitivo $A \subset \mathbb{N} \setminus \{1\}$, a série de densidade de divisores satisfaz $\sum_{a \in A} \frac{1}{a \log a} \le \sum_{p \in \mathbb{P}} \frac{1}{p \log p} = C_{\text{prim}}$, formalizando limitantes assintóticos e cotas para subfamílias finitas com multiplicidade de fatores primos.

Alterações permitidas: `lean_proofs/`, `src/evobyte/discrepancy.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p142-config.json`, `experiments/p142-run.sh`.
Fora do escopo: alegações de resultados analíticos novos fora do escopo comprovado no kernel do Lean 4.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-teoria-de-discrepância-problema-da-discrepância-de-erdős-e-sistemas-de-recobrimento-em-lean-4-p137p144).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar definições de conjuntos primitivos, propriedades de cadeias de divisores e cotas de Lichtman–Erdős em `lean_proofs/Generated/PrimitiveSetsDivisorsTheorems.lean`.
2. Adicionar algoritmos de teste de primitividade, enumeração de famílias primitivas extremais e avaliação de somas $\sum \frac{1}{a \log a}$ em `src/evobyte/discrepancy.py`.
3. Adicionar interface de auditoria P142 em `benchmarks/science_matrix.py` (`run_p142_primitive_sets_audit`).

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry` e auditoria P142 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P142 --config experiments/p142-config.json --output /tmp/evobyte-p142-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p142 primitive sets divisor series erdos"
git push -u origin HEAD
gh pr create --base codex/p141-covering-systems-minimum-modulus-hough --title "feat(formal): implement p142 primitive sets divisor series erdos" --body-file /tmp/evobyte-p142-pr.md
```
