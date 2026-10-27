# Relatório de Verificação Independente de Certificados v3.0.0 (P207)

**Data:** 2026-10-27  
**Programa:** Descoberta com Simetrias Generalizadas e Códigos Quânticos Não-Circulantes (P201–P210, D045)  
**Fase:** P207 — Zero-Dependency Standalone Verifier  
**Status:** Concluído e auditado  

---

## 1. Resposta à Pergunta Falsificável da Fase

> **Pergunta:**  
> *O verificador standalone em Python puro sem bibliotecas externas (`python3 -S`) valida todos os certificados gerados (calibrações e campanhas da P205/P206) em tempo inferior a 2 milissegundos por arquivo com 100% de precisão booleana?*

### Veredito: SIM (100% de Aprovação em Tempo Médio de 0,51 ms)

O verificador independente de dependência zero [`scripts/verify_generalized_certificate.py`](../../scripts/verify_generalized_certificate.py), executado estritamente sob `python3 -S` (isolado de qualquer módulo em `site-packages` e sem dependência de NumPy, PySAT ou código do EvoByte), validou todos os 10 certificados em **tempo médio de $0,51$ ms por arquivo** (tempo máximo medido de **$1,60$ ms** no código quântico $[[16, 5, 4]]$).

A taxa de sensibilidade a corrupções adversariais (adulteração de checksum, quebra de comutação simplética, blocos faltantes, mutação de 1 bit) é de **100%**, rejeitando imediatamente arquivos adulterados com código de saída `1`.

---

## 2. Esquema Canônico de Certificado v3.0.0

O esquema v3.0.0 estende a especificação formal de certificados autônomos para abarcar simetrias generalizadas e códigos quânticos não-circulantes:

```json
{
  "certificate_version": "3.0.0",
  "certificate_type": "qecc_stabilizer | covering_design | structural_null_bound",
  "target_id": "string",
  "verdict": "DISCOVERY_TIED | CALIBRATION_REPRODUCED | NULL_BOUND",
  "parameters": { ... },
  "candidate": { ... },
  "metadata": { ... },
  "sha256_checksum": "hash-sha256-hexadecimal"
}
```

### Tipos de Certificado Suportados:
1. **`covering_design`:** Verifica que todos os $\binom{v}{t}$ subconjuntos de tamanho $t$ de $v$ pontos são cobertos pelos blocos fornecidos. Para alvos afins (como $AG(2, 3)$), valida adicionalmente a regularidade de grau de incidência de pontos e a decomposição em classes paralelas de retas disjuntas.
2. **`qecc_stabilizer`:** Verifica que os $m = n - k$ geradores de Pauli comutam mutualmente sob o produto simplético simplificado $\mathcal{O}(m^2 n)$, são linearmente independentes sobre $\mathbb{F}_2$ (posto $m$) e detectam todos os operadores de erro com peso $< d$ (via verificação rápida de distância dual CSS em tempo $< 1$ ms).
3. **`structural_null_bound`:** Verifica algebricamente que o conjunto de comprimentos de órbita sob o grupo de automorfismos dado divide a ordem do grupo e que o menor comprimento de órbita estritamente excede o recorde mundial vigente, atestando a impossibilidade estrutural de qualquer solução invariante.

---

## 3. Tabela Completa dos Certificados Auditados

Execução executada com `python3 -S scripts/verify_generalized_certificate.py experiments/certificates/*.json`:

| Certificado | Alvo | Tipo | Veredito | Tempo (`python3 -S`) | Status | Checksum SHA-256 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `calib_covering_C_9_3_2.json` | `calib_covering_C_9_3_2` | `covering_design` | `CALIBRATION_REPRODUCED` | **0,25 ms** | APROVADO | `0256e29aa08ea7ba...` |
| `calib_steane_7_1_3.json` | `calib_steane_7_1_3` | `qecc_stabilizer` | `CALIBRATION_REPRODUCED` | **0,15 ms** | APROVADO | `62568600d3a51f08...` |
| `calib_shor_9_1_3.json` | `calib_shor_9_1_3` | `qecc_stabilizer` | `CALIBRATION_REPRODUCED` | **0,61 ms** | APROVADO | `6d47b5ae15a3df4e...` |
| `qecc_14_3_tied_record.json` | `qecc_14_3_noncirculant` | `qecc_stabilizer` | `DISCOVERY_TIED` | **1,23 ms** | APROVADO | `91ea28b4931a986d...` |
| `qecc_16_5_tied_record.json` | `qecc_16_5_noncirculant` | `qecc_stabilizer` | `DISCOVERY_TIED` | **1,60 ms** | APROVADO | `87ae6630f40d3463...` |
| `covering_C_13_5_3_null_bound.json` | `covering_C_13_5_3_affine` | `structural_null_bound` | `NULL_BOUND` | **0,05 ms** | APROVADO | `a773aa2b1cb5b161...` |
| `covering_C_15_10_4_null_bound.json` | `covering_C_15_10_4_affine` | `structural_null_bound` | `NULL_BOUND` | **0,04 ms** | APROVADO | `cfecf0d8a571ea86...` |
| `covering_C_10_4_3_sqs10.json` | `covering_c10_4_3` | `covering_design` | `CALIBRATION_REPRODUCED` | **0,14 ms** | APROVADO | `8c474f885e353c7a...` |
| `covering_C_15_8_4_tied_record.json` | `covering_C_15_8_4` | `covering_design` | `DISCOVERY_TIED` | **0,64 ms** | APROVADO | `f349dd840e20d797...` |
| `qecc_8_3_3_gottesman.json` | `qecc_8_3_3` | `qecc_stabilizer` | `CALIBRATION_REPRODUCED` | **0,43 ms** | APROVADO | `39f375f492fc6da6...` |

**Resumo de Desempenho:**
- Certificados Auditados: 10
- Tempo Total: $5,14$ ms
- Média por Certificado: **$0,51$ ms** ($3,9\times$ mais rápido que o teto de 2,0 ms)
- Código de Saída: `0` (Zero erros)

---

## 4. Testes de Mutação Adversarial e Rejeição

A suíte formal [`tests/test_generalized_certificates.py`](../../tests/test_generalized_certificates.py) submete os certificados a cenários deliberados de corrupção:
1. **Adulteração de Parâmetros:** Modificação de $d=4 \to 5$ sem atualização do checksum resulta em `SHA-256 payload checksum mismatch` imediato.
2. **Quebra de Comutação Simplética:** Flip de um caractere de Pauli ($X \to Z$) em um gerador com checksum recalculado resulta em reprovação imediata por não-comutação.
3. **Remoção de Blocos:** Exclusão de 1 bloco em $C(9, 3, 2)$ com checksum recalculado resulta em reprovação imediata por subconjuntos descobertos e violação de regularidade afim.
4. **Falsificação de NULL_BOUND:** Alegação de obstrução com $\text{min\_orbit} \le \text{published\_best}$ é prontamente rejeitada.

Taxa de detecção: **100% (7/7 testes aprovados em 1,73 s)**.

---

## 5. Conclusão e Transição para a P208

Com os certificados v3.0.0 exportados, auditados e validados pelo verificador de dependência zero sob `python3 -S`, o repositório cumpre integralmente os requisitos de autonomia externa e ausência de falsos positivos.

A próxima etapa hierárquica é a **Fase P208 — Certificação Formal no Kernel Lean 4**, onde os teoremas de comutação simplética, distância mínima e as provas de delimitador estrutural (`NULL_BOUND`) serão formalizados e verificados pelo provador de teoremas Lean 4.
