# Veredito estatístico consolidado com controle FWER e registro de resultados nulos (P169)

- **Fase:** P169 — Veredito estatístico consolidado com controle FWER e registro de resultados nulos
- **Dependência:** P168 (certificados formais em Lean 4), P166 (campanha pré-registrada de recordes), P165 (protocolo de redescoberta cega), P164 (baselines combinatórios)
- **Módulo de avaliação estatística:** [`src/evobyte/statistical_evaluation.py`](../../src/evobyte/statistical_evaluation.py)
- **Suíte de testes:** [`tests/test_statistical_evaluation.py`](../../tests/test_statistical_evaluation.py)
- **Dados brutos de entrada:** [`experiments/p166-campaign/summary.json`](../../experiments/p166-campaign/summary.json)
- **Artefato consolidado de veredito:** [`experiments/p169-statistical-verdict.json`](../../experiments/p169-statistical-verdict.json)
- **Data de emissão:** 2026-10-22

---

## 1. Resumo Executivo e Vereditos Formais

Em cumprimento estrito às regras metodológicas e epistemológicas de `AGENTS.md` (Integridade Científica, Evidência sobre Alegações e Ausência de Falsos Positivos):

1. **Veredito sobre a vantagem evolutiva:**
   > **"A hipótese de superioridade estrita de busca evolutiva em bytecode é REJECTED (NOT SUPPORTED)."**
   >
   > *Fundamentação:* Para os problemas de combinatória extremal discretos (colorações de van der Waerden e partições sum-free de Schur), o motor genético de bytecode de EvoByte não possui representação especializada em relação às meta-heurísticas combinatórias dedicadas (Simulated Annealing e Tabu Search). Em concordância com os relatórios das fases P164, P165 e P166, nenhuma superioridade empírica evolutiva sobre os baselines é sustentada nesses domínios.

2. **Veredito sobre novos recordes matemáticos:**
   > **"A hipótese de descoberta de novos recordes matemáticos na campanha pré-registrada é NULL RESULT."**
   >
   > *Fundamentação:* Dos 3 alvos matemáticos abertos atacados ao longo de 120 ensaios sob orçamento estrito de relógio (10 s por ensaio, 12.016.204 avaliações reais), **0 alvos** superaram as cotas publicadas da literatura (`DISCOVERY_BEATEN = 0`). Um alvo (`vanderwaerden_w3_3`) empatou com o recorde exato publicado ($W(3,3)=27$) com 10 testemunhas formalmente verificadas pelo oráculo independente da P163 (`DISCOVERY_TIED`), enquanto os outros dois alvos (`vanderwaerden_w2_6` e `schur_s5`) resultaram em ausência completa de soluções válidas (`NULL_RESULT`).

---

## 2. Bateria de Testes Pareados com Controle FWER (Holm-Bonferroni)

Para comparar o desempenho das abordagens combinatórias de forma não enviesada, aplicou-se o teste não-paramétrico de postos sinalizados de Wilcoxon (*Wilcoxon signed-rank test*, bilateral) pareado estritamente por alvo, tamanho e semente idêntica ($n = 10$ sementes por subconjunto), com controle de Taxa de Erro por Família (FWER) via procedimento step-down de Holm-Bonferroni sob limiar estrito de significância:

$$\alpha = 0.01$$

### 2.1 Tabela Consolidada de Comparações Pareadas

| Comparação Pareada | $N_{\text{pares}}$ | Wilcoxon $W$ | $p_{\text{raw}}$ | $p_{\text{Holm}}$ | Direção | $\le \alpha$ ($0.01$)? | Veredito Formal |
|---|---:|---:|---:|---:|---|:---:|---|
| `SA_vs_Tabu_schur_s5_beat` | 10 | 9.5 | 0.2578 | 1.0000 | `method_a_superior` | Não | `NOT_SUPPORTED_NULL` |
| `SA_vs_Tabu_schur_s5_tie` | 10 | 8.5 | 0.0527 | 0.3164 | `method_b_superior` | Não | `NOT_SUPPORTED_NULL` |
| `SA_vs_Tabu_vanderwaerden_w2_6_beat` | 10 | 0.0 | 0.00195 | 0.01172 | `method_a_superior` | Não | `NOT_SUPPORTED_NULL` |
| `SA_vs_Tabu_vanderwaerden_w2_6_tie` | 10 | 0.0 | 0.00195 | 0.01172 | `method_a_superior` | Não | `NOT_SUPPORTED_NULL` |
| `SA_vs_Tabu_vanderwaerden_w3_3_beat` | 10 | 0.0 | 0.2500 | 1.0000 | `method_b_superior` | Não | `NOT_SUPPORTED_NULL` |
| `SA_vs_Tabu_vanderwaerden_w3_3_tie` | 10 | 0.0 | 0.00781 | 0.04688 | `method_b_superior` | Não | `NOT_SUPPORTED_NULL` |
| **`SA_vs_Tabu_pooled_campaign`** | **60** | **285.0** | **0.00108** | **0.00108** | `method_a_superior` | **Sim** | **`SUPPORTED_METHOD_A_SUPERIOR`** |

*Legenda:* Method A = Simulated Annealing; Method B = Tabu Search.

### 2.2 Análise Estatística dos Resultados

1. **Subconjuntos por Instância ($n = 10$, Família $m = 6$):**
   - Sob correção de multiplicidade estrita de Holm com $\alpha = 0.01$, **nenhum** dos subconjuntos atinge significância estatística isoladamente.
   - Em `vanderwaerden_w2_6`, embora Simulated Annealing tenha superado Tabu Search em todos os 10 pares com valor bruto $p_{\text{raw}} = 0.001953$, a correção de Holm com tamanho de família 6 eleva o valor para $p_{\text{Holm}} = 0.01172$, situando-se marginalmente acima do corte rigoroso pré-definido de $0.01$. De acordo com a regra anti-p-hacking, o resultado é mantido formalmente como **não significativo / nulo** (`NOT_SUPPORTED_NULL`).
   - Em `vanderwaerden_w3_3` (tie), Tabu Search encontrou testemunhas válidas em 9 de 10 sementes contra 1 de 10 do Simulated Annealing ($p_{\text{raw}} = 0.00781$), mas após controle FWER ($p_{\text{Holm}} = 0.04688$) não satisfaz $\alpha = 0.01$.

2. **Comparação Global Agrupada ($N = 60$ pares):**
   - Ao analisar toda a campanha pré-registrada de forma agregada ($N = 60$), Simulated Annealing exibe $W = 285.0$ com $p = 0.00108 \le 0.01$, suportando superioridade agregada em pontuação média devido ao comportamento em instâncias de grande porte ($W(2,6)$, $N=1131, 1132$), onde Simulated Annealing acumula substancialmente menos violações em tempo fixo.

---

## 3. Síntese dos Alvos e Resultados Nulos da Campanha

A tabela abaixo sintetiza o desfecho final dos alvos da campanha pré-registrada P166, auditados conforme o catálogo P163 e oráculos independentes:

| Alvo de Pesquisa | Problema Combinatório | Cota da Literatura | Veredito P169 | Justificativa |
|---|---|---|---|---|
| `vanderwaerden_w3_3` | Ausência de 3-PA em 3 cores | $W(3,3) \ge 27$ | **DISCOVERY_TIED** | 10 testemunhas válidas em $N=26$ com 0 violações; no alvo de quebra ($N=27$), melhor candidato teve 1 violação (o que condiz com o fato demonstrado na literatura de que $W(3,3)=27$ é cota máxima estrita). |
| `vanderwaerden_w2_6` | Ausência de 6-PA em 2 cores | $W(2,6) \ge 1132$ | **NULL_RESULT** | 0 soluções aceitas; melhor candidato conteve 2.285 violações. |
| `schur_s5` | Partição sum-free em 5 caixas | $S(5) \ge 160$ | **NULL_RESULT** | 0 soluções aceitas; melhor candidato conteve 4 violações. |

---

## 4. Cadeia de Custódia e Rastreabilidade Criptográfica

Para assegurar auditoria completa por terceiros sem perdas de integridade:

| Artefato | Localização Relativa | SHA-256 |
|---|---|---|
| Resumo da campanha P166 | `experiments/p166-campaign/summary.json` | `cc6d756fb822514e4f61e7f6b5b0ea47a39e531329a3a9460c4be831209db306` |
| Artefato de veredito P169 | `experiments/p169-statistical-verdict.json` | `13225b42d75013ff7500186f061bb85f959eb2f0853aee4be70963c75dadc8b4` |
| Módulo estatístico | `src/evobyte/statistical_evaluation.py` | *(rastreado no commit)* |
| Testes unitários | `tests/test_statistical_evaluation.py` | *(rastreado no commit)* |

---

## 5. Conclusão Metodológica

A Fase P169 cumpre integralmente seu propósito epistemológico:
- Nenhum falso positivo foi declarado.
- Nenhum p-hacking foi tolerado: limiares não atingidos após correção de Holm ($p_{\text{Holm}} > 0.01$) foram registrados honestamente como hipóteses não suportadas.
- O registro de resultados nulos consolida o histórico científico do projeto EvoByte, preparando os dados empíricos rigorosos necessários para a finalização do programa na Fase P170.
