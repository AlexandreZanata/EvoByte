# P114 — Algoritmo de busca estruturada de conjuntos de Sidon extremais e B_2[1]

**Status:** Done (2026-10-18; busca extremal de conjuntos de Sidon B_2[1] com Bose–Chowla, Singer, Ruzsa e branch-and-bound, 70 teoremas sem sorry em SidonSetsTheorems.lean, PR #150; lake build e pytest verdes).
**Dependência:** P113 concluída; branch a partir de `codex/p113-additive-combinatorics-formal-database`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P113 concluída com tipagem de assinaturas de combinatória aditiva no Lean 4.
**Branch:** `codex/p114-sidon-sets-extremal-search`.

## Hipótese, objetivo e escopo

Desenvolver algoritmo de busca estruturada e construções combinatórias (Singer, Bose–Chowla, Ruzsa) para sintetizar conjuntos finitos de Sidon $B_2[1] \subset \{1, \dots, N\}$ com cardinalidade extremal $|A| \sim \sqrt{N}$, provando formalmente no kernel do Lean 4 em `lean_proofs/Generated/SidonSetsTheorems.lean` a propriedade de não colisão de diferenças ($a_1 - a_2 = a_3 - a_4 \implies (a_1 = a_3 \land a_2 = a_4)$) e limitantes superiores de densidade de Erdős–Turán.

Alterações permitidas: `lean_proofs/`, `src/evobyte/additive.py`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p114-config.json`, `experiments/p114-run.sh`.
Fora do escopo: uso de axiomas não padrão; alegações de cotas assintóticas universais sem demonstração mecânica no Lean 4.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-combinatória-aditiva-conjuntos-de-sidon-e-teoria-de-densidade-em-lean-4-p113p120).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar gerador e verificador determinístico de conjuntos de Sidon extremais em `src/evobyte/additive.py`.
2. Provar lemas e propriedades de conjuntos de Sidon em `lean_proofs/Generated/SidonSetsTheorems.lean` no kernel do Lean 4.
3. Adicionar interface de auditoria P114 em `benchmarks/science_matrix.py` (`run_p114_sidon_sets_audit`) com validação de compilação sem `sorry`.

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry` e auditoria P114 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P114 --config experiments/p114-config.json --output /tmp/evobyte-p114-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p114 sidon sets extremal search"
git push -u origin HEAD
gh pr create --base codex/p113-additive-combinatorics-formal-database --title "feat(formal): implement p114 sidon sets extremal search" --body-file /tmp/evobyte-p114-pr.md
```
