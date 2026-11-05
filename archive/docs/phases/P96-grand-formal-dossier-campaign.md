# P96 — Grande campanha formal e dossiê certificado final em Lean 4

**Status:** Done.
**Dependência:** P95 Proposed; branch a partir de `codex/p95-extreme-scale-blind-confirmation`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P95 concluída com confirmação estatística extrema aprovada.
**Branch:** `codex/p96-grand-formal-dossier-campaign`.

## Hipótese, objetivo e escopo

Consolidar a campanha formal final do programa P89–P96, gerando e certificando no Lean 4 um catálogo integrado com mais de 500 teoremas formais comprovados sem `sorry`, acompanhado do dossiê matemático e hash chain de todos os certificados gerados.

Alterações permitidas: `lean_proofs/`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p96-config.json`, `experiments/p96-run.sh`, `docs/`.
Fora do escopo: alegações de completude sem compilação de provas no kernel; uso de axiomas não padrão.

## Trabalho ordenado

1. Executar campanha formal gerando o dossiê consolidado e integrando todos os lemas em `lean_proofs/Generated/`.
2. Validar que a contagem total de teoremas no Lean 4 ultrapassa 500 teoremas com zero `sorry`.
3. Adicionar auditoria final P96 em `benchmarks/science_matrix.py` (`run_p96_grand_campaign_audit`).

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry` e auditoria P96 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P96 --config experiments/p96-config.json --output /tmp/evobyte-p96-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p96 grand formal dossier campaign"
git push -u origin HEAD
gh pr create --base codex/p95-extreme-scale-blind-confirmation --title "feat(formal): implement p96 grand formal dossier campaign" --body-file /tmp/evobyte-p96-pr.md
```
