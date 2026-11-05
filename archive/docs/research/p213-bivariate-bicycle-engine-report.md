# Relatório Técnico P213: Motor de Códigos Quânticos Bicíclicos Bivariados e Lifted Product 2D

**Data:** 2026-10-27  
**Programa:** Descoberta com Códigos Quânticos Bicíclicos Bivariados e Geometrias Projetivas (P211–P220, D047)  
**Autor:** Agente Executor EvoByte  
**Status:** Concluído e Validado  

---

## 1. Resumo Executivo

A Fase **P213** implementou com sucesso o motor algébrico de códigos quânticos corretores de erros (QECC) bicíclicos bivariados (*bivariate bicycle codes*, Bravyi et al., 2024) e *lifted products* 2D em [`src/evobyte/bivariate_bicycle.py`](../../src/evobyte/bivariate_bicycle.py), acompanhado por suíte completa de testes unitários em [`tests/test_bivariate_bicycle.py`](../../tests/test_bivariate_bicycle.py).

### Principais Entregas
1. **Motor Bicíclico Bivariado (`BivariateBicycleEngine`):**
   - Construtor parametrizado sobre anéis $\mathbb{F}_2[\mathbb{Z}_l \times \mathbb{Z}_m] = \mathbb{F}_2[x, y] / \langle x^l - 1, y^m - 1 \rangle$.
   - Matrizes de verificação de paridade CSS com garantia matemática de 100% de ortogonalidade simplética:
     $$H_X = (M(A) \mid M(B)), \quad H_Z = (M(B)^T \mid M(A)^T)$$
     $$H_X H_Z^T = M(A)M(B) + M(B)M(A) \equiv 0 \pmod 2$$
   - Cálculo determinístico de posto sobre $\mathbb{F}_2$ via eliminação bit-paralela ultrarrápida (`fast_gf2_basis_and_indices`), reduzindo a latência para **$0.96$ ms por candidato em $n=72$** ($> 5\times$ mais rápido que a meta de $5$ ms).
2. **Motor de Lifted Products 2D (`LiftedProduct2DEngine`):**
   - Construção generalizada de produto hipergráfico a partir de matrizes clássicas e complexos de cadeias bivariados:
     $$H_X = (H_1 \otimes I_{m_2} \mid I_{m_1} \otimes H_2), \quad H_Z = (I_{n_1} \otimes H_2^T \mid H_1^T \otimes I_{n_2})$$
3. **Validação de Códigos de Referência Conhecidos:**
   - **Bravyi et al. (2024) $[[72, 12, 6]]$:** $l=6, m=6, k=12, d=6$, sparsidade $> 91.6\%$, verificado 100% no catálogo oficial de calibração.
   - **Família de Códigos Tóricos 2D de Kitaev $[[2 L^2, 2, L]]$:** $[[8, 2, 2]]$, $[[18, 2, 3]]$ e $[[32, 2, 4]]$.
   - **Código Bicíclico Bivariado $[[16, 2, 4]]$:** sobre $\mathbb{Z}_2 \times \mathbb{Z}_4$.

---

## 2. Fundamentação Algébrica e Comutatividade

Em um anel comutativo de grupo abeliano 2D $G = \mathbb{Z}_l \times \mathbb{Z}_m$, os geradores $x$ e $y$ satisfazem $x^l = 1$, $y^m = 1$ e $xy = yx$.
Para quaisquer polinômios $A(x, y), B(x, y) \in \mathbb{F}_2[\mathbb{Z}_l \times \mathbb{Z}_m]$, suas representações matriciais $M(A), M(B) \in \mathbb{F}_2^{lm \times lm}$ são matrizes circulantes em blocos que comutam estritamente:
$$M(A) M(B) = M(B) M(A)$$

A transposta $M(A)^T$ corresponde à involução algébrica $\tau(x^i y^j) = x^{-i} y^{-j} = x^{l-i} y^{m-j}$.
Assim:
$$H_X H_Z^T = \begin{pmatrix} M(A) & M(B) \end{pmatrix} \begin{pmatrix} M(B) \\ M(A) \end{pmatrix} = M(A) M(B) + M(B) M(A) \equiv 0 \pmod 2$$

Essa identidade elimina totalmente a perda de candidatos por violação simplética durante a busca evolutiva (taxa de aceitação simplética de $100\%$).

---

## 3. Desempenho e Medições Experimentais

### 3.1 Latência de Amostragem e Cálculo de Posto ($n = 72$, $l=6, m=6$)

Medição executada em bateria de 100 amostras com polinômios de peso 3:

| Operação | Tempo Médio | Fração do Ciclo |
| :--- | :--- | :--- |
| Amostragem aleatória de monômios | $0.012$ ms | $1.2\%$ |
| Avaliação matricial bivariada vetorial | $0.024$ ms | $2.5\%$ |
| Concatenação de blocos ($H_X, H_Z$) | $0.004$ ms | $0.4\%$ |
| Eliminação bit-paralela $\mathbb{F}_2$ (rank & basis) | $0.049$ ms | $5.1\%$ |
| Instanciação imutável e perfil de sparsidade | $0.871$ ms | $90.8\%$ |
| **Total por Candidato** | **$0.960$ ms** | **$100\%$** |

- **Throughput:** $> 1040$ códigos bivariados completos por segundo.
- **Portão de Latência (< 5 ms):** **APROVADO com margem de $5.2\times$**.

---

## 4. Códigos de Referência Validados

| Código | Anel $(l, m)$ | Polinômio $A(x, y)$ | Polinômio $B(x, y)$ | $\operatorname{rank}(H_X)$ | $\operatorname{rank}(H_Z)$ | $k$ | $d$ | Sparsidade |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Tórico $L=2$** | $(2, 2)$ | $1 + x$ | $1 + y$ | 3 | 3 | 2 | 2 | $50.0\%$ |
| **Bivariado $[[16, 2, 4]]$** | $(2, 4)$ | $1 + x + y^2 + xy^3$ | $y + x + xy^2 + xy^3$ | 7 | 7 | 2 | 4 | $50.0\%$ |
| **Tórico $L=3$** | $(3, 3)$ | $1 + x$ | $1 + y$ | 8 | 8 | 2 | 3 | $77.8\%$ |
| **Tórico $L=4$** | $(4, 4)$ | $1 + x$ | $1 + y$ | 15 | 15 | 2 | 4 | $87.5\%$ |
| **Bravyi et al. (2024)** | $(6, 6)$ | $x^3 + y + y^2$ | $y^3 + x + x^2$ | 30 | 30 | 12 | 6 | $91.67\%$ |

Todos os 5 códigos de referência foram verificados de forma determinística e com 100% de compatibilidade simplética.

---

## 5. Resposta à Pergunta Falsificável

> **Pergunta:** O gerador bivariado produz matrizes estabilizadoras com comutatividade simplética exata de 100%, cálculo determinístico de $k$ em tempo $< 5$ ms por candidato e suporte à parametrização de alvos com $n \in [18, 72]$ qubits?

**Resposta:** **SIM (CONFIRMADO)**.
- Comutatividade simplética exata de $100\%$ garantida por teorema algébrico e validada em testes unitários.
- Cálculo determinístico de $k$ em tempo médio de $0.960$ ms por candidato em $n=72$ (e $< 0.4$ ms para $n \le 24$).
- Suporte completo a parametrização de anéis $\mathbb{Z}_l \times \mathbb{Z}_m$ cobrindo os alvos $n=18, 20, 24, 32, 72$.
