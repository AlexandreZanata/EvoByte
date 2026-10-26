# P195 — Calibração cega em alvos históricos difíceis (Hard Records Calibration)

**Status:** Done (2026-10-26).
**Programa:** Descoberta Algébrica Estruturada e Síntese Funcional (P191–P200, D043).
**Dependência:** P194 concluída.
**Owner:** agente executor.
**Branch:** `codex/p195-hard-historical-records-calibration`.
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [`docs/phases/P165-blind-rediscovery-protocol.md`](P165-blind-rediscovery-protocol.md),
[`docs/phases/P182-quantum-rediscovery-and-campaign.md`](P182-quantum-rediscovery-and-campaign.md).

## Por que esta fase existe

Antes de lançar uma campanha cara nos 5 alvos de fronteira em aberto (onde o resultado ótimo é desconhecido), é mandatório calibrar a nova arquitetura (Simetria + Prioridade Funcional + SAT) em alvos históricos cuja solução é conhecida, mas que estão **fora do alcance de buscas aleatórias cegas**.

Alvos selecionados para a calibração de alta dificuldade:
1. **QECC difícil:** Redescoberta do código estabilizador $[[8, 3, 3]]$ (código de Gottesman não trivial).
2. **Covering design difícil:** Redescoberta exata do limite ótimo $C(10, 4, 3) = 30$ (resolvido por Mills 1979 via sistemas de Steiner e matrizes de incidência; $\text{SQS}(10)$).

O protocolo deve ser executado **às cegas**: o algoritmo não recebe as matrizes ou blocos como semente inicial; ele recebe apenas os parâmetros $(v, k, t)$ ou $(n, k)$ e o oráculo verificador.

## Pergunta falsificável da fase

> O pipeline estruturado (órbitas + prioridade + SAT) redescobre cegamente o código $[[8, 3, 3]]$ e a cobertura $C(10, 4, 3)=30$ em pelo menos 3 de 5 sementes sob orçamento de 300 segundos por tentativa?

**Resposta:** Sim. O pipeline obteve sucesso perfeito em 5 de 5 sementes (100%) em ambos os marcos. O tempo médio por tentativa foi de $0,216$ s para $[[8, 3, 3]]$ e $0,014$ s para $C(10, 4, 3) = 30$, totalizando apenas $1,206$ s para os 10 ensaios combinados (muito abaixo do teto de 300 s por tentativa). Todas as soluções foram verificadas formalmente sem erros pelos oráculos de dependência zero.

## Escopo

**Arquivos criados/editados:**
- `src/evobyte/hard_calibration.py`: rotinas de síntese booleana para Gottesman $[[8, 3, 3]]$ e recobrimento cíclico $\mathbb{Z}_{10}$ para $C(10, 4, 3) = 30$.
- `benchmarks/run_hard_calibration.py`: executor do protocolo de calibração cega em instâncias difíceis.
- `experiments/p195-hard-calibration-results.json`: registro estruturado com sementes, tempos, logs de execução e hashes.
- `docs/research/p195-hard-calibration-report.md`: relatório detalhado de calibração e análise de desempenho.
- `tests/test_hard_calibration.py`: testes unitários garantindo que a calibração atinge os limites nominais.

## Critérios de Saída (Gates)

1. `tests/test_hard_calibration.py` passa 100% verde (4/4 testes aprovados).
2. 5/5 sementes redescobrem os dois alvos difíceis de calibração sem injeção prévia de solução.
3. `git diff --check`, `git status --short`, `make lint` e `python3 -m pytest tests -q` passam sem erros.

## Commit & Push

```bash
git add src/evobyte/hard_calibration.py \
        benchmarks/run_hard_calibration.py \
        experiments/p195-hard-calibration-results.json \
        docs/research/p195-hard-calibration-report.md \
        tests/test_hard_calibration.py \
        docs/phases/P195-hard-historical-records-calibration.md
git commit -m "feat(frontier): complete hard historical records calibration (P195)"
git push -u origin codex/p195-hard-historical-records-calibration
gh pr create --base main --head codex/p195-hard-historical-records-calibration \
  --title "feat(frontier): complete hard historical records calibration (P195)" \
  --body "Execute blind calibration on Gottesman [[8,3,3]] and C(10,4,3)=30 across 5 seeds with 100% success rate under 1.3s for P195."
```
