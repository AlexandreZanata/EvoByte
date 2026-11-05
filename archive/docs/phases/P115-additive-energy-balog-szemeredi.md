# P115 — Teoremas de energia aditiva e limitantes de Balog-Szemerédi-Gowers

**Status:** Done (2026-10-18; teoremas de energia aditiva, Cauchy–Schwarz, Plünnecke–Ruzsa e fibras de Balog–Szemerédi–Gowers, 79 teoremas sem sorry em AdditiveEnergyTheorems.lean, PR #151; lake build e pytest verdes).
**Dependência:** P114 concluída; branch a partir de `codex/p114-sidon-sets-extremal-search`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P114 concluída com construções de Sidon provadas em Lean 4.
**Branch:** `codex/p115-additive-energy-balog-szemeredi`.

## Hipótese, objetivo e escopo

Formalizar e certificar em Lean 4 (`lean_proofs/Generated/AdditiveEnergyTheorems.lean`) teoremas fundamentais da combinatória aditiva conectando a energia aditiva $E(A, B)$ ao tamanho do conjunto soma $|A+B|$ e conjunto diferença $|A-A|$ (desigualdades de Cauchy–Schwarz aditivas, lemas de Plünnecke–Ruzsa $|A+B| \le K|A| \implies |kA - \ell A| \le K^{k+\ell}|A|$ e limitantes estruturais de tipo Balog–Szemerédi–Gowers), integrando crivo de verificação de energia em Python.

Alterações permitidas: `lean_proofs/`, `src/evobyte/additive.py`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p115-config.json`, `experiments/p115-run.sh`.
Fora do escopo: uso de axiomas não padrão; provas incompletas ou aproximações sem certificados exatos.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-combinatória-aditiva-conjuntos-de-sidon-e-teoria-de-densidade-em-lean-4-p113p120).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar motor de cálculo e limitantes de energia aditiva e constantes de doubling em `src/evobyte/additive.py`.
2. Provar teoremas de energia aditiva e desigualdades de soma-diferença no Lean 4 em `lean_proofs/Generated/AdditiveEnergyTheorems.lean`.
3. Adicionar interface de auditoria P115 em `benchmarks/science_matrix.py` (`run_p115_additive_energy_audit`) com compilação sem `sorry`.

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry` e auditoria P115 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P115 --config experiments/p115-config.json --output /tmp/evobyte-p115-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p115 additive energy balog szemeredi"
git push -u origin HEAD
gh pr create --base codex/p114-sidon-sets-extremal-search --title "feat(formal): implement p115 additive energy balog szemeredi" --body-file /tmp/evobyte-p115-pr.md
```
