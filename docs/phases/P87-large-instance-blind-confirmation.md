# P87 — Confirmação cega em grande escala com controle estatístico

**Status:** Proposed.
**Dependência:** P86 Proposed; branch a partir de `codex/p86-multiterm-diophantine-generalization`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P86 concluída com generalização diofantina certificada.
**Branch:** `codex/p87-large-instance-blind-confirmation`.

## Hipótese, objetivo e escopo

Confirmar a eficácia e robustez do crivo estruturado e dos lemas diofantinos em uma partição selada de 50 instâncias primas difíceis de grande porte ($10^5 \le n \le 10^7$) com controle estrito de taxa de erro familiar (Holm FWER $\alpha = 0{,}05$) comparado a baselines de busca por força bruta.

Alterações permitidas: `experiments/p87-blind-split.json`, `experiments/p87-config.json`, `experiments/p87-run.sh`, `benchmarks/science_matrix.py`, `tests/`.
Fora do escopo: acesso não auditado à partição selada antes do congelamento dos parâmetros; alteração post hoc de limiares.

## Trabalho ordenado

1. Gerar e selar criptograficamente a partição cega de grandes primos em `experiments/p87-blind-split.json`.
2. Executar teste pareado sob igual orçamento de tempo entre o motor algébrico estruturado e baseline de busca direta.
3. Avaliar significância estatística via teste de postos sinalizados de Wilcoxon com correção de Holm e registrar o veredito.

## Gate de saída

Confirmação estatística cega com $p < 0{,}05$ e veredito `ACCEPTED` em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P87 --config experiments/p87-config.json --output /tmp/evobyte-p87-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p87 large instance blind confirmation"
git push -u origin HEAD
gh pr create --base codex/p86-multiterm-diophantine-generalization --title "feat(formal): implement p87 large instance blind confirmation" --body-file /tmp/evobyte-p87-pr.md
```
