# P150 — Auditoria rigorosa de novidade contra literatura internacional e checadores duais

**Status:** Proposed.
**Dependência:** P149 concluída; branch a partir de `codex/p149-extremal-finite-constructive-certificates`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P149 concluída com certificados construtivos verificados formalmente.
**Branch:** `codex/p150-world-literature-novelty-dual-audit`.

## Hipótese, objetivo e escopo

Auditar cada identidade paramétrica e certificado construtivo descoberto em P147–P149 contra os corpora de literatura mundial indexados (ErdosProblems, OEIS, publicações de Schinzel/Sierpiński/Elsholtz-Tao, MathOverflow e bases de grafos/Sidon). Submeter cada candidato a um verificador dual independente (checador aritmético simbólico em Python puro com biblioteca `fractions` + checador formal estrito em Lean 4). Classificar cada resultado com honestidade científica irrestrita: `known-rediscovery`, `novel-extension`, ou `inconclusive-instance`.

Alterações permitidas: `src/evobyte/algebraic.py`, `docs/research/`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p150-config.json`, `experiments/p150-run.sh`.
Fora do escopo: promoção de redescobertas conhecidas a alegações de novidade internacional; supressão de resultados negativos.

Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar motor de checagem cruzada e comparação com corpora de identidades conhecidas da literatura em `src/evobyte/algebraic.py`.
2. Elaborar relatório preliminar de novidade matemática em `docs/research/p150-novelty-audit-report.md`.
3. Adicionar interface de auditoria P150 em `benchmarks/science_matrix.py` (`run_p150_world_literature_audit`).

## Gate de saída

Execução com 100% de concordância entre checadores duais independentes e auditoria de literatura aceita:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P150 --config experiments/p150-config.json --output /tmp/evobyte-p150-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(research): implement p150 world literature novelty dual audit"
git push -u origin HEAD
gh pr create --base codex/p149-extremal-finite-constructive-certificates --title "feat(research): implement p150 world literature novelty dual audit" --body-file /tmp/evobyte-p150-pr.md
```
