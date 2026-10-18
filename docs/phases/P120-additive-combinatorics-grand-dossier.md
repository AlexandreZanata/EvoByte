# P120 — Grande campanha de combinatória aditiva e dossiê certificado final em Lean 4

**Status:** Done (2026-10-18; grande campanha formal com 2.392 teoremas no kernel do Lean 4 em 32 módulos sem sorry, hash chain SHA-256 final 8013152a11ac6cf28559ea1067cba32bfb3c7319d66d27766f636e1bec39acc3, dossiê docs/research/p120-additive-combinatorics-dossier.md, PR #156; lake build e pytest verdes).
**Dependência:** P119 concluída; branch a partir de `codex/p119-additive-blind-confirmation`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P119 concluída com confirmação estatística cega aprovada; ambiente Lean 4 e Lake herméticos.
**Branch:** `codex/p120-additive-combinatorics-grand-dossier`.

## Hipótese, objetivo e escopo

Consolidar a biblioteca formal unificada de combinatória aditiva e conjuntos de Sidon no Lean 4 com mais de 2.000 teoremas matemáticos certificados sem `sorry`, acompanhado do dossiê exaustivo de literatura em `docs/research/p120-additive-combinatorics-dossier.md`, integridade criptográfica com hash chain SHA-256 e delimitação honesta entre instâncias resolvidas, teoremas gerais parciais e o estado aberto contínuo das conjecturas universais (Erdős–Turán, Sidon, Roth e Freiman).

Alterações permitidas: `lean_proofs/`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p120-config.json`, `experiments/p120-run.sh`, `docs/research/p120-additive-combinatorics-dossier.md`.
Fora do escopo: alegações de resolução universal de conjecturas abertas sem demonstração no kernel do Lean 4; uso de axiomas não padrão.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-combinatória-aditiva-conjuntos-de-sidon-e-teoria-de-densidade-em-lean-4-p113p120).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Executar campanha formal integrando todos os novos módulos de combinatória aditiva da biblioteca Lean 4.
2. Validar que a contagem total de teoremas no kernel do Lean 4 ultrapassa 2.000 teoremas com zero `sorry`.
3. Elaborar dossiê exaustivo de literatura matemática em `docs/research/p120-additive-combinatorics-dossier.md` com hash chain SHA-256 encadeada.
4. Adicionar interface de auditoria final P120 em `benchmarks/science_matrix.py` (`run_p120_additive_grand_campaign_audit`).

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry`, hash chain imutável e auditoria P120 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P120 --config experiments/p120-config.json --output /tmp/evobyte-p120-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p120 additive combinatorics grand dossier"
git push -u origin HEAD
gh pr create --base codex/p119-additive-blind-confirmation --title "feat(formal): implement p120 additive combinatorics grand dossier" --body-file /tmp/evobyte-p120-pr.md
```
