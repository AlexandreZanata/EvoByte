# P202 — Relatório Técnico: Motor de Grupos de Automorfismos Generalizados (Affine, Dihedral & Quasi-Cyclic Orbits)

**Data:** 2026-10-27
**Programa:** Descoberta com Simetrias Generalizadas e Códigos Quânticos Não-Circulantes (P201–P210, D045)
**Status da Fase:** Concluída com Gates 100% Verdes
**Branch:** `codex/p202-generalized-automorphism-orbit-reduction`

---

## 1. Contexto e Motivação Científica

Na fase anterior P201, congelamos 5 alvos de fronteira estreita ($gap \le 2$) e 3 alvos de calibração histórica. A limitação fundamental identificada no programa anterior (D043/D044) foi a **barreira circulante pura**:
1. Para códigos estabilizadores quânticos $[[14, 3]]$ e $[[16, 5]]$, o teorema formal provado no Lean 4 (Proposição 4.1) demonstrou que matrizes estritamente circulantes não podem atingir $d \ge 4$.
2. Para covering designs com parâmetros mais densos como $C(13, 5, 3)$, o grupo cíclico $\mathbb{Z}_{13}$ possui apenas 13 elementos, comprimindo o espaço de 1287 subconjuntos para 99 órbitas cíclicas ($13\times$ de redução). Essa dimensionalidade ainda é ampla para buscas exaustivas ou genéticas rápidas.

A fase P202 desenvolve o motor algébrico de **grupos de automorfismos de ordem superior**:
- **Grupo Afim 1-Dimensional $\text{AGL}(1, q)$:** composto por transformações $x \mapsto ax + b \pmod q$, com $a \in \mathbb{F}_q^*$ e $b \in \mathbb{F}_q$. Possui ordem $|G| = \phi(q) \cdot q$, o que para $q=13$ primo resulta em $12 \times 13 = 156$ transformações.
- **Grupo Diédrico $D_m$:** composto por rotações $x \mapsto x + s \pmod m$ e reflexões modulares $x \mapsto -x + s \pmod m$. Possui ordem $|G| = 2m$.
- **Gerador Bicirculante Quase-Cíclico (Bicirculant CSS):** gera blocos $H_X = (A \mid B)$ e $H_Z = (B^T \mid A^T)$ onde $A$ e $B$ são matrizes circulantes de dimensão $L \times L$. Pela comutatividade matricial entre circulantes ($A B = B A$), a ortogonalidade simplética $H_X H_Z^T = A B + B A = 2 A B \equiv 0 \pmod 2$ é garantida algebricamente a $100\%$ por construção, quebrando a simetria circulante global em $n=2L$ qubits.

---

## 2. Formalização Algébrica dos Grupos

### 2.1 Grupo Afim $\text{AGL}(1, q)$
Dado um módulo $q > 1$:
- Elementos: $g = (a, b) \in \mathbb{Z}_q^* \times \mathbb{Z}_q$, onde $\gcd(a, q) = 1$.
- Operação de composição:
  $$(a_1, b_1) \circ (a_2, b_2) = ((a_1 a_2) \pmod q, (a_1 b_2 + b_1) \pmod q)$$
- Elemento neutro: $e = (1, 0)$.
- Elemento inverso:
  $$(a, b)^{-1} = (a^{-1} \pmod q, -a^{-1} b \pmod q)$$
- Ação em subconjunto $S \subset \mathbb{Z}_q$: $g(S) = \{ (ax + b) \pmod q \mid x \in S\}$.

### 2.2 Grupo Diédrico $D_m$
Dado o número de vértices $m \ge 3$:
- Elementos: $g = (r, s)$, onde $r \in \{0, 1\}$ denota reflexão e $s \in \mathbb{Z}_m$ denota deslocamento.
- Operação de composição:
  $$(r_1, s_1) \circ (r_2, s_2) = (r_1 \oplus r_2, (s_1 + (-1)^{r_1} s_2) \pmod m)$$
- Elemento neutro: $e = (0, 0)$.
- Inverso: se $r=0$, $(0, s)^{-1} = (0, -s \pmod m)$; se $r=1$, $(1, s)^{-1} = (1, s)$ (toda reflexão é idempotente).

---

## 3. Resultados Empíricos de Redução de Órbitas

A tabela abaixo resume os resultados obtidos pelo `GeneralizedCoveringOrbitEngine` comparando a compressão obtida com o grupo cíclico $\mathbb{Z}_m$ versus o grupo generalizado:

| Alvo Combinatório | Total Subconjuntos $\binom{v}{k}$ | Órbitas Cíclicas $\mathbb{Z}_m$ | Órbitas Generalizadas ($G$) | Compressão Cíclica | Compressão Generalizada | Ganho Adicional vs $\mathbb{Z}_m$ |
|---|---|---|---|---|---|---|
| $C(13, 5, 3)$ | 1287 | 99 | **10** ($\text{AGL}(1, 13)$) | $13.00\times$ | **$128.70\times$** | **$9.90\times$** |
| $C(7, 3, 2)$ | 35 | 5 | **2** ($\text{AGL}(1, 7)$) | $7.00\times$ | **$17.50\times$** | **$2.50\times$** |
| $C(11, 5, 2)$ | 462 | 42 | **6** ($\text{AGL}(1, 11)$) | $11.00\times$ | **$77.00\times$** | **$7.00\times$** |
| $C(15, 10, 4)$ | 3003 | 201 | **111** ($D_{15}$) | $14.94\times$ | **$27.05\times$** | **$1.81\times$** |

### Observações:
1. **Compressão Afim Massiva ($9.90\times$ adicional):** Em $C(13, 5, 3)$, a partição sob $\text{AGL}(1, 13)$ colapsa todo o espaço de 1287 blocos candidatos em apenas **10 representantes canônicos**, permitindo que o algoritmo evolutivo explore o espaço de famílias de blocos de forma combinatoriamente trivial.
2. **Fusão Quiral Diédrica ($1.81\times$ adicional):** Em $C(15, 10, 4)$, o grupo $D_{15}$ funde quase todos os pares quirais de blocos cíclicos, reduzindo 201 órbitas para 111 (fator próximo do teto teórico de $2\times$ para um grupo de ordem dobrada).

---

## 4. Desempenho e Tempos de Execução

Medições obtidas em ambiente determinístico CPU (Python 3.12 + NumPy):
- **Decomposição completa em órbitas para $C(13, 5, 3)$ ($\text{AGL}(1, 13)$):** $855.82$\,ms.
- **Decomposição completa em órbitas para $C(15, 10, 4)$ ($D_{15}$):** $535.19$\,ms.
- **Geração e verificação simplética bicirculante:** $0.7391$\,ms por par $(H_X, H_Z)$.
- **Taxa de comutatividade simplética $H_X H_Z^T \equiv 0 \pmod 2$:** **100.0%** em 150/150 amostras aleatórias testadas em $L \in \{7, 8, 9\}$ ($n \in \{14, 16, 18\}$ qubits).

---

## 5. Resposta à Pergunta Falsificável

> **Pergunta:** A fatoração por grupos afins $\text{AGL}(1, q)$ ou diédricos $D_m$ atinge uma taxa de compressão de parâmetros $\ge 2\times$ adicional em relação ao grupo cíclico $\mathbb{Z}_m$, preservando a corretude de geração de órbitas em 100% dos testes algébricos formais?
>
> **Resposta:** **SIM**. A compressão com $\text{AGL}(1, 13)$ atinge $9.90\times$ de redução adicional em relação a $\mathbb{Z}_{13}$ (excedendo amplamente o limiar de $2\times$). Todos os axiomas de grupo (fechamento, elemento neutro, elemento inverso e associatividade) e invariância de ação foram validados com 100% de aprovação na suíte formal `tests/test_generalized_symmetry.py`.
