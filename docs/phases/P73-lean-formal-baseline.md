# P73 — Infraestrutura de verificação formal e harness Lean 4

**Status:** Proposed.
**Dependência:** P72 concluída (PR #100 aberto); branch a partir de `codex/p72-novelty-nomination`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P72 concluída com medição de novidade aceita em árvore limpa; ambiente local com Lean 4 (`lean_proofs/`) e Lake operacionais hermeticamente.
**Branch:** `codex/p73-lean-formal-baseline`.

## Hipótese, objetivo e escopo

Garantir um harness hermético de verificação formal em Lean 4 para validação de teoremas matemáticos gerados pelo EvoByte sem dependência de rede em tempo de teste.

Alterações permitidas: `lean_proofs/`, `benchmarks/science_matrix.py`, testes de integração formal e scripts de auditoria em `experiments/`.
Fora do escopo: novas conjecturas, download de pacotes externos durante a execução de testes, modificação de semântica do Lean kernel.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-busca-algébrica-e-verificação-formal-lean-4-p73p80).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Auditar a configuração de `lean_proofs/` (`lakefile.toml`, `lean-toolchain`, pacotes locais em `.lake`).
2. Implementar interface de checagem formal rápida via Lake (`lake env lean`) que recebe arquivos de prova gerados e valida o kernel sem rede.
3. Adicionar testes unitários garantindo que provas válidas passam (`norm_num`, `ring`) e provas falsas são rejeitadas pelo kernel.

## Gate de saída

Execução limpa de compilação Lean hermética, verificação de teoremas de teste (`P48Proofs.lean`) e interface de aceitação P73:

```bash
git diff --check
git status --short
python3 -m pytest tests/test_science.py -q
lake --directory lean_proofs build
python3 benchmarks/science_matrix.py --acceptance-phase P73
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p73 lean formal baseline"
git push -u origin HEAD
gh pr create --base codex/p72-novelty-nomination --title "feat(formal): implement p73 lean formal baseline" --body-file /tmp/evobyte-p73-pr.md
```
