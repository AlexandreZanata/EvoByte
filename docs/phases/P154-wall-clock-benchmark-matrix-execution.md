# P154 — Execução da matriz completa sob orçamentos estritos de tempo de parede

**Status:** Proposed.
**Dependência:** P153 concluída; branch a partir de `codex/p153-p13-clean-reproduction-harness-audit`.
**Owner:** agente executor; revisor formal/sistemas nos gates indicados.
**Pré-requisito:** P153 concluída com harness hermético aprovado.
**Branch:** `codex/p154-wall-clock-benchmark-matrix-execution`.

## Hipótese, objetivo e escopo

Executar a matriz completa do benchmark em orçamentos reais de tempo de parede (10 s, 1 min, 10 min, 1 h) sobre os alvos sintéticos padronizados (Level-A: $y = x+1$, $y = x^2+3x+7$; Level-B: $\sin(x) + x^2$, Nguyen-1 a Nguyen-12) em pelo menos 20 sementes independentes na GPU RTX 4060 de referência. Medir CVPS (Candidates Verified Per Second) real, taxa de sucesso de redescoberta, MSE de treino e uso contínuo de memória VRAM (< 6 GB). Registrar cada execução individual em arquivo JSON estruturado imutável.

Alterações permitidas: `benchmarks/full_matrix.py`, `experiments/p154-matrix/`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p154-config.json`, `experiments/p154-run.sh`.
Fora do escopo: extrapolação de execuções incompletas; estimativas post-hoc.

Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Executar bateria de testes com 20 sementes para orçamentos de 10 s, 1 min, 10 min e 1 h com gravação determinística em `experiments/p154-matrix/`.
2. Registrar estatísticas brutas (tempo exato, gerações, candidatos S0/S1/S2/S3 avaliados, CVPS médio e pico).
3. Confirmar que a taxa de redescoberta para os alvos primários atinge $\ge 80\%$ (16/20 sementes) dentro do orçamento de 1 h.
4. Adicionar interface de auditoria P154 em `benchmarks/science_matrix.py` (`run_p154_matrix_execution_audit`).

## Gate de saída

Execução integral das 20 sementes com matriz de dados gerada e auditoria P154 aceita:

```bash
git diff --check
git status --short
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P154 --config experiments/p154-config.json --output /tmp/evobyte-p154-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(benchmark): implement p154 wall clock benchmark matrix execution"
git push -u origin HEAD
gh pr create --base codex/p153-p13-clean-reproduction-harness-audit --title "feat(benchmark): implement p154 wall clock benchmark matrix execution" --body-file /tmp/evobyte-p154-pr.md
```
