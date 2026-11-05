# P221 — Relatório de Honestidade Formal e Recálculo Independente

**Data:** 2026-10-28
**Programa:** Progresso Científico Verificável (P221–P228, D049)
**Status da Fase:** CONCLUÍDA
**Veredito:** SUCESSO DE AUDITORIA FORMAL (Provas sobre matrizes reais no kernel Lean 4 e recálculo independente em Python)
**Autor:** Agente Executor EvoByte
**Autor Correspondente Humano:** Alexandre Zanata

---

## 1. Visão Geral da Fase

A fase P221 cumpre o objetivo fundacional do Programa D049: substituir formalizações superficiais ou aritméticas por provas formais sobre os objetos matemáticos genuínos, aliadas a recálculos computacionais independentes sem qualquer importação do framework `evobyte`.

A auditoria anterior mediu que:
1. `bivariate_bicycle_parity_invariant` provava meramente `2 * (lm - r) ≠ 3` por `omega` aritmético sobre $\mathbb{N}$, sem modelar anéis de grupos ou postos de matrizes.
2. `pgl2_13_orbit_obstruction` e `agl2_4_orbit_obstruction` executavam `decide` sobre listas numéricas de tamanhos escritas à mão.

Em resposta, a fase P221 realizou:
- **Recálculo independente em Python puro (`tests/test_p221_independent_recompute.py`):** sem importar `evobyte`, implementou álgebra de bloco bivariada, posto sobre $\mathbb{F}_2$ e busca exaustiva de distância por combinação combinatorial.
- **Recálculo independente de órbitas (`tests/test_p221_orbit_recompute.py`):** sem importar `evobyte`, gerou do zero as ações de $\operatorname{PGL}(2, 13)$ e $\operatorname{AGL}(2, 4)$ por BFS em classes de subconjuntos.
- **Módulo Lean real (`lean_proofs/Generated/BivariateReal.lean`):** construiu e verificou formalmente no kernel do Lean 4 as matrizes binárias concretas, seus postos $\mathbb{F}_2$, a comutação simplética, a ausência de operadores lógicos de baixo peso (`decide +kernel`) e a existência de testemunhas lógicas exatas de peso $d$.

---

## 2. O que o Lean Agora Prova vs. O que Continua Computacional

| Propriedade | Estado no Lean 4 (Kernel) | Estado Computacional (Python / SAT) | Axiomas Lean |
|---|---|---|---|
| Posto $H_X$ e $H_Z$ de $[[20, 2, 6]]$ ($r=9$) | PROVADO no kernel (`rank_hx20`, `rank_hz20`) | Recomputado independente (`test_p221_independent_recompute.py`) | `[propext]` |
| Comutação simplética $H_X H_Z^T = 0$ de $[[20, 2, 6]]$ | PROVADO no kernel (`commute20`) | Recomputado independente | `[propext]` |
| Distância $d \ge 6$ de $[[20, 2, 6]]$ (21.699 máscaras) | PROVADO no kernel (`no_logical_weight_le5_20`) | Verificado por busca exaustiva e SAT CaDiCaL | `[propext]` |
| Testemunha lógica $d \le 6$ de $[[20, 2, 6]]$ (máscara 991264) | PROVADO no kernel (`logical_weight6_20`) | Testemunha extraída do recálculo independente | `[propext]` |
| Distância exata $d = 6$ de $[[20, 2, 6]]$ | PROVADO no kernel (combinação $d \ge 6 \land d \le 6$) | Recomputado independente | `[propext]` |
| Posto $H_X$ e $H_Z$ de $[[16, 2, 4]]$ ($r=7$) | PROVADO no kernel (`rank_hx16`, `rank_hz16`) | Recomputado independente | `[propext]` |
| Comutação simplética de $[[16, 2, 4]]$ | PROVADO no kernel (`commute16`) | Recomputado independente | `[propext]` |
| Distância $d \ge 4$ de $[[16, 2, 4]]$ (696 máscaras) | PROVADO no kernel (`no_logical_weight_le3_16`) | Verificado por busca exaustiva | `[propext]` |
| Testemunha lógica $d \le 4$ de $[[16, 2, 4]]$ (máscara 61440) | PROVADO no kernel (`logical_weight4_16`) | Testemunha extraída do recálculo independente | `[propext]` |
| Distância exata $d = 4$ de $[[16, 2, 4]]$ | PROVADO no kernel (combinação $d \ge 4 \land d \le 4$) | Recomputado independente | `[propext]` |
| Invariante geral de paridade $k$ para qualquer polinômio | NÃO provado em geral no Lean (apenas lema aritmético em `BivariateDiscovery.lean`) | Provado analiticamente em $\mathbb{F}_2[\mathbb{Z}_\ell \times \mathbb{Z}_m]$ | N/A |
| Partição de órbitas $\operatorname{PGL}(2, 13)$ e $\operatorname{AGL}(2, 4)$ | NÃO provada como teoria de grupos no Lean | Recomputada rigorosamente por BFS em Python | N/A |

---

## 3. Tempos e Métricas Medidas (Saídas Reais dos Comandos)

1. **Recálculo Independente de Códigos (`pytest tests/test_p221_independent_recompute.py`):**
   - $[[20, 2, 6]]$: $r_X = 9$, $r_Z = 9$, $k = 20 - 9 - 9 = 2$, $d = 6$, testemunha lógica `991264` (`0xf2020`, peso 6).
   - $[[16, 2, 4]]$: $r_X = 7$, $r_Z = 7$, $k = 16 - 7 - 7 = 2$, $d = 4$, testemunha lógica `61440` (`0xf000`, peso 4).
   - Tempo de execução total: `0.24 s`.

2. **Recálculo Independente de Órbitas (`pytest tests/test_p221_orbit_recompute.py`):**
   - $\operatorname{PGL}(2, 13)$ em 6-subconjuntos de 14 pontos: 5 órbitas, tamanhos ordenados `[91, 182, 546, 1092, 1092]`, soma `3003`. Mínimo `91 > 25`.
   - $\operatorname{AGL}(2, 4)$ em 7-subconjuntos de 16 pontos: 10 órbitas, tamanhos ordenados `[160, 240, 480, 960, 960, 1440, 1440, 1440, 1440, 2880]`, soma `11440`. Mínimo `160 > 24`.
   - Tempo de execução total: `0.40 s`.

3. **Compilação Formal Lean 4 (`lake build Generated.BivariateReal`):**
   - Compilação limpa em `138 s`.
   - Verificação via script hermético `scripts/verify_lean_p221.sh`: 0 tokens `sorry`.
   - Todos os 10 teoremas emitidos dependem estritamente do axioma canônico `[propext]`. Zero axiomas não-padrão; zero `Lean.ofReduceBool`.

---

## 4. Medição Detalhada: $\operatorname{AGL}(2, 4)$ vs. $\operatorname{A\Gamma L}(2, 4)$

O código legado de P216/P218 incorporava o automorfismo de corpo de Frobenius $z \mapsto z^2$ em $\mathbb{F}_4$, operando sob o grupo semilinear afim $\operatorname{A\Gamma L}(2, 4)$ de ordem 5.760, mas rotulando-o como $\operatorname{AGL}(2, 4)$.

Na fase P221, mediu-se a partição exata de ambos os grupos:
- **$\operatorname{AGL}(2, 4)$ (ordem 2.880, translações e matrizes lineares $\operatorname{GL}(2, 4)$):**
  - Particiona os 11.440 7-subconjuntos em **10 órbitas**: `[160, 240, 480, 960, 960, 1440, 1440, 1440, 1440, 2880]`.
- **$\operatorname{A\Gamma L}(2, 4)$ (ordem 5.760, incluindo Frobenius):**
  - O automorfismo de Frobenius funde pares de órbitas lineares, resultando em **9 órbitas**: `[160, 240, 480, 960, 960, 1440, 1440, 2880, 2880]`.
- Em ambos os casos, a órbita mínima é $160 > 24$, de modo que a cota nula computacional permanece rigorosamente válida sob ambas as formulações.

---

## 5. Declaração de Integridade Científica

**NENHUMA ALEGAÇÃO NOVA DE DESCOBERTA É FEITA NESTA FASE.**
Os resultados obtidos constituem reconstrução e certificação formal exata no kernel do Lean 4 de códigos e propriedades de grupos já estabelecidos na literatura matemática, substituindo lemas vazios por provas matemáticas substantivas e reproduzíveis.
