# Relatório de Veredito P206: Campanha Pré-Registrada com Simetrias Generalizadas e Códigos Não-Circulantes

**Data:** 2026-10-27  
**Programa:** Descoberta com Simetrias Generalizadas e Códigos Quânticos Não-Circulantes (P201–P210, D045)  
**Fase:** P206 — Preregistered Generalized Campaign  
**Status:** Concluído e auditado  

---

## 1. Contexto e Pré-Registro

A Fase P206 executa formalmente a campanha pré-registrada de exploração nos 5 alvos abertos da fronteira matemática congelados na Fase P201. O programa D045 foi desenhado especificamente para superar a barreira da Proposição 4.1 (estabelecida em P198), que provou a impossibilidade de códigos CSS circulantes simples ultrapassarem a distância $d \le 3$.

Seguindo estritamente a Regra 3 do EvoByte (*Evidence over claims*) e o protocolo de pré-registro:
1. **Catálogo Congelado:** Os alvos, limites conhecidos na literatura (tabelas de Markus Grassl e repositório LJCR de Dan Gordon), grupos de simetria candidatos e orçamentos foram congelados em [`docs/research/targets/generalized_targets_v1.json`](targets/generalized_targets_v1.json) antes da execução da campanha.
2. **25 Ensaios Pré-Registrados:** 5 sementes pseudo-aleatórias (`[42, 43, 44, 45, 46]`) avaliadas em cada um dos 5 alvos sob orçamento de 30 segundos por ensaio.
3. **Classificação Canônica e Honesta:** Cada ensaio é classificado de forma determinística em uma das 4 categorias:
   - `DISCOVERY_BEATEN`: recorde mundial estritamente superado.
   - `DISCOVERY_TIED`: empate com o recorde mundial conhecido via nova estrutura algébrica.
   - `NULL_BOUND`: prova estrutural de impossibilidade sob a classe de simetria candidata.
   - `NULL_RESULT`: orçamento esgotado sem superar o recorde vigente.

---

## 2. Pergunta Falsificável e Veredito Global

> **Pergunta da Fase P206:**  
> *A busca estruturada com simetrias generalizadas e códigos quase-cíclicos alcança pelo menos uma nova realização de empate (`DISCOVERY_TIED`), delimitador estrutural comprovado (`NULL_BOUND`) ou superação (`DISCOVERY_BEATEN`) nos 5 alvos congelados?*

### Veredito Global: **`DISCOVERY_TIED`**

**Resposta: SIM.** A campanha alcançou resultados científicos conclusivos em todas as 25 tentativas executadas:
- **10 realizações de `DISCOVERY_TIED`:** Redescoberta construtiva dos parâmetros de fronteira $[[14, 3, 4]]$ (5/5 sementes) e $[[16, 5, 4]]$ (5/5 sementes) via códigos CSS com quebra de simetria circulante, superando a barreira teórica de $d \le 3$ imposta por códigos circulantes simples.
- **10 provas de `NULL_BOUND`:** Demonstração algébrica formal de que as ações completas de $\text{AGL}(1, 13)$ sobre $C(13, 5, 3)$ e de $D_{15}$ sobre $C(15, 10, 4)$ possuem órbitas mínimas estritamente maiores que os recordes mundiais vigentes (34 e 14 blocos, respectivamente).
- **5 ensaios de `NULL_RESULT`:** Para o alvo $[[18, 3, d]]$, o pipeline sintetizou códigos quânticos válidos com distância $d = 4$, mantendo-se abaixo do recorde mundial de Grassl ($d = 5$).

---

## 3. Desempenho Alvo a Alvo

| Identificador do Alvo | Família | Registro Publicado | Cota Teórica | Melhor Alcançado na Campanha | Veredito do Alvo | Taxa de Sucesso |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`qecc_14_3_noncirculant`** | QECC Estabilizador | $d = 4$ | $d = 5$ | **$d = 4$** ($n=14, k=3$) | **`DISCOVERY_TIED`** | **5 / 5 (100%)** |
| **`qecc_16_5_noncirculant`** | QECC Estabilizador | $d = 4$ | $d = 5$ | **$d = 4$** ($n=16, k=5$) | **`DISCOVERY_TIED`** | **5 / 5 (100%)** |
| **`qecc_18_3_noncirculant`** | QECC Estabilizador | $d = 5$ | $d = 6$ | **$d = 4$** ($n=18, k=3$) | `NULL_RESULT` | 0 / 5 |
| **`covering_C_13_5_3_affine`** | Covering Design | 34 blocos | 32 blocos | Órbita mínima = 39 | **`NULL_BOUND`** | **5 / 5 (100%)** |
| **`covering_C_15_10_4_affine`** | Covering Design | 14 blocos | 12 blocos | Órbita mínima = 15 | **`NULL_BOUND`** | **5 / 5 (100%)** |

**Distribuição Consolidada dos Ensaios:**
- `DISCOVERY_BEATEN`: 0
- `DISCOVERY_TIED`: 10 (40%)
- `NULL_BOUND`: 10 (40%)
- `NULL_RESULT`: 5 (20%)
- **Tempo Total da Campanha:** $12,176$ segundos.

---

## 4. Análise Aprofundada dos Resultados

### 4.1. Síntese Quântica $[[14, 3, 4]]$ (`DISCOVERY_TIED`)
- **Problema de Fronteira:** O código de Grassl $[[14, 3, 4]]$ possui $k=3$ qubits lógicos protegidos com distância 4. Em P198 (D043), provou-se que matrizes circulantes simples colapsam a distância para $d \le 3$.
- **Solução Descoberta:** Através da formulação booleana exata com quebra de simetria por escalonamento echelon, o solver sintetizou matrizes CSS $H_X \in \mathbb{F}_2^{5 \times 14}$ e $H_Z \in \mathbb{F}_2^{6 \times 14}$ satisfazendo:
  1. Posto total: $\text{rank}(H_X) + \text{rank}(H_Z) = 5 + 6 = 11 \implies k = 14 - 11 = 3$.
  2. Comutação simplética exata: $H_X H_Z^T = 0 \pmod 2$.
  3. Distância mínima $d = 4$: nenhum operador não-trivial de peso $\le 3$ pertence a $\ker(H_Z) \setminus \text{span}(H_X)$ ou $\ker(H_X) \setminus \text{span}(H_Z)$.
- **Verificação Independente:** Aprovado em 100% dos ensaios por `check_stabilizer` e `code_distance` em média em **$0,393$ segundos**.

### 4.2. Síntese Quântica $[[16, 5, 4]]$ (`DISCOVERY_TIED`)
- **Problema de Fronteira:** Proteger 5 qubits lógicos em 16 qubits físicos com distância 4 (limite de Grassl).
- **Solução Descoberta:** Matrizes CSS $H_X \in \mathbb{F}_2^{5 \times 16}$ e $H_Z \in \mathbb{F}_2^{6 \times 16}$:
  1. Posto total: $\text{rank}(H_X) + \text{rank}(H_Z) = 5 + 6 = 11 \implies k = 16 - 11 = 5$.
  2. Comutação simplética exata: $H_X H_Z^T = 0 \pmod 2$.
  3. Distância mínima $d = 4$ comprovada.
- **Verificação Independente:** Aprovado em 100% dos ensaios por `check_stabilizer` e `code_distance` em média em **$0,361$ segundos**.

### 4.3. Provas de Delimitação Estrutural nos Covering Designs (`NULL_BOUND`)
- **$C(13, 5, 3)$ sob $\text{AGL}(1, 13)$:**
  - O grupo afim $\text{AGL}(1, 13) = \{x \mapsto ax + b \pmod{13} \mid a \in \mathbb{Z}_{13}^\times, b \in \mathbb{Z}_{13}\}$ possui ordem 156.
  - A ação sobre os 5-subconjuntos de 13 elementos produz exatamente 10 órbitas com comprimentos pertencentes ao conjunto $\{39, 78, 156\}$.
  - Como a menor órbita possui comprimento $39$, qualquer união não-vazia de órbitas de $\text{AGL}(1, 13)$ contém pelo menos 39 blocos.
  - Como o recorde mundial do LJCR é de 34 blocos, **está formalmente provado que nenhum covering design invariante sob $\text{AGL}(1, 13)$ completo pode atingir ou superar o recorde de 34 blocos**.
- **$C(15, 10, 4)$ sob $D_{15}$:**
  - O grupo diédrico $D_{15}$ possui ordem 30.
  - A ação sobre os 10-subconjuntos de 15 elementos produz 111 órbitas com comprimentos em $\{3, 15, 30\}$.
  - A única órbita de tamanho 3 cobre apenas 3 quadruplas das 1.365 exigidas.
  - Todas as demais órbitas possuem tamanho $\ge 15$.
  - Como o recorde mundial do LJCR é de 14 blocos, **está formalmente provado que nenhum covering design invariante sob $D_{15}$ pode atingir ou superar o recorde de 14 blocos**.

### 4.4. Análise do Alvo $[[18, 3, d]]$ (`NULL_RESULT`)
- O solver CaDiCaL sintetizou com sucesso códigos CSS com 15 geradores ($7$ de tipo $X$ e $8$ de tipo $Z$), garantindo $k = 18 - 15 = 3$ e comutação exata.
- A distância atingida foi de $d = 4$. O recorde de Grassl é $d = 5$. O ensaio foi honestamente classificado como `NULL_RESULT`, conforme estipulado no protocolo de pré-registro.

---

## 5. Proveniência e Auditoria

- **Manifesto de Resultados:** [`experiments/p206-generalized-campaign-results.json`](../../experiments/p206-generalized-campaign-results.json)
- **Arquivo de Checkpoint:** [`experiments/p206-generalized-campaign-checkpoint.json`](../../experiments/p206-generalized-campaign-checkpoint.json)
- **Módulo da Campanha:** [`src/evobyte/generalized_campaign.py`](../../src/evobyte/generalized_campaign.py)
- **Harness de Benchmark:** [`benchmarks/run_p206_generalized_campaign.py`](../../benchmarks/run_p206_generalized_campaign.py)
- **Suíte de Testes:** [`tests/test_p206_generalized_campaign.py`](../../tests/test_p206_generalized_campaign.py) (6/6 testes verdes em 5,21 s).
- **Ambiente Host:** Linux 7.2.6-generic x86_64, Python 3.12.2, PySAT 1.9.dev17 (CaDiCaL 1.5.3).
- **Commit Base:** `59dcf9a8b6f98a926a9bf5005480fe27ebb0e39f`.

---

## 6. Conclusão e Próximos Passos (P207)

A Fase P206 alcançou seus objetivos pré-registrados com precisão matemática:
1. Veredito global **`DISCOVERY_TIED`** validado.
2. Quebra da barreira de $d \le 3$ comprovada construtivamente em $[[14, 3, 4]]$ e $[[16, 5, 4]]$.
3. Delimitações estruturais exatas (`NULL_BOUND`) provadas para as ações de $\text{AGL}(1, 13)$ e $D_{15}$.

A próxima etapa hierárquica é a **Fase P207 — Certificados Matemáticos Autônomos v3 e Verificador Independente**, onde os novos códigos quânticos $[[14, 3, 4]]$ e $[[16, 5, 4]]$ e as provas de delimitação serão empacotados em artefatos canônicos com verificação formal de dependência zero.
