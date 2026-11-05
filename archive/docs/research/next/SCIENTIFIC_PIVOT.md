# Scientific Pivot

Proposta de 2026-11-05. A unidade de progresso será uma pergunta refutada,
uma redução demonstrada ou um resultado certificado sob orçamento explícito.
A hipótese de que mais candidatos por segundo produzem mais valor científico
passa a ser uma hipótese histórica a comparar. A nova prioridade é reduzir o
trabalho necessário para obter a mesma garantia matemática.

## Estado auditado

A base integrada é `4eb274795ae0fcdc78483f10994c5eccef9451dd`, P221. A P222
está localmente arquivada como `ARCHIVED / INCOMPLETE`. Seu recorte cobre
65.016 pares e contém 30.285 registros com k positivo até n = 20. Duas
reexecuções anteriores reproduziram o mesmo arquivo. A suíte global ficou
pendente após timeout da compilação Lean em uma cópia isolada.
[Arquivo da P222](../p222-census-report.md)

O ledger D047 classifica as construções [[20,2,6]] e [[16,2,4]] como
reconstruções verificadas e a paridade de k como fato conhecido. Os limites
por órbitas restringem classes de simetria. O esgotamento do orçamento de uma
campanha delimita a busca realizada. A retratação P161 e a auditoria D048
são antecedentes que orientam o novo protocolo.
[Ledger D047](../claims-ledger-d047.md) ·
[Retratação P161](../p161-claim-retraction.md) ·
[Decisões históricas](../../DECISIONS.md)

## Componentes a preservar

- `src/evobyte/evolution.py` possui mutação, cruzamento, seleção e gerações.
  A comparação do valor evolutivo exige controles sob o mesmo orçamento.
- `evaluate_qecc_20_2_bivariate`, em `bivariate_campaign.py`, amostra suportes
  com RNG em até 2.000 tentativas. Esse caminho é amostragem aleatória. As
  outras rotas também incluem construção SAT e verificações específicas.
- Aritmética GF(2), representação Pauli binária e construção de matrizes
  bivariadas são recursos reutilizáveis em códigos, grafos e observáveis.
- O recálculo independente P221 é referência para as duas instâncias reais.
  `Generated/BivariateReal.lean` trata matrizes e máscaras concretas. O lema
  de paridade em `BivariateDiscovery.lean` tem escopo aritmético menor.
- O censo local oferece entradas pequenas para conferir algoritmos novos.
  Sua contagem inclui descrições equivalentes.

[Motor evolutivo](../../../src/evobyte/evolution.py) ·
[Campanha bivariada](../../../src/evobyte/bivariate_campaign.py) ·
[P221](../p221-formal-honesty-report.md)

## Garantias que precisam ser explicitadas antes de comparar velocidade

Na implementação inspecionada, `verify_qecc_stabilizer_pure` enumera núcleos
para códigos CSS até n = 20 e procura lógicos abaixo de `claimed_d`. A
aceitação dessa rotina sustenta uma cota inferior nesse domínio. A rotina
precisa de uma testemunha de peso d para compor a afirmação de distância
exata. Para CSS com n > 20, o ramo usa colunas não nulas e distintas, que
sustentam d ≥ 3. O caminho geral não CSS também requer delimitação de escopo.
O relatório de milissegundos da P217 precisa ser lido à luz dessas garantias.
[Implementação do verificador](../../../scripts/verify_bivariate_certificate.py)

A estrutura `SATDistanceCertificate` armazena resposta, testemunha e métricas.
Uma resposta UNSAT deve ser acompanhada por prova rechecável ou por um
recálculo independente completo antes de uma alegação de impossibilidade.
[Solver de distância](../../../src/evobyte/sat_distance_solver.py)

## Onde reduzir complexidade

As campanhas e os relatórios por fase acumulam lógica especializada. Um
novo framework unificador aumentaria a superfície a auditar. O próximo
programa terá três scripts pequenos de experimento e verificadores próprios,
reutilizando apenas operações existentes cuja semântica foi conferida.
Os arquivos históricos ficam disponíveis para reprodução.

O novo ciclo usa quatro papéis. O Discoverer sugere candidatos. O Verifier
confere uma propriedade e um domínio explícitos. O Novelty Auditor registra
fontes, versões e possíveis redundâncias. O Formal Prover atua sobre um
candidato selecionado e um enunciado revisado. A equipe humana decide
originalidade e mudança de problema.

## Hipóteses substitutas

H-A pergunta se a enumeração do núcleo em Gray code reduz tempo e memória
para certificar a mesma distância exata. H-B pergunta se uma decomposição
certificada por subgrupo evita verificações repetidas de blocos. H-C pergunta
se uma representação exata de circuitos CNOT+T produz certificados de
identidade mais baratos que a busca sobre palavras. Os três experimentos
podem terminar com um resultado negativo ou uma reprodução de método conhecido.
[Experimentos](THREE_EXPERIMENTS_THAT_COULD_MATTER.md)

A bibliografia inicial já estabelece paridade, fórmulas de dimensão e
reduções por simetria para famílias BB. A busca de um teorema novo exige
uma lacuna mais específica, como condições de preservação de peso para
uma redução ainda sem prova. Essa lacuna será registrada na P229 antes
de promover a linha a pesquisa de originalidade.
[BB peso 8, v1](https://arxiv.org/abs/2609.06572v1) ·
[Bicycle por divisores, v3](https://arxiv.org/abs/2608.09115v3)
