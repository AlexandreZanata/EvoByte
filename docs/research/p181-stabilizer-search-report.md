# P181 — Relatório da evolução de estabilizadores com Q-Forge

**Data:** 2026-10-25
**Fase:** P181 — Descoberta na Fronteira (D042)
**Status:** Concluído

## 1. Arquitetura e Representação

- **Representação do Genoma**: Matriz binária em $\mathbb{F}_2$ de dimensões $(n-k) \times 2n$, onde as primeiras $n$ colunas codificam a máscara $X$ e as $n$ colunas seguintes codificam a máscara $Z$.
- **Reuso de Operadores do Q-Forge**:
  - `evobyte.quantum.pauli.Pauli` e `commutes_with`: checagem estrita da comutação simplética entre pares de geradores.
  - `evobyte.quantum.evolution_q.mutate_candidate`: mutação estocástica nos operadores de Pauli e substituição direcionada.
  - `evobyte.quantum.evolution_q.crossover_candidates`: recombinação pontual entre pares de candidatos preservando a paridade de dimensões.
  - `evobyte.quantum.evolution_q.tournament_select`: seleção por torneio determinístico.

## 2. Reparo de Comutação por Álgebra Simplética GF(2)

Para garantir que a busca não gere candidatos quase-válidos inválidos:
1. Candidatos mutuamente comutantes com posto $m = n-k$ são aceitos sem modificação (`repair_commutation` preserva conjuntos válidos exatamente).
2. Para candidatos com falhas de comutação par a par, uma projeção sequencial de síndrome simplética $M \Delta = s \pmod 2$ é resolvida via eliminação Gaussiana sobre $\mathbb{F}_2$.
3. Se a projeção restaurar a comutação e a independência linear (posto $n-k$), o candidato reparado é emitido como `(True, fixed)`.
4. Caso a matriz seja irrecuperável ou degenerada (posto menor que $n-k$), o candidato é honestamente rejeitado com `(False, candidate)`.

## 3. Avaliação de Fitness e Oráculo Independente

A avaliação de fitness de cada conjunto estabilizador é delegada estritamente ao verificador independente da P179:
- Se o candidato não comuta ou não possui posto $n-k$: `fitness = 0.0`.
- Se o candidato é válido: `d` é calculado por varredura determinística do centralizador simplético em `evobyte.qecc_verifier.code_distance`.
- O score resultante é exatamente `float(d)`, com flag `is_record_candidate = (d > best_known_value)`.
- Qualquer candidato que alegue superar o recorde é revalidado imediatamente pelo oráculo da P179 e tem seu hash SHA-256 e geradores arquivados.

## 4. Calibração Experimental (Redescoberta Cega)

Medições realizadas sob o protocolo `benchmarks/run_stabilizer_search.py` com orçamento de 300 avaliações por semente (população de 20 candidatos):

| Código Alvo | Parâmetros $[[n,k]]$ | Cota Canônica $d$ | Melhor $d$ Encontrado | Tempo Médio por Semente | Sucesso de Redescoberta |
|---|---|---|---|---|---|
| `five_qubit_5_1_3` | $[[5,1]]$ | 3 | **3** | $0.074\text{ s}$ | Sim (sementes 43 e 44) |
| `steane_7_1_3` | $[[7,1]]$ | 3 | **3** | $0.152\text{ s}$ | Sim (todas as 3 sementes) |
| `shor_9_1_3` | $[[9,1]]$ | 3 | **3** | $0.325\text{ s}$ | Sim (todas as 3 sementes) |

O motor demonstrou capacidade reprodutível de convergir de estados binários pseudoaleatórios até códigos estabilizadores com $d=3$ em frações de segundo.

## 5. Limitações Declaradas

- Espaço de busca exponencial $O(4^{n(n-k)})$ contido por reparo linear e elitismo.
- Avaliação exata de $d$ no loop interno tem custo governado pela varredura por peso no verificador P179 (óptimo para $n \le 12$; aplicável para $n \le 20$ em instâncias com $d \le 4$).
