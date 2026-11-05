# Quantum Frontier Research Map

Mapa de triagem de 2026-11-05. As perguntas abaixo são propostas específicas,
com lacunas candidatas. A leitura de páginas primárias, resumos e versões
não constitui auditoria completa de novidade. A P229 deve conferir os
teoremas relevantes e registrar a decisão antes da execução. Confiança na
novidade é baixa em todas as quinze entradas nesta rodada.

Os tetos iniciais são nível A, 2 núcleos, 512 MiB e 30 s para uma instância
mínima. Quando o algoritmo exigir mais, registrar INCONCLUSIVE e revisar
a proposta. Os tetos são orçamentos, sem previsão medida de duração.
As propostas são matemáticas/computacionais e independem de laboratório.
Uma validação experimental de efeito físico seria um projeto separado.

## Referências solicitadas e estado da consulta

- BB peso 8, arXiv:2609.06572v1, enviado em 2026-09-06. Página primária e
  resumo conferidos. Fórmulas de dimensão, simetrias e subgrupos já aparecem
  no trabalho. Isso torna esses temas candidatos a reprodução.
  [Fonte](https://arxiv.org/abs/2609.06572v1)
- Busca por divisores, arXiv:2608.09115v3, revisão de 2026-09-01. Página e
  resumo conferidos. Gcd no caso cíclico já é parte do método.
  [Fonte](https://arxiv.org/abs/2608.09115v3)
- ZX exaustivo, arXiv:2503.10983v2, revisão de 2025-05-08. Página e resumo
  conferidos. DFS/IDDFS e podas já são baseline publicado.
  [Fonte](https://arxiv.org/abs/2503.10983v2)
- qcode-discovery. README do repositório consultado em 2026-11-05. Ele
  apresenta busca evolutiva guiada por LLM para BB/PBB. Seus resultados e
  commit precisam ser fixados e auditados na P229, antes de comparar.
  [Repositório](https://github.com/qiskit-community/qcode-discovery)
- DOI 10.1103/1757-fx9c, PRL 136, 246501, publicado em 2026-06-17.
  Título e resumo editorial conferidos. O texto integral pede acesso na
  página consultada. A avaliação de detalhes do método fica pendente.
  [Página primária](https://journals.aps.org/prl/abstract/10.1103/1757-fx9c)
- DOI 10.1103/1gjs-2rhx, PRX Quantum 6, 040325, publicado em 2025-11-05.
  A página primária descreve representação de estabilizadores por grafos.
  Conferir as condições dos teoremas para qualquer novo filtro.
  [Página primária](https://journals.aps.org/prxquantum/abstract/10.1103/1gjs-2rhx)
- Fábricas compactas, arXiv:2606.07734v2, revisão de 2026-07-09. Os no-gos
  e protocolos pequenos já relatados restringem propostas de minimalidade.
  [Fonte](https://arxiv.org/abs/2606.07734v2)
- Verificação formal de circuitos é uma dependência bibliográfica adicional.
  O corpus inicial usa semântica exata e o histórico Lean do projeto. Uma
  auditoria específica de ferramentas como VyZX/VOQC precisa preceder
  qualquer alegação de contribuição formal nova.

## Critérios e matriz de decisão

Cada vetor tem nove notas na ordem O,V,E,M,G,R,U,I,F. Elas significam
originalidade potencial, verificação independente, economia de processamento,
microexperimento viável, generalização, relevância comunitária, reutilização,
limites/impossibilidades e falsificabilidade. Zero é impedimento conhecido,
1 é fraco, 2 é incerto, 3 é plausível, 4 é favorável e 5 é diretamente
estruturado para o critério. As notas são juízos de planejamento, sem
medição ou probabilidade numérica. Não calcular uma média para ranquear.

São eliminatórios um checker inviável, hardware fora do orçamento, pergunta
sem falsificação, resultado inteiramente resolvido sem contribuição de
método e experimento que apenas mede uma propriedade conhecida. Uma linha
pode ser mantida como calibração de engenharia com essa classificação,
mesmo quando sua candidatura a novidade for eliminada.

## R01 — Distância CSS com núcleo percorrido em Gray code

- Subárea — Correção quântica de erros.
- Problema específico — Nos seis exemplos P222 com d ≥ 4, uma enumeração em streaming do núcleo certifica o mesmo d com menos tempo e memória?
- Interesse — Custo de certificar uma distância pequena é um gargalo mensurável e reutiliza referências reais.
- Melhor resultado verificado nesta triagem — O verificador P217 já enumera núcleos em parte do domínio, enquanto P221 usa máscaras por peso. A mudança proposta é de representação e custo.
- Lacuna a auditar — Falta uma comparação de garantia, tempo e memória em entradas congeladas. A novidade algorítmica está pendente.
- Contribuição potencial — Um benchmark reproduzível e, se houver ganho, um checker menor ou menos memória para o mesmo domínio.
- Algoritmo — Eliminação GF(2), Gray code e mínimo de peso fora do estabilizador.
- Redução — Enumerar 2^(n−r) vetores do núcleo, em vez de todas as máscaras ambientais, quando isso for menor.
- Hardware — CPU local, primeiro teste com até 2 núcleos e 512 MiB.
- Custo previsto — microinstância limitada a 30 s, duração real por medir.
- Verificação independente — Baseline P221 reexecutado por caminho independente, com teste separado da testemunha.
- Certificado — Suportes, ranks, máscara lógica e protocolo completo de replay da cota inferior.
- Risco principal — O custo de pertencimento pode dominar e o método já pode ser bem conhecido.
- Sucesso objetivo — Mesmos seis resultados e ganho agregado ≥ 1,2× em duas baterias, dentro do teto.
- Abandono — Encerrar a hipótese de ganho no recorte quando o ganho não se reproduzir.
- Chance qualitativa — Média para engenharia, baixa para originalidade matemática. Há entradas prontas, mas o algoritmo básico é conhecido.
- Última consulta — 2026-11-05. Confiança de novidade baixa até auditoria específica.
- Notas O,V,E,M,G,R,U,I,F — `[1, 5, 5, 5, 3, 4, 5, 3, 5]`. Originalidade baixa pela enumeração conhecida. Verificação exata, custos pequenos e falsificação direta favorecem o piloto. Generalização limitada pelo tamanho do núcleo.

[Referência de partida](../p221-formal-honesty-report.md)

## R02 — Decomposição BB por cosets do subgrupo de suporte

- Subárea — Códigos quânticos e álgebra de grupos.
- Problema específico — A normalização independente dos dois suportes induz uma decomposição certificada que transfere k e d para blocos menores?
- Interesse — Uma identidade estrutural pode eliminar verificações repetidas de componentes.
- Melhor resultado verificado nesta triagem — A literatura BB recente estabelece fórmulas de dimensão, simetrias e vetores associados a subgrupos. A decomposição básica pertence a essa estrutura conhecida.
- Lacuna a auditar — É preciso delimitar uma implementação com certificado de permutação e seu ganho líquido no EvoByte.
- Contribuição potencial — Uma redução verificável do trabalho e eventual contraexemplo a uma extensão proposta.
- Algoritmo — Fecho aditivo em grupo pequeno, cosets e conferência exata de blocos.
- Redução — Trocar t blocos idênticos pela distância de um bloco e pela verificação da transformação.
- Hardware — CPU local, primeiro teste com até 2 núcleos e 512 MiB.
- Custo previsto — microinstância limitada a 30 s, duração real por medir.
- Verificação independente — Reconstrução independente de HX/HZ, permutações completas e controle por componentes.
- Certificado — Permutações, partição em cosets, blocos e testemunha lógica levantada.
- Risco principal — Confundir equivalência linear com preservação de peso, ou ignorar degenerescência.
- Sucesso objetivo — Transformação correta nos 128 registros e custo poupado maior que seu checker em casos aplicáveis.
- Abandono — Uma discrepância matemática exige revisão. Ausência de decomposição nos 128 encerra o recorte.
- Chance qualitativa — Média para método, baixa para teorema novo. A estrutura é barata, mas há sobreposição bibliográfica forte.
- Última consulta — 2026-11-05. Confiança de novidade baixa até auditoria específica.
- Notas O,V,E,M,G,R,U,I,F — `[1, 5, 5, 5, 5, 4, 5, 4, 5]`. Generalização alta pela fórmula de blocos. Verificação e reutilização altas. A novidade tem nota baixa porque a álgebra de subgrupos já é estudada.

[Referência de partida](https://arxiv.org/abs/2609.06572v1)

## R03 — Filtro de dimensão em bicycle cíclico com gcd

- Subárea — CSS cíclicos e quasi-cíclicos.
- Problema específico — Um filtro de gcd evita construir matrizes para suportes de peso ≤ 4 em Z_l, l ≤ 15, com k incompatível com o alvo?
- Interesse — Descartar a família antes da distância pode ser mais barato que acelerar o solver.
- Melhor resultado verificado nesta triagem — A busca por divisores em 2026 usa o anel polinomial cíclico e extrai dimensão por gcd.
- Lacuna a auditar — A pergunta local é o ganho medido e o limite de aplicação em grupos não cíclicos.
- Contribuição potencial — Reprodução de um filtro conhecido e catálogo explícito de onde a extensão falha.
- Algoritmo — Euclides em F2[x], seguido de rank GF(2) como controle.
- Redução — Rejeitar k impossível antes de construir HX/HZ.
- Hardware — CPU local, primeiro teste com até 2 núcleos e 512 MiB.
- Custo previsto — microinstância limitada a 30 s, duração real por medir.
- Verificação independente — Posto de matrizes reconstruídas por outro caminho.
- Certificado — Polinômios, gcd e identidades de Bézout.
- Risco principal — Aplicar automaticamente um resultado cíclico a um produto que não é cíclico.
- Sucesso objetivo — Concordância exata de k no domínio e ganho líquido sobre construção direta.
- Abandono — Regra redundante sem ganho ou extensão incorreta encerra a proposta.
- Chance qualitativa — Média para engenharia, baixa para contribuição original porque o filtro já foi publicado.
- Última consulta — 2026-11-05. Confiança de novidade baixa até auditoria específica.
- Notas O,V,E,M,G,R,U,I,F — `[1, 5, 5, 5, 4, 4, 4, 4, 5]`. Excelente economia potencial e checker simples. Novidade baixa e aplicabilidade restrita ao anel correto reduzem sua prioridade.

[Referência de partida](https://arxiv.org/abs/2608.09115v3)

## R04 — Impossibilidades em fábricas de magic states restritas

- Subárea — Magic-state distillation e códigos triortogonais.
- Problema específico — Em uma gramática fixa de matrizes binárias com até 8 colunas e 4 linhas, uma restrição adicional de profundidade impede a distância desejada?
- Interesse — Restrições de recursos podem produzir um no-go curto e útil.
- Melhor resultado verificado nesta triagem — O trabalho de fábricas compactas de 2026 usa códigos clássicos e SAT, com no-gos e construções pequenas. Os limites publicados têm hipóteses de implementação.
- Lacuna a auditar — Uma restrição extra só oferece oportunidade se escapar do teorema existente e tiver relevância prática.
- Contribuição potencial — Contraexemplo ou impossibilidade na gramática declarada, com prova rechecável.
- Algoritmo — SAT incremental sobre paridades e sobreposições, redução por permutações de colunas.
- Redução — Fixar forma escalonada e classes de colunas apenas após demonstrar completude.
- Hardware — CPU local, primeiro teste com até 2 núcleos e 512 MiB.
- Custo previsto — microinstância limitada a 30 s, duração real por medir.
- Verificação independente — Checker de matrizes e prova UNSAT conferida por ferramenta distinta.
- Certificado — Matriz/circuito para existência ou prova verificável para impossibilidade.
- Risco principal — Redescobrir um no-go já publicado ou generalizar além da gramática.
- Sucesso objetivo — Resolver integralmente um domínio novo e delimitado com certificado.
- Abandono — Sem prova verificável ou com teorema publicado cobrindo a pergunta, eliminar.
- Chance qualitativa — Baixa a média. Instâncias discretas são acessíveis, mas a literatura de 2026 já cobre limites fortes.
- Última consulta — 2026-11-05. Confiança de novidade baixa até auditoria específica.
- Notas O,V,E,M,G,R,U,I,F — `[2, 4, 3, 4, 4, 5, 3, 5, 5]`. Relevância e impossibilidade altas. Custo e certificado dependem do solver, e originalidade requer uma restrição adicional defensável.

[Referência de partida](https://arxiv.org/abs/2606.07734v2)

## R05 — Contextualidade com pesos racionais em grafo fixo

- Subárea — Fundamentos quânticos e contextualidade.
- Problema específico — Em um grafo de exclusividade fixado com até 9 vértices, pesos inteiros de 0 a 3 geram um testemunho mais robusto sob uma restrição física explícita?
- Interesse — Separar limite clássico e realização quântica permite certificados pequenos.
- Melhor resultado verificado nesta triagem — A otimização de desigualdades de contextualidade pode ser formulada por programação linear. O método geral é conhecido.
- Lacuna a auditar — A lacuna depende de uma família de projetores e de uma restrição de robustez ainda não cobertas.
- Contribuição potencial — Uma desigualdade específica ou um certificado de que a nova restrição não melhora o limite.
- Algoritmo — Enumeração de conjuntos independentes e LP racional.
- Redução — Automorfismos do grafo e agrupamento de pesos equivalentes.
- Hardware — CPU local, primeiro teste com até 2 núcleos e 512 MiB.
- Custo previsto — microinstância limitada a 30 s, duração real por medir.
- Verificação independente — Enumerar todos os conjuntos independentes e conferir projetores exatos.
- Certificado — Pesos, limite clássico, vetores/projetores e identidade racional.
- Risco principal — Um gap em um invariante de grafo pode não ter realização física na dimensão escolhida.
- Sucesso objetivo — Violação exata com realização e ganho no critério de robustez pré-registrado.
- Abandono — Ausência de realização exata ou desigualdade já conhecida elimina a proposta.
- Chance qualitativa — Baixa a média. O domínio é pequeno, mas converter o gap em contribuição requer cuidado físico.
- Última consulta — 2026-11-05. Confiança de novidade baixa até auditoria específica.
- Notas O,V,E,M,G,R,U,I,F — `[2, 4, 4, 5, 3, 4, 2, 4, 5]`. Piloto pequeno e falsificável. A realização quântica e a novidade são os pontos menos resolvidos.

[Referência de partida](https://arxiv.org/abs/1204.3741v2)

## R06 — Bell pequeno com certificado SOS exato

- Subárea — Não-localidade e emaranhamento.
- Problema específico — Um ansatz SOS de grau 2 em observáveis binários encontra uma cota simbólica para uma família bipartida com três ajustes?
- Interesse — Uma identidade SOS pode substituir uma otimização numérica extensa.
- Melhor resultado verificado nesta triagem — Construções de Bell por somas de quadrados e nullifiers já produzem famílias e resultados de self-testing.
- Lacuna a auditar — Uma família nova exige parâmetros, estado-alvo e lacuna em relação às construções existentes.
- Contribuição potencial — Cota certificada, identidade paramétrica ou refutação do ansatz.
- Algoritmo — SDP exploratória e reconstrução algébrica exata dos coeficientes.
- Redução — Simetrias de troca de partes, sinais e ajustes, com relações de comutação declaradas.
- Hardware — CPU local, primeiro teste com até 2 núcleos e 512 MiB.
- Custo previsto — microinstância limitada a 30 s, duração real por medir.
- Verificação independente — Expandir a identidade em álgebra não comutativa independente e testar o estado-alvo.
- Certificado — Lista de quadrados e identidade polinomial exata, com hipótese dos operadores.
- Risco principal — Uma matriz numericamente positiva não é um certificado exato.
- Sucesso objetivo — Identidade SOS válida e comparação específica com a melhor cota verificada.
- Abandono — Reconstrução exata inviável ou cota já estabelecida sem método novo.
- Chance qualitativa — Baixa para descoberta imediata. A validação pode ser curta depois de uma busca difícil.
- Última consulta — 2026-11-05. Confiança de novidade baixa até auditoria específica.
- Notas O,V,E,M,G,R,U,I,F — `[3, 4, 3, 4, 5, 5, 1, 5, 5]`. Generalização e relevância altas. Pouco código reutilizável e reconstrução exata incerta justificam adiar.

[Referência de partida](https://arxiv.org/abs/2308.08601v2)

## R07 — Limites clássicos de jogos de correlação reduzidos

- Subárea — Fundamentos e jogos não locais.
- Problema específico — Para um jogo bipartido binário com até três perguntas por parte, uma restrição de comunicação zero admite um limite racional certificado mais compacto?
- Interesse — É uma ponte barata entre correlação, programação linear e testemunhas.
- Melhor resultado verificado nesta triagem — Jogos de matching e correlações quânticas distinguem estratégias clássicas, nonsignaling e quânticas sob hipóteses específicas.
- Lacuna a auditar — É preciso fixar um jogo fora dos casos resolvidos e uma nova função objetivo antes da busca.
- Contribuição potencial — Certificado dual racional ou contraexemplo a uma cota conjecturada.
- Algoritmo — Enumerar estratégias determinísticas e resolver o dual LP exatamente.
- Redução — Órbitas de relabeling de perguntas e respostas.
- Hardware — CPU local, primeiro teste com até 2 núcleos e 512 MiB.
- Custo previsto — microinstância limitada a 30 s, duração real por medir.
- Verificação independente — Conferir a cota em todas as estratégias e validar a estratégia candidata separadamente.
- Certificado — Coeficientes duais e estratégia de realização.
- Risco principal — Uma vantagem nonsignaling pode não ser quântica.
- Sucesso objetivo — Limite com prova e separação relevante no cenário fixado.
- Abandono — Jogo saturado na literatura ou ausência de realização física elimina.
- Chance qualitativa — Baixa. A mecânica é barata, mas cenários muito pequenos estão bem estudados.
- Última consulta — 2026-11-05. Confiança de novidade baixa até auditoria específica.
- Notas O,V,E,M,G,R,U,I,F — `[2, 5, 4, 5, 3, 4, 2, 4, 5]`. Verificação clássica é simples. A originalidade e a realização quântica limitam a expectativa.

[Referência de partida](https://arxiv.org/abs/2502.05136v1)

## R08 — Identidades locais CNOT+T com certificado exato

- Subárea — Circuitos e síntese exata.
- Problema específico — No alfabeto de seis portas e comprimento até seis, agrupar semânticas encontra regras mais baratas que o baseline local e baratas de verificar?
- Interesse — Uma regra local pode ser reaplicada em circuitos maiores com certificado pequeno.
- Melhor resultado verificado nesta triagem — T-count em CNOT+T tem formulação conhecida em códigos Reed–Muller. A síntese exata pequena é uma área madura.
- Lacuna a auditar — A lacuna candidata é custo de certificação/extração no fluxo do projeto, sob comparação com método estabelecido.
- Contribuição potencial — Catálogo auditável, resultado metodológico medido ou regra realmente ausente das referências.
- Algoritmo — Enumeração de palavras e chave semântica exata L,p mod 8.
- Redução — Fundir palavras equivalentes, com cobertura da gramática preservada.
- Hardware — CPU local, primeiro teste com até 2 núcleos e 512 MiB.
- Custo previsto — microinstância limitada a 30 s, duração real por medir.
- Verificação independente — Matrizes 4×4 sobre Z[zeta8] por implementação separada.
- Certificado — Duas palavras, domínio, custos e igualdade exata.
- Risco principal — Redescobrir identidades elementares ou medir só o grafo intermediário.
- Sucesso objetivo — Equivalência exata, regra além do baseline e vantagem após extração.
- Abandono — Só identidades conhecidas sem lacuna metodológica encerra a linha.
- Chance qualitativa — Média para ferramenta de verificação, baixa para identidade inédita. O domínio é inteiramente verificável.
- Última consulta — 2026-11-05. Confiança de novidade baixa até auditoria específica.
- Notas O,V,E,M,G,R,U,I,F — `[1, 5, 5, 5, 4, 4, 2, 3, 5]`. Custo e checker favorecem execução delimitada pelo Flash. Originalidade baixa exige comparação forte antes de qualquer alegação.

[Referência de partida](https://arxiv.org/abs/1601.07363v2)

## R09 — Regras ZX com custo de extração certificado

- Subárea — ZX-calculus e reescrita de grafos.
- Problema específico — Em patches ZX de até seis spiders, uma regra reduz o T-count do circuito extraído sob contexto de fronteira fixo?
- Interesse — A extração pode decidir se a redução gráfica tem utilidade real.
- Melhor resultado verificado nesta triagem — Busca exaustiva em ZX com DFS/IDDFS e podas foi publicada em 2025 e integrada a bibliotecas.
- Lacuna a auditar — Uma nova regra exige condições de fronteira, semântica e benefício além das regras já implementadas.
- Contribuição potencial — Regra contextual certificada ou contraexemplo ao benefício da extração.
- Algoritmo — Enumeração canônica de patches e busca em largura limitada.
- Redução — Isomorfismos que fixem a fronteira e reescritas já provadas.
- Hardware — CPU local, primeiro teste com até 2 núcleos e 512 MiB.
- Custo previsto — microinstância limitada a 30 s, duração real por medir.
- Verificação independente — Contração exata pequena e replay da derivação por regras verificadas.
- Certificado — Patch de entrada/saída, fronteira, prova e circuito extraído.
- Risco principal — Crescimento do grafo e ganho que desaparece na extração.
- Sucesso objetivo — Igualdade semântica e menor custo no circuito final em casos congelados.
- Abandono — Regra já coberta ou extração anulando a vantagem encerra a proposta.
- Chance qualitativa — Baixa a média. Há baselines diretos e risco alto de redundância.
- Última consulta — 2026-11-05. Confiança de novidade baixa até auditoria específica.
- Notas O,V,E,M,G,R,U,I,F — `[2, 4, 3, 4, 4, 5, 2, 3, 5]`. Comunidade e falsificação claras. Verificador e extração aumentam custo comparados ao piloto CNOT+T.

[Referência de partida](https://arxiv.org/abs/2503.10983v2)

## R10 — Cargas locais em cadeia com termo de três corpos

- Subárea — Hamiltonianos e invariantes.
- Problema específico — Na família H(a,b) do documento de experimentos, existe Q de alcance até três fora das cargas conhecidas, para N=4,5,6?
- Interesse — Uma identidade local pode sugerir uma família de simetrias ou uma obstrução.
- Melhor resultado verificado nesta triagem — A literatura recente já prova dicotomias de integrabilidade para amplas cadeias isotrópicas de vizinho mais próximo.
- Lacuna a auditar — O termo de três corpos e as hipóteses da classificação precisam ser confrontados antes de alegar lacuna.
- Contribuição potencial — Carga candidata exata ou certificado de ausência dentro da gramática finita.
- Algoritmo — Núcleo racional da aplicação Q -> [H,Q].
- Redução — Translação, simetrias realmente presentes e eliminação de cargas conhecidas.
- Hardware — CPU local, primeiro teste com até 2 núcleos e 512 MiB.
- Custo previsto — microinstância limitada a 30 s, duração real por medir.
- Verificação independente — Comutador por matrizes exatas separado da representação Pauli da busca.
- Certificado — Coeficientes racionais e residual identicamente zero, ou rank completo na gramática.
- Risco principal — Artefato de tamanho finito e carga que é polinômio de H.
- Sucesso objetivo — Carga extra validada e enunciado finito fiel, com proposta de generalização.
- Abandono — Só cargas conhecidas ou ausência na gramática encerra o piloto.
- Chance qualitativa — Baixa, com alto interesse intelectual. A busca é pequena e a interpretação é difícil.
- Última consulta — 2026-11-05. Confiança de novidade baixa até auditoria específica.
- Notas O,V,E,M,G,R,U,I,F — `[3, 5, 4, 4, 5, 5, 4, 5, 5]`. É a aposta de maior generalização. A interpretação e a auditoria exigem mais julgamento que os três pilotos iniciais.

[Referência de partida](https://arxiv.org/abs/2504.14315v4)

## R11 — Energia Hubbard pequena com dual racional

- Subárea — Hamiltonianos e limites certificados.
- Problema específico — Em Hubbard de quatro sítios e setor fixo, um bootstrap reduzido por simetria fornece uma cota racional útil com certificado pequeno?
- Interesse — Uma cota inferior exata pode servir de controle a métodos numéricos.
- Melhor resultado verificado nesta triagem — O artigo PRL de 2026 usa relaxações semidefinidas e simetrias, com demonstração no Hubbard 1D.
- Lacuna a auditar — Falta delimitar se a racionalização/compactação proposta acrescenta algo ao método publicado.
- Contribuição potencial — Certificado dual exato com custo comparado à diagonalização por setores.
- Algoritmo — Blocos por número de partículas e spin, SDP para sugerir dual e LDLᵀ exato.
- Redução — Setores invariantes e relações lineares entre observáveis.
- Hardware — CPU local, primeiro teste com até 2 núcleos e 512 MiB.
- Custo previsto — microinstância limitada a 30 s, duração real por medir.
- Verificação independente — Conferir identidade e positividade racional por outra implementação.
- Certificado — Matriz dual racional, fatoração e valor da cota.
- Risco principal — Falha de positividade após arredondamento e benefício metodológico ausente.
- Sucesso objetivo — Cota rigorosa com custo e tamanho de certificado documentados.
- Abandono — Acesso insuficiente ao método completo ou certificado exato inviável exige adiar.
- Chance qualitativa — Baixa a média. O exemplo é pequeno, mas a reconstrução rigorosa pode custar mais que resolver o sistema.
- Última consulta — 2026-11-05. Confiança de novidade baixa até auditoria específica.
- Notas O,V,E,M,G,R,U,I,F — `[2, 4, 3, 4, 4, 5, 2, 5, 5]`. Relevância alta. Acesso apenas ao resumo editorial nesta rodada reduz a confiança de novidade.

[Referência de partida](https://journals.aps.org/prl/abstract/10.1103/1757-fx9c)

## R12 — Invariantes baratos de equivalência de estados de grafo

- Subárea — Descoberta de invariantes e informação quântica.
- Problema específico — Um perfil de cut-rank de subconjuntos até tamanho três separa órbitas de complementação local em grafos de até sete vértices?
- Interesse — Filtros demonstrados podem evitar testes caros de equivalência.
- Melhor resultado verificado nesta triagem — Equivalência LU de estados de grafo possui algoritmo quase polinomial em trabalho de 2025. Uma representação universal de stabilizer codes por grafos também foi publicada.
- Lacuna a auditar — Um perfil proposto precisa de prova de invariância e avaliação de colisões. Ele pode ser filtro incompleto.
- Contribuição potencial — Contraexemplo à completude do perfil ou filtro com taxa de rejeição medida.
- Algoritmo — Eliminação GF(2) de cortes e BFS em órbitas de complementação local.
- Redução — Isomorfismo e invariantes antes do teste de equivalência.
- Hardware — CPU local, primeiro teste com até 2 núcleos e 512 MiB.
- Custo previsto — microinstância limitada a 30 s, duração real por medir.
- Verificação independente — Aplicar as transformações e verificar o perfil em todas as etapas.
- Certificado — Sequência de complementações ou par de grafos com mesmo perfil e órbitas distintas.
- Risco principal — Confundir LC com LU ou perfil necessário com critério completo.
- Sucesso objetivo — Prova de invariância e utilidade medida, ou contraexemplo mínimo certificado.
- Abandono — Perfil já publicado sem ganho de método encerra a linha.
- Chance qualitativa — Média para contraexemplo de hipótese interna, baixa para invariante novo.
- Última consulta — 2026-11-05. Confiança de novidade baixa até auditoria específica.
- Notas O,V,E,M,G,R,U,I,F — `[2, 5, 4, 5, 4, 4, 4, 4, 5]`. Reuso GF(2) e verificabilidade altos. O perfil perde informação e pode reproduzir filtros conhecidos.

[Referência de partida](https://arxiv.org/abs/2502.06566v3)

## R13 — CEGIS de desigualdades entre invariantes pequenos

- Subárea — Descoberta de teoremas e conjecturas.
- Problema específico — Uma gramática de desigualdades lineares entre n, número de arestas, alpha e matching produz uma hipótese que resiste a contraexemplos fora da base de treino?
- Interesse — Contraexemplos curtos podem melhorar a seleção de perguntas científicas.
- Melhor resultado verificado nesta triagem — TxGraffiti automatiza conjecturas e usa dados e heurísticas, com histórico de colaboração matemática.
- Lacuna a auditar — A contribuição depende da hipótese e da prova obtida, além do mecanismo conhecido de mineração.
- Contribuição potencial — Contraexemplo documentado, teorema restrito ou resultado negativo sobre a gramática.
- Algoritmo — CEGIS em coeficientes inteiros de −3 a 3 e grafos canônicos até sete vértices.
- Redução — Deduplicação por isomorfismo e exclusão de desigualdades implicadas por fatos conhecidos.
- Hardware — CPU local, primeiro teste com até 2 núcleos e 512 MiB.
- Custo previsto — microinstância limitada a 30 s, duração real por medir.
- Verificação independente — Cálculo exato dos invariantes e prova humana/formal do sobrevivente selecionado.
- Certificado — Grafo contraexemplo ou demonstração fiel com domínio declarado.
- Risco principal — Overfitting ao catálogo e conjectura sem interesse.
- Sucesso objetivo — Uma hipótese simples com contraexemplo novo verificado ou prova de família relevante.
- Abandono — Hipóteses triviais ou todas conhecidas encerram a gramática.
- Chance qualitativa — Baixa a média. Refutações são acessíveis, enquanto relevância e originalidade exigem julgamento.
- Última consulta — 2026-11-05. Confiança de novidade baixa até auditoria específica.
- Notas O,V,E,M,G,R,U,I,F — `[3, 5, 4, 5, 4, 3, 3, 5, 5]`. Falsificação e certificado fáceis. O valor científico de uma conjectura gerada é a maior incerteza.

[Referência de partida](https://arxiv.org/abs/2409.19379v2)

## R14 — Obstruções locais a uma redução de férmions livres

- Subárea — Fronteira entre álgebra de operadores e sistemas integráveis.
- Problema específico — Para conjuntos de até seis termos Pauli de três corpos, um ansatz de redução linear falha por um padrão mínimo de anticomutação?
- Interesse — Uma obstrução pequena pode excluir uma família inteira de representações.
- Melhor resultado verificado nesta triagem — Chapman–Flammia caracterizam uma classe de modelos solúveis por reconhecimento de line graphs de frustração.
- Lacuna a auditar — Uma extensão precisa indicar qual hipótese do teorema existente está sendo relaxada.
- Contribuição potencial — Contraexemplo à extensão ou obstrução formal para o ansatz declarado.
- Algoritmo — Grafos de anticomutação e eliminação algébrica exata do ansatz.
- Redução — Isomorfismo de grafos e conjugação Clifford que preserve a pergunta.
- Hardware — CPU local, primeiro teste com até 2 núcleos e 512 MiB.
- Custo previsto — microinstância limitada a 30 s, duração real por medir.
- Verificação independente — Conferência independente das relações e da obstrução em matrizes pequenas.
- Certificado — Padrão finito de relações e prova de incompatibilidade.
- Risco principal — Excluir um ansatz restrito e anunciar impossibilidade física geral.
- Sucesso objetivo — Obstrução correta e hipótese que delimite uma extensão ainda relevante.
- Abandono — Extensão já resolvida ou impossibilidade de certificar o ansatz exige abandonar.
- Chance qualitativa — Baixa. É ousada e barata de refutar, mas as hipóteses algébricas são delicadas.
- Última consulta — 2026-11-05. Confiança de novidade baixa até auditoria específica.
- Notas O,V,E,M,G,R,U,I,F — `[3, 4, 4, 4, 5, 4, 4, 5, 4]`. Potencial de família alto, mas o certificado e a relevância da extensão exigem revisão especializada.

[Referência de partida](https://arxiv.org/abs/2003.05465v2)

## R15 — Matching quântico em pequenos grafos não bipartidos

- Subárea — Jogos quânticos e complexidade de operadores.
- Problema específico — Uma estratégia projetiva de dimensão no máximo quatro existe para um jogo de matching em um grafo não bipartido fixado com até sete vértices?
- Interesse — É uma instância finita de uma fronteira de complexidade e correlação.
- Melhor resultado verificado nesta triagem — O artigo de 2025 constrói matchings quânticos em K_n ímpar a partir de sete vértices e deixa a complexidade geral em grafos em aberto.
- Lacuna a auditar — A novidade exige um grafo e restrição de dimensão fora dos exemplos resolvidos.
- Contribuição potencial — Estratégia exata ou impossibilidade apenas na dimensão/ansatz fixados.
- Algoritmo — Síntese de projetores com entradas em pequeno corpo algébrico e busca de contraexemplos.
- Redução — Automorfismos do grafo e fixação de gauge dos projetores.
- Hardware — CPU local, primeiro teste com até 2 núcleos e 512 MiB.
- Custo previsto — microinstância limitada a 30 s, duração real por medir.
- Verificação independente — Multiplicar projetores e conferir ortogonalidade/completude por aritmética exata.
- Certificado — Projetores algébricos e identidades, ou prova da obstrução restrita.
- Risco principal — Busca falha não decide o problema geral, e dimensões maiores continuam possíveis.
- Sucesso objetivo — Certificado exato para uma instância nova após auditoria.
- Abandono — Só aproximações ou caso já resolvido encerra a instância.
- Chance qualitativa — Baixa. Certificação de uma estratégia pode ser pequena, mas encontrá-la é uma aposta de alto risco.
- Última consulta — 2026-11-05. Confiança de novidade baixa até auditoria específica.
- Notas O,V,E,M,G,R,U,I,F — `[3, 4, 2, 3, 5, 5, 2, 4, 4]`. Alto interesse teórico. Custo da síntese e limites de dimensão tornam a execução mais incerta.

[Referência de partida](https://arxiv.org/abs/2502.05136v1)

## Seleção inicial e impedimentos

R01, R02 e R08 são os três pilotos propostos por terem domínio fechado,
checagem independente definida e baixo custo de integração. A escolha
prioriza estabelecer uma comparação honesta de eficiência. A contribuição
científica deles depende de uma lacuna metodológica validada na P229.
Se restar apenas reprodução, a entrega será classificada como engenharia
ou calibração e a linha científica será encerrada ou reformulada.

R10 é a quarta aposta de alto risco e piloto barato, indicada para análise
matemática depois da revisão dos três pilotos. R06 e R14 também têm maior
potencial de resultado de família, mas exigem mais revisão especializada.
Essas linhas não recebem tarefas de implementação neste ciclo.

Antes de liberação, P229 registra, para cada piloto, a afirmação publicada
mais próxima, a diferença proposta, fontes completas e a decisão humana.
Uma pesquisa rápida sem correspondência não confirma originalidade.
[Experimentos](THREE_EXPERIMENTS_THAT_COULD_MATTER.md) ·
[Programa e gate de seleção](EVOBYTE_NEXT_RESEARCH_PROGRAM.md)
