# Fases, portões e estados científicos

As fases organizam implementação. Os estados organizam a evidência de uma pergunta
científica. Uma fase concluída não substitui o estado nem autoriza a próxima
campanha. Os tetos abaixo são computação local; esforço humano não está estimado.
Os limites agregados e suas somas têm autoridade em [orçamento](05-experiment-budget.md).

## F0 Especificação científica

Dependência: planejamento entregue. Tarefas F00-T01 e F00-T02. Entregar revisão
bibliográfica, protocolo P0, grade finita de ajuste e parecer independente.
Aceitação: o revisor consegue explicar hipótese, falha, endpoint e custo; todos
os valores usados possuem fonte. Teste: checklist documental e hashes conferidos.
Custo: sem execução experimental; até 10 minutos de verificações documentais,
contados na quota de testes. Riscos: valores de outra família, congelamento falso.
Parar se faltar fonte ou houver ambiguidade científica; voltar ao estado afetado.

## F1 Candidatos e verificadores

Dependência: F0. Tarefas F01-T01 a F01-T06. Entregar esqueleto mínimo, representação,
dois verificadores, testes exaustivos e exportação de certificados. Aceitação:
concordância em todos os grafos rotulados até n=6, rejeição dos casos malformados,
C3/C4 detectados e C5 aceito, sem núcleo compartilhado. Testes independentes da
busca. Custo: quota conjunta de testes F0–F4 até 1 h. Risco: bug correlacionado
ou normalização que esconda duplicatas. Parar no primeiro desacordo e registrar
contraexemplo. Revisão independente de código, casos e saídas obrigatória.

## F2 Execução reproduzível

Dependência: F1. Tarefas F02-T01 a F02-T05. Entregar logs, ambiente, orçamento,
supervisor e CLI de uma execução. Aceitação: processo lento, travado e que falha
produz status e evidência; custos são reconciliados com o pai; checkpoint permanece
legível. Repetir configuração em ambiente observado e explicar diferenças sem
prometer determinismo entre hardware. Custo: dentro da quota de testes de 1 h.
Riscos: trabalho escapar do supervisor, tempo de CUDA assíncrono, arquivos parciais.
Parar se não for possível contabilizar ou encerrar e observar o processo.

## F3 Referências não aprendidas

Dependência: F2. Tarefas F03-T01 a F03-T05. Entregar motor, random, greedy,
local_uniform, local_manual e relatório de desenvolvimento. Aceitação: todos
produzem grafos certificados, logs completos e comportamento de reinício real;
revisor inspeciona execuções, não apenas o relatório. Custo: parcela de 32 das
48 execuções curtas de desenvolvimento, até 1920 s, além da quota de testes.
Riscos: referência fraca ou demasiado lenta, efeito de teto. Parar antes da IA
se o motor ou as referências não passarem. Melhorias aqui mudam P0 se necessário.

## F4 Política aprendida mínima

Dependência: F3 com parecer aceito. Tarefas F04-T01 a F04-T06. Entregar 12
características, regressão linear, controle sem treino, ajuste limitado e piloto.
Aceitação: 13 parâmetros, dados/treino contabilizados, invariância conferida e
comparação com referências competente. Ganhar não é requisito para passar:
é necessário um experimento válido que possa perder.
Custo: 16 execuções curtas restantes, 24 de ajuste e 36 de piloto, até 36960 s
(10 h 16 min), além da quota de testes. Riscos: overfitting, treino consumir todo
o tempo, custo de calcular características superar seu benefício. Parar se houver
vazamento, falha persistente de treino ou ausência de evidência confiável.

## F5 Avaliação congelada

Dependência: F4 e decisão documentada de viabilidade. Tarefas F05-T01 a F05-T03.
Entregar manifesto P1, B*, R e campanha final completa com certificados.
Aceitação: revisão independente antes da primeira execução final, sem ajustes
retroativos; todos os braços e falhas preservados. Custo: 3×6×R×600 s,
30–60 h para R=10–20, com reserva de até 2 h para blocos externos repetidos.
Riscos: potência baixa, saturação, mudança de ambiente, erro descoberto tarde.
Parar com inconclusão quando validade ou orçamento impedir conclusão; não aumentar
amostra a partir da significância observada.

## F6 Reprodução e conclusão

Dependência: F5, inclusive resultados negativos ou incompletos preservados.
Tarefas F06-T01 a F06-T03. Entregar análise, revisão dos certificados, reprodução
limpa e relatório. Aceitação: outra sessão reconstrói análise dos arquivos e executa
dois novos blocos por tamanho; relatório distingue validade, desempenho e ausência
de avaliação de novidade. Reprodução é descritiva, não um segundo teste de H1.
Custo: 6 h de novas execuções e até 2 h de verificação/análise. Riscos: dependências
não fixadas ou evidências irrecuperáveis. Divergência material impede declarar
suporte; investigar, registrar e limitar a conclusão. Parecer final independente.

## Máquina de estados

Transições exigem eventos com responsável, horário, protocolo e hashes. Somente
as transições listadas são permitidas. Recuar preserva versões; não apaga evidências.
De qualquer estado pode-se ir a ARCHIVED por cancelamento, inviabilidade ou falha
irrecuperável, registrando motivo e evidências disponíveis. Arquivar não significa
experimento bem-sucedido.

### QUESTION

- Entrada: pergunta e limite de recursos do usuário.
- Saída: problema e escopo em `00` e `01`.
- Aceitação: objetivo verificável único e quatro alegações separadas.
- Falha: pergunta não operacionalizável ou domínio múltiplo.
- Próximo: RELATED_WORK.
- Evidências: versão da pergunta, restrições e decisão de escopo.

### RELATED_WORK

- Entrada: problema formal e parâmetros candidatos.
- Saída: fontes primárias, valores conhecidos e pendências em `02`.
- Aceitação: parâmetros e metas checados; redescoberta identificada.
- Falha: fonte insuficiente ou problema diferente do bibliografado.
- Próximos: QUESTION ou HYPOTHESIS.
- Evidências: URLs, datas, versões, seções e extratos com hashes.

### HYPOTHESIS

- Entrada: escopo e literatura.
- Saída: H1, endpoint, braços, condições de refutação e plano de análise.
- Aceitação: uma pessoa independente reproduz a regra de decisão sem improviso.
- Falha: sucesso subjetivo, custo oculto ou hipótese impossível de refutar.
- Próximos: RELATED_WORK ou PROTOCOL_FROZEN.
- Evidências: proposta versionada e parecer sobre a hipótese.

### PROTOCOL_FROZEN

- Entrada: hipótese revisada e protocolo/manifesto completos para a etapa.
- Saída: P0 de desenvolvimento ou P1 confirmatório, commit e hash imutáveis.
- Aceitação: orçamento, split, análise, parada, falhas e revisões preenchidos.
- Falha: campo pendente exigido pela etapa ou dados finais já consultados.
- Próximos: VALIDATOR_READY para P0; CONFIRMATORY_RUN para P1, exigindo também
  VALIDATOR_READY e BASELINES_READY ainda válidos; HYPOTHESIS para revisão.
- Evidências: snapshot completo, configuração, autorização de fase e parecer.

### VALIDATOR_READY

- Entrada: P0 e testes de verificadores executados.
- Saída: conjunto certificado de testes e revisão F1.
- Aceitação: acordo exaustivo n≤6 e independência de implementação inspecionada.
- Falha: discordância ou ausência de testemunhos de rejeição.
- Próximos: PROTOCOL_FROZEN para correção versionada ou BASELINES_READY.
- Evidências: commit, comandos, saídas, contagens e contraexemplos.

### BASELINES_READY

- Entrada: verificadores aceitos e supervisor validado.
- Saída: quatro referências com resultados de desenvolvimento.
- Aceitação: custo real, validade e competência revisados em F3.
- Falha: referência inoperante, logs incompletos ou comparação artificial.
- Próximos: VALIDATOR_READY se houver bug de validade; PILOT.
- Evidências: configurações, sementes, certificados, tempos e parecer F3.

### PILOT

- Entrada: referências prontas, política testada e quota de piloto disponível.
- Saída: variância, R proposto, B*, diagnóstico de teto e custo medido.
- Aceitação: nenhum n final executado; escolhas seguem a regra predeclarada.
- Falha: vazamento, dados insuficientes, custo inviável ou treino inoperante.
- Próximos: BASELINES_READY para reparo; HYPOTHESIS para mudança científica;
  PROTOCOL_FROZEN para criar P1.
- Evidências: todas as execuções de ajuste/piloto, decisões e relatório de custo.

### CONFIRMATORY_RUN

- Entrada: P1 com revisão F5, manifesto fechado e ambiente observado compatível.
- Saída: resultados de todas as execuções e inventário de arquivos.
- Aceitação: agenda respeitada e custos/falhas registrados.
- Falha: corrupção, violação de protocolo ou teto agregado excedido.
- Próximos: INDEPENDENT_VERIFICATION; HYPOTHESIS para nova pergunta/versionamento
  após invalidar o caráter confirmatório da evidência afetada.
- Evidências: logs brutos, checkpoints, commits, ambiente, falhas e candidatos.

### INDEPENDENT_VERIFICATION

- Entrada: candidatos exportados e inventário de campanha.
- Saída: releitura independente de certificados e parecer de integridade.
- Aceitação: todos os resultados usados na análise reconciliados por hash e regras.
- Falha: certificado faltante, discordância ou alteração de conteúdo.
- Próximos: ANALYSIS; VALIDATOR_READY em caso de defeito, invalidando a campanha
  afetada e exigindo novo protocolo antes de qualquer repetição científica.
- Evidências: comandos independentes, versões e testemunhos de divergência.

### ANALYSIS

- Entrada: P1, resultados e parecer de verificação, inclusive falhas.
- Saída: efeitos por n, incerteza, custos, sensibilidade e conclusão provisória.
- Aceitação: todas as sementes presentes; análise coincide com plano congelado.
- Falha: seleção de melhores sementes ou mudança de endpoint sem rotular exploração.
- Próximos: INDEPENDENT_VERIFICATION para erro de evidência; REPRODUCTION.
- Evidências: script/versões, saída, sementes de análise e inventário de entradas.

### REPRODUCTION

- Entrada: pacote de evidências e ambiente fixado.
- Saída: reconstrução da análise e dois novos blocos por n em instalação limpa.
- Aceitação: hashes de entradas e recálculo coincidem; diferenças estocásticas ou
  de hardware são explicadas e limitam conclusões quando materiais.
- Falha: instalação irrecuperável ou discrepância sem explicação suficiente.
- Próximos: ANALYSIS para incorporar limitação; REPORT.
- Evidências: comandos desde clone limpo, ambiente, novos registros e parecer.

### REPORT

- Entrada: análise e reprodução, completas ou com limitações explícitas.
- Saída: relatório positivo, negativo ou inconclusivo com quatro alegações separadas.
- Aceitação: revisor confere evidências, custos e limites da conclusão.
- Falha: afirmação de novidade/optimalidade sem suporte ou omissão de resultado ruim.
- Próximos: ANALYSIS para correção editorial/analítica versionada; ARCHIVED.
- Evidências: relatório final, parecer, protocolo e pacote reproduzível.

### ARCHIVED

- Entrada: relatório aceito ou motivo explícito de encerramento antecipado.
- Saída: inventário imutável e resumo do que foi e não foi demonstrado.
- Aceitação: evidência acessível por commit/hash, inclusive negativa.
- Falha: arquivos ausentes ou encerramento sem motivo.
- Próximo: nenhum; nova pergunta recebe novo identificador em QUESTION.
- Evidências: todo o pacote anterior e registro do encerramento.
