# P129 — Banco formal de geometria discreta, métricas e distâncias distintas de Erdős em Lean 4

**Status:** Proposed.
**Dependência:** P128 concluída; branch a partir de `codex/p129-p136-discrete-geometry-program`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P128 concluída com grande campanha de grafos e Ramsey consolidada documentalmente sob D034.
**Branch:** `codex/p129-discrete-geometry-formal-database`.

## Hipótese, objetivo e escopo

Formalizar no Lean 4 o arcabouço tipado dependente de geometria discreta plana, métricas euclidianas e distâncias distintas de Erdős (`lean_proofs/Generated/DiscreteGeometrySignatures.lean`), definindo com rigor matemático a distância euclidiana ao quadrado $d^2(p, q) = (x_p - x_q)^2 + (y_p - y_q)^2$, o conjunto de distâncias distintas $\Delta(P) = \{ \|p - q\| : p \ne q \in P \}$, a desigualdade elementar $|\Delta(P)| \ge \sqrt{n - 3/4} - 1/2$, a não colisão métrica e as propriedades fundamentais de configurações de pontos em $\mathbb{R}^2$.

Alterações permitidas: `lean_proofs/`, `src/evobyte/discrete_geometry.py`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p129-config.json`, `experiments/p129-run.sh`.
Fora do escopo: download de pacotes externos; alteração de axiomas do kernel Lean 4; alegações de solução de conjecturas universais sem certificados formais.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-geometria-discreta-distâncias-distintas-de-erdős-e-configurações-de-pontos-em-lean-4-p129p136).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar definições, predicados e teoremas elementares de métricas euclidianas, configurações finitas de pontos e distâncias distintas em `lean_proofs/Generated/DiscreteGeometrySignatures.lean`.
2. Adicionar módulo `src/evobyte/discrete_geometry.py` com algoritmos determinísticos para cálculo exato de distâncias euclidianas ao quadrado, contagem de distâncias distintas $|\Delta(P)|$ e configurações canônicas de pontos.
3. Adicionar interface de auditoria P129 em `benchmarks/science_matrix.py` (`run_p129_discrete_geometry_baseline_audit`) com compilação hermética sem `sorry`.

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry` e auditoria P129 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P129 --config experiments/p129-config.json --output /tmp/evobyte-p129-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p129 discrete geometry formal database"
git push -u origin HEAD
gh pr create --base codex/p129-p136-discrete-geometry-program --title "feat(formal): implement p129 discrete geometry formal database" --body-file /tmp/evobyte-p129-pr.md
```
