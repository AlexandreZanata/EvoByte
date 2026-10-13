# P82 — Síntese automática de lemas de divisibilidade diofantina

**Status:** Proposed.
**Dependência:** P81 Proposed; branch a partir de `codex/p81-inductive-proof-baseline`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P81 concluída com baseline indutivo verificado no kernel Lean 4.
**Branch:** `codex/p82-divisibility-lemma-synthesis`.

## Hipótese, objetivo e escopo

Sintetizar e certificar formalmente lemas de divisibilidade exata em $\mathbb{N}$ e $\mathbb{Z}$ para denominadores diofantinos da equação $a/n = 1/x + 1/y + 1/z$, provando formalmente que $n(x+y) \equiv 0 \pmod{4xy - n(x+y)}$ sob hipóteses explícitas de congruência.

Alterações permitidas: `src/evobyte/algebraic.py`, `src/evobyte/formal_bridge.py`, `lean_proofs/Generated/`, `benchmarks/science_matrix.py`, testes e configurações em `experiments/`.
Fora do escopo: alegações de resolução universal de conjecturas abertas; táticas ad hoc não reprodutíveis.

## Trabalho ordenado

1. Implementar sintetizador de lemas de divisibilidade inteira para classes de congruência parametrizadas.
2. Gerar arquivo Lean 4 (`DivisibilityLemmas.lean`) contendo lemas de divisibilidade demonstrados por `omega` e `ring`.
3. Validar compilação hermética com zero `sorry` via Lake e auditoria P82 no `science_matrix.py`.

## Gate de saída

Compilação integral de lemas de divisibilidade em Lean 4 sem `sorry` e relatório de auditoria aceito:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P82 --config experiments/p82-config.json --output /tmp/evobyte-p82-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p82 divisibility lemma synthesis"
git push -u origin HEAD
gh pr create --base codex/p81-inductive-proof-baseline --title "feat(formal): implement p82 divisibility lemma synthesis" --body-file /tmp/evobyte-p82-pr.md
```
