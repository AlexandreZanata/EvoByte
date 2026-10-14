# P101 — Teoremas de momentos assintóticos e limites de densidade de soluções

**Status:** Proposed.
**Dependência:** P100 concluída; branch a partir de `codex/p97-p104-diophantine-geometry-program`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P100 concluída com meta-tática `dioph_surface` verificada; ambiente Lean 4 e Lake herméticos.
**Branch:** `codex/p101-solution-moments-asymptotics`.

## Hipótese, objetivo e escopo

Formalizar cotas assintóticas para a função de contagem de soluções $f_a(n) = \#\{(x, y, z) \in (\mathbb{Z}^+)^3 : \frac{a}{n} = \frac{1}{x} + \frac{1}{y} + \frac{1}{z}\}$, provando em Lean 4 que o primeiro momento satisfaz $\frac{1}{X} \sum_{n \le X} f_a(n) \ge c_a \log^2 X$ para uma constante explícita $c_a > 0$, estabelecendo formalmente a abundância média de soluções diofantinas em `lean_proofs/Generated/SolutionMomentsTheorems.lean`.

Alterações permitidas: `lean_proofs/`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p101-config.json`, `experiments/p101-run.sh`.
Fora do escopo: enfraquecimento do rigor do kernel Lean 4.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-geometria-algébrica-diofantina-fibrados-de-superfícies-cúbicas-e-invariantes-em-lean-4-p97p104).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar teoremas de momentos assintóticos e somas de divisores em `lean_proofs/Generated/SolutionMomentsTheorems.lean`.
2. Adicionar gerador de certificados analíticos em `src/evobyte/formal_bridge.py`.
3. Adicionar interface de auditoria P101 em `benchmarks/science_matrix.py` (`run_p101_solution_moments_audit`) com validação de compilação sem `sorry`.

## Gate de saída

Execução limpa de compilação dos teoremas de momentos assintóticos no Lean 4 com 0 `sorry` e interface de aceitação P101:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P101 --config experiments/p101-config.json --output /tmp/evobyte-p101-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p101 solution moments asymptotics"
git push -u origin HEAD
gh pr create --base codex/p97-p104-diophantine-geometry-program --title "feat(formal): implement p101 solution moments asymptotics" --body-file /tmp/evobyte-p101-pr.md
```
