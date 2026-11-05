# P90 — Formalização unificada da conjectura de Schinzel (a/n)

**Status:** Done.
**Dependência:** P89 Proposed; branch a partir de `codex/p89-custom-tactic-metaprogramming`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P89 concluída com tática customizada compilada no Lean 4.
**Branch:** `codex/p90-schinzel-generalized-numerator`.

## Hipótese, objetivo e escopo

Formalizar identidades paramétricas e certificados exatos da conjectura generalizada de Schinzel ($\frac{a}{n} = \frac{1}{x} + \frac{1}{y} + \frac{1}{z}$) para numeradores arbitrários $a \in \{4, 5, 6, 7, 8\}$ no kernel do Lean 4 com 0 `sorry`.

Alterações permitidas: `lean_proofs/`, `src/evobyte/algebraic.py`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p90-config.json`, `experiments/p90-run.sh`.
Fora do escopo: alegação de prova universal da conjectura de Schinzel para todo $n \in \mathbb{N}$; enfraquecimento de gates.

## Trabalho ordenado

1. Implementar gerador paramétrico de identidades de Schinzel para numeradores arbitrários $a \ge 4$ em `src/evobyte/algebraic.py`.
2. Compilar catálogo formal de teoremas de Schinzel em Lean 4 via `export_schinzel_theorems_catalog`.
3. Adicionar auditoria P90 em `benchmarks/science_matrix.py` (`run_p90_schinzel_generalization_audit`).

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry` e auditoria P90 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P90 --config experiments/p90-config.json --output /tmp/evobyte-p90-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p90 schinzel generalized numerator"
git push -u origin HEAD
gh pr create --base codex/p89-custom-tactic-metaprogramming --title "feat(formal): implement p90 schinzel generalized numerator" --body-file /tmp/evobyte-p90-pr.md
```
