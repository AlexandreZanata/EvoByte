# P192 — Motor de simetrias algébricas e redução por órbitas (Automorphism Orbit Reduction)

**Status:** Proposed.
**Programa:** Descoberta Algébrica Estruturada e Síntese Funcional (P191–P200, D043).
**Dependência:** P191 concluída.
**Owner:** agente executor.
**Branch:** `codex/p192-symmetry-groups-orbit-reduction`.
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [`docs/phases/P191-narrow-gap-frontier-targets.md`](P191-narrow-gap-frontier-targets.md),
[`src/evobyte/stabilizer_search.py`](../../src/evobyte/stabilizer_search.py).

## Por que esta fase existe

A busca combinatória cega avalia configurações individuais ponto a ponto no espaço $2^N$. Quando consideramos a ação de um grupo de simetrias $G$ (por exemplo, o grupo cíclico $\mathbb{Z}_m$ atuando por deslocamento de coordenadas ou matrizes circulantes), o espaço de busca se divide em **órbitas**:
$$\mathcal{X} / G$$
O tamanho do espaço cai exponencialmente: se $|G| = m$, o número de parâmetros independentes é reduzido drasticamente, tornando o espaço pesquisável pelo EvoByte.

Esta fase implementa operadores de geração e mutação restritos a subespaços invariantes por grupos de automorfismos:
1. Matrizes estabilizadoras bloco-circulantes e quase-cíclicas (para códigos quânticos).
2. Famílias de blocos geradas por órbitas de matrizes de diferenças sob $\mathbb{Z}_v$ (para covering designs).

## Pergunta falsificável da fase

> A restrição do espaço de busca a órbitas sob grupos cíclicos $\mathbb{Z}_m$ reduz o espaço de parâmetros efetivo em pelo menos $4\times$ mantendo a taxa de preservação de comutatividade simplética (em QECC) acima de 90% dos candidatos gerados?

## Escopo

**Arquivos a criar/editar:**
- `src/evobyte/symmetry_engine.py`: geradores de matrizes circulantes, classes de órbitas e operadores de permutação invariante.
- `docs/research/p192-symmetry-reduction-report.md`: estudo analítico e medições de compressão do espaço de busca.
- `tests/test_symmetry_engine.py`: testes unitários e de propriedades invariantes (comutatividade sob ação do grupo).

## Critérios de Saída (Gates)

1. `tests/test_symmetry_engine.py` passa 100% verde com testes de invariância formal.
2. Demonstração de redução mensurada de dimensionalidade sem geração de candidatos triviais ou degenerados.
3. `git diff --check`, `git status --short`, `make lint` e `python3 -m pytest tests -q` passam sem erros.
