# P199 — Relatório de Auditoria na Literatura Mundial e Dossiê para Curadores

**Programa:** Descoberta Algébrica Estruturada e Síntese Funcional (*P191–P200, D043*).  
**Fase:** P199 — Auditoria de novidade na literatura mundial e dossiê para curadores.  
**Data:** 2026-10-26.  
**Branch:** `codex/p199-world-literature-audit-curator-dossier`.  
**Auditoria de Novidade:** [`experiments/p199-novelty-audit.json`](../../experiments/p199-novelty-audit.json).  
**Índice Rastreado:** [`docs/research/p199-curator-packages-index.json`](p199-curator-packages-index.json).  
**Diretório de Pacotes:** `dist/curator-submissions/p199/`.  
**Status de Submissão:** `pending_human_submission`.  

---

## 1. Declaração Mandatória de Custódia Humana e Não-Submissão Autônoma

> **Protocolo de Integridade Científica:**
> 1. O agente autônomo **nunca** submete dados, e-mails, issues ou mensagens a curadores externos.
> 2. Todas as comunicações geradas permanecem estritamente no repositório com o status `pending_human_submission`.
> 3. Qualquer contato com curadores (Dan Gordon, Markus Grassl, Neil Sloane / OEIS Editorial Board) é de inteira responsabilidade e custódia manual do autor correspondente humano (**Alexandre Zanata**).
> 4. Nenhum endereço de e-mail privado de terceiros é embutido no código, cartas ou metadados versionados.

---

## 2. Auditoria Independente de Novidade em Duas Camadas

### Camada 1: Verificação Cruzada contra Literatura e Bases Mundiais Indexadas

A auditoria cobriu tanto os alvos primários da campanha exploratória quanto os alvos de calibração exata, mapeando os limites conhecidos na literatura:

| Alvo / Domínio | Referência Canônica | Melhor Cota Mundial Conhecida | Resultado EvoByte | Veredito de Novidade |
|---|---|---|---|---|
| **$C(15, 8, 4)$** | LJCR (Gordon, 1996) | $30$ blocos | $30$ blocos ($2$ blocos-base sob $Z_{15}$) | `DISCOVERY_TIED` (Realização cíclica alternativa) |
| **$C(10, 4, 3)$** | SQS(10), Mills (1979), OEIS A066010 | $30$ blocos | $30$ blocos ($3$ blocos-base sob $Z_{10}$) | `CALIBRATION_REPRODUCED` (Calibração exata) |
| **$[[8, 3, 3]]$** | Gottesman (1996), codetables.de | $k=3, d=3$ em $n=8$ | $k=3, d=3$ ($5$ geradores comutantes) | `CALIBRATION_REPRODUCED` (Síntese cega SAT) |
| **$[[14, 3, 4]]$** | codetables.de (Grassl) | $d=3$ (aberto para $d=4$) | $d=3$ (circulante CSS) | `NULL_BOUND` (Cota negativa comprovada) |
| **$[[16, 5, 4]]$** | codetables.de (Grassl) | $d=3$ (aberto para $d=4$) | $d=3$ (circulante CSS) | `NULL_BOUND` (Cota negativa comprovada) |
| **$C(13, 5, 3)$** | LJCR (Gordon) | $15$ blocos | $19$ blocos ($2$ órbitas parciais) | `NULL_RESULT` (Não superou LJCR) |
| **$C(14, 6, 4)$** | LJCR (Gordon) | $26$ blocos | $32$ blocos ($Z_{14}$ órbitas) | `NULL_RESULT` (Não superou LJCR) |
| **$C(16, 6, 4)$** | LJCR (Gordon) | $37$ blocos | $44$ blocos ($Z_{16}$ órbitas) | `NULL_RESULT` (Não superou LJCR) |

### Camada 2: Pacotes Standalone com Reprodução Offline em Menos de 10 Segundos

Todos os pacotes de curador em `dist/curator-submissions/p199/` são estritamente auto-contidos:
- Contêm o certificado canônico (`certificate.json` v2.0.0) ou notificação formal de cota negativa (`null-result-notice.md`).
- Contêm o verificador padrão sem dependências externas (`verify_structured_certificate.py`), executável com `python3 -S` (sem bibliotecas de terceiros).
- Contêm o script `reproduce.sh` que checa a integridade SHA-256 e executa a verificação completa.
- **Tempo de reprodução medido:**
  - `dan_gordon_ljcr`: $\approx 1.2$ ms.
  - `markus_grassl_codetables`: $\approx 0.6$ ms.
  - `neil_sloane_oeis`: $\approx 0.3$ ms.
  - Tempo total dos 3 pacotes combinados: $< 3$ ms (bem abaixo da meta de 10 segundos).

---

## 3. Inventário dos Pacotes e Hashes SHA-256

Conforme catalogado em [`docs/research/p199-curator-packages-index.json`](p199-curator-packages-index.json):

### 3.1 Dan Gordon — LJCR (`dan_gordon_ljcr`)
- **Canal Público:** `https://dmgordon.org/cover/`
- **Veredito:** `discovery_tied` ($C(15, 8, 4) = 30$)
- **Arquivos:**
  - `README.md`
  - `certificate.json` (SHA-256: `9c0610f9c8cfacf403a984aa58361f868d17c51d99499724f28a09e7d684905e`)
  - `verify_structured_certificate.py`
  - `reproduce.sh` (executável)
  - `submission-letter.md`
  - `submission-letter.txt`

### 3.2 Markus Grassl — codetables.de (`markus_grassl_codetables`)
- **Canal Público:** `http://www.codetables.de/`
- **Veredito:** `calibration_and_null_bound` ($[[8, 3, 3]]$ e cota negativa para CSS circulante)
- **Arquivos:**
  - `README.md`
  - `certificate.json` (SHA-256: `952d6b04b0664daa4fcc8c4219ba7958ed60655ce7728467c515ca7769c60ecd`)
  - `null-result-notice.md`
  - `verify_structured_certificate.py`
  - `reproduce.sh` (executável)
  - `submission-letter.md`
  - `submission-letter.txt`

### 3.3 Neil Sloane — OEIS (`neil_sloane_oeis`)
- **Canal Público:** `https://oeis.org/A066010`
- **Veredito:** `calibration_sqs10` ($\text{SQS}(10) = 30$)
- **Arquivos:**
  - `README.md`
  - `certificate.json` (SHA-256: `e20a8c24a3ae395b6a8d481c95f7b84f89589a290448bad290b80e6b0196cc64`)
  - `verify_structured_certificate.py`
  - `reproduce.sh` (executável)
  - `submission-letter.md`
  - `submission-letter.txt`

---

## 4. Instruções de Reprodução

Para reproduzir localmente qualquer um dos pacotes sem necessidade de instalar dependências Python:

```bash
# Dan Gordon (LJCR)
bash dist/curator-submissions/p199/dan_gordon_ljcr/reproduce.sh

# Markus Grassl (codetables.de)
bash dist/curator-submissions/p199/markus_grassl_codetables/reproduce.sh

# Neil Sloane (OEIS)
bash dist/curator-submissions/p199/neil_sloane_oeis/reproduce.sh
```

---

## 5. Próximos Passos (Transição para P200)

Com a auditoria de novidade concluída e o dossiê devidamente empacotado em conformidade com as regras de custódia humana:
- A fase P200 consolidará a decisão formal de encerramento do Programa D043 (`DECISION-D043.md`) e elaborará o manuscrito científico final documentando a síntese algébrica estruturada e certificação formal.
