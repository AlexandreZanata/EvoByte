# P215 — Calibração cega em códigos bivariados históricos e designs projetivos (Blind Bivariate Calibration)

**Status:** Proposed.
**Programa:** Descoberta com Códigos Quânticos Bicíclicos Bivariados e Geometrias Projetivas (P211–P220, D047).
**Dependência:** P214 concluída e integrada em `main`.
**Owner:** agente executor.
**Branch:** `codex/p215-blind-calibration-bivariate-projective` (a partir de `main`).
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [`docs/phases/P205-blind-calibration-affine-non-circulant.md`](P205-blind-calibration-affine-non-circulant.md),
[`docs/phases/P195-hard-historical-records-calibration.md`](P195-hard-historical-records-calibration.md).

## Por que esta fase existe

A regra de integridade do EvoByte exige que nenhum pipeline de busca seja aplicado a alvos em aberto sem antes comprovar sua capacidade de redescobrir cegamente instâncias canônicas da literatura.
Esta fase submete o pipeline bivariado e projetivo a 3 alvos históricos de calibração cega:
1. **Código Bicíclico Bivariado de Bravyi et al. $[[72, 12, 6]]$:** Teste de reprodução fiel da álgebra $\mathbb{F}_2[\mathbb{Z}_6 \times \mathbb{Z}_6]$ e verificação dos estabilizadores com peso $w=6$.
2. **Código Quântico $[[18, 2, 4]]$ ou $[[16, 4, 4]]$:** Reprodução exata de distâncias e comutatividade simplética em parâmetros intermediários.
3. **Plano Projetivo / Espaço Afim Desarguesiano $\text{PG}(2, 3)$ ou $C(9, 3, 2) = 12$:** Reprodução estruturada via órbitas sob transformações projetivas lineares.

## Pergunta falsificável da fase

> O pipeline bivariado e projetivo reproduz 100% dos 3 alvos de calibração cega sob orçamentos estritos de busca sem qualquer violação simplética ou inconsistência de cota?

## Escopo

**Arquivos a criar/editar:**
- `src/evobyte/bivariate_calibration.py`: rotina de execução cega dos alvos históricos.
- `experiments/p215-bivariate-calibration-results.json`: registro estruturado dos resultados de calibração cega.
- `docs/research/p215-bivariate-calibration-report.md`: análise detalhada das redescobertas cegas.
- `tests/test_bivariate_calibration.py`: suíte de validação dos testes cegos.
- `docs/phases/P215-blind-calibration-bivariate-projective.md`: atualização de status e evidências.

## Critérios de Saída (Gates)

1. `tests/test_bivariate_calibration.py` passa 100% verde.
2. Todos os 3 alvos históricos redescobrem suas soluções ótimas conhecidas com verificação simplética estrita.
3. `git diff --check`, `git status --short`, `make lint` e `python3 -m pytest tests -q` passam sem erros.

## Commit & Push

```bash
git add src/evobyte/bivariate_calibration.py \
  experiments/p215-bivariate-calibration-results.json \
  docs/research/p215-bivariate-calibration-report.md \
  tests/test_bivariate_calibration.py \
  docs/phases/P215-blind-calibration-bivariate-projective.md
git commit -m "feat(calibration): execute blind calibration on bivariate and projective targets (P215)"
git push -u origin codex/p215-blind-calibration-bivariate-projective
gh pr create --base main \
  --title "feat(calibration): execute blind calibration on bivariate and projective targets (P215)" \
  --body "Executa calibração cega bivariada e projetiva sob D047."
```
