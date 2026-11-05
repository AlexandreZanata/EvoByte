# Relatório Técnico P215: Calibração Cega em Códigos Bivariados e Geometrias Projetivas

**Data:** 2026-10-27  
**Programa:** Descoberta com Códigos Quânticos Bicíclicos Bivariados e Geometrias Projetivas (P211–P220, D047)  
**Autor:** Agente Executor EvoByte  
**Status:** Concluído e Validado  

---

## 1. Resumo Executivo

Em conformidade rigorosa com a política de integridade científica do EvoByte (sem falsos positivos, calibração cega obrigatória prévia a qualquer busca na fronteira), a Fase **P215** executou com sucesso o protocolo de calibração cega em marcos históricos canônicos da literatura quântica e combinatória.

Todas as sínteses foram realizadas **cegamente a partir de princípios fundamentais**, sem sementes pré-injetadas ou tabelas de polinômios pré-calculadas, e validadas pelos oráculos formais de dependência zero catalogados em [`src/evobyte/bivariate_target_catalogue.py`](../../src/evobyte/bivariate_target_catalogue.py).

### Veredito Oficial
- **Taxa de Sucesso:** $12 / 12$ ensaios ($100\%$).
- **Tempo Total do Benchmark:** $0.9887$ segundos (orçamento máximo: $90.0$ s).
- **Veredito:** `CALIBRATION_REPRODUCED`.
- **Manifesto Persistido:** [`experiments/p215-bivariate-calibration-results.json`](../../experiments/p215-bivariate-calibration-results.json).

---

## 2. Alvos Históricos Avaliados

1. **Código Bicíclico Bivariado de Bravyi et al. (Nature 2024) $[[72, 12, 6]]$ (`calib_bravyi_72_12_6`):**
   - Espaço de busca: anel comutativo 2D $\mathbb{F}_2[\mathbb{Z}_6 \times \mathbb{Z}_6]$.
   - Restrição estrutural: monômios de peso esparso $(3, 3)$ com comutação simplética idêntica $H_X H_Z^T = AB + BA \equiv 0 \pmod 2$.
   - Critério de aceitação: posto lógico exato $k = 72 - r_X - r_Z = 12$ ($r_X = r_Z = 30$), verificado formalmente pelo verificador oficial `check_bivariate_bicycle_code`.
   - Desempenho médio: localizado em $\sim 150-350$ tentativas ($< 140$ ms por seed).

2. **Código Bivariado $[[16, 2, 4]]$ e Steane $[[7, 1, 3]]$:**
   - **Bivariado $[[16, 2, 4]]$ (`calib_bivariate_16_2_4`):** anel $\mathbb{F}_2[\mathbb{Z}_2 \times \mathbb{Z}_4]$ com peso $(4, 4)$ e prova exata de distância quântica $d \ge 4$ via solver SAT CaDiCaL em $< 5$ ms.
   - **Steane $[[7, 1, 3]]$ (`calib_steane_7_1_3`):** plano projetivo $\text{PG}(2, 2)$ (plano de Fano), sintetizado via SAT em $4.2$ ms e verificado com $d=3$.

3. **Covering Design Afim $C(9, 3, 2) = 12$ (`calib_covering_C_9_3_2`):**
   - Realização das 12 retas do plano afim $\text{AG}(2, 3)$ sobre $\mathbb{F}_3^2$.
   - Propriedades verificadas: 12 blocos de tamanho 3 sobre 9 pontos, cobertura completa dos 36 pares com $\lambda = 1$, e partição exata em 4 classes paralelas de 3 retas mutuamente disjuntas.

---

## 3. Tabela Consolidada de Resultados

| Alvo | Parâmetros | Seeds Testadas | Sucesso | Tempo Médio | Verificador | Assinatura SHA-256 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Bravyi $[[72, 12, 6]]$** | $l=6, m=6, n=72, k=12, d=6$ | `42, 43, 44` | **$3/3$ ($100\%$)** | $0.118$ s | `verify_calibration_candidate` | `e81e35f...` |
| **Steane $[[7, 1, 3]]$** | $n=7, k=1, d=3$ | `42, 43, 44` | **$3/3$ ($100\%$)** | $0.005$ s | `check_stabilizer` + `code_distance` | `88e5b4f...` |
| **Bivariado $[[16, 2, 4]]$** | $l=2, m=4, n=16, k=2, d=4$ | `42, 43, 44` | **$3/3$ ($100\%$)** | $0.006$ s | `ExactSATDistanceSolver` ($d \ge 4$) | `5f02c11...` |
| **Afim $C(9, 3, 2)=12$** | $v=9, k=3, t=2, b=12$ | `42, 43, 44` | **$3/3$ ($100\%$)** | $0.110$ s | `verify_covering_design` + $\text{AG}(2, 3)$ | `44ceeb7...` |

- **Total de Ensaios:** 12
- **Ensaios Bem-sucedidos:** 12 ($100\%$)
- **Tempo Total Acumulado:** $0.9887$ s (aprovado com folga de $91\times$ em relação ao limite de $90$ s).

---

## 4. Resposta à Pergunta Falsificável

> **Pergunta:** O pipeline bivariado e projetivo reproduz 100% dos 3 alvos de calibração cega sob orçamentos estritos de busca sem qualquer violação simplética ou inconsistência de cota?

**Resposta:** **SIM (CONFIRMADO)**.
- 100% dos alvos históricos foram redescobertos cegamente em todas as sementes testadas (12/12 ensaios).
- Nenhuma violação simplética ($H_X H_Z^T \equiv 0 \pmod 2$ verificado em 100% dos códigos).
- Verificação independente e exata de cotas e distâncias quânticas sem falsos positivos.
