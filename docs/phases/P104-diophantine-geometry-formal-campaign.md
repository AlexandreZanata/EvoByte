# P104 — Grande campanha formal e dossiê de geometria diofantina em Lean 4

**Status:** Done.
**Dependência:** P103 concluída; branch a partir de `codex/p103-hyper-scale-blind-confirmation`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P103 concluída com confirmação estatística em hiper-escala aceita; ambiente Lean 4 e Lake herméticos.
**Branch:** `codex/p104-diophantine-geometry-formal-campaign`.

## Hipótese, objetivo e escopo

Consolidar a biblioteca formal de geometria diofantina em Lean 4, expandindo para mais de 1.200 teoremas matemáticos no kernel com zero tokens `sorry` através de mais de 20 módulos formais em `lean_proofs/Generated/`. Gerar a cadeia criptográfica de integridade SHA-256 de todos os módulos e publicar o dossiê científico completo em `docs/research/p104-diophantine-geometry-dossier.md`.

Alterações permitidas: `lean_proofs/`, `docs/research/p104-diophantine-geometry-dossier.md`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p104-config.json`, `experiments/p104-run.sh`.
Fora do escopo: enfraquecimento do kernel; alegações infundadas de resolução universal de conjecturas abertas.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-geometria-algébrica-diofantina-fibrados-de-superfícies-cúbicas-e-invariantes-em-lean-4-p97p104).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Consolidar os módulos formais em `lean_proofs/Generated/` totalizando 1.200+ teoremas verificados sem `sorry`.
2. Implementar auditoria global de integridade da biblioteca e cálculo de cadeia SHA-256 em `src/evobyte/formal_bridge.py`.
3. Compilar e publicar o dossiê de pesquisa de geometria diofantina em `docs/research/p104-diophantine-geometry-dossier.md`.
4. Adicionar interface de auditoria P104 em `benchmarks/science_matrix.py` (`run_p104_grand_formal_campaign_audit`).

## Gate de saída

Execução integral da auditoria com compilação hermética Lake, 0 `sorry`, 1.200+ teoremas e cadeia SHA-256 íntegra:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P104 --config experiments/p104-config.json --output /tmp/evobyte-p104-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p104 diophantine geometry formal campaign"
git push -u origin HEAD
gh pr create --base codex/p103-hyper-scale-blind-confirmation --title "feat(formal): implement p104 diophantine geometry formal campaign" --body-file /tmp/evobyte-p104-pr.md
```
