# P109 — Alvo aberto Erdős-Graham: formalização e busca de frações unitárias com denominadores densos

**Status:** Done.
**Dependência:** P108 concluída; branch a partir de `codex/p108-tactic-tree-formal-mcts`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P108 concluída com motor MCTS formal ativo; ambiente Lean 4 e Lake herméticos.
**Branch:** `codex/p109-erdos-graham-unit-fractions`.
**Resultado:** ACCEPTED — 113 teoremas formais compilados no kernel do Lean 4 em `lean_proofs/Generated/ErdosGrahamTheorems.lean` com zero tokens `sorry`, 79 decomposições unitárias exatas matematicamente verificadas ($\sum_{d \in S} 1/d = 1$ em $\mathbb{Q}$) e identidades de MMC escaladas em $\mathbb{N}$.

## Hipótese, objetivo e escopo

Aplicar a metodologia unificada (banco de problemas abertos P105, grafos de obstruções P106, modelo condicional P107 e MCTS formal P108) à subconjectura de Erdős–Graham sobre decomposição unitária $\sum_{d \in S} 1/d = 1$ para subconjuntos de densidade positiva, formalizando lemas de densidade finita e certificados construtivos no kernel do Lean 4 em `lean_proofs/Generated/ErdosGrahamTheorems.lean`.

Alterações permitidas: `lean_proofs/`, `src/evobyte/formal_bridge.py`, `src/evobyte/algebraic.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p109-config.json`, `experiments/p109-run.sh`.
Fora do escopo: alegação de prova universal da conjectura plena de Erdős–Graham sem fechamento formal de todos os casos; enfraquecimento de tolerâncias.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-descoberta-formal-em-problemas-abertos-e-teoria-de-modelos-guiada-por-provas-em-lean-4-p105p112).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar formalização de lemas de densidade harmônica e somas unitárias finitas no Lean 4 em `lean_proofs/Generated/ErdosGrahamTheorems.lean`.
2. Adicionar gerador de certificados construtivos para famílias de denominadores em `src/evobyte/formal_bridge.py`.
3. Adicionar interface de auditoria P109 em `benchmarks/science_matrix.py` (`run_p109_erdos_graham_audit`) com validação de compilação sem `sorry`.

## Gate de saída

Execução limpa de compilação dos teoremas de Erdős-Graham no Lean 4 com 0 `sorry` e interface de aceitação P109:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P109 --config experiments/p109-config.json --output /tmp/evobyte-p109-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p109 erdos graham unit fractions"
git push -u origin HEAD
gh pr create --base codex/p108-tactic-tree-formal-mcts --title "feat(formal): implement p109 erdos graham unit fractions" --body-file /tmp/evobyte-p109-pr.md
```
