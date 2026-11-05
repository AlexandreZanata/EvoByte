# Arquitetura mínima e contratos propostos

**Especificação, sem implementação nesta entrega.** Os comandos e assinaturas
abaixo são contratos a implementar, não programas disponíveis.

## Componentes e dependências

Uma aplicação Python local com biblioteca padrão; NumPy entra somente na política
linear e na análise. pytest é dependência de desenvolvimento. Versão exata de
Python e versões resolvidas serão medidas e fixadas em F1, sem inventar versões
de CUDA ou bibliotecas. O verificador de referência deve funcionar sem NumPy.

Estrutura futura:

```text
src/evobyte/
  candidate.py             entrada estrutural e serialização
  validation/reference.py enumerador simples independente
  validation/runtime.py   representação por conjuntos ou bitsets
  search/engine.py         motor local e ações legais
  search/selectors.py      referências não aprendidas
  policy/features.py      características simétricas
  policy/linear.py         geração de dados, ajuste e escores
  budget.py               relógio e contabilidade
  supervisor.py           trabalhador separado e encerramento
  records.py              manifests, eventos e escrita atômica
  campaign.py             agenda e orçamento agregado
  analysis.py             análise a partir de registros imutáveis
  cli.py                  interface pequena
tests/                    casos fixos, exaustivos, falhas e integração
protocols/                P0 e P1 versionados, somente após os portões
runs/<campaign>/<run>/    evidências, nunca entradas executáveis
reports/                  relatórios e pareceres
```

O motor recebe uma configuração validada e um seletor; não recebe permissão para
editar verificadores, protocolo, fontes ou manifesto. O supervisor lê entradas
imutáveis e dá ao trabalhador somente o diretório da execução. Isso é uma fronteira
de responsabilidade para código confiável, não uma promessa de sandbox contra
código hostil. Não há execução de código arbitrário gerado pela IA.

## Candidato e identidade

`CandidatePayload` contém exatamente `schema_version`, `rules_id`, `n`, `edges` e
`claimed_m`. `schema_version=1`, `rules_id=girth-ge-5-v1`, n inteiro estrito ≥1;
booleanos não são inteiros válidos. Cada aresta é um array de dois inteiros em
[0,n). A entrada bruta deve ser examinada antes de normalizar: rejeitar laços,
duplicatas e pares invertidos repetidos; não “corrigir” a entrada com um set.
Após validação, orientar cada par com u<v e ordenar lexicograficamente.
`claimed_m` deve ser exatamente o comprimento da lista, sem duplicatas.

Bytes canônicos: UTF-8 de JSON com chaves ordenadas, separadores `,` e `:`, sem
espaços, NaN ou nova linha final. SHA-256 desses bytes é `content_sha256`.
O envelope inclui `run_id`, payload, hash e referência ao certificado; não entra
no hash do payload. Rejeitar campos desconhecidos em versão 1 para evitar regras
ocultas. Permutar rótulos pode alterar o hash; isomorfismo está fora do MVP.

## Dois verificadores independentes

Contrato de ambos: `validate(raw_payload, expected_n) -> ValidationResult`.
Saída: `valid`, `computed_m` (null se estrutura ilegível), `violations` com códigos
estáveis e testemunhos, `validator_id`, `validator_version`, `code_commit` e
`payload_sha256` (null se não canonizável). Não aceitar `valid=true` informado
pelo candidato. Comparar `n` com `expected_n` externo, além de conferir índices.

**Referência:** ler JSON bruto de forma independente; construir adjacência simples;
examinar todas as triplas para C3 e, para cada quádrupla distinta, as três ordens
de ciclos não equivalentes por rotação/reversão para C4. Não exigir ausência de
cordas. Conferir contagem por duas leituras explícitas da lista. Priorizar legibilidade.

**Execução:** realizar suas próprias verificações estruturais; construir bitsets;
para cada aresta uv, exigir N(u)∩N(v) vazio; para cada par distinto de vértices,
exigir |N(u)∩N(v)|≤1. A primeira condição exclui C3, a segunda C4.
Pode compartilhar apenas tipos e a especificação de serialização; não compartilhar
parser de estrutura, adjacência, máscara legal ou núcleo de violações com a referência.

O certificado final vem de processo separado que relê o arquivo exportado com o
verificador de referência, sem importar motor ou verificador de execução. “Independente”
significa independência de implementação e leitura; não prova correção formal.

Testes obrigatórios: vazio, caminhos, árvores, C3 rejeitado, C4 rejeitado, C5 aceito,
C4 com corda rejeitado, índices negativos/fora da faixa, duplicatas invertidas,
laços, bool, floats, JSON quebrado, n divergente, claimed_m divergente, permutações,
grafos Erdős–Rényi gerados por gerador de testes separado e enumeração de todos
os grafos rotulados para n=1..6. São 33867 grafos no total; reduzir n somente com
decisão registrada se o teto do teste impedir execução, sem declarar o portão F1
completo. Injetar defeitos deliberados nos testes para conferir sua sensibilidade.

## Ações e seletor

`legal_additions(candidate) -> tuple[(u,v), ...]`: somente pares ausentes cuja
adição mantém validade; isso equivale a distância atual ≥4 ou vértices em
componentes diferentes. Essa equivalência deve ser testada contra a referência,
não tomada como certificado final. Remoções sempre preservam ausência de ciclos.

`select(candidate, legal_actions, rng, budget) -> action | None`: `None` somente
quando não há ações ou o prazo exige parar. Uma ação fora da máscara é erro do
método; registrar e interromper. Não remover ações para favorecer um seletor.
`score(features) -> float` não pode modificar candidato ou regras. Pesos não
finitos, dimensões divergentes ou hash incompatível são erros explícitos.

`run_search(config, selector, budget, emit) -> SearchOutcome`: produz a melhor
construção e contadores, sem atribuir a si mesmo certificação independente.
A configuração do motor e as características estão definidas em `01`.

## Configuração e manifesto

`RunConfig`: versões de schema/protocolo e seus hashes, campaign_id/run_id, commit
limpo, rules_id, n, method, modalidade, streams de sementes, parâmetros completos,
dispositivo, limites de execução e caminhos de saída. Hash da configuração é o
SHA-256 de sua serialização canônica completa, sem campo autorreferente.
Configuração desconhecida, método não declarado, n fora do conjunto, manifesto
ausente, árvore de trabalho suja ou `is_example=true` devem impedir execução real.

`CampaignManifest`: lista finita de execuções planejadas, R, B*, grade de ajuste,
ordem aleatorizada, versões e hashes, valores de referência, limite agregado,
máximo de lançamentos e reserva de repetição. O manifesto não muda durante uma
confirmação. Especificar separadamente quotas por fase, testes e análises.

Os exemplos em [examples](examples/README.md) mostram formatos; não autorizam nem
iniciam campanha. `is_example` é metadado do arquivo de exemplo, fora do payload.

## Evidências e estados de resultado

Cada execução preserva `config.json`, `environment.json`, `events.jsonl`,
`checkpoints/`, `candidate.json`, `certificate.json` e `result.json`. Antes de
começar, o pai registra a tentativa e seu orçamento reservado. Eventos append-only
têm sequência, tempo monotônico desde t0, etapa, contadores e hash do candidato.
Escritas usam arquivo temporário e rename no mesmo filesystem; arquivos finais
recebem hashes em um inventário. O relatório só lê evidências, nunca as reescreve.

Ambiente: commit, hash da configuração, protocolo, sementes, dependências fixadas,
SO/kernel, CPU, RAM, GPU/driver/CUDA quando observados, modo energético, threads,
dispositivo e opções de determinismo. Medidas indisponíveis são null com motivo,
nunca zero inventado. Tempos: parede do supervisor, CPU acumulada dos processos,
estágios e GPU quando efetivamente medida. RSS em bytes; VRAM em bytes e com
instrumento/intervalo. Energia apenas com medição ou estimativa identificada.

`RunResult` contém `status` entre `completed`, `training_failed`, `invalid`,
`timeout`, `oom`, `crashed`, `external_failure`; e `certification_status` entre
`CERTIFIED`, `UNCERTIFIED`, `INVALID`. Inclui `primary_m`, `observed_best_m`,
tempos, custos anteriores no modo amortizado, hashes, interrupções e saída do
trabalhador. O pai decide o status. Política de falhas e pontuação: seção de
integridade do protocolo. Um checkpoint não certificado não entra em `primary_m`.

`Certificate`: hash do candidato, run_id, rules_id, expected_n, ambos os resultados
de validação, commit do verificador, timestamp UTC e status final. Hash de payload
ou verdictos divergentes interrompem o portão e preservam a evidência.
O `is_example` não pode aparecer em um certificado real.

## CLI proposta

```text
python -m evobyte verify candidate.json --expected-n 8 --reference
python -m evobyte run --config config.json --manifest campaign.json
python -m evobyte campaign --manifest campaign.json
python -m evobyte analyze --manifest campaign.json --output reports/campaign
```

Saídas: JSON legível por máquina e resumo curto. Código 0 significa conclusão
válida da operação, 2 entrada/protocolo inválido, 3 falha experimental registrada.
Nem `run` nem `campaign` podem alterar o protocolo ou iniciar avaliação não
declarada. O supervisor é obrigatório mesmo para uma única execução.
