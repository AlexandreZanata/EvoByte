# P125 — Alvo finito aberto erdos-307: produto unitário de somas de recíprocos de primos e obstrução p-ádica

**Status:** Proposed.
**Dependência:** P124 concluída; branch a partir de `codex/p124-prime-divisor-structural-closure`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P124 concluída; catálogo `docs/research/open-problems.json` com entrada `erdos-307` (`dataset_state: verifiable`, *"Open, but could be proved with a finite example"*).
**Branch:** `codex/p125-erdos-307-prime-reciprocal-products`.

## Hipótese, objetivo e escopo

Atacar o **Problema #307 de Erdős** (`erdos-307` em `docs/research/open-problems.json`):
> *"Are there two finite sets of primes $P, Q$ such that $1 = \left(\sum_{p \in P} \frac{1}{p}\right)\left(\sum_{q \in Q} \frac{1}{q}\right)$?"*

Este problema está aberto e é classificado na fonte primária como `verifiable` (um único par finito $(P, Q)$ resolve a conjectura afirmativamente; reciprocamente, teoremas estruturais de obstrução $p$-ádica e cotas exaustivas reduzem o espaço de busca). O escopo desta fase compreende:
1. Formalizar no Lean 4 (`lean_proofs/Generated/Erdos307PrimeReciprocals.lean`) o predicado exato `IsErdos307Solution (P Q : Finset ℕ)` (todos os elementos primos e produto das somas de recíprocos igual a $1 \in \mathbb{Q}$).
2. Provar formalmente em Lean 4 a **Obstrução $p$-ádica de Disjunção**: se $(P, Q)$ satisfaz `IsErdos307Solution P Q`, então $P \cap Q = \emptyset$, e para cada $p \in P$, o primo $p$ divide o numerador reduzido de $\sum_{q \in Q} \frac{1}{q}$ (e simetricamente para $q \in Q$).
3. Implementar o motor de busca exata guiada por grafos de divisibilidade primo-a-primo (`p | num(sum(1/q))`) e certificar em Lean 4 a inexistência exaustiva de soluções (`exhaustive-null`) até o limite de primos testado $B$ (ou certificar a solução $(P, Q)$ caso encontrada).

Alterações permitidas: `lean_proofs/`, `src/evobyte/open_problems.py`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p125-config.json`, `experiments/p125-run.sh`.
Fora do escopo: afirmar solução universal sem prova completa; confundir inexistência até $B$ com impossibilidade assintótica; uso de `sorry`.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-teoremas-estruturais-em--e-descoberta-em-problemas-de-domínio-finito-aberto-p121p128).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Formalizar `IsErdos307Solution` em `lean_proofs/Generated/Erdos307PrimeReciprocals.lean` e provar os teoremas estruturais de obstrução $p$-ádica, disjunção $P \cap Q = \emptyset$, e cotas inferiores de cardinalidade $|P| + |Q|$ baseadas nas somas parciais de $\sum 1/p$.
2. Implementar em `src/evobyte/open_problems.py` o solver exato de acoplamento de divisibilidade para `erdos-307` (`search_erdos_307_prime_reciprocals`), testando sistematicamente pares de subconjuntos de primos sob poda $p$-ádica.
3. Compilar os teoremas de exclusão exaustiva por janela finita (ou o certificado de construção) em `Erdos307PrimeReciprocals.lean` e adicionar a auditoria P125 em `benchmarks/science_matrix.py` (`run_p125_erdos_307_audit`).

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry`, teoremas estruturais e cotas exaustivas para `erdos-307` verificados e auditoria P125 aceita em árvore limpa:

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
git commit -m "feat(formal): implement p125 erdos 307 prime reciprocal products"
git push -u origin HEAD
gh pr create --base codex/p124-prime-divisor-structural-closure --title "feat(formal): implement p125 erdos 307 prime reciprocal products" --body-file /tmp/evobyte-p125-pr.md
```
