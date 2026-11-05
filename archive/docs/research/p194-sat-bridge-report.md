# Relatório Técnico P194: Ponte de Hibridização EvoByte → Solver SAT (SAT Completion Bridge)

**Data:** 2026-10-26
**Programa:** Descoberta Algébrica Estruturada e Síntese Funcional (P191–P200, D043)
**Fase:** P194 — SAT Solver Exact Completion Bridge
**Status:** Validado e auditado

---

## 1. Contexto e Motivação

Algoritmos genéticos, síntese em bytecode e métodos estocásticos (como os motores desenvolvidos em P192 e P193) são notavelmente eficazes em descobrir a macro-estrutura de soluções combinatórias extremais: conseguem atingir rapidamente de 90% a 98% das restrições satisfeitas. No entanto, esses métodos estocásticos sofrem do clássico **"problema do último bit"** (*last-mile gap*): à medida que o número de restrições violadas cai para menos de 5%, qualquer mutação aleatória nos blocos existentes tende a desmanchar dezenas de restrições já satisfeitas, exigindo um esforço computacional exponencial para fechar as últimas violações.

Por outro lado, solvers SAT modernos baseados em CDCL (*Conflict-Driven Clause Learning*), como CaDiCaL, Glucose e Minisat, são imbatíveis na propagação de restrições unitárias e resolução exata de restrições booleanas discretas, mas enfrentam explosão combinatória quando aplicados sobre todo o espaço combinatorial sem simetrias ou sem heurísticas estruturais de guiamento.

A **Fase P194 implementa a ponte de hibridização**:
1. O EvoByte encontra o esqueleto inicial (subconjunto de órbitas ou blocos base sob o grupo de automorfismo $\mathbb{Z}_v$).
2. O problema residual (completar a cobertura dos $t$-subconjuntos remanescentes respeitando o limite máximo de blocos $B$) é formulado em Forma Normal Conjuntiva (CNF).
3. Um contador sequencial de Sinz codifica a restrição de cardinalidade $\sum x_j \le K$ em $O(N \cdot K)$ cláusulas com garantia de consistência de arco sob propagação unitária.
4. O solver SAT CDCL resolve o problema residual em milissegundos.
5. A solução montada é estritamente validada pelo verificador independente de dependência zero (`verify_covering_design`, `check_stabilizer`).

---

## 2. Pergunta Falsificável e Resultados dos Gates

> **Pergunta da Fase P194:**
> *A ponte híbrida EvoByte + SAT (com codificação CNF exata) consegue resolver instâncias residuais de covering design que a busca estocástica pura rejeitou por violações remanescentes, com orçamento de tempo menor que 5 segundos por chamada de SAT?*

### Resumo dos Resultados Experimentais

| Instância / Alvo | Macro-Esqueleto Fixado | Restrições Remanescentes | Tempo SAT Medido | Solução Verificada | Status do Gate |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **$C(7, 3, 2)$** | 5 de 7 blocos (Fano) | 6 pares descobertos | **$0,464$ ms** | Sim (`verify_covering_design`) | Aprovado ($10.775\times$ mais rápido que o teto) |
| **$C(8, 4, 3)$** | 11 de 14 blocos | 12 triplas descobertas | **$0,809$ ms** | Sim (`verify_covering_design`) | Aprovado ($6.180\times$ mais rápido que o teto) |
| **$C(13, 6, 3)$** | Órbitas $\mathbb{Z}_{13}$ ($k_{\text{base}} \le 2$) | 286 triplas | **$40,90$ ms** | Sim (26 blocos expandidos) | Aprovado ($122\times$ mais rápido que o teto) |
| **$C(14, 6, 3)$** | Órbitas $\mathbb{Z}_{14}$ ($k_{\text{base}} \le 2$) | 364 triplas | **$82,08$ ms** | Sim (28 blocos expandidos) | Aprovado ($60,9\times$ mais rápido que o teto) |
| **$C(15, 8, 4)$** | Órbitas $\mathbb{Z}_{15}$ ($k_{\text{base}} \le 2$) | 1.365 quádruplas | **$483,13$ ms** | Sim (30 blocos, iguala recorde LJCR) | Aprovado ($10,35\times$ mais rápido que o teto) |
| **Steane $[[7, 1, 3]]$** | 4 geradores fixados | Comutatividade simplética | **$0,24$ ms** | Sim (`check_stabilizer`) | Aprovado ($20.833\times$ mais rápido que o teto) |

**Conclusão Falsificável:** Sim. Em todas as instâncias avaliadas, a ponte SAT resolveu o resíduo combinatorial em menos de $0,5$ segundo (entre $10\times$ e $20.000\times$ mais rápido que o orçamento máximo de 5 segundos), e 100% das soluções completas geradas foram rigorosamente aprovadas pelo verificador de dependência zero.

---

## 3. Arquitetura da Ponte SAT (`sat_bridge.py`)

### 3.1. Codificação CNF e Contador Sequencial de Sinz
A restrição de cardinalidade "selecionar no máximo $K$ blocos candidatos dentre $N$" ($\sum_{j=1}^N x_j \le K$) é codificada utilizando o contador sequencial de Sinz (*Towards an Optimal CNF Encoding of Boolean Cardinality Constraints*, CP 2005):
- Introduz variáveis auxiliares $s_{i, j}$ para $1 \le i \le N-1$ e $1 \le j \le K$, significando que pelo menos $j$ variáveis entre $x_1, \dots, x_i$ são verdadeiras.
- As cláusulas de propagação de escada:
  $$\neg x_i \lor s_{i, 1}$$
  $$\neg s_{i-1, 1} \lor s_{i, 1}$$
  $$\neg x_i \lor \neg s_{i-1, j-1} \lor s_{i, j}$$
  $$\neg s_{i-1, j} \lor s_{i, j}$$
- Cláusula de teto no limite $K$:
  $$\neg x_i \lor \neg s_{i-1, K}$$
- Garante consistência de arco completa: assim que $K$ variáveis tornam-se verdadeiras, a propagação unitária força imediatamente todas as $N - K$ variáveis restantes para falso, podando ramos mortos no espaço de busca.

### 3.2. Restrições Lineares sobre $\mathbb{F}_2$ (Cláusulas XOR / Tseitin)
Para códigos estabilizadores quânticos QECC, a comutatividade simplética entre operadores de Pauli:
$$\sum_{j=1}^n (x_{A, j} z_{B, j} + z_{A, j} x_{B, j}) \equiv 0 \pmod 2$$
é expressa como um encadeamento de paridade XOR. O método `add_xor` decompõe somas de paridade de tamanho arbitrário em cláusulas ternárias via variáveis auxiliares de Tseitin em $O(p)$ cláusulas, permitindo síntese instantânea ($0,24$ ms) de geradores comutantes.

### 3.3. Comparativo de Motores de Resolução (Backends)

O benchmark comparou os seguintes motores para resolver o problema de complementação de $C(7, 3, 2)$ ($5 \to 7$ blocos):

| Motor SAT | Tempo de Resolução | Verificado por Verificador Independente |
| :--- | :--- | :--- |
| **Glucose 4 (`g4`)** | **$0,325$ ms** | Sim (`verify_covering_design`) |
| **CaDiCaL 1.5.3 (`cadical153`)** | **$0,503$ ms** | Sim (`verify_covering_design`) |
| **Pure Python DPLL (`pure_python`)** | **$6,221$ ms** | Sim (`verify_covering_design`) |

O motor em Python puro (`PurePythonSolver`) fornece uma garantia absoluta de fallback sem dependências externas, mantendo tempo de execução estritamente na casa dos milissegundos para instâncias residuais.

---

## 4. Evidência Experimental e Hardware

Os dados numéricos foram medidos e registrados no artefato:
`docs/research/benchmarks/p194_sat_bridge_results.json`

- **Ambiente de Medição:** Linux 7.2.6-generic x86_64, Python 3.12.2.
- **Bibliotecas SAT:** PySAT 1.9.dev17 (incluindo CaDiCaL 1.5.3 e Glucose 4 C++ wrappers).
- **Commit Base:** `0fc2647d3670c2da3a819deb6bf0faf2f55eb45b`.
- **Hashes Criptográficos das Descobertas:**
  - $C(7, 3, 2)$ (7 blocos): `1f9261311da07a83a59b6ae596305ac94d768d1ec8cf9ae965e9045a864bc524`
  - $C(8, 4, 3)$ (14 blocos): `ea093100a2e9ae6cdb8ea03c3f2aa4f497b6225ac53852ab9a9f421ce7fc3911`
  - $C(13, 6, 3)$ (26 blocos): `6a6c1e9baeec1c997280057127a3cfb761e69032a56b502e5951b133c4cd770e`
  - $C(14, 6, 3)$ (28 blocos): `eb5d0de9a23a25dd551fc3e9151e4cfe3ec5e7cdc5bfc9e32d1c3b70ab22225e`
  - $C(15, 8, 4)$ (30 blocos): `f6bc07d7386c49e82000f67f4061bfa8b2e6cbbe20a51dfc7f880732df042f0e`

---

## 5. Próximos Passos (P195 e Diante)

Com a ponte SAT validada e integrada ao catálogo de órbitas (P192) e ao motor de prioridade funcional (P193), a próxima etapa (**P195 — Calibração em Registros Históricos Difíceis**) consiste em submeter o pipeline híbrido completo à reprodução autônoma dos limites conhecidos e calibração de hiperparâmetros antes da campanha de registro formal (P196).
