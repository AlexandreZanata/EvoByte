# P197 — Extração de certificados autônomos e verificador independente de dependência zero

**Status:** Proposed.
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

**Arquivos a criar/editar:**
- `scripts/verify_structured_certificate.py`: verificador autônomo standalone zero-dep.
- `src/evobyte/certificate_extractor.py`: extrator e gerador de certificados em JSON canônico.
- `docs/research/p197-certificate-validation-report.md`: relatório de teste de estresse e corrupção deliberada.
- `tests/test_structured_certificate.py`: testes unitários de verificação positiva e rejeição de corrupção.

## Critérios de Saída (Gates)

1. `tests/test_structured_certificate.py` passa 100% verde com testes de mutação adversarial.
2. O script standalone executa com `python3 -S` (sem pacotes de terceiros) e retorna código 0 para o certificado válido.
3. `git diff --check`, `git status --short`, `make lint` e `python3 -m pytest tests -q` passam sem erros.
