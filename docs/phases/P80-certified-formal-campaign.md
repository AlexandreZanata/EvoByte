# P80 — Campanha formal bounded e dossiê de teoremas Lean 4

**Status:** Done.
**Dependência:** P79 Proposed; branch a partir de `codex/p79-blind-residue-confirmation`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P79 concluída com confirmação formal registrada.
**Branch:** `codex/p80-certified-formal-campaign`.

## Hipótese, objetivo e escopo

Executar campanha bounded de 1 hora no alvo formal nominado, compilando todas as identidades descobertas em teoremas formais provados no kernel Lean 4 (Mathlib), com dossiê reproduzível e avaliação rigorosa de novidade na literatura.

Alterações permitidas: `experiments/p80-config.json`, `experiments/p80-run.sh`, `docs/research/p80-formal-dossier.md`.
Fora do escopo: alegações de solução completa de conjectura aberta sem prova de 100% dos resíduos restantes; adulteração de logs.

## Trabalho ordenado

1. Congelar configuração da campanha (orçamento de 3600 s, teto de coordenadas e regras de crivo).
2. Executar campanha em árvore limpa com persistência durável dos artefatos e teoremas `.lean` gerados.
3. Compilar dossiê formal de novidade (`docs/research/p80-formal-dossier.md`) com revisão de literatura e status de cada resíduo.

## Gate de saída

Dossiê de campanha formal com 100% dos teoremas compilando no kernel Lean 4 sem `sorry`, artefatos duráveis com hashes verificados e auditoria via `science_matrix.py`:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P80 --config experiments/p80-config.json --output /tmp/evobyte-p80-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "docs(formal): record p80 certified formal campaign"
git push -u origin HEAD
gh pr create --base codex/p79-blind-residue-confirmation --title "docs(formal): record p80 certified formal campaign" --body-file /tmp/evobyte-p80-pr.md
```
