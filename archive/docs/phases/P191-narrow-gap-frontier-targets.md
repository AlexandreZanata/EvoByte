# P191 — Seleção e congelamento de alvos de fronteira com gap estreito (gap ≤ 2)

**Status:** Done (2026-10-26).
**Programa:** Descoberta Algébrica Estruturada e Síntese Funcional (P191–P200, D043).
**Dependência:** P190 concluída; PR #237 integrado em `main`.
**Owner:** agente executor; autor correspondente humano valida os 5 alvos selecionados.
**Branch:** `codex/p191-narrow-gap-frontier-targets` (a partir de `main`).
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [`docs/DECISIONS.md`](../DECISIONS.md) (D040, D041, D042),
[`docs/phases/P171-frontier-target-catalogue-v2.md`](P171-frontier-target-catalogue-v2.md), [`docs/phases/P180-grassl-bounds-frontier-catalogue.md`](P180-grassl-bounds-frontier-catalogue.md).

## Por que esta fase existe

A lição central do programa P171–P190 foi clara: atacar alvos com gaps amplos ou espaços de busca não restritos ($2^{100}$ a $2^{500}$ estados) usando mutação cega esgota o orçamento computacional sem quebrar limites mundiais.
Para que o novo programa de descoberta estruturada tenha chance real de avanço científico inédito, a seleção de alvos deve obedecer a dois critérios estritos:
1. **Gap Estreito:** A diferença entre o melhor limite inferior conhecido e o limite superior teórico deve ser de no máximo 2 unidades ($d_{hi} - d_{lo} \le 2$ em códigos corretores quânticos QECC ou $U - L \le 2$ em covering designs).
2. **Atratividade Algébrica:** O alvo deve admitir fatoração sob grupos de automorfismos cíclicos $\mathbb{Z}_m$ ou matrizes quase-circulantes que ainda não foram totalmente exauridos por busca exaustiva.

Esta fase mapeia, valida e congela exatamente 5 alvos de fronteira de gap estreito com snapshots e verificadores independentes.

## Pergunta falsificável da fase

> É possível identificar e congelar exatamente 5 alvos da fronteira ativa (LJCR e Grassl codetables) que satisfaçam simultaneamente: (a) gap conhecido $\le 2$, (b) ausência de prova de otimalidade fechada, (c) representação compacta verificável em menos de 10 segundos por verificador standalone de dependência zero?

**Resposta:** SIM. 5 alvos de gap estreito ($gap = 1$) foram congelados, acompanhados de proveniência por snapshots SHA-256, verificadores calibrados (< 0,05 s) e grupos candidatos $\mathbb{Z}_{13}, \mathbb{Z}_{14}, \mathbb{Z}_{15}, \mathbb{Z}_{16}$.

## Escopo Realizado

**Arquivos criados/editados:**
- `src/evobyte/narrow_gap_catalogue.py`: catálogo formal dos 5 alvos de gap estreito com metadados e verificadores calibrados.
- `docs/research/targets/narrow_gap_targets_v1.json`: manifesto estruturado JSON congelado para as campanhas P195 e P196.
- `docs/research/p191-narrow-gap-targets-report.md`: relatório técnico justificando cada alvo, cota teórica e grupo de simetria candidato.
- `tests/test_narrow_gap_catalogue.py`: suíte unitária completa (10/10 testes verdes em ~1,6s).
- `docs/phases/P191-narrow-gap-frontier-targets.md`: registro final de execução.

## Alvos Congelados ($gap = 1$)

1. `covering_C_13_6_3`: $v=13, k=6, t=3$, $L=20, U=21$, gap 1, simetria $\mathbb{Z}_{13}$.
2. `covering_C_14_6_3`: $v=14, k=6, t=3$, $L=24, U=25$, gap 1, simetria $\mathbb{Z}_{14}$.
3. `covering_C_15_8_4`: $v=15, k=8, t=4$, $L=29, U=30$, gap 1, simetria $\mathbb{Z}_{15}$.
4. `qecc_14_3_open`: $[[14,3,d]]$, $d_{lo}=4, d_{hi}=5$, gap 1, simetria bloco-circulante $\mathbb{Z}_{14}$.
5. `qecc_16_5_open`: $[[16,5,d]]$, $d_{lo}=4, d_{hi}=5$, gap 1, simetria bloco-circulante $\mathbb{Z}_{16}$.

## Critérios de Saída (Gates)

1. `tests/test_narrow_gap_catalogue.py` passa 100% verde (10/10 passed).
2. Cada um dos 5 alvos possui SHA-256 de snapshot e verificador calibrado contra calibração conhecida (Fano, AG(3,2), Steane, Shor, 5-qubit).
3. `git diff --check`, `git status --short`, `make lint` e `python3 -m pytest tests -q` passam sem erros.

## Commit & Push

```bash
git add src/evobyte/narrow_gap_catalogue.py \
  docs/research/targets/narrow_gap_targets_v1.json \
  docs/research/p191-narrow-gap-targets-report.md \
  tests/test_narrow_gap_catalogue.py \
  docs/phases/P191-narrow-gap-frontier-targets.md
git diff --cached --check
git commit -m "feat(frontier): freeze narrow-gap frontier catalogue and verifiers (P191)"
git push -u origin codex/p191-narrow-gap-frontier-targets
gh pr create --base main \
  --title "feat(frontier): freeze narrow-gap frontier catalogue (P191)" \
  --body "Implementa a fase P191 congelando exatamente 5 alvos de gap estreito (gap=1) em Covering Designs e QECC."
```
