# P172 — Relatório de Baselines Competitivos e Harness de Solver

**Data:** 2026-10-22
**Status:** Concluído com evidência empírica
**Fase:** P172 — Descoberta na Fronteira (D042)
**Artefato de medição:** [`experiments/p172-calibration.json`](../../experiments/p172-calibration.json)

---

## 1. Resumo Executivo

A fase P172 estabelece os baselines competitivos honestos e o harness de solver exato para as campanhas de busca combinatória na fronteira (Trilhas A e B do programa D042). Todas as implementações utilizam unicamente a biblioteca padrão do Python e bibliotecas pré-instaladas (`numpy`, `scipy`), sem adicionar dependências externas ao projeto.

Os baselines foram testados contra os portões de calibração calibrados na P171:
1. **Portões do Verificador:** Verificação exata e instantânea de Fano plane $C(7,3,2)$, planos afins $AG(2,3)$, sistema de Steiner $S(3,4,8)$, e a partição fraca de Schur $WS(2)$ sobre $[1..8]$. Todas as remoções de blocos unitários foram devidamente rejeitadas.
2. **Reprodução por Busca — WS(2):** Simulated Annealing encontrou a partição fraca ótima $[1, 1, 2, 1, 2, 2, 2, 1]$ de $[1..8]$ em **0,0010 s** (247 avaliações), contra o orçamento estrito de 2,0 s.
3. **Reprodução por Busca — C(7,3,2):** Simulated Annealing com inicialização gulosa e movimentos de troca encontrou o plano de Fano cobrindo todos os 21 pares com 7 blocos em **0,0259 s** (2105 avaliações), contra o orçamento estrito de 2,0 s.
4. **Tempo Total de Calibração:** **0,0317 s** no total do script de calibração, uma margem de ~94× sobre o limite duro de 3,0 s.

---

## 2. Metodologia e Arquitetura

### 2.1 Interface dos Baselines

O módulo [`src/evobyte/frontier_baselines.py`](../../src/evobyte/frontier_baselines.py) fornece:

- **`BaselineResult`**:
  Dataclass imutável contendo 8 campos essenciais + rastreamento de simetria:
  - `method`: Nome do método (`RandomSearch`, `SimulatedAnnealing`, `HillClimbing`).
  - `target_id`: Identificador do alvo na fronteira.
  - `best_candidate`: Melhor estrutura encontrada.
  - `best_score`: Pontuação máxima alcançada (maior = melhor).
  - `is_solution`: Booleano estrito indicando validade total.
  - `evaluations`: Contador real de chamadas ao avaliador.
  - `elapsed_sec`: Tempo medido via `time.perf_counter()`.
  - `seed`: Semente do gerador pseudo-aleatório.
  - `skipped_symmetry`: Contagem de estados pulados devido à equivalência sob o grupo de simetrias.

- **`canonical_form(candidate, symmetries)`**:
  Calcula o menor elemento lexicográfico na órbita do candidato gerada pelo grupo de permutações de índices fornecido. Permite filtragem canônica $O(1)$ de estados isomórficos.

- **`run_random_search`**:
  Busca aleatória pura com amostragem independente até atingir a solução ou o tempo limite.

- **`run_simulated_annealing`**:
  Recozimento simulado com resfriamento geométrico $T_{k+1} = T_k \cdot \alpha$, critério de aceitação de Metropolis $P = \exp(\Delta / T)$ para movimentos deteriorantes, e aceitação estrita garantida para qualquer $\Delta \ge 0$.

- **`run_hill_climbing`**:
  *Steepest ascent* determinístico com desempate pelo menor índice de vizinho e reinícios aleatórios determinísticos dada a semente.

- **`solve_tiny_sat_dpll`**:
  Algoritmo DPLL puro em Python stdlib com propagação unitária, eliminação de literal puro e ordem fixa de decisão de variáveis. Retorna `(True, modelo, stats)` para fórmulas SAT, `(False, None, stats)` para UNSAT, ou `(None, None, stats)` quando o orçamento de decisões é esgotado.

- **`external_sat_solver_status`**:
  Sonda não-bloqueante no `$PATH` à procura dos binários de solvers industriais `kissat` ou `cadical`.

---

## 3. Decisão de Dependência: Por Que Não Há PySAT?

O ambiente de execução padrão do repositório não dispõe do pacote `pysat` (ou `z3-solver`). Em conformidade estrita com a regra de integridade de dependências (`AGENTS.md`), nenhuma biblioteca C/C++ externa foi introduzida no `pyproject.toml`.

Em vez disso:
- Para testes unitários e calibrações rápidas em instâncias reduzidas, utilizamos `solve_tiny_sat_dpll` em Python puro com garantias formais de corretude (sem palpites heurísticos quando o orçamento se esgota).
- Para campanhas combinatórias industriais futuras em grande escala, a função `external_sat_solver_status()` provê o gancho de integração para invocar binários de alto desempenho (`kissat` / `cadical`) caso estejam presentes no host.

---

## 4. Resultados Medidos de Calibração

Medições obtidas pela execução de [`benchmarks/frontier_baseline_calibration.py`](../../benchmarks/frontier_baseline_calibration.py) gravadas em [`experiments/p172-calibration.json`](../../experiments/p172-calibration.json):

| Etapa | Alvo | Resultado | Avaliações | Tempo Medido | Orçamento Limite |
|---|---|---|---|---|---|
| Portões do Verificador | Fano, AG(2,3), S(3,4,8), WS(2) | `all_pass` | — | 0,0009 s | < 0,1 s |
| Busca SA | $WS(2)$ sobre $[1..8]$ | `hit: true` | 247 | 0,0010 s | 2,0 s |
| Busca Gulosa + SA | $C(7,3,2)=7$ | `hit: true` | 2.105 | 0,0259 s | 2,0 s |
| **Total Benchmark** | — | **Aprovado** | — | **0,0317 s** | **3,0 s** |

---

## 5. Limitações e Escopo

1. **Escalabilidade do DPLL:** O solver `solve_tiny_sat_dpll` é intencionalmente restrito a instâncias pedagógicas e testes unitários com poucas variáveis e decisões ($\le 10^3$). Ele não substitui solucionadores CDCL (como Kissat) com aprendizagem de cláusulas de conflito e 2-watched-literals para fórmulas de fronteira abertas.
2. **Tratamento de Entradas Malformadas:** Todas as rotinas de avaliação de candidatos capturam exceções e tratam formatos incompatíveis (como tuplas vazias, tipos heterogêneos ou blocos de cardinalidade inconsistente) retornando veredito negativo sem interromper o laço de busca.
