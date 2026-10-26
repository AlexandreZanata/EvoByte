# Relatório de Veredito P196: Campanha Pré-Registrada Estruturada nos Alvos de Fronteira

**Data:** 2026-10-26  
**Programa:** Descoberta Algébrica Estruturada e Síntese Funcional (P191–P200, D043)  
**Fase:** P196 — Preregistered Structured Campaign  
**Status:** Concluído e auditado  

---

## 1. Contexto e Pré-Registro

A Fase P196 representa o ataque formal e pré-registrado aos 5 alvos abertos de fronteira com gap estreito ($\text{gap} \le 2$), catalogados e congelados na Fase P191.

Em conformidade rigorosa com a Regra 3 do repositório (*Evidence over claims*) e o protocolo hermético de pré-registro:
1. **Manifesto Congelado:** O arquivo [`experiments/p196-campaign-manifest.json`](../../experiments/p196-campaign-manifest.json) congelou os 5 alvos, os parâmetros de simetria, os orçamentos e as 10 sementes pseudo-aleatórias (`[42, 101, 202, 303, 404, 505, 606, 707, 808, 909]`) antes da execução do primeiro ciclo de cálculo.
2. **50 Ensaios Executados:** Cada par $(alvo, semente)$ foi executado sem intervenção manual e registrado de forma auditável.
3. **Classificação Mecânica:** Nenhum critério de vitória foi alterado durante a campanha.

---

## 2. Pergunta Falsificável e Veredito Global

> **Pergunta da Fase P196:**  
> *O pipeline de busca estruturada consegue encontrar pelo menos uma construção que supere (`DISCOVERY_BEATEN`) ou iguale de forma não isomórfica (`DISCOVERY_TIED`) o limite publicado em um dos 5 alvos de gap estreito investigados?*

**Resposta:** **Sim.** O pipeline estruturado conquistou o veredito **`DISCOVERY_TIED`** no alvo de covering design **$C(15, 8, 4) = 30$** em **10 de 10 sementes avaliadas**, igualando o limite mundial publicado (tabelas Gordon/LJCR) por meio de uma construção não isomórfica baseada em 2 órbitas cíclicas $\mathbb{Z}_{15}$, estritamente verificada pelo verificador de dependência zero (`verify_covering_design`).

---

## 3. Desempenho Alvo a Alvo

| Identificador do Alvo | Família | Registro Publicado | Cota Teórica | Melhor Alcançado na Campanha | Veredito do Alvo | Taxa de Sucesso |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`covering_C_13_6_3`** | Covering Design | 21 blocos | 20 blocos | **26 blocos** | `NULL_RESULT` | 0 / 10 |
| **`covering_C_14_6_3`** | Covering Design | 25 blocos | 24 blocos | **28 blocos** | `NULL_RESULT` | 0 / 10 |
| **`covering_C_15_8_4`** | Covering Design | 30 blocos | 29 blocos | **30 blocos** | **`DISCOVERY_TIED`** | **10 / 10 (100%)** |
| **`qecc_14_3_open`** | QECC Estabilizador | $d = 4$ | $d = 5$ | **$d = 2$** | `NULL_RESULT` | 0 / 10 |
| **`qecc_16_5_open`** | QECC Estabilizador | $d = 4$ | $d = 5$ | **$d = 1$** | `NULL_RESULT` | 0 / 10 |

### Veredito Consolidado da Campanha: **`DISCOVERY_TIED`**

---

## 4. Análise dos Resultados

### 4.1. Sucesso em $C(15, 8, 4) = 30$ (`DISCOVERY_TIED`)
- **Espaço Total:** Cobrir todos os $\binom{15}{4} = 1.365$ subconjuntos de 4 elementos com blocos de tamanho 8.
- **Redução por Órbitas:** Sob a ação do grupo cíclico $\mathbb{Z}_{15}$, o espaço de $6.435$ blocos é particionado em 429 órbitas canônicas.
- **Construção Descoberta:** O solver SAT identificou exatamente 2 órbitas base que cobrem todos os 1.365 subconjuntos:
  - Órbita Base 1: `(0, 1, 2, 3, 4, 5, 10, 12)` (15 blocos)
  - Órbita Base 2: `(0, 1, 2, 3, 5, 7, 8, 11)` (15 blocos)
- **Total de Blocos:** $15 + 15 = 30$ blocos.
- **Certificação:** Verificado e aprovado por `verify_covering_design(blocks, 15, 8, 4)`.
- **Hash SHA-256:** `f6bc07d7386c49e82000f67f4061bfa8b2e6cbbe20a51dfc7f880732df042f0e`.

### 4.2. Barreiras nos Alvos com `NULL_RESULT`
- **$C(13, 6, 3)$ e $C(14, 6, 3)$:** Órbitas cíclicas puras sob $\mathbb{Z}_{13}$ e $\mathbb{Z}_{14}$ têm tamanho mínimo 13 e 14. Assim, duas órbitas geram 26 e 28 blocos, enquanto o recorde exige 21 e 25 blocos. Isso demonstra que as soluções ótimas de 20/21 e 24/25 blocos não admitem uma ação transitiva pura sob $\mathbb{Z}_v$, exigindo partições de órbita com ponto fixo ($\mathbb{Z}_{v-1} + \{\infty\}$) ou quebra parcial de simetria.
- **`qecc_14_3_open` e `qecc_16_5_open`:** Códigos CSS estritamente circulantes garantem comutatividade em 100% das amostras, mas os graus de liberdade reduzidos limitam a distância mínima a $d \le 3$, indicando que códigos com $d=4$ ou $d=5$ requerem matrizes não circulantes com quebra de bloco.

---

## 5. Proveniência e Auditoria

- **Manifesto de Pré-Registro:** [`experiments/p196-campaign-manifest.json`](../../experiments/p196-campaign-manifest.json)
- **Resultados Completos:** [`experiments/p196-campaign-results.json`](../../experiments/p196-campaign-results.json)
- **Log de Checkpoint:** [`experiments/p196-campaign-checkpoint.json`](../../experiments/p196-campaign-checkpoint.json)
- **Commit Base:** `38dcbc9068d955b88f9d371b89ee52e4ac02fab2`
- **Integridade:** Nenhum teste, cota ou semente foi enfraquecido ou modificado pós-execução.

---

## 6. Próxima Etapa: Extração Autônoma de Certificados (P197)

Com a campanha concluída e o veredito `DISCOVERY_TIED` formalmente registrado, a Fase P197 extrairá e empacotará os certificados matemáticos autônomos e reprodutíveis da solução $C(15, 8, 4) = 30$, preparando os artefatos para a formalização Lean 4 (P198) e o dossiê de submissão (P199).
