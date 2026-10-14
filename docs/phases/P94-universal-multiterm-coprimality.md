# P94 — Generalização multitermo universal e coprimalidade total

**Status:** Proposed.
**Dependência:** P93 Proposed; branch a partir de `codex/p93-asymptotic-density-coverage`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P93 concluída com densidade assintótica comprovada.
**Branch:** `codex/p94-universal-multiterm-coprimality`.

## Hipótese, objetivo e escopo

Formalizar decomposições unitárias diofantinas com $k \ge 5$ termos unitários coprimos em pares ($\gcd(x_i, x_j) = 1$ para todo $i \ne j$) para frações $\frac{a}{n}$ no Lean 4 com 0 `sorry`, estendendo a infraestrutura para expansões multitermo arbitrárias.

Alterações permitidas: `lean_proofs/`, `src/evobyte/algebraic.py`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p94-config.json`, `experiments/p94-run.sh`.
Fora do escopo: enfraquecimento da exigência de coprimalidade aos pares; supressão de restrições de positividade em $\mathbb{N}$.

## Trabalho ordenado

1. Implementar gerador de decomposições multitermo coprimas de ordem $k \ge 5$ em `src/evobyte/algebraic.py`.
2. Formalizar lemas de coprimalidade mútua no Lean 4 via `evobyte_solve` e despacho de táticas.
3. Adicionar auditoria P94 em `benchmarks/science_matrix.py` (`run_p94_multiterm_coprimality_audit`).

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry` e auditoria P94 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P94 --config experiments/p94-config.json --output /tmp/evobyte-p94-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p94 universal multiterm coprimality"
git push -u origin HEAD
gh pr create --base codex/p93-asymptotic-density-coverage --title "feat(formal): implement p94 universal multiterm coprimality" --body-file /tmp/evobyte-p94-pr.md
```
