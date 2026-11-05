# Trabalhos relacionados e referências verificadas

Consulta bibliográfica em **5 de novembro de 2026**. Fontes primárias consultadas
para delimitar o benchmark, não para certificar qualquer execução do EvoByte.

## R1 Garnick, Kwong e Lazebnik

David K. Garnick, Y. H. Harris Kwong e Felix Lazebnik, *Extremal Graphs without
Three-Cycles or Four-Cycles*, Journal of Graph Theory 17 (1993), 633–645.
[Texto dos autores em PDF](https://www.dcs.gla.ac.uk/~pat/jchoco/extremal/papers/10.1.1.92.3502.pdf).

O resumo estabelece valores exatos até 24 vértices e construções que fornecem
limites inferiores até 200. A definição inicial coincide com ex(n;{C3,C4}).
A tabela 1 inclui construções e alguns valores exatos, que não devem ser
confundidos: uma construção sozinha fornece apenas um limite inferior.
Uso no projeto: formalização e referências históricas para tamanhos pequenos.

## R2 Miller e Codish

Alice Miller e Michael Codish, *Graphs with girth at least 5 with orders between
20 and 32*, arXiv:1708.06576v2, 23 de agosto de 2017.
[Registro versionado](https://arxiv.org/abs/1708.06576v2) e
[texto completo](https://arxiv.org/html/1708.06576v2).

O trabalho desenvolve restrições estruturais e enumeração com quebra de simetria.
A tabela 1 registra, entre outros, f(24)=54, f(28)=68 e f(32)=85. Os apêndices
apresentam construções. Uso no projeto: confirmar que os tamanhos finais propostos
têm ótimos conhecidos e que busca exata com simetria é uma referência científica
relevante, embora não seja a primeira implementação sob 600 s.

## R3 Afzaly e McKay

Narjess Afzaly e Brendan McKay, *Extremal Graphs and Turan numbers*, coleção
mantida pelos pesquisadores na Australian National University.
[Seção H={C3,C4}](https://users.cecs.anu.edu.au/~bdm/data/extremal.html).

Na seção correta, os pares n:ex(n;{C3,C4}) para a faixa inicial são:

```text
 8:10   9:12  10:15  11:16  12:18  13:21  14:23  15:26  16:28
17:31  18:34  19:38  20:41  21:44  22:47  23:50  24:54  25:57
26:61  27:65  28:68  29:72  30:76  31:80  32:85
```

Essas entradas estão sem o prefixo “≥”, que a coleção usa para distinguir valores
exatos de limites inferiores. Há arquivos sparse6 associados às construções.
Não usar a seção que proíbe somente C4, cujos números são diferentes.
Uso: metas e validação documental; os arquivos de grafos não integram o treino
ou a inicialização da avaliação final. O laboratório ainda não baixou nem verificou
essas construções.

## R4 Goedgebeur, Jooken, Joret e Van den Eede

Jan Goedgebeur, Jorik Jooken, Gwenaël Joret e Tibo Van den Eede, *Improved lower
bounds on the maximum size of graphs with girth 5*, arXiv:2508.05562v2,
22 de setembro de 2026.
[Registro versionado](https://arxiv.org/abs/2508.05562v2) e
[seção 2 do texto completo](https://arxiv.org/html/2508.05562v2#S2).

O algoritmo 1 alterna adições legais, com seleção parcialmente aleatória baseada
em graus, e remoções aleatórias com memória recente. O algoritmo completo transfere
construções entre ordens vizinhas. O artigo apresenta melhorias de limites
inferiores na faixa 74–198, exceto 96 e 97. Uso no projeto: exigir uma busca local
competente como referência, não somente amostragem aleatória. A versão inicial
do EvoByte simplifica o motor e não transfere grafos entre tamanhos; suas conclusões
ficam restritas aos métodos efetivamente comparados.

## Conclusão de escopo

A evidência acima sustenta usar n≤32 para reprodução e avaliação de método.
Não há, nesta faixa, uma oportunidade de “novo recorde” presumida pelo plano.
Uma melhoria de desempenho continua sendo hipótese, e seu caráter publicável
exigiria comparação mais ampla de métodos. Não reivindicar ineditismo da política
linear ou da ideia de orientar busca com aprendizado.

## Pendências antes dos congelamentos

- F0: revisor conferir os números usados no manifesto contra R2/R3 e registrar
  URL, data, versão, seção e hash do extrato bibliográfico armazenado localmente.
- F3: verificar se `local_manual` representa uma referência suficientemente
  competente; documentar limitações frente ao algoritmo completo de R4.
- F5: reconferir as fontes se houver mudança de n, regra ou objetivo. Não estender
  os ótimos da tabela a tamanhos não listados nem a grafos regulares/conexos.
- Qualquer futura alegação de novidade exige pesquisa específica e comparação
  independente na data da alegação. Busca sem achado não prova inexistência.

Não se propõe domínio alternativo agora: os verificadores são pequenos e o problema
é compatível com um piloto local. Se o piloto demonstrar inviabilidade, registrar
uma única alternativa verificável e sua justificativa antes de mudar o domínio.
