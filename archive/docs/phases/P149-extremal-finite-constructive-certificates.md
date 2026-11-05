# P149 — Síntese e verificação formal de certificados extremais construtivos em combinatória finita

**Status:** Done.
**Dependência:** P148 concluída; branch a partir de `codex/p148-lean4-kernel-certification-identities`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P148 concluída com identidades paramétricas de Schinzel certificadas no kernel Lean 4.
**Branch:** `codex/p149-extremal-finite-constructive-certificates`.

## Hipótese, objetivo e escopo

Aprofundar a síntese de certificados construtivos explícitos em combinatória finita onde instâncias discretas podem ser descobertas via busca massiva e provadas formalmente sem margem para contra-exemplos. Focar em: (1) conjuntos de Sidon $B_2[1]$ densos de tamanho máximo para intervalos finitos $N \le 2000$ que igualem ou superem os limites conhecidos de Bose–Chowla/Mian–Chowla; e (2) colorações euclidianas livres de conflito ou grafos unitários com altos números cromáticos locais. Formalizar os certificados e suas provas de não-colisão de diferenças em `lean_proofs/Generated/ExtremalConstructiveCertificates.lean`.

Alterações permitidas: `docs/phases/P149-extremal-finite-constructive-certificates.md`, `lean_proofs/`, `src/evobyte/additive.py`, `src/evobyte/discrete_geometry.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p149-config.json`, `experiments/p149-run.sh`.
Fora do escopo: alegações assintóticas universais sem demonstração formal; uso de números flutuantes sem precisão exata.

Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar busca por algoritmos combinatórios exatos (branch-and-bound vetorial em GPU/CPU) para conjuntos de Sidon finitos ótimos e grafos de distância unitária em `src/evobyte/additive.py`.
2. Formalizar no Lean 4 a verificação exata e computável via tática `decide` / `norm_num` dos certificados construtivos em `lean_proofs/Generated/ExtremalConstructiveCertificates.lean`.
3. Adicionar interface de auditoria P149 em `benchmarks/science_matrix.py` (`run_p149_constructive_certificates_audit`).

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry` e auditoria P149 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P149 --config experiments/p149-config.json --output /tmp/evobyte-p149-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p149 extremal finite constructive certificates"
git push -u origin HEAD
gh pr create --base codex/p148-lean4-kernel-certification-identities --title "feat(formal): implement p149 extremal finite constructive certificates" --body-file /tmp/evobyte-p149-pr.md
```
