# Orçamento de execução e campanha

Todos os números de duração abaixo são **tetos de planejamento, não medições**.
Não foram executados benchmarks do hardware. O orçamento de pesquisa é cumulativo;
600 segundos limitam uma execução completa, não toda a investigação.

## Relógio e encerramento de uma execução

t0 é o relógio monotônico do supervisor antes de iniciar o trabalhador. Importação
de bibliotecas, criação do processo, dados, aquecimento/compilação, treino,
inferência, busca, validação, logs e salvamento entram no tempo de parede total.
Instalação inicial e download de dependências ficam fora, com duração separada;
importações e carregamento durante o experimento continuam dentro.

- Até 120 s: teto total para geração/ajuste da política no modo de partida;
  geração para até 115 s, ajuste dentro do saldo. Nenhum braço recebe atraso artificial.
- Em t0+540 s: parar propostas de busca e iniciar fechamento final.
- Até t0+570 s: verificar candidato exportado e persistir resultado.
- Em t0+580 s: pai solicita encerramento dos processos ainda ativos.
- Em t0+590 s: pai força encerramento do grupo de processos, se necessário.
- Em t0+600 s: limite externo e registro de timeout/excesso observado.

Checkpoints a cada 5 s, e ao melhorar a solução, usando escrita atômica. O grafo
vazio certificado deve existir antes de qualquer trabalho oneroso. Para limites
curtos de desenvolvimento, escalar os marcos por B/600: parar busca em 0.90B,
fechar em 0.95B, TERM em 29B/30, KILL em 59B/60. O treino recebe no máximo 0.20B,
com a mesma proporção de geração e ajuste. Testes devem injetar relógio, sem dormir
600 s para verificar regras temporais.

Não se promete que matar o processo libere GPU instantaneamente, nem que uma
chamada bloqueada obedeça ao prazo. Medir parede até o encerramento observado,
processos descendentes e, quando observável, liberação dos recursos. Overrun é
falha registrada e consumo real adicional; não pontuar a execução como concluída.
Não lançar o próximo trabalho enquanto persistirem recursos/processos atribuíveis
ao anterior. Parar campanha se não for possível confirmar encerramento.

## Partida e amortização

**Partida, avaliação principal:** cada execução começa sem dataset e pesos;
geração, ajuste e inicialização entram no seu limite. Dados apenas dos tamanhos
de desenvolvimento. Usar CPU inicialmente, com uma thread de computação por
processo e mesma configuração de threads entre braços. O supervisor leve não
é uma segunda busca. Registrar afinidade, ambiente e tempos reais.

**Amortizado, campanha futura separada:** treinar uma política antes de M execuções,
registrar T_preparo e todos os dados/ajustes anteriores; cada execução paga seu
tempo medido e T_preparo/M no custo atribuído. Reportar tanto tempo online como
custo atribuído. Para alegar comparação de 600 s por execução, exigir
`T_online + T_preparo/M ≤ 600`, não somente `T_online ≤ 600`. Não misturar esses
resultados com H1 de partida. Não há quota amortizada na campanha inicial.

Custos de ajuste, pilotos e tentativas descartadas sempre aparecem no total da
pesquisa, mesmo que não componham o custo de uma política já fixada.

## Estimativa cumulativa da campanha inicial

A agenda é serial. Se um estágio falhar no portão, não consumir os seguintes.

- Testes e verificações locais F0–F4: até 3600 s, ou **1 h**, quota compartilhada
  por tarefas. Inclui leitura/validação de exemplos e testes de falhas.
- Desenvolvimento: 6 métodos × 4 tamanhos × 2 sementes × 60 s = **2880 s,
  48 min**. F3 usa 32 execuções; F4 usa as 16 restantes. Esses ensaios curtos
  verificam integração e não substituem a métrica confirmatória de 600 s.
- Ajuste limitado: **24 execuções × 600 s = 14400 s, 4 h**. Grade finita no P0.
- Piloto: 6 métodos × 2 tamanhos × 3 sementes × 600 s = **21600 s, 6 h**.
- Confirmação: 6 métodos × 3 tamanhos × R × 600 s. Com R=10: **108000 s,
  30 h**, 180 execuções; com R=20: **216000 s, 60 h**, 360 execuções.
- Reprodução limpa: 6 métodos × 3 tamanhos × 2 sementes × 600 s = **21600 s,
  6 h**, 36 execuções novas. Inclui custo de partida outra vez.
- Releitura independente, análise e relatório computacional: **7200 s, 2 h**.
  Verificação normal de cada execução já foi incluída no respectivo limite.
- Reserva de falhas externas: **12 execuções × 600 s = 7200 s, 2 h**;
  permite repetir até dois blocos completos de seis métodos, sem escolher sementes.

Total reservado: **186480 s = 51 h 48 min**, se R=10; **294480 s = 81 h 48 min**,
se R=20. Sem a reserva de falhas, os tetos são 49 h 48 min e 79 h 48 min.
Essas durações não incluem pausas entre sessões nem trabalho humano. O piloto
deve informar se vale alocar a confirmação; não é promessa de tempo até descobrir algo.

## Travas agregadas

Teto global absoluto proposto: **300000 s, 83 h 20 min**, até **516 lançamentos
experimentais** quando R=20 (48 desenvolvimento + 24 ajuste + 36 piloto + 360
confirmação + 36 reprodução + 12 reserva). Para R=10, 336 lançamentos e reserva
de 186480 s. Não iniciar 516 execuções só porque o teto permite: usar a lista
finita e a reserva efetivamente congeladas para o R escolhido.

O controlador reserva o limite inteiro de cada tarefa/execução antes de lançá-la,
somando consumido real + reservas em aberto + próximo limite. Rejeitar início
se ultrapassar quota da etapa, quantidade de tentativas ou teto global. Não devolver
consumo de falhas. Reconciliar custo real, incluindo overrun, ao observar término.
Uma trava/lock local impede dois controladores da mesma campanha; sua recuperação
exige reconciliar processos e logs, sem zerar contadores. Reiniciar a máquina não
reinicia o orçamento. Horas ociosas entre sessões não entram como computação ativa.

Alterar limites exige novo manifesto e decisão com custo já consumido preservado.
Não abrir campanhas novas para contornar o teto da mesma pergunta. O máximo de
300000 s inclui pequena margem para excessos imprevistos; não é verba adicional
para escolher uma nova grade. Operações sem teto são proibidas.

## Medidas e decisões do piloto

Registrar parede, CPU agregada dos processos, RSS máximo, contadores de verificações,
dados, treinamento, características e inferência. CUDA só se disponível e medida;
operações assíncronas exigem sincronização nas fronteiras medidas. Sem instrumento,
GPU, VRAM e energia são indisponíveis, não inferidas a partir do nome da placa.

O piloto decide R pela regra de `01`, B*, parâmetros do motor e lambda já dentro
da grade limitada; avalia variância, efeito de teto, custo do treino e necessidade
de ampliar reservas antes de P1. Dispositivo fica CPU na campanha inicial: GPU
exige estudo exploratório com quota explícita e nova decisão, não troca automática.
Se os tamanhos pequenos não discriminarem métodos ou o teto não comportar inferência,
concluir a limitação ou elaborar um novo protocolo antes de qualquer teste final.
