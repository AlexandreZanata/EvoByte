# P212 — Motor de grupos projetivos e álgebras de grupo bivariadas (PGL(2, q) & Bivariate Group Algebras)

**Status:** Done (2026-10-27).
**Programa:** Descoberta com Códigos Quânticos Bicíclicos Bivariados e Geometrias Projetivas (P211–P220, D047).
**Dependência:** P211 concluída e integrada em `main`.
**Owner:** agente executor.
**Branch:** `codex/p212-projective-groups-and-bivariate-group-algebras` (a partir de `main`).
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [`docs/phases/P202-generalized-automorphism-orbit-reduction.md`](P202-generalized-automorphism-orbit-reduction.md),
[`src/evobyte/generalized_symmetry.py`](../../src/evobyte/generalized_symmetry.py).

## Por que esta fase existe

A exploração combinatória em espaços de busca exponenciais exige forte redução de simetria:
1. **Álgebras de Grupo Bivariadas $\mathbb{F}_2[\mathbb{Z}_l \times \mathbb{Z}_m]$:** Definidas pelo anel quociente $\mathbb{F}_2[x, y] / \langle x^l - 1, y^m - 1 \rangle$. Matrizes circulantes bivariadas comutam algebricamente, viabilizando a construção direta de códigos CSS quânticos com comutatividade simplética garantida analiticamente sem violações de paridade.
2. **Grupo Projetivo Linear $\text{PGL}(2, q)$:** Ação 3-transitiva sobre os $q+1$ pontos da reta projetiva $\mathbb{P}^1(\mathbb{F}_q)$ via transformações de Möbius $z \mapsto \frac{az + b}{cz + d}$ com $ad - bc \neq 0$. Essa simetria agrega blocos de covering em órbitas com alta densidade de empacotamento combinatorial.
3. **Geometrias Afins 2-Dimensionais $\text{AGL}(2, q)$:** Mapeamentos afins $v \mapsto Mv + b$ em $\mathbb{F}_q^2$ com $M \in \text{GL}(2, q)$, gerando blocos alinhados com subespaços afins.

Esta fase implementa as estruturas de dados algébricas para calcular órbitas, polinômios bivariados e matrizes de paridade quântica.

## Pergunta falsificável da fase

> O motor de representação algébrica de $\mathbb{F}_2[\mathbb{Z}_l \times \mathbb{Z}_m]$ e $\text{PGL}(2, q)$ particiona os espaços de busca com comutatividade simplética estrita de 100% e compressão combinatória $\ge 5\times$ em relação à enumeração direta em todos os alvos da P211?

**Resposta:** SIM. 100% dos pares de polinômios bivariados em $\mathbb{F}_2[\mathbb{Z}_l \times \mathbb{Z}_m]$ comprovam analiticamente a comutatividade simplética ($H_X H_Z^T = 0 \pmod 2$) e o código de Bravyi et al. $[[72, 12, 6]]$ foi reproduzido com posto 60 e $k=12$; em $C(14, 6, 3)$, o grupo $\text{PGL}(2, 13)$ particionou os 3003 subconjuntos em exatamente 5 órbitas canônicas com compressão de $600.6\times$ em 26 ms.

## Escopo Realizado

**Arquivos criados/editados:**
- `src/evobyte/bivariate_algebra.py`: representação de polinômios bivariados em $\mathbb{F}_2[x, y] / \langle x^l - 1, y^m - 1 \rangle$, translações 2D e produto tensorial.
- `src/evobyte/projective_symmetry.py`: grupo projetivo linear $\text{PGL}(2, q)$ e gerador de órbitas projetivas sobre $\mathbb{P}^1(\mathbb{F}_q)$.
- `docs/research/p212-bivariate-projective-report.md`: medições de compressão e tempos de decomposição em órbitas.
- `tests/test_bivariate_algebra.py` e `tests/test_projective_symmetry.py`: suíte de testes algébricos (10/10 testes verdes).
- `docs/phases/P212-projective-groups-and-bivariate-group-algebras.md`: atualização de status e evidências.

## Critérios de Saída (Gates)

1. `tests/test_bivariate_algebra.py` e `tests/test_projective_symmetry.py` passam 100% verdes — Aprovado (10/10 testes verdes).
2. Comutatividade simplética de polinômios bivariados comprovada analiticamente em 100% das amostras — Aprovado.
3. `git diff --check`, `git status --short`, `make lint` e `python3 -m pytest tests -q` passam sem erros — Aprovado.

## Commit & Push

```bash
git add src/evobyte/bivariate_algebra.py \
  src/evobyte/projective_symmetry.py \
  docs/research/p212-bivariate-projective-report.md \
  tests/test_bivariate_algebra.py \
  tests/test_projective_symmetry.py \
  docs/phases/P212-projective-groups-and-bivariate-group-algebras.md
git commit -m "feat(algebra): implement bivariate group algebra and PGL(2, q) engine (P212)"
git push -u origin codex/p212-projective-groups-and-bivariate-group-algebras
gh pr create --base main \
  --title "feat(algebra): implement bivariate group algebra and PGL(2, q) engine (P212)" \
  --body "Implementa álgebra bivariada e gerador de órbitas projetivas sob D047."
```
