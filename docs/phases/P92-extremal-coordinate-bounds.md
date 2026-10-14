# P92 — Limites extremais certificados e minimização de coordenadas

**Status:** Proposed.
**Dependência:** P91 Proposed; branch a partir de `codex/p91-quadratic-ring-sieve`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P91 concluída com crivo quadrático verificado.
**Branch:** `codex/p92-extremal-coordinate-bounds`.

## Hipótese, objetivo e escopo

Provar formalmente no Lean 4 cotas superiores rigorosas sobre o tamanho das coordenadas $\max(x, y, z) \le C n^2$ e demonstrar que o crivo estruturado atinge coordenadas estritamente subcúbicas.

Alterações permitidas: `lean_proofs/`, `src/evobyte/algebraic.py`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p92-config.json`, `experiments/p92-run.sh`.
Fora do escopo: extrapolação de cotas além dos domínios formalmente provados.

## Trabalho ordenado

1. Implementar verificação formal de desigualdades de limites de coordenadas em `src/evobyte/formal_bridge.py`.
2. Provar lemas formais no Lean 4 delimitando $\max(x, y, z)$ em função de $n$.
3. Adicionar auditoria P92 em `benchmarks/science_matrix.py` (`run_p92_extremal_bounds_audit`).

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry` e auditoria P92 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P92 --config experiments/p92-config.json --output /tmp/evobyte-p92-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p92 extremal coordinate bounds"
git push -u origin HEAD
gh pr create --base codex/p91-quadratic-ring-sieve --title "feat(formal): implement p92 extremal coordinate bounds" --body-file /tmp/evobyte-p92-pr.md
```
