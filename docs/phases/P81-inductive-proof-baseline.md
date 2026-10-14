# P81 — Harness de prova indutiva e verificação estrutural Lean 4

**Status:** Done.
**Dependência:** P80 concluída (PR #109 aberto) e P81-P88 formalizados; branch a partir de `codex/p81-p88-inductive-lean-program`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P80 concluída com dossiê formal de campanha e 149 teoremas provados no kernel Lean 4; ambiente local Lean 4 e Lake operacionais hermeticamente.
**Branch:** `codex/p81-inductive-proof-baseline`.

## Hipótese, objetivo e escopo

Estabelecer infraestrutura no Lean 4 e harness hermético em Python para verificação de provas indutivas e lemas auxiliares sobre divisores e congruências em $\mathbb{N}$ (superando a restrição de identidades de anel puramente racionais em $\mathbb{Q}[k]$).

Alterações permitidas: `lean_proofs/`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/test_formal_bridge.py`, `experiments/p81-config.json`, `experiments/p81-run.sh`.
Fora do escopo: download de pacotes externos em tempo de execução; axiomas não padrão; enfraquecimento do kernel Lean 4.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-prova-indutiva-síntese-de-lemas-e-automação-de-táticas-em-lean-4-p81p88).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Auditar suporte às táticas indutivas e de aritmética de Presburger (`omega`, `linarith`, `induction`) em `lean_proofs/`.
2. Implementar módulo de geração e validação de lemas indutivos básicos em $\mathbb{N}$ em `src/evobyte/formal_bridge.py` (`export_inductive_lemmas_catalog`).
3. Adicionar interface de auditoria P81 em `benchmarks/science_matrix.py` (`run_p81_inductive_baseline_audit`) com validação de compilação sem `sorry`.

## Gate de saída

Execução limpa de compilação Lean hermética de lemas indutivos em $\mathbb{N}$ com 0 `sorry` e interface de aceitação P81:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P81 --config experiments/p81-config.json --output /tmp/evobyte-p81-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p81 inductive proof baseline"
git push -u origin HEAD
gh pr create --base codex/p81-p88-inductive-lean-program --title "feat(formal): implement p81 inductive proof baseline" --body-file /tmp/evobyte-p81-pr.md
```
