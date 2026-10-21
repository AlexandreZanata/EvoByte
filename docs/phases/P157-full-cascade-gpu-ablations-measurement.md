# P157 — Auditoria e medição sistemática das 9 ablações de pipeline e cascata

**Status:** Proposed.
**Dependência:** P156 concluída; branch a partir de `codex/p156-generalization-hidden-extrapolation-audit`.
**Owner:** agente executor; revisor formal/sistemas nos gates indicados.
**Pré-requisito:** P156 concluída com matriz de generalização consolidada.
**Branch:** `codex/p157-full-cascade-gpu-ablations-measurement`.

## Hipótese, objetivo e escopo

Executar medições empíricas limpas das 9 ablações de arquitetura especificadas em `docs/ABLATIONS.md`: (Abl-1) Busca aleatória pura vs. Genético; (Abl-2) Genético puro vs. MAP-Elites; (Abl-3) Modelo ilhas com migração vs. população única; (Abl-4) Otimização de constantes local vs. fixa; (Abl-5) Gerador neural vs. genético (reprodução do drop P12); (Abl-6) Execução CPU (NumPy) vs. GPU (PyTorch); (Abl-7) Lotes pequenos vs. batching massivo; (Abl-8) Verificador em cascata S0–S3 vs. scoring completo de dados; (Abl-9) Early termination vs. avaliação exaustiva. Medir o impacto individual de cada componente em CVPS e MSE.

Alterações permitidas: `benchmarks/run_ablations.py`, `experiments/p157-ablations/`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p157-config.json`, `experiments/p157-run.sh`.
Fora do escopo: uso de estimativas teóricas no lugar de execuções medidas.

Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Executar as 9 ablações completas com 10 sementes por configuração sob orçamento fixo de 10 min em `benchmarks/run_ablations.py`.
2. Quantificar a contribuição do verificador em cascata e comprovar experimentalmente o speedup de $\approx 14\times$ em CVPS sobre a avaliação ingênua.
3. Medir a eficiência da residência em VRAM e comprovar o ganho de throughput GPU sobre CPU.
4. Adicionar interface de auditoria P157 em `benchmarks/science_matrix.py` (`run_p157_ablations_audit`).

## Gate de saída

Execução integral das 9 ablações com relatório quantitativo e auditoria P157 aceita:

```bash
git diff --check
git status --short
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P157 --config experiments/p157-config.json --output /tmp/evobyte-p157-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(benchmark): implement p157 full cascade gpu ablations measurement"
git push -u origin HEAD
gh pr create --base codex/p156-generalization-hidden-extrapolation-audit --title "feat(benchmark): implement p157 full cascade gpu ablations measurement" --body-file /tmp/evobyte-p157-pr.md
```
