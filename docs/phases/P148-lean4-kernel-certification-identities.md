# P148 — Certificação formal no kernel Lean 4 das novas identidades paramétricas

**Status:** Proposed.
**Dependência:** P147 concluída; branch a partir de `codex/p147-automated-polynomial-identity-synthesis`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P147 concluída com identidades polinomiais descobertas e verificadas simbolicamente em Python.
**Branch:** `codex/p148-lean4-kernel-certification-identities`.

## Hipótese, objetivo e escopo

Compilar e certificar formalmente no kernel do Lean 4 (`lean_proofs/Generated/SchinzelHighModuliTheorems.lean`) todas as novas identidades paramétricas sintetizadas em P147. Demonstrar mecanicamente que cada identidade satisfaz a equação de Schinzel $a \cdot X(k) Y(k) Z(k) = n(k) (Y(k)Z(k) + X(k)Z(k) + X(k)Y(k))$ no anel $\mathbb{Q}[k]$ via tática `ring`, e provar lemas indutivos em $\mathbb{N}$ que garantam que os denominadores são inteiros estritamente positivos para todo $k \ge 0$, sem uso de `sorry`, axiomas ad-hoc ou atalhos heurísticos.

Alterações permitidas: `lean_proofs/`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p148-config.json`, `experiments/p148-run.sh`.
Fora do escopo: uso de axiomas não padrão; teoremas com `admit` ou `sorry`.

Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar gerador automático de teoremas Lean 4 para identidades paramétricas de alta ordem em `src/evobyte/formal_bridge.py`.
2. Provar no kernel do Lean 4 a correção algébrica exata e a positividade inteira em `lean_proofs/Generated/SchinzelHighModuliTheorems.lean`.
3. Adicionar interface de auditoria P148 em `benchmarks/science_matrix.py` (`run_p148_schinzel_lean4_certification_audit`).

## Gate de saída

Compilação completa pelo Lake no Lean 4 com 0 `sorry` e auditoria P148 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P148 --config experiments/p148-config.json --output /tmp/evobyte-p148-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p148 lean4 kernel certification identities"
git push -u origin HEAD
gh pr create --base codex/p147-automated-polynomial-identity-synthesis --title "feat(formal): implement p148 lean4 kernel certification identities" --body-file /tmp/evobyte-p148-pr.md
```
