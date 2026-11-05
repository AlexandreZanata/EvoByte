# P207 — Extração de certificados autônomos v3.0.0 e verificador independente de dependência zero (Zero-Dependency Standalone Verifier)

**Status:** Concluída (2026-10-27).
**Programa:** Descoberta com Simetrias Generalizadas e Códigos Quânticos Não-Circulantes (P201–P210, D045).
**Dependência:** P206 concluída e integrada em `main`.
**Owner:** agente executor.
**Branch:** `codex/p207-v3-certificates-and-standalone-verifier` (a partir de `main`).
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [`docs/phases/P197-autonomous-certificate-extraction.md`](P197-autonomous-certificate-extraction.md),
[`scripts/verify_structured_certificate.py`](../../scripts/verify_structured_certificate.py).

## Por que esta fase existe

Todo resultado matemático e computacional produzido pelo EvoByte deve ser independente do software proprietário ou do repositório completo para ser verificado por terceiros.
Esta fase entrega:
1. **Esquema de Certificado Canônico v3.0.0:** Extensão do formato JSON formal para incorporar blocos sob grupos afins $\text{AGL}(1, q)$, representações bicirculantes e matrizes de estabilizadores quânticos quase-cíclicos, acompanhados de hashes criptográficos SHA-256 encadeados.
2. **Verificador Standalone de Dependência Zero (`scripts/verify_generalized_certificate.py`):** Script escrito em Python 3 puro utilizando unicamente módulos da biblioteca padrão (`sys`, `json`, `hashlib`, `math`), executável com `python3 -S` em tempo inferior a 2 milissegundos por certificado.

## Pergunta falsificável da fase

> O verificador standalone em Python puro sem bibliotecas externas (`python3 -S`) valida todos os certificados gerados (calibrações e campanhas da P205/P206) em tempo inferior a 2 milissegundos por arquivo com 100% de precisão booleana?

**Resposta:** SIM. O verificador standalone em Python puro (`python3 -S`) validou todos os 10 certificados em tempo médio de 0,51 ms por arquivo (tempo máximo de 1,60 ms no código $[[16, 5, 4]]$), muito abaixo do teto de 2,0 ms, com código de saída 0 e 100% de precisão booleana e detecção de corrupção adversarial.

## Escopo Realizado

**Arquivos criados/editados:**
- `src/evobyte/generalized_certificate_extractor.py`: extrator canônico de certificados JSON v3.0.0.
- `scripts/verify_generalized_certificate.py`: verificador autônomo de dependência zero em Python puro.
- `experiments/certificates/`: 7 novos certificados canônicos exportados (`calib_covering_C_9_3_2.json`, `calib_steane_7_1_3.json`, `calib_shor_9_1_3.json`, `qecc_14_3_tied_record.json`, `qecc_16_5_tied_record.json`, `covering_C_13_5_3_null_bound.json`, `covering_C_15_10_4_null_bound.json`).
- `docs/research/p207-standalone-verification-report.md`: relatório com tempos medidos de verificação e hashes SHA-256.
- `tests/test_generalized_certificates.py`: suíte formal de testes do verificador autônomo (7/7 verdes).
- `docs/phases/P207-v3-certificates-and-standalone-verifier.md`: atualização de status e evidências.

## Critérios de Saída (Gates)

1. `tests/test_generalized_certificates.py` passa 100% verde — Aprovado (7/7 testes em 1,73 s).
2. `python3 -S scripts/verify_generalized_certificate.py experiments/certificates/*.json` valida com código de saída 0 e tempo $< 2$\,ms por certificado — Aprovado (0,51 ms médio, 1,60 ms máximo).
3. `git diff --check`, `git status --short`, `make lint` e `python3 -m pytest tests -q` passam sem erros — Aprovado.

## Commit & Push

```bash
git add src/evobyte/generalized_certificate_extractor.py \
  scripts/verify_generalized_certificate.py \
  experiments/certificates/ \
  docs/research/p207-standalone-verification-report.md \
  tests/test_generalized_certificates.py \
  docs/phases/P207-v3-certificates-and-standalone-verifier.md
git commit -m "feat(certificates): autonomous v3 certificates and verifier (P207)"
git push -u origin codex/p207-v3-certificates-and-standalone-verifier
gh pr create --base main \
  --title "feat(certificates): implement autonomous v3 certificate extractor and zero-dep verifier (P207)" \
  --body "Entrega extrator de certificados v3.0.0 e verificador independente sob D045."
```
