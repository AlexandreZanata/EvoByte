# P102 — Generalização para potências superiores e frações diofantinas de grau k

**Status:** Proposed.
**Dependência:** P101 concluída; branch a partir de `codex/p97-p104-diophantine-geometry-program`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P101 concluída com teoremas de momentos assintóticos verificados; ambiente Lean 4 e Lake herméticos.
**Branch:** `codex/p102-higher-power-diophantine-fractions`.

## Hipótese, objetivo e escopo

Generalizar as identidades diofantinas para frações com denominadores de potências superiores $\frac{a}{n^k} = \frac{1}{x} + \frac{1}{y} + \frac{1}{z}$ para expoentes $k \ge 2$, provando identidades algébricas parametrizadas em $\mathbb{Q}[k]$ e lemas de divisibilidade inteira em `lean_proofs/Generated/HigherPowerTheorems.lean`.

Alterações permitidas: `lean_proofs/`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p102-config.json`, `experiments/p102-run.sh`.
Fora do escopo: enfraquecimento do kernel Lean 4.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-geometria-algébrica-diofantina-fibrados-de-superfícies-cúbicas-e-invariantes-em-lean-4-p97p104).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar formalização de identidades para denominadores quadráticos e cúbicos $n^k$ em `lean_proofs/Generated/HigherPowerTheorems.lean`.
2. Adicionar síntese de soluções de grau superior em `src/evobyte/formal_bridge.py`.
3. Adicionar interface de auditoria P102 em `benchmarks/science_matrix.py` (`run_p102_higher_power_audit`) com validação de compilação sem `sorry`.

## Gate de saída

Execução limpa de compilação dos teoremas de potências superiores no Lean 4 com 0 `sorry` e interface de aceitação P102:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P102 --config experiments/p102-config.json --output /tmp/evobyte-p102-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p102 higher power diophantine fractions"
git push -u origin HEAD
gh pr create --base codex/p97-p104-diophantine-geometry-program --title "feat(formal): implement p102 higher power diophantine fractions" --body-file /tmp/evobyte-p102-pr.md
```
