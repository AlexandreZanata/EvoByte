# Registro de decisões

Data inicial: 5 de novembro de 2026. Decisões de desenho são propostas para P0;
não equivalem a aprovação de portões ou evidência experimental.

## D001 Recomeçar na raiz ativa

Adotar arquitetura nova, preservando referências, branch e tag do legado.
Rejeitar migração ou auditoria do projeto antigo nesta etapa. Base local encontrada:
`99fbfc068c0426503645e58347b131a44ae28516`; árvore de trabalho inicialmente limpa.
Arquivos ativos preexistentes registrados em `00`; não havia implementação nova.

## D002 Um domínio e uma contribuição inicial

Usar ex(n;{C3,C4}) e priorizar eficiência de método. A literatura de `02` registra
ótimos para n=8..32; não presumir que a faixa contenha recordes em aberto.
Rejeitar expansão simultânea para vários problemas. Não se justifica alternativa
de domínio antes de um piloto demonstrar inviabilidade.

## D003 Verificadores antes da busca aprendida

Referência por enumeração de triplas/quádruplas e execução por vizinhanças/bitsets.
Rejeitar um único verificador reutilizado em todos os papéis. Custo e legibilidade
são adequados a n≤32; independência reduz erro correlacionado sem prometer prova formal.

## D004 Política linear antes de rede neural

Escolher regressão ridge sobre 12 características simétricas, 13 parâmetros.
Rejeitar Transformer, GNN complexa e RL inicial por custo e dificuldade de isolar
efeitos. NumPy basta; PyTorch, GPU e modelos maiores não entram por antecipação.
O teto de 300 mil parâmetros é limite, nunca alvo. Falhar com 13 parâmetros é
um resultado útil; não autoriza aumentar indefinidamente até vencer.

## D005 Busca local como referência obrigatória

Além de random/greedy, usar motor de adição e perturbação com seleção uniforme
e manual inspirada em R4. Comparar pesos aprendidos e aleatórios no mesmo motor.
Rejeitar gerar grafos quase sempre inválidos como referência. Adaptação inicial
não autoriza alegar superioridade sobre todo o estado da arte.

## D006 Métrica, custo e split

Métrica principal: melhor m certificado em 600 s de partida, por n.
Reservar n={24,28,32}; desenvolvimento n={8,10,12,16}; ajuste n={18,20}.
Não trocar para tempo até ótimo se o endpoint saturar. Modo amortizado é futuro
e exige contabilização própria. Limites e cronograma estão em `05`.

## D007 Congelamento em duas etapas

P0 fixa desenvolvimento, grade e regra de piloto; P1 fixa B*, R, sementes e
análise antes do final. Não rotular a versão de planejamento 0.1 como congelada.
Mudanças científicas depois do final criam versão nova e tornam o final observado
exploratório. Rejeitar ajustes silenciosos e exclusão de resultados negativos.

## D008 Revisão independente baseada em evidência

F0, F1, F3, F5 e F6 exigem sessão/revisor separado, commit de entrada, comandos,
arquivos inspecionados, parecer e pendências. A revisão não pode aprovar apenas
por concordar com o resumo do autor. Esta entrega não contém pareceres fictícios.

## D009 Falha entra na análise

Execução com falha do método recebe m=0 do grafo vazio certificado inicial;
checkpoints posteriores são sensibilidade. Evento externo verificável repete o
bloco inteiro dentro da reserva. Isso evita selecionar só sucessos e prioriza
conclusão ponta a ponta. Relatar também frequência e causa das falhas.

## Questões que dependem do piloto

- Q001: treino e características custam menos que o benefício na busca?
- Q002: referências saturam o ótimo e tornam H1 pouco informativa?
- Q003: qual B* e qual R resultam das regras congeladas em P0?
- Q004: qual configuração compartilhada e lambda vencem o ajuste limitado?
- Q005: reservas de verificação/salvamento suportam o ambiente observado?
- Q006: a variação entre tamanhos permite inferência útil com até 20 blocos?

Essas perguntas não estão respondidas. Qualquer mudança fora das escolhas já
previstas deve registrar: motivo, evidência anterior à decisão, alternativas,
impacto em validade/custo/split, responsável, versão afetada e novo portão exigido.

## D010 Congelamento do protocolo P0 e aprovação do portão F0

Em 5 de novembro de 2026, com a conclusão de F00-T01 e F00-T02, o protocolo de
desenvolvimento P0 foi congelado em `protocols/development-v1.json` (SHA-256:
`3811a92fc15ecf4584edb604dbb26225a0915ba60d801ad41a128e7d4764ede7`), amparado
pelo extrato bibliográfico `reports/sources/girth-ge-5-v1.md`. A revisão independente
do portão F0 foi formalizada em `reports/reviews/F0.md` com parecer APROVADO,
autorizando o avanço para a fase F1 (tarefa F01-T01).

## Situação da entrega de planejamento

- **Planejado:** domínio, H1, contratos, fases, máquina de estados, tarefas e quotas.
- **Concluído e Aprovado:** Portão F0 (F00-T01 auditoria bibliográfica e F00-T02 protocolo P0 congelado com revisão independente).
- **Não executado:** laboratório, instalação experimental, verificadores, busca,
  treinamento, medições do hardware, campanhas e revisões científicas dos portões futuros.
- **Bloqueado por portão futuro:** implementação além da ficha autorizada,
  aprendizado antes de F3 e confirmação antes de P1. Não há dependência de cloud
  nem fonte indispensável inacessível registrada nesta entrega.
