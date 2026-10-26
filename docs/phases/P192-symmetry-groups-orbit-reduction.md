# P192 — Motor de simetrias algébricas e redução por órbitas (Automorphism Orbit Reduction)

**Status:** Done (2026-10-26).
**Programa:** Descoberta Algébrica Estruturada e Síntese Funcional (P191–P200, D043).
**Dependência:** P191 concluída e integrada em `main`.
**Owner:** agente executor.
**Branch:** `codex/p192-symmetry-groups-orbit-reduction` (a partir de `main`).
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

**Resposta:** SIM. As medições empíricas registraram reduções de parâmetros entre **11,00× e 15,00×** (muito superiores aos 4× requeridos) com taxa de preservação de comutatividade simplética de **100,0%** em 500 amostras avaliadas, sem geração de candidatos triviais ou degenerados.

## Escopo Realizado

**Arquivos criados/editados:**
- `src/evobyte/symmetry_engine.py`: classes `CyclicGroup`, `CoveringOrbitEngine`, `QuasiCyclicStabilizerEngine`, geradores de matrizes circulantes e benchmarks de compressão.
- `docs/research/p192-symmetry-reduction-report.md`: estudo analítico e relatório detalhado com medições dos 5 alvos da P191.
- `tests/test_symmetry_engine.py`: suíte formal de testes unitários e de propriedades invariantes (10/10 verdes em ~2,6 s).
- `docs/phases/P192-symmetry-groups-orbit-reduction.md`: este registro de conclusão.

## Critérios de Saída (Gates)

1. `tests/test_symmetry_engine.py` passa 100% verde com testes de invariância formal.
2. Demonstração de redução mensurada de dimensionalidade sem geração de candidatos triviais ou degenerados ($rank=m$, sem linhas nulas ou duplicadas).
3. `git diff --check`, `git status --short`, `make lint` e `python3 -m pytest tests -q` passam sem erros.

## Commit & Push

```bash
git add src/evobyte/symmetry_engine.py \
  docs/research/p192-symmetry-reduction-report.md \
  tests/test_symmetry_engine.py \
  docs/phases/P192-symmetry-groups-orbit-reduction.md
git diff --cached --check
git commit -m "feat(frontier): implement automorphism orbit reduction engine (P192)"
git push -u origin codex/p192-symmetry-groups-orbit-reduction
gh pr create --base main \
  --title "feat(frontier): implement automorphism orbit reduction engine (P192)" \
  --body "Implementa a fase P192 entregando o motor de simetrias algébricas e redução por órbitas para Covering Designs e QECC."
```
