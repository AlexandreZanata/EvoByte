# Índice das tarefas de implementação

**Estado:** todas as fichas são planejadas. Nenhuma tarefa de implementação ou campanha foi executada nesta entrega. Cada ficha autoriza uma unidade verificável quando for explicitamente atribuída ao executor.

Leia [AGENTS.md](../AGENTS.md), confira dependências e execute somente uma ficha por vez. Arquivos futuros mencionados nas fichas ainda não existem. Relatórios de conclusão devem registrar comandos, saídas, commit, custos e falhas.

## Primeiras três tarefas

1. [F00-T01](F00-T01.md): conferir fontes primárias e metas.
2. [F00-T02](F00-T02.md): congelar P0 com revisão independente.
3. [F01-T01](F01-T01.md): criar o esqueleto mínimo, após F0 aceito.

## Ordem e dependências

### F0

- [F00-T01 — Conferir referências e metas do domínio](F00-T01.md). Depende de: planejamento.
- [F00-T02 — Congelar o protocolo de desenvolvimento P0](F00-T02.md). Depende de: F00-T01.

### F1

- [F01-T01 — Criar o esqueleto mínimo executável](F01-T01.md). Depende de: F00-T02.
- [F01-T02 — Definir candidato e serialização canônica](F01-T02.md). Depende de: F01-T01.
- [F01-T03 — Implementar o verificador de referência](F01-T03.md). Depende de: F01-T02.
- [F01-T04 — Implementar o verificador de execução](F01-T04.md). Depende de: F01-T03.
- [F01-T05 — Confrontar verificadores em casos exaustivos](F01-T05.md). Depende de: F01-T04.
- [F01-T06 — Exportar candidato e certificado independente](F01-T06.md). Depende de: F01-T05.

### F2

- [F02-T01 — Registrar configuração, ambiente e eventos](F02-T01.md). Depende de: F01-T06.
- [F02-T02 — Controlar o relógio de uma execução](F02-T02.md). Depende de: F02-T01.
- [F02-T03 — Supervisionar trabalhador e encerramento seguro](F02-T03.md). Depende de: F02-T02.
- [F02-T04 — Aplicar limite agregado da campanha](F02-T04.md). Depende de: F02-T03.
- [F02-T05 — Expor CLI de verificação e execução supervisionada](F02-T05.md). Depende de: F02-T04.

### F3

- [F03-T01 — Gerar a máscara de adições legais](F03-T01.md). Depende de: F02-T05.
- [F03-T02 — Construir a referência aleatória com reinícios](F03-T02.md). Depende de: F03-T01.
- [F03-T03 — Adicionar o seletor guloso por graus](F03-T03.md). Depende de: F03-T02.
- [F03-T04 — Adicionar perturbação e referências locais](F03-T04.md). Depende de: F03-T03.
- [F03-T05 — Medir referências no desenvolvimento](F03-T05.md). Depende de: F03-T04.

### F4

- [F04-T01 — Calcular características simétricas de ações](F04-T01.md). Depende de: F03-T05.
- [F04-T02 — Gerar alvos de aprendizado por completações](F04-T02.md). Depende de: F04-T01.
- [F04-T03 — Ajustar e aplicar a política linear](F04-T03.md). Depende de: F04-T02.
- [F04-T04 — Integrar controle sem treino e ensaios curtos](F04-T04.md). Depende de: F04-T03.
- [F04-T05 — Executar a grade de ajuste predefinida](F04-T05.md). Depende de: F04-T04.
- [F04-T06 — Executar piloto e calcular decisões para P1](F04-T06.md). Depende de: F04-T05.

### F5

- [F05-T01 — Implementar análise pré-especificada em dados sintéticos](F05-T01.md). Depende de: F04-T06.
- [F05-T02 — Congelar manifesto confirmatório e revisar F5](F05-T02.md). Depende de: F05-T01.
- [F05-T03 — Executar a confirmação sem ajustes retroativos](F05-T03.md). Depende de: F05-T02.

### F6

- [F06-T01 — Rever certificados e produzir análise congelada](F06-T01.md). Depende de: F05-T03.
- [F06-T02 — Reproduzir em ambiente limpo](F06-T02.md). Depende de: F06-T01.
- [F06-T03 — Concluir, revisar e arquivar a pergunta](F06-T03.md). Depende de: F06-T02.

## Portões e política de reparo

F0, F1, F3, F5 e F6 exigem revisão independente em sessão separada, baseada em evidências. F2 exige encerramento e contabilidade demonstrados. F4 exige aprendizado mensurado e controles, não vitória. Os critérios completos estão em [fases e estados](../docs/04-phases-and-gates.md).

Um portão falho não libera a próxima ficha. Registrar o contraexemplo e criar uma ficha de reparo restrita aos arquivos afetados, com hipótese causal e teste de regressão; decisão científica volta ao responsável pelo protocolo. O agente não altera os critérios de aceitação.

As quotas são compartilhadas, não multiplicadas pelo número de tarefas. Campanhas de desenvolvimento, ajuste, piloto, confirmação e reprodução seguem [orçamento](../docs/05-experiment-budget.md). Toda execução real usa manifesto e supervisor. Fixe código, configuração e manifesto em commit limpo antes de começar a campanha; escreva os relatórios versionados depois de encerrar as tentativas. Nenhuma ficha autoriza mexer no legado.

Os exemplos em [docs/examples](../docs/examples/README.md) são dados ilustrativos e devem ser recusados para execução.
