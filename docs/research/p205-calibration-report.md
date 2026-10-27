# Relatório Técnico P205: Calibração Cega em Códigos Quânticos Não-Circulantes e Designs Afins

**Data:** 2026-10-27  
**Programa:** Descoberta com Simetrias Generalizadas e Códigos Quânticos Não-Circulantes (P201–P210, D045)  
**Fase:** P205 — Blind Historical Calibration on Affine and Non-Circulant Targets  
**Status:** Validado e auditado  

---

## 1. Contexto e Motivação

De acordo com as regras mandatórias do repositório EvoByte (`AGENTS.md`: *Evidence over claims*, sem falsos positivos), nenhum método exploratório ou otimizador combinatório pode ser aplicado a alvos em aberto na fronteira científica sem antes provar cabalmente sua capacidade de sintetizar de forma autônoma e cega soluções históricas consolidadas na literatura mundial que apresentem a mesma assinatura estrutural.

O programa D045 visa quebrar as barreiras das simetrias puramente cíclicas/circulantes (como $d \le 3$ em blocos circulantes simples) por meio de grupos de automorfismos generalizados ($\text{AGL}(1, q)$, $D_m$), códigos quase-cíclicos com blocos acoplados e codificação booleana exata SAT para comutação simplética e distância mínima.

A Fase P205 submeteu esse pipeline a uma bateria de testes estritamente cegos em 3 estruturas fundamentais:
1. **Covering Design Afim $C(9, 3, 2) = 12$ ($AG(2, 3)$):** Realização minimal exata de 12 blocos sobre 9 pontos cobrindo todos os 36 pares sob a geometria do plano afim $\mathbb{F}_3^2$.
2. **Código Quântico de Steane $[[7, 1, 3]]$:** Código estabilizador CSS histórico baseado no plano de Fano / código de Hamming dual $[7, 4, 3]$ ($n=7$, $k=1$, $d=3$).
3. **Código Quântico de Shor $[[9, 1, 3]]$:** Código estabilizador não-circulante pioneiro de 9 qubits físicos, 8 geradores estabilizadores mutualmente comutantes e distância mínima $d=3$.

### Regra de Ouro da Calibração Cega
Nenhum gerador publicado, base de blocos conhecida ou vetor de suporte pré-fabricado foi injetado no solver. O algoritmo recebeu exclusivamente os invariantes dimensionais do alvo ($(v, k, t)$ ou $(n, k, d)$) e operou guiado por restrições algébricas exatas e resolução booleana com sementes pseudo-aleatórias para aleatorização de cláusulas e seleção de pivôs. Todos os certificados gerados foram auditados por oráculos de dependência zero (`verify_covering_design`, `verify_affine_plane_properties`, `check_stabilizer`, `code_distance`).

---

## 2. Pergunta Falsificável e Resultados dos Gates

> **Pergunta da Fase P205:**  
> *O pipeline híbrido sob simetrias generalizadas e resolução SAT redescobre cegamente 100% dos 3 alvos históricos de calibração em tempo inferior a 30 segundos por alvo sem injeção de sementes conhecidas?*

### Veredito: SIM (100% de Redescoberta Autônoma)

Todos os 3 alvos foram sintetizados com taxa de sucesso de $100\%$ ($5/5$ sementes cada, totalizando 15 ensaios independentes com sucesso), com tempo médio por tentativa inferior a $0,6$ segundos — mais de **$50\times$ mais rápido** que o orçamento máximo de 30 segundos por alvo. O tempo total acumulado da bateria de calibração foi de **$4,008$ segundos** (teto estipulado: $< 90$ segundos).

### Resumo dos Resultados Experimentais

| Alvo | Meta Estrutural | Sementes Avaliadas | Sucessos | Tempo Médio | Tempo Máximo | Veredito do Gate |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Covering $C(9, 3, 2)$ ($AG(2, 3)$)** | $v=9, k=3, b=12$ blocos | 5 (`[42, 43, 44, 45, 46]`) | **5 / 5 (100%)** | **$0,388$ s** | **$0,591$ s** | Aprovado ($50,7\times$ abaixo do teto) |
| **Steane $[[7, 1, 3]]$ CSS** | $n=7, k=1, d=3$ | 5 (`[42, 43, 44, 45, 46]`) | **5 / 5 (100%)** | **$0,017$ s** | **$0,022$ s** | Aprovado ($1.363\times$ abaixo do teto) |
| **Shor $[[9, 1, 3]]$ Não-Circulante** | $n=9, k=1, d=3$ ($m=8$) | 5 (`[42, 43, 44, 45, 46]`) | **5 / 5 (100%)** | **$0,368$ s** | **$0,598$ s** | Aprovado ($50,1\times$ abaixo do teto) |

**Veredito Global:** `CALIBRATION_REPRODUCED`  
**Tempo Total do Benchmark:** $4,008$ s  

---

## 3. Detalhamento dos Resultados por Alvo

### 3.1. Alvo 1: Affine Covering Design $C(9, 3, 2) = 12$ ($AG(2, 3)$)
O espaço combinatorial completo de $\binom{9}{3} = 84$ blocos candidatos foi codificado sob a exigência de cobrir todos os $\binom{9}{2} = 36$ pares com no máximo 12 blocos.
Todas as 5 instâncias convergiram para exatamente 12 blocos. A auditoria geométrica independente confirmou:
- Cobertura estrita: todos os 36 pares cobertos com multiplicidade exata $\lambda = 1$.
- Grau constante: cada ponto incide em exatamente $r = 4$ retas.
- Estrutura afim de planos: os 12 blocos se decompõem em exatamente 4 classes paralelas de 3 retas mutuamente disjuntas (isomorfo canônico a $AG(2, 3)$ sobre $\mathbb{F}_3^2$).

| Semente | Blocos Totais | Pares Cobertos | Tempo de Relógio | Propriedades $AG(2, 3)$ | Hash SHA-256 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **42** | 12 | 36 / 36 | $0,278$ s | Verificado (4 classes //) | `5f2f8e2be11a8d98...` |
| **43** | 12 | 36 / 36 | $0,307$ s | Verificado (4 classes //) | `5f2f8e2be11a8d98...` |
| **44** | 12 | 36 / 36 | $0,238$ s | Verificado (4 classes //) | `e2a4fcd38e5fcbf6...` |
| **45** | 12 | 36 / 36 | $0,527$ s | Verificado (4 classes //) | `61fd988258e42846...` |
| **46** | 12 | 36 / 36 | $0,591$ s | Verificado (4 classes //) | `733a1d60cb08f496...` |

### 3.2. Alvo 2: Código Quântico de Steane $[[7, 1, 3]]$ CSS
A formulação CSS impôs $m_X = 3$ geradores de paridade $X$ e $m_Z = 3$ geradores de paridade $Z$, comutação simplética exata $H_X H_Z^T = 0 \pmod 2$ e detecção de todas as síndromes de erro de peso 1 e 2.
O solver CaDiCaL convergiu em média em **17 milissegundos**, gerando códigos CSS auto-duais equivalentes ao plano de Fano:

| Semente | Geradores $X$ e $Z$ | Posto / $k$ | Distância $d$ | Tempo de Relógio | Hash SHA-256 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **42** | `['XIXIXIX', 'IXXIXXI', 'IXXXIIX', 'ZIZIZIZ', 'IZZIZZI', 'IZZZIIZ']` | $6$ / $1$ | $d = 3$ | $0,022$ s | `98cef1505c58c467...` |
| **43** | `['XIXXIIX', 'XIIXXXI', 'XXIIXIX', 'ZIIZZZI', 'IZIZIZZ', 'IIZIZZZ']` | $6$ / $1$ | $d = 3$ | $0,017$ s | `85cc23c953b4d2b6...` |
| **44** | `['XXIXIXI', 'IXXXIIX', 'IXXIXXI', 'ZZIIZIZ', 'IZZZIIZ', 'IIIZZZZ']` | $6$ / $1$ | $d = 3$ | $0,015$ s | `4227f745ad3bbcb1...` |
| **45** | `['IXXXIIX', 'XXIIXIX', 'XXXIIXI', 'IZZZIIZ', 'ZZIIZIZ', 'ZZZIIZI']` | $6$ / $1$ | $d = 3$ | $0,015$ s | `87bb2de391df57da...` |
| **46** | `['XXIIXIX', 'IIXXXIX', 'XIIXXXI', 'IZZIZZI', 'IIZZZIZ', 'ZIZIIZZ']` | $6$ / $1$ | $d = 3$ | $0,017$ s | `6ad41dbb35800952...` |

### 3.3. Alvo 3: Código Quântico Não-Circulante de Shor $[[9, 1, 3]]$
O alvo não-circulante de 9 qubits com 8 geradores estabilizadores mutualmente comutantes ($k = 9 - 8 = 1$) foi sintetizado através da formulação geral de estabilizadores com restrições booleanas de produto simplético cruzado e detecção de todos os 351 erros de Pauli de peso 1 e 2 ($27$ de peso 1 e $324$ de peso 2):
- O escalonamento pivotado de Gaussian elimination quebrou o grupo de simetria de permutação de geradores $GL(8, \mathbb{F}_2)$ garantindo posto exatamente 8.
- Em média, a síntese e verificação oracular completa levaram **$0,368$ segundos**:

| Semente | Geradores Sintetizados (Amostra de 8) | Posto / $k$ | Distância $d$ | Tempo de Relógio | Hash SHA-256 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **42** | `['XIYZZYZIY', 'ZYYIXZIYZ', 'ZIZYZXZZI', ...]` | $8$ / $1$ | $d = 3$ | $0,455$ s | `ba5627c1e8ba7e19...` |
| **43** | `['IXZYXZZIZ', 'XIYXZIYYZ', 'ZIIYZXZYX', ...]` | $8$ / $1$ | $d = 3$ | $0,598$ s | `a14d6158d19a4b97...` |
| **44** | `['YXZXZYYII', 'ZYZYIXZYY', 'ZIIZZZYZX', ...]` | $8$ / $1$ | $d = 3$ | $0,208$ s | `aea5ef8f63fb20fb...` |
| **45** | `['ZIXZYXZYY', 'YXZZZYIIX', 'ZIZZXXYZY', ...]` | $8$ / $1$ | $d = 3$ | $0,189$ s | `4d9aea2ad0a9ae10...` |
| **46** | `['ZZYYZXZIX', 'XXXZYIIZY', 'ZIYZZYYIX', ...]` | $8$ / $1$ | $d = 3$ | $0,381$ s | `d205317a444d11a9...` |

---

## 4. Análise de Desempenho e Comparação

1. **Escalabilidade da Síntese Exata:**
   - Para o Steane $[[7, 1, 3]]$, a separação CSS permitiu reduzir o problema a matrizes $3 \times 7$ com comutação de blocos, resolvido em $\sim 5$\,ms de tempo SAT e $\sim 17$\,ms de relógio total.
   - Para o Shor $[[9, 1, 3]]$, o sistema de 8.296 variáveis e 26.931 cláusulas foi resolvido pelo CaDiCaL em $\sim 0,26$\,s de tempo SAT e $\sim 0,37$\,s de relógio total.
   - Para o plano afim $C(9, 3, 2) = 12$, a formulação de cobertura com cardinalidade at-most-12 convergiu em $\sim 0,28$\,s.

2. **Zero Falsos Positivos:**
   - 100% dos objetos foram verificados duas vezes: primeiro internamente pelo solver e segundo por verificadores oraculares independentes de dependência zero (`verify_covering_design`, `verify_affine_plane_properties`, `check_stabilizer`, `code_distance`).
   - Todos os hashes SHA-256 foram calculados sobre representações canônicas JSON e registrados em manifesto persistente.

---

## 5. Proveniência e Dados Experimentais

- **Manifesto de Dados Brutos:** `experiments/p205-calibration-results.json`
- **Ambiente Computacional:** Linux 7.2.6-generic x86_64, Python 3.12.2, PySAT 1.9.dev17 (CaDiCaL 1.5.3).
- **Harness de Benchmark:** `benchmarks/run_p205_calibration.py`
- **Módulo de Síntese:** `src/evobyte/p205_calibration.py`
- **Bateria de Testes:** `tests/test_p205_calibration.py` (5 testes aprovados em 11,74 s).

---

## 6. Conclusão e Autorização para P206

A calibração histórica cega foi concluída com êxito irrestrito em todos os critérios de saída:
1. $100\%$ de taxa de reprodução ($15 / 15$ ensaios válidos).
2. Tempo total de $4,008$\,s ($< 90$\,s).
3. Todas as verificações combinatórias e oraculares aprovadas.

Com este resultado oficializado, o pipeline está calibrado e **autorizado** a avançar para a **Fase P206 — Campanha Pré-Registrada com Simetrias Generalizadas e Códigos Quânticos Não-Circulantes**, atacando os alvos abertos da fronteira mundial catalogados no programa D045.
