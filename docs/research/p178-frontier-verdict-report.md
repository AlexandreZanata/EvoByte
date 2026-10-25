# P178 — Veredito consolidado das campanhas combinatórias (P176/P177)

**Data:** 2026-10-24
**Fase:** P178 — Descoberta na Fronteira (D042)

## 1. Frases literais de veredito

- "A hipótese de superioridade estrita de busca evolutiva em bytecode é **NOT SUPPORTED**."
  Motivo explícito: as campanhas P176/P177 executaram **zero** ensaios de evolução em bytecode
  (apenas SimulatedAnnealing, HillClimbing e GreedyPlusLocalSearch clássicos); esta base de
  evidência não contém nenhuma observação sobre bytecode. NOT SUPPORTED aqui significa
  ausência de evidência, não evidência de ausência.
- "A hipótese de descoberta de novos recordes matemáticos é **NULL RESULT**."
  Nenhum certificado `DISCOVERY_BEATEN` em 396 ensaios (360 covering + 36 Schur fraco).

## 2. Bateria pareada (SA-vs-HC, Wilcoxon bilateral + Holm passo único, α = 0,01)

Pareamento estrito por alvo, tamanho e semente (mesmo orçamento). `p_holm = min(1, p_raw × 46)`
para a bateria (46 comparações; correção conservadora de passo único, documentada, não
Holm step-down). Com n = 3 sementes por teste, o menor `p_raw` bilateral possível é 0,25 —
a bateria por alvo não tem poder para α = 0,01 por construção; o veredito formal vem do
agrupado exploratório (§3) e dos certificados (§4).

| comparação | n | W | p_raw | p_Holm | direção | veredito |
|---|---|---|---|---|---|---|
| P176:covering_C_12_7_4\|B23\|SA-vs-HC | 3 | 0.0 | 0.25 | 1 | b_greater | NOT_SUPPORTED_NULL |
| P176:covering_C_19_11_3\|B10\|SA-vs-HC | 3 | 0.0 | 0.25 | 1 | b_greater | NOT_SUPPORTED_NULL |
| P176:covering_C_19_11_4\|B22\|SA-vs-HC | 3 | 0.0 | 0.25 | 1 | b_greater | NOT_SUPPORTED_NULL |
| P176:covering_C_19_13_6\|B41\|SA-vs-HC | 3 | 0.0 | 0.25 | 1 | b_greater | NOT_SUPPORTED_NULL |
| P176:covering_C_20_12_4\|B19\|SA-vs-HC | 3 | 0.0 | 0.25 | 1 | b_greater | NOT_SUPPORTED_NULL |
| P176:covering_C_20_12_5\|B41\|SA-vs-HC | 3 | 0.0 | 0.25 | 1 | b_greater | NOT_SUPPORTED_NULL |
| P176:covering_C_21_9_6\|B1059\|SA-vs-HC | 3 | 0.0 | 0.25 | 1 | b_greater | NOT_SUPPORTED_NULL |
| P176:covering_C_22_13_3\|B10\|SA-vs-HC | 3 | 0.0 | 0.25 | 1 | b_greater | NOT_SUPPORTED_NULL |
| P176:covering_C_22_15_6\|B45\|SA-vs-HC | 3 | 0.0 | 0.25 | 1 | b_greater | NOT_SUPPORTED_NULL |
| P176:covering_C_23_16_5\|B19\|SA-vs-HC | 3 | 0.0 | 0.25 | 1 | b_greater | NOT_SUPPORTED_NULL |
| P176:covering_C_23_16_6\|B37\|SA-vs-HC | 3 | 0.0 | 0.25 | 1 | b_greater | NOT_SUPPORTED_NULL |
| P176:covering_C_24_14_3\|B10\|SA-vs-HC | 3 | 0.0 | 0.25 | 1 | b_greater | NOT_SUPPORTED_NULL |
| P176:covering_C_25_16_4\|B16\|SA-vs-HC | 3 | 0.0 | 0.25 | 1 | b_greater | NOT_SUPPORTED_NULL |
| P176:covering_C_26_15_3\|B10\|SA-vs-HC | 3 | 1.0 | 0.5 | 1 | b_greater | NOT_SUPPORTED_NULL |
| P176:covering_C_26_16_4\|B17\|SA-vs-HC | 3 | 0.0 | 0.25 | 1 | b_greater | NOT_SUPPORTED_NULL |
| P176:covering_C_28_16_3\|B10\|SA-vs-HC | 3 | 1.5 | 0.75 | 1 | b_greater | NOT_SUPPORTED_NULL |
| P176:covering_C_28_9_5\|B1215\|SA-vs-HC | 3 | 2.0 | 0.75 | 1 | a_greater | NOT_SUPPORTED_NULL |
| P176:covering_C_32_16_6\|B285\|SA-vs-HC | 3 | 3.0 | 1 | 1 | a_greater | NOT_SUPPORTED_NULL |
| P176:covering_C_40_18_5\|B185\|SA-vs-HC | 3 | 0.0 | 0.25 | 1 | a_greater | NOT_SUPPORTED_NULL |
| P176:covering_C_40_21_6\|B225\|SA-vs-HC | 3 | 0.0 | 1 | 1 | no_difference | INCONCLUSIVE_IDENTICAL |
| P176:covering_C_42_18_5\|B246\|SA-vs-HC | 3 | 3.0 | 1 | 1 | a_greater | NOT_SUPPORTED_NULL |
| P176:covering_C_43_13_5\|B1834\|SA-vs-HC | 3 | 2.0 | 0.75 | 1 | a_greater | NOT_SUPPORTED_NULL |
| P176:covering_C_44_18_5\|B337\|SA-vs-HC | 3 | 0.0 | 0.25 | 1 | b_greater | NOT_SUPPORTED_NULL |
| P176:covering_C_44_22_6\|B341\|SA-vs-HC | 3 | 0.0 | 1 | 1 | no_difference | INCONCLUSIVE_IDENTICAL |
| P176:covering_C_46_14_5\|B1947\|SA-vs-HC | 3 | 0.0 | 0.25 | 1 | b_greater | NOT_SUPPORTED_NULL |
| P176:covering_C_48_11_4\|B1158\|SA-vs-HC | 3 | 1.0 | 0.5 | 1 | a_greater | NOT_SUPPORTED_NULL |
| P176:covering_C_49_18_5\|B634\|SA-vs-HC | 3 | 0.0 | 0.25 | 1 | a_greater | NOT_SUPPORTED_NULL |
| P176:covering_C_50_15_3\|B67\|SA-vs-HC | 3 | 0.0 | 0.25 | 1 | b_greater | NOT_SUPPORTED_NULL |
| P176:covering_C_51_11_4\|B1496\|SA-vs-HC | 3 | 3.0 | 1 | 1 | a_greater | NOT_SUPPORTED_NULL |
| P176:covering_C_53_11_4\|B1699\|SA-vs-HC | 3 | 0.0 | 0.25 | 1 | a_greater | NOT_SUPPORTED_NULL |
| P176:covering_C_54_16_2\|B15\|SA-vs-HC | 3 | 0.0 | 0.25 | 1 | b_greater | NOT_SUPPORTED_NULL |
| P176:covering_C_56_18_5\|B1215\|SA-vs-HC | 3 | 0.0 | 1 | 1 | no_difference | INCONCLUSIVE_IDENTICAL |
| P176:covering_C_59_20_4\|B152\|SA-vs-HC | 3 | 3.0 | 1 | 1 | b_greater | NOT_SUPPORTED_NULL |
| P176:covering_C_62_23_4\|B126\|SA-vs-HC | 3 | 0.0 | 0.25 | 1 | b_greater | NOT_SUPPORTED_NULL |
| P176:covering_C_64_22_5\|B860\|SA-vs-HC | 3 | 0.0 | 1 | 1 | no_difference | INCONCLUSIVE_IDENTICAL |
| P176:covering_C_65_15_4\|B830\|SA-vs-HC | 3 | 1.0 | 0.5 | 1 | b_greater | NOT_SUPPORTED_NULL |
| P176:covering_C_84_11_2\|B72\|SA-vs-HC | 3 | 0.0 | 0.25 | 1 | b_greater | NOT_SUPPORTED_NULL |
| P176:covering_C_86_16_3\|B257\|SA-vs-HC | 3 | 0.0 | 0.25 | 1 | b_greater | NOT_SUPPORTED_NULL |
| P176:covering_C_88_21_4\|B858\|SA-vs-HC | 3 | 1.0 | 0.5 | 1 | a_greater | NOT_SUPPORTED_NULL |
| P176:covering_C_98_22_2\|B26\|SA-vs-HC | 3 | 0.0 | 0.25 | 1 | b_greater | NOT_SUPPORTED_NULL |
| P177/free:weak_schur_5\|B208\|SA-vs-HC | 3 | 0.0 | 0.25 | 1 | b_greater | NOT_SUPPORTED_NULL |
| P177/free:weak_schur_6\|B651\|SA-vs-HC | 3 | 2.0 | 0.75 | 1 | b_greater | NOT_SUPPORTED_NULL |
| P177/free:weak_schur_7\|B2147\|SA-vs-HC | 3 | 2.0 | 0.75 | 1 | b_greater | NOT_SUPPORTED_NULL |
| P177/symmetric_p3:weak_schur_5\|B208\|SA-vs-HC | 3 | 0.0 | 1 | 1 | no_difference | INCONCLUSIVE_IDENTICAL |
| P177/symmetric_p3:weak_schur_6\|B651\|SA-vs-HC | 3 | 0.0 | 1 | 1 | no_difference | INCONCLUSIVE_IDENTICAL |
| P177/symmetric_p3:weak_schur_7\|B2147\|SA-vs-HC | 3 | 0.0 | 1 | 1 | a_greater | NOT_SUPPORTED_NULL |

Resultado da bateria: 40 NOT_SUPPORTED_NULL + 6 INCONCLUSIVE_IDENTICAL (empates nas 3 sementes); zero
vereditos de superioridade na bateria corrigida.

## 3. Agrupados exploratórios (family_size = 1, sem correção; não confirmatórios)

| comparação | n | W | p_raw | p_Holm | direção | veredito |
|---|---|---|---|---|---|---|
| P176:grouped:SA-vs-HC:exploratory | 120 | 1984.5 | 0.003304 | 0.003304 | b_greater | SUPPORTED_B_GREATER |
| P177/free:grouped:SA-vs-HC:exploratory | 9 | 13.0 | 0.2891 | 0.2891 | b_greater | NOT_SUPPORTED_NULL |
| P177/symmetric_p3:grouped:SA-vs-HC:exploratory | 9 | 0.0 | 1 | 1 | a_greater | NOT_SUPPORTED_NULL |

Leitura honesta: o único sinal significant (p_Holm = 0.003304 ≤ 0.01) é o agrupado da P176,
não corrigido e rotulado como exploratório, e diz apenas que SA deixa menos descobertos que HC
em covering (b_greater = valores de HC maiores, i.e. piores; menor é melhor). Não é evidência
sobre bytecode, não é recorde, e não sobrevive como afirmação confirmatória por ser pooled e
não corrigido para a família.

## 4. Descoberta matemática

`mathematical_record_discovery = NULL_RESULT`: 0 certificados `DISCOVERY_BEATEN` em 43 alvos
(40 covering + 3 Schur fraco). Nenhum objeto abaixo/igual-acima da cota foi produzido.

## 5. Cadeia de custódia

- `experiments/p176-covering-results.json`: SHA-256 `fe072215c3610b47…`
- `experiments/p177-weak-schur-results.json`: SHA-256 `2c2ef5c4030b9a6…`
- `experiments/p178-frontier-verdict.json`: SHA-256 registrado no artefato (`custody.output_sha256`).
- Nenhum dado de entrada foi alterado (p-hacking seria relatar `p_raw` sem `p_Holm`; todos os
  vereditos acima usam `p_Holm`).
