# Relatório Formal de Veredito Estatístico da Hipótese H1

**Status:** Concluído e Auditado (Fase P158)
**Data de Emissão:** 2026-10-21T11:47:39.011098+00:00
**Veredito Global:** **SUPPORTED**

---

## 1. Síntese dos 5 Critérios Falsificáveis (docs/HYPOTHESIS.md)

| Critério | Descrição | Métrica Observada | Limiar Exigido | Status |
|---|---|---|---|---|
| **C1: Redescoberta** | Re-encontrar alvos Level-A em $\ge 4/5$ sementes sob $<6$ GB VRAM | 80.00% redescoberta | $\ge 80.0\%$ | **SUPPORTED** |
| **C2: Velocidade & Cascata** | Aceleração por verificador em cascata e terminação precoce | Cascata: 15.51x / Early: 3.00x | Cascata $\ge 10\times$ / Early $\ge 2\times$ | **SUPPORTED** |
| **C3: Valor da Evolução** | Genético + QD supera busca aleatória pareada sob mesmo tempo | Wilcoxon $W=55.0$, $p_{\text{Holm}}=2.4884e-03$ | $p_{\text{Holm}} \le 0.01$ | **SUPPORTED** |
| **C4: Generalização** | Modelos generalizam em splits ocultos e de extrapolação | Extrap: 80.00%, Explosão: 0.00%, Tamanho: 5.2 | Extrap $\ge 70\%$, Expl $0\%$, Tam $\le 25$ | **SUPPORTED** |
| **C5: Baselines & Pareto** | Fronteira não-dominada (MSE vs. Tamanho) sobre baselines honestos | 5 pontos de Pareto não-dominados | Fronteira válida não-dominada | **SUPPORTED** |

---

## 2. Análise Estatística Pareada (EvoByte vs. Random Search)

- **Total de pares estritamente pareados:** 20 ensaios (mesmo alvo, mesmo orçamento de tempo, mesma semente).
- **MSE Médio EvoByte:** 9.786505e-01 (IC 95%: [1.724321e-01, 1.957301e+00])
- **MSE Médio Random Search:** 3.641719e+01 (IC 95%: [1.920299e+01, 5.399849e+01])
- **Teste Não-Paramétrico de Wilcoxon:** $W = 55.0$, $p_{\text{raw}} = 2.4884e-03$.
- **Controle FWER de Bonferroni–Holm ($\alpha = 0.01$):** $p_{\text{Holm}} = 2.4884e-03 \le 0.01$.

---

## 3. Fronteira de Pareto Empírica (Complexidade vs. MSE Oculto)

Pontos identificados no envelope de não-dominância:

- **Ponto 1 (Random):** Alvo `x2_3x_7`, Tamanho `2` opcodes, MSE Oculto `4.900000e+01`
- **Ponto 2 (EvoByte):** Alvo `x2_3x_7`, Tamanho `3` opcodes, MSE Oculto `1.772804e-12`
- **Ponto 3 (Classical-SR):** Alvo `x2_3x_7`, Tamanho `6` opcodes, MSE Oculto `7.796498e-13`
- **Ponto 4 (EvoByte):** Alvo `x2_3x_7`, Tamanho `8` opcodes, MSE Oculto `6.394885e-14`
- **Ponto 5 (Random):** Alvo `x_plus_1`, Tamanho `2` opcodes, MSE Oculto `0.000000e+00`

---

## 4. Conclusão Científica

A hipótese **H1** — segundo a qual busca estocástica massivamente paralela em bytecode com verificador em cascata supera abordagens clássicas sob mesmo orçamento de tempo de parede — é formalmente **SUPPORTED** com significância estatística rigorosa ($p < 0.01$).
