# EvoByte Next Research Program

Proposta de 2026-11-05 para revisão de Alexandre. Este é o ponto de entrada
para o Gemini Flash 3.8. O pacote atual é planejamento documental. Os
experimentos P229–P234 permanecem `PROPOSED`.

## Direção e documentos

A pergunta é como obter propriedades matemáticas verificáveis com menos
trabalho. O ciclo combina pergunta falsificável, estrutura algébrica,
refutação barata, certificação independente e auditoria bibliográfica.

1. [Scientific Pivot](SCIENTIFIC_PIVOT.md) registra a análise do código e a motivação.
2. [Quantum Frontier Research Map](QUANTUM_FRONTIER_RESEARCH_MAP.md) contém 15 oportunidades e a seleção inicial.
3. [Low-Compute Discovery Architecture](LOW_COMPUTE_DISCOVERY_ARCHITECTURE.md) delimita a arquitetura e 20 técnicas.
4. [Three Experiments That Could Matter](THREE_EXPERIMENTS_THAT_COULD_MATTER.md) define três pilotos e uma aposta adicional.
5. Este documento contém a ordem, o contrato de execução e o prompt.

## Arquivo da P222 e transição

A P222 foi arquivada por solicitação expressa com estado `ARCHIVED / INCOMPLETE`.
A cobertura preservada termina em ℓ·m = 10. O estado dos gates está no
relatório. A retomada do censo exigirá uma decisão própria. D049 e P223–P228
continuam disponíveis como registro do plano anterior. D051 registra esta
mudança de direção e o ADR-0011 propõe a prioridade de CPU no novo programa.
[Arquivo P222](../p222-census-report.md) ·
[ADR-0011](../../adr/ADR-0011-low-compute-discovery.md)

## Quatro ciclos e seis tarefas

- Ciclo A, auditoria e seleção — [P229](../../phases/P229-low-compute-audit-preregistration.md) fixa entradas, garantias, baselines e pré-registro.
- Ciclo B, três pilotos independentes — [P230](../../phases/P230-exact-distance-kernel-pilot.md) mede distância por núcleo, [P231](../../phases/P231-certified-subgroup-decomposition.md) testa decomposição, [P232](../../phases/P232-exact-cnot-t-identities.md) testa identidades de circuitos. Executar uma fase por vez.
- Ciclo C, certificação e comparação — [P233](../../phases/P233-independent-comparison.md) reproduz os pilotos elegíveis com os mesmos dados e garantias.
- Ciclo D, decisão científica — [P234](../../phases/P234-scientific-decision.md) escolhe continuar, reformular, publicar resultado negativo/metodológico ou abandonar.

Apenas P229 é a próxima tarefa proposta. P230–P232 dependem de pré-registro
e revisão do escopo matemático. Uma linha refutada recebe seu veredito e
uma revisão decide se o próximo piloto independente pode começar. Falha
de teste, discrepância de verificador ou gate vermelho exige parada.
Uma hipótese científica negativa com software correto pode fechar uma
fase com veredito `REFUTED` ou `INCONCLUSIVE` e revisão explícita.

## Pré-requisitos comuns

1. O usuário/revisor aprova este plano e registra a revisão aprovada.
2. O arquivo da P222 e o planejamento devem estar duráveis e a árvore Git
   limpa. A existência local dos arquivos não satisfaz esse requisito.
3. Qualquer gate global pendente precisa de resolução em uma microtarefa
   própria de ambiente antes da execução científica.
4. A base da tarefa deve conter os predecessores aceitos. P229 lê a P222
   como referência parcial, sem exigir a conclusão de seu censo.
5. Conferir os caminhos e funções indicados na fase. Uma API ausente é uma
   diferença a reportar antes de implementar uma solução alternativa.

## Regras para o executor

- Ler `AGENTS.md`, este documento e somente a fase solicitada. As fontes
  adicionais obrigatórias estão enumeradas nessa fase.
- Executar uma tarefa e um commit atômico por ciclo. Usar a branch indicada
  pela fase. Encerrar após push, PR e relatório.
- Editar apenas os caminhos autorizados. Um arquivo adicional exige revisar
  o escopo da fase antes de prosseguir.
- Reusar APIs inspecionadas. Os scripts P230–P233 descritos neste plano são
  entregáveis futuros, ainda ausentes. Criá-los apenas na fase correspondente.
- Registrar a linha de comando real, código de saída, entrada/hash, revisão,
  estado dirty, ambiente, pacotes, orçamento solicitado e consumido.
- Alteração científica, aumento do domínio e novo limite são decisões do
  revisor. Uma falha gera um registro técnico com a saída bruta.
- Um SHA-256 confere identidade do arquivo. A propriedade matemática exige
  uma testemunha ou uma verificação completa e explícita.
- Identificar o executor real. Uma segunda execução pelo mesmo agente é
  reexecução. Reprodução independente exige outra implementação ou executor,
  e o relatório descreve qual independência foi obtida.

## Recursos e métricas

O nível A tem até 2 núcleos, 512 MiB e 30 s por piloto. O nível B tem até
4 núcleos, 2 GiB e 5 min para a comparação. O nível C tem até 4 núcleos,
4 GiB e 30 min e depende de resultado preliminar. GPU é opcional.
Instalação e gates de engenharia têm tempos próprios, registrados
separadamente do experimento. Uma preparação pesada de Lean deve ser
tratada como ambiente, antes da medição.

Cada runner usará um processo no primeiro piloto e fixará
`OMP_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1` e `MKL_NUM_THREADS=1` antes
dos imports numéricos. Registrar tempo de parede, CPU-segundos, RSS de pico,
preparo, geração, certificação, tamanho do certificado, objetos distintos,
classes eliminadas com justificativa, hipóteses refutadas e ganho observado.
Guardar resultados por caso e tentativas interrompidas.

Usar `null` com motivo para dados indisponíveis. Um timeout implica
`INCONCLUSIVE` para a afirmação ainda sem certificado. Comparar cinco
repetições por caso, alternando baseline/candidato. Preservar o primeiro
resultado e os tempos de importação, além das repetições aquecidas.

## Classificação das alegações

Os rótulos são dimensões distintas, podendo coexistir. O estado matemático
é `HYPOTHESIS`, `CANDIDATE`, `COMPUTATIONALLY_VERIFIED`, `FORMALLY_PROVED`,
`REFUTED` ou `INCONCLUSIVE`. A situação bibliográfica é `KNOWN_RESULT`,
`NOVELTY_PENDING` ou `NOVELTY_CONFIRMED`. A reprodução recebe
`INDEPENDENTLY_REPRODUCED` quando há evidência da independência declarada.

`FORMALLY_PROVED` exige enunciado fiel, domínio e axiomas conferidos.
`NOVELTY_CONFIRMED` exige fontes, comparação específica e revisão humana
identificada. Distância exata exige d ≤ valor e d ≥ valor. Uma cota
inferior isolada fica identificada como cota inferior.

## Gates comuns de qualquer commit

Executar os comandos abaixo e guardar a saída integral fora dos dados de
pesquisa. A condição de árvore limpa vale antes de iniciar a tarefa e após
seu commit. O diff esperado da tarefa existe durante a validação.

```bash
set -euo pipefail
git diff --check
git status --short
python3 -m ruff format --check src tests benchmarks
make verify
```

`make verify` inclui `python3 -m pytest tests -q`. Os gates específicos da
fase são adicionais. Se um gate falhar, parar com a saída e os arquivos
locais preservados. Preparação de dependências pode ser corrigida no ciclo
apropriado. As condições de aceite são mantidas.

## Prompt para copiar ao executor

> Execute somente a P229 do EvoByte, após a revisão deste plano e seus
> pré-requisitos. Leia AGENTS.md, docs/research/next/EVOBYTE_NEXT_RESEARCH_PROGRAM.md
> e docs/phases/P229-low-compute-audit-preregistration.md.
> Confirme a árvore limpa e a base aceita. Confira as entradas e os hashes
> indicados. Edite apenas os arquivos autorizados e execute os comandos da
> fase na ordem escrita. Registre o que a implementação realmente prova e
> os limites das referências. Pare em qualquer gate vermelho, API ausente,
> divergência matemática ou decisão científica pendente. Depois de todos
> os gates verdes, faça um commit atômico, push na branch da fase e abra PR.
> Entregue arquivos, comandos/códigos de saída, veredito e pendências.
> Encerre o ciclo após essa entrega.

## As cinco perguntas do projeto

1. Uma fronteira doméstica concreta é certificar distância em pequenos CSS
   com controle explícito do custo, usando as seis referências da P222.
   Uma contribuição metodológica depende da comparação com métodos existentes.
2. Decompor o grupo em cosets de um subgrupo de suporte pode trocar uma
   verificação grande por verificações de blocos menores, depois de provar
   as permutações que preservam peso e os espaços estabilizadores.
3. O caminho mais próximo de um teorema é identificar uma condição suficiente
   de decomposição com preservação de distância. A decomposição básica é
   uma construção conhecida. Uma extensão teria de passar por auditoria.
4. Um script específico de descoberta, um verificador independente e um
   certificado pequeno por problema permitem investigar áreas diferentes.
5. Com 4 núcleos, 2 GiB e 30 min, a escolha inicial é P231 no recorte já
   arquivado. Primeiro construir o subgrupo das diferenças de suporte e
   certificar a decomposição. Usar no máximo os 128 primeiros registros
   ordenados. Conferir seis exemplos por distância independente. Os 30 min
   são teto de investigação, condicionado ao piloto de 30 s. O pseudocódigo
   e os critérios estão no documento de experimentos. Esse teste pode
   confirmar somente um método conhecido ou refutar uma extensão.
