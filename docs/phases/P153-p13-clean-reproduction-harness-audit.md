# P153 — Auditoria e isolamento do harness de reprodução limpa da matriz P13

**Status:** Proposed.
**Dependência:** P152 concluída (ou autorizada em paralelo); branch a partir de `codex/p152-constructive-algebraic-grand-dossier`.
**Owner:** agente executor; revisor formal/sistemas nos gates indicados.
**Pré-requisito:** D013 e D016 compreendidos; isolamento completo de simulações e dados pré-calculados.
**Branch:** `codex/p153-p13-clean-reproduction-harness-audit`.

## Hipótese, objetivo e escopo

Auditar e blindar o harness de benchmark unificado `benchmarks/full_matrix.py` contra qualquer resíduo histórico contestado em D013 (despacho CPU mascarado como GPU, valores pré-fixados de ablações ou simulações estatísticas). Garantir que toda e qualquer métrica de tempo, CVPS, MSE e uso de VRAM seja medida exclusivamente a partir de execuções reais no processo atual. Estabelecer gravação imutável de proveniência de hardware (RTX 4060 Laptop 8GB, i7-13620H, versão do driver CUDA, hash de commit e sementes PRNG).

Alterações permitidas: `benchmarks/full_matrix.py`, `benchmarks/synthetic.py`, `src/evobyte/resident.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p153-config.json`, `experiments/p153-run.sh`.
Fora do escopo: alteração retroativa de arquivos históricos de log; relaxamento de tolerâncias de erro.

Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Auditar `benchmarks/full_matrix.py` removendo qualquer atalho, interpolação ou fallback para estimativas históricas.
2. Garantir temporização estrita de parede via `time.perf_counter()` medindo o laço quente completo (geração + cópia + execução GPU + scoring cascata + seleção).
3. Adicionar checagem de integridade de hardware e registro de telemetria de VRAM em `benchmarks/hw_probe.py`.
4. Adicionar interface de auditoria P153 em `benchmarks/science_matrix.py` (`run_p153_clean_harness_audit`).

## Gate de saída

Execução com harness hermético auditado em árvore limpa:

```bash
git diff --check
git status --short
python3 -m pytest tests -q
python3 benchmarks/synthetic.py --smoke
python3 benchmarks/science_matrix.py --acceptance-phase P153 --config experiments/p153-config.json --output /tmp/evobyte-p153-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(benchmark): implement p153 p13 clean reproduction harness audit"
git push -u origin HEAD
gh pr create --base codex/p152-constructive-algebraic-grand-dossier --title "feat(benchmark): implement p153 p13 clean reproduction harness audit" --body-file /tmp/evobyte-p153-pr.md
```
