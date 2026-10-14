# P100 — Meta-tática unificada dioph_surface com eliminação algébrica em Lean 4

**Status:** Done.
**Dependência:** P99 concluída; branch a partir de `codex/p99-quaternion-algebra-sieve`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P99 concluída com crivo quaternônico verificado; ambiente Lean 4 e Lake herméticos.
**Branch:** `codex/p100-dioph-surface-metatactic`.

## Hipótese, objetivo e escopo

Desenvolver uma meta-tática nativa em Lean 4 (`dioph_surface`) integrando algoritmos de eliminação de variáveis, resultante de Bézout e normalização de frações racionais sobre variedades algébricas, provando teoremas de superfícies diofantinas de forma direta sem etapas manuais de reescrita.

Alterações permitidas: `lean_proofs/Tactic/`, `lean_proofs/Generated/`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p100-config.json`, `experiments/p100-run.sh`.
Fora do escopo: download de dependências externas ao ecossistema do repositório.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-geometria-algébrica-diofantina-fibrados-de-superfícies-cúbicas-e-invariantes-em-lean-4-p97p104).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar o módulo de tática `dioph_surface` em `lean_proofs/Tactic/DiophSurface.lean`.
2. Adicionar suporte a compilação com `dioph_surface` em `src/evobyte/formal_bridge.py`.
3. Adicionar interface de auditoria P100 em `benchmarks/science_matrix.py` (`run_p100_dioph_surface_audit`) com validação de compilação sem `sorry`.

## Gate de saída

Execução limpa de compilação da meta-tática `dioph_surface` no Lean 4 com 0 `sorry` e interface de aceitação P100:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P100 --config experiments/p100-config.json --output /tmp/evobyte-p100-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p100 dioph surface metatactic"
git push -u origin HEAD
gh pr create --base codex/p99-quaternion-algebra-sieve --title "feat(formal): implement p100 dioph surface metatactic" --body-file /tmp/evobyte-p100-pr.md
```
