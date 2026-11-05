# Veredito da campanha pré-registrada de recordes (P166)

- **Fase:** P166 — Campanha pré-registrada de busca por novos recordes mundiais sob orçamento fixo
- **Manifesto pré-registrado (congelado antes da execução):** [`experiments/p166-campaign-manifest.json`](../../experiments/p166-campaign-manifest.json)
- **Executor (dirigido pelo manifesto):** [`benchmarks/run_preregistered_campaign.py`](../../benchmarks/run_preregistered_campaign.py)
- **Dados brutos:** [`experiments/p166-campaign/summary.json`](../../experiments/p166-campaign/summary.json)
- **Data de execução:** 2026-10-22, 13:02:39Z → 13:21:34Z

---

## 1. Resumo Executivo

| Métrica | Valor |
|---|---:|
| Alvos atacados | 3 (`vanderwaerden_w3_3`, `vanderwaerden_w2_6`, `schur_s5`) |
| Alvos excluídos antes da campanha | 1 (`spectral_graph_diam_mu2`, ver §6) |
| Ensaios (trials) | 120 (3 alvos × 2 tamanhos × 2 algoritmos × 10 sementes) |
| Avaliações reais | **12.016.204** |
| Tempo de máquina total | **1.134,1 s (18,9 min)** |
| Orçamento pré-registrado | 10,0 s de relógio por semente e algoritmo |
| Maior tempo de um ensaio | 10,019 s (dentro do limite de 3× do manifesto) |
| Vereditos | 1 `DISCOVERY_TIED`, 2 `NULL_RESULT`, **0 `DISCOVERY_BEATEN`** |

A campanha consumiu o orçamento total em todos os 120 ensaios sem que nenhum candidato
**superasse** estritamente a cota publicada da literatura. Um alvo empatou com o recorde
publicado (`vanderwaerden_w3_3`) e dois terminaram como resultado nulo.

## 2. Tabela de Vereditos por Alvo

| Alvo | Recorde Literatura | Melhor Encontrado | Status | Verificador Independente |
|---|---|---|---|---|
| `vanderwaerden_w3_3` | $W(3,3) = 27$ (Chvátal 1970) | Empate: coloração válida de $[1..26]$ com 3 cores, 0 violações (10/20 ensaios); no tamanho de quebra, o melhor foi **1 violação** em $[1..27]$ | **DISCOVERY_TIED** | `verify_vanderwaerden_coloring` → `valid: zero monochromatic 3-term APs in 1..26 with 3 colors` (10 certificados) |
| `vanderwaerden_w2_6` | $W(2,6) = 1132$ (Kouril 2008) | Nenhum certificado; melhor candidato com **2.285 violações** em $[1..1132]$ (e 2.303 em $[1..1131]$) | **NULL_RESULT** | `verify_vanderwaerden_coloring` → nenhum certificado aceito (0/20) |
| `schur_s5` | $S(5) \ge 160$ (Exoo 1994; Heule 2018) | Nenhum certificado; melhor candidato com **4 violações** em $[1..160]$ (e 7 em $[1..161]$) | **NULL_RESULT** | `verify_schur_partition` → nenhum certificado aceito (0/20) |

Detalhamento por algoritmo e tamanho (10 sementes cada):

| Alvo | Tamanho | Algoritmo | Certificados | Tempo médio até o hit | Avaliações médias |
|---|---|---|---:|---:|---:|
| `vanderwaerden_w3_3` | empate (26) | Simulated Annealing | 1/10 | 0,229 s | 216.792 |
| `vanderwaerden_w3_3` | empate (26) | Tabu Search | **9/10** | 3,732 s | 108.826 |
| `vanderwaerden_w3_3` | quebra (27) | Simulated Annealing | 0/10 | — | 224.832 |
| `vanderwaerden_w3_3` | quebra (27) | Tabu Search | 0/10 | — | 230.309 |
| `vanderwaerden_w2_6` | empate (1131) | Simulated Annealing | 0/10 | — | 7.744 |
| `vanderwaerden_w2_6` | empate (1131) | Tabu Search | 0/10 | — | 7.633 |
| `vanderwaerden_w2_6` | quebra (1132) | Simulated Annealing | 0/10 | — | 7.719 |
| `vanderwaerden_w2_6` | quebra (1132) | Tabu Search | 0/10 | — | 7.730 |
| `schur_s5` | empate (160) | Simulated Annealing | 0/10 | — | 100.666 |
| `schur_s5` | empate (160) | Tabu Search | 0/10 | — | 103.004 |
| `schur_s5` | quebra (161) | Simulated Annealing | 0/10 | — | 101.123 |
| `schur_s5` | quebra (161) | Tabu Search | 0/10 | — | 85.238 |

Observação: nos 40 ensaios de `vanderwaerden_w3_3` o número de violações registrado ficou
apenas em {0, 1, 2}. Ou seja, a heurística chega a 1 violação do alvo de quebra — que,
por ser $W(3,3) = 27$ um valor **provado** na literatura, **não existe** coloração válida
de $[1..27]$. A busca exaustiva feita no harness da P165 (verificação de ótimo, 7,27 s)
confirmou que **não existe** coloração válida de $[1..27]$ com 3 cores; o alvo de quebra é,
por construção, um alvo vazio.

## 3. Registro de Descobertas ou Resultados Nulos

### 3.1 `vanderwaerden_w3_3` — DISCOVERY_TIED (empate com o recorde publicado)

O único alvo em que a campanha encontrou um certificado. Witness do veredito:

| Campo | Valor |
|---|---|
| Algoritmo / semente | Simulated Annealing, semente 707 |
| Tamanho | 26 (tamanho de empate, `published_bound = 26.0`) |
| Tempo até o hit | 0,229 s (orçamento de 10,0 s) |
| Avaliações | 5.702 |
| Verificador independente | `verify_vanderwaerden_coloring(candidate, 3, 3)` → `valid: zero monochromatic 3-term APs in 1..26 with 3 colors` |
| SHA-256 do candidato da campanha | `6570ebe0ba7fc4078afff061ad2989cad8f1263343a4a18307195731a9ea8a81` |

Este é um **redescoberta do marco publicado** ($W(3,3) \ge 27$), não um recorde novo. Pelo
critério congelado no manifesto, um certificado no tamanho de empate é `DISCOVERY_TIED`.

Para que a afirmação seja verificável sem reexecutar a campanha, anexa-se um **certificado
independente** da mesma afirmação (obtido por busca exaustiva na P165, e não pela campanha),
aceito pelo mesmo verificador independente da P163:

```json
[1, 1, 2, 2, 1, 1, 2, 3, 2, 3, 3, 1, 3, 1, 1, 2, 1, 2, 2, 3, 1, 3, 3, 2, 3, 2]
```

- SHA-256 do certificado (mesma convenção do executor): `eb5349570f87d2cf4f46aaa8d84b34df2fa5bb0ad56415dff74a5c868b542882`
- Verificador independente: `verify_vanderwaerden_coloring(candidate, 3, 3)` → `True`,
  `valid: zero monochromatic 3-term APs in 1..26 with 3 colors`

Os 10 candidatos certificados pela campanha têm o hash SHA-256 individual registrado em
`experiments/p166-campaign/summary.json` (campo `candidate_sha256`). O executor grava o
**hash** do candidato, não o vetor; por isso o certificado acima é apresentado como
certificado independente da mesma afirmação, e não como o candidato literal da campanha.
Essa lacuna de artefato (hash sem vetor) está registrada como limitação 5.3.

### 3.2 Resultados nulos — `vanderwaerden_w2_6` e `schur_s5`

> **A busca estocástica sob o orçamento pré-registrado não superou os recordes mundiais da
> literatura. O resultado nulo é publicado de acordo com a regra de integridade científica de
> AGENTS.md.**

Os dois alvos terminaram como `NULL_RESULT`: o orçamento de 10,0 s por semente foi esgotado
em 40 ensaios (2 tamanhos × 2 algoritmos × 10 sementes) sem nenhum candidato aceito pelo
verificador independente. O melhor candidato de `vanderwaerden_w2_6` ficou com 2.285
progressões aritméticas monocromáticas de 6 termos ainda presentes; o melhor de `schur_s5`
ficou com 4 violações sum-free.

Nenhum resultado nulo é reportado como vitória, e nenhum `DISCOVERY_BEATEN` foi emitido.

## 4. Cadeia de custódia e integridade

| Item | SHA-256 |
|---|---|
| Manifesto pré-registrado | `3b0c20dd28992766c6331c36c66aaf5f6ab40edd9908737cd8a53098613fedb4` |
| Catálogo de alvos (`open_targets.json`) | `400eeb5a188564402dfbbd4cac9b6abcf51d63498b04c837a15d27d4ffd338d5` |
| Resumo da campanha (`summary.json`) | `13c3afd4bb9c130a1b8ec96e62051dba5a67d0f61eb16bb5719a240cf639b7a1` |
| Certificado de empate independente | `eb5349570f87d2cf4f46aaa8d84b34df2fa5bb0ad56415dff74a5c868b542882` |
| Cada candidato certificado | `candidate_sha256` por ensaio em `summary.json` |

O manifesto foi **commitado antes da execução** (commit `3e360be`, 2026-10-22 09:02:06
-0400); a campanha começou em 2026-10-22 13:02:39Z, ou seja, depois do congelamento. O
histórico do Git prova que a meta, o orçamento, as sementes, os algoritmos e o critério de
vitória estavam fixados antes de qualquer resultado existir. O executor **lê todos esses
parâmetros do manifesto** (nada é fixado em código), e aborta a campanha se:

- o SHA-256 do catálogo não bater com o congelado no manifesto;
- um ensaio exceder 3× o orçamento (nenhum excedeu: máximo 10,019 s contra 10,0 s);
- a busca local e o verificador independente discordarem sobre um candidato (nunca
  discordaram; a checagem roda em todos os 120 ensaios).

O manifesto também congela o `verdict_rule` usado na §2, e nenhum parâmetro foi alterado
durante a campanha.

## 5. Limitações

1. **O resultado nulo é parcialmente esperado a priori.** Os alvos do catálogo P163 são
   definidos como "supere a cota publicada": o espaço de busca do tamanho de quebra é
   $[1..27]$ para $W(3,3)$, $[1..1132]$ para $W(2,6)$ e $[1..161]$ para $S(5)$, e os
   valores publicados ($27$, $1132$, $160$) são **valores exatos provados** na literatura.
   Ou seja: um resultado nulo é o desfecho esperado para qualquer busca finita, e o que a
   campanha mede é **o quanto a heurística se aproxima** do alvo impossível (1 violação em
   $[1..27]$), não a possibilidade de superá-lo. Isso é uma limitação do *desenho* dos
   alvos, e ela está declarada aqui para que nenhum leitor interprete o resultado nulo como
   uma surpresa.
2. **Orçamento de 10 s por semente.** O manifesto previa 60 s como exemplo de orçamento de
   produção; 10 s foi congelado para caber no orçamento de execução da fase. A taxa de
   acerto no empate de `vanderwaerden_w3_3` (9/10 do Tabu) é, portanto, específica deste
   orçamento e não deve ser extrapolada.
3. **O resumo guarda o hash do candidato, não o vetor.** Para auditoria de terceira parte
   sem reexecução, o candidato literal precisaria ser gravado; hoje ele é reconstituível
   apenas por reexecução (a trajetória é dependente do relógio de parede). Lacuna do
   executor, a ser corrigida em fase posterior.
4. **Não há braço EvoByte.** A campanha executa os dois algoritmos do manifesto
   (`SimulatedAnnealing`, `TabuSearch`). O motor de bytecode do EvoByte ainda não tem
   codificação para colorações/partições, e a P165 registrou essa lacuna. Nenhuma afirmação
   de superioridade ou inferioridade do EvoByte é feita aqui.
5. **Contagens de avaliações e tempos dependem da máquina.** Semente, alvo, tamanho,
   orçamento e estrutura do resultado são reprodutíveis; o número de avaliações e o tempo
   até o hit não são.
6. **Número de sementes.** 10 sementes por célula é o mínimo do manifesto; as taxas
   reportadas têm intervalo de confiança amostral largo e devem ser lidas como
   indicativas.

## 6. Alvo excluído antes da campanha

`spectral_graph_diam_mu2` foi **excluído no manifesto**, antes da execução, e não aparece
nos vereditos. A razão está registrada no próprio manifesto: a conjectura registrada
`AH_diam_mu2` pede um grafo conexo com `diameter + mu_2 < 2.0`, condição inalcançável para
todo grafo conexo com $n \ge 2$ — se o diâmetro é 1 o grafo é completo e $\mu_2 = n \ge 2$,
e se o diâmetro é $\ge 2$ então `diameter + mu_2 ≥ 2` já. Excluir o alvo é mais honesto do
que reportar um resultado nulo vacuoso sobre um espaço de busca sem candidatos.

## 7. Reprodução

```bash
python3 benchmarks/run_preregistered_campaign.py \
  --manifest experiments/p166-campaign-manifest.json \
  --output-dir experiments/p166-campaign
python3 -m pytest tests/test_target_catalogue.py tests/test_combinatorial_baselines.py -q
make verify
```

A reexecução com o manifesto congelado reproduz a regra de campanha e os vereditos; as
contagens de avaliações e os tempos até o hit variam com a velocidade da máquina.
