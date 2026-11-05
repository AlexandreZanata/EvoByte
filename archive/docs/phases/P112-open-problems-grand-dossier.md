# P112 — Grande campanha de resolução e progresso formal com dossiê de literatura e 1.500+ teoremas

**Status:** Done (2026-10-17; campanha formal com 1.929 teoremas no kernel do Lean 4 em 26 módulos sem sorry, hash chain imutável SHA-256 final 0ee06b77b0f6019362c34070d3ea7b13903d020f26be441d8aebc1f8170c3268, dossiê docs/research/p112-open-problems-dossier.md, artefato /tmp/evobyte-p112-acceptance.json; lake build e pytest verdes).
**Dependência:** P111 concluída; branch a partir de `codex/p111-multiproblem-blind-confirmation`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P111 concluída com confirmação estatística cega multiproblema aprovada; ambiente Lean 4 e Lake herméticos.
**Branch:** `codex/p112-open-problems-grand-dossier`.

## Hipótese, objetivo e escopo

Consolidar a campanha formal multiproblema no Lean 4 com mais de 1.500 teoremas matemáticos certificados sem `sorry`, acompanhado do dossiê exaustivo de literatura, integridade criptográfica com hash chain SHA-256 e delimitação honesta entre instâncias resolvidas, teoremas gerais parciais e o estado aberto contínuo das conjecturas universais.

Alterações permitidas: `lean_proofs/`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p112-config.json`, `experiments/p112-run.sh`, `docs/research/p112-open-problems-dossier.md`.
Fora do escopo: alegações de resolução universal sem provas completas no kernel; uso de axiomas não padrão.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-descoberta-formal-em-problemas-abertos-e-teoria-de-modelos-guiada-por-provas-em-lean-4-p105p112).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Executar campanha formal integrando todos os módulos gerados da biblioteca Lean 4.
2. Validar que a contagem total de teoremas no kernel do Lean 4 ultrapassa 1.500 teoremas com zero `sorry`.
3. Elaborar dossiê exaustivo de literatura matemática em `docs/research/p112-open-problems-dossier.md` com hash chain SHA-256 encadeada.
4. Adicionar interface de auditoria final P112 em `benchmarks/science_matrix.py` (`run_p112_open_problems_grand_campaign_audit`).

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry`, hash chain imutável e auditoria P112 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P112 --config experiments/p112-config.json --output /tmp/evobyte-p112-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p112 open problems grand dossier"
git push -u origin HEAD
gh pr create --base codex/p111-multiproblem-blind-confirmation --title "feat(formal): implement p112 open problems grand dossier" --body-file /tmp/evobyte-p112-pr.md
```
