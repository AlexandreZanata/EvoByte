# P176 — Relatório da campanha pré-registrada de covering designs

**Data:** 2026-10-24
**Fase:** P176 — Descoberta na Fronteira (D042)

## 1. Resumo executivo

- **Alvos:** 40 covering designs com `role = record` do catálogo v2 (P171); tentativa de quebra = `published_size - 1` blocos em todos, sem exceção e sem redefinição de meta.
- **Ensaios:** 360 (40 alvos × 3 algoritmos × 3 sementes 42/101/202), orçamento dual por ensaio: **2,0 s OU 20 000 avaliações**, o que estourar primeiro.
- **Avaliações totais:** 1 958 802 deltas; tempo de busca+init somado: 824 s (233 s de init); 0 chamadas ao verificador disparadas por cobertura total (nenhum ensaio atingiu `uncovered = 0`).
- **Vereditos:** `DISCOVERY_BEATEN` **0** · `NULL_RESULT` **40** · `INCOMPLETE` 0.
- Nenhum objeto abaixo da cota publicada foi produzido; nenhum certificado foi emitido. Nenhum dos 40 tamanhos de tentativa está abaixo do `lower_bound` conhecido (0/40 impossíveis por construção) — os nulos são informativos, não vácuos.

## 2. Tabela de vereditos por alvo

`best_uncovered` = menor nº de t-subconjuntos descobertos entre os 9 ensaios do alvo (`total` = C(v,t)).

| alvo | v,k,t | published | attempt | verdict | best_uncovered/total | certificado |
|---|---|---|---|---|---|---|
| covering_C_12_7_4 | 12,7,4 | 24 | 23 | NULL_RESULT | 16/495 | — |
| covering_C_19_11_3 | 19,11,3 | 11 | 10 | NULL_RESULT | 48/969 | — |
| covering_C_19_11_4 | 19,11,4 | 23 | 22 | NULL_RESULT | 202/3876 | — |
| covering_C_19_13_6 | 19,13,6 | 42 | 41 | NULL_RESULT | 485/27132 | — |
| covering_C_20_12_4 | 20,12,4 | 20 | 19 | NULL_RESULT | 220/4845 | — |
| covering_C_20_12_5 | 20,12,5 | 42 | 41 | NULL_RESULT | 704/15504 | — |
| covering_C_21_9_6 | 21,9,6 | 1060 | 1059 | NULL_RESULT | 6135/54264 | — |
| covering_C_22_13_3 | 22,13,3 | 11 | 10 | NULL_RESULT | 63/1540 | — |
| covering_C_22_15_6 | 22,15,6 | 46 | 45 | NULL_RESULT | 869/74613 | — |
| covering_C_23_16_5 | 23,16,5 | 20 | 19 | NULL_RESULT | 751/33649 | — |
| covering_C_23_16_6 | 23,16,6 | 38 | 37 | NULL_RESULT | 1557/100947 | — |
| covering_C_24_14_3 | 24,14,3 | 11 | 10 | NULL_RESULT | 108/2024 | — |
| covering_C_25_16_4 | 25,16,4 | 17 | 16 | NULL_RESULT | 335/12650 | — |
| covering_C_26_15_3 | 26,15,3 | 11 | 10 | NULL_RESULT | 162/2600 | — |
| covering_C_26_16_4 | 26,16,4 | 18 | 17 | NULL_RESULT | 645/14950 | — |
| covering_C_28_16_3 | 28,16,3 | 11 | 10 | NULL_RESULT | 233/3276 | — |
| covering_C_28_9_5 | 28,9,5 | 1216 | 1215 | NULL_RESULT | 13337/98280 | — |
| covering_C_32_16_6 | 32,16,6 | 286 | 285 | NULL_RESULT | 55469/906192 | — |
| covering_C_40_18_5 | 40,18,5 | 186 | 185 | NULL_RESULT | 45377/658008 | — |
| covering_C_40_21_6 | 40,21,6 | 226 | 225 | NULL_RESULT | 144112/3838380 | — |
| covering_C_42_18_5 | 42,18,5 | 247 | 246 | NULL_RESULT | 55828/850668 | — |
| covering_C_43_13_5 | 43,13,5 | 1835 | 1834 | NULL_RESULT | 67527/962598 | — |
| covering_C_44_18_5 | 44,18,5 | 338 | 337 | NULL_RESULT | 65760/1086008 | — |
| covering_C_44_22_6 | 44,22,6 | 342 | 341 | NULL_RESULT | 187150/7059052 | — |
| covering_C_46_14_5 | 46,14,5 | 1948 | 1947 | NULL_RESULT | 75925/1370754 | — |
| covering_C_48_11_4 | 48,11,4 | 1159 | 1158 | NULL_RESULT | 18671/194580 | — |
| covering_C_49_18_5 | 49,18,5 | 635 | 634 | NULL_RESULT | 107023/1906884 | — |
| covering_C_50_15_3 | 50,15,3 | 68 | 67 | NULL_RESULT | 2678/19600 | — |
| covering_C_51_11_4 | 51,11,4 | 1497 | 1496 | NULL_RESULT | 24731/249900 | — |
| covering_C_53_11_4 | 53,11,4 | 1700 | 1699 | NULL_RESULT | 32836/292825 | — |
| covering_C_54_16_2 | 54,16,2 | 16 | 15 | NULL_RESULT | 235/1431 | — |
| covering_C_56_18_5 | 56,18,5 | 1216 | 1215 | NULL_RESULT | 246536/3819816 | — |
| covering_C_59_20_4 | 59,20,4 | 153 | 152 | NULL_RESULT | 75550/455126 | — |
| covering_C_62_23_4 | 62,23,4 | 127 | 126 | NULL_RESULT | 61062/557845 | — |
| covering_C_64_22_5 | 64,22,5 | 861 | 860 | NULL_RESULT | 378470/7624512 | — |
| covering_C_65_15_4 | 65,15,4 | 831 | 830 | NULL_RESULT | 110698/677040 | — |
| covering_C_84_11_2 | 84,11,2 | 73 | 72 | NULL_RESULT | 720/3486 | — |
| covering_C_86_16_3 | 86,16,3 | 258 | 257 | NULL_RESULT | 19975/102340 | — |
| covering_C_88_21_4 | 88,21,4 | 859 | 858 | NULL_RESULT | 253283/2331890 | — |
| covering_C_98_22_2 | 98,22,2 | 27 | 26 | NULL_RESULT | 913/4753 | — |

(tabela gerada de `experiments/p176-covering-results.json`; valores por ensaio + `best_sha256` por trial no JSON. Nenhum certificado: coluna vazia em todos.)

## 3. Frase literal aplicável (vale para cada um dos 40 alvos sem recorde)

> A busca estocástica sob o orçamento pré-registrado não superou a cota publicada. O resultado nulo é publicado de acordo com a regra de integridade científica de AGENTS.md.

## 4. Integridade

- Manifesto: `experiments/p176-covering-manifest.json`, `created_at` 2026-10-23T23:56:31+00:00, anterior ao `started_at` da campanha; SHA-256 `8a0e6da89dda…` registrado no JSON de resultados.
- Checkpoint incremental: `experiments/p176-covering-checkpoint.json` (360/360 ensaios; resume verificado pelo teste de roundtrip; a execução final do gate retomou 0 ensaios e apenas consolidou os resultados).
- Orçamento: `budget_sec_per_seed` 2,0 s + `max_evaluations_per_trial` 20 000 por (alvo, tamanho, algoritmo, semente); sementes 42/101/202; regra de veredito congelada no manifesto.
- Verificador independente: `frontier_catalogue.verify_covering_design` (P171) armado para certificação imediata; 0 certificados emitidos porque nenhum ensaio atingiu cobertura total — o caminho de certificação foi exercitado nos portões P171, não por atalho.
- Tamanhos de quebra: exatamente `published_size - 1` em todos os alvos (teste `test_break_size_is_published_minus_one`).

## 5. Limitações

- Orçamento de sondagem (2 s/ensaio): nulos válidos sob este orçamento; não reivindica esgotamento nem impossibilidade (exceto onde `lower_bound` já decide — 0 casos aqui).
- Operadores: SA / Hill-Climbing com restarts / guloso aleatório + busca local, todos sobre representação direta de blocos com avaliação delta incremental; sem SAT dedicado, sem simetria-breaking, sem constructions algébricas.
- Cobertura total nunca atingida em 360 ensaios ⇒ a via de certificação imediata não foi percorrida nesta campanha; permanece armada para fases futuras com orçamentos maiores.
