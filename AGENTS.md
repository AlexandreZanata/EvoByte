# Regras para agentes do EvoByte

Estas regras valem para toda a raiz ativa. O projeto está em planejamento;
implemente somente quando receber uma ficha de tarefa explicitamente autorizada.

1. Leia esta orientação, a ficha em `tasks/` e seus contratos referenciados.
2. Confira dependências e evidências dos portões antes de editar código.
3. Execute uma tarefa por vez; respeite a lista de arquivos permitidos.
4. Preserve `HISTORICO.md`, a branch `archive/legacy-history`, a tag
   `archive-v1-legacy` e quaisquer outros artefatos arquivados. Não restaure,
   audite ou migre o legado como pré-requisito do novo projeto.
5. Preserve trabalho novo encontrado. Registre conflitos e pare a tarefa afetada.
6. A definição científica está em `docs/01-scientific-protocol.md`; os contratos,
   em `docs/03-architecture-and-contracts.md`; os custos, em
   `docs/05-experiment-budget.md`. Não duplique regras divergentes.
7. Não altere hipótese, métrica, regras, verificadores, referências ou avaliação
   final para favorecer resultados. Mudanças científicas exigem decisão registrada
   e nova versão do protocolo; não são decisões do implementador.
8. Implemente e valide os dois verificadores antes de qualquer política aprendida.
   Eles não podem compartilhar o núcleo de detecção de ciclos.
9. Candidatos são dados. Não execute código produzido pela política.
10. Não inicie campanha sem manifesto, limite agregado e registro de consumo.
11. Conte geração de dados, aquecimento, treino, inferência, busca, verificação e
    salvamento conforme a modalidade. Não oculte ajuste ou pré-treinamento.
12. Preserve sementes ruins, erros, interrupções e resultados negativos.
13. Não confunda validade, desempenho, novidade, maximalidade e optimalidade.
    O agente executor não declara novidade científica.
14. Não reduza testes para passar, nem amplie arquitetura ou modelo por iniciativa
    própria. Ambiguidade científica vira questão no registro de decisões.
15. Execute o comando de aceitação da ficha e registre saída, commit e custo em
    `reports/tasks/<ID>.md`. Um comando planejado ainda inexistente não passou.
16. Entregue resumo curto com arquivos, verificações, falhas, custos e próxima
    dependência. Pare ao concluir a tarefa; não avance automaticamente.
17. Revisões independentes nos portões F0, F1, F3, F5 e F6 devem inspecionar
    arquivos e evidências em sessão separada, com identidade e parecer registrados.
    A explicação do autor não substitui essa revisão.

Ordem de trabalho e primeiras tarefas: `tasks/INDEX.md`.
