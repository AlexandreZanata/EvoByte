# P208 — Certificação formal no kernel Lean 4 (Formal Verification Gate)

**Status:** Proposed.
**Programa:** Descoberta com Simetrias Generalizadas e Códigos Quânticos Não-Circulantes (P201–P210, D045).
**Dependência:** P207 concluída e integrada em `main`.
**Owner:** agente executor.
**Branch:** `codex/p208-lean4-kernel-formal-certification` (a partir de `main`).
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [`docs/phases/P198-lean4-kernel-formal-certification.md`](P198-lean4-kernel-formal-certification.md),
[`lean_proofs/Generated/StructuredDiscovery.lean`](../../lean_proofs/Generated/StructuredDiscovery.lean).

## Por que esta fase existe

A confiança científica definitiva em construções discretas e cotas estruturais atinge seu ápice quando o assistente de provas formais Lean 4 verifica e aceita cada proposição no seu micronúcleo (kernel).
Esta fase formaliza e prova no Lean 4:
1. **Teoremas de Cobertura Afim e Diédrica:** Prova exata de que os blocos-base gerados cobrem todas as sub-tuplas requeridas em $\mathbb{N}$, sem axiomas customizados e com zero tokens `sorry`.
2. **Teoremas de Comutatividade Simplética e Distância Quântica Não-Circulante:** Prova formal de que as matrizes de paridade quase-cíclicas comutam no produto simplético ($H_X H_Z^T \equiv 0 \pmod 2$) e que a distância é estritamente $d \ge d_{certified}$.
3. **Revisão Humana de Fidelidade Matemática:** Auditoria e congelamento de enunciados garantindo ausência de premissas contraditórias (`False \to P`) ou tautologias numéricas triviais.

## Pergunta falsificável da fase

> Todos os teoremas correspondentes aos certificados válidos da P207 compilam no kernel do Lean 4 via `lake build` com zero tokens `sorry`, utilizando estritamente os axiomas padrão da teoria de tipos (`propext`, `Classical.choice`, `Quot.sound`)?

## Escopo

**Arquivos a criar/editar:**
- `lean_proofs/Generated/GeneralizedDiscovery.lean`: definições e teoremas formais provados no kernel Lean 4.
- `lean_proofs/Generated.lean`: exportação dos novos módulos formais.
- `docs/research/p208-lean-formal-certification-report.md`: relatório de compilação, axiomas utilizados e revisão de fidelidade.
- `tests/test_lean_p208.py`: teste Python que audita a árvore Lean 4, garantindo ausência de `sorry` e contagem exata de teoremas.
- `docs/phases/P208-lean4-kernel-formal-certification.md`: atualização de status e evidências.

## Critérios de Saída (Gates)

1. `lake build` compila sem erros ou avisos na pasta `lean_proofs/`.
2. `tests/test_lean_p208.py` passa 100% verde com contagem formal de teoremas provados e zero `sorry`.
3. `git diff --check`, `git status --short`, `make lint` e `python3 -m pytest tests -q` passam sem erros.

## Commit & Push

```bash
git add lean_proofs/Generated/GeneralizedDiscovery.lean \
  lean_proofs/Generated.lean \
  docs/research/p208-lean-formal-certification-report.md \
  tests/test_lean_p208.py \
  docs/phases/P208-lean4-kernel-formal-certification.md
git commit -m "feat(formal): certify generalized discovery and non-circulant bounds in Lean 4 (P208)"
git push -u origin codex/p208-lean4-kernel-formal-certification
gh pr create --base main \
  --title "feat(formal): certify generalized discovery and non-circulant bounds in Lean 4 (P208)" \
  --body "Certifica teoremas no kernel Lean 4 com zero sorry sob D045."
```
