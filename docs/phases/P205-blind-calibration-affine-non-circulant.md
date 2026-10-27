# P205 — Calibração cega em códigos quânticos não-circulantes e designs afins (Blind Historical Calibration)

**Status:** Proposed.
**Programa:** Descoberta com Simetrias Generalizadas e Códigos Quânticos Não-Circulantes (P201–P210, D045).
**Dependência:** P204 concluída e integrada em `main`.
**Owner:** agente executor.
**Branch:** `codex/p205-blind-calibration-affine-non-circulant` (a partir de `main`).
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [`docs/phases/P195-hard-historical-records-calibration.md`](P195-hard-historical-records-calibration.md),
[`experiments/p195-calibration-results.json`](../../experiments/p195-calibration-results.json).

## Por que esta fase existe

De acordo com as regras mandatórias do EvoByte (sem falsos positivos, calibração obrigatória antes de qualquer alegação na fronteira), nenhum método pode ser aplicado a alvos em aberto sem antes provar sua capacidade de redescobrir autonomamente alvos históricos conhecidos com as mesmas propriedades estruturais.
Esta fase submete o pipeline híbrido (órbitas afins/quase-cíclicas + prioridade funcional em bytecode + ponte SAT) a uma bateria de teste cego em 3 estruturas históricas da literatura mundial:
1. **Código Quântico de Shor $[[9, 1, 3]]$:** Código estabilizador não-circulante histórico (9 qubits, 8 geradores comutantes, distância 3).
2. **Código Quântico de Steane $[[7, 1, 3]]$:** Código CSS baseado no plano de Fano sob grupo afim $\text{AGL}(1, 7)$.
3. **Covering Design Afim $C(9, 3, 2) = 12$:** Realização exata minimal de 12 blocos sob ação afim em $\mathbb{F}_9$.

## Pergunta falsificável da fase

> O pipeline híbrido sob simetrias generalizadas e resolução SAT redescobre cegamente 100% dos 3 alvos históricos de calibração em tempo inferior a 30 segundos por alvo sem injeção de sementes conhecidas?

## Escopo

**Arquivos a criar/editar:**
- `benchmarks/run_p205_calibration.py`: harness executável da calibração cega com medição rigorosa de tempo e contadores.
- `experiments/p205-calibration-results.json`: manifesto com resultados brutos, tempos e hashes SHA-256.
- `docs/research/p205-calibration-report.md`: relatório técnico da reprodução.
- `tests/test_p205_calibration.py`: validação automatizada dos 3 certificados de calibração.
- `docs/phases/P205-blind-calibration-affine-non-circulant.md`: atualização de status e evidências.

## Critérios de Saída (Gates)

1. `tests/test_p205_calibration.py` passa 100% verde com verificação exata dos 3 alvos de calibração (`CALIBRATION_REPRODUCED`).
2. Tempo de execução total da calibração $< 90$\,s.
3. `git diff --check`, `git status --short`, `make lint` e `python3 -m pytest tests -q` passam sem erros.

## Commit & Push

```bash
git add benchmarks/run_p205_calibration.py \
  experiments/p205-calibration-results.json \
  docs/research/p205-calibration-report.md \
  tests/test_p205_calibration.py \
  docs/phases/P205-blind-calibration-affine-non-circulant.md
git commit -m "feat(frontier): complete blind calibration on affine and non-circulant targets (P205)"
git push -u origin codex/p205-blind-calibration-affine-non-circulant
gh pr create --base main \
  --title "feat(frontier): complete blind calibration on affine and non-circulant targets (P205)" \
  --body "Executa calibração cega obrigatória em alvos históricos sob D045."
```
