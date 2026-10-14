# P95 — Confirmação cega em escala extrema (10^7 a 10^9) sob controle FWER

**Status:** Proposed.
**Dependência:** P94 Proposed; branch a partir de `codex/p94-universal-multiterm-coprimality`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P94 concluída com generalização multitermo coprima verificada.
**Branch:** `codex/p95-extreme-scale-blind-confirmation`.

## Hipótese, objetivo e escopo

Executar protocolo estatístico cego com partição selada de instâncias diofantinas em escala extrema ($10^7 \le n \le 10^9$) com controle rigoroso de taxa de erro por família (FWER / Bonferroni-Holm, $\alpha = 0.01$), verificando zero falhas do crivo estruturado sem vazamento de informação.

Alterações permitidas: `src/evobyte/algebraic.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p95-config.json`, `experiments/p95-run.sh`.
Fora do escopo: acesso prévio ao split de teste; extrapolação empírica tratada como prova universal.

## Trabalho ordenado

1. Implementar gerador determinístico de partição selada de teste em escala extrema ($10^7 \le n \le 10^9$) com hash SHA-256 e seed fixa.
2. Executar protocolo de confirmação cego com verificação exata de identidades e controle FWER.
3. Adicionar auditoria P95 em `benchmarks/science_matrix.py` (`run_p95_extreme_scale_audit`).

## Gate de saída

Auditoria P95 aceita em árvore limpa com FWER $\le 0.01$ e zero violações:

```bash
git diff --check
git status --short
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P95 --config experiments/p95-config.json --output /tmp/evobyte-p95-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p95 extreme scale blind confirmation"
git push -u origin HEAD
gh pr create --base codex/p94-universal-multiterm-coprimality --title "feat(formal): implement p95 extreme scale blind confirmation" --body-file /tmp/evobyte-p95-pr.md
```
