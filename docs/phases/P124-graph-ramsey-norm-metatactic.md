# P124 — Meta-tática customizada graph_ramsey_norm e automação combinatória em Lean 4

**Status:** In review.
**Dependência:** P123 concluída; branch a partir de `codex/p123-zarankiewicz-kovari-sos-turan`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P123 concluída com teoremas de Zarankiewicz e Kővári–Sós–Turán provados em Lean 4.
**Branch:** `codex/p124-graph-ramsey-norm-metatactic`.

## Hipótese, objetivo e escopo

Desenvolver as meta-táticas customizadas `graph_ramsey_norm` e `graph_ramsey_intro` em Lean 4 para automatizar identidades de contagem dupla em grafos ($\sum d(v) = 2|E|$, complemento $|E(G)| + |E(\overline{G})| = \binom{n}{2}$), desigualdades quadráticas de graus ($\sum d(v)^2 \ge 4|E|^2 / n$), relações de Turán e identidades de Goodman para contagem de triângulos monocromáticos em 2-colorações de $K_n$, gerando `lean_proofs/Generated/GraphRamseyTacticTheorems.lean`.

Alterações permitidas: `lean_proofs/`, `src/evobyte/graph_ramsey.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p124-config.json`, `experiments/p124-run.sh`.
Fora do escopo: meta-táticas que introduzam axiomas não verificados ou `sorry`.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-teoria-extremal-de-grafos-números-de-ramsey-e-progressões-aritméticas-em-lean-4-p121p128).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Definir a sintaxe e regras de macro das meta-táticas `graph_ramsey_norm` e `graph_ramsey_intro` em `lean_proofs/Generated/GraphRamseyTacticTheorems.lean`.
2. Implementar verificação algébrica de leis de grafos (aperto de mãos, complemento, fórmula de Goodman para triângulos monocromáticos) em `src/evobyte/graph_ramsey.py` e provar mais de 60 teoremas via `graph_ramsey_norm` sem `sorry`.
3. Adicionar interface de auditoria P124 em `benchmarks/science_matrix.py` (`run_p124_graph_ramsey_norm_audit`).

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry` e auditoria P124 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P124 --config experiments/p124-config.json --output /tmp/evobyte-p124-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p124 graph ramsey norm metatactic"
git push -u origin HEAD
gh pr create --base codex/p123-zarankiewicz-kovari-sos-turan --title "feat(formal): implement p124 graph ramsey norm metatactic" --body-file /tmp/evobyte-p124-pr.md
```
