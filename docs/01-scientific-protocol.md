# Protocolo científico inicial

**Versão de especificação:** 0.1. **Estado:** PLANNED, ainda não congelado.
As escolhas abaixo são propostas concretas. F0 deve congelar um protocolo de
desenvolvimento P0; após o piloto, F5 deve congelar P1 para confirmação, antes de
consultar qualquer execução final. Ambos exigem commit, hash e parecer independente.

## Problema formal

Para um inteiro n, seja V = {0, …, n−1}. Um candidato G = (V,E) contém um conjunto
de pares não ordenados de vértices distintos. O espaço tem 2^(n(n−1)/2) grafos
rotulados. São admissíveis apenas grafos sem subgrafo C3 e sem subgrafo C4,
incluindo ciclos com cordas; não basta proibir ciclos induzidos. Não se exige
conexidade nem regularidade. Florestas são admissíveis, com cintura infinita.

O objetivo é maximizar m = |E|, isto é, estudar ex(n; {C3,C4}). A construção é
um objeto com n e lista explícita de arestas, nas regras do contrato `03`.
Laços, duplicatas inclusive invertidas, índices inválidos, tipos malformados,
contagem de arestas divergente ou ciclos proibidos invalidam a entrada.

Um grafo é **maximal** se nenhuma aresta ausente pode ser adicionada mantendo as
restrições. Pode haver outro grafo com mais arestas. Um grafo é **máximo comprovado**
quando é válido e possui tantas arestas quanto um limite superior demonstrado
para aquele n; a prova ou fonte do limite deve acompanhar a alegação.

## Hipótese e separação dos conjuntos

H1: uma política linear aprendida de seleção de arestas, integrada à busca local,
melhora a média da melhor quantidade de arestas certificadas ao fim de 600 s,
em pelo menos uma aresta, contra a referência competente B* escolhida no piloto,
em cada um dos três tamanhos finais, incluindo seu custo de partida.

- Desenvolvimento e geração de exemplos: n em {8,10,12,16}; sementes 0 a 99.
- Ajuste e piloto: n em {18,20}; sementes 100 a 199, separando ajuste 100–149
  e piloto 150–199. Nunca usar o piloto para estimar desempenho confirmatório.
- Confirmação: n em {24,28,32}; identificadores de sementes a partir de 10000,
  definidos no manifesto de P1, sem ensaios experimentais de busca nesses tamanhos
  antes do congelamento. Testes unitários dos verificadores podem usar esses n,
  sem avaliar ou ajustar o desempenho dos métodos de busca.
- Reprodução: novas sementes a partir de 20000, definidas em P1.

Os tamanhos restantes entre 8 e 32 não são ensaios implícitos. O holdout é de
tamanho dentro da mesma família; não demonstra generalização a outra família.
Consultar ótimos publicados é permitido; carregar suas construções no treinamento
ou como início da busca final é proibido. Todos os métodos começam no grafo vazio.
Treinar durante uma execução final usa somente os tamanhos de desenvolvimento.

## Métodos e controles

Seis braços, identificadores fixos:

1. `random`: adicionar uniformemente entre arestas legais até maximalidade e reiniciar.
2. `greedy`: adicionar a aresta legal com maior soma dos graus, desempate uniforme;
   reiniciar ao atingir maximalidade.
3. `local_uniform`: preencher com seleção uniforme e, na maximalidade, remover
   aleatoriamente de 1 até k_max arestas; reiniciar após S ciclos sem melhora.
4. `local_manual`: mesmo motor local, escolhendo a maior soma de graus com
   probabilidade p e uma aresta uniforme com probabilidade 1−p.
5. `local_linear`: mesmo motor, usando o escore aprendido para escolher a adição.
6. `local_untrained`: mesmo motor e mesmas características, com pesos N(0,1)
   sorteados na semente de inicialização, sem treino.

O motor retém a melhor construção independentemente das perturbações. Controles
locais compartilham geração de ações legais, critérios de reinício, orçamento,
registro e verificação. Só muda o seletor de adição. Remoções e reinícios não são
decisões aprendidas na versão inicial. Não limitar avaliações das referências
para compensar custo da política. A busca local é uma adaptação simples inspirada
na literatura de `02`, sem afirmar reprodução integral dos algoritmos publicados.

Grade proposta: k_max em {1,3}, S em {50,200}, p em {0.5,1.0}. Primeiro, testar
as oito combinações de `local_manual` em n=18 e n=20, semente de bloco 100:
16 execuções. Escolher a menor média de déficit relativo, depois menor tempo
mediano até meta e depois a tupla (k_max,S,p) em ordem crescente. Fixar esse motor
para todos os braços locais, com p aplicável somente ao seletor manual. Em seguida,
testar `local_linear` com lambda ridge em {0.1,1.0}, nos dois n e sementes 101 e
102: oito execuções. Escolher lambda pelo mesmo déficit, depois tempo e menor lambda.
São exatamente 24 execuções de ajuste; a agenda e a regra condicional para o motor
ficam em P0. Os braços random e greedy podem usar todo o tempo restante para reinícios.

B* será um dos quatro braços não aprendidos: menor média, sobre n=18 e n=20,
do déficit relativo `(ótimo−m)/ótimo` no piloto; empate pelo menor tempo mediano
até a meta, depois pela ordem lexical do identificador. Seu identificador fica
congelado em P1. Os quatro resultados continuam no relatório, mesmo sem serem B*.

## Política mínima

Para cada ação legal a={u,v}, um vetor x de 12 características simétricas:

1. n/32.
2. m/binom(n,2).
3. Número de adições legais/binom(n,2).
4. Variância populacional dos graus/(n−1)^2.
5. Grau mínimo global/(n−1).
6. Grau máximo global/(n−1).
7. min(d(u),d(v))/(n−1).
8. max(d(u),d(v))/(n−1).
9. Menor soma de graus dos vizinhos entre u e v, dividida por (n−1)^2.
10. Maior dessas somas, com a mesma normalização.
11. Variação do número de adições legais após adicionar a, dividida por binom(n,2).
12. min(distância(u,v),n)/n; para componentes distintos, valor 1.

Escore w·x+b, exatamente 13 parâmetros treináveis. n≥8 nas buscas evita divisões
degeneradas; verificadores também devem aceitar n≥1. Nenhum ID de vértice entra
no vetor. Empates têm distribuição uniforme, não preferência pelo menor rótulo.
Testar invariância exata dos vetores/escores sob permutação e robustez estatística
dos resultados; não exigir trajetória idêntica com uma enumeração diferente.

Em cada execução de partida, gerar estados parciais por construção aleatória nos
quatro tamanhos de desenvolvimento. Para cada estado, amostrar até oito ações
legais; para cada ação, fazer duas completações uniformes independentes até um
grafo maximal. O alvo é a média de `m_terminal−m_estado`. Essa regressão é uma
aproximação de valor de curto horizonte, não um ótimo nem aprendizado por reforço.
Até 4096 pares estado/ação, sem reutilizar dataset ou pesos entre execuções de
partida. Gerar dados por até 115 s; ajustar uma vez por mínimos quadrados ridge,
com intercepto não penalizado, até completar 120 s desde t0 do supervisor.
O restante serve à busca. Não há atualizações online nem recompensa atrasada:
os rollouts fornecem o alvo antes do único ajuste.

Sem dados suficientes (menos de 32 pares com alvos finitos), falha numérica ou
prazo excedido: registrar `training_failed`, usar o grafo vazio já certificado
como resultado de falha e manter a execução na análise. Não trocar silenciosamente
por uma heurística. Custo de características, rollouts, inferência e ajuste será medido;
não se promete que a política caiba ou vença nesse tempo.

## Métrica e critérios de decisão

Métrica principal por execução: maior m de um candidato certificado dentro do
limite total de 600 s e antes do fechamento do resultado. A busca para em 540 s;
o restante é a reserva de verificação e salvamento definida em `05`.
Por tamanho, estimar Delta = média(m_linear−m_B*) entre blocos independentes de
semente. Não somar arestas de tamanhos diferentes como endpoint principal.

Melhoria prática mínima: Delta≥1 aresta em cada tamanho. H1 recebe suporte apenas
se o limite inferior simultâneo de confiança de Delta for ≥1 em todos os três n,
e os portões de validade e reprodução passarem. Se o limite superior simultâneo
for <1 em qualquer n, H1 é refutada na configuração estudada. Nos outros casos,
H1 é inconclusiva. Uma vitória isolada ou um p pequeno não substitui esse critério.
Se todos atingirem o ótimo, reportar efeito de teto; tempo até meta continua
secundário e não pode resgatar H1 por troca retroativa de métrica.

Métricas secundárias: curva da melhor solução, tempo até ótimo
publicado (censurado no limite quando não atingido), avaliações, adições testadas,
inválidos, tempos por etapa, RSS e VRAM quando observáveis. Uma avaliação é uma
chamada completa ao verificador de execução sobre um candidato; consultas de
máscara legal e rollouts têm contadores próprios. Todas as verificações de rollouts
entram no total. Uma campanha por número igual de avaliações deve ter manifesto
separado, contabilizar treinamento e respeitar o limite temporal; não integra a
confirmação inicial nem pode ser executada sem nova alocação agregada. Distinguir
o instante de descoberta de um candidato do instante de sua certificação.
Curvas intermediárias indicam validação de execução; a releitura independente dos
checkpoints pode ocorrer na análise, com custo registrado. Nunca atribuir
certificação retroativa ao tempo de descoberta nem usar essa releitura tardia
para aumentar o endpoint principal de uma execução encerrada.

## Repetições e análise

Unidade de análise: uma execução completa de um método em um bloco de semente,
n e ambiente. Candidatos internos não são réplicas. Cada bloco deriva streams
distintos para dados, treino, busca e desempates; o emparelhamento controla
condições e agenda, sem prometer números aleatórios idênticos entre algoritmos.
Ordem dos métodos aleatorizada em blocos; execução serial, tomada e modo energético
fixos, sem outras cargas experimentais concorrentes. Registrar temperatura e
throttling quando disponíveis, sem excluir sementes pelo resultado.

Piloto: três blocos por n de ajuste, seis métodos. Estimar a maior variância de
diferenças emparelhadas linear−cada referência nos dois tamanhos. Usar como guia
`R = ceil((2.394*s/0.5)^2)`, truncado ao intervalo [10,20], sendo s o maior desvio
padrão observado. A constante aproxima um intervalo normal bilateral com correção
de Bonferroni para três tamanhos, e 0.5 é a meia largura desejada em arestas.
Isso é uma regra de precisão aproximada, não garantia de poder em tamanhos novos.
Se a estimativa exigir R>20, registrar a limitação; não ampliar campanha escondida.
Fixar R uma vez em P1. R não muda depois de olhar a confirmação.

Na análise final, apresentar pares individuais, médias, medianas, Delta e intervalos
bootstrap percentis emparelhados, 10000 reamostragens de blocos e semente fixa em
P1. Intervalos bilaterais de 98.333…% por n dão cobertura simultânea nominal ≥95%
por Bonferroni. São aproximações sob independência dos blocos e representatividade;
amostra pequena, assimetria, saturação e falhas devem limitar a interpretação.
Não reivindicar inferência exata ou generalização populacional ampla.
Comparações com as outras referências e com pesos aleatórios são descritivas;
qualquer teste adicional deve ter família e correção próprias antes de P1.

## Falhas e integridade

O grafo vazio deve ser certificado no início, inclusive antes do treino. Interrupção,
OOM, timeout ou erro do método recebe, na análise principal de intenção de execução,
apenas esse resultado inicial m=0. Checkpoints posteriores podem ser auditados e
mostrados em análise de sensibilidade, sem premiar encerramento malsucedido.
Não certificado é status explícito e nunca uma pontuação presumida válida.

Evento externo demonstrável, como queda de energia, invalida o bloco inteiro;
preservar todos os arquivos e repetir todos os seis braços uma única vez dentro
da reserva. Sem reserva ou segunda falha, declarar incompletude, sem excluir
silenciosamente ou alegar suporte confirmatório. Um bug de verificador interrompe
a campanha; sua correção exige nova versão e reavaliação de toda evidência afetada.

Pesos e datasets do modo amortizado possuem campanha própria, custo anterior,
hash e número de reutilizações. H1 acima é exclusivamente de partida.
Modificações após consultar o final tornam esses dados exploratórios: emitir P2,
novos dados finais e decisão registrada, ou concluir sem nova confirmação.
