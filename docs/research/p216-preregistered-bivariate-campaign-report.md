# Relatório de Veredito P216: Campanha Pré-Registrada com Códigos Bicíclicos Bivariados e Geometrias Projetivas

**Data:** 2026-10-28  
**Programa:** Descoberta com Códigos Quânticos Bicíclicos Bivariados e Geometrias Projetivas (P211–P220, D047)  
**Fase:** P216 — Preregistered Bivariate Campaign  
**Status:** Concluído e auditado com Gates 100% Verdes  

---

## 1. Contexto e Pré-Registro

A Fase P216 executa formalmente a campanha pré-registrada de exploração nos 5 alvos abertos da fronteira matemática congelados na Fase P211. O programa D047 foi desenhado especificamente para superar os limites dos códigos quase-cíclicos 1-dimensionais investigados em D045, introduzindo a álgebra comutativa bivariada $\mathbb{F}_2[\mathbb{Z}_l \times \mathbb{Z}_m]$ (*bivariate bicycle codes* de Bravyi et al.) e geometrias projetivas e afins 2D ($\text{PGL}(2, 13)$ e $\text{AGL}(2, 4)$).

Seguindo estritamente a Regra 3 do EvoByte (*Evidence over claims*) e o protocolo científico estrito:
1. **Catálogo Congelado:** Os alvos, limites conhecidos na literatura (tabelas de Markus Grassl e repositório LJCR de Dan Gordon), grupos de simetria candidatos e orçamentos foram congelados em [`docs/research/targets/bivariate_targets_v1.json`](targets/bivariate_targets_v1.json).
2. **25 Ensaios Pré-Registrados:** 5 sementes pseudo-aleatórias (`[42, 43, 44, 45, 46]`) avaliadas em cada um dos 5 alvos sob orçamento de 30 segundos por ensaio.
3. **Classificação Canônica e Honesta:** Cada ensaio é classificado de forma determinística em uma das 4 categorias:
   - `DISCOVERY_BEATEN`: recorde mundial estritamente superado ($d > d_{lo}$ ou blocos $< U$).
   - `DISCOVERY_TIED`: empate com o recorde mundial conhecido via nova estrutura algébrica ($d = d_{lo}$ ou blocos $= U$).
   - `NULL_BOUND`: prova estrutural de impossibilidade sob a classe de simetria candidata.
   - `NULL_RESULT`: orçamento esgotado sem superar ou empatar com o recorde vigente.

---

## 2. Pergunta Falsificável e Veredito Global

> **Pergunta da Fase P216:**  
> *A campanha pré-registrada produz resultados auditáveis nos 5 alvos congelados sob orçamentos pré-definidos, gerando vereditos matemáticos rastreáveis sem qualquer falso positivo ou alteração de thresholds post-hoc?*

### Veredito Global: **`DISCOVERY_TIED`**

**Resposta: SIM.** A campanha produziu vereditos matemáticos formais auditáveis em todas as 25 tentativas executadas:
- **5 realizações de `DISCOVERY_TIED`:** Redescoberta construtiva dos parâmetros de fronteira $[[20, 2, 6]]$ (5/5 sementes, 100%) através de códigos quânticos bicíclicos bivariados esparsos sobre $\mathbb{F}_2[\mathbb{Z}_5 \times \mathbb{Z}_2]$, empatando com o recorde mundial de Grassl ($d = 6$) e certificado pelo solver SAT exato com prova de $d \ge 6$ em tempo sub-segundo ($< 0,1$\,s).
- **10 provas de `NULL_BOUND`:** Demonstração analítica rigorosa de que as ações completas de $\text{PGL}(2, 13)$ sobre $C(14, 6, 3)$ e de $\text{AGL}(2, 4)$ sobre $C(16, 7, 3)$ possuem órbitas mínimas estritamente maiores que os recordes mundiais vigentes (25 e 24 blocos, respectivamente).
- **10 ensaios de `NULL_RESULT`:** Para os alvos $[[18, 3, d]]$ e $[[20, 3, d]]$, o pipeline sintetizou códigos quânticos válidos com distância $d = 4$, mantendo-se honestamente abaixo dos recordes mundiais de Grassl ($d = 5$ e $d = 6$).

---

## 3. Desempenho Alvo a Alvo

| Identificador do Alvo | Família | Registro Publicado | Cota Teórica | Melhor Alcançado na Campanha | Veredito do Alvo | Taxa de Sucesso |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`qecc_20_2_bivariate`** | QECC Estabilizador | $d = 6$ (Grassl) | $d \le 7$ | **$d = 6$** ($n=20, k=2$) | **`DISCOVERY_TIED`** | **5 / 5 (100%)** |
| **`covering_C_14_6_3_projective`** | Covering Design | 25 blocos (LJCR) | 24 blocos | Órbita mínima = 91 | **`NULL_BOUND`** | **5 / 5 (100%)** |
| **`covering_C_16_7_3_affine2d`** | Covering Design | 24 blocos (LJCR) | 23 blocos | Órbita mínima = 160 | **`NULL_BOUND`** | **5 / 5 (100%)** |
| **`qecc_18_3_bivariate`** | QECC Estabilizador | $d = 5$ (Grassl) | $d \le 6$ | **$d = 4$** ($n=18, k=3$) | `NULL_RESULT` | 0 / 5 |
| **`qecc_20_3_bivariate`** | QECC Estabilizador | $d = 6$ (Grassl) | $d \le 7$ | **$d = 4$** ($n=20, k=3$) | `NULL_RESULT` | 0 / 5 |

**Distribuição Consolidada dos Ensaios:**
- `DISCOVERY_BEATEN`: 0
- `DISCOVERY_TIED`: 5 (20%)
- `NULL_BOUND`: 10 (40%)
- `NULL_RESULT`: 10 (40%)
- **Tempo Total da Campanha:** $69,632$ segundos.

---

## 4. Análise Aprofundada dos Resultados

### 4.1. Síntese Quântica $[[20, 2, 6]]$ (`DISCOVERY_TIED`)
- **Problema de Fronteira:** O código de Grassl $[[20, 2, 6]]$ possui 2 qubits lógicos protegidos em 20 físicos com distância 6.
- **Solução Descoberta:** Através da álgebra bicíclica bivariada $\mathbb{F}_2[\mathbb{Z}_5 \times \mathbb{Z}_2]$, a busca sintetizou polinômios $A, B$ esparsos cujas matrizes geradoras $H_X = (A \mid B)$ e $H_Z = (B^T \mid A^T)$ satisfazem:
  1. Posto total: $\text{rank}(H_X) = 9$ e $\text{rank}(H_Z) = 9 \implies k = 20 - 18 = 2$.
  2. Comutação simplética analítica exata: $AB = BA \implies H_X H_Z^T = 0 \pmod 2$.
  3. Distância mínima $d = 6$: certificada formalmente via `ExactSATDistanceSolver` (CaDiCaL 1.9.5 com encoding totalizer), provando que não existe qualquer operador lógico de peso $\le 5$ em menos de $0,1$\,s, e identificando uma testemunha lógica exata de peso 6 (`IIIIIIIIIXIIIIXXXIXX`).
  4. Cota estrita do espaço: Uma varredura exaustiva completa de todas as 97.800 combinações de pares de polinômios em $\mathbb{F}_2[\mathbb{Z}_5 \times \mathbb{Z}_2]$ com $k=2$ comprovou que a distância máxima atingível no ansatz bicíclico bivariado é estritamente $d = 6$, provando a otimalidade desta realização.
- **Verificação Independente:** Aprovado em 100% dos ensaios por `verify_target_candidate`, `check_stabilizer`, `code_distance` e `ExactSATDistanceSolver` em média em **$0,290$ segundos** por ensaio.

### 4.2. Invariante de Paridade e Análise dos Alvos com $k=3$ (`NULL_RESULT`)
- **Teorema de Paridade Bivariada:** Em qualquer código bicíclico bivariado CSS padrão com $H_X = (A \mid B)$ e $H_Z = (B^T \mid A^T)$, temos $\text{rank}(H_X) = \text{rank}(H_Z) = r$. Logo, a dimensão lógica é dada por:
  $$k = n - 2r = 2(lm - r)$$
  Portanto, $k$ é estritamente **PAR**. Códigos com $k$ ímpar (como $k=3$ em $[[18, 3]]$ e $[[20, 3]]$) são matematicamente inacessíveis pela forma bicíclica simétrica padrão.
- **Formulação Echelon:** Para investigar $k=3$, empregou-se formulação echelon assimétrica. Para $[[18, 3, d]]$, o pipeline sintetizou códigos com 15 geradores e distância $d=4$ (abaixo do recorde de Grassl $d=5$). Para $[[20, 3, d]]$, o pipeline sintetizou códigos com 17 geradores e distância $d=4$ (abaixo do recorde $d=6$). Ambos foram classificados honestamente como `NULL_RESULT`.

### 4.3. Provas de Delimitação Estrutural em Covering Designs (`NULL_BOUND`)
- **$C(14, 6, 3)$ sob $\text{PGL}(2, 13)$:**
  - O grupo projetivo linear $\text{PGL}(2, 13)$ possui ordem $2.184$ agindo sobre $\mathbb{P}^1(\mathbb{F}_{13})$ (14 pontos).
  - A partição dos $\binom{14}{6} = 3.003$ subconjuntos de tamanho 6 resulta em exatamente 5 órbitas canônicas de tamanhos $\{91, 182, 546, 1092, 1092\}$.
  - A menor órbita possui tamanho $91$.
  - Como o recorde mundial do LJCR é de 25 blocos, **está formalmente provado que nenhum covering design invariante sob $\text{PGL}(2, 13)$ completo pode atingir $\le 25$ blocos**.
- **$C(16, 7, 3)$ sob $\text{AGL}(2, 4)$:**
  - O grupo afim bidimensional $\text{AGL}(2, 4)$ (com automorfismo de Frobenius) possui ordem $5.760$ agindo sobre $\mathbb{F}_4^2$ (16 pontos).
  - A partição dos $\binom{16}{7} = 11.440$ subconjuntos de tamanho 7 resulta em exatamente 9 órbitas de tamanhos $\{160, 240, 480, 960, 1440, 2880\}$.
  - A menor órbita possui tamanho $160$.
  - Como o recorde mundial do LJCR é de 24 blocos, **está formalmente provado que nenhum covering design invariante sob $\text{AGL}(2, 4)$ pode atingir $\le 24$ blocos**.

---

## 5. Proveniência e Auditoria

- **Manifesto de Resultados:** [`experiments/p216-bivariate-campaign-results.json`](../../experiments/p216-bivariate-campaign-results.json)
- **Arquivo de Checkpoint:** [`experiments/p216-bivariate-campaign-checkpoint.json`](../../experiments/p216-bivariate-campaign-checkpoint.json)
- **Módulo da Campanha:** [`src/evobyte/bivariate_campaign.py`](../../src/evobyte/bivariate_campaign.py)
- **Suíte Unitária da Campanha:** [`tests/test_bivariate_campaign.py`](../../tests/test_bivariate_campaign.py) (6/6 testes verdes em 39,97s).
