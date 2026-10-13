# P88 — Campanha formal de meta-teoremas e dossiê certificado

**Status:** Proposed.
**Dependência:** P87 Proposed; branch a partir de `codex/p87-large-instance-blind-confirmation`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P87 concluída com confirmação estatística aceita.
**Branch:** `codex/p88-meta-theorem-formal-campaign`.

## Hipótese, objetivo e escopo

Executar campanha formal bounded de 1 hora gerando uma biblioteca unificada de meta-teoremas e lemas diofantinos compilados no kernel do Lean 4 (Mathlib) com zero tokens `sorry`, e compilar o dossiê formal de novidade (`docs/research/p88-formal-dossier.md`) com limites rigorosos de escopo matemático.

Alterações permitidas: `experiments/p88-config.json`, `experiments/p88-run.sh`, `docs/research/p88-formal-dossier.md`.
Fora do escopo: alegação de solução universal de conjectura em aberto sem indução fechada sobre todo $\mathbb{N}$; adulteração de dados experimentais.

## Trabalho ordenado

1. Congelar configuração da campanha formal P88 (tempo limite, instâncias e regras de crivo).
2. Executar compilação integral da biblioteca de meta-teoremas no Lean 4 via Lake com verificação de zero `sorry`.
3. Elaborar dossiê formal de novidade e revisão de literatura em `docs/research/p88-formal-dossier.md`.

## Gate de saída

Biblioteca formal de meta-teoremas compilando 100% no Lean 4 com 0 `sorry`, integridade confirmada por auditoria P88 em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P88 --config experiments/p88-config.json --output /tmp/evobyte-p88-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "docs(formal): record p88 meta theorem formal campaign"
git push -u origin HEAD
gh pr create --base codex/p87-large-instance-blind-confirmation --title "docs(formal): record p88 meta theorem formal campaign" --body-file /tmp/evobyte-p88-pr.md
```
