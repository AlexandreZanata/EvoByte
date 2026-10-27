# P202 — Motor de grupos de automorfismos generalizados (Affine, Dihedral & Projective Orbits)

**Status:** Done (2026-10-27).
**Programa:** Descoberta com Simetrias Generalizadas e Códigos Quânticos Não-Circulantes (P201–P210, D045).
**Dependência:** P201 concluída e integrada em `main`.
**Owner:** agente executor.
**Branch:** `codex/p202-generalized-automorphism-orbit-reduction` (a partir de `main`).
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [`docs/phases/P192-symmetry-groups-orbit-reduction.md`](P192-symmetry-groups-orbit-reduction.md),
[`src/evobyte/symmetry_engine.py`](../../src/evobyte/symmetry_engine.py).

## Por que esta fase existe

O motor de simetrias da P192 limitava-se a grupos cíclicos $\mathbb{Z}_m$. Embora $\mathbb{Z}_m$ seja eficaz para blocos rotacionais simples ($C(15, 8, 4) = 30$), sistemas mais densos exigem grupos com automorfismos multiplicativos ou reflexões:
1. **Grupo Afim 1-Dimensional $\text{AGL}(1, q)$:** Mapeamentos $x \mapsto ax + b \pmod q$ com $a \in \mathbb{F}_q^*$ e $b \in \mathbb{F}_q$. Permite gerar matrizes de incidência balanceadas com muito menos blocos-base.
2. **Grupo Diédrico $D_m$:** Inclui reflexões modulares $x \mapsto -x + b \pmod m$, duplicando a cardinalidade do grupo e fundindo órbitas quirais.
3. **Bicirculantes Quase-Cíclicos:** Gera pares $H_X = (A \mid B)$ e $H_Z = (B^T \mid A^T)$ com $100\%$ de comutatividade simplética garantida algebricamente pela comutatividade de blocos circulantes ($A B = B A$).

Esta fase implementa as estruturas de dados algébricas para calcular órbitas, estabilizadores de subconjuntos e matrizes de representação sob $\text{AGL}(1, q)$, $D_m$ e construtores bicirculantes.

## Pergunta falsificável da fase

> A fatoração por grupos afins $\text{AGL}(1, q)$ ou diédricos $D_m$ atinge uma taxa de compressão de parâmetros $\ge 2\times$ adicional em relação ao grupo cíclico $\mathbb{Z}_m$, preservando a corretude de geração de órbitas em 100% dos testes algébricos formais?

**Resposta:** SIM. Em $C(13, 5, 3)$, o grupo afim $\text{AGL}(1, 13)$ particionou os 1287 subconjuntos em apenas 10 órbitas canônicas (compressão $128.7\times$), representando um fator adicional de $9.90\times$ em relação ao grupo cíclico $\mathbb{Z}_{13}$ (99 órbitas), superando amplamente o limiar de $2\times$. Em $C(15, 10, 4)$, o grupo diédrico $D_{15}$ reduziu 201 órbitas cíclicas para 111 órbitas ($1.81\times$ adicional pela fusão quiral). A comutatividade simplética bicirculante obteve $100.0\%$ de taxa de sucesso analítica.

## Escopo Realizado

**Arquivos criados/editados:**
- `src/evobyte/generalized_symmetry.py`: classes `AffineGroup1D`, `DihedralGroup`, `GeneralizedCoveringOrbitEngine` e `BicirculantBlockGenerator`.
- `docs/research/p202-generalized-symmetry-report.md`: medições formais de compressão, tempos de decomposição em órbitas e teoremas.
- `tests/test_generalized_symmetry.py`: testes de axiomas de grupo, compressão comparada e comutatividade simplética (6/6 verdes).
- `docs/phases/P202-generalized-automorphism-orbit-reduction.md`: atualização de status e evidências.

## Critérios de Saída (Gates)

1. `tests/test_generalized_symmetry.py` passa 100% verde com testes de fecho de grupo e corretude de órbitas.
2. Medição empírica de compressão superior a $\mathbb{Z}_m$ demonstrada nos alvos da P201.
3. `git diff --check`, `git status --short`, `make lint` e `python3 -m pytest tests -q` passam sem erros.

## Commit & Push

```bash
git add src/evobyte/generalized_symmetry.py \
  docs/research/p202-generalized-symmetry-report.md \
  tests/test_generalized_symmetry.py \
  docs/phases/P202-generalized-automorphism-orbit-reduction.md
git commit -m "feat(frontier): implement generalized automorphism orbit reduction engine (P202)"
git push -u origin codex/p202-generalized-automorphism-orbit-reduction
gh pr create --base main \
  --title "feat(frontier): implement generalized automorphism orbit reduction engine (P202)" \
  --body "Implementa motor de órbitas afins e diédricas sob D045."
```
