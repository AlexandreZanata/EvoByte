# P77 — Compilador bytecode para teoremas certificados em Lean 4

**Status:** Proposed.
**Dependência:** P76 Proposed; branch a partir de `codex/p76-rational-divisor-sieve`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P76 aceita; harness Lean 4 operacional.
**Branch:** `codex/p77-bytecode-lean-proof-bridge`.

## Hipótese, objetivo e escopo

Compilar automaticamente expressões matemáticas geradas pelo EvoByte em definições e teoremas válidos em Lean 4, provados rigorosamente por táticas formais (`ring`, `norm_num`, `linarith`, `omega`) sem intervenção humana manual.

Alterações permitidas: `src/evobyte/formal_bridge.py`, `lean_proofs/Generated/`, `tests/test_formal_bridge.py`.
Fora do escopo: uso de táticas não confiáveis ou `sorry` no código Lean gerado.

## Trabalho ordenado

1. Implementar gerador de sintaxe Lean 4 para identidades racionais em $\mathbb{Q}$ e $\mathbb{N}$.
2. Gerar scripts de prova automáticos estruturados com introdução de variáveis, expansão algébrica e tática de fechamento.
3. Testar compilação direta via Lake e rejeitar compilações com `sorry` ou erros de tipo.

## Gate de saída

Compilação com sucesso de 100% dos teoremas gerados pelo pipeline no kernel Lean 4, sem avisos de incompletude (`sorry`), e validação via CI:

```bash
git diff --check
git status --short
python3 -m pytest tests/test_formal_bridge.py -q
lake --directory lean_proofs build
python3 benchmarks/science_matrix.py --acceptance-phase P77
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p77 bytecode lean proof bridge"
git push -u origin HEAD
gh pr create --base codex/p76-rational-divisor-sieve --title "feat(formal): implement p77 bytecode lean proof bridge" --body-file /tmp/evobyte-p77-pr.md
```
