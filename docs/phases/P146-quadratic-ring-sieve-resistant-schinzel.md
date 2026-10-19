# P146 — Crivo diofantino acelerado em anéis quadráticos para classes resistentes de Schinzel

**Status:** Proposed.
**Dependência:** P145 concluída; branch a partir de `codex/p145-schinzel-high-moduli-congruence-database`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P145 concluída com catálogo formal de resíduos resistentes de alta ordem aprovado.
**Branch:** `codex/p146-quadratic-ring-sieve-resistant-schinzel`.

## Hipótese, objetivo e escopo

Implementar um crivo diofantino acelerado baseado em fatoração em anéis de inteiros quadráticos $\mathbb{Z}[\sqrt{d}]$ e anéis de quatérnios de Hurwitz $\mathbb{H}$ para desobstrução de classes resistentes de Schinzel ($a \in \{5, 6, 7\}$) que resistem ao crivo linear padrão sobre $(axy - n(x+y)) \mid n^2$. Provar no Lean 4 (`lean_proofs/Generated/SchinzelQuadraticRingSieveTheorems.lean`) lemas de divisibilidade de normas algébricas $\mathcal{N}(u + v\sqrt{d})$ garantindo que ramos de busca com discriminantes sem quadrados possam ser podados antecipadamente sem perda de soluções.

Alterações permitidas: `lean_proofs/`, `src/evobyte/algebraic.py`, `src/evobyte/quaternion_sieve.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p146-config.json`, `experiments/p146-run.sh`.
Fora do escopo: alegações de resolução completa de classes infinitas não certificadas; axiomas não clássicos.

Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Formalizar no Lean 4 os teoremas de crivo de normas em anéis quadráticos $\mathbb{Z}[\sqrt{d}]$ associados à hiper-superfície $a x y z = n(y z + x z + x y)$ em `lean_proofs/Generated/SchinzelQuadraticRingSieveTheorems.lean`.
2. Implementar em `src/evobyte/algebraic.py` o gerador de candidatos com crivo de divisores quadráticos otimizado em C/Python vetorial para $M \ge 840$.
3. Adicionar interface de auditoria P146 em `benchmarks/science_matrix.py` (`run_p146_schinzel_quadratic_sieve_audit`).

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry` e auditoria P146 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P146 --config experiments/p146-config.json --output /tmp/evobyte-p146-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p146 quadratic ring sieve resistant schinzel"
git push -u origin HEAD
gh pr create --base codex/p145-schinzel-high-moduli-congruence-database --title "feat(formal): implement p146 quadratic ring sieve resistant schinzel" --body-file /tmp/evobyte-p146-pr.md
```
