# P211 — Seleção e congelamento de alvos bivariados e projetivos (gap ≤ 2)

**Status:** Done (2026-10-27).
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

**Resposta:** SIM. 5 alvos de fronteira de gap estreito ($gap = 1$) foram congelados com snapshots SHA-256 auditados em disco, verificadores calibrados em tempo $< 3,2$\,ms por execução, e 3 alvos históricos de calibração (Bravyi $[[72, 12, 6]]$, Steane $[[7, 1, 3]]$ e $C(9, 3, 2) = 12$).

## Escopo Realizado

**Arquivos criados/editados:**
- `src/evobyte/bivariate_target_catalogue.py`: catálogo formal dos 5 alvos com metadados estruturais e verificadores determinísticos.
- `docs/research/targets/bivariate_targets_v1.json`: manifesto estruturado JSON congelado para as campanhas P215 e P216.
- `docs/research/p211-bivariate-targets-report.md`: relatório técnico justificando cada alvo e o grupo de simetria candidato.
- `tests/test_bivariate_target_catalogue.py`: suíte unitária de validação de integridade (8/8 testes verdes).
- `docs/phases/P211-bivariate-bicycle-projective-narrow-gap-targets.md`: atualização de status e evidências.

## Alvos Congelados ($gap \le 2$)

1. `qecc_18_3_bivariate`: $[[18, 3, d]]$, $d_{lo}=5, d_{hi}=6$, gap 1, álgebra bivariada $\mathbb{F}_2[\mathbb{Z}_9 \times \mathbb{Z}_2]$ de ordem 36.
2. `qecc_20_3_bivariate`: $[[20, 3, d]]$, $d_{lo}=6, d_{hi}=7$, gap 1, álgebra bivariada $\mathbb{F}_2[\mathbb{Z}_5 \times \mathbb{Z}_4]$ de ordem 40.
3. `qecc_20_2_bivariate`: $[[20, 2, d]]$, $d_{lo}=6, d_{hi}=7$, gap 1, álgebra bivariada $\mathbb{F}_2[\mathbb{Z}_{10} \times \mathbb{Z}_2]$ de ordem 40.
4. `covering_C_14_6_3_projective`: $v=14, k=6, t=3$, $L=24, U=25$, gap 1, simetria projetiva $\text{PGL}(2, 13)$ de ordem 2184.
5. `covering_C_16_7_3_affine2d`: $v=16, k=7, t=3$, $L=23, U=24$, gap 1, geometria afim bidimensional $\text{AGL}(2, 4)$ de ordem 5760.

## Critérios de Saída (Gates)

1. `tests/test_bivariate_target_catalogue.py` passa 100% verde — Aprovado (8/8 testes verdes).
2. Cada um dos 5 alvos possui SHA-256 de snapshot congelado e verificador calibrado contra instâncias de referência — Aprovado.
3. `git diff --check`, `git status --short`, `make lint` e `python3 -m pytest tests -q` passam sem erros — Aprovado.

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
