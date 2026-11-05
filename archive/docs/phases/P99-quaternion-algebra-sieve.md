# P99 — Crivo algébrico em ordens quaternônicas e álgebras de divisão

**Status:** Done.
**Dependência:** P98 concluída; branch a partir de `codex/p98-rational-conic-parametrizations`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P98 concluída com parametrizações de cônicas verificadas; ambiente Lean 4 e Lake herméticos.
**Branch:** `codex/p99-quaternion-algebra-sieve`.

## Hipótese, objetivo e escopo

Desenvolver um crivo de fatoração em ordens de quatérnios $\mathcal{O} \subset \mathbb{H}(\alpha, \beta)$ sobre $\mathbb{Q}$, decompondo a norma reduzida $N(q) = x_0^2 - \alpha x_1^2 - \beta x_2^2 + \alpha \beta x_3^2$ para desobstruir classes modulares resistentes com fatores não-quadráticos, provando formalmente a correspondência diofantina em `lean_proofs/Generated/QuaternionAlgebraTheorems.lean`.

Alterações permitidas: `lean_proofs/`, `src/evobyte/quaternion_sieve.py`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p99-config.json`, `experiments/p99-run.sh`.
Fora do escopo: bibliotecas externas de álgebra computacional sem ligação hermética.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-geometria-algébrica-diofantina-fibrados-de-superfícies-cúbicas-e-invariantes-em-lean-4-p97p104).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar motor de fatoração quaternônica em `src/evobyte/quaternion_sieve.py` com testes unitários em `tests/test_quaternion_sieve.py`.
2. Implementar teoremas de álgebra de quatérnios e fatoração de normas em `lean_proofs/Generated/QuaternionAlgebraTheorems.lean`.
3. Adicionar interface de auditoria P99 em `benchmarks/science_matrix.py` (`run_p99_quaternion_sieve_audit`) com validação de compilação sem `sorry`.

## Gate de saída

Execução limpa de compilação dos teoremas quaternônicos no Lean 4 com 0 `sorry` e interface de aceitação P99:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests/test_quaternion_sieve.py -q
python3 benchmarks/science_matrix.py --acceptance-phase P99 --config experiments/p99-config.json --output /tmp/evobyte-p99-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p99 quaternion algebra sieve"
git push -u origin HEAD
gh pr create --base codex/p98-rational-conic-parametrizations --title "feat(formal): implement p99 quaternion algebra sieve" --body-file /tmp/evobyte-p99-pr.md
```
