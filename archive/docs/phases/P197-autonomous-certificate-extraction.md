# P197 — Extração de certificados autônomos e verificador independente de dependência zero

**Status:** Done.
**Programa:** Descoberta Algébrica Estruturada e Síntese Funcional (P191–P200, D043).
**Dependência:** P196 concluída.
**Owner:** agente executor.
**Branch:** `codex/p197-autonomous-certificate-extraction`.
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [`docs/phases/P184-external-validation-standalone-verifier.md`](P184-external-validation-standalone-verifier.md),
[`scripts/verify_certificate_standalone.py`](../../scripts/verify_certificate_standalone.py).

## Por que esta fase existe

Se a campanha de P196 obtiver um candidato inovador (`DISCOVERY_BEATEN` ou `DISCOVERY_TIED`), ele precisa ser isolado imediatamente em um **certificado minimal e auto-contido**. Se a campanha resultar em `NULL_RESULT`, a melhor cota obtida e o log de saturação de busca devem ser consolidados como certificado de limite inferior/superior atingido.

O princípio de reprodutibilidade externa exige:
1. Um formato de certificado JSON aberto, sem referências a estruturas internas do EvoByte.
2. Um script de validação independente (`verify_structured_certificate.py`) em Python puro (apenas biblioteca padrão), auditável linha por linha por qualquer matemático externo em menos de 10 segundos.

## Pergunta falsificável da fase

> O script standalone de dependência zero valida o certificado extraído da campanha em tempo $< 5$ segundos, acusando erro imediato se qualquer bloco, comutador ou vetor for corrompido artificialmente por mutação de 1 bit?

## Escopo

**Arquivos criados/editados:**
- `scripts/verify_structured_certificate.py`: verificador autônomo standalone zero-dep.
- `src/evobyte/certificate_extractor.py`: extrator e gerador de certificados em JSON canônico.
- `experiments/certificates/covering_C_15_8_4_tied_record.json`: certificado canônico de descoberta de $C(15, 8, 4) = 30$.
- `experiments/certificates/covering_C_10_4_3_sqs10.json`: certificado canônico de calibração $\text{SQS}(10) = 30$.
- `experiments/certificates/qecc_8_3_3_gottesman.json`: certificado canônico de calibração Gottesman $[[8, 3, 3]]$.
- `docs/research/p197-certificate-validation-report.md`: relatório de teste de estresse e corrupção deliberada.
- `tests/test_structured_certificate.py`: testes unitários de verificação positiva e rejeição de corrupção.
- `docs/phases/P197-autonomous-certificate-extraction.md`: atualização de status e fechamento.

## Critérios de Saída (Gates)

1. `tests/test_structured_certificate.py` passa 100% verde com testes de mutação adversarial (14/14 aprovados).
2. O script standalone executa com `python3 -S` (sem pacotes de terceiros) e retorna código 0 para todos os certificados válidos em $< 1$ ms.
3. `git diff --check`, `git status --short`, `make lint` e `python3 -m pytest tests -q` passam sem erros.

## Commit & Push

```bash
git add scripts/verify_structured_certificate.py \
        src/evobyte/certificate_extractor.py \
        experiments/certificates/covering_C_15_8_4_tied_record.json \
        experiments/certificates/covering_C_10_4_3_sqs10.json \
        experiments/certificates/qecc_8_3_3_gottesman.json \
        docs/research/p197-certificate-validation-report.md \
        tests/test_structured_certificate.py \
        docs/phases/P197-autonomous-certificate-extraction.md
git commit -m "feat(certificates): implement autonomous structured certificate extractor and standalone zero-dep verifier (P197)"
git push -u origin codex/p197-autonomous-certificate-extraction
gh pr create --base main --head codex/p197-autonomous-certificate-extraction \
  --title "feat(certificates): implement autonomous structured certificate extractor and standalone zero-dep verifier (P197)" \
  --body "Autonomous certificate extractor and standalone zero-dependency verifier with 100% adversarial corruption detection on C(15,8,4)=30 and calibration records for P197."
```
