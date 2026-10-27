# P205 — Calibração cega em códigos quânticos não-circulantes e designs afins (Blind Historical Calibration)

**Status:** Concluída (2026-10-27).
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

**Resposta:** SIM. 100% dos 3 alvos históricos foram redescobertos cegamente em 5 de 5 sementes cada (15/15 ensaios válidos) em tempo médio inferior a 0,6 s por tentativa. O tempo acumulado do benchmark completo foi de 4,008 segundos, muito abaixo do orçamento máximo de 90 segundos. O veredito oficial é `CALIBRATION_REPRODUCED`.

## Escopo Realizado

**Arquivos criados/editados:**
- `src/evobyte/p205_calibration.py`: rotinas de síntese cega via SAT para $C(9, 3, 2) = 12$, Steane $[[7, 1, 3]]$ e Shor $[[9, 1, 3]]$, com verificador afim $AG(2, 3)$.
- `benchmarks/run_p205_calibration.py`: harness executável da calibração cega com medição de tempo, metadados de hardware e hashes SHA-256.
- `experiments/p205-calibration-results.json`: manifesto com resultados brutos, tempos e hashes SHA-256 dos 15 ensaios.
- `docs/research/p205-calibration-report.md`: relatório técnico da reprodução e análise comparativa.
- `tests/test_p205_calibration.py`: validação automatizada dos 3 certificados de calibração e integridade do manifesto.
- `docs/phases/P205-blind-calibration-affine-non-circulant.md`: status e evidências atualizados.

## Critérios de Saída (Gates)

1. `tests/test_p205_calibration.py` passa 100% verde com verificação exata dos 3 alvos de calibração (`CALIBRATION_REPRODUCED`) — Aprovado (5/5 testes em 11,74 s).
2. Tempo de execução total da calibração $< 90$\,s — Aprovado (4,008 s).
3. `git diff --check`, `git status --short`, `make lint` e `python3 -m pytest tests -q` passam sem erros — Aprovado.

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
