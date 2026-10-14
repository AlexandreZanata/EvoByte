# P91 — Crivo algébrico em anéis quadráticos para classes resistentes

**Status:** Proposed.
**Dependência:** P90 Proposed; branch a partir de `codex/p90-schinzel-generalized-numerator`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P90 concluída com formalização de Schinzel unificada.
**Branch:** `codex/p91-quadratic-ring-sieve`.

## Hipótese, objetivo e escopo

Desenvolver crivo algébrico baseado em anéis de inteiros quadráticos $\mathbb{Z}[\sqrt{d}]$ e fatoração de normas para desobstruir as classes residuais resistentes módulo 840 ($n \equiv 1, 121, 169, 289, 361, 529 \pmod{840}$).

Alterações permitidas: `lean_proofs/`, `src/evobyte/algebraic.py`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p91-config.json`, `experiments/p91-run.sh`.
Fora do escopo: alteração post hoc de instâncias; omissão de classes não resolvidas.

## Trabalho ordenado

1. Implementar crivo de fatoração de normas quadráticas em `src/evobyte/algebraic.py`.
2. Formalizar no Lean 4 identidades quadráticas cobrindo os resíduos resistentes mod 840.
3. Adicionar auditoria P91 em `benchmarks/science_matrix.py` (`run_p91_quadratic_ring_audit`).

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry` e auditoria P91 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P91 --config experiments/p91-config.json --output /tmp/evobyte-p91-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p91 quadratic ring sieve"
git push -u origin HEAD
gh pr create --base codex/p90-schinzel-generalized-numerator --title "feat(formal): implement p91 quadratic ring sieve" --body-file /tmp/evobyte-p91-pr.md
```
