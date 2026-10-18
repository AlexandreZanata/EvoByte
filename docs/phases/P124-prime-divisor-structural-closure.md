# P124 — Fechamento estrutural multiparamétrico em N por divisores em classes de desobstrução

**Status:** Proposed.
**Dependência:** P123 concluída; branch a partir de `codex/p123-quadratic-residue-polynomial-obstruction`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P123 concluída com a obstrução de 1 parâmetro formalizada no Lean 4.
**Branch:** `codex/p124-prime-divisor-structural-closure`.

## Hipótese, objetivo e escopo

Superar a barreira de 1 parâmetro de P123 provando em `lean_proofs/Generated/PrimeDivisorClosureTheorems.lean` teoremas estruturais universais de **2 parâmetros** $(k, m) \in \mathbb{N}^2$ sobre números naturais positivos $\mathbb{N}^+$. Demonstrar formalmente no Lean 4 que se um inteiro $n$ na classe resistente $n \equiv 1 \pmod{24}$ (ou $n \equiv r^2 \pmod{840}$) admite uma fatoração $n = d \cdot q$ ou um deslocamento $4x - n = d$ onde $d \equiv 3 \pmod 4$ (ou $d \equiv -1 \pmod{4ab}$), então existem polinômios explícitos $X(k, m), Y(k, m), Z(k, m) \in \mathbb{N}^+$ tais que `IsUnitFractionSol 4 n (X k m) (Y k m) (Z k m)` é verdadeiro para todo $(k, m) \in \mathbb{N}^2$.

Alterações permitidas: `lean_proofs/`, `src/evobyte/algebraic.py`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p124-config.json`, `experiments/p124-run.sh`.
Fora do escopo: certificados pontuais finitos; identidades que não concluam `IsUnitFractionSol` em $\mathbb{N}$; uso de `sorry`.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-teoremas-estruturais-em--e-descoberta-em-problemas-de-domínio-finito-aberto-p121p128).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Sintetizar e provar em `lean_proofs/Generated/PrimeDivisorClosureTheorems.lean` o teorema geral de fechamento por divisor `divisor_mod4_r3_unit_fraction_sol`: se $n = (4k + 3) \cdot m$ (inclusive quando $(4k+3) \cdot m \equiv 1 \pmod{24}$, p.ex. $4k+3 \equiv 7, 11, 19, 23 \pmod{24}$ e $m \equiv 4k+3 \pmod{24}$), então $\exists x, y, z \in \mathbb{N},\; \mathrm{IsUnitFractionSol}\; 4\; n\; x\; y\; z$.
2. Provar em $\mathbb{N}$ teoremas de fechamento de 2 parâmetros para famílias quadráticas $n(k, m)$ dentro dos 6 resíduos resistentes módulo 840 ($1, 121, 169, 289, 361, 529$), conectando-os diretamente a `IsUnitFractionSol`.
3. Adicionar interface de auditoria P124 em `benchmarks/science_matrix.py` (`run_p124_prime_divisor_closure_audit`).

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry`, teoremas de 2 parâmetros provando `IsUnitFractionSol` nas classes resistentes e auditoria P124 aceita em árvore limpa:

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
git commit -m "feat(formal): implement p124 prime divisor structural closure"
git push -u origin HEAD
gh pr create --base codex/p123-quadratic-residue-polynomial-obstruction --title "feat(formal): implement p124 prime divisor structural closure" --body-file /tmp/evobyte-p124-pr.md
```
