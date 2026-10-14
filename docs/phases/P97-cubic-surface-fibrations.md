# P97 — Formalização de fibrados cônicos e superfícies cúbicas em Lean 4

**Status:** Done.
**Dependência:** P96 concluída na `main` e P97-P104 formalizados; branch a partir de `codex/p97-p104-diophantine-geometry-program`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P96 concluída com 965 teoremas Lean 4 verificados e consolidação na branch main; ambiente Lean 4 e Lake herméticos.
**Branch:** `codex/p97-cubic-surface-fibrations`.

## Hipótese, objetivo e escopo

Modelar formalmente a variedade diofantina $a x y z = n(yz + xz + xy)$ no kernel do Lean 4 como uma família de cônicas projetivas/afins $C_x(y, z)$ fibradas sobre a reta projetiva $\mathbb{P}^1(\mathbb{Q})$, provando o discriminante $\Delta(x) = (nx)^2$ e a existência de seções racionais globais no módulo `CubicSurfaceFibrations.lean`.

Alterações permitidas: `lean_proofs/`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p97-config.json`, `experiments/p97-run.sh`.
Fora do escopo: download de bibliotecas Lean não registradas; enfraquecimento do kernel; uso de axiomas não padrão.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-geometria-algébrica-diofantina-fibrados-de-superfícies-cúbicas-e-invariantes-em-lean-4-p97p104).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar formalização da cônica afim fibrada $C_x(y, z)$ e de sua matriz hessiana/discriminante em `lean_proofs/Generated/CubicSurfaceFibrations.lean`.
2. Adicionar gerador de certificados e teoremas de fibrados cúbicos em `src/evobyte/formal_bridge.py`.
3. Adicionar interface de auditoria P97 em `benchmarks/science_matrix.py` (`run_p97_cubic_surface_audit`) com validação de compilação sem `sorry`.

## Gate de saída

Execução limpa de compilação dos teoremas de fibrados cúbicos no Lean 4 com 0 `sorry` e interface de aceitação P97:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P97 --config experiments/p97-config.json --output /tmp/evobyte-p97-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p97 cubic surface fibrations"
git push -u origin HEAD
gh pr create --base codex/p97-p104-diophantine-geometry-program --title "feat(formal): implement p97 cubic surface fibrations" --body-file /tmp/evobyte-p97-pr.md
```
