# P147 — Síntese automatizada de identidades paramétricas polinomiais para classes residuais abertas

**Status:** Done.
**Dependência:** P146 concluída; branch a partir de `codex/p146-quadratic-ring-sieve-resistant-schinzel`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P146 concluída com crivo de anéis quadráticos verificado no Lean 4.
**Branch:** `codex/p147-automated-polynomial-identity-synthesis`.

## Hipótese, objetivo e escopo

Desenvolver um motor de síntese evolutiva estruturada e interpolação racional exata em `src/evobyte/algebraic.py` que descubra novas identidades polinomiais explícitas $(X(k), Y(k), Z(k)) \in (\mathbb{Q}[k])^3$ cobrindo classes de progressões aritméticas $n(k) = M k + r$ ($M \ge 840$) para a conjectura de Schinzel ($a \in \{5, 6, 7\}$) que permaneciam sem identidades na literatura aberta. Exigir estrita positividade e integridade dos denominadores para todo $k \ge k_0$, rejeitando soluções com denominadores degenerados ou nulos.

Alterações permitidas: `docs/phases/P147-automated-polynomial-identity-synthesis.md`, `src/evobyte/algebraic.py`, `src/evobyte/evolution.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p147-config.json`, `experiments/p147-run.sh`.
Fora do escopo: aceitação de identidades heurísticas sem verificação algébrica simbólica exata em $\mathbb{Q}[k]$.

Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar sintetizador de identidades polinomiais baseado em interpolação de Newton sobre frações contínuas e busca evolutiva estruturada em `src/evobyte/algebraic.py`.
2. Adicionar validação de integridade e positividade de coordenadas em $\mathbb{N}$ com garantia de não degenerescência $X(k) < Y(k) < Z(k)$.
3. Adicionar interface de auditoria P147 em `benchmarks/science_matrix.py` (`run_p147_polynomial_identity_synthesis_audit`).

## Gate de saída

Execução com 100% dos testes verdes e síntese exata de identidades polinomiais não triviais verificadas simbolicamente:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P147 --config experiments/p147-config.json --output /tmp/evobyte-p147-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(algebraic): implement p147 automated polynomial identity synthesis"
git push -u origin HEAD
gh pr create --base codex/p146-quadratic-ring-sieve-resistant-schinzel --title "feat(algebraic): implement p147 automated polynomial identity synthesis" --body-file /tmp/evobyte-p147-pr.md
```
