# Revisão de código R1 — contrato de decisões P58 (2026-10-07)

- Alvo: commit `57c6c88` (`feat(research): implement p58 R1 decision contract`).
- Revisor: Alexandre, por delegação expressa (D019, 2026-10-06).
  Execução desta revisão: agente executor (identificado; não é autoria
  independente nem certificação científica).
- Escopo revisado: `_validate_p58_decisions` e `_validate_p58_code_review`
  em `benchmarks/science_matrix.py`, integração ao
  `run_p58_acceptance_baseline_audit` e testes R1 em `tests/test_science.py`.

## Conferido

- Seis IDs exatos exigidos, sem ausência/duplicata/inesperado.
- Campos obrigatórios por decisão (responsável, executor, data, escopo,
  justificativa, origem da autorização, revisão examinada, caminho/hash da
  evidência, disposição, usos permitidos/proibidos).
- Disposições restritas ao conjunto
  `reference_only/excluded_from_claims/approved_for_current_use`;
  `approved_for_current_use` exige aprovação científica
  `approved/not_required` e `allowed_uses` não-vazio; restrição exige
  `prohibited_uses` não-vazio; interseção permitido/proibido bloqueia.
- Evidência: existência do arquivo + igualdade de sha256; `rejected` no
  escopo atual bloqueia; data validada como AAAA-MM-DD.
- Revisão de código: exige `status=accepted`, revisor e registro
  identificável (`review_id/record/pr/commit`).
- Checker matemático exato inalterado; nenhuma flag virou `approved` como
  atalho (config de produção seguiu sem decisões).
- Regressões preservadas: fonte suja, raw ausente, selo quebrado,
  certificado inválido, recuperação.

## Limitações registradas (não bloqueantes para a base técnica)

- O relatório trunca `findings` em 12 itens; os achados completos de
  decisões/revisão seguem nos campos `decisions_findings` e
  `code_review_findings`.
- Valores de `scientific_approval` fora de `approved/not_required`
  bloqueiam o uso `approved_for_current_use` (falha segura por padrão).
- Caminhos de evidência absolutos são aceitos (usados pelos testes); em
  produção, preferir caminhos relativos à raiz do repo.

## Veredito

`accepted` para o uso na base técnica P58. Esta revisão não certifica
limiares, revisão prévia, independência, ganho ou descoberta de nenhum
resultado histórico.
