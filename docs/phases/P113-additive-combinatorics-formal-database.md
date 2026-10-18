# P113 — Banco formal de combinatória aditiva e conjuntos de Sidon em Lean 4

**Status:** In review.
**Dependência:** P112 concluída; branch a partir de `codex/p113-p120-additive-combinatorics-program`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P112 concluída com campanha formal de problemas abertos e consolidação documental sob D030.
**Branch:** `codex/p113-additive-combinatorics-formal-database`.

## Hipótese, objetivo e escopo

Formalizar no Lean 4 o arcabouço tipado dependente de combinatória aditiva (`lean_proofs/Generated/AdditiveCombinatoricsSignatures.lean`), definindo com rigor matemático os predicados de conjuntos de Sidon $B_2[g]$ (onde cada soma $a + b$ ocorre no máximo $g$ vezes), soma de Minkowski $A + B$, diferença $A - A$, energia aditiva $E(A, B) = |\{(a_1, a_2, b_1, b_2) \in A^2 \times B^2 : a_1 + b_1 = a_2 + b_2\}|$ e conjuntos livres de soma, com separação estrita entre conjuntos públicos e partições cegas seladas.

Alterações permitidas: `lean_proofs/`, `src/evobyte/additive.py`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p113-config.json`, `experiments/p113-run.sh`.
Fora do escopo: download de pacotes externos; alteração de axiomas do kernel Lean 4; alegações de solução de conjecturas universais sem certificados formais.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-combinatória-aditiva-conjuntos-de-sidon-e-teoria-de-densidade-em-lean-4-p113p120).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar definições, predicados e teoremas elementares de combinatória aditiva em Lean 4 em `lean_proofs/Generated/AdditiveCombinatoricsSignatures.lean`.
2. Adicionar módulo de orquestração de instâncias de combinatória aditiva em `src/evobyte/additive.py` com validação de invariantes e propriedades de Sidon.
3. Adicionar interface de auditoria P113 em `benchmarks/science_matrix.py` (`run_p113_additive_combinatorics_baseline_audit`) com compilação hermética sem `sorry`.

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry` e auditoria P113 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P113 --config experiments/p113-config.json --output /tmp/evobyte-p113-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p113 additive combinatorics formal database"
git push -u origin HEAD
gh pr create --base codex/p113-p120-additive-combinatorics-program --title "feat(formal): implement p113 additive combinatorics formal database" --body-file /tmp/evobyte-p113-pr.md
```
