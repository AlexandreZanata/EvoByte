# P218 — Certificação formal no kernel Lean 4 (Formal Verification Gate)

**Status:** Proposed.
**Programa:** Descoberta com Códigos Quânticos Bicíclicos Bivariados e Geometrias Projetivas (P211–P220, D047).
**Dependência:** P217 concluída e integrada em `main`.
**Owner:** agente executor; autor correspondente humano revisa a fidelidade das definições formais.
**Branch:** `codex/p218-lean4-kernel-formal-certification` (a partir de `main`).
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [`docs/phases/P208-lean4-kernel-formal-certification.md`](P208-lean4-kernel-formal-certification.md),
[`formal/lean/EvoByte/GeneralizedDiscovery.lean`](../../formal/lean/EvoByte/GeneralizedDiscovery.lean).

## Por que esta fase existe

O padrão de prova matemática do EvoByte exige que toda alegação de descoberta (`DISCOVERY_TIED` ou `DISCOVERY_BROKEN`) e toda cota negativa (`NULL_BOUND`) seja formalizada e checada pelo kernel do assistente de provas Lean 4:
1. **Zero Tokens Desonestos:** Proibição estrita de tokens `sorry`, `axiom` não-padrão ou gaps de prova.
2. **Fidelidade Semântica:** Auditoria formal garantindo que os teoremas Lean expressam fielmente comutatividade simplética de matrizes sobre $\mathbb{F}_2$, cardinalidade de blocos em coverings ou cotas combinatórias exatas.
3. **Reproducibilidade Offline:** Validação estrita via script de verificação Lean (`scripts/verify_lean_p218.sh`) checando tipos e axiomas.

## Pergunta falsificável da fase

> O kernel do Lean 4 compila e aceita formalmente 100% dos teoremas da campanha bivariada e projetiva com zero `sorry`, dependendo exclusivamente dos axiomas padrão do Lean 4 (`propext`, `Classical.choice`, `Quot.sound`), sem timeouts ou axiomas ad-hoc?

## Escopo

**Arquivos a criar/editar:**
- `formal/lean/EvoByte/BivariateDiscovery.lean`: formalização Lean 4 dos teoremas do programa D047.
- `lean_proofs/Generated/BivariateDiscovery.lean`: arquivo de provas compilável via `lake build`.
- `scripts/verify_lean_p218.sh`: script de auditoria de axiomas e ausência de `sorry`.
- `docs/research/p218-lean-formal-certification-report.md`: relatório de checagem do kernel.
- `tests/test_lean_p218.py`: suíte de testes de integração com o Lean 4.
- `docs/phases/P218-lean4-kernel-formal-certification.md`: atualização de status e evidências.

## Critérios de Saída (Gates)

1. `tests/test_lean_p218.py` passa 100% verde validando a integridade formal.
2. `scripts/verify_lean_p218.sh` confirma zero ocorrências de `sorry` e dependência estrita de axiomas padrão.
3. `git diff --check`, `git status --short`, `make lint` e `python3 -m pytest tests -q` passam sem erros.

## Commit & Push

```bash
git add formal/lean/EvoByte/BivariateDiscovery.lean \
  lean_proofs/Generated/BivariateDiscovery.lean \
  scripts/verify_lean_p218.sh \
  docs/research/p218-lean-formal-certification-report.md \
  tests/test_lean_p218.py \
  docs/phases/P218-lean4-kernel-formal-certification.md
git commit -m "feat(formal): certify bivariate discovery in Lean 4 (P218)"
git push -u origin codex/p218-lean4-kernel-formal-certification
gh pr create --base main \
  --title "feat(formal): certify bivariate discovery in Lean 4 (P218)" \
  --body "Certifica formalmente teoremas do programa D047 no Lean 4."
```
