# EvoByte

Planejamento de um laboratório científico computacional local para testar se uma
política aprendida pequena melhora uma busca combinatória sob orçamento limitado.
O primeiro domínio é construir grafos sem triângulos nem ciclos de quatro vértices,
maximizando arestas. **Nesta etapa, o laboratório ainda não está implementado.**

## Planejamento da nova versão

- [Visão e escopo](docs/00-vision-and-scope.md)
- [Protocolo científico proposto](docs/01-scientific-protocol.md)
- [Fontes primárias e resultados conhecidos](docs/02-related-work.md)
- [Arquitetura e contratos](docs/03-architecture-and-contracts.md)
- [Fases, portões e estados científicos](docs/04-phases-and-gates.md)
- [Orçamento por execução e campanha](docs/05-experiment-budget.md)
- [Decisões e questões do piloto](docs/06-decision-log.md)
- [Exemplos de formatos, sem resultados reais](docs/examples/README.md)
- [Índice das tarefas de implementação](tasks/INDEX.md)
- [Regras para agentes executores](AGENTS.md)

A primeira entrega futura é revisar fontes e congelar o protocolo de desenvolvimento.
Depois vêm candidatos, verificadores independentes, execução supervisionada e
referências não aprendidas. A política só entra após esses portões. Comece pelas
três primeiras fichas do índice e execute uma tarefa por vez.

---

## Histórico Arquivado (Legado v1: P00 — P234)

Todo o código-fonte, dados experimentais, provas formais em Lean 4, benchmarks, artigos científicos e propostas desenvolvidos no ciclo anterior (fases P00 a P234) foram integralmente preservados e arquivados para fins de rastreabilidade e integridade científica:

- **Pasta local de arquivo:** [`archive/`](archive/) contendo todo o código, testes, experimentos e documentação do ciclo v1.
- **Branch de arquivo:** [`archive/legacy-history`](https://github.com/AlexandreZanata/EvoByte/tree/archive/legacy-history)
- **Tag permanente:** [`archive-v1-legacy`](https://github.com/AlexandreZanata/EvoByte/releases/tag/archive-v1-legacy)
- **Registro histórico completo:** Consulte [HISTORICO.md](HISTORICO.md) para a documentação de todas as fases, decisões arquiteturais (D001–D051) e resultados obtidos.

---

## Licença

Este repositório é distribuído sob a licença MIT. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.
