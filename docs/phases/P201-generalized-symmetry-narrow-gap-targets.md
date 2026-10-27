# P201 — Seleção e congelamento de alvos não-circulantes e afins (gap ≤ 2)

**Status:** Proposed.
**Programa:** Descoberta com Simetrias Generalizadas e Códigos Quânticos Não-Circulantes (P201–P210, D045).
**Dependência:** P200 concluída; PR de registro de D045 integrado em `main`.
**Owner:** agente executor; autor correspondente humano valida os alvos selecionados.
**Branch:** `codex/p201-generalized-symmetry-narrow-gap-targets` (a partir de `main`).
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [`docs/DECISIONS.md`](../DECISIONS.md) (D043, D044),
[`docs/phases/P191-narrow-gap-frontier-targets.md`](P191-narrow-gap-frontier-targets.md),
[`docs/structured-paper/main.pdf`](../structured-paper/main.pdf).

## Por que esta fase existe

A Proposição 4.1 provou em P198 que nenhum código estabilizador CSS puramente circulante pode atingir $d \ge 4$ para $[[14, 3]]$ e $[[16, 5]]$ (`NULL_BOUND`). Além disso, os covering designs densos $C(13, 5, 3)$ e $C(14, 6, 4)$ resistiram à simetria puramente cíclica $\mathbb{Z}_m$.
Portanto, para alcançar progresso matemático genuíno nos parâmetros em aberto da literatura mundial (tabelas de Grassl e repositório LJCR de Dan Gordon), o catálogo de alvos da fronteira deve ser estendido para:
1. **Códigos Quânticos com Quebra de Simetria Circulante:** Códigos quase-cíclicos com deslocamentos independentes, matrizes bicirculantes acopladas ou códigos produto levantados (lifted product) nos alvos $[[14, 3, 4]]$ e $[[16, 5, 4]]$.
2. **Covering Designs com Grupos Afins e Diédricos:** Alvos densos de gap estreito onde grupos afins $\text{AGL}(1, q) = \{x \mapsto ax + b \pmod q\}$ ou grupos diédricos $D_m$ fornecem órbitas mais ricas que o grupo cíclico $\mathbb{Z}_m$ puro.

Esta fase formaliza, valida e congela exatamente 5 alvos de gap estreito com snapshots e verificadores independentes.

## Pergunta falsificável da fase

> É possível formalizar e congelar exatamente 5 alvos de fronteira de gap estreito ($gap \le 2$) que requeiram simetria generalizada (afim, diédrica ou bicirculante quase-cíclica), acompanhados de snapshots SHA-256 e verificadores independentes de tempo de execução inferior a 50 ms?

## Escopo

**Arquivos a criar/editar:**
- `src/evobyte/generalized_target_catalogue.py`: catálogo formal dos 5 alvos com metadados estruturais e verificadores.
- `docs/research/targets/generalized_targets_v1.json`: manifesto estruturado JSON congelado.
- `docs/research/p201-generalized-targets-report.md`: relatório técnico justificando cada alvo e o grupo de simetria candidato.
- `tests/test_generalized_target_catalogue.py`: suíte unitária de validação de integridade.
- `docs/phases/P201-generalized-symmetry-narrow-gap-targets.md`: atualização de status e evidências.

## Critérios de Saída (Gates)

1. `tests/test_generalized_target_catalogue.py` passa 100% verde.
2. Cada um dos 5 alvos possui SHA-256 de snapshot congelado e verificador calibrado contra instâncias conhecidas.
3. `git diff --check`, `git status --short`, `make lint` e `python3 -m pytest tests -q` passam sem erros.

## Commit & Push

```bash
git add src/evobyte/generalized_target_catalogue.py \
  docs/research/targets/generalized_targets_v1.json \
  docs/research/p201-generalized-targets-report.md \
  tests/test_generalized_target_catalogue.py \
  docs/phases/P201-generalized-symmetry-narrow-gap-targets.md
git commit -m "feat(frontier): freeze generalized symmetry and non-circulant targets (P201)"
git push -u origin codex/p201-generalized-symmetry-narrow-gap-targets
gh pr create --base main \
  --title "feat(frontier): freeze generalized symmetry and non-circulant targets (P201)" \
  --body "Congela catálogo formal de alvos não-circulantes e afins sob D045."
```
