# P141 — Sistemas de recobrimento de congruências e teorema de Hough do módulo mínimo

**Status:** Done.
**Dependência:** P140 concluída; branch a partir de `codex/p140-discrepancy-norm-metatactic`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P140 concluída com meta-tática `discrepancy_norm` funcional e testada.
**Branch:** `codex/p141-covering-systems-minimum-modulus-hough`.

## Hipótese, objetivo e escopo

Formalizar no Lean 4 os teoremas de sistemas de recobrimento de congruências de Paul Erdős (1950) e a resolução histórica da Conjectura do Menor Módulo por Bob Hough (2015) (`lean_proofs/Generated/CoveringSystemsTheorems.lean`). Provar propriedades de sistemas de recobrimento $\bigcup_{i=1}^k (a_i \pmod{m_i}) = \mathbb{Z}$ com módulos estritamente distintos $m_1 < m_2 < \dots < m_k$, a cota superior universal de Hough para o menor módulo $m_1 \le 10^{16}$, a densidade local via crivo probabilístico e a inexistência de sistemas de recobrimento estritamente ímpares de tamanho limitado.

Alterações permitidas: `lean_proofs/`, `src/evobyte/discrepancy.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p141-config.json`, `experiments/p141-run.sh`.
Fora do escopo: alegações de solução para o problema do módulo ímpar irrestrito fora do formalismo comprovado.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-teoria-de-discrepância-problema-da-discrepância-de-erdős-e-sistemas-de-recobrimento-em-lean-4-p137p144).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar teoremas de congruências de recobrimento, bounds de densidade de módulo e invariantes de Hough em `lean_proofs/Generated/CoveringSystemsTheorems.lean`.
2. Adicionar geradores de sistemas de congruências de recobrimento e crivos modulares em `src/evobyte/discrepancy.py`.
3. Adicionar interface de auditoria P141 em `benchmarks/science_matrix.py` (`run_p141_covering_systems_audit`).

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry` e auditoria P141 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P141 --config experiments/p141-config.json --output /tmp/evobyte-p141-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p141 covering systems minimum modulus hough"
git push -u origin HEAD
gh pr create --base codex/p140-discrepancy-norm-metatactic --title "feat(formal): implement p141 covering systems minimum modulus hough" --body-file /tmp/evobyte-p141-pr.md
```
