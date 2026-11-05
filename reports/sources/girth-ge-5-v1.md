# Extrato Bibliográfico e Metas de Referência: Grafos sem C3 e C4 (Cintura >= 5)

**Identificador:** `sources/girth-ge-5-v1`  
**Data da conferência:** 5 de novembro de 2026  
**Tarefa associada:** F00-T01  
**Domínio:** Extremal Graphs sem triângulos ($C_3$) e sem ciclos de 4 vértices ($C_4$), isto é, $ex(n; \{C_3, C_4\})$, equivalendo a grafos simples não-direcionados com cintura $g \ge 5$.

---

## 1. Fontes Primárias Auditadas

### R1 — Garnick, Kwong e Lazebnik (1993)
- **Citação:** David K. Garnick, Y. H. Harris Kwong e Felix Lazebnik, *Extremal Graphs without Three-Cycles or Four-Cycles*, Journal of Graph Theory, Vol. 17, No. 5 (1993), pp. 633–645.
- **Acesso:** [https://www.dcs.gla.ac.uk/~pat/jchoco/extremal/papers/10.1.1.92.3502.pdf](https://www.dcs.gla.ac.uk/~pat/jchoco/extremal/papers/10.1.1.92.3502.pdf)
- **Seção auditada:** Tabela 1 (pág. 635) e Teoremas 1–3.
- **Valores documentados:** Determina valores exatos comprovados de $ex(n; \{C_3, C_4\})$ para $n \le 24$:
  - $n=8 \implies 10$ arestas
  - $n=10 \implies 15$ arestas
  - $n=12 \implies 18$ arestas
  - $n=16 \implies 28$ arestas
  - $n=18 \implies 34$ arestas
  - $n=20 \implies 41$ arestas
  - $n=24 \implies 54$ arestas
- **Rigor metodológico:** Distingue explicitamente valores exatos provados de construções isoladas (que fornecem apenas cotas inferiores).

### R2 — Miller e Codish (2017)
- **Citação:** Alice Miller e Michael Codish, *Graphs with girth at least 5 with orders between 20 and 32*, arXiv:1708.06576v2 [math.CO], submetido em 22 de agosto de 2017, versão 2 de 23 de agosto de 2017.
- **Acesso registro:** [https://arxiv.org/abs/1708.06576v2](https://arxiv.org/abs/1708.06576v2)
- **Acesso texto completo:** [https://arxiv.org/html/1708.06576v2](https://arxiv.org/html/1708.06576v2)
- **Seção auditada:** Seção 1 (Introdução), Tabela 1 (pág. 3) e Apêndices A/B.
- **Valores documentados:** Enumeração exata com quebra de simetria estabelecendo os máximos:
  - $f(20) = 41$
  - $f(24) = 54$
  - $f(28) = 68$
  - $f(32) = 85$
- **Rigor metodológico:** Confirmação de que os limites nos tamanhos confirmatórios finais (24, 28 e 32) são ótimos conhecidos e certificados na literatura matemática, servindo exclusivamente como metas de reprodução e calibração de baselines.

### R3 — Afzaly e McKay (Coleção ANU)
- **Citação:** Narjess Afzaly e Brendan D. McKay, *Extremal Graphs and Turan numbers*, Department of Computer Science, Australian National University.
- **Acesso:** [https://users.cecs.anu.edu.au/~bdm/data/extremal.html](https://users.cecs.anu.edu.au/~bdm/data/extremal.html)
- **Seção auditada:** Subseção $\mathcal{H} = \{C_3, C_4\}$ (*Graphs without triangles and 4-cycles*).
- **Alerta de integridade:** Proibido utilizar a seção $\{C_4\}$, cujos valores são divergentes (admite triângulos). A seção correta proíbe ambos $C_3$ e $C_4$.
- **Valores auditados (sem prefixo '>=', valores exatos):**
  - $n=8: 10$
  - $n=9: 12$
  - $n=10: 15$
  - $n=11: 16$
  - $n=12: 18$
  - $n=13: 21$
  - $n=14: 23$
  - $n=15: 26$
  - $n=16: 28$
  - $n=17: 31$
  - $n=18: 34$
  - $n=19: 38$
  - $n=20: 41$
  - $n=21: 44$
  - $n=22: 47$
  - $n=23: 50$
  - $n=24: 54$
  - $n=25: 57$
  - $n=26: 61$
  - $n=27: 65$
  - $n=28: 68$
  - $n=29: 72$
  - $n=30: 76$
  - $n=31: 80$
  - $n=32: 85$
- **Rigor metodológico:** Os arquivos sparse6 da coleção não integram o conjunto de dados nem são utilizados para inicialização; todos os métodos iniciam do grafo vazio.

### R4 — Goedgebeur, Jooken, Joret e Van den Eede (2026)
- **Citação:** Jan Goedgebeur, Jorik Jooken, Gwenaël Joret e Tibo Van den Eede, *Improved lower bounds on the maximum size of graphs with girth 5*, arXiv:2508.05562v2 [math.CO], 22 de setembro de 2026.
- **Acesso registro:** [https://arxiv.org/abs/2508.05562v2](https://arxiv.org/abs/2508.05562v2)
- **Acesso seção 2:** [https://arxiv.org/html/2508.05562v2#S2](https://arxiv.org/html/2508.05562v2#S2)
- **Seção auditada:** Seção 2 (Heurística de busca local com reinícios e remoções).
- **Limites da adaptação para o EvoByte:** O algoritmo original de R4 utiliza perturbações com memória e transferência estrutural de grafos entre ordens vizinhas ($n \to n+1$). O EvoByte implementa uma adaptação local simplificada (`local_manual`), executada independentemente por ordem $n$ a partir do grafo nulo, sem transferência entre tamanhos.

---

## 2. Consolidação das Metas dos Nove Tamanhos da Campanha

Conforme pré-especificado em `docs/01-scientific-protocol.md`:

| Função no Protocolo | Ordem ($n$) | Meta Exata Conhecida ($m$) | Fontes Primárias Comprovadas |
|---|---|---|---|
| **Desenvolvimento** | 8 | 10 | R1 (Tab. 1), R3 ($\mathcal{H}=\{C_3,C_4\}$) |
| **Desenvolvimento** | 10 | 15 | R1 (Tab. 1), R3 ($\mathcal{H}=\{C_3,C_4\}$) |
| **Desenvolvimento** | 12 | 18 | R1 (Tab. 1), R3 ($\mathcal{H}=\{C_3,C_4\}$) |
| **Desenvolvimento** | 16 | 28 | R1 (Tab. 1), R3 ($\mathcal{H}=\{C_3,C_4\}$) |
| **Ajuste / Piloto** | 18 | 34 | R1 (Tab. 1), R3 ($\mathcal{H}=\{C_3,C_4\}$) |
| **Ajuste / Piloto** | 20 | 41 | R1 (Tab. 1), R2 (Tab. 1), R3 ($\mathcal{H}=\{C_3,C_4\}$) |
| **Confirmação Final**| 24 | 54 | R1 (Tab. 1), R2 (Tab. 1), R3 ($\mathcal{H}=\{C_3,C_4\}$) |
| **Confirmação Final**| 28 | 68 | R2 (Tab. 1), R3 ($\mathcal{H}=\{C_3,C_4\}$) |
| **Confirmação Final**| 32 | 85 | R2 (Tab. 1), R3 ($\mathcal{H}=\{C_3,C_4\}$) |

---

## 3. Delimitações e Vedações Científicas

1. **Ausência de Novidade nos Valores:** Os valores $m \in \{10, 15, 18, 28, 34, 41, 54, 68, 85\}$ são fatos matemáticos conhecidos e comprovados. Encontrar ou reproduzir uma construção com 54 arestas em $n=24$, 68 em $n=28$ ou 85 em $n=32$ constitui **estritamente validação de eficácia de busca**, e em nenhuma hipótese pode ser declarada novidade científica ou descoberta de recorde mundial.
2. **Sem Vazamento de Grafos:** As representações explícitas das construções de R1, R2 e R3 estão blindadas e não podem ser baixadas, embutidas em código de teste, usadas para treino supervisionado ou carregadas como sementes de busca. Todos os algoritmos partem de um grafo vazio ($E = \emptyset$).
3. **Condições da Hipótese H1:** A hipótese H1 é puramente comparativa sob orçamento uniforme de 600 segundos de tempo de parede: avalia se a política linear aprendida (`local_linear`) alcança média de arestas superior em pelo menos 1 aresta em relação à melhor referência não aprendida ($B^*$) nos tamanhos 24, 28 e 32, contabilizando o custo de partida.
