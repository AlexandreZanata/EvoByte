# P108 — Busca em árvore Monte Carlo (MCTS) guiada pelo kernel do Lean 4 no espaço de táticas

**Status:** Done.
**Dependência:** P107 concluída; branch a partir de `codex/p107-lightweight-conditional-proposer`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P107 concluída com modelo condicional congelado; ambiente Lean 4 e Lake herméticos.
**Branch:** `codex/p108-tactic-tree-formal-mcts`.
**Resultado:** ACCEPTED — Motor FormalMCTSSearcher com feedback binário estrito acoplado ao compilador Lean 4 (lake env lean --stdin), guiado por priors do modelo neural P107, alcançando 100% de taxa de fechamento de provas (8/8 metas demonstradas) com zero tokens `sorry`.

## Hipótese, objetivo e escopo

Desenvolver motor de busca em árvore Monte Carlo (MCTS formal) para exploração sistemática do espaço de táticas Lean 4 (`omega`, `aesop`, `ring`, `linarith`, `norm_num`, `dioph_solve`, `dioph_surface`), guiado por priors do modelo condicional P107 e podas de obstrução P106, recebendo feedback binário estrito do kernel do Lean 4 (`lake build`) sem tolerar `sorry` ou atalhos heurísticos.

Alterações permitidas: `src/evobyte/mcts_formal.py`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p108-config.json`, `experiments/p108-run.sh`.
Fora do escopo: busca descontrolada em nós infinitos; enfraquecimento do kernel; uso de recompensas aproximadas sem compilação.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-descoberta-formal-em-problemas-abertos-e-teoria-de-modelos-guiada-por-provas-em-lean-4-p105p112).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar motor de busca MCTS formal em grafos de táticas em `src/evobyte/mcts_formal.py`.
2. Integrar oráculo de recompensa direta acoplado ao compilador Lean 4 em `src/evobyte/formal_bridge.py`.
3. Adicionar interface de auditoria P108 em `benchmarks/science_matrix.py` (`run_p108_formal_mcts_audit`) validando profundidade, nós explorados e taxa de fechamento de provas.

## Gate de saída

Execução limpa do motor MCTS formal com fechamento de lemas no Lean 4 e interface de aceitação P108:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P108 --config experiments/p108-config.json --output /tmp/evobyte-p108-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p108 tactic tree formal mcts"
git push -u origin HEAD
gh pr create --base codex/p107-lightweight-conditional-proposer --title "feat(formal): implement p108 tactic tree formal mcts" --body-file /tmp/evobyte-p108-pr.md
```
