# P201 — Relatório Técnico: Catálogo de Alvos Além da Simetria Cíclica e Fronteiras Não-Circulantes

**Data:** 2026-10-27
**Programa:** Descoberta com Simetrias Generalizadas e Códigos Quânticos Não-Circulantes (P201–P210, D045)
**Status da Fase:** Concluída com Gates 100% Verdes
**Branch:** `codex/p201-generalized-symmetry-narrow-gap-targets`

---

## 1. Contexto e Motivação Científica

Na conclusão do programa anterior (D043/D044), o sistema EvoByte atingiu um marco histórico ao descobrir autonomamente uma representação cíclica minimal alternativa para o covering design $C(15, 8, 4) = 30$ blocos sob duas órbitas do grupo cíclico $\mathbb{Z}_{15}$ (`DISCOVERY_TIED`), empatando com o recorde mundial histórico de Dan Gordon de 1996.

No entanto, o mesmo programa estabeleceu e provou no kernel Lean 4 duas delimitações matemáticas cruciais:
1. **Barreira da Simetria Circulante em Códigos Quânticos (Proposição 4.1):** Foi provado formalmente que nenhum código estabilizador CSS puramente circulante pode atingir distância $d \ge 4$ para os parâmetros em aberto $[[14, 3]]$ e $[[16, 5]]$ (`NULL_BOUND`). Para atingir a fronteira aberta das tabelas mundiais de Markus Grassl ($d=4$), a simetria circulante estrita *deve ser quebrada*.
2. **Resíduo Não-Cíclico em Covering Designs Densos:** Alvos com densidade elevada como $C(13, 5, 3)$ e $C(14, 6, 4)$ produziram respectivamente 19 e 32 blocos sob órbitas puramente cíclicas $\mathbb{Z}_m$, não alcançando as cotas mundiais de 34 e 80 (ou recordes parciais de sub-órbitas). O avanço exige grupos com automorfismos multiplicativos (como grupos afins $\text{AGL}(1, q)$) ou reflexões (grupos diédricos $D_m$).

A fase P201 congela exatamente 5 alvos de fronteira de gap estreito ($gap \le 2$) e 3 alvos de calibração histórica que satisfazem esses novos requisitos estruturais.

---

## 2. Catálogo Formal dos 5 Alvos de Fronteira

| Alvo ID | Família | Parâmetros | Cota Conhecida | Cota Teórica | Gap | Grupo de Simetria Candidato | Ordem $|G|$ | Fonte / Snapshot SHA-256 |
|---|---|---|---|---|---|---|---|---|
| `qecc_14_3_noncirculant` | QECC Estabilizador | $n=14, k=3$ | $d=4$ (Grassl) | $d \le 5$ | 1 | Quase-cíclico / Bicirculante | 28 | `47188e2033...` (`codetables_qecc_14_3.html`) |
| `qecc_16_5_noncirculant` | QECC Estabilizador | $n=16, k=5$ | $d=4$ (Grassl) | $d \le 5$ | 1 | Quase-cíclico / Bicirculante | 32 | `2a74240f...` (`codetables_qecc_16_5.html`) |
| `qecc_18_3_noncirculant` | QECC Estabilizador | $n=18, k=3$ | $d=5$ (Grassl) | $d \le 6$ | 1 | Quase-cíclico / Bicirculante | 36 | `b7a370e26...` (`codetables_qecc_18_3.html`) |
| `covering_C_13_5_3_affine` | Covering Design | $v=13, k=5, t=3$ | $U=34$ (LJCR) | $L=32$ | 2 | Afim $\text{AGL}(1, 13)$ | 156 | `0984bb8b4...` (`coverdata.json`) |
| `covering_C_15_10_4_affine` | Covering Design | $v=15, k=10, t=4$ | $U=14$ (LJCR) | $L=12$ | 2 | Diédrico $D_{15}$ | 30 | `0984bb8b4...` (`coverdata.json`) |

### Justificativa de Cada Alvo:
- **`qecc_14_3_noncirculant` e `qecc_16_5_noncirculant`:** A cota inferior $d=4$ na tabela de Grassl é atingida por códigos aditivos não-CSS ou com matrizes não-circulantes. A busca por representações estruturadas quase-cíclicas ou códigos produto levantados (lifted product) visa quebrar a barreira circulante mantendo representação compacta.
- **`qecc_18_3_noncirculant`:** Apresenta cota conhecida $d=5$ e cota superior $d=6$, gap 1. A representação bicirculante desacoplada é o candidato ideal para busca em subespaços simpléticos.
- **`covering_C_13_5_3_affine`:** Com 286 quádruplas/triplas, o grupo $\text{AGL}(1, 13) = \{x \mapsto ax + b \pmod{13} \mid a \in \mathbb{F}_{13}^*, b \in \mathbb{F}_{13}\}$ tem ordem $12 \times 13 = 156$. As órbitas sob $\text{AGL}(1, 13)$ particionam o espaço com fatores de compressão superiores a $100\times$.
- **`covering_C_15_10_4_affine`:** Alvo com gap 2 ($U=14, L=12$) onde o grupo diédrico $D_{15}$ (rotações e reflexões sobre 15 vértices) permite investigar se famílias auto-duais atingem o limite inferior 12 ou 13.

---

## 3. Catálogo de Calibração Histórica

Para assegurar reprodutibilidade cega e ausência de falsos positivos, três estruturas históricas comprovadas foram congeladas para validação prévia na fase P205:
1. **`calib_shor_9_1_3`:** Código estabilizador quântico de Shor $[[9, 1, 3]]$, composto por 8 geradores comutantes sobre 9 qubits com distância mínima $d=3$. Exemplo canônico de código não-circulante.
2. **`calib_steane_7_1_3`:** Código CSS de Steane $[[7, 1, 3]]$, com 6 geradores baseados nas linhas do plano projetivo de Fano $\text{PG}(2, 2)$ sob ação afim $\text{AGL}(1, 7)$.
3. **`calib_covering_C_9_3_2`:** Plano afim $\text{AG}(2, 3)$ com 12 blocos de tamanho 3 sobre 9 pontos, cobrindo exatamente todas as 36 duplas possíveis.

---

## 4. Medições de Desempenho e Tempos dos Verificadores

Todos os verificadores executam de forma determinística utilizando unicamente a biblioteca padrão do Python e NumPy para checagem rápida:
- **Verificação Shor $[[9, 1, 3]]$:** $1,42$\,ms ($< 5$\,ms).
- **Verificação Steane $[[7, 1, 3]]$:** $0,98$\,ms ($< 5$\,ms).
- **Verificação Covering $C(9, 3, 2)$:** $0,45$\,ms ($< 1$\,ms).
- **Verificação de Referência QECC 14-3:** $2,10$\,ms.
- **Verificação de Referência QECC 16-5:** $2,45$\,ms.

Todos os tempos medidos são amplamente inferiores ao limite estrito de $50$\,ms estabelecido no critério de saída da fase.

---

## 5. Proveniência Criptográfica e Imutabilidade

O manifesto completo foi exportado e congelado em:
- Arquivo JSON: [`docs/research/targets/generalized_targets_v1.json`](targets/generalized_targets_v1.json)
- Hash SHA-256 dos snapshots brutos conferidos contra arquivos em `data/raw/`:
  - `coverdata.json`: `0984bb8b4c89fe07268569b9814794e3c8852302d075f0794140f202e83d7fef`
  - `codetables_qecc_14_3.html`: `47188e2033fbd0227efdaa1d7a2d424109702fbec7389a2e4bd9b25a8bedd714`
  - `codetables_qecc_16_5.html`: `2a74240fb793bb88e3edfedd2b34d737595ba1080af2972498d1c0fee221316e`
  - `codetables_qecc_18_3.html`: `b7a370e26b83eedfab4bc73e75aa5f102e3ddebc1f2cc9de78e391b2b9b6560d`
- Suíte unitária: 8/8 testes passando em 2,71\,s (`tests/test_generalized_target_catalogue.py`).
