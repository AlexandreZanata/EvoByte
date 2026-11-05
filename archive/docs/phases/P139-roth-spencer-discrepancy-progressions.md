# P139 — Cota de Roth em progressões aritméticas e cota de Spencer de seis desvios

**Status:** In review.
**Dependência:** P138 concluída; branch a partir de `codex/p138-erdos-discrepancy-completely-multiplicative`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P138 concluída com teoremas de multiplicatividade e EDP aprovados.
**Branch:** `codex/p139-roth-spencer-discrepancy-progressions`.

## Hipótese, objetivo e escopo

Formalizar no Lean 4 o célebre teorema de Klaus Roth (1964) estabelecendo a cota inferior para a discrepância de qualquer coloração de $\{1, \dots, N\}$ com respeito a progressões aritméticas ($\text{disc}(\mathcal{AP}) \ge c \cdot N^{1/4}$), e o teorema fundamental de Joel Spencer (1985) "Six standard deviations suffice" para sistemas finitos de $n$ subconjuntos em $n$ elementos ($\text{disc}(\mathcal{F}) \le 6\sqrt{n}$), superando a cota probabilística ingênua de $O(\sqrt{n \log n})$ (`lean_proofs/Generated/RothSpencerDiscrepancyTheorems.lean`).

Alterações permitidas: `lean_proofs/`, `src/evobyte/discrepancy.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p139-config.json`, `experiments/p139-run.sh`.
Fora do escopo: alegações de cotas inferiores estritas superiores a $\Omega(N^{1/4})$ para progressões sem prova formal.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-teoria-de-discrepância-problema-da-discrepância-de-erdős-e-sistemas-de-recobrimento-em-lean-4-p137p144).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar teoremas da cota inferior de Roth $\text{disc}(\mathcal{AP}) = \Omega(N^{1/4})$ via método de Fourier/somas quadráticas e teoremas de Spencer para matrizes de incidência balanceadas em `lean_proofs/Generated/RothSpencerDiscrepancyTheorems.lean`.
2. Adicionar algoritmos de cálculo de discrepância em progressões aritméticas e otimização de colorações de Spencer em `src/evobyte/discrepancy.py`.
3. Adicionar interface de auditoria P139 em `benchmarks/science_matrix.py` (`run_p139_roth_spencer_discrepancy_audit`).

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry` e auditoria P139 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P139 --config experiments/p139-config.json --output /tmp/evobyte-p139-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p139 roth spencer discrepancy progressions"
git push -u origin HEAD
gh pr create --base codex/p138-erdos-discrepancy-completely-multiplicative --title "feat(formal): implement p139 roth spencer discrepancy progressions" --body-file /tmp/evobyte-p139-pr.md
```
