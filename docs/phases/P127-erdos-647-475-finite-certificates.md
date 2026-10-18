# P127 — Alvos finitos abertos erdos-647 (m + tau(m) <= n + 2) e erdos-475 (somas parciais distintas em F_p)

**Status:** Proposed.
**Dependência:** P126 concluída; branch a partir de `codex/p126-erdos-287-unit-fraction-max-gap`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P126 concluída; entradas `erdos-647` (`verifiable`, prêmio £25) e `erdos-475` (`decidable`, *"Resolved up to a finite check"*) em `docs/research/open-problems.json`.
**Branch:** `codex/p127-erdos-647-475-finite-certificates`.

## Hipótese, objetivo e escopo

Atacar dois problemas abertos finitamente decidíveis/verificáveis do catálogo `docs/research/open-problems.json`:
1. **`erdos-647` (Prêmio £25, `verifiable`):** *"Let $\tau(n)$ count the number of divisors of $n$. Is there some $n > 24$ such that $\max_{m < n}(m + \tau(m)) \le n + 2$?"*
   - Nota estrutural: Para que $\max_{m < n}(m + \tau(m)) \le n + 2$, é necessário que $\tau(n - 1) \le 3$, $\tau(n - 2) \le 4$, $\tau(n - 3) \le 5$, $\dots$, $\tau(n - k) \le k + 2$ simultaneamente para todo $1 \le k < n$. Em particular, $n - 1$ deve ser primo ou quadrado de primo ($\tau(n-1) \le 3$), $n - 2$ deve ser primo, semiprimo livre de quadrados ou cubo de primo ($\tau(n-2) \le 4$), e múltiplos próximos de 6, 12, 24 geram obstruções locais imediatas ($\tau(m) > n - m + 2$).
   - Objetivo: Provar formalmente em Lean 4 os lemas de obstrução local de divisores que eliminam classes inteiras de congruência para $n > 24$, executar busca vetorizada rápida para estender o horizonte verificado $N_{\max}$ e certificar em Lean 4 a ausência de soluções em janelas seladas (ou o certificado de $n > 24$ caso exista).
2. **`erdos-475` (Conjectura de Graham em $\mathbb{F}_p$, `decidable` — *"Resolved up to a finite check"*):** *"Let $p$ be a prime. Given any finite set $A \subseteq \mathbb{F}_p \setminus \{0\}$, is there always a rearrangement $A = \{a_1, \dots, a_t\}$ such that all partial sums $\sum_{1 \le k \le m} a_k$ are distinct, for all $1 \le m \le t$?"*
   - Objetivo: Formalizar o predicado `HasDistinctPartialSumsModP` em Lean 4 (`lean_proofs/Generated/Erdos647And475Certificates.lean`) e usar busca guiada (MCTS / backtracking exato) para construir e certificar no kernel do Lean 4 permutações válidas para famílias críticas de subconjuntos $A \subseteq \mathbb{F}_p \setminus \{0\}$ nos primos finitos do regime decidível.

Alterações permitidas: `lean_proofs/`, `src/evobyte/open_problems.py`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p127-config.json`, `experiments/p127-run.sh`.
Fora do escopo: alegar prova assintótica não formalizada; uso de `sorry`.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-teoremas-estruturais-em--e-descoberta-em-problemas-de-domínio-finito-aberto-p121p128).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Formalizar em `lean_proofs/Generated/Erdos647And475Certificates.lean` os predicados `IsErdos647Target (n : ℕ)` e `HasDistinctPartialSumsModP (p : ℕ) (perm : List ℕ)`, provando o caso clássico $n = 24$ e os lemas de obstrução local ($\tau(n-k) > k + 2 \implies \neg \mathrm{IsErdos647Target}\; n$).
2. Implementar em `src/evobyte/open_problems.py` o crivo de janela local para `erdos-647` (`search_erdos_647_divisor_barrier`) e o sintetizador de permutações de Graham para `erdos-475` (`solve_erdos_475_partial_sums`).
3. Compilar os certificados e teoremas de obstrução em `Erdos647And475Certificates.lean` e adicionar a auditoria P127 em `benchmarks/science_matrix.py` (`run_p127_erdos_647_475_audit`).

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry`, teoremas de obstrução para `erdos-647` e certificados de permutação para `erdos-475` verificados, e auditoria P127 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P127 --config experiments/p127-config.json --output /tmp/evobyte-p127-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p127 erdos 647 and 475 finite certificates"
git push -u origin HEAD
gh pr create --base codex/p126-erdos-287-unit-fraction-max-gap --title "feat(formal): implement p127 erdos 647 and 475 finite certificates" --body-file /tmp/evobyte-p127-pr.md
```
