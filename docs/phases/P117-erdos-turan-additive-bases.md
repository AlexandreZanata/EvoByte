# P117 — Alvo aberto Erdős-Turán em bases aditivas e representações

**Status:** In review.
**Dependência:** P116 concluída; branch a partir de `codex/p116-additive-norm-metatactic`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P116 concluída com meta-tática `additive_norm` provada em Lean 4.
**Branch:** `codex/p117-erdos-turan-additive-bases`.

## Hipótese, objetivo e escopo

Investigar formalmente a célebre conjectura de Erdős–Turán para bases aditivas de ordem 2 ($A \subset \mathbb{N}$ tal que $r_{A+A}(n) \ge 1$ para todo $n$ suficientemente grande $\implies \limsup_{n \to \infty} r_{A+A}(n) = \infty$). Implementar crivo de busca de bases aditivas finitas minimais e provar formalmente no kernel do Lean 4 em `lean_proofs/Generated/ErdosTuranBasesTheorems.lean` limitantes estruturais de representação, propriedades de finitude e lemas de contagem de somas.

Alterações permitidas: `lean_proofs/`, `src/evobyte/additive.py`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p117-config.json`, `experiments/p117-run.sh`.
Fora do escopo: alegações de resolução universal definitiva da conjectura de Erdős–Turán sem prova analítica completa e fechada; uso de axiomas não padrão.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-combinatória-aditiva-conjuntos-de-sidon-e-teoria-de-densidade-em-lean-4-p113p120).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar motor de avaliação de bases aditivas e funções de representação $r_{A+A}(n)$ em `src/evobyte/additive.py`.
2. Provar teoremas formais sobre funções de representação e limitantes inferiores em `lean_proofs/Generated/ErdosTuranBasesTheorems.lean`.
3. Adicionar interface de auditoria P117 em `benchmarks/science_matrix.py` (`run_p117_erdos_turan_bases_audit`) com validação de compilação sem `sorry`.

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry` e auditoria P117 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P117 --config experiments/p117-config.json --output /tmp/evobyte-p117-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p117 erdos turan additive bases"
git push -u origin HEAD
gh pr create --base codex/p116-additive-norm-metatactic --title "feat(formal): implement p117 erdos turan additive bases" --body-file /tmp/evobyte-p117-pr.md
```
