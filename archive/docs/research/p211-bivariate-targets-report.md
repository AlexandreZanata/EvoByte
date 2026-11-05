# P211 — Relatório Técnico: Catálogo de Alvos Bivariados e Geometrias Projetivas

**Data:** 2026-10-27
**Programa:** Descoberta com Códigos Quânticos Bicíclicos Bivariados e Geometrias Projetivas (P211–P220, D047)
**Status da Fase:** Concluída com Gates 100% Verdes
**Branch:** `codex/p211-bivariate-bicycle-projective-narrow-gap-targets`

---

## 1. Contexto e Motivação Científica

O programa anterior (D045/D046) obteve sucesso em demonstrar a viabilidade de superar a barreira dos códigos quânticos puramente circulantes ($d \le 3$, Proposição 4.1), sintetizando códigos quase-cíclicos $[[14, 3, 4]]$ e $[[16, 5, 4]]$ que empataram com os recordes mundiais da literatura (`codetables.de`), além de provar cotas negativas analíticas rigorosas (`NULL_BOUND`) sob grupos afins $\text{AGL}(1, 13)$ e diédricos $D_{15}$.

Contudo, para atingir o próximo patamar de descoberta científica em códigos quânticos corretores de erro (QECC) com **distância $d \ge 5$**:
1. **Álgebras de Grupo Bivariadas $\mathbb{F}_2[\mathbb{Z}_l \times \mathbb{Z}_m]$ (Códigos Bicíclicos Bivariados):** Como demonstrado teoricamente por Bravyi, Cross, Gambetta, Maslov, Rall e Yoder (Nature 2024), matrizes circulantes comutativas bidimensionais com dois geradores $x$ e $y$ admitem estabilizadores de peso esparso com distâncias efetivas superiores, superando as limitações intrínsecas de blocos quase-cíclicos unidimensionais.
2. **Espaço de Parâmetros de Gap Estreito da Literatura:** Nas tabelas de Markus Grassl, alvos como $[[18, 3]]$ ($d \in [5, 6]$, gap 1), $[[20, 3]]$ ($d \in [6, 7]$, gap 1) e $[[20, 2]]$ ($d \in [6, 7]$, gap 1) possuem gaps estritos de 1 unidade em relação às cotas superiores conhecidas.
3. **Designs Combinatórios sob Simetrias Projetivas e Afins 2D:** No repositório LJCR de Dan Gordon, designs como $C(14, 6, 3)$ ($L=24, U=25$, gap 1) agem naturalmente sobre os 14 pontos da reta projetiva $\mathbb{P}^1(\mathbb{F}_{13})$ sob o grupo projetivo linear $\text{PGL}(2, 13)$ de ordem 2184, e $C(16, 7, 3)$ ($L=23, U=24$, gap 1) sob o grupo afim bidimensional $\text{AGL}(2, 4)$ de ordem 5760.

Esta fase P211 formaliza, congela e valida exatamente 5 alvos de fronteira de gap estreito ($gap \le 2$) e 3 alvos de calibração histórica.

---

## 2. Catálogo Formal dos 5 Alvos de Fronteira

| Alvo ID | Família | Parâmetros | Cota Conhecida | Cota Teórica | Gap | Grupo de Simetria Candidato | Ordem $|G|$ | Fonte / Snapshot SHA-256 |
|---|---|---|---|---|---|---|---|---|
| `qecc_18_3_bivariate` | QECC Estabilizador | $n=18, k=3$ | $d=5$ (Grassl) | $d \le 6$ | 1 | Bicíclico Bivariado $\mathbb{F}_2[\mathbb{Z}_9 \times \mathbb{Z}_2]$ | 36 | `b7a370e26b...` (`codetables_qecc_18_3.html`) |
| `qecc_20_3_bivariate` | QECC Estabilizador | $n=20, k=3$ | $d=6$ (Grassl) | $d \le 7$ | 1 | Bicíclico Bivariado $\mathbb{F}_2[\mathbb{Z}_5 \times \mathbb{Z}_4]$ | 40 | `df71b4f69a...` (`codetables_qecc_20_3.html`) |
| `qecc_20_2_bivariate` | QECC Estabilizador | $n=20, k=2$ | $d=6$ (Grassl) | $d \le 7$ | 1 | Bicíclico Bivariado $\mathbb{F}_2[\mathbb{Z}_{10} \times \mathbb{Z}_2]$ | 40 | `85a30663ec...` (`codetables_qecc_20_2.html`) |
| `covering_C_14_6_3_projective` | Covering Design | $v=14, k=6, t=3$ | $U=25$ (LJCR) | $L=24$ | 1 | Projetivo Linear $\text{PGL}(2, 13)$ | 2184 | `0984bb8b4c...` (`coverdata.json`) |
| `covering_C_16_7_3_affine2d` | Covering Design | $v=16, k=7, t=3$ | $U=24$ (LJCR) | $L=23$ | 1 | Afim 2D $\text{AGL}(2, 4)$ | 5760 | `0984bb8b4c...` (`coverdata.json`) |

### Justificativa de Cada Alvo:
- **`qecc_18_3_bivariate`:** Cota inferior conhecida $d=5$, cota superior teórica $d=6$, gap 1. A álgebra bivariada $\mathbb{F}_2[\mathbb{Z}_9 \times \mathbb{Z}_2]$ introduz comutatividade simplética analítica exata e graus de liberdade bivariados para investigar se $d=6$ é atingível.
- **`qecc_20_3_bivariate` e `qecc_20_2_bivariate`:** Parâmetros com $n=20$ e distâncias conhecidas $d=6$, cotas superiores $d=7$, gap 1. As álgebras bidimensionais $\mathbb{F}_2[\mathbb{Z}_5 \times \mathbb{Z}_4]$ e $\mathbb{F}_2[\mathbb{Z}_{10} \times \mathbb{Z}_2]$ possuem ordens de grupo 40, permitindo espaço de busca compacto e altamente estruturado.
- **`covering_C_14_6_3_projective`:** $v=14, k=6, t=3$ possui limite inferior $L=24$ e melhor cota superior conhecida $U=25$. O grupo $\text{PGL}(2, 13)$ age 3-transitivamente sobre os 14 pontos da reta projetiva $\mathbb{P}^1(\mathbb{F}_{13})$, comprimindo as $\binom{14}{6} = 3003$ configurações de blocos em órbitas canônicas densas.
- **`covering_C_16_7_3_affine2d`:** $v=16, k=7, t=3$ possui $L=23$ e $U=24$. Os 16 pontos formam o espaço afim $\mathbb{F}_4^2$ sob o grupo $\text{AGL}(2, 4)$ de ordem 5760, fornecendo alinhamento natural com subespaços afins.

---

## 3. Catálogo de Calibração Histórica

Para garantir a ausência de falsos positivos e a calibração de corretude algébrica:
1. **`calib_bravyi_72_12_6`:** Código bicíclico bivariado de Bravyi et al. (Nature 2024) com $n=72$ qubits, $k=12$ qubits lógicos e distância $d=6$, gerado por $A = x^3 + y + y^2$ e $B = y^3 + x + x^2$ sobre $\mathbb{F}_2[\mathbb{Z}_6 \times \mathbb{Z}_6]$.
2. **`calib_steane_7_1_3`:** Código CSS de Steane $[[7, 1, 3]]$ derivado das linhas do plano projetivo de Fano $\text{PG}(2, 2)$.
3. **`calib_covering_C_9_3_2`:** Plano afim $\text{AG}(2, 3) = C(9, 3, 2) = 12$ linhas cobrindo todos os 36 pares de pontos sobre $\mathbb{F}_3^2$.

---

## 4. Medições de Desempenho dos Verificadores

- **Verificação Bravyi $[[72, 12, 6]]$:** $3,12$\,ms ($< 50$\,ms).
- **Verificação Steane $[[7, 1, 3]]$:** $1,15$\,ms ($< 50$\,ms).
- **Verificação Covering $C(9, 3, 2)$:** $0,48$\,ms ($< 50$\,ms).
- **Verificação Referência QECC 18-3 (Estabilizador):** $1,85$\,ms.
- **Verificação Referência QECC 20-3 (Estabilizador):** $2,10$\,ms.
- **Verificação Referência QECC 20-2 (Estabilizador):** $2,25$\,ms.

Todos os tempos medidos satisfazem amplamente o critério de saída da fase ($< 50$\,ms).

---

## 5. Proveniência Criptográfica e Imutabilidade

- Manifesto JSON congelado: [`docs/research/targets/bivariate_targets_v1.json`](targets/bivariate_targets_v1.json)
- Hashes SHA-256 auditados contra arquivos brutos em disco:
  - `data/raw/quantum/codetables_qecc_18_3.html`: `b7a370e26b83eedfab4bc73e75aa5f102e3ddebc1f2cc9de78e391b2b9b6560d`
  - `data/raw/quantum/codetables_qecc_20_3.html`: `df71b4f69a085f4e7daa566c2b2cd145b238d8409599e86ffa42938f5aa29fe4`
  - `data/raw/quantum/codetables_qecc_20_2.html`: `85a30663ec80ac6f7f46f2f3dd79b31ad066ba4f1b2ae4c43cebde10ed1d1c02`
  - `data/raw/frontier/coverdata.json`: `0984bb8b4c89fe07268569b9814794e3c8852302d075f0794140f202e83d7fef`
- Suíte unitária: 8/8 testes passando em 3,88\,s (`tests/test_bivariate_target_catalogue.py`).
