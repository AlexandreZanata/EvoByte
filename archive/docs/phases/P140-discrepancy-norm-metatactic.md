# P140 — Meta-tática customizada discrepancy_norm e automação de discrepância em Lean 4

**Status:** Done.
**Dependência:** P139 concluída; branch a partir de `codex/p139-roth-spencer-discrepancy-progressions`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P139 concluída com teoremas de Roth e Spencer aprovados no kernel do Lean 4.
**Branch:** `codex/p140-discrepancy-norm-metatactic`.

## Hipótese, objetivo e escopo

Projetar e implementar no Lean 4 a meta-tática combinatória `discrepancy_norm` e seu despachador `discrepancy_intro` (`lean_proofs/Generated/DiscrepancyTacticTheorems.lean`), automatizando a simplificação algébrica de somas de sinais $\sum \chi(x)$, desigualdades triangulares de valores absolutos $|a + b| \le |a| + |b|$, limites de Cauchy–Schwarz $\left(\sum a_i b_i\right)^2 \le \sum a_i^2 \sum b_i^2$, cotas de ortogonalidade e normalização de somas parciais de discrepância em $\{-1, 1\}^n$.

Alterações permitidas: `lean_proofs/`, `src/evobyte/discrepancy.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p140-config.json`, `experiments/p140-run.sh`.
Fora do escopo: alteração de regras do kernel Lean 4; táticas incompletas com pendência de prova.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-teoria-de-discrepância-problema-da-discrepância-de-erdős-e-sistemas-de-recobrimento-em-lean-4-p137p144).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar a sintaxe e os elaboradores das meta-táticas `discrepancy_norm` e `discrepancy_intro` em `lean_proofs/Generated/DiscrepancyTacticTheorems.lean`.
2. Provar pelo menos 80 teoremas e lemas formais no Lean 4 despachados exclusivamente via `discrepancy_norm`.
3. Adicionar interface de auditoria P140 em `benchmarks/science_matrix.py` (`run_p140_discrepancy_norm_audit`).

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry`, meta-tática funcional e auditoria P140 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P140 --config experiments/p140-config.json --output /tmp/evobyte-p140-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p140 discrepancy norm metatactic"
git push -u origin HEAD
gh pr create --base codex/p139-roth-spencer-discrepancy-progressions --title "feat(formal): implement p140 discrepancy norm metatactic" --body-file /tmp/evobyte-p140-pr.md
```
