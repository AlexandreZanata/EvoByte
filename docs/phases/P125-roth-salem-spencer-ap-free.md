# P125 — Alvo aberto de Roth e Salem-Spencer sobre conjuntos livres de progressões de 3 termos

**Status:** Proposed.
**Dependência:** P124 concluída; branch a partir de `codex/p124-graph-ramsey-norm-metatactic`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P124 concluída com meta-tática `graph_ramsey_norm` provada em Lean 4.
**Branch:** `codex/p125-roth-salem-spencer-ap-free`.

## Hipótese, objetivo e escopo

Formalizar e buscar conjuntos extremais livres de progressões aritméticas de 3 termos ($3\text{-AP}$-free, onde $x + z = 2y \implies x = y = z$, também conhecidos como conjuntos de Stanley/Salem–Spencer), combinando a construção ternária de Salem–Spencer (inteiros cujos dígitos em base 3 pertencem a $\{0, 1\}$), a sequência gulosa de Stanley $S(0, 1)$ e busca branch-and-bound exata para $r_3(N)$ em horizontes finitos, gerando `lean_proofs/Generated/RothSalemSpencerTheorems.lean`.

Alterações permitidas: `lean_proofs/`, `src/evobyte/graph_ramsey.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p125-config.json`, `experiments/p125-run.sh`.
Fora do escopo: alegações assintóticas universais não provadas no kernel; uso de `sorry`.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-teoria-extremal-de-grafos-números-de-ramsey-e-progressões-aritméticas-em-lean-4-p121p128).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar verificação de conjuntos $3\text{-AP}$-free, construção de Salem–Spencer em base 3, sequência de Stanley e busca extremal branch-and-bound em `src/evobyte/graph_ramsey.py`.
2. Exportar mais de 60 teoremas formais em `lean_proofs/Generated/RothSalemSpencerTheorems.lean` com zero `sorry`.
3. Adicionar interface de auditoria P125 em `benchmarks/science_matrix.py` (`run_p125_roth_salem_spencer_audit`).

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry` e auditoria P125 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P125 --config experiments/p125-config.json --output /tmp/evobyte-p125-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p125 roth salem spencer ap free"
git push -u origin HEAD
gh pr create --base codex/p124-graph-ramsey-norm-metatactic --title "feat(formal): implement p125 roth salem spencer ap free" --body-file /tmp/evobyte-p125-pr.md
```
