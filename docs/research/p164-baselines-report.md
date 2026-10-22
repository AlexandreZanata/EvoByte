# Baselines combinatórios honestos e pareados (P164)

- **Fase:** P164 — Baselines combinatórios honestos (Random Search, Simulated Annealing, Tabu Search)
- **Data:** 2026-10-21
- **Dependência:** P163 (catálogo de alvos e oráculos independentes) concluída
- **Módulo dos baselines:** [`src/evobyte/combinatorial_baselines.py`](../../src/evobyte/combinatorial_baselines.py)
- **Benchmark:** [`benchmarks/combinatorial_benchmark.py`](../../benchmarks/combinatorial_benchmark.py)
- **Artefato medido:** [`experiments/p164-baseline-smoke.json`](../../experiments/p164-baseline-smoke.json)

---

## 1. Por que esta fase existe

A auditoria D038 mediu que, na P155, o baseline alegado (PySR) teve **zero execuções
completas** (`completed_runs = 0`) e os orçamentos foram de frações de segundo (0,4 s /
0,8 s). Uma alegação de superioridade ou eficácia algorítmica só é válida se o método
principal for comparado contra **baselines honestos, totalmente implementados**, sob
**orçamento pareado de tempo de relógio de parede**.

Os três baselines implementados aqui são meta-heurísticas clássicas, sem dependência
externa faltante:

1. **Random Search** — busca estocástica pura, sem memória.
2. **Simulated Annealing (SA)** — aceitação por temperatura com decaimento geométrico.
3. **Tabu Search** — busca local com lista tabu de proibição de movimentos recentes e
   critério de aspiração.

## 2. Protocolo de medição

- **Relógio:** `time.perf_counter()` (monotônico), medido em cada execução. O campo
  `elapsed_sec` de cada resultado e o `max_elapsed_sec` do resumo vêm desse relógio.
- **Orçamento:** cada execução recebe exatamente `--seconds` de relógio de parede; o laço
  verifica o deadline **antes** de cada avaliação, então o overshoot máximo é o custo de
  uma única avaliação.
- **Pareamento:** o mesmo alvo, o mesmo orçamento e a mesma semente são usados para os
  três métodos em cada semente.
- **Proveniência:** cada execução registra `method`, `target_id`, `seed`, `evaluations`,
  `elapsed_sec`, `best_score`, `is_solution` e o melhor candidato — todos serializáveis no
  JSON de saída.
- **Contagem de avaliações:** `evaluations` conta chamadas reais ao avaliador de objetivo.
  Nenhum contador é artificial; nenhuma execução é simulada, mockada ou replicada.

Comando do smoke registrado:

```bash
python3 benchmarks/combinatorial_benchmark.py \
  --target-id vanderwaerden_w3_3 --seconds 0.5 --seeds 42,101 \
  --output experiments/p164-baseline-smoke.json
```

## 3. Alvo e semântica do certificado

O alvo vem do catálogo congelado da P163 (`vanderwaerden_w3_3`, `published_bound = 26.0`,
referência Chvátal 1970, valor publicado exato $W(3,3) = 27$). O espaço de busca é uma
coloração de $[1..27]$ com 3 cores ($N =$ `published_bound` $+$ 1$):

- **objetivo:** minimizar o número de progressões aritméticas monocromáticas de 3 termos
  (`score = -violations`, pois a interface dos baselines maximiza o score);
- **solução:** `violations == 0` — ou seja, uma coloração de $[1..27]$ sem progressão
  aritmética monocromática de 3 termos, que **certificaria $W(3,3) \ge 28$**, quebrando o
  recorde publicado;
- **certificação:** cada melhor candidato é conferido pelo oráculo independente da P163
  (`verify_vanderwaerden_coloring`), e o veredito é gravado no JSON (`oracle_certified`,
  `oracle_message`).

## 4. Resultado medido (2 sementes, 0,5 s por execução)

| Método | Avaliações (2 sementes) | `max_elapsed_sec` | Melhores violações | Soluções | Certificados pelo oráculo |
|---|---:|---:|---:|---:|---:|
| Random Search | 24.795 | 0,500 | 6 | 0/2 | 0/2 |
| Simulated Annealing | 24.694 | 0,500 | 1 | 0/2 | 0/2 |
| Tabu Search | 25.577 | 0,500 | 1 | 0/2 | 0/2 |

Detalhe por execução (de `experiments/p164-baseline-smoke.json`):

| Método | Semente | Avaliações | `elapsed_sec` | Violações | `is_solution` | `oracle_certified` |
|---|---:|---:|---:|---:|---|---|
| RandomSearch | 42 | 12.300 | 0,500 | 6 | falso | falso |
| RandomSearch | 101 | 12.495 | 0,500 | 6 | falso | falso |
| SimulatedAnnealing | 42 | 12.071 | 0,500 | 1 | falso | falso |
| SimulatedAnnealing | 101 | 12.623 | 0,500 | 2 | falso | falso |
| TabuSearch | 42 | 12.781 | 0,500 | 1 | falso | falso |
| TabuSearch | 101 | 12.796 | 0,500 | 1 | falso | falso |

**Nenhum recorde foi quebrado e nenhuma nova solução foi obtida.** Simulated Annealing e
Tabu Search chegaram a **1 violação** (contra 6 da busca aleatória), isto é, ficaram a
uma progressão aritmética de encontrar uma coloração válida de $[1..27]$ — e o oráculo
indepetente confirma que nenhum dos candidatos é solução. Esse resultado é reportado sem
censura: a meta-heurística determinística de vizinhança é muito mais próxima do alvo
extremal do que a busca cega, mas o alvo é NP-difícil e 0,5 s não bastam.

### O oráculo independente encontrou um bug no contador local

Na primeira execução do smoke, o contador local de progressões aritméticas reportou
`violations = 0` para candidatos que o oráculo da P163 rejeitou. A causa era um
`&` bitwise aplicado entre array de inteiros e máscara booleana no NumPy (as cores 2 e 3
ficavam 0 pela operação `cor & 1`), o que zerava as contagens. O contador foi corrigido
para `&=` booleano, validado contra uma referência de força bruta (200 colorações
aleatórias, 0 divergências) e contra o oráculo da P163 (300 colorações aleatórias, 0
divergências). A correção está travada pelo teste
`test_local_counter_agrees_with_independent_oracle`, que compara o contador local com o
oráculo da P163 em 50 colorações aleatórias a cada execução da suíte. O registro `experiments/p164-baseline-smoke.json` contém o resultado
**corrigido**. O episódio é a evidência mais direta do valor do oráculo independente: sem
ele, o smoke teria reportado uma falsa solução.

## 5. Compromisso de auditoria

- Os três baselines executam **código de verdade**: cada avaliação chama o avaliador de
  objetivo real, que reconta as progressões aritméticas (van der Waerden) ou os pares
  sum-free (Schur) do candidato.
- Nenhuma execução é simulada, mockada ou replicada; nenhum contador é artificial.
- Se um baseline superar o método principal, o resultado é reportado sem censura. Neste
  smoke não há execução do método principal: a comparação pareada contra o EvoByte é
  escopo da campanha pré-registrada da P166, e este artefato é apenas o smoke de
  infraestrutura.
- As regras de parada da fase foram respeitadas: **nenhum** método reportou
  `evaluations = 0`, e o maior `elapsed_sec` observado (0,500 s) não excede em 200% o
  orçamento de 0,5 s.
- Os alvos do catálogo com espaço de busca não combinatório (por exemplo
  `spectral_graph_diam_mu2`, cujo candidato é uma matriz de adjacência) são rejeitados com
  mensagem explícita pelo benchmark, em vez de receber um espaço de busca inventado.

## 6. Limitações

- Este artefato é um **smoke de infraestrutura** (2 sementes, 0,5 s, um alvo). Não é
  campanha, não é evidência de superioridade de nenhum método e não substitui a
  campanha pré-registrada da P166.
- O número de avaliações depende da velocidade da máquina (o laço é interrompido pelo
  relógio de parede), portanto não é reprodutível bit a bit entre máquinas diferentes;
  a semente, o alvo, o orçamento e a estrutura do resultado são.
- Só o alvo `vanderwaerden_w3_3` foi exercitado neste smoke; `vanderwaerden_w2_6` e
  `schur_s5` estão implementados no benchmark, mas não foram executados aqui.

## 7. Reprodução

```bash
python3 -m pytest tests/test_combinatorial_baselines.py -q
python3 benchmarks/combinatorial_benchmark.py \
  --target-id vanderwaerden_w3_3 --seconds 0.5 --seeds 42,101 \
  --output experiments/p164-baseline-smoke.json
python3 -m pytest tests -q
make verify
```
