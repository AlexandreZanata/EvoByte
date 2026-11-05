# P136 — Grande campanha formal de geometria discreta com dossiê certificado em Lean 4

**Status:** In review.
**Dependência:** P135 concluída; branch a partir de `codex/p135-discrete-geometry-blind-confirmation`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P135 concluída com confirmação estatística cega aprovada; ambiente Lean 4 e Lake herméticos.
**Branch:** `codex/p136-discrete-geometry-grand-dossier`.

## Hipótese, objetivo e escopo

Consolidar a biblioteca formal unificada de geometria discreta, distâncias distintas de Erdős e configurações de pontos no Lean 4 com mais de 3.300 teoremas matemáticos certificados em 44 módulos sem `sorry`, acompanhado do dossiê exaustivo de literatura em `docs/research/p136-discrete-geometry-dossier.md` e hash chain criptográfica SHA-256 encadeada.

Alterações permitidas: `lean_proofs/`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p136-config.json`, `experiments/p136-run.sh`, `docs/research/p136-discrete-geometry-dossier.md`.
Fora do escopo: alegações de resolução universal de conjecturas abertas sem demonstração no kernel do Lean 4; uso de axiomas não padrão.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-geometria-discreta-distâncias-distintas-de-erdős-e-configurações-de-pontos-em-lean-4-p129p136).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Executar campanha formal integrando todos os 44 módulos da biblioteca Lean 4.
2. Validar que a contagem total de teoremas no kernel do Lean 4 ultrapassa 3.300 teoremas com zero `sorry`.
3. Elaborar dossiê exaustivo de literatura matemática em `docs/research/p136-discrete-geometry-dossier.md` com hash chain SHA-256 encadeada.
4. Adicionar interface de auditoria final P136 em `benchmarks/science_matrix.py` (`run_p136_discrete_geometry_grand_campaign_audit`).

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry`, hash chain imutável e auditoria P136 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P136 --config experiments/p136-config.json --output /tmp/evobyte-p136-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p136 discrete geometry grand dossier"
git push -u origin HEAD
gh pr create --base codex/p135-discrete-geometry-blind-confirmation --title "feat(formal): implement p136 discrete geometry grand dossier" --body-file /tmp/evobyte-p136-pr.md
```
