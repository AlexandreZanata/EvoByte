# P217 — Extração de certificados autônomos v4.0.0 e verificador independente de dependência zero

**Status:** Proposed.
**Programa:** Descoberta com Códigos Quânticos Bicíclicos Bivariados e Geometrias Projetivas (P211–P220, D047).
**Dependência:** P216 concluída e integrada em `main`.
**Owner:** agente executor.
**Branch:** `codex/p217-v4-certificates-and-standalone-verifier` (a partir de `main`).
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [`docs/phases/P207-v3-certificates-and-standalone-verifier.md`](P207-v3-certificates-and-standalone-verifier.md),
[`scripts/verify_generalized_certificate.py`](../../scripts/verify_generalized_certificate.py).

## Por que esta fase existe

Os resultados obtidos na campanha P216 devem ser exportados em formato canônico padronizado para auditoria por qualquer pesquisador ou sistema externo, sem requerer instalação de frameworks pesados:
1. **Certificados Canônicos v4.0.0:** JSON autocontido com esquema formal, metadados de proveniência (hash Git, seed, timestamp), matrizes geradoras esparsas em coordenadas (COO), parâmetros $[[n, k, d]]$ ou $(v, k, t)$, digest SHA-256 e assinatura estruturada.
2. **Verificador Standalone de Dependência Zero:** Script Python puro de biblioteca padrão (`scripts/verify_bivariate_certificate.py`) executando em $< 2.0$ ms por certificado, validando comutatividade simplética ($H_X H_Z^T = 0 \pmod 2$), posto binário em $\mathbb{F}_2$ via eliminação gaussiana e distância mínima ou cobertura combinatória.

## Pergunta falsificável da fase

> O script independente de dependência zero valida 100% dos certificados v4.0.0 gerados pela P216 e rejeita 100% das mutações adversariais sintéticas (bit flips em matrizes ou distâncias alteradas) em tempo médio $< 2$ ms por verificação?

## Escopo

**Arquivos a criar/editar:**
- `experiments/certificates/v4/`: diretório de certificados v4.0.0 canônicos gerados na P216.
- `scripts/verify_bivariate_certificate.py`: verificador standalone em Python puro sem NumPy, PyTorch ou dependências externas.
- `docs/research/p217-v4-certificates-report.md`: relatório formal de integridade dos certificados e medições de tempo.
- `tests/test_verify_bivariate_certificate.py`: testes automatizados de aceitação de certificados legítimos e rejeição de adulterações adversariais.
- `docs/phases/P217-v4-certificates-and-standalone-verifier.md`: atualização de status e evidências.

## Critérios de Saída (Gates)

1. `tests/test_verify_bivariate_certificate.py` passa 100% verde com 0 falso-positivos e 0 falso-negativos em mutações adversariais.
2. Tempo de execução de `scripts/verify_bivariate_certificate.py` inferior a 2.0 ms por certificado auditado.
3. `git diff --check`, `git status --short`, `make lint` e `python3 -m pytest tests -q` passam sem erros.

## Commit & Push

```bash
git add experiments/certificates/v4/ \
  scripts/verify_bivariate_certificate.py \
  docs/research/p217-v4-certificates-report.md \
  tests/test_verify_bivariate_certificate.py \
  docs/phases/P217-v4-certificates-and-standalone-verifier.md
git commit -m "feat(certificates): autonomous v4 certificates and standalone verifier (P217)"
git push -u origin codex/p217-v4-certificates-and-standalone-verifier
gh pr create --base main \
  --title "feat(certificates): autonomous v4 certificates and standalone verifier (P217)" \
  --body "Entrega certificados v4.0.0 e verificador de dependência zero sob D047."
```
