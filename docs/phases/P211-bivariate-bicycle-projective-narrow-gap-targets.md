# P211 — Seleção e congelamento de alvos bivariados e projetivos (gap ≤ 2)

**Status:** Proposed.
**Programa:** Descoberta com Códigos Quânticos Bicíclicos Bivariados e Geometrias Projetivas (P211–P220, D047).
**Dependência:** P210 concluída e integrada em `main` (D046).
**Owner:** agente executor; autor correspondente humano valida os alvos selecionados.
**Branch:** `codex/p211-bivariate-bicycle-projective-narrow-gap-targets` (a partir de `main`).
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [`docs/DECISIONS.md`](../DECISIONS.md) (D045, D046, D047),
[`docs/phases/P201-generalized-symmetry-narrow-gap-targets.md`](P201-generalized-symmetry-narrow-gap-targets.md),
[`docs/generalized-paper/main.pdf`](../generalized-paper/main.pdf).

## Por que esta fase existe

O programa D045 superou a barreira dos códigos quânticos puramente circulantes ($d \le 3$), construindo explicitamente códigos quase-cíclicos $[[14, 3, 4]]$ e $[[16, 5, 4]]$ que empataram com os recordes mundiais da literatura (`codetables.de`). Além disso, delimitou cotas nulas (`NULL_BOUND`) rigorosas sob grupos afins $\text{AGL}(1, 13)$ e diédricos $D_{15}$.
Para avançar a fronteira do conhecimento matemático:
1. **Códigos Quânticos com Distância $d \ge 5$:** Na literatura de códigos corretores quânticos, instâncias com $d \ge 5$ (como $[[18, 3, 5]]$, $[[18, 5, 5]]$ e $[[20, 4, 6]]$) possuem gaps estritos de 1 unidade em relação às cotas superiores teóricas e não foram acessíveis por métodos 1-dimensionais simples. A álgebra de grupo bivariada $\mathbb{F}_2[\mathbb{Z}_l \times \mathbb{Z}_m]$ (códigos bicíclicos bivariados / *bivariate bicycle codes*) introduz dois operadores de translação comutativos $x$ e $y$, expandindo o espaço de soluções e permitindo estabilizadores de peso esparso com maior distância efetiva.
2. **Covering Designs com Grupos Projetivos e Geometrias 2D:** Em problemas combinatórios de cobertura, alvos com $v \ge 14$ resistiram a $\text{AGL}(1, q)$ e $D_m$. O grupo projetivo linear $\text{PGL}(2, q)$ agindo sobre a reta projetiva $\mathbb{P}^1(\mathbb{F}_q)$ (por exemplo $\text{PGL}(2, 13)$ em $v=14$) e geometrias afins 2D $\text{AGL}(2, q)$ agindo sobre $\mathbb{F}_q^2$ (por exemplo $v=16$) oferecem estruturas de incidência altamente simétricas com órbitas canônicas ricas.

Esta fase formaliza, valida e congela exatamente 5 alvos de gap estreito ($gap \le 2$), snapshots e verificadores determinísticos independentes.

## Pergunta falsificável da fase

> É possível formalizar e congelar exatamente 5 alvos de fronteira de gap estreito ($gap \le 2$) que demandem formulações bivariadas $\mathbb{F}_2[\mathbb{Z}_l \times \mathbb{Z}_m]$ ou grupos projetivos $\text{PGL}(2, q)$, acompanhados de snapshots SHA-256 e verificadores determinísticos com tempo de execução inferior a 50 ms?

## Escopo

**Arquivos a criar/editar:**
- `src/evobyte/bivariate_target_catalogue.py`: catálogo formal dos 5 alvos com metadados estruturais e verificadores determinísticos.
- `docs/research/targets/bivariate_targets_v1.json`: manifesto estruturado JSON congelado para as campanhas P215 e P216.
- `docs/research/p211-bivariate-targets-report.md`: relatório técnico justificando cada alvo e o grupo de simetria candidato.
- `tests/test_bivariate_target_catalogue.py`: suíte unitária de validação de integridade.
- `docs/phases/P211-bivariate-bicycle-projective-narrow-gap-targets.md`: atualização de status e evidências.

## Alvos Candidatos ($gap \le 2$)

1. `qecc_18_3_bivariate`: $[[18, 3, d]]$, $d_{lo}=5, d_{hi}=6$, gap 1, álgebra bivariada $\mathbb{F}_2[\mathbb{Z}_9 \times \mathbb{Z}_2]$.
2. `qecc_18_5_bivariate`: $[[18, 5, d]]$, $d_{lo}=5, d_{hi}=6$, gap 1, álgebra bivariada $\mathbb{F}_2[\mathbb{Z}_9 \times \mathbb{Z}_2]$.
3. `qecc_20_4_bivariate`: $[[20, 4, d]]$, $d_{lo}=6, d_{hi}=7$, gap 1, álgebra bivariada $\mathbb{F}_2[\mathbb{Z}_5 \times \mathbb{Z}_4]$.
4. `covering_C_14_6_4_projective`: $v=14, k=6, t=4$, $L=65, U=67$, gap 2, simetria projetiva $\text{PGL}(2, 13)$ de ordem 2184.
5. `covering_C_16_6_3_affine2d`: $v=16, k=6, t=3$, $L=16, U=17$, gap 1, geometria afim bidimensional $\text{AGL}(2, 4)$.

## Critérios de Saída (Gates)

1. `tests/test_bivariate_target_catalogue.py` passa 100% verde.
2. Cada um dos 5 alvos possui SHA-256 de snapshot congelado e verificador calibrado contra instâncias de referência.
3. `git diff --check`, `git status --short`, `make lint` e `python3 -m pytest tests -q` passam sem erros.

## Commit & Push

```bash
git add src/evobyte/bivariate_target_catalogue.py \
  docs/research/targets/bivariate_targets_v1.json \
  docs/research/p211-bivariate-targets-report.md \
  tests/test_bivariate_target_catalogue.py \
  docs/phases/P211-bivariate-bicycle-projective-narrow-gap-targets.md
git commit -m "feat(frontier): freeze bivariate bicycle and projective targets (P211)"
git push -u origin codex/p211-bivariate-bicycle-projective-narrow-gap-targets
gh pr create --base main \
  --title "feat(frontier): freeze bivariate bicycle and projective targets (P211)" \
  --body "Congela catálogo formal de alvos bivariados e projetivos sob D047."
```
