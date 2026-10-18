# P122 — Grafos de Paley e construções algébricas de cotas inferiores de Ramsey R(s,t)

**Status:** In review.
**Dependência:** P121 concluída; branch a partir de `codex/p121-extremal-graph-ramsey-formal-database`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P121 concluída com assinaturas de grafos extremais e Mantel–Turán provadas em Lean 4.
**Branch:** `codex/p122-paley-graphs-ramsey-constructions`.

## Hipótese, objetivo e escopo

Implementar construções algébricas de grafos de Paley $P(q)$ sobre resíduos quadráticos em $\mathbb{F}_q$ ($q \equiv 1 \pmod 4$ primo) e grafos circulantes simétricos para certificar cotas inferiores exatas de números de Ramsey $R(s, t) > n$ (como $R(3, 3) = 6$ via $P(5) = C_5$, $R(4, 4) = 18$ via $P(17)$) e regularidade fortemente regular $\text{srg}(q, \frac{q-1}{2}, \frac{q-5}{4}, \frac{q-1}{4})$, gerando teoremas formais em `lean_proofs/Generated/RamseyPaleyTheorems.lean`.

Alterações permitidas: `lean_proofs/`, `src/evobyte/graph_ramsey.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p122-config.json`, `experiments/p122-run.sh`.
Fora do escopo: alegações assintóticas não provadas sobre números de Ramsey diagonais; uso de `sorry`.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-teoria-extremal-de-grafos-números-de-ramsey-e-progressões-aritméticas-em-lean-4-p121p128).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar construção de grafos de Paley $P(q)$, verificação de parâmetros fortemente regulares $(q, k, \lambda, \mu)$ e certificação de ausência de $K_s$ e $\overline{K}_t$ em `src/evobyte/graph_ramsey.py`.
2. Exportar mais de 60 teoremas formais em `lean_proofs/Generated/RamseyPaleyTheorems.lean` com zero `sorry`.
3. Adicionar interface de auditoria P122 em `benchmarks/science_matrix.py` (`run_p122_paley_ramsey_audit`).

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry` e auditoria P122 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P122 --config experiments/p122-config.json --output /tmp/evobyte-p122-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p122 paley graphs ramsey constructions"
git push -u origin HEAD
gh pr create --base codex/p121-extremal-graph-ramsey-formal-database --title "feat(formal): implement p122 paley graphs ramsey constructions" --body-file /tmp/evobyte-p122-pr.md
```
