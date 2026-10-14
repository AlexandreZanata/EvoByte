# P89 — Meta-programação e tática customizada evobyte_solve em Lean 4

**Status:** Done.
**Dependência:** P88 concluída na `main` e P89-P96 formalizados; branch a partir de `codex/p89-p96-generalized-schinzel-program`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P88 concluída com 406 teoremas Lean 4 verificados e consolidação na branch main; ambiente Lean 4 e Lake herméticos.
**Branch:** `codex/p89-custom-tactic-metaprogramming`.

## Hipótese, objetivo e escopo

Construir e verificar uma tática customizada de meta-programação em Lean 4 (`evobyte_solve` / `evobyte_diophantine`) que unifique regras de reescrita algébrica de anéis, simplificação aritmética e despacho guiado para identidades e desigualdades de frações unitárias diofantinas.

Alterações permitidas: `lean_proofs/`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p89-config.json`, `experiments/p89-run.sh`.
Fora do escopo: download de bibliotecas Lean não registradas; enfraquecimento do kernel; uso de axiomas não padrão.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-resolução-modular-generalizada-meta-táticas-e-conjectura-de-schinzel-ampliada-em-lean-4-p89p96).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar módulo de meta-programação em Lean 4 definindo a macro-tática customizada `evobyte_solve` em `lean_proofs/Tactic/` (com suporte a `macro`, `syntax` e encadeamento de táticas).
2. Adicionar gerador de teoremas com despacho via `evobyte_solve` em `src/evobyte/formal_bridge.py`.
3. Adicionar interface de auditoria P89 em `benchmarks/science_matrix.py` (`run_p89_custom_tactic_audit`) com validação de compilação sem `sorry`.

## Gate de saída

Execução limpa de compilação da tática customizada no Lean 4 com 0 `sorry` e interface de aceitação P89:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P89 --config experiments/p89-config.json --output /tmp/evobyte-p89-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p89 custom tactic metaprogramming"
git push -u origin HEAD
gh pr create --base codex/p89-p96-generalized-schinzel-program --title "feat(formal): implement p89 custom tactic metaprogramming" --body-file /tmp/evobyte-p89-pr.md
```
