# P83 — Crivo de fatoração estruturada e seleção de divisores ótimos

**Status:** Done.
**Dependência:** P82 Proposed; branch a partir de `codex/p82-divisibility-lemma-synthesis`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P82 concluída com lemas de divisibilidade certificados.
**Branch:** `codex/p83-optimal-divisor-selection`.

## Hipótese, objetivo e escopo

Desenvolver e verificar um crivo estruturado que seleciona pares ótimos de divisores $(u, v)$ de $(n x - 1)$ minimizando a coordenada máxima $\max(x, y, z)$ da representação $a/n = 1/x + 1/y + 1/z$, provando a finitude da busca e a cota de coordenadas.

Alterações permitidas: `src/evobyte/algebraic.py`, `tests/test_algebraic.py`, `benchmarks/science_matrix.py`, `experiments/p83-config.json`, `experiments/p83-run.sh`.
Fora do escopo: busca não guiada; extrapolação sem cota explícita.

## Trabalho ordenado

1. Implementar estratégia de ordenação e poda de divisores por tamanho logarítmico em `src/evobyte/algebraic.py`.
2. Demonstrar redução mensurável no tamanho máximo de $z$ em instâncias de teste primas $n \equiv 1 \pmod{24}$.
3. Validar consistência exata dos certificados gerados via Lean 4 e checagem no `science_matrix.py`.

## Gate de saída

Crivo de divisores ótimos executado com sucesso e verificado sem achados de integridade:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P83 --config experiments/p83-config.json --output /tmp/evobyte-p83-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p83 optimal divisor selection"
git push -u origin HEAD
gh pr create --base codex/p82-divisibility-lemma-synthesis --title "feat(formal): implement p83 optimal divisor selection" --body-file /tmp/evobyte-p83-pr.md
```
