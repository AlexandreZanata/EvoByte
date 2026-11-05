# P106 — Motor de grafos de obstruções e espaços negativos de busca diofantina

**Status:** Done.
**Dependência:** P105 concluída; branch a partir de `codex/p105-open-problems-formal-database`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P105 concluída com assinaturas formais de problemas abertos compiladas no Lean 4.
**Branch:** `codex/p106-obstruction-graphs-data-engine`.

## Hipótese, objetivo e escopo

Construir motor de dados e grafos relacionais que indexa espaços negativos de busca (classes de impossibilidade modular, não-resíduos quadráticos múltiplos e obstruções de paridade), provando lemas formais de poda e incompatibilidade no kernel do Lean 4 em `lean_proofs/Generated/ObstructionGraphTheorems.lean`.

Alterações permitidas: `lean_proofs/`, `src/evobyte/formal_bridge.py`, `src/evobyte/algebraic.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p106-config.json`, `experiments/p106-run.sh`.
Fora do escopo: busca aleatória não guiada; remoção de verificadores de nulidade; enfraquecimento de provas formais.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-descoberta-formal-em-problemas-abertos-e-teoria-de-modelos-guiada-por-provas-em-lean-4-p105p112).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar formalização de lemas de obstrução modular e grafos de poda relacional em `lean_proofs/Generated/ObstructionGraphTheorems.lean`.
2. Adicionar motor de grafos de obstruções diofantinas em `src/evobyte/algebraic.py`.
3. Adicionar interface de auditoria P106 em `benchmarks/science_matrix.py` (`run_p106_obstruction_graphs_audit`) com validação de compilação sem `sorry`.

## Gate de saída

Execução limpa de compilação dos teoremas de obstrução no Lean 4 com 0 `sorry` e interface de aceitação P106:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P106 --config experiments/p106-config.json --output /tmp/evobyte-p106-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p106 obstruction graphs data engine"
git push -u origin HEAD
gh pr create --base codex/p105-open-problems-formal-database --title "feat(formal): implement p106 obstruction graphs data engine" --body-file /tmp/evobyte-p106-pr.md
```
