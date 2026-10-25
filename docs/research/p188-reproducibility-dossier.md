# P188 — Dossiê de Reprodutibilidade e Container Hermético

**Programa:** Descoberta na Fronteira (*P171–P190, D042*). Trilhas A, B e fundação comum.
**Fase:** P188 — Pacote Zenodo Arquivável e Container Hermético de Reprodução.
**Data:** 2026-10-25.
**Manifesto Top-Level:** [`dist/zenodo-bundle-frontier/final-manifest-sha256.json`](../../dist/zenodo-bundle-frontier/final-manifest-sha256.json).
**Status da Hermeticidade:** `VERIFIED_HERMETIC` (executado e auditado sem rede).

---

## 1. Contexto e Pergunta Falsificável

A fase **P188** consolida a reprodutibilidade pública do programa de Descoberta na Fronteira através de dois pilares complementares e independentes:

> **Pergunta Falsificável:**
> *Um terceiro, com apenas o tarball e o Dockerfile, reproduz a verificação completa (verificadores sobre certificados + suíte rápida de testes) sem rede, e o manifesto SHA-256 valida 100% dos arquivos?*

---

## 2. Métricas do Pacote Zenodo Exportado

O pacote arquivável foi gerado pelo utilitário [`scripts/export_zenodo_bundle.py`](../../scripts/export_zenodo_bundle.py):

- **Diretório de Exportação:** `dist/zenodo-bundle-frontier/evobyte-research-bundle`
- **Arquivo Tarball:** `dist/zenodo-bundle-frontier/evobyte-zenodo-bundle.tar.gz`
- **Total de Arquivos Coletados:** 646 arquivos
- **Tamanho Total Descompactado:** 8,11 MB (8.506.000+ bytes)
- **Tamanho do Tarball Comprimido:** ~1,85 MB
- **Integridade Mecânica:** 100% de correspondência nos hashes SHA-256 (`verify_zenodo_bundle_integrity` retornou zero achados).

### Cadeia de Custódia e Coleta:
O pacote abrange integralmente:
1. **Especificações de Fases:** P150–P190 (`docs/phases/P*.md`).
2. **Catálogos de Fronteira:** `frontier_targets_v2.json`, `frontier_sources_v2.json`, `qecc_frontier_v1.json`.
3. **Resultados e Checkpoints de Campanhas:** P172, P174, P175, P176, P177, P182, P186, P187.
4. **Verificadores e Certificados Externos:** `verify_frontier_certificate.py` e os 5 certificados de calibração em `dist/external-validation/`.
5. **Módulos Formais Lean 4:** `lean_proofs/Generated/FrontierDiscoveryCertificates.lean` e `docs/research/lean-fidelity-reviews.json`.
6. **Código-Fonte Completo:** Todos os módulos em `src/evobyte/` e benchmarks em `benchmarks/`.

---

## 3. Evidência Experimental do Container Hermético (`--network none`)

A reprodutibilidade sem rede foi validada executando a suíte de testes de fronteira e os verificadores autônomos dentro do container com egress de rede totalmente desativado:

- **Imagem Docker:** `evobyte-frontier-repro:p188`
- **Hash SHA-256 da Imagem:** `sha256:71b9d66c7335c09bc1375d7973a17cfe3b088c99c870e0e786392bce4de86865`
- **Isolamento de Rede:** Flag mandatória `--network none`
- **Comando de Verificação Executado:**
  ```bash
  docker run --rm --network none evobyte-frontier-repro:p188 bash -c \
    "python3 -m pytest tests/test_frontier_catalogue.py tests/test_qecc_verifier.py -q -m 'not slow' && \
     python3 scripts/verify_frontier_certificate.py dist/external-validation/frontier_sample_covering.json && \
     python3 scripts/verify_frontier_certificate.py dist/external-validation/frontier_sample_weak_schur.json && \
     python3 scripts/verify_frontier_certificate.py dist/external-validation/frontier_sample_qecc_stabilizer.json && \
     echo 'HERMETIC_VERIFICATION_PASSED'"
  ```

### Log de Saída do Container Hermético:
```text
.................                                                        [100%]
[*] Certificate target: fano_plane_c7_3_2 (Type: covering)
[*] File SHA-256: 07bfba962b113f04a3e10b5f2051f1b80bea8dad45169159c3e2035110bb2aec
[SUCCESS] VERIFIED: all 21 2-subsets of 1..7 covered by 7 blocks
[*] Certificate target: weak_schur_k2_n8 (Type: weak_schur)
[*] File SHA-256: 89e2747ecc89d2e25bbd31c5e0e82e7c66f9762e0fe597222d4b8af24cb21685
[SUCCESS] VERIFIED: valid weak sum-free partition of 1..8 into 2 classes
[*] Certificate target: qecc_steane_7_1_3 (Type: qecc_stabilizer)
[*] File SHA-256: 599d4207dc1b0326cf363f3f53e86a60e97ecef309797aeaa7b629058771537c
[SUCCESS] VERIFIED: valid quantum stabilizer code [[7,1,3]]
HERMETIC_VERIFICATION_PASSED
```

---

## 4. Instruções de Reprodução por Terceiros em 3 Passos

Para qualquer pesquisador externo auditar o trabalho de forma 100% independente:

```bash
# Passo 1: Extrair o pacote arquivado ou clonar o repositório
tar -xzf evobyte-zenodo-bundle.tar.gz && cd evobyte-zenodo-bundle

# Passo 2: Construir a imagem local hermética
docker build -t evobyte-repro .

# Passo 3: Executar a verificação completa com rede estritamente desativada
docker run --rm --network none evobyte-repro bash -c \
  "python3 -m pytest tests/test_frontier_catalogue.py tests/test_qecc_verifier.py -q && \
   python3 scripts/verify_frontier_certificate.py dist/external-validation/frontier_sample_covering.json"
```

---

## 5. Limitações e Próximos Passos

- **Manuscrito P189:** Os dados deste pacote cobrem as fases P171 a P188. O manuscrito consolidado de síntese científica será redigido na fase P189 (`docs/phases/P189-frontier-discovery-manuscript.md`). Após a compilação do PDF final, o pacote será atualizado para o depósito oficial definitivo.
- **Isolamento de GPU:** O container de reprodução hermética utiliza execução CPU determinística para portabilidade universal em qualquer nó Linux x86_64 padrão.
