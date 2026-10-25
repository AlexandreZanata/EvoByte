# P182 — Relatório da redescoberta cega de QECC e campanha pré-registrada

**Data:** 2026-10-25
**Fase:** P182 — Descoberta na Fronteira (D042)
**Status:** Concluído
**Manifesto SHA-256:** `393e7022a7fef48c1560f967dd1fb5ffdc6a1e62f42c8c2389f8e1a90c6113c6`

## 1. Integridade do Pré-registro

O manifesto `experiments/p182-qecc-manifest.json` congelou previamente todos os parâmetros da campanha:
- **Alvos de calibração**: `steane_7_1_3`, `shor_9_1_3` com sementes `[42, 101]`.
- **Alvos de recorde**: 7 alvos prioritários com gap aberto extraídos do catálogo P180 (`qecc_frontier_v1.json`) com sementes `[42, 101, 202]`.
- **Orçamento duplo**: tempo limite por ensaio OU limite máximo de avaliações (50 avaliações por ensaio de campanha; 200 por ensaio de calibração).
- **Inicialização estritamente pseudoaleatória**: zero sementes manuais ou geradores conhecidos no genoma inicial.
- **Oráculo de verificação**: exclusivamente `evobyte.qecc_verifier.code_distance`.

## 2. Fase 1: Redescoberta Cega de Calibração

O motor de busca P181 operou a partir de populações puramente aleatórias (sem conhecimento prévio da estrutura dos códigos de Steane e Shor), atingindo sucesso em todas as sementes:

| Alvo | Parâmetros $[[n,k]]$ | Cota $d$ | Semente | $d$ Encontrado | Avaliações | Tempo | Veredito |
|---|---|---|---|---|---|---|---|
| `steane_7_1_3` | $[[7,1]]$ | 3 | 42 | **3** | 20 | $0.014\text{ s}$ | `REDISCOVERY_OK` |
| `steane_7_1_3` | $[[7,1]]$ | 3 | 101 | **3** | 20 | $0.009\text{ s}$ | `REDISCOVERY_OK` |
| `shor_9_1_3` | $[[9,1]]$ | 3 | 42 | **3** | 20 | $0.038\text{ s}$ | `REDISCOVERY_OK` |
| `shor_9_1_3` | $[[9,1]]$ | 3 | 101 | **3** | 20 | $0.039\text{ s}$ | `REDISCOVERY_OK` |

**Status da Calibração**: `ALL_CALIBRATIONS_PASSED`. A autorização para prosseguir para a campanha foi formalmente satisfeita (regra de parada 4 não foi acionada).

## 3. Fase 2: Campanha Pré-registrada nos Parâmetros Abertos

A campanha avaliou 21 ensaios (7 alvos $\times$ 3 sementes). Cada candidato com potencial superior ao melhor valor conhecido do catálogo seria imediatamente revalidado pelo oráculo da P179.

| Alvo (`target_id`) | Parâmetros $[[n,k]]$ | Limitantes $[d_{lo}, d_{hi}]$ | Melhor $d$ Conhecido | Melhor $d$ Encontrado na Busca | Ensaios Executados | Veredito Consolidado |
|---|---|---|---|---|---|---|
| `qecc_14_3_open` | $[[14,3]]$ | $[4, 5]$ | 4 | 3 | 3 | `NULL_RESULT` |
| `qecc_16_5_open` | $[[16,5]]$ | $[4, 5]$ | 4 | 3 | 3 | `NULL_RESULT` |
| `qecc_17_3_open` | $[[17,3]]$ | $[5, 6]$ | 5 | 4 | 3 | `NULL_RESULT` |
| `qecc_18_3_open` | $[[18,3]]$ | $[5, 6]$ | 5 | 4 | 3 | `NULL_RESULT` |
| `qecc_19_10_open` | $[[19,10]]$ | $[3, 4]$ | 3 | 2 | 3 | `NULL_RESULT` |
| `qecc_20_2_open` | $[[20,2]]$ | $[6, 7]$ | 6 | 5 | 3 | `NULL_RESULT` |
| `qecc_20_3_open` | $[[20,3]]$ | $[6, 7]$ | 6 | 5 | 3 | `NULL_RESULT` |

Nenhum candidato atingiu $d > best\_known\_value$ nos alvos de recorde sob o orçamento pré-registrado. Nenhum certificado espúrio foi gerado.

- **Tempo total da campanha**: $87.52\text{ s}$.
- **Certificados de novo recorde emitidos**: 0.
- **Status consolidado da campanha**: `NULL_RESULT`.

## 4. Declaração Formal de Veredito

A hipótese de descoberta de novos recordes matemáticos QECC sob o orçamento fixo pré-registrado é NULL RESULT.
