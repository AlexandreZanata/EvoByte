# P126 — Alvo finito aberto erdos-287: poda exata branch-and-bound e cotas formais para gaps <= 2 em frações unitárias

**Status:** Proposed.
**Dependência:** P125 concluída; branch a partir de `codex/p125-erdos-307-prime-reciprocal-products`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P125 concluída; catálogo `docs/research/open-problems.json` com entrada `erdos-287` (`dataset_state: falsifiable`, *"Open, but could be disproved with a finite counterexample"*).
**Branch:** `codex/p126-erdos-287-unit-fraction-max-gap`.

## Hipótese, objetivo e escopo

Atacar o **Problema #287 de Erdős** (`erdos-287` em `docs/research/open-problems.json`):
> *"Let $k \ge 2$. Is it true that, for any distinct integers $1 < n_1 < \dots < n_k$ such that $1 = \frac{1}{n_1} + \dots + \frac{1}{n_k}$ we must have $\max(n_{i+1} - n_i) \ge 3$?"*

Uma sequência de inteiros $1 < n_1 < \dots < n_k$ viola a conjectura se e somente se $\sum_{i=1}^k \frac{1}{n_i} = 1$ e todos os passos consecutivos satisfazem $n_{i+1} - n_i \in \{1, 2\}$ (além do caso contíguo conhecido ou impossível para $n_1$ grande). O objetivo desta fase é:
1. Formalizar em `lean_proofs/Generated/Erdos287GapBounds.lean` o predicado `IsErdos287Counterexample (ns : List ℕ)` (`StrictlyIncreasing`, `∀ x ∈ ns, x > 1`, `maxGap ns ≤ 2`, `unitSum ns = 1`).
2. Implementar um algoritmo exato de poda *branch-and-bound* + filtro 2-ádico/3-ádico sobre árvores binárias de passos $\Delta_i \in \{1, 2\}$ partindo de $n_1 \ge 2$.
3. Provar formalmente no kernel do Lean 4 teoremas exaustivos certificando que para todo $n_1$ e comprimento $k$ dentro do horizonte computacional verificado, nenhuma sequência com $\max(n_{i+1} - n_i) \le 2$ (exceto a decomposição trivial contígua se aplicável, ou provando $\max \ge 3$ para todo $k \ge 2$) soma $1$, estabelecendo cotas inferiores formais certificadas (ou encontrando um contraejemplo finito inédito).

Alterações permitidas: `lean_proofs/`, `src/evobyte/open_problems.py`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p126-config.json`, `experiments/p126-run.sh`.
Fora do escopo: aproximações em ponto flutuante; descartar ramos sem prova exata de cota superior/inferior em $\mathbb{Q}$; uso de `sorry`.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-teoremas-estruturais-em--e-descoberta-em-problemas-de-domínio-finito-aberto-p121p128).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Formalizar `IsErdos287Counterexample` e lemas de poda harmônica e 2-ádica em `lean_proofs/Generated/Erdos287GapBounds.lean`.
2. Implementar em `src/evobyte/open_problems.py` a busca exata *branch-and-bound* sobre árvores de passos $\Delta_i \in \{1, 2\}$ (`search_erdos_287_bounded_gaps`) com aritmética racional exata (`Fraction`) e poda por maior potência de 2.
3. Exportar a árvore de poda verificada para teoremas formais em `Erdos287GapBounds.lean` (provando $\max(n_{i+1} - n_i) \ge 3$ nas famílias certificadas e inexistência de contraejemplos até o horizonte $N_{\max}$) e adicionar a auditoria P126 em `benchmarks/science_matrix.py` (`run_p126_erdos_287_audit`).

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry`, árvore de impossibilidade/cota para `erdos-287` certificada e auditoria P126 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P126 --config experiments/p126-config.json --output /tmp/evobyte-p126-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p126 erdos 287 unit fraction max gap"
git push -u origin HEAD
gh pr create --base codex/p125-erdos-307-prime-reciprocal-products --title "feat(formal): implement p126 erdos 287 unit fraction max gap" --body-file /tmp/evobyte-p126-pr.md
```
