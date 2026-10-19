# P144 — Grande campanha formal de discrepância e recobrimentos com dossiê certificado em Lean 4

**Status:** Proposed.
**Dependência:** P143 concluída; branch a partir de `codex/p143-discrepancy-covering-blind-confirmation`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P143 concluída com confirmação estatística cega aprovada; ambiente Lean 4 e Lake herméticos.
**Branch:** `codex/p144-discrepancy-covering-grand-dossier`.

## Hipótese, objetivo e escopo

Consolidar a biblioteca formal unificada de teoria de discrepância combinatória, o Problema da Discrepância de Erdős (EDP), sistemas de recobrimento e conjuntos primitivos no Lean 4 com mais de 3.800 teoremas matemáticos certificados em 50 módulos sem `sorry`, acompanhado do dossiê exaustivo de literatura em `docs/research/p144-discrepancy-covering-dossier.md` e hash chain criptográfica SHA-256 encadeada.

Alterações permitidas: `lean_proofs/`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p144-config.json`, `experiments/p144-run.sh`, `docs/research/p144-discrepancy-covering-dossier.md`.
Fora do escopo: alegações de resolução universal de conjecturas abertas sem demonstração no kernel do Lean 4; uso de axiomas não padrão.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-teoria-de-discrepância-problema-da-discrepância-de-erdős-e-sistemas-de-recobrimento-em-lean-4-p137p144).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Executar campanha formal integrando todos os 50 módulos da biblioteca Lean 4.
2. Validar que a contagem total de teoremas no kernel do Lean 4 ultrapassa 3.800 teoremas com zero `sorry`.
3. Elaborar dossiê exaustivo de literatura matemática em `docs/research/p144-discrepancy-covering-dossier.md` com hash chain SHA-256 encadeada.
4. Adicionar interface de auditoria final P144 em `benchmarks/science_matrix.py` (`run_p144_discrepancy_covering_grand_campaign_audit`).

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry`, hash chain imutável e auditoria P144 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P144 --config experiments/p144-config.json --output /tmp/evobyte-p144-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p144 discrepancy covering grand dossier"
git push -u origin HEAD
gh pr create --base codex/p143-discrepancy-covering-blind-confirmation --title "feat(formal): implement p144 discrepancy covering grand dossier" --body-file /tmp/evobyte-p144-pr.md
```
