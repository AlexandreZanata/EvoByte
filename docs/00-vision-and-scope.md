# Visão e escopo do EvoByte

## Estado e finalidade

Planejamento inicial de 5 de novembro de 2026. O laboratório ainda não foi
implementado. Esta entrega contém especificações, contratos, exemplos e tarefas.
Nenhum treinamento, busca experimental ou benchmark foi executado nesta etapa.

O EvoByte investigará se uma política aprendida pequena melhora a eficiência de
uma busca combinatória local sob orçamento computacional limitado. O primeiro
experimento construirá grafos simples não direcionados sem triângulos nem ciclos
de quatro vértices, maximizando arestas. A contribuição inicial pretendida é um
método de busca mensurável, inclusive se a conclusão for negativa.

O processo é: pergunta, hipótese, protocolo, referências, busca, verificação,
análise, reprodução e conclusão. A faixa de 8 a 32 vértices tem resultados
conhecidos e será usada como benchmark; a bibliografia está em
[trabalhos relacionados](02-related-work.md).

## Quatro alegações distintas

- **Correção:** a construção satisfaz as regras, segundo verificadores independentes.
- **Desempenho:** o método melhora resultados sob custos e condições definidos.
- **Novidade:** comparação bibliográfica independente demonstra contribuição nova.
- **Optimalidade:** um limite superior provado coincide com a construção encontrada.

Uma pontuação alta não implica nenhuma das outras alegações. Alcançar um ótimo
publicado reproduz um resultado conhecido. Um hash identifica conteúdo serializado,
sem certificar não isomorfismo.

## MVP e restrições

Uma aplicação local de linha de comando, em Python, com arquivos JSON e JSONL,
dois verificadores, referências sem aprendizado, orçamento supervisionado e
análise reproduzível. A primeira política será linear, com 13 parâmetros; NumPy
é suficiente. PyTorch só será considerado se um experimento posterior justificar
aprendizado neural. O teto absoluto de 300 mil parâmetros continua obrigatório.

Hardware informado: RTX 4060 Laptop com 8 GB de VRAM, i7-13620H, 32 GB de RAM,
Linux/Pop!_OS. Drivers, CUDA, disponibilidade efetiva e desempenho ainda serão
verificados localmente. CPU é o dispositivo inicial; GPU exige benefício medido.
Cada execução completa terá até 600 segundos. A campanha inteira terá limites
próprios em [orçamento](05-experiment-budget.md).

Não integram o MVP: chatbot, frontend, plataforma multiagente, modelo grande,
cloud obrigatória, APIs pagas, avaliação numérica por LLM, microsserviços,
Kubernetes, banco vetorial, plugins universais ou execução de código gerado.
Rust só entra após perfil de desempenho demonstrar um gargalo relevante.

## Critério de entrega do laboratório futuro

Uma campanha congelada deve produzir construções verificadas, resultados de todas
as execuções, custos completos, análise de incerteza e reprodução limpa. Seu
relatório deve separar exploração de confirmação e declarar conclusão positiva,
negativa ou inconclusiva conforme o [protocolo](01-scientific-protocol.md).

## Preservação e fontes de autoridade

A raiz encontrada continha `README.md`, `HISTORICO.md`, `LICENSE` e `.gitignore`.
Não havia trabalho novo não commitado. O histórico não foi usado para decidir
a arquitetura, e seu conteúdo permanece protegido. As referências de arquivo
do README devem permanecer acessíveis.

Cada tema possui um local principal: ciência em `01`, literatura em `02`,
interfaces em `03`, fases e estados em `04`, custos em `05`, decisões em `06`.
`AGENTS.md` governa execução de tarefas e `tasks/INDEX.md` determina sua ordem.
