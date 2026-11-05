# P121 — Banco formal de grafos extremais, Mantel-Turán e invariantes de Ramsey em Lean 4

**Status:** In review.
**Dependência:** P120 concluída; branch a partir de `codex/p121-p128-extremal-graph-ramsey-program`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P120 concluída com campanha formal de combinatória aditiva e consolidação documental sob D032.
**Branch:** `codex/p121-extremal-graph-ramsey-formal-database`.

## Hipótese, objetivo e escopo

Formalizar no Lean 4 o arcabouço tipado dependente de teoria extremal de grafos e invariantes de Ramsey (`lean_proofs/Generated/ExtremalGraphRamseySignatures.lean`), definindo com rigor matemático o lema do aperto de mãos ($\sum_{v \in V} d(v) = 2|E|$), os grafos multipartidos completos de Turán $T(n, r)$, o teorema de Mantel ($\text{ex}(n, K_3) = \lfloor n^2 / 4 \rfloor$), a cota extremal de Turán ($\text{ex}(n, K_{r+1}) \le \frac{r-1}{2r} n^2$) e a recorrência binomial de Erdős–Szekeres para números de Ramsey $R(s, t) \le \binom{s+t-2}{s-1}$.

Alterações permitidas: `lean_proofs/`, `src/evobyte/graph_ramsey.py`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p121-config.json`, `experiments/p121-run.sh`.
Fora do escopo: download de pacotes externos; alteração de axiomas do kernel Lean 4; alegações de solução de conjecturas universais sem certificados formais.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-teoria-extremal-de-grafos-números-de-ramsey-e-progressões-aritméticas-em-lean-4-p121p128).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar definições, predicados e teoremas elementares de grafos extremais, Mantel–Turán e Erdős–Szekeres em `lean_proofs/Generated/ExtremalGraphRamseySignatures.lean`.
2. Adicionar módulo `src/evobyte/graph_ramsey.py` com algoritmos determinísticos para grafos de Turán $T(n, r)$, verificação de cliques $K_k$, número de independência $\alpha(G)$ e certificados de Mantel–Turán.
3. Adicionar interface de auditoria P121 em `benchmarks/science_matrix.py` (`run_p121_extremal_graph_ramsey_baseline_audit`) com compilação hermética sem `sorry`.

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry` e auditoria P121 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P121 --config experiments/p121-config.json --output /tmp/evobyte-p121-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p121 extremal graph ramsey formal database"
git push -u origin HEAD
gh pr create --base codex/p121-p128-extremal-graph-ramsey-program --title "feat(formal): implement p121 extremal graph ramsey formal database" --body-file /tmp/evobyte-p121-pr.md
```
