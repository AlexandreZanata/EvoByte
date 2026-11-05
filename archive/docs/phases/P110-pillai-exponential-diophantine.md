# P110 — Alvo aberto Pillai-Catalan: formas lineares em logaritmos e crivo de expoentes diofantinos

**Status:** Done (2026-10-17; formas lineares em logaritmos e crivo de expoentes Pillai–Catalan formalizados em Lean 4 com 175 teoremas, 100% de vitórias contra crivo ingênuo, artefato experiments/p110-acceptance.json; lake build e pytest verdes).
**Dependência:** P109 concluída; branch a partir de `codex/p109-erdos-graham-unit-fractions`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P109 concluída com teoremas de frações unitárias no Lean 4.
**Branch:** `codex/p110-pillai-exponential-diophantine`.

## Hipótese, objetivo e escopo

Formalizar no kernel do Lean 4 limites analíticos de formas lineares em logaritmos (teoria de Baker) para a equação diofantina exponencial $|x^p - y^q| = c$ ($c \ge 1$, $p, q \ge 2$), provando lemas de finitude efetiva para pares fixos de bases $(x, y)$ e classes de expoentes, eliminando candidatos via crivo algébrico em `lean_proofs/Generated/PillaiCatalanTheorems.lean`.

Alterações permitidas: `lean_proofs/`, `src/evobyte/formal_bridge.py`, `src/evobyte/algebraic.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p110-config.json`, `experiments/p110-run.sh`.
Fora do escopo: alegações de resolução completa da conjectura universal de Pillai sem prova de todos os casos; enfraquecimento do kernel.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-descoberta-formal-em-problemas-abertos-e-teoria-de-modelos-guiada-por-provas-em-lean-4-p105p112).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar formalização de lemas de finitude exponencial e limites de Baker em `lean_proofs/Generated/PillaiCatalanTheorems.lean`.
2. Adicionar crivo de expoentes e resíduos diofantinos para equações de Pillai em `src/evobyte/algebraic.py`.
3. Adicionar interface de auditoria P110 em `benchmarks/science_matrix.py` (`run_p110_pillai_catalan_audit`) com validação de compilação sem `sorry`.

## Gate de saída

Execução limpa de compilação dos teoremas de Pillai-Catalan no Lean 4 com 0 `sorry` e interface de aceitação P110:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P110 --config experiments/p110-config.json --output /tmp/evobyte-p110-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p110 pillai exponential diophantine"
git push -u origin HEAD
gh pr create --base codex/p109-erdos-graham-unit-fractions --title "feat(formal): implement p110 pillai exponential diophantine" --body-file /tmp/evobyte-p110-pr.md
```
