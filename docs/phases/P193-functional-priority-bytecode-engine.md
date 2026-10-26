# P193 — Motor de síntese de funções de prioridade em bytecode (EvoSearch Functional Priority)

**Status:** Proposed.
**Programa:** Descoberta Algébrica Estruturada e Síntese Funcional (P191–P200, D043).
**Dependência:** P192 concluída.
**Owner:** agente executor.
**Branch:** `codex/p193-functional-priority-bytecode-engine`.
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [`docs/phases/P173-constructive-bytecode-priority-engine.md`](P173-constructive-bytecode-priority-engine.md),
[`docs/phases/P174-h2-preregistered-funsearch-calibration.md`](P174-h2-preregistered-funsearch-calibration.md).

## Por que esta fase existe

No paradigma do FunSearch (DeepMind, *Nature* 2024), a chave para ultrapassar limites extremais não foi manipular vetores discretos diretamente, mas sim evoluir uma **função de prioridade**:
$$\pi_\theta: \mathcal{V} \to \mathbb{R}$$
onde cada elemento ou órbita candidata recebe uma pontuação contínua, e uma rotina de construção gulosa (*greedy selection*) seleciona iterativamente os elementos em ordem decrescente de prioridade que satisfazem as restrições livres de conflito.

O interpretador de bytecode compacto do EvoByte (64 bytes, 8 registradores, execução vetorizada ultra-rápida sem AST) é perfeitamente adequado para atuar como o sintetizador dessa função $\pi_\theta$.

Esta fase implementa:
1. Um harness de execução onde cada programa bytecode representa uma função de prioridade sobre elementos/órbitas.
2. Um extrator guloso acelerado que constrói os objetos matemáticos determinísticamente a partir do ranking de prioridades gerado pelo bytecode.

## Pergunta falsificável da fase

> A síntese de funções de prioridade em bytecode atinge throughput de pelo menos $50.000$ construções completas por segundo na GPU/CPU e redescobre com sucesso a calibração de cap set $n=3$ ($|C|=9$) e $n=4$ ($|C|=20$) em menos de 10 segundos?

## Escopo

**Arquivos a criar/editar:**
- `src/evobyte/functional_priority.py`: avaliador de prioridade funcional em bytecode e rotina de construção gulosa.
- `benchmarks/run_functional_priority_benchmark.py`: medição de throughput e velocidade de convergência.
- `docs/research/p193-functional-priority-report.md`: análise de landscape e viabilidade de convergência.
- `tests/test_functional_priority.py`: testes unitários de determinismo e integridade.

## Critérios de Saída (Gates)

1. `tests/test_functional_priority.py` passa 100% verde.
2. Redescoberta determinística dos alvos de calibração comprovada por teste unitário.
3. `git diff --check`, `git status --short`, `make lint` e `python3 -m pytest tests -q` passam sem erros.
