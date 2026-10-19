# P137 — Banco formal de teoria de discrepância combinatória e recobrimentos em Lean 4

**Status:** Proposed.
**Dependência:** P136 concluída; branch a partir de `codex/p137-p144-discrepancy-covering-program`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P136 concluída com grande campanha de geometria discreta consolidada documentalmente sob D036.
**Branch:** `codex/p137-discrepancy-covering-formal-database`.

## Hipótese, objetivo e escopo

Formalizar no Lean 4 o arcabouço tipado dependente de teoria de discrepância combinatória, sequências de sinais em $\{-1, +1\}$, hipergrafos de incidência e sistemas de congruências de recobrimento (`lean_proofs/Generated/DiscrepancyCoveringSignatures.lean`). Definir com rigor matemático o operador de discrepância combinatória $\text{disc}(\mathcal{F}, \chi) = \max_{S \in \mathcal{F}} |\sum_{x \in S} \chi(x)|$, o balanço sobre progressões aritméticas $\sum_{k=1}^n f(k \cdot d)$, a propriedade de multiplicatividade completa $f(a \cdot b) = f(a) f(b)$, sistemas de congruências $(a_i \pmod{m_i})$ e o predicado de recobrimento $\bigcup (a_i \pmod{m_i}) = \mathbb{Z}$.

Alterações permitidas: `lean_proofs/`, `src/evobyte/discrepancy.py`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p137-config.json`, `experiments/p137-run.sh`.
Fora do escopo: download de pacotes externos; alteração de axiomas do kernel Lean 4; alegações de resolução universal de conjecturas abertas sem certificados formais.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-teoria-de-discrepância-problema-da-discrepância-de-erdős-e-sistemas-de-recobrimento-em-lean-4-p137p144).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar definições, predicados e teoremas fundamentais de discrepância de sinais, hipergrafos finitos e sistemas de recobrimento em `lean_proofs/Generated/DiscrepancyCoveringSignatures.lean`.
2. Adicionar módulo `src/evobyte/discrepancy.py` com algoritmos determinísticos para cálculo exato de discrepância combinatória, verificação de multiplicatividade completa e teste de recobrimento de congruências.
3. Adicionar interface de auditoria P137 em `benchmarks/science_matrix.py` (`run_p137_discrepancy_covering_baseline_audit`) com compilação hermética sem `sorry`.

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry` e auditoria P137 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P137 --config experiments/p137-config.json --output /tmp/evobyte-p137-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p137 discrepancy covering formal database"
git push -u origin HEAD
gh pr create --base codex/p137-p144-discrepancy-covering-program --title "feat(formal): implement p137 discrepancy covering formal database" --body-file /tmp/evobyte-p137-pr.md
```
