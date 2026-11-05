# Protocolo de redescoberta cega de recordes conhecidos (P165)

- **Fase:** P165 — Protocolo de redescoberta cega de recordes conhecidos da literatura
- **Data:** 2026-10-21
- **Dependência:** P164 (baselines combinatórios honestos) concluída
- **Módulo do protocolo:** [`src/evobyte/rediscovery.py`](../../src/evobyte/rediscovery.py)
- **Harness da campanha:** [`benchmarks/run_rediscovery_campaign.py`](../../benchmarks/run_rediscovery_campaign.py)
- **Artefato medido:** [`experiments/p165-rediscovery-results.json`](../../experiments/p165-rediscovery-results.json)

---

## 1. Objetivo

Antes de lançar uma busca cara por recordes inéditos, o método precisa provar sua competência
**reproduzindo soluções ótimas conhecidas em instâncias de calibração**, sem acesso à
resposta no espaço de busca (cega). O protocolo mede a taxa de redescoberta de marcos de
ótimo publicado:

- `vdw_3_3_26` — coloração de $[1..26]$ com 3 cores sem progressão aritmética monocromática
  de 3 termos, ou seja, um certificado de $W(3,3) \ge 27$ (valor publicado exato: 27);
- `vdw_2_4_34` — coloração de $[1..34]$ com 2 cores sem PA monocromática de 4 termos, ou
  seja, um certificado de $W(2,4) \ge 35$ (valor publicado exato: 35).

A comparação é feita contra os **baselines implementados na P164** sob o **mesmo orçamento de
relógio de parede** e as **mesmas sementes**, e o resultado é registrado sem censura.

### Cegueira

A população inicial é **puramente aleatória** (`rng.integers(1, r+1, size=n)`), sem qualquer
candidato conhecido, estrutura pré-definida ou dica do alvo. Nenhuma solução publicada é
hardcoded no espaço de busca. O único conhecimento do alvo usado pelo protocolo é o
*critério de aceitação* (o oráculo independente `verify_vanderwaerden_coloring` da P163),
que é a definição do problema, não a resposta.

## 2. Protocolo de medição

- **Relógio:** `time.perf_counter()`, medido em cada trial (`elapsed_sec`).
- **Orçamentos pareados:** 1,0 s e 10,0 s por trial, idênticos para os três métodos.
- **Sementes:** 5, 42, 101, 202, 303 (5 sementes por configuração).
- **Instâncias:** 2 (as implementadas por `run_single_calibration_trial`).
- **Total:** 60 trials (2 orçamentos × 2 instâncias × 3 métodos × 5 sementes).
- **Critério de sucesso:** o trial termina quando o avaliador retorna `solved = True`, o que
  ocorre **exclusivamente** quando o oráculo independente da P163 aceita a coloração.

## 3. Verificação independente de que as instâncias são o ótimo publicado

Um alvo de calibração só tem valor se for exatamente o marco publicado. O harness faz uma
busca exaustiva por backtracking, independente do avaliador dos métodos, e confronta o
resultado com o valor publicado:

| Instância | Viável em $n$? | Viável em $n+1$? | Ótimo publicado | Confere? | Certificado aceito pelo oráculo P163 | Custo da prova de inviabilidade |
|---|---|---|---|---|---|---:|
| `vdw_3_3_26` | sim (26) | **não** (27) | $W(3,3) = 27$ | sim | sim | 7,27 s |
| `vdw_2_4_34` | sim (34) | **não** (35) | $W(2,4) = 35$ | sim | sim | 0,12 s |

Ou seja: a verificação exaustiva reproduz de forma independente os valores exatos publicados
$W(3,3) = 27$ e $W(2,4) = 35$, e os certificados são aceitos pelo oráculo da P163. Qualquer
redescoberta reportada abaixo é, portanto, a redescoberta do marco publicado — e não um alvo
trivial nem impossível.

## 4. Resultados

| Método | Instância | Orçamento | Taxa de sucesso (seeds) | Evals/s | Tempo médio até o hit | Tempo mediano até o hit |
|---|---|---:|---:|---:|---:|---:|
| Random Search | `vdw_3_3_26` | 1,0 s | 0/5 | 6.267 | — | — |
| Simulated Annealing | `vdw_3_3_26` | 1,0 s | 0/5 | 5.215 | — | — |
| Tabu Search | `vdw_3_3_26` | 1,0 s | 0/5 | 5.247 | — | — |
| Random Search | `vdw_2_4_34` | 1,0 s | 0/5 | 5.028 | — | — |
| **Simulated Annealing** | `vdw_2_4_34` | 1,0 s | **2/5** | 4.386 | **0,183 s** | 0,183 s |
| Tabu Search | `vdw_2_4_34` | 1,0 s | 0/5 | 4.591 | — | — |
| Random Search | `vdw_3_3_26` | 10,0 s | 0/5 | 6.077 | — | — |
| Simulated Annealing | `vdw_3_3_26` | 10,0 s | 0/5 | 5.149 | — | — |
| **Tabu Search** | `vdw_3_3_26` | 10,0 s | **4/5** | 5.334 | **6,259 s** | 5,432 s |
| Random Search | `vdw_2_4_34` | 10,0 s | 0/5 | 5.241 | — | — |
| **Simulated Annealing** | `vdw_2_4_34` | 10,0 s | **2/5** | 4.584 | **0,169 s** | 0,169 s |
| **Tabu Search** | `vdw_2_4_34` | 10,0 s | **3/5** | 4.677 | **3,040 s** | 2,618 s |

Hits individuais registrados no artefato:

| Orçamento | Instância | Método | Semente | Tempo até o hit | Avaliações |
|---:|---|---|---:|---:|---:|
| 1,0 s | `vdw_2_4_34` | SimulatedAnnealing | 202 | 0,199 s | 898 |
| 1,0 s | `vdw_2_4_34` | SimulatedAnnealing | 303 | 0,168 s | 718 |
| 10,0 s | `vdw_3_3_26` | TabuSearch | 5 | 5,553 s | 29.130 |
| 10,0 s | `vdw_3_3_26` | TabuSearch | 42 | 5,312 s | 27.517 |
| 10,0 s | `vdw_3_3_26` | TabuSearch | 202 | 9,410 s | 51.106 |
| 10,0 s | `vdw_3_3_26` | TabuSearch | 303 | 4,760 s | 25.792 |
| 10,0 s | `vdw_2_4_34` | SimulatedAnnealing | 202 | 0,188 s | 898 |
| 10,0 s | `vdw_2_4_34` | SimulatedAnnealing | 303 | 0,150 s | 718 |
| 10,0 s | `vdw_2_4_34` | TabuSearch | 5 | 1,329 s | 6.074 |
| 10,0 s | `vdw_2_4_34` | TabuSearch | 42 | 2,618 s | 12.358 |
| 10,0 s | `vdw_2_4_34` | TabuSearch | 303 | 5,173 s | 25.184 |

### Declaração explícita de melhor performance de redescoberta

**Tabu Search é o método com melhor performance de redescoberta.** É o único que
redescoberta a instância mais difícil (`vdw_3_3_26`, 4/5 sementes em 10 s, tempo médio de
6,26 s) e também lidera em taxa de acerto na mais fácil (`vdw_2_4_34`, 3/5 contra 2/5 do
Simulated Annealing). **Simulated Annealing** acerta mais rápido quando acerta
(0,17 s contra 3,04 s em `vdw_2_4_34`), mas nunca resolve a instância mais difícil e tem
taxa de acerto menor. **Random Search não redescobre nenhuma das instâncias em nenhum
orçamento** — o que confirma que o problema exige busca com vizinhança, não apenas
amostragem.

Nenhum dos métodos medidos é o EvoByte: ver a limitação 7.2.

## 5. Regra de parada da fase

A fase determina: "Nenhum método atingir redescoberta em `vdw_3_3_26` em menos de 10 s
(indica bug no gerador de vizinhança ou avaliador) → PARE". A condição **não** disparou:
**Tabu Search atinge a redescoberta de `vdw_3_3_26` em 4 de 5 sementes, com tempo médio de
6,26 s** (medianas 5,43 s; mínimo 4,76 s), abaixo do limiar de 10 s. Isso confirma que o
gerador de vizinhança e o avaliador estão corretos. Em complemento, o oráculo independente
da P163 (usado dentro do avaliador) e a verificação exaustiva da seção 3 concordam sobre o
que é solução.

## 6. Reprodutibilidade

O número de avaliações depende da velocidade da máquina, porque o laço é interrompido pelo
relógio de parede; a semente, a instância, o orçamento e a estrutura do resultado são
reproduzíveis. Por isso a mesma configuração pode reportar contagens de avaliações
diferentes entre execuções, e o tempo até o hit varia na casa de décimos de segundo.

## 7. Limitações e lacunas reais

### 7.1 Só 2 das 4 instâncias declaradas são implementáveis

O docstring de `src/evobyte/rediscovery.py` declara quatro alvos (`vdw_3_3_26`,
`vdw_2_4_34`, `schur_3_13`, `spectral_counter_sample`), mas a função mandada
`run_single_calibration_trial` só implementa as duas primeiras e levanta `ValueError` para
as outras duas. A frase da fase "mede a taxa de redescoberta em 4 alvos conhecidos" **não é
sustentada pelo código mandated**: só 2 alvos são mensuráveis. O harness aceita apenas as
duas instâncias implementadas e rejeita as demais com mensagem explícita, em vez de
reportar um número vazio.

### 7.2 Não há braço EvoByte nesta fase

A justificativa da fase pede a comparação "contra o EvoByte", mas o módulo mandated
implementa **apenas os três baselines da P164** — não há braço EvoByte, e o EvoByte (motor
de regressão simbólica com bytecode de 64 bytes) não possui, no estado atual do repositório,
uma codificação para colorações de van der Waerden. Portanto a comparação pareada
EvoByte-vs-baselines **não é medida aqui** e **não é afirmada**. O que esta fase calibra é
a capacidade dos baselines sobre instâncias de ótimo conhecido. A codificação de
coloração/partition para o bytecode do EvoByte, e a campanha pareada contra os baselines,
são escopo de fase posterior (P166).

### 7.3 Alcance do resultado

Estes números **não** são evidência de que qualquer método quebrar recordes. Indicam
calibração de competência: com 10 s de relógio de parede, uma busca local com lista tabu
reencontra o marco publicado $W(3,3) = 27$ em 80% das sementes. A extrapolação para
$W(2,6) = 1132$ ou $S(5) = 160$ **não** é medida aqui e não deve ser afirmada: o número de
variáveis cresce de 26 para 1131 posições.

## 8. Reprodução

```bash
python3 -m pytest tests/test_rediscovery.py -q
python3 benchmarks/run_rediscovery_campaign.py \
  --instances vdw_3_3_26,vdw_2_4_34 --seconds 1.0,10.0 --seeds 5,42,101,202,303 \
  --output experiments/p165-rediscovery-results.json
python3 -m pytest tests -q
make verify
```

O harness aceita orçamentos múltiplos (`--seconds 1.0,10.0`) porque a execução com o
orçamento de 1,0 s isolado **não** produz nenhuma redescoberta em `vdw_3_3_26` e, portanto,
dispararia a regra de parada da fase. O orçamento de 10,0 s é o próprio limiar definido
pela regra de parada.
