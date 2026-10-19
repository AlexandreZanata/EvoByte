# P135 — Confirmação cega em larga escala em geometria discreta sob controle FWER (Bonferroni-Holm)

**Status:** In review.
**Dependência:** P134 concluída; branch a partir de `codex/p134-hadwiger-nelson-plane-coloring`.
**Owner:** agente executor; revisor estatístico/matemático nos gates indicados.
**Pré-requisito:** P134 concluída com teoremas de geometria discreta e colorações provados; partição cega selada de 100 instâncias intocada.
**Branch:** `codex/p135-discrete-geometry-blind-confirmation`.

## Hipótese, objetivo e escopo

Validar o motor formal de geometria discreta, distâncias distintas, incidências de Szemerédi–Trotter, Happy Ending e Hadwiger–Nelson do EvoByte em partição cega selada de 100 instâncias (`experiments/p135-blind-split.json`, 25 instâncias em cada uma das 4 trilhas: `distinct_distances_grid`, `unit_distances_szemeredi`, `happy_ending_convex`, `hadwiger_nelson_chromatic`) sob controle rigoroso de erro familiar (FWER via Bonferroni–Holm em $\alpha = 0{,}01$).

Alterações permitidas: `src/evobyte/discrete_geometry.py`, `src/evobyte/statistical.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p135-config.json`, `experiments/p135-run.sh`, `experiments/p135-blind-split.json`.
Fora do escopo: vazamento de instâncias seladas; flexibilização de $\alpha = 0{,}01$.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-geometria-discreta-distâncias-distintas-de-erdős-e-configurações-de-pontos-em-lean-4-p129p136).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Gerar e selar criptograficamente a partição cega de 100 instâncias em `experiments/p135-blind-split.json`.
2. Implementar motor de avaliação pareada e confirmação cega em `src/evobyte/statistical.py`.
3. Adicionar interface de auditoria P135 em `benchmarks/science_matrix.py` (`run_p135_discrete_geometry_blind_confirmation_audit`).

## Gate de saída

Execução da confirmação cega com 100/100 certificados aprovados, FWER controlado em $\alpha = 0{,}01$ e árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P135 --config experiments/p135-config.json --output /tmp/evobyte-p135-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p135 discrete geometry blind confirmation"
git push -u origin HEAD
gh pr create --base codex/p134-hadwiger-nelson-plane-coloring --title "feat(formal): implement p135 discrete geometry blind confirmation" --body-file /tmp/evobyte-p135-pr.md
```
