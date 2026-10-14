# P84 — Síntese de identidades quadráticas multiparâmetro

**Status:** Done.
**Dependência:** P83 Done; branch a partir de `codex/p83-optimal-divisor-selection`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P83 concluída com crivo ótimo de divisores.
**Branch:** `codex/p84-multiparameter-quadratic-identities`.

## Hipótese, objetivo e escopo

Sintetizar identidades algébricas diofantinas parametrizadas por formas quadráticas e de 2 parâmetros $n = a u^2 + b u v + c v^2$ para abordar os resíduos resistentes mod 840 de Erdős–Straus e mod 120 de Sierpiński, com validação formal no kernel Lean 4.

Alterações permitidas: `src/evobyte/algebraic.py`, `src/evobyte/formal_bridge.py`, `lean_proofs/Generated/`, `benchmarks/science_matrix.py`, `experiments/`.
Fora do escopo: soluções não polinomiais; alegação de cobertura universal total sem prova formal completa.

## Trabalho ordenado

1. Implementar sintetizador de identidades algébricas multivariadas em $\mathbb{Q}[u, v]$ (`Poly2D` e `QuadraticIdentity`).
2. Descobrir e certificar identidades para resíduos quadráticos resistentes selecionados (Erdős–Straus mod 840: $121, 169, 289, 361, 529$; Sierpiński mod 120: $9, 49, 121, 169, 529$).
3. Exportar teoremas para Lean 4 (`QuadraticIdentities.lean`) e compilar via Lake com zero `sorry`.

## Gate de saída

Identidades quadráticas sintetizadas e compiladas no Lean 4 com aceitação integral:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P84 --config experiments/p84-config.json --output /tmp/evobyte-p84-acceptance.json
```

## Evidência de aceitação e auditoria formal

Auditoria executada em árvore limpa com veredicto **ACCEPTED** registrado em `/tmp/evobyte-p84-acceptance.json`:

- **Veredicto:** `ACCEPTED`
- **Total de teoremas:** 22 (12 identidades paramétricas multivariadas em $\mathbb{Q}[u, v]$ provadas via `ring` + 10 certificados diofantinos para resíduos resistentes provados via `norm_num`).
- **Has sorry:** `false` (0 tokens `sorry`).
- **Módulo Lean 4:** `lean_proofs/Generated/QuadraticIdentities.lean`.
- **SHA-256 do módulo:** `05abf53c1b4b142a449428e3c316edad4155f68ec1fb6eb4f94ccd83f5520f83`.
- **Revisão:** `c8242af2679e678331639dcd3c0850f0894de53d`.
- **Árvore limpa:** `dirty: ""` confirmado.

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p84 multiparameter quadratic identities"
git push -u origin HEAD
gh pr create --base codex/p83-optimal-divisor-selection --title "feat(formal): implement p84 multiparameter quadratic identities" --body-file /tmp/evobyte-p84-pr.md
```
