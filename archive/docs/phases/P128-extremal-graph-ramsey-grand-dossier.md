# P128 — Grande campanha formal de grafos e Ramsey com dossiê certificado em Lean 4

**Status:** In review.
**Dependência:** P127 concluída; branch a partir de `codex/p127-graph-ramsey-blind-confirmation`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P127 concluída com confirmação estatística cega aprovada; ambiente Lean 4 e Lake herméticos.
**Branch:** `codex/p128-extremal-graph-ramsey-grand-dossier`.

## Hipótese, objetivo e escopo

Consolidar a biblioteca formal unificada de teoria extremal de grafos, números de Ramsey e progressões aritméticas no Lean 4 com mais de 2.800 teoremas matemáticos certificados em 38 módulos sem `sorry`, acompanhado do dossiê exaustivo de literatura em `docs/research/p128-extremal-graph-ramsey-dossier.md` e hash chain criptográfica SHA-256 encadeada.

Alterações permitidas: `lean_proofs/`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p128-config.json`, `experiments/p128-run.sh`, `docs/research/p128-extremal-graph-ramsey-dossier.md`.
Fora do escopo: alegações de resolução universal de conjecturas abertas sem demonstração no kernel do Lean 4; uso de axiomas não padrão.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-teoria-extremal-de-grafos-números-de-ramsey-e-progressões-aritméticas-em-lean-4-p121p128).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Executar campanha formal integrando todos os 38 módulos da biblioteca Lean 4.
2. Validar que a contagem total de teoremas no kernel do Lean 4 ultrapassa 2.800 teoremas com zero `sorry`.
3. Elaborar dossiê exaustivo de literatura matemática em `docs/research/p128-extremal-graph-ramsey-dossier.md` com hash chain SHA-256 encadeada.
4. Adicionar interface de auditoria final P128 em `benchmarks/science_matrix.py` (`run_p128_extremal_graph_ramsey_grand_campaign_audit`).

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry`, hash chain imutável e auditoria P128 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P128 --config experiments/p128-config.json --output /tmp/evobyte-p128-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p128 extremal graph ramsey grand dossier"
git push -u origin HEAD
gh pr create --base codex/p127-graph-ramsey-blind-confirmation --title "feat(formal): implement p128 extremal graph ramsey grand dossier" --body-file /tmp/evobyte-p128-pr.md
```
