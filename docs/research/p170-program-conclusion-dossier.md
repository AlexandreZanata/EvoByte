# Dossiê de conclusão do programa de descoberta validada (P161–P170)

- **Fase:** P170 — Manuscrito auditado, pacote arquivável Zenodo e conclusão do programa
- **Data:** 2026-10-22
- **Decisão:** D041 (ver `docs/DECISIONS.md`)
- **Manuscrito:** [`docs/paper/main.tex`](../../docs/paper/main.tex) e [`docs/paper/main.pdf`](../../docs/paper/main.pdf)
- **Pacote arquivável:** [`dist/zenodo-bundle/final-manifest-sha256.json`](../../dist/zenodo-bundle/final-manifest-sha256.json)
- **Veredito consolidado:** [`experiments/p169-statistical-verdict.json`](../../experiments/p169-statistical-verdict.json)

---

## 1. A jornada: de alegações não verificadas a rigor científico absoluto

O programa P161–P170 começou onde a auditoria D038 encontrou o repositório: com um manuscrito
que afirmava orçamentos de 10 s a 1 h (executados: 0,4 s e 0,8 s), comparação com PySR
(zero execuções completas), residência em VRAM (pico medido: 2,72 MB) e um veredito H1
`SUPPORTED` contradito pelos próprios dados de baseline (Classical-SR 100% contra 80% do
EvoByte); com 49 de 58 identidades de Schinzel classificadas como `novel-extension` sem
solução inteira; e com teoremas Lean "provados" que eram igualdades de constantes
(`hadwigerNelsonLowerDeGrey = 5 := rfl`).

Cada alegação foi submetida a um gate mecânico, e cada gate produziu retratação ou
confirmação registrada:

| Fase | Gate mecânico | Resultado |
|---|---|---|
| P161 | Auditoria de integralidade em ℚ das 58 identidades de Schinzel | **49 retratadas** (só valem em ℚ); 9 inteiras de rotina |
| P161 | Baselines P155 contra o veredito H1 SUPPORTED | **Veredito retratado** → NOT SUPPORTED |
| P161 | Orçamentos e PySR do manuscrito contra os JSONs executados | **Abstract e frases corrigidos**, PDF recompilado |
| P162 | Classificador de fidelidade sobre 4888 teoremas Lean | **51 vacuous-constant, 2012 numeric-literal** (limite inferior) |
| P163 | Catálogo congelado com verificadores independentes | 4 alvos, oráculos em Python puro |
| P164 | Baselines honestos pareados, código real, sem mocks | 6/1/1 violações, 0 certificados |
| P165 | Redescoberta cega de ótimos publicados | Tabu 4/5 em $W(3,3)$; confirmação exaustiva de $W(3,3)=27$, $W(2,4)=35$ |
| P166 | Campanha pré-registrada (manifesto commitado antes) | **1 empate, 2 nulos, 0 recordes** |
| P167 | Verificador autônomo (só biblioteca padrão) | Certificado verificado em < 1 s, cadeia fechada |
| P168 | `lake build` + `decide` + linter + revisão humana | **2 certificados fiéis**, 0 `sorry` |
| P169 | Wilcoxon pareado com Holm a 0.01 sobre a campanha | 6 nulos + 1 agrupado significativo (SA) |

Nenhum gate foi enfraquecido para acomodar implementação: quando o código da especificação
estava matematicamente falso (a coloração `[1, 1, 2, 1, 2, 2, 1, 2]` contém a PA 1, 4, 7), a
fase parou, reportou e corrigiu com objeto verificado — nunca o contrário.

## 2. Contribuições genuínas de engenharia de sistemas do EvoByte

O que sobreviveu à auditoria como engenharia medida, não alegada:

- **Bytecode linear de 64 bytes** executado sem parsing de strings ou AST no caminho quente
  (arquitetura, código versionado, testes de VM).
- **Cascata de verificação S0–S3**: 15,51× de speedup medido contra avaliação monolítica
  (P157, ablação A8, 5 sementes, alvo $y = x^2+3x+7$).
- **Terminação antecipada**: 3,00× adicional (P157, ablação A9).
- **Execução em GPU contra CPU do mesmo bytecode**: 2,60× (P157, ablação A6; é execução em
  dispositivo, não residência de população — a distinção está registrada no manuscrito).
- **Throughputs medidos**: média 3.326 CVPS (matriz P154) e 4.800 CVPS (baselines P155),
  com 500 a 25.017 candidatos verificados por execução.
- **Vitória honesta sobre busca aleatória**: Wilcoxon pareado $W = 55.0$,
  $p_{\text{Holm}} = 2,49 \times 10^{-3} \le 0.01$ (P155, 20 pares; P169 confirma o padrão).
- **Anti-bloat estrutural**: 80% de redescoberta em extrapolação, 0% de explosão
  assintótica, 5,2 opcodes médios — com a ressalva auditada de que os baselines honestos
  atingem 100% (Classical-SR) e 50% (Classic-GP) na mesma divisão.

## 3. Resultados e recordes combinatórios com verificação independente

O programa de descoberta combinatória (P163–P166) produziu exatamente o que os dados
sustentam — nem mais, nem menos:

- **Catálogo congelado** (`docs/research/targets/open_targets.json`, v1.0.0): 4 alvos com
  cotas publicadas e verificadores independentes.
- **Calibração cega** (P165): Tabu Search reencontra $W(3,3) = 27$ (4/5 sementes, 10 s,
  média 6,26 s); Simulated Annealing 2/5 em $W(2,4) = 35$; busca aleatória 0 em tudo.
  Verificação exaustiva independente reproduz os valores publicados exatos.
- **Campanha pré-registrada** (P166): 120 ensaios, 12.016.204 avaliações reais, 1.134,1 s.
  Um alvo empatou o recorde publicado (`vanderwaerden_w3_3`, 10 certificados de $[1..26]$
  verificados pelo oráculo P163, melhor tentativa de quebra com 1 violação); dois alvos
  terminaram `NULL_RESULT` (`vanderwaerden_w2_6`, melhor 2.285 violações; `schur_s5`,
  melhor 4 violações). **Nenhum recorde novo foi batido, e nenhum foi alegado.**
- **Validação externa** (P167): verificador autônomo (só `json`, `sys`, `hashlib`) certifica
  o certificado de exemplo em < 1 s; SHA-256 do objeto `00775b4c…` fecha a cadeia com o
  trial da campanha.
- **Certificados formais** (P168): 2 teoremas Lean 4 fiéis provados no kernel, com revisão
  humana explícita registrada.

## 4. Veredito final do programa

1. **A hipótese de superioridade estrita de busca evolutiva em bytecode é REJECTED (NOT
   SUPPORTED).** O motor de bytecode do EvoByte não possui representação especializada para
   os domínios combinatórios discretos medidos, e a campanha não contém braço EvoByte por
   decisão registrada (a codificação não existe no repositório).
2. **A hipótese de descoberta de novos recordes matemáticos na campanha pré-registrada é
   NULL RESULT.** Dos 3 alvos, 0 superaram cotas publicadas; 1 empatou; 2 terminaram sem
   solução válida. Declarado com integridade, conforme a regra de `AGENTS.md`.
3. **A comparação honesta entre heurísticas favorece Simulated Annealing sobre Tabu Search
   no agregado** (P169, $N = 60$ pareados, $W = 285.0$, $p_{\text{Holm}} = 0.00108$), sem
   significância em nenhum subconjunto isolado após Holm — um resultado real, reportado
   sem censura, que não altera os dois vereditos acima.

## 5. Onde está cada evidência (cadeia de custódia)

O arquivo `dist/zenodo-bundle/final-manifest-sha256.json` registra o SHA-256 de cada
artefato abaixo, com flags de versionamento em git e pertencimento ao pacote Zenodo:

- P154 matriz, P155 baselines, P156 generalização, P157 ablações, P158 veredito
  (artefatos de execução locais, com hash medido);
- P162 fidelidade, P163 catálogo, P164 smoke, P165 redescoberta, P166 manifesto +
  resumo, P169 veredito consolidado, registro de revisões humanas, certificados Lean
  fiéis, manuscrito `.tex` + `.pdf`, certificado de exemplo (todos versionados).

O pacote `dist/zenodo-bundle/evobyte-zenodo-bundle.tar.gz` contém os 544 arquivos de
evidência (5,46 MB) com `manifest-sha256.json` e `checksums.sha256` internos, e passa na
verificação `verify_zenodo_bundle_integrity` sem achados.

## 6. Limitações assumidas (não serão reabertas sem nova fase)

1. Orçamentos sub-segundo nas fases P154–P156: os números são os medidos, e o manuscrito
   declara explicitamente que 10 s–1 h não foram executados.
2. A P166 não tem braço EvoByte; nada neste programa afirma superioridade do EvoByte em
   combinatória discreta.
3. O catálogo P163 cobre Ramsey/Schur/espectral-amostra; grafos grandes e inteiros de alta
   ordem estão fora de escopo.
4. O `decide` dos certificados Lean não escala para instâncias grandes; vale para calibração.
5. O registro de revisões humanas tem 2 entradas `faithful`; qualquer nova alegação de
   resultado Lean exige entrada assinada — regra vigente desde P162.
