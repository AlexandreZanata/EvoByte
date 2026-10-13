# P79 — Confirmação cega e controle estatístico de seleção

**Status:** Done (partição cega selada H_ES e H_SIER confirmadas com W=20/L=0 em ambas, controle de Holm FWER p=3.81e-6 < 0.05, reduções de 2535x e 184x contra baseline, veredito ACCEPTED em árvore limpa run_id=1dacdf80fdb1c90a; registro em docs/research/p79-confirmation-record.md).
**Dependência:** P78 Proposed; branch a partir de `codex/p78-sierpinski-schinzel-generalization`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P78 aceita com motor generalizado.
**Branch:** `codex/p79-blind-residue-confirmation`.

## Hipótese, objetivo e escopo

Validar o motor de busca algébrica em um conjunto selado de classes de teste (blind residue split) sob controle estrito de comparações múltiplas (Holm $\alpha=0.05$), impedindo overfitting simbólico.

Alterações permitidas: `experiments/p79-config.json`, `experiments/p79-run.sh`, `docs/research/p79-confirmation-record.md`.
Fora do escopo: acesso prévio ao conjunto selado durante a fase de desenvolvimento, relaxamento de limiares estatísticos.

## Trabalho ordenado

1. Selecionar e congelar partição cega de classes de resíduos com hash imutável.
2. Executar avaliação pareada em árvore limpa com sementes e configurações idênticas.
3. Aplicar procedimento de Holm para controle de taxa de erro de família (FWER) a 5%.

## Gate de saída

Relatório estatístico auditável com veredito formal (`ACCEPTED`, `NULL` ou `INCONCLUSIVE`) e reprodução independente:

```bash
git diff --check
git status --short
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P79
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "docs(formal): record p79 blind residue confirmation"
git push -u origin HEAD
gh pr create --base codex/p78-sierpinski-schinzel-generalization --title "docs(formal): record p79 blind residue confirmation" --body-file /tmp/evobyte-p79-pr.md
```
