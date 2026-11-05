# P98 — Síntese de parametrizações racionais via princípio local-global

**Status:** Done.
**Dependência:** P97 concluída; branch a partir de `codex/p97-p104-diophantine-geometry-program`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P97 concluída com teoremas de superfícies cúbicas compilados sem sorry; ambiente Lean 4 e Lake herméticos.
**Branch:** `codex/p98-rational-conic-parametrizations`.

## Hipótese, objetivo e escopo

Sintetizar e certificar formalmente parametrizações racionais unipotentes sobre curvas cônicas $C_x$ associadas a divisores diofantinos, provando via análise de Hilbert local-global que a ausência de obstruções em $\mathbb{Q}_p$ para fatores primos $p \mid n$ garante a solvabilidade da cônica em `lean_proofs/Generated/ConicParametrizations.lean`.

Alterações permitidas: `lean_proofs/`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p98-config.json`, `experiments/p98-run.sh`.
Fora do escopo: download de bibliotecas externas; alteração de axiomas do kernel Lean 4.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-geometria-algébrica-diofantina-fibrados-de-superfícies-cúbicas-e-invariantes-em-lean-4-p97p104).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar formalização das parametrizações racionais de Legendre para cônicas diofantinas em `lean_proofs/Generated/ConicParametrizations.lean`.
2. Adicionar gerador de identidades racionais locais-globais em `src/evobyte/formal_bridge.py`.
3. Adicionar interface de auditoria P98 em `benchmarks/science_matrix.py` (`run_p98_conic_parametrizations_audit`) com validação de compilação sem `sorry`.

## Gate de saída

Execução limpa de compilação dos teoremas de parametrização de cônicas no Lean 4 com 0 `sorry` e interface de aceitação P98:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P98 --config experiments/p98-config.json --output /tmp/evobyte-p98-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p98 rational conic parametrizations"
git push -u origin HEAD
gh pr create --base codex/p97-p104-diophantine-geometry-program --title "feat(formal): implement p98 rational conic parametrizations" --body-file /tmp/evobyte-p98-pr.md
```
