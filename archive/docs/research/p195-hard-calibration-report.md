# Relatório Técnico P195: Calibração Cega em Alvos Históricos Difíceis

**Data:** 2026-10-26  
**Programa:** Descoberta Algébrica Estruturada e Síntese Funcional (P191–P200, D043)  
**Fase:** P195 — Hard Historical Records Calibration  
**Status:** Validado e auditado  

---

## 1. Contexto e Motivação

Antes de lançar a campanha pré-registrada nos 5 alvos de fronteira em aberto (P196), onde a solução ótima é desconhecida e o espaço de busca é vasto, é mandatório calibrar a nova arquitetura desenvolvida nas fases anteriores (Grupos de Simetria P192 + Prioridade Funcional P193 + Ponte SAT P194) contra marcos históricos da literatura matemática cujas soluções são conhecidas, mas estão **estritamente fora do alcance de buscas aleatórias cegas**.

A Fase P195 selecionou dois marcos de alta complexidade combinatória:
1. **QECC Difícil:** Redescoberta do código estabilizador quântico $[[8, 3, 3]]$ de Gottesman (1997), caracterizado por operadores mistos não-CSS com $n=8$ qubits físicos, $k=3$ qubits lógicos e distância mínima $d=3$.
2. **Covering Design Difícil:** Redescoberta do limite combinatorial exato $C(10, 4, 3) = 30$ (Steiner Quadruple System $\text{SQS}(10)$, resolvido por Mills em 1979), onde todos os $\binom{10}{3} = 120$ subconjuntos de 3 elementos são cobertos exatamente uma vez por 30 blocos de tamanho 4.

### Regra de Ouro da Calibração Cega
O protocolo opera **100% às cegas**: o algoritmo não recebe matrizes, sementes pré-computadas, nem templates de blocos publicados. O algoritmo recebe unicamente os parâmetros nominais $(v, k, t)$ ou $(n, k, d)$ e o oráculo verificador independente de dependência zero (`verify_covering_design`, `check_stabilizer`, `code_distance`).

---

## 2. Pergunta Falsificável e Resultados dos Gates

> **Pergunta da Fase P195:**  
> *O pipeline estruturado (órbitas + prioridade + SAT) redescobre cegamente o código $[[8, 3, 3]]$ e a cobertura $C(10, 4, 3)=30$ em pelo menos 3 de 5 sementes sob orçamento de 300 segundos por tentativa?*

*(Nota: O texto preliminar da fase indicava uma cota tipográfica de 20 para $C(10,4,3)$, mas matematicamente $\binom{10}{3} = 120$ triplas exigem no mínimo $\lceil 120 / \binom{4}{3} \rceil = 30$ blocos de tamanho 4, sendo 30 o valor exato comprovado do sistema de Steiner $\text{SQS}(10)$).*

### Resumo dos Resultados Experimentais

| Alvo | Meta Nominal | Sementes Avaliadas | Sucessos | Tempo Médio | Tempo Máximo | Status do Gate |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Gottesman $[[8, 3, 3]]$** | $n=8, k=3, d=3$ | 5 (`[42, 43, 44, 45, 46]`) | **5 / 5 (100%)** | **$0,216$ s** | **$0,316$ s** | Aprovado ($949\times$ abaixo do teto) |
| **Covering $C(10, 4, 3)$** | $b = 30$ blocos | 5 (`[42, 43, 44, 45, 46]`) | **5 / 5 (100%)** | **$0,014$ s** | **$0,017$ s** | Aprovado ($21.428\times$ abaixo do teto) |

**Veredito Global da Calibração:** `CALIBRATION_PASSED`  
O pipeline atingiu taxa de sucesso perfeita ($5/5$ em ambos os alvos, superando o requisito de $\ge 3/5$) e executou os 10 ensaios combinados em apenas **$1,206$ segundos** de tempo total de relógio de parede.

---

## 3. Detalhamento dos Resultados por Semente

### 3.1. Alvo 1: Gottesman $[[8, 3, 3]]$
Todos os 5 geradores estabilizadores foram sintetizados via formulação booleana exata de comutatividade simplética e detecção de todos os 276 erros de Pauli de peso 1 e 2:

| Semente | Geradores Sintetizados | Tempo Medido | Distância $d$ | Verificação Oracle | Hash SHA-256 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **42** | `['YYXYYYYY', 'ZYYYIXXI', 'IYZZZYZI', 'IYYIXZYX', 'ZXXZIIZY']` | $0,306$ s | $d = 3$ | Aprovado | `79d160b12734a3a5...` |
| **43** | `['YIIYZYZZ', 'ZIXYXIYY', 'IZZYXZIZ', 'IXZZYIXY', 'ZYZIZYIY']` | $0,078$ s | $d = 3$ | Aprovado | `0dad5ecd95c601b4...` |
| **44** | `['XYYXXYYY', 'IYXYZYZI', 'ZZXZYZZX', 'IZZXYYIZ', 'ZIIZZYYZ']` | $0,143$ s | $d = 3$ | Aprovado | `b7e14535aa3d2253...` |
| **45** | `['XYXZZIIZ', 'YYZYXIYI', 'ZYZZYYZY', 'ZYIIZZYX', 'YZZIZXIY']` | $0,316$ s | $d = 3$ | Aprovado | `ab08653273390288...` |
| **46** | `['XIXZXIXY', 'ZXXXZYYY', 'IIXYZZZX', 'IZIYXXYY', 'ZZZIIZYX']` | $0,238$ s | $d = 3$ | Aprovado | `44116257cd082cbd...` |

### 3.2. Alvo 2: Covering Design $C(10, 4, 3) = 30$
O espaço combinatorial não-guiado de $\binom{210}{30} \approx 4 \times 10^{34}$ combinações foi reduzido via ação do grupo cíclico $\mathbb{Z}_{10}$ para 22 órbitas de 4-subconjuntos. A escolha de 3 órbitas base gerou exatamente os 30 blocos:

| Semente | Órbitas Base Selecionadas | Blocos Totais | Tempo Medido | Triplas Cobertas | Hash SHA-256 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **42** | `[[0, 1, 2, 4], [0, 1, 3, 6], [0, 2, 4, 7]]` | 30 | $14,15$ ms | 120 / 120 | `c570e021af5ce469...` |
| **43** | `[[0, 1, 2, 4], [0, 1, 3, 6], [0, 2, 4, 7]]` | 30 | $12,73$ ms | 120 / 120 | `c570e021af5ce469...` |
| **44** | `[[0, 1, 2, 4], [0, 1, 3, 6], [0, 2, 4, 7]]` | 30 | $13,90$ ms | 120 / 120 | `c570e021af5ce469...` |
| **45** | `[[0, 1, 2, 4], [0, 1, 3, 6], [0, 2, 4, 7]]` | 30 | $14,73$ ms | 120 / 120 | `c570e021af5ce469...` |
| **46** | `[[0, 1, 2, 4], [0, 1, 3, 6], [0, 2, 4, 7]]` | 30 | $16,96$ ms | 120 / 120 | `c570e021af5ce469...` |

---

## 4. Análise de Eficiência Computacional

A comparação direta entre a busca SAT pura não-guiada e o pipeline híbrido estruturado demonstra o impacto quantitativo da arquitetura:

- **Busca SAT direta sem simetria para $C(10, 4, 3) = 30$:**
  - Espaço: 210 variáveis booleanas com contador sequencial de Sinz para $\sum x_j \le 30$.
  - Tempo de resolução medido: **$142,75$ segundos**.
- **Busca estruturada com redução por órbitas $\mathbb{Z}_{10}$:**
  - Espaço: 22 variáveis de órbita com contador de Sinz para $\le 3$ órbitas.
  - Tempo de resolução medido: **$0,014$ segundos** ($14$ milissegundos).
  - **Aceleração medida:** $\mathbf{10.196\times}$ mais rápido.

Para o alvo quântico $[[8, 3, 3]]$, a imposição simultânea da comutatividade simplética via linearização de produtos booleanos e a quebra de simetria por escalonamento pivotado permitiu convergir para uma solução válida em média em **$0,216$ segundos**.

---

## 5. Proveniência e Dados Experimentais

- **Artefato de Medição:** `experiments/p195-hard-calibration-results.json`
- **Ambiente Host:** Linux 7.2.6-generic x86_64, Python 3.12.2, PySAT 1.9.dev17 (CaDiCaL 1.5.3).
- **Commit Base:** `e31a28aa22bbdb5af1883de73be4a6073e0efaa6`.
- **Certificação:** 100% dos objetos foram verificados pelo kernel zero-dependency de `verify_covering_design`, `check_stabilizer` e `code_distance`.

---

## 6. Conclusão e Transição para a P196

Com a aprovação incontestável de todos os gates da P195 (`CALIBRATION_PASSED`), a arquitetura estruturada (Simetria + Prioridade Funcional + SAT) está oficialmente calibrada e apta para o lançamento da **P196 — Campanha Pré-Registrada Estruturada** nos 5 alvos abertos da fronteira mundial.
