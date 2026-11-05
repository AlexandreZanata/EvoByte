# P215 — Calibração cega em códigos bivariados históricos e designs projetivos (Blind Bivariate Calibration)

**Status:** Done (2026-10-27).
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
2. **Código Quântico $[[16, 2, 4]]$ e Steane $[[7, 1, 3]]$:** Reprodução exata de distâncias e comutatividade simplética em parâmetros intermediários.
3. **Plano Projetivo / Espaço Afim Desarguesiano $\text{PG}(2, 3)$ ou $C(9, 3, 2) = 12$:** Reprodução estruturada via órbitas sob transformações projetivas lineares.

## Pergunta falsificável da fase

> O pipeline bivariado e projetivo reproduz 100% dos 3 alvos de calibração cega sob orçamentos estritos de busca sem qualquer violação simplética ou inconsistência de cota?

**Resposta:** **SIM (CONFIRMADO)**.
- 100% de reprodução cega nos alvos históricos (12/12 ensaios válidos, 3 sementes independentes por alvo).
- Tempo total do benchmark de $0.9887$ s, muito abaixo do orçamento máximo de 90 segundos.
- Verificação simplética estrita de 100% e certificação oficial com veredito `CALIBRATION_REPRODUCED`.

## Escopo Realizado

**Arquivos criados/editados:**
- `src/evobyte/bivariate_calibration.py`: rotinas de síntese cega para Bravyi $[[72, 12, 6]]$, Bivariado $[[16, 2, 4]]$, Steane $[[7, 1, 3]]$ e Afim $C(9, 3, 2) = 12$, com bateria multi-semente.
- `experiments/p215-bivariate-calibration-results.json`: manifesto com 12 ensaios, metadados de execução, tempos e assinaturas SHA-256.
- `docs/research/p215-bivariate-calibration-report.md`: relatório técnico documentando as taxas de sucesso e tempos de execução.
- `tests/test_bivariate_calibration.py`: 5 testes unitários cobrindo todos os alvos e a integridade do manifesto.
- `docs/phases/P215-blind-calibration-bivariate-projective.md`: atualização de status e evidências.

## Critérios de Saída (Gates)

1. `tests/test_bivariate_calibration.py` passa 100% verde (5/5 testes).
2. Todos os alvos históricos redescobrem suas soluções ótimas conhecidas com verificação simplética estrita (`CALIBRATION_REPRODUCED`).
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
